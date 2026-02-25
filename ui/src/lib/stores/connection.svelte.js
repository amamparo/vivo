let socket = $state(null)
let connected = $state(false)
let messageHandlers = []

export function onMessage(handler) {
  messageHandlers.push(handler)
  return () => {
    messageHandlers = messageHandlers.filter(h => h !== handler)
  }
}

export function connect() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.host}/ws`
  const ws = new WebSocket(wsUrl)

  ws.onopen = () => {
    socket = ws
    connected = true
  }

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data)
    for (const handler of messageHandlers) {
      handler(msg)
    }
  }

  ws.onclose = () => {
    socket = null
    connected = false
    setTimeout(connect, 2000)
  }

  ws.onerror = () => {
    ws.close()
  }
}

export function send(msg) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(msg))
  }
}

export function getConnected() {
  return connected
}
