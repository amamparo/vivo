use std::fs;
use std::net::UdpSocket;
use std::path::PathBuf;
use std::process::{Child, Command};
use std::sync::Mutex;

use qrcode::QrCode;
use tauri::{
    image::Image,
    menu::{MenuBuilder, MenuItemBuilder, PredefinedMenuItem},
    tray::TrayIconBuilder,
    webview::WebviewWindowBuilder,
    Manager,
};

struct Sidecar(Mutex<Option<Child>>);

impl Drop for Sidecar {
    fn drop(&mut self) {
        if let Ok(mut guard) = self.0.lock() {
            if let Some(ref mut child) = *guard {
                let _ = child.kill();
                let _ = child.wait();
            }
        }
    }
}

fn find_open_port() -> u16 {
    UdpSocket::bind("127.0.0.1:0")
        .ok()
        .and_then(|s| s.local_addr().ok())
        .map(|a| a.port())
        .unwrap_or(8000)
}

fn local_ip() -> String {
    UdpSocket::bind("0.0.0.0:0")
        .and_then(|s| {
            s.connect("8.8.8.8:80")?;
            s.local_addr()
        })
        .map(|a| a.ip().to_string())
        .unwrap_or_else(|_| "localhost".to_string())
}

fn project_dir() -> PathBuf {
    std::env::var("VIVO_PROJECT_DIR")
        .map(PathBuf::from)
        .unwrap_or_else(|_| {
            let mut dir = std::env::current_exe()
                .unwrap_or_default()
                .parent()
                .unwrap_or(std::path::Path::new("."))
                .to_path_buf();
            for _ in 0..3 {
                dir = dir.parent().unwrap_or(&dir).to_path_buf();
            }
            dir
        })
}

fn read_version(init_path: &std::path::Path) -> Option<String> {
    let text = fs::read_to_string(init_path).ok()?;
    text.lines()
        .find(|l| l.starts_with("__version__"))
        .and_then(|l| {
            let start = l.find(['\'', '"'])?;
            let rest = &l[start + 1..];
            let end = rest.find(['\'', '"'])?;
            Some(rest[..end].to_string())
        })
}

fn install_remote_script(project: &std::path::Path) {
    let source = project.join("remote_script").join("__init__.py");
    let target_dir: PathBuf = dirs::home_dir()
        .unwrap_or_default()
        .join("Music/Ableton/User Library/Remote Scripts/VivOSC");
    let target = target_dir.join("__init__.py");

    let source_version = read_version(&source).unwrap_or_default();
    let installed_version = read_version(&target);

    if installed_version.as_deref() == Some(&source_version) {
        log::info!("VivOSC {} already up to date", source_version);
        return;
    }

    let venv_python = project.join(".venv/bin/python");
    let setup_script = project.join("setup_remote_script.py");

    match Command::new(venv_python).arg(&setup_script).current_dir(project).output() {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let stderr = String::from_utf8_lossy(&output.stderr);
            if output.status.success() {
                log::info!("Remote script install: {}", stdout.trim());
            } else {
                log::error!("Remote script install failed: {} {}", stdout.trim(), stderr.trim());
            }
        }
        Err(e) => log::error!("Failed to run setup_remote_script.py: {}", e),
    }
}

fn kill_stale_vivo(project: &std::path::Path) {
    let pid_file = project.join("logs/vivo.pid");
    if let Ok(contents) = fs::read_to_string(&pid_file) {
        if let Ok(pid) = contents.trim().parse::<u32>() {
            let check = Command::new("kill").args(["-0", &pid.to_string()]).output();
            if check.map(|o| o.status.success()).unwrap_or(false) {
                log::info!("Killing stale Vivo server (pid {})", pid);
                let _ = Command::new("kill").arg(pid.to_string()).output();
                std::thread::sleep(std::time::Duration::from_millis(500));
            }
        }
        let _ = fs::remove_file(&pid_file);
    }
}

fn start_sidecar(project: &std::path::Path, port: u16) -> Option<Child> {
    kill_stale_vivo(project);

    log::info!("Starting sidecar from: {}", project.display());

    let venv_bin = project.join(".venv/bin");

    Command::new(venv_bin.join("python"))
        .args([
            "-m", "uvicorn",
            "server.main:app",
            "--host", "0.0.0.0",
            "--port", &port.to_string(),
        ])
        .current_dir(project)
        .env("VIRTUAL_ENV", project.join(".venv"))
        .env("PATH", format!("{}:{}", venv_bin.display(), std::env::var("PATH").unwrap_or_default()))
        .spawn()
        .map_err(|e| log::error!("Failed to start sidecar: {}", e))
        .ok()
}

