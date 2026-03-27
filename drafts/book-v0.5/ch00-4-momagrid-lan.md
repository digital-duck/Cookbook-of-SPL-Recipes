# Running Recipes on a LAN Momagrid

<!-- *"The orchestra plays better when every musician has room to breathe." — Wen Gong* -->

<!-- --- -->

## The Problem with a Single Node

In the previous chapter, you installed `spl-llm` and ran your first workflow against a local Ollama instance. That gets you started. But if you want to run 40 recipes in sequence — some of them multi-step, multi-model, parallel — you will quickly feel the ceiling: one GPU, one queue, one point of failure.

The classic engineering answer to this is horizontal scaling. In the database world, you add read replicas. In the SPL world, you add **agents** to a **Momagrid**.

**Momagrid** is a decentralized, peer-to-peer LLM inference network. Instead of sending every task to one Ollama instance, SPL submits tasks to a **hub** that dispatches them to whichever agent on your LAN has the right model, free VRAM, and lowest queue depth. With two machines, you double throughput. With four, you quadruple it. The `.spl` files are unchanged — the grid is invisible to the recipe.

If you have a spare machine on your home network — even an old workstation with a GTX 1080 — this chapter shows you how to turn it into a production LAN AI grid.

<!-- --- -->

## Architecture

```
[Machine A — Hub + Agent]                [Machine B — Agent only]
  mg hub up --port 9000                    mg join --hub http://A:9000
  mg join --hub http://localhost:9000      Ollama running locally
  Ollama running locally
        |
        |  SPL submits tasks here
        v
  spl run recipe.spl --adapter momagrid
```

The `mg` binary is a single self-contained Go executable. It runs both hub (coordinator) and agent (worker). No Python, no Docker, no runtime dependencies beyond Ollama.

<!-- --- -->

## Prerequisites

### Every Machine in the Grid

- **Ollama** installed and running (`ollama serve`)
- At least one model pulled on each node: `ollama pull gemma3`
- **`mg` binary** (built or copied, see below)
- Machines on the same LAN with port 9000 accessible between them

### On the Hub Machine Only

- `spl-llm` installed (for running SPL recipes against the grid)
- `httpx` Python package: `pip install httpx`

<!-- --- -->

## Step 1: Build the `mg` Binary

Momagrid requires **Go 1.22+**. On Ubuntu/Linux the easiest path is:

```bash
# Install Go via snap
sudo snap install go --classic

# Verify
go version
# go version go1.22.x linux/amd64
```

Clone and build:

```bash
git clone https://github.com/digital-duck/momagrid.git
cd momagrid

go mod tidy
go build -buildvcs=false -o mg ./cmd/mg
```

Make it available system-wide:

```bash
mkdir -p ~/.local/bin
ln -sf $(pwd)/mg ~/.local/bin/mg

# Add to ~/.bashrc if not already present
echo 'export PATH=$PATH:$HOME/.local/bin' >> ~/.bashrc
source ~/.bashrc

mg --help   # verify
```

Copy the binary to every other machine you want in the grid — it is a single static executable, no dependencies.

<!-- --- -->

## Step 2: Start the Hub (Machine A)

The hub is the coordinator. It receives tasks from SPL, routes them to agents, and collects results. Start it on Machine A:

```bash
# Find your LAN IP first
hostname -I
# 192.168.0.177  ← use your actual IP below

mg hub up \
  --host 0.0.0.0 \
  --port 9000 \
  --hub-url http://192.168.0.177:9000
```

The hub creates a SQLite database at `.igrid/hub.sqlite3` on first run — no configuration needed. The `--hub-url` flag tells agents and clients the hub's reachable address on the LAN.

Verify it is running:

```bash
mg status --hub-url http://localhost:9000
# Hub: ONLINE | Agents: 0
```

<!-- --- -->

## Step 3: Join Agents

An **agent** is any machine running Ollama that has registered with the hub. Join Machine A's own GPU first (in a new terminal):

```bash
# Machine A — local agent
mg join \
  --hub http://localhost:9000 \
  --name gpu-a \
  --host 0.0.0.0 \
  --port 9001
```

On Machine B, copy the `mg` binary and run:

```bash
# Machine B — remote agent
mg join \
  --hub http://192.168.0.177:9000 \
  --name gpu-b \
  --host 0.0.0.0 \
  --port 9001
```

Verify both agents appear on the grid:

```bash
mg agents
```

Expected output:

