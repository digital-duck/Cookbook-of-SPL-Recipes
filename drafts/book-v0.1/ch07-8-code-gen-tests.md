# Code Gen + Tests

*"Code without tests is just a bug waiting to happen."*

---

## The Pattern

In the world of AI-assisted development, "generating code" is easy. Generating *correct* code that follows your organization's standards and includes a comprehensive test suite is much harder. If you simply ask for "a function and tests," the model often produces a single, tangled block of text that is difficult to parse or verify.

**Test-Driven Generation (TDG)** is the pattern of breaking the coding process into distinct, sequential phases:
1.  **Implement**: Generate the core logic based on a specification and language-specific conventions.
2.  **Review**: Have the model (or a second model) audit the code for common errors or style violations.
3.  **Refine**: Fix any issues found during the review.
4.  **Test**: Generate unit tests that specifically target the refined implementation.
5.  **Verify**: Perform a final static check to ensure the generated code and tests are syntactically valid.

The SQL analogy is a **Stored Procedure with Unit Tests**. You aren't just writing logic; you are building a "Contract." The implementation is the promise, and the tests are the proof that the promise is kept.

The Code Gen + Tests recipe (Recipe 30) implements this robust lifecycle. It allows you to specify a task (e.g., "Binary search") and a language (e.g., "Go"), and it handles all the details of formatting, conventions, and test framework selection automatically.

---

## The SPL Approach

This recipe demonstrates **Contextual Pipelining**—passing the implementation as a variable directly into the test generation step to ensure perfect alignment.

---

## The .spl File (Annotated)

```spl
-- Recipe 30: Code Generator + Tests
-- Generate logic, then generate tests — in a single workflow.

WORKFLOW code_gen_with_tests
    INPUT: @spec TEXT, @language TEXT DEFAULT 'Python'
DO
    -- Phase 1: Implementation
    GENERATE implement_function(
        @spec,
        @language,
        language_conventions(@language)           -- (1) Injecting Style Guides
    ) INTO @implementation

    -- Phase 2: Self-Review
    GENERATE review_implementation(@implementation) INTO @notes

    EVALUATE @notes
        WHEN contains('issue') THEN
            GENERATE fix_implementation(@implementation, @notes) INTO @implementation
    END

    -- Phase 3: Test Generation
    GENERATE generate_tests(
        @implementation,                          -- (2) Passing code as context
        @spec,
        @language,
        test_framework_guide(@language)           -- (3) Choosing the runner
    ) INTO @tests

    -- Phase 4: Assembly
    GENERATE assemble_output(@implementation, @tests) INTO @final_output
    COMMIT @final_output WITH status = 'complete'
END
```

### (1) Injecting Style Guides (`language_conventions`)

We don't hardcode "use PEP 8" in the prompt. Instead, we use a `CREATE FUNCTION` that returns the correct standards based on the `@language` parameter. 
- If `@language="Go"`, it injects "Return (value, error) and use table-driven tests."
- If `@language="Python"`, it injects "Use type hints and Google-style docstrings."

### (2) Passing Code as Context

In the `generate_tests` step, we pass the `@implementation` variable. 
- **Why?** This ensures the tests are "Implementation-Aware." The LLM sees the actual function names, argument names, and logic paths it just wrote, allowing it to write tests that actually work.

### (3) Choosing the Runner (`test_framework_guide`)

Just as we inject style guides, we inject framework instructions. If the user wants Go, we tell the LLM to use the standard `testing` package. If they want Python, we point them toward `pytest`. This prevents the model from hallucinating a "generic" test format that doesn't run.

---

## Running It

Generate a Python function for email validation:

```bash
spl run cookbook/30_code_gen/code_gen.spl --adapter ollama \
    spec="A function that validates an email address using regex" \
    language="Python"
```

Then, try a complex algorithm in Go:

```bash
spl run cookbook/30_code_gen/code_gen.spl --adapter ollama \
    spec="Binary search over a sorted list, return index or -1" \
    language="Go" \
    test_framework="testing"
```

---

## What Just Happened

**LLM calls: 4–6.** (Implement, Review, [Fix], Test, Verify, Assemble)

The "Conductor" (SPL Runtime) managed a "Full-Stack Developer":
1.  **Interpreted** the technical requirement.
2.  **Enforced** the language-specific style guide.
3.  **Audited** its own work for bugs.
4.  **Covered** the logic with relevant unit tests.
5.  **Packaged** the result into a single, cohesive file.

---

## Reproducibility Note

The stability of code generation is very high for standard algorithms but lower for niche libraries. 

On a **GTX 1080 Ti**, the entire process takes **40–80 seconds**. This is significantly faster than a human writing both the code and the tests from scratch, and it ensures that the "Boring" part of development—writing boilerplate tests—is never skipped.

---

## When to Use This Pattern

Use the **Code Gen + Tests** pattern when:
- **Greenfield Development**: Quickly scaffolding new utility functions.
- **Legacy Refactoring**: Porting a function from one language to another while ensuring the logic remains identical (via tests).
- **Prototyping**: Exploring different algorithm implementations and seeing how they pass a set of edge cases.

---

## Exercises

1.  **Add a "Docstring" Pass.** Add a step between Implementation and Review that specifically asks the model to "Generate a detailed README section for this function."
2.  **Add a "Complexity" Check.** (Advanced) Add a Python tool that runs a static analyzer (like `radon` for Python) on the `@implementation`. If the cyclomatic complexity is too high, trigger a `refactor` step.
3.  **Switch Frameworks.** Run the recipe for Python but override the `test_framework` to `unittest`. Observe how the model changes its test class structure.