fn stop_sidecar(state: &Sidecar) {
    if let Ok(mut guard) = state.0.lock() {
        if let Some(ref mut child) = *guard {
            log::info!("Stopping sidecar (pid {})", child.id());
            let _ = child.kill();
            let _ = child.wait();
        }
        *guard = None;
    }
}

fn register_mdns_hostname(ip: &str) -> Option<Child> {
    // Use macOS dns-sd to register "vivo.local" as an A record via mDNS.
    // dns-sd -P registers a proxy service with an explicit hostname + IP.
    // The process must stay alive for the registration to persist.
    let child = Command::new("dns-sd")
        .args([
            "-P",           // register proxy
            "Vivo",         // service name
            "_http._tcp",   // service type
            "local",        // domain
            "80",           // port (unused for hostname resolution, overridden by URL)
            "vivo.local.",  // hostname to register
            ip,             // IP address
        ])
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .spawn()
        .map_err(|e| log::error!("dns-sd registration failed: {}", e))
        .ok()?;

    log::info!("Registered mDNS hostname: vivo.local → {}", ip);
    Some(child)
}

fn qr_code_svg(url: &str) -> String {
    let code = QrCode::new(url.as_bytes()).unwrap();
    let svg = code
        .render::<qrcode::render::svg::Color>()
        .quiet_zone(false)
        .dark_color(qrcode::render::svg::Color("#000000"))
        .light_color(qrcode::render::svg::Color("#ffffff"))
        .build();
    svg
}

