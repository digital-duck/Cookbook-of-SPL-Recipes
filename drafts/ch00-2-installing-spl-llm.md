# Chapter 0.2 — Installing spl-llm, Running Your First Workflow

*"Before you can conduct, you must first gather the orchestra."*

---

## The Path to Hello World

If you have spent any time in the modern AI ecosystem, you are likely used to a "dependency nightmare." You spend more time debugging your Python virtual environment, updating the OpenAI SDK, and managing your API keys than you do actually writing prompts. 

SPL 2.0 changes the game. By moving the complexity into the runtime, it reduces the "install and run" process to a single `pip install` and a model pull. In this chapter, we will go from zero to a working workflow in under fifteen minutes.

---

## Step 1: Install the Runtime

The `spl-llm` package is the heart of the ecosystem. It contains the parser, the execution engine, and all the adapters for local and cloud models. 

It is available on PyPI:

```bash
# We recommend using a clean virtual environment
python -m venv venv
source venv/bin/activate

# Install the runtime
pip install spl-llm
```

Verify the installation by running the `spl2` binary:

```bash
spl2 --version
# Expected: spl-llm v2.0.x
```

## Step 2: Set Up Your Orchestra (Ollama)

While SPL can connect to cloud providers like Claude and OpenAI, the core mission of this book is to run AI on **your own hardware**. For this, we use **Ollama**, the most popular open-source tool for running models locally.

1. **Install Ollama**: Download it from [ollama.com](https://ollama.com).
2. **Start the Service**: Ensure `ollama serve` is running in your background.
3. **Pull a Model**: For most recipes in this book, we recommend **gemma3 (27B)** for reasoning and **phi4** or **Llama 3.2** for speed.

```bash
# Pull our primary "conductor" model
ollama pull gemma3
```

## Step 3: Run Your First Workflow

Navigate to the `Cookbook-of-SPL-Recipes` directory. We will run the **Hello World** recipe from Chapter 1.1.

```bash
spl2 run cookbook/01_hello_world/hello.spl --adapter ollama -m gemma3
```

You should see an output like this:
```output
Hello! I'm Gemma, a helpful AI assistant... 
SPL 2.0 is the declarative score for this performance.
```

If you see this, your "stove is on." You have a working, end-to-end environment that can parse SPL files, communicate with an adapter, and generate intelligence from a local model.

---

## The Adapter Configuration

By default, SPL looks for a `.spl/config.yaml` file to manage your adapters. You can store your API keys and default models there to save typing.

Example configuration for cloud models:

```yaml
adapters:
  anthropic:
    api_key: "your-key-here"
    model: "claude-3-5-sonnet"
  ollama:
    host: "localhost:11434"
    model: "gemma3"
```

Once configured, you can run any recipe without flags:

```bash
# Uses the defaults in your config file
spl2 run hello.spl
```

## Troubleshooting

- **"Model not found"**: Ensure you have pulled the model using `ollama pull`. 
- **"Connection refused"**: Check that `ollama serve` is running.
- **"VRAM Limit"**: If your model is slow or crashes, you might be exceeding your GPU’s memory. Try a smaller model like `phi4` or `llama3.2:3b`.

---

## What Just Happened?

You didn't write any Python. You didn't import an SDK. You didn't manage a response envelope. You simply pointed a **Score** (`hello.spl`) at an **Orchestra** (`ollama`) and let the **Runtime** (`spl2`) handle the performance.

In the next part, we will dive into the **Basics** and see how to pass parameters, handle multiple languages, and compare different models side-by-side.

---
