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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