fn connection_html(url: &str, qr_svg: &str) -> String {
    format!(
        r#"<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    padding: 24px;
    background: #f5f5f5;
    color: #333;
    margin: 0;
    text-align: center;
  }}
  h2 {{ margin-top: 0; font-size: 16px; }}
  .url {{
    font-size: 18px;
    font-weight: 600;
    color: #0066cc;
    margin: 12px 0;
    word-break: break-all;
  }}
  .qr {{ margin: 16px auto; width: 200px; height: 200px; }}
  .qr svg {{ width: 100%; height: 100%; }}
  .hint {{ color: #666; font-size: 12px; margin-top: 12px; }}
</style>
</head>
<body>
  <h2>Connect to Vivo</h2>
  <p class="hint">Open this URL on your phone, or scan the QR code</p>
  <p class="url">{url}</p>
  <div class="qr">{qr_svg}</div>
  <p class="hint">Make sure your phone is on the same Wi-Fi network</p>
</body>
</html>"#,
        url = url,
        qr_svg = qr_svg,
    )
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let project = project_dir();
    let port = find_open_port();
    let ip = local_ip();
    let bonjour_url = format!("http://vivo.local:{}", port);
    let fallback_url = format!("http://{}:{}", ip, port);

    // Install/update VivOSC remote script
    install_remote_script(&project);

    // Register vivo.local hostname via mDNS (dns-sd process stays alive)
    let _dns_sd = register_mdns_hostname(&ip);

    // Pre-generate connection page HTML
    let qr_svg = qr_code_svg(&bonjour_url);
    let conn_html = connection_html(&bonjour_url, &qr_svg);

    tauri::Builder::default()
        .plugin(
            tauri_plugin_log::Builder::default()
                .level(log::LevelFilter::Info)
                .build(),
        )
        .plugin(tauri_plugin_shell::init())
        .manage(Sidecar(Mutex::new(None)))
        .register_uri_scheme_protocol("vivo", move |_ctx, req| {
            let uri = req.uri().to_string();
            log::info!("vivo:// request: {}", uri);
            let (body, content_type) = if uri.contains("connect") {
                (conn_html.as_bytes().to_vec(), "text/html")
            } else {
                (include_str!("../html/guide.html").as_bytes().to_vec(), "text/html")
            };
            tauri::http::Response::builder()
                .header("Content-Type", content_type)
                .body(body)
                .unwrap()
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                api.prevent_close();
                let _ = window.hide();
            }
        })
        .setup(move |app| {
            let bonjour_for_open = bonjour_url.clone();
            let bonjour_for_copy = bonjour_url.clone();
            let fallback_for_copy = fallback_url.clone();
            let project_for_toggle = project.clone();
            let project_for_start = project.clone();

            // -- Build tray menu --
            let header = MenuItemBuilder::with_id("header", format!("Vivo — {}", &bonjour_url))
                .enabled(false)
                .build(app)?;
            let connect = MenuItemBuilder::with_id("connect", "Show QR Code")
                .build(app)?;
            let open_ui = MenuItemBuilder::with_id("open_ui", "Open in Browser")
                .build(app)?;
            let copy_url = MenuItemBuilder::with_id("copy_url", "Copy URL")
                .build(app)?;
            let sep1 = PredefinedMenuItem::separator(app)?;
            let toggle = MenuItemBuilder::with_id("toggle", "Stop Server")
                .build(app)?;
            let sep2 = PredefinedMenuItem::separator(app)?;
            let guide = MenuItemBuilder::with_id("guide", "Installation Guide")
                .build(app)?;
            let sep3 = PredefinedMenuItem::separator(app)?;
            let quit = MenuItemBuilder::with_id("quit", "Quit Vivo")
                .build(app)?;

            let menu = MenuBuilder::new(app)
                .items(&[
                    &header, &connect, &open_ui, &copy_url,
                    &sep1, &toggle,
                    &sep2, &guide,
                    &sep3, &quit,
                ])
                .build()?;

            let icon = Image::from_bytes(include_bytes!("../icons/32x32.png"))?;

            TrayIconBuilder::new()
                .icon(icon)
                .icon_as_template(false)
                .menu(&menu)
                .show_menu_on_left_click(true)
                .tooltip("Vivo")
                .on_menu_event(move |app, event| {
                    match event.id().as_ref() {
                        "connect" => {
                            if let Some(win) = app.get_webview_window("connect") {
                                let _ = win.show();
                                let _ = win.set_focus();
                            } else {
                                let _ = WebviewWindowBuilder::new(
                                    app,
                                    "connect",
                                    tauri::WebviewUrl::External("vivo://connect".parse().unwrap()),
                                )
                                .title("Vivo — Connect")
                                .inner_size(340.0, 440.0)
                                .resizable(false)
                                .minimizable(false)
                                .maximizable(false)
                                .build();
                            }
                        }
                        "open_ui" => {
                            let _ = open::that(&bonjour_for_open);
                        }
                        "copy_url" => {
                            // Copy both URLs so the user has the fallback IP too
                            let text = format!("{}\n{}", bonjour_for_copy, fallback_for_copy);
                            let _ = Command::new("pbcopy")
                                .stdin(std::process::Stdio::piped())
                                .spawn()
                                .and_then(|mut child| {
                                    use std::io::Write;
                                    if let Some(ref mut stdin) = child.stdin {
                                        let _ = stdin.write_all(text.as_bytes());
                                    }
                                    child.wait()
                                });
                        }
                        "guide" => {
                            if let Some(win) = app.get_webview_window("guide") {
                                let _ = win.show();
                                let _ = win.set_focus();
                            } else {
                                let _ = WebviewWindowBuilder::new(
                                    app,
                                    "guide",
                                    tauri::WebviewUrl::External("vivo://guide".parse().unwrap()),
                                )
                                .title("Vivo — Installation Guide")
                                .inner_size(400.0, 320.0)
                                .resizable(false)
                                .minimizable(false)
                                .maximizable(false)
                                .build();
                            }
                        }
                        "toggle" => {
                            let state = app.state::<Sidecar>();
                            let running = state.0.lock().map(|g| g.is_some()).unwrap_or(false);
                            if running {
                                stop_sidecar(&state);
                                let _ = toggle.set_text("Start Server");
                            } else {
                                let child = start_sidecar(&project_for_toggle, port);
                                if let Ok(mut guard) = state.0.lock() {
                                    *guard = child;
                                }
                                let _ = toggle.set_text("Stop Server");
                            }
                        }
                        "quit" => {
                            let state = app.state::<Sidecar>();
                            stop_sidecar(&state);
                            app.exit(0);
                        }
                        _ => {}
                    }
                })
                .build(app)?;

            // -- Start sidecar immediately --
            let child = start_sidecar(&project_for_start, port);
            let state = app.state::<Sidecar>();
            if let Ok(mut guard) = state.0.lock() {
                *guard = child;
            }

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
