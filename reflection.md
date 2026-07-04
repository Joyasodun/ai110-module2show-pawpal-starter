# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML design had four classes:

- **Pet** — holds basic info about a pet (`name`, `species`) and its care `preferences`. Its job is to represent a single animal and report what it likes (`get_preferences()`).

- **Owner** — represents the pet owner. It tracks the owner's `name`, the `pets` they have, and the hours they're `available`. It's responsible for managing pets (`add_pet()`) and reporting availability (`get_availability()`).

- **Task** — represents one care task to be done, with a `todo` description, an `importance` level, and a `status`. Its responsibility is to track whether the task is finished (`mark_done()`).

- **PetCare** — tracks the actual care state for a pet: what `food` and how many `ounces`, plus whether the pet has been `fed`, given a `shower`, and a `walk`. It's responsible for recording feedings (`feed()`) and reporting whether all care is complete (`all_done()`).

The Owner owns many Pets and plans many Tasks, each Pet has one PetCare record, and completing a Task updates the PetCare state.

**b. Design changes**

Yes. After reviewing my class skeleton I found gaps that would have blocked the scheduling logic, so I made several changes:

- **Linked Task to Pet.** Originally a Task was just a description with no idea which pet it belonged to, so an owner with two pets couldn't tell whose walk was whose. I added a `pet` reference to Task.

- **Added a Scheduler class.** My first four classes (Pet, Owner, Task, PetCare) stored data but nothing actually built or explained a plan, which is the whole point of the app. I added a `Scheduler` class with `build_schedule()` and `explain_plan()` to own that logic.

- **Gave Task a duration and a clear importance scale.** I added `duration_minutes` because you can't fit tasks into the owner's available time without knowing how long each takes, and I defined `importance` as 1–5 (higher = more urgent) so the scheduler can sort consistently.

- **Connected Task to PetCare.** I added a `care_type` field ("feed"/"walk"/"shower") so finishing a task can update the matching flag in PetCare, instead of the two classes being disconnected.

- **Cleaned up Task status.** I replaced the free-form `status` string with a simple `done` boolean to avoid typos like "Done" vs "complete" silently breaking comparisons, and gave Owner a `tasks` list plus `add_task()` so it can actually hold the tasks it plans.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

One tradeoff my scheduler makes is that its conflict detection (`detect_conflicts()`) only flags tasks that share the **exact same start time**, not tasks whose **durations overlap**. It groups tasks by their `"HH:MM"` start string and warns when two land on the same time. So a 30-minute walk at 08:00 and a feeding at 08:15 truly collide in real life, but because their start times differ, my scheduler stays silent. Catching true overlaps would mean comparing each task's `[start, start + duration)` interval against every other task's interval.

This tradeoff is reasonable for this scenario because the goal is a *lightweight* warning, not a guarantee. The exact-match check is simple, fast (one pass with a dictionary), and easy to read, and it already catches the most common and most confusing case — two things booked for the same moment. Full interval-overlap checking adds noticeably more logic for a pet-care planner where the owner can still eyeball the printed schedule and adjust. I'd rather ship the simple, correct-for-its-scope version and note the limitation than add complexity the scenario doesn't demand. (This mirrors a second, related tradeoff: `detect_conflicts()` reports problems as warning strings and never raises or drops a task, so the program keeps running and the owner decides what to do.)

---

## 3. AI Collaboration

**a. How you used AI**

I used AI throughout the build, but in small, controlled steps rather than asking it to write the whole system at once. The most useful pattern was asking for a *menu of incremental improvements* first ("suggest small, beginner-friendly upgrades to my scheduler") and then picking one at a time — real clock times, per-slot packing, preference matching, recurrence, conflict detection — so I always understood each change before moving on.

The prompts that helped most were the specific, scoped ones:

- "How could this algorithm be simplified for better readability or performance?" (on a single method)
- "What are the most important edge cases to test for a pet scheduler with sorting and recurring tasks?"
- "Based on my final implementation, what updates should I make to my UML diagram?"

I also used AI for the mechanical parts — drafting docstrings, wiring the Streamlit UI to my Scheduler methods, and generating a test plan — which freed me to focus on the logic decisions.

**b. Judgment and verification**

