# Interview Sim

*"To master a skill, you must first survive the simulation."*

---

## The Pattern

High-stakes interactions—like job interviews, sales pitches, or crisis management—require more than just knowledge. They require "Grace Under Pressure." The best way to prepare for these moments is through simulation. But human-led simulation is expensive and time-consuming. You need a partner who can play a specific role, stay in character, and provide objective feedback after the session.

The **Interactive Interview Simulation** pattern uses multiple LLM instances to create a "closed-loop" training environment. 
1.  **Interviewer**: One model instance plays the role of a professional interviewer, asking probing technical questions.
2.  **Candidate**: A second model instance (the "Dummy Candidate") answers the questions to test the interview's difficulty.
3.  **Evaluator**: A third model instance (the "Judge") reviews the entire transcript and scores it based on a professional rubric.

The SQL analogy is a **Three-Way Join with an Audit Log**. You are joining the "Interviewer Persona" with the "Candidate Persona" over a series of "Turn IDs," and then auditing the resulting "Conversation Table" for quality and consistency.

The Interview Sim recipe (Recipe 33) implements this triad. It allows you to simulate technical interviews for any role (Senior SWE, Data Scientist, etc.) and provides a structured evaluation report that highlights strengths and weaknesses.

---

## The SPL Approach

This recipe demonstrates **Multi-Role Orchestration**—managing three distinct personas in a single workflow while using deterministic tools to aggregate scores.

---

## The .spl File (Annotated)

```sql
-- Recipe 33: Interview Simulator
-- Two-persona structured Q&A with evaluation.

WORKFLOW interview_sim
    INPUT: @role TEXT, @focus TEXT, @candidate_profile TEXT
DO
    -- Phase 1: Planning
    GENERATE generate_questions(@role, @focus) INTO @questions_json -- (1) Upfront Planning

    -- Phase 2: The Interview (Sequential Generation)
    CALL extract_question(@questions_json, 1) INTO @q1
    GENERATE answer(@q1, @candidate_profile) INTO @a1 -- (2) Role-play generation
    
    CALL extract_question(@questions_json, 2) INTO @q2
    GENERATE answer(@q2, @candidate_profile) INTO @a2

    -- Phase 3: Evaluation (The Judge)
    GENERATE score(@q1, @a1, evaluation_rubric()) INTO @score1 -- (3) Applying the Rubric
    GENERATE score(@q2, @a2, evaluation_rubric()) INTO @score2

    -- Phase 4: Aggregation (Deterministic)
    CALL aggregate_scores(@score1, @score2) INTO @totals -- (4) Python Math Tool

    -- Phase 5: Synthesis
    GENERATE write_report(@totals, @role) INTO @final_report
    COMMIT @final_report WITH status = 'complete'
END
```

### (1) Upfront Planning (`generate_questions`)

Instead of asking one question at a time, we ask the "Interviewer" model to generate a set of three questions upfront. 
- **Why?** This ensures the interview has a logical flow (e.g., easy → medium → hard) rather than being a random list of disconnected queries.

### (2) Role-play Generation

When the "Candidate" model answers, it doesn't just give the "right answer." It answers based on its `@candidate_profile`. If the profile says "Junior Developer," the model might give a shallow answer or admit it doesn't know. 
- This creates a **Realistic Simulation**. We aren't just testing the facts; we are testing the interaction.

### (3) Applying the Rubric (`evaluation_rubric`)

We use a formal JSON rubric to score the answers. This ensures that the evaluation is objective and consistent across different interview runs. We score dimensions like "Technical Accuracy," "Communication," and "Experience."

### (4) Python Math Tool (`aggregate_scores`)

As always, we hand the numbers back to Python. Python sums the scores, calculates the average, and flags any "Red Flags" found in the JSON feedback. This ensures the final `@totals` are mathematically perfect.

---

## Running It

Run a simulation for a Senior SWE role:

```bash
spl run cookbook/33_interview_sim/interview_sim.spl \
    --adapter ollama --tools cookbook/33_interview_sim/tools.py \
    role="Senior Software Engineer" focus="Distributed Systems" \
    candidate_id="alice_senior_swe"
```

Expected output: A full transcript of the three-question interview, followed by a structured evaluation report with a total score (e.g., 32/40) and specific feedback for the candidate.

---

## What Just Happened

**LLM calls: 8–10.** (Question set + 3 answers + 3 scores + 1 final report)
**Tool calls: 5.** (Role loading, Candidate loading, Question extraction, Score aggregation)

The "Conductor" (SPL Runtime) managed a "HR Assessment Center":
1.  **Sourced** the correct expertise (Role Context).
2.  **Choreographed** a three-turn dialogue between two distinct personas.
3.  **Audited** every turn against a professional standard.
4.  **Calculated** the performance metrics.
5.  **Synthesized** a comprehensive hiring recommendation.

---

## Reproducibility Note

This recipe is highly stable because the questions are generated upfront. The variability comes from the "Candidate's" responses. 

On a **GTX 1080 Ti**, a full simulation takes **60–90 seconds**. This is an incredible tool for **Interview Preparation** or for **Hiring Managers** to test their own question sets before using them on real candidates.

---

## When to Use This Pattern

Use the **Interview Sim** pattern when:
- **Personal Coaching**: Preparing for a specific job or a high-stakes presentation.
- **Content Generation**: Creating "Synthetic Transcripts" for training materials or educational videos.
- **Model Evaluation**: Testing how different models perform in a specific persona (e.g., "How does Llama 3 handle being a CEO vs. a Developer?").

---

## Exercises

1.  **Add a "Live" mode.** (Advanced) Modify the workflow to replace the `@candidate_profile` with a `context.user_response` parameter, allowing a real human to type the answers in a terminal while the AI asks the questions.
2.  **Change the Difficulty.** Add a `@difficulty` parameter to the `interviewer_persona` and observe how the questions change from "basic syntax" to "architectural trade-offs."
3.  **Stress Test.** Give the "Candidate" a profile that says "You are very defensive and don't like being questioned." Observe how the "Interviewer" handles the conflict.
