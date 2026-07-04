# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I used an AI agent (Claude Code) to extend my scheduler across several multi-step tasks — adding real clock-time scheduling, per-slot packing, preference matching, recurring tasks, and conflict detection — each of which touched multiple files (`pawpal_system.py`, `main.py`, `tests/test_pawpal.py`, and later `app.py`, `README.md`, and the UML). I also asked it to run two focused, isolated sub-agent sessions: one to produce an edge-case test plan, and one to review my final code against my UML diagram.

**What did the agent do?**

For each feature it edited the logic in `pawpal_system.py`, updated `main.py` to demonstrate the behavior, added tests, and ran `python -m pytest` and `python main.py` to confirm the change worked before moving on. For the UI step it rewired `app.py` to call my Scheduler methods (`sort_by_time()`, `filter_tasks()`, `detect_conflicts()`) using `st.table`, `st.success`, and `st.warning`. It spawned separate context-free sub-agents to (a) generate a ranked edge-case test plan and (b) list the exact UML deltas needed, then applied the results (e.g. writing `diagrams/uml_final.mmd`).

**What did you have to verify or fix manually?**

I verified every change by reading the diffs and checking the actual terminal output, not just trusting that it ran. This caught a real bug: the preference logic was leaking a pet's "evening walks" preference onto *every* task for that pet (including feeding), which only showed up in the printed schedule. I also overrode the agent on a simplification suggestion (see SF11 below), and I had to reconcile the UML honestly — the agent correctly flagged that my `PetCare` class is disconnected from the rest of the code, so I marked that link as "planned" rather than pretending it existed.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Claude Code | Claude Code |
| **Prompt** | "How could this algorithm be simplified for better readability or performance?" (on `detect_conflicts()`) — took the grouping-idiom suggestion | Same prompt — took the "make it one list comprehension" suggestion |
| **Response summary** | Replace my manual `dict` + `setdefault` grouping with `collections.defaultdict(list)` | Collapse the whole warning-building loop into a single list comprehension with an inline f-string and `", ".join(...)` |
| **What was useful** | Cleaner, standard Python idiom; removes the `setdefault` boilerplate with no readability cost | Fewer lines; technically "more Pythonic" |
| **Problems noticed** | None — it's a well-known, readable idiom | Dense and hard to read: chaining `f"..." + ", ".join(...) + "."` inside a comprehension hides the logic and is easy to misread |
| **Decision** | **Accepted** | **Rejected** |

**Which approach did you use in your final implementation and why?**

I applied Option A (`defaultdict`) but rejected Option B. The one-line comprehension was shorter but noticeably harder to follow, and this is a learning codebase where readability matters more than terseness. This was a good reminder that "more Pythonic" is not automatically better — I kept the explicit `for` loop for the warning-building and only adopted the change that improved clarity without costing it.