```
NAME    AGENT_ID   TIER    STATUS  TPS
gpu-a   a1b2c3d4   SILVER  ONLINE  12.4
gpu-b   e5f6g7h8   SILVER  ONLINE  11.8
```

The `TIER` reflects hardware capability (`BRONZE` → `SILVER` → `GOLD`), inferred from VRAM. The hub uses tier and load to route tasks to the best available agent.

<!-- --- -->

## Step 4: Configure the SPL Momagrid Adapter

The SPL runtime has a built-in `momagrid` adapter. Tell it where your hub is by adding it to `~/.spl/config.yaml`:

```yaml
adapter: momagrid         # use momagrid as the default adapter

adapters:
  momagrid:
    hub_url: "http://192.168.0.177:9000"   # your hub's LAN address
    default_model: "gemma3"
    timeout: 300
    min_tier: "BRONZE"    # accept any available agent

  ollama:                 # keep ollama config as fallback
    base_url: "http://localhost:11434"
    default_model: "gemma3"
    timeout: 120
```

Alternatively, set the hub URL as an environment variable (no config file change needed):

```bash
export MOMAGRID_HUB_URL=http://192.168.0.177:9000
```

<!-- --- -->

## Step 5: Run Any Recipe Against the Grid

With the adapter configured, every existing SPL recipe runs against the LAN grid without any modification to the `.spl` file:

```bash
cd references/SPL20

# Run a recipe — SPL submits to the hub, hub dispatches to an agent
spl run cookbook/01_hello_world/hello.spl --adapter momagrid -m gemma3

# Or use your config defaults (no flags needed if config.yaml is set)
spl run cookbook/02_ollama_proxy/proxy.spl prompt="Explain transformer attention"
```

The hub selects which agent handles each task. If both gpu-a and gpu-b are online, the hub balances load automatically.

To run all 40 recipes against the grid:

```bash
cd references/SPL20
python cookbook/run_all.py
```

Because `adapter: momagrid` is set as the default in `~/.spl/config.yaml`, every recipe in the batch uses the grid.

<!-- --- -->

## Monitoring the Grid

While recipes run, watch the grid from a separate terminal:

```bash
# Live task queue
mg tasks --detail

# Stream logs as tasks complete
mg logs --follow

# Per-agent reward accounting (tracks which node did the work)
mg rewards
```

Each task result includes the serving agent's identity:

```
Hello! I'm running on gpu-b with gemma3...

[model=gemma3 tokens=18+94 latency=3201ms agent=gpu-b completed=2026-03-27T09:14:52Z]
```

<!-- --- -->

## Smoke Test Before Running All Recipes

Submit a manual task to confirm the grid is healthy before running the full batch:

```bash
mg submit "What is 2 + 2?" --model gemma3
```

If this returns an answer within a few seconds, your grid is ready.

<!-- --- -->

## Troubleshooting

**Hub starts but agents cannot connect from Machine B**
Ensure port 9000 is open on Machine A's firewall:
```bash
sudo ufw allow 9000/tcp
```

**Agent joins but tasks never dispatch**
The hub routes to agents that have the requested model loaded. Confirm Ollama has the model on that machine:
```bash
ollama list   # run on the agent machine
```
If the model is missing: `ollama pull gemma3`.

**`Cannot connect to Momagrid hub`**
The SPL adapter cannot reach the hub. Check `MOMAGRID_HUB_URL` or `hub_url` in `~/.spl/config.yaml` matches the hub's actual LAN IP. Run `mg status` to confirm the hub is up.

**Agent shows BRONZE tier, recipes are slow**
BRONZE agents have limited VRAM. If all your machines are BRONZE, lower the minimum tier requirement (the default is already `BRONZE`). For faster throughput, use a model that fits comfortably in VRAM: `phi4` or `llama3.2:3b` instead of a 27B model.

**Running on a single machine (no LAN)**
Everything works with hub and agent on the same machine — just use `localhost` everywhere and skip Machine B. This is a valid setup for testing the adapter before expanding to multi-node.

<!-- --- -->

## What Just Happened

You built a distributed AI inference grid from commodity hardware and open-source software. SPL's adapter abstraction means no recipe in this book needed to change to take advantage of it — the same `.spl` file runs on a single Ollama instance, a two-GPU LAN grid, or a rack of machines. The score stays the same; the orchestra scales.

In the chapters that follow, every recipe can be run against your Momagrid. Recipes that use `WITH` blocks (parallel CTEs) will naturally dispatch their branches to separate agents, getting true parallel speedup across machines.
