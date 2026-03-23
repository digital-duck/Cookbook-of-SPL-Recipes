"""
recipe_kitchen.py — SPL Recipe Kitchen
A Streamlit UI for exploring, running, and creating SPL recipes.

Usage:
    cd /path/to/Cookbook-of-SPL-Recipes/references/SPL20
    streamlit run ../../scripts/recipe_kitchen.py

Tabs:
    1. Playground   — run any single recipe with custom inputs
    2. Recipe Maker — describe a workflow in plain English → generate SPL → run it
    3. Bake-All     — trigger run_all.py and browse logs
"""

import json
import os
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR   = Path(__file__).resolve().parent
REPO_ROOT    = SCRIPT_DIR.parent
SPL20_DIR    = REPO_ROOT / "references" / "SPL20"
COOKBOOK_DIR = SPL20_DIR / "cookbook"
CATALOG_PATH = COOKBOOK_DIR / "cookbook_catalog.json"
LOG_DIR      = COOKBOOK_DIR / "out"
RUN_ALL_PY   = COOKBOOK_DIR / "run_all.py"
TEXT2SPL_PY  = SPL20_DIR / "spl" / "text2spl.py"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@st.cache_data(ttl=30)
def load_catalog() -> dict:
    with open(CATALOG_PATH) as f:
        return json.load(f)


