# ch07-8: Code Generator + Tests

Generate a function from a spec, self-review it, refine if issues are found, then generate unit tests — all in one workflow.

## Pattern

```
implement_function(spec, language) → @implementation
  └─► review_implementation → issues?
        ├─ yes → fix_implementation → @implementation
        └─► generate_tests(implementation) → @tests
              └─► verify_test_syntax → assemble_output
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `spec` | TEXT | *(required)* | Natural language description of the function |
| `language` | TEXT | `Python` | Target language: `Python`, `Go`, `TypeScript`, `Rust` |
| `test_framework` | TEXT | `default` | Test framework: `pytest`, `unittest`, `testing`, `jest` |

## Usage

```bash
# Local Ollama
spl run src/recipes/ch07-8-code-gen-tests/code_gen.spl --adapter ollama \
    spec="A function that validates an email address" \
    language="Python"

spl run src/recipes/ch07-8-code-gen-tests/code_gen.spl --adapter ollama \
    spec="Binary search over a sorted list, return index or -1" \
    language="Go" \
    test_framework="testing"

spl run src/recipes/ch07-8-code-gen-tests/code_gen.spl --adapter ollama \
    spec="Parse a JWT and return its claims as an object" \
    language="TypeScript" \
    test_framework="jest"

# Momagrid
spl run src/recipes/ch07-8-code-gen-tests/code_gen.spl --adapter momagrid \
    spec="A function that validates an email address" \
    language="Python"

spl run src/recipes/ch07-8-code-gen-tests/code_gen.spl --adapter momagrid \
    spec="Binary search over a sorted list, return index or -1" \
    language="Go" \
    test_framework="testing"

spl run src/recipes/ch07-8-code-gen-tests/code_gen.spl --adapter momagrid \
    spec="Parse a JWT and return its claims as an object" \
    language="TypeScript" \
    test_framework="jest"
```

## Output status

| Status | Meaning |
|---|---|
| `complete` | Implementation + tests assembled |
| `implementation_only` | Test generation failed; implementation returned |
