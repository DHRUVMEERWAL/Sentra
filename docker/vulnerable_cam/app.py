from flask import Flask, Response, request
import time
import threading

app = Flask(__name__)

# Mock RTSP state
rtsp_sessions = {}

@app.route('/')
def index():
    return "<h1>IP Camera V 2.0 Login</h1><form><input type='text' name='user'><input type='password' name='pass'></form>"

@app.route('/api/status')
def status():
    return {"status": "online", "uptime": time.time(), "fps": 30}

# Mocking RTSP via HTTP for simplicity in this proto, or just open port
# In a real brute force tools often target 554 key exchange.
# We will just log "connections" to this port if we ran a raw socket listener.
# For simplicity, we'll assume the attacker hits this web server on a specific 'admin' endpoint 
# or we run a dummy socket on 554.

def rtsp_listener():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 554))
    s.listen(5)
    print("RTSP Listener on 554...")
    while True:
        conn, addr = s.accept()
        print(f"RTSP Connecting from {addr}")
        # Just accept and close to mimic "open but auth required" or keep open briefly
        conn.close()

if __name__ == "__main__":
    # Start dummy RTSP in background
    t = threading.Thread(target=rtsp_listener, daemon=True)
    t.start()
    
    app.run(host='0.0.0.0', port=80)
