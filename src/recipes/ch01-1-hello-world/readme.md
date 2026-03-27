# ch01-1: Hello World

Minimal SPL program — verifies that `spl`, the chosen adapter, and the model are all wired up correctly. No parameters required.

## Usage

```bash
# Echo adapter (no LLM needed — mirrors prompt back)
spl run src/recipes/ch01-1-hello-world/hello.spl

# Local Ollama
spl run src/recipes/ch01-1-hello-world/hello.spl --adapter ollama

# Momagrid
spl run src/recipes/ch01-1-hello-world/hello.spl --adapter momagrid

# Specific model
spl run src/recipes/ch01-1-hello-world/hello.spl --adapter ollama -m gemma3

# Momagrid with specific model
spl run src/recipes/ch01-1-hello-world/hello.spl --adapter momagrid -m gemma3

# Claude Code CLI
spl run src/recipes/ch01-1-hello-world/hello.spl --adapter claude_cli
```

## What it does

Sends a single `GENERATE greeting()` with a system role instructing the model to introduce itself and SPL 2.0 in two sentences.