def run_command(args: list[str], cwd: Path, timeout: int = 120) -> tuple[str, str, int]:
    """Run a shell command and return (stdout, stderr, returncode)."""
    try:
        result = subprocess.run(
            args, cwd=str(cwd),
            capture_output=True, text=True, timeout=timeout
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", f"Timed out after {timeout}s", 1
    except Exception as e:
        return "", str(e), 1


def args_to_display(args: list[str]) -> str:
    return " ".join(str(a) for a in args)


def get_log_files() -> list[Path]:
    if not LOG_DIR.exists():
        return []
    return sorted(LOG_DIR.glob("*.md"), reverse=True)


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="SPL Recipe Kitchen",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("🍳 SPL Recipe Kitchen")
st.caption("Play with recipes · Create your own · Bake them all")

tab1, tab2, tab3 = st.tabs(["🥘 Playground", "✨ Recipe Maker", "🍞 Bake-All"])

# ---------------------------------------------------------------------------
# TAB 1 — Playground
# ---------------------------------------------------------------------------

with tab1:
    st.header("Recipe Playground")
    st.markdown("Select a recipe, tweak the inputs, and run it — no CLI required.")

    catalog = load_catalog()
    recipes = catalog["recipes"]

    # Sidebar filters
    col_filter, col_main = st.columns([1, 3])

    with col_filter:
        categories = sorted({r["category"] for r in recipes})
        selected_cat = st.selectbox("Filter by category", ["all"] + categories)
        show_inactive = st.checkbox("Show inactive recipes", value=False)

    filtered = [
        r for r in recipes
        if (selected_cat == "all" or r["category"] == selected_cat)
        and (show_inactive or r["is_active"])
    ]

    recipe_names = [f"#{r['id']} — {r['name']}" for r in filtered]

    with col_filter:
        selected_label = st.selectbox("Recipe", recipe_names)

    selected_recipe = next(
        r for r in filtered
        if f"#{r['id']} — {r['name']}" == selected_label
    )

    with col_main:
        st.subheader(f"#{selected_recipe['id']} · {selected_recipe['name']}")
        st.caption(f"**Category:** {selected_recipe['category']} · "
                   f"**Status:** {selected_recipe['approval_status']}")
        st.markdown(f"_{selected_recipe['description']}_")

        # Parse args into editable fields
        # Args format: [..., "key=value", ...] for SPL input params
        base_args = []
        input_params = {}
        args = selected_recipe["args"]

        i = 0
        while i < len(args):
            arg = args[i]
            if "=" in arg and not arg.startswith("-") and not arg.startswith("spl") and not arg.startswith("bash") and not arg.startswith("./"):
                key, val = arg.split("=", 1)
                input_params[key] = val
            else:
                base_args.append(arg)
            i += 1

        # Show base command (read-only)
        st.code(args_to_display(base_args), language="bash")

        # Editable input parameters
        edited_params = {}
        if input_params:
            st.markdown("**Input parameters** (editable):")
            for key, default in input_params.items():
                edited_params[key] = st.text_input(key, value=default, key=f"param_{selected_recipe['id']}_{key}")

        # Build final command
        final_args = base_args + [f"{k}={v}" for k, v in edited_params.items()]

        run_col, _ = st.columns([1, 4])
        with run_col:
            run_btn = st.button("▶ Run Recipe", type="primary", key="run_playground")

        if run_btn:
            with st.spinner(f"Running #{selected_recipe['id']} {selected_recipe['name']}..."):
                t0 = time.time()
                stdout, stderr, rc = run_command(final_args, cwd=COOKBOOK_DIR)
                elapsed = time.time() - t0

            st.markdown(f"**Completed in {elapsed:.1f}s** · Exit code: `{rc}`")

            if stdout:
                st.markdown("**Output:**")
                st.code(stdout, language="text")
            if stderr:
                with st.expander("⚠ stderr / warnings"):
                    st.code(stderr, language="text")

            if rc == 0:
                st.success("Recipe ran successfully.")
            else:
                st.error("Recipe exited with errors. Check stderr above.")

# ---------------------------------------------------------------------------
# TAB 2 — Recipe Maker
# ---------------------------------------------------------------------------

with tab2:
    st.header("Recipe Maker")
    st.markdown(
        "Describe what you want in plain English. SPL generates the workflow. "
        "You review, edit, and run it — all without writing a single line of SPL."
    )

    st.info(
        "💡 This uses the **Text2SPL compiler** (Recipe #22). "
        "For best results, use `--adapter claude_cli` with a code-generation model."
    )

    desc = st.text_area(
        "Describe your workflow",
        height=100,
        placeholder="e.g. Summarize a document, evaluate the quality, and refine it if the score is below 0.8",
    )

    col_mode, col_adapter, col_model = st.columns(3)
    with col_mode:
        mode = st.selectbox("Mode", ["auto", "prompt", "workflow"], index=0)
    with col_adapter:
        adapter = st.selectbox("Adapter", ["ollama", "claude_cli", "openrouter"], index=0)
    with col_model:
        model = st.text_input("Model", value="gemma3")

    gen_btn = st.button("✨ Generate SPL", type="primary", disabled=not desc.strip())

    if gen_btn and desc.strip():
        if not TEXT2SPL_PY.exists():
            st.error(f"text2spl.py not found at {TEXT2SPL_PY}. Check your SPL installation.")
        else:
            with st.spinner("Generating SPL from your description…"):
                args = [
                    sys.executable, str(TEXT2SPL_PY),
                    "--description", desc,
                    "--mode", mode,
                    "--adapter", adapter,
                    "--model", model,
                ]
                stdout, stderr, rc = run_command(args, cwd=SPL20_DIR, timeout=60)

            if rc == 0 and stdout.strip():
                st.session_state["generated_spl"] = stdout.strip()
                st.success("SPL generated.")
            else:
                st.error("Generation failed.")
                if stderr:
                    st.code(stderr, language="text")

    # SPL editor
    spl_code = st.session_state.get("generated_spl", "")
    edited_spl = st.text_area(
        "Generated SPL (editable)",
        value=spl_code,
        height=300,
        key="spl_editor",
        placeholder="Generated SPL will appear here. You can edit it before running.",
    )

    col_save, col_run2 = st.columns([1, 1])

    with col_save:
        recipe_name = st.text_input("Recipe name (for saving)", placeholder="my_custom_recipe")
        if st.button("💾 Save as .spl file") and edited_spl.strip() and recipe_name.strip():
            # Sanitize: strip directory components to prevent path traversal
            safe_name = Path(recipe_name.strip()).name
            save_path = COOKBOOK_DIR / f"{safe_name}.spl"
            save_path.write_text(edited_spl)
            st.success(f"Saved to `{save_path.name}`")

    with col_run2:
        run_adapter = st.selectbox("Run with adapter", ["ollama", "claude_cli"], key="run_adapter")
        run_model = st.text_input("Model", value="gemma3", key="run_model_maker")

        if st.button("▶ Run Generated Recipe", type="primary") and edited_spl.strip():
            # Write to a temp file and run
            tmp_path = COOKBOOK_DIR / "_tmp_recipe_kitchen.spl"
            tmp_path.write_text(edited_spl)
            run_args = ["spl", "run", str(tmp_path), "--adapter", run_adapter, "-m", run_model]

            with st.spinner("Running your recipe…"):
                t0 = time.time()
                stdout, stderr, rc = run_command(run_args, cwd=COOKBOOK_DIR, timeout=120)
                elapsed = time.time() - t0

            tmp_path.unlink(missing_ok=True)

            st.markdown(f"**Completed in {elapsed:.1f}s** · Exit code: `{rc}`")
            if stdout:
                st.code(stdout, language="text")
            if stderr:
                with st.expander("stderr"):
                    st.code(stderr, language="text")
            if rc == 0:
                st.success("Recipe ran successfully.")

# ---------------------------------------------------------------------------
# TAB 3 — Bake-All
# ---------------------------------------------------------------------------

with tab3:
    st.header("Bake-All")
    st.markdown("Run all active recipes and review the output logs.")

    col_run, col_logs = st.columns([1, 2])

    with col_run:
        st.subheader("Run All")
        catalog2 = load_catalog()
        active = [r for r in catalog2["recipes"] if r["is_active"]]
        st.metric("Active recipes", len(active))

        # Per-category breakdown
        cat_counts = Counter(r["category"] for r in active)
        for cat, count in sorted(cat_counts.items()):
            st.markdown(f"- **{cat}**: {count}")

        st.markdown("---")
        if st.button("🍞 Bake All Active Recipes", type="primary"):
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_path = LOG_DIR / f"run_all_{timestamp}.md"

            with st.spinner("Baking all recipes… this may take several minutes."):
                stdout, stderr, rc = run_command(
                    [sys.executable, str(RUN_ALL_PY)],
                    cwd=SPL20_DIR,
                    timeout=600
                )
                with open(log_path, "w") as f:
                    f.write(stdout)
                    if stderr:
                        f.write("\n\n--- STDERR ---\n")
                        f.write(stderr)

            if rc == 0:
                st.success(f"Bake complete. Log: `{log_path.name}`")
            else:
                st.warning(f"Bake finished with exit code {rc}. Check log below.")

            st.code(stdout[:3000] + ("..." if len(stdout) > 3000 else ""), language="text")

    with col_logs:
        st.subheader("Log Browser")
        log_files = get_log_files()

        if not log_files:
            st.info("No logs yet. Run the bake above to generate logs.")
        else:
            log_names = [f.name for f in log_files]
            selected_log = st.selectbox("Select log", log_names)
            log_path = LOG_DIR / selected_log

            try:
                content = log_path.read_text()
                # Count structured markers emitted by run_all.py:
                #   "     result: SUCCESS"  and  "     result: FAILED"
                import re as _re
                passed = len(_re.findall(r"result:\s+SUCCESS", content))
                failed = len(_re.findall(r"result:\s+FAILED", content))

                mcol1, mcol2 = st.columns(2)
                mcol1.metric("✓ Passed", passed)
                mcol2.metric("✗ Failed", failed)

                st.markdown("**Full log:**")
                st.code(content, language="text")
            except Exception as e:
                st.error(f"Could not read log: {e}")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown("---")
st.caption(
    "SPL Recipe Kitchen · "
    "A Cookbook of SPL Recipes · "
    "Built by the AI Quartet — Wen Gong, Claude, Gemini, Z.ai"
)
