# ch10-4: Extending with UDF (Tool Use)

Demonstrates the hybrid CALL/GENERATE pattern: deterministic Python tools handle math and data operations while the LLM focuses on language generation only.

The recipe makes the architectural principle explicit in the comments:
> LLMs are great at language, terrible at arithmetic. Keep them in their lane.

6 CALL steps = 0 LLM calls. 1 GENERATE step = 1 LLM call for the narrative. That's the pattern.

## Usage

```bash
# Local Ollama
spl run src/recipes/ch10-4-extending-with-udf/tool_use.spl \
    --adapter ollama \
    --tools src/recipes/ch10-4-extending-with-udf/tools.py \
    sales="1200,1450,1380,1600,1750,1900" \
    prev_total="7800" \
    period="H1 2025"

# Momagrid
spl run src/recipes/ch10-4-extending-with-udf/tool_use.spl \
    --adapter momagrid \
    --tools src/recipes/ch10-4-extending-with-udf/tools.py \
    sales="1200,1450,1380,1600,1750,1900" \
    prev_total="7800" \
    period="H1 2025"
```
