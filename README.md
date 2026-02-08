<div align="center">

# 🛡️ SENTRA

### Autonomous IoT Defense System with Agentic AI

**Real-time threat detection, autonomous response, and active deception for IoT networks**

[Features](#-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [Dashboard](#-dashboard) • [Documentation](#-documentation)

</div>

---

## 🎯 Overview

**Sentra** is an autonomous IoT security system that combines machine learning anomaly detection with an agentic AI decision-making pipeline. It operates as a sidecar defense layer, protecting vulnerable IoT devices by:

- 🔍 **Detecting** attacks in real-time using ensemble ML models (GMM + LSTM)
- 🤖 **Analyzing** threats with local LLM inference (Gemma3:270m via Ollama)
- 🧠 **Remembering** attack patterns using dual memory (Neo4j + ChromaDB)
- 🍯 **Deceiving** attackers by redirecting them to honeypots and injecting fake data

---

## ✨ Features

### 🔬 Machine Learning Detection
- **Ensemble Model**: Gaussian Mixture Model (GMM) + LSTM neural network
- **Adaptive Baseline**: Dynamic threshold tuning based on traffic patterns
- **Z-Score Analysis**: Statistical anomaly detection with optimized thresholds
- **Real-time Inference**: Sub-second detection on live network traffic

### 🤖 Agentic AI Pipeline
- **Local LLM**: Gemma3:270m via Ollama for privacy-preserving inference
- **Contextual Analysis**: LLM receives device history and attack patterns
- **Autonomous Decision Making**: Agent decides response actions independently

### 🧠 Dual Memory System
- **Graph Memory (Neo4j)**: Device relationships, incidents, attacker tracking
- **Vector Memory (ChromaDB)**: Semantic search over incident embeddings
- **Context Building**: Historical data enriches LLM analysis

### 🍯 Active Deception
- **Cowrie Honeypot**: SSH/Telnet honeypot for attacker engagement
- **Traffic Redirection**: Automatic attacker routing to honeypots
- **Fake Data Injection**: Decoy RTSP streams to waste attacker resources

### 📊 Real-time Dashboard
- **WebSocket Streaming**: Live event feed
- **Attack Timeline**: Visual attack progression
- **Device Monitoring**: Health scores and incident counts
- **Agent Pipeline Visualization**: LLM decision flow

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SENTRA ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐           │
│   │   ATTACKER   │────▶│  IoT DEVICE  │◀────│ SENTRA CORE  │           │
│   │   (hping3)   │     │   (Camera)   │     │  (Sidecar)   │           │
│   └──────────────┘     └──────────────┘     └──────┬───────┘           │
│                                                     │                   │
│   ┌─────────────────────────────────────────────────┼─────────────────┐ │
│   │                    SENTRA CORE                  ▼                 │ │
│   │  ┌──────────────────────────────────────────────────────────────┐ │ │
│   │  │                    PERCEPTION LAYER                          │ │ │
│   │  │  • Network Sniffer (Scapy)                                   │ │ │
│   │  │  • Feature Extraction (SLM Compactor)                        │ │ │
│   │  │  • Device Discovery                                          │ │ │
│   │  └──────────────────────────────────────────────────────────────┘ │ │
│   │                              │                                     │ │
│   │                              ▼                                     │ │
│   │  ┌──────────────────────────────────────────────────────────────┐ │ │
│   │  │                    ANALYSIS LAYER                            │ │ │
│   │  │  • Ensemble Model (GMM + LSTM)                               │ │ │
│   │  │  • Z-Score Anomaly Detection                                 │ │ │
│   │  │  • Adaptive Baseline Tracking                                │ │ │
│   │  └──────────────────────────────────────────────────────────────┘ │ │
│   │                              │                                     │ │
│   │                              ▼                                     │ │
│   │  ┌──────────────────────────────────────────────────────────────┐ │ │
│   │  │                    AGENT LAYER (LangGraph)                   │ │ │
│   │  │  ┌────────┐   ┌────────┐   ┌────────┐   ┌─────────┐         │ │ │
│   │  │  │ANALYZE │──▶│ DECIDE │──▶│ DEPLOY │──▶│ MONITOR │         │ │ │
│   │  │  └────────┘   └────────┘   └────────┘   └─────────┘         │ │ │
│   │  │       │            │            │                            │ │ │
│   │  │       ▼            ▼            ▼                            │ │ │
│   │  │  ┌─────────────────────────────────────────────────────────┐ │ │ │
│   │  │  │  LLM (Gemma3:270m via Ollama)                          │ │ │ │
│   │  │  └─────────────────────────────────────────────────────────┘ │ │ │
│   │  └──────────────────────────────────────────────────────────────┘ │ │
│   │                              │                                     │ │
│   │                              ▼                                     │ │
│   │  ┌──────────────────────────────────────────────────────────────┐ │ │
│   │  │                   RESPONSE LAYER                             │ │ │
│   │  │  • Honeypot Redirection (Cowrie)                             │ │ │
│   │  │  • Fake Data Injection                                       │ │ │
│   │  │  • Incident Storage                                          │ │ │
│   │  └──────────────────────────────────────────────────────────────┘ │ │
│   └─────────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│   ┌────────────────┐  ┌────────────────┐  ┌────────────────┐           │
│   │    Neo4j       │  │   ChromaDB     │  │    Cowrie      │           │
│   │ Graph Memory   │  │ Vector Memory  │  │   Honeypot     │           │
│   └────────────────┘  └────────────────┘  └────────────────┘           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Docker** & Docker Compose
- **Python 3.10+** (for local development)
- **Ollama** (for LLM inference)

### 1. Clone & Setup

```bash
git clone https://github.com/dhruvmeerwal/sentra.git
cd sentra/v1

# Create virtual environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Ollama & Pull Model

```bash
# Start Ollama (if not running)
ollama serve

# Pull the Gemma3 model
ollama pull gemma3:270m
```

### 3. Launch with Docker Compose

```bash
# Start all services
docker compose -f production.yml up -d

# View logs
docker compose -f production.yml logs -f sentra_core
```

### 4. Check Status

```bash
docker compose -f production.yml ps
```

Expected output:
```
NAME              STATUS          PORTS
sentra-attacker   Up              
sentra-cam        Up              80/tcp, 554/tcp
sentra-chroma     Up              0.0.0.0:8000->8000/tcp
sentra-core       Up              
sentra-cowrie     Up              0.0.0.0:2222-2223->2222-2223/tcp
sentra-neo4j      Up (healthy)    0.0.0.0:7474->7474/tcp, 0.0.0.0:7687->7687/tcp
sentra-ollama     Up              0.0.0.0:11434->11434/tcp
```

---

## 📊 Dashboard

### Start the Dashboard

```bash
# Terminal 1: Start API backend
cd web/api
source ../../.venv/bin/activate
uvicorn main:app --reload --port 8080

# Terminal 2: Start Next.js frontend
cd web/dashboard
npm install
npm run dev
```

Open **http://localhost:3000** in your browser.

### Dashboard Features

| Panel | Description |
|-------|-------------|
| **Live Event Stream** | Real-time attack detections and system events |
| **Stats Grid** | Attacks detected, honeypot redirects, LLM decisions |
| **Device Monitor** | Health scores and incident counts per device |
| **Agent Pipeline** | Visual representation of ANALYZE→DECIDE→DEPLOY→MONITOR |

---

## 📁 Project Structure

```
sentra/v1/
├── core/                       # Main application
│   ├── agent/                  # Agentic AI components
│   │   ├── brain.py           # LangGraph workflow (SentraAgent)
│   │   └── llm.py             # Ollama client for Gemma3
│   ├── analysis/               # ML detection
│   │   ├── ensemble.py        # GMM + LSTM ensemble model
│   │   └── builder.py         # Event construction
│   ├── control/                # Response actions
│   │   └── policy.py          # Policy engine
│   ├── data/                   # Data processing
│   │   ├── features.py        # Feature extraction
│   │   ├── slm.py             # SLM compactor
│   │   └── store.py           # Packet storage
│   ├── deception/              # Active deception
│   │   └── deception.py       # Honeypot & fake data injection
│   ├── memory/                 # Dual memory system
│   │   ├── graph.py           # Neo4j graph memory
│   │   └── vector.py          # ChromaDB vector memory
│   ├── perception/             # Network sensing
│   │   ├── sniffer.py         # Scapy packet capture
│   │   └── scanner.py         # Device discovery
│   ├── web/                    # Dashboard integration
│   │   └── publisher.py       # Event publishing
│   ├── main.py                # Application entry point
│   └── pipeline.py            # Model pipeline
├── docker/                     # Container definitions
│   ├── attacker/              # Attack simulation
│   ├── sentra_core/           # Core Dockerfile
│   └── vulnerable_cam/        # Target IoT device
├── models/                     # Trained models
│   ├── sentra_v1.pkl          # GMM model
│   └── sentra_v1.keras        # LSTM model
├── scripts/                    # Utility scripts
│   ├── evaluate_model.py      # Model evaluation
│   └── init_neo4j.py          # Schema initialization
├── sentra-dashboard-app/      # Web components
├── production.yml              # Docker Compose config
└── requirements.txt            # Python dependencies
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTRA_MODE` | `INFERENCE` | `TRAIN` or `INFERENCE` mode |
| `SENTRA_INTERFACE` | `eth0` | Network interface to monitor |
| `SENTRA_THRESHOLD` | `2.5` | Anomaly detection threshold |
| `SENTRA_TRAIN_DURATION` | `60` | Training phase duration (seconds) |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j connection URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `password` | Neo4j password |
| `CHROMA_HOST` | `localhost` | ChromaDB host |
| `CHROMA_PORT` | `8000` | ChromaDB port |

---

## 📖 Commands Reference

```bash
# === SYSTEM CONTROL ===
docker compose -f production.yml up -d          # Start all services
docker compose -f production.yml down           # Stop all services
docker compose -f production.yml ps             # Check status
docker compose -f production.yml restart        # Restart all

# === LOGS ===
docker compose -f production.yml logs -f sentra_core    # Core logs
docker compose -f production.yml logs -f                 # All logs
docker compose -f production.yml logs --tail=50 sentra_core

# === REBUILD ===
docker compose -f production.yml up -d --build --force-recreate sentra_core
docker compose -f production.yml restart attacker   # New attack cycle

# === EVALUATION ===
source .venv/bin/activate
python scripts/evaluate_model.py    # Run model evaluation
python scripts/init_neo4j.py        # Initialize Neo4j schema

# === OLLAMA ===
ollama list                         # List models
ollama pull gemma3:270m            # Pull model
docker exec sentra-ollama ollama list
```

---

## 📈 Model Performance

| Metric | Value | Threshold |
|--------|-------|-----------|
| **Accuracy** | 92.3% | z-score = 0.5 |
| **Precision** | 100% | Zero false positives |
| **Recall** | 73% | Optimal detection |
| **F1 Score** | 0.84 | Balanced metric |
| **AUC-ROC** | 1.00 | Perfect separation |

---

## 🔒 Security Considerations

- **Local LLM**: All inference runs locally via Ollama - no data leaves your network
- **Network Isolation**: Containers on isolated Docker network
- **No Default Creds in Production**: Change `NEO4J_PASSWORD` and other defaults
- **Honeypot Logging**: All attacker interactions logged to `honeypot_logs/`

---

## 🛠️ Development

### Running Locally (Without Docker)

```bash
# Activate environment
source .venv/bin/activate

# Set mode
export SENTRA_MODE=INFERENCE
export SENTRA_INTERFACE=en0  # macOS

# Run core
python -m core.main
```

### Adding New Detection Rules

1. Edit `core/analysis/ensemble.py` for ML modifications
2. Edit `core/agent/brain.py` for agent workflow changes
3. Edit `core/deception/deception.py` for new response actions

---

<div align="center">

[Report Bug](https://github.com/DHRUVMEERWAL/Sentra/issues) • [Request Feature](https://github.com/DHRUVMEERWAL/Sentra/issues)

</div>