One clear moment: when I asked AI to simplify my `detect_conflicts()` method, it suggested two changes — switching my manual `dict` + `setdefault` grouping to `collections.defaultdict`, and collapsing the whole warning-building loop into a single list comprehension. I **accepted the `defaultdict` change** (it's a clean, standard idiom with no readability cost) but **rejected the one-line comprehension**: chaining an f-string with `+ ", ".join(...) + "."` inside a comprehension was denser and harder to read, and this is a learning codebase where clarity matters more than terseness. Pythonic isn't automatically better.

I verified AI suggestions two ways. First, I ran the code — every feature was checked against `main.py` output and the test suite, and I caught a real bug this way: my preference logic leaked a pet's "evening walks" preference onto *every* task for that pet (including feeding), which I only saw by tracing actual output. Second, for the UML and test-plan questions I ran the AI review in a fresh, context-free session so it evaluated the final code on its own merits rather than agreeing with earlier conversation.

---

## 4. Testing and Verification

**a. What you tested**

I wrote 12 automated tests (`tests/test_pawpal.py`, run with `python -m pytest`) covering the core behaviors:

- **Basic model** — marking a task done; adding a task to a pet.
- **Time-slot packing** — tasks get sequential `"HH:MM"` start times; a task too big for any slot is dropped *without blocking* the tasks after it; and `build_schedule()` never disagrees with the timed view.
- **Preferences** — a time-of-day preference biases the matching task into its window (and only that task).
- **Sorting correctness** — `sort_by_time()` returns tasks in chronological order regardless of the order they were added.
- **Recurrence** — completing a daily task creates a next-day copy (with `done` reset and no stale time), weekly advances one week, and `once` does not repeat.
- **Conflict detection** — same-start-time tasks produce a warning naming both; distinct/unscheduled times produce none.

These were important because they are exactly the "smart" behaviors that are easy to break silently — an off-by-one in slot packing, a sign flip in the sort key, or a stale time on a recurring copy would all produce a wrong schedule without throwing an error. Tests catch those regressions the moment they happen.

**b. Confidence**

**Confidence: 4 out of 5.** All 12 tests pass and every core algorithm has direct coverage, so I'm confident the happy paths and the main edge cases work. I hold back the fifth star because a few edge cases are documented but not yet tested: the exact-slot-fit boundary (a task that fills a slot to the minute), `next_occurrence()` when a task has no due date, month/year rollover for recurrence, and combined `filter_tasks()` filters.

If I had more time, those are exactly the tests I'd add next, along with a test that documents the known conflict-detection limitation: it only flags *exact* same-start-time clashes, not *overlapping durations* (a 30-minute task at 08:00 and a task at 08:15 truly overlap but aren't flagged).

---

## 5. Reflection

**a. What went well**

I'm most satisfied with how the scheduler grew from a naive "sort by importance and greedily pack minutes" into something that assigns real clock times, respects preferences, handles recurrence, and warns about conflicts — all while staying readable. Building it one small feature at a time, with a test locking in each behavior before moving on, meant I never had a big broken mess to untangle. The `explain_plan()` output also makes the system's decisions transparent, which I like.

**b. What you would improve**

Two things. First, `PetCare` ended up disconnected from the rest of the system — the design intended completing a task to update a pet's care state (via `care_type`), but that link was never wired up. I'd either implement it or remove the class so the code and UML match reality. Second, I'd upgrade conflict detection from exact-time matching to true interval-overlap detection, since real scheduling conflicts are about overlapping durations, not identical start times.

**c. Key takeaway**

The biggest thing I learned is that working with AI is most effective when *I* stay the decision-maker: scoping changes small, reading and running everything it produces, and rejecting suggestions that don't fit — like the "more Pythonic" one-liner that hurt readability. AI is fast at drafting and spotting edge cases, but verifying against real output (which is how I caught the preference bug) and knowing why each piece exists is what actually made the system reliable.

---

## 6. AI Strategy

**a. Which AI coding assistant features were most effective for building your scheduler?**

Three features did the most work for me. **Agent/automatic editing mode** let the assistant make coordinated multi-file changes — for example, adding recurrence touched `Task`, the `Scheduler`, `main.py`, and the tests together, which would have been tedious to keep in sync by hand. **The chat, used on one specific method at a time**, was best for reasoning ("how do I sort `"HH:MM"` strings with a lambda key?", "how does `timedelta` handle month rollover?") because the answers were focused and I could follow them. And **running the code and tests inside the workflow** meant I could verify each change immediately instead of guessing whether it worked.

**b. One AI suggestion you rejected or modified to keep your design clean**

When I asked the assistant to simplify `detect_conflicts()`, it offered to collapse the whole warning-building loop into a single list comprehension with an inline f-string and `", ".join(...)`. It was shorter and technically more "Pythonic," but it packed the logic into one dense line that was hard to read. I rejected that part and kept my explicit `for` loop, adopting only the smaller `defaultdict` change that improved clarity without costing it. Readability beat cleverness.

**c. How did using separate chat sessions for different phases help you stay organized?**

Keeping sessions separate stopped context from bleeding between phases. I planned the algorithms in one session, then ran the *testing* work in a fresh session so the assistant would think about edge cases from scratch rather than just defending code it had already written. I did the same for the UML review — a clean, context-free session evaluated my final `pawpal_system.py` on its own merits and honestly flagged that my `PetCare` class was disconnected, something a session invested in the earlier work might have glossed over. Fresh sessions gave me more independent, less biased feedback.

**d. What you learned about being the "lead architect" when collaborating with powerful AI tools**

The AI is a very fast implementer, but it will happily build the wrong thing well, or optimize for the wrong quality (terseness over readability). Being the lead architect meant I owned the decisions: what to build and in what order, which suggestions to accept, and — most importantly — verifying the output against reality instead of trusting it. The clearest proof was catching the preference-leak bug by reading actual `main.py` output; the code *ran* and looked plausible, but only a human checking behavior against intent noticed it was wrong. AI amplified how fast I could work, but the judgment about whether the system was actually correct and well-designed had to stay with me.
