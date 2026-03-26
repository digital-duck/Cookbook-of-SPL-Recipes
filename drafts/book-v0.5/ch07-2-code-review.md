# Code Review

<!-- *"A second pair of eyes is good; a second, third, and fourth pair of specialized eyes is better." — Wen Gong* -->

<!-- --- -->

## The Pattern

In professional software development, code review is the primary defense against bugs, security vulnerabilities, and technical debt. But manual review is slow, subjective, and prone to human fatigue. A reviewer might catch a logic bug but miss a subtle security flaw, or focus on code style while overlooking a performance bottleneck.

**Automated Multi-Pass Review** solves this by breaking the review into specialized "audits." Instead of one generic "review this code" prompt, you run the code through several distinct passes:
1.  **Security Audit**: Look specifically for injections, leaked secrets, and unsafe functions.
2.  **Performance Check**: Identify inefficient loops, redundant allocations, and slow I/O.
3.  **Style & Best Practices**: Verify adherence to language-specific conventions (e.g., PEP 8 for Python).
4.  **Bug Detection**: Search for logic errors, edge cases, and unhandled exceptions.

The SQL analogy is **Multi-Constraint Validation** or **Static Analysis Rules**. You don't just check if the data "looks okay"; you run it against a suite of specific rules (foreign keys, check constraints, unique indexes) to ensure total integrity.

The Code Review recipe (section 8.3) implements this multi-pass strategy. It scores each category for "Severity" and uses those scores to decide whether to `approve`, `request_changes`, or `block` the code—bringing the discipline of a senior engineer to an automated pipeline.

<!-- --- -->

## The SPL Approach

This recipe demonstrates **Pass-by-Pass Analysis** and **Threshold-Based Branching** using numeric evaluation.

<!-- --- -->

## The .spl File (Annotated)

```spl
-- Recipe 15: Automated Code Review
-- Multi-pass code review: security, performance, style, then synthesis.

WORKFLOW code_review
    INPUT: @code TEXT, @language TEXT
DO
    -- Pass 1-4: Specialized Audits
    GENERATE security_audit(@code, @language) INTO @security_findings -- (1) Specialized Pass
    GENERATE performance_review(@code, @language) INTO @perf_findings
    GENERATE style_review(@code, @language) INTO @style_findings
    GENERATE bug_detection(@code, @language) INTO @bug_findings

    -- Severity scoring (Turning prose into numbers)
    GENERATE severity_score(@security_findings) INTO @sec_score      -- (2) Quantifying Risk
    GENERATE severity_score(@perf_findings) INTO @perf_score
    GENERATE severity_score(@bug_findings) INTO @bug_score

    -- Synthesize all findings
    GENERATE synthesize_review(...) INTO @review

    -- Phase 5: Automated Verdict
    EVALUATE @sec_score                                             -- (3) Threshold Branching
        WHEN > 8 THEN
            COMMIT @review WITH status = 'critical_issues', verdict = 'block'
        WHEN > 5 THEN
            COMMIT @review WITH status = 'needs_fixes', verdict = 'request_changes'
        OTHERWISE
            COMMIT @review WITH status = 'approved', verdict = 'approve'
    END
END
```

### (1) Specialized Passes

Each `GENERATE` call uses a focused prompt. By asking the model to *only* look for security issues, we reduce the noise from style or performance concerns. This results in much higher "Recall" (finding actual bugs) than a single-pass review.

### (2) Quantifying Risk (`severity_score`)

LLMs are great at prose, but systems are better at numbers. We use a middle step to "quantify" the findings. We ask the model: "On a scale of 1–10, how severe are these security findings?" This turns a subjective text block into a objective metric that the `WORKFLOW` can act upon.

### (3) Threshold Branching

This is where the automation takes action. We use the `@sec_score` to drive the `EVALUATE` block. 
- If a critical security flaw is found (score > 8), we `block` the code immediately. 
- If issues are moderate, we `request_changes`. 
- Only if the score is low do we `approve`.

SQL Analogy: A **Trigger with a Threshold**. If a transaction amount exceeds a limit, the trigger blocks the insert; otherwise, it allows it to proceed.

<!-- --- -->

## Running It

Review a Python file with a known security flaw:

```bash
spl run cookbook/15_code_review/code_review.spl --adapter ollama \
    code="def run_cmd(user_input): eval(user_input)" \
    language="Python"
```

Expected result: The `security_audit` will flag the `eval()` call, the `@sec_score` will be high (likely 9 or 10), and the final `verdict` will be `block`.

<!-- --- -->

## What Just Happened

**LLM calls: 8.** (4 audits + 3 scores + 1 synthesis)

The "Conductor" (SPL Runtime) acted as a Senior Reviewer:
1.  **Decomposed** the review into four logical dimensions.
2.  **Analyzed** the code from four different perspectives.
3.  **Measured** the risk in each dimension.
4.  **Synthesized** a final report.
5.  **Decided** on a binding verdict based on the measured risk.

<!-- --- -->

## Reproducibility Note

The scoring step (`severity_score`) is the most sensitive part of this recipe. Different models have different "scales" of what they consider severe. 

On a **GTX 1080 Ti**, a full 8-call review takes **60–120 seconds**. This is slower than a human scan but much faster (and more thorough) than a human deep-dive review.

<!-- --- -->

## When to Use This Pattern

Use the **Code Review** pattern when:
- **Pre-Commit Hooks**: Automatically block unsafe code from being committed to your repository.
- **CI/CD Quality Gates**: Add a "Generative Linting" step to your build pipeline.
- **Learning Tool**: Use it to get feedback on your own code as you learn a new language.

<!-- --- -->

## Exercises

1.  **Add a "Fixer" step.** If the verdict is `request_changes`, add a step that tries to generate a "Fixed" version of the code and includes it in the final review.
2.  **Language-Specific Rules.** Modify the `security_audit` prompt to look for specific flaws in specific languages (e.g., "Buffer overflows" in C++, "SQL Injection" in PHP).
3.  **Parallel Audits.** (Advanced) Use the `WITH` clause (Chapter 9.1) to run all four audit passes in parallel, significantly reducing the total execution time.
