import websocket
import json

DERIV_API_TOKEN = ""

def on_message(ws, message):
    response = json.loads(message)
    print("Deriv API Response:", response)

def on_error(ws, error):
    print("WebSocket Error:", error)

def on_open(ws):
    auth_request = json.dumps({"authorize": DERIV_API_TOKEN})
    ws.send(auth_request)

# Connect to Deriv WebSocket API
ws = websocket.WebSocketApp(
    "wss://ws.deriv.com/websockets/v3",
    on_message=on_message,
    on_error=on_error
)
ws.on_open = on_open
ws.run_forever()
