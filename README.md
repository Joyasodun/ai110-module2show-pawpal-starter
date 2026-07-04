# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

PawPal+ implements the following algorithms and behaviors (see [Smarter Scheduling](#-smarter-scheduling) for method-level detail):

- **Time-aware scheduling** — packs tasks into the owner's real availability hours (60-minute slots), assigning each a concrete `"HH:MM"` start time instead of a bare ordered list.
- **Priority ordering** — tasks are placed most-important-first, with shorter tasks breaking ties so quick wins come earlier.
- **Sorting by time** — the daily plan is returned in chronological order.
- **Filtering** — tasks can be filtered by completion status and/or by pet.
- **Preference matching** — a pet's time-of-day preference (e.g. "evening walks") biases the matching task toward that window.
- **Conflict warnings** — the scheduler flags tasks booked at the same start time and reports a clear warning (without crashing).
- **Daily & weekly recurrence** — completing a recurring task automatically creates its next occurrence (next day / next week), while one-off tasks do not repeat.
- **Explainable plans** — every scheduled task comes with a plain-English reason for its placement.
- **Tested** — 12 automated tests cover sorting, recurrence, conflict detection, slot packing, and filtering.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Terminal output from running `python main.py`:

```
========================================
           TODAY'S SCHEDULE
========================================
Care plan for Alex:
1. Morning walk for Rex (importance 5, 30 min) — scheduled because it is among the most urgent tasks that fit the available time.
2. Feed Mochi for Mochi (importance 4, 5 min) — scheduled because it is among the most urgent tasks that fit the available time.
3. Breakfast feeding for Rex (importance 4, 10 min) — scheduled because it is among the most urgent tasks that fit the available time.
4. Litter box cleanup for Mochi (importance 3, 15 min) — scheduled because it is among the most urgent tasks that fit the available time.
========================================
```

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

### What the tests cover

The suite (12 tests in `tests/test_pawpal.py`) verifies the core scheduling behaviors:

- **Basic model** — marking a task done, and adding a task to a pet.
- **Time-slot packing** — tasks get sequential `"HH:MM"` start times, a task too big for any slot is dropped without blocking others, and `build_schedule()` never disagrees with the timed view.
- **Preferences** — a time-of-day preference biases the matching task into its window.
- **Sorting correctness** — `sort_by_time()` returns tasks in chronological order regardless of add/importance order.
- **Recurring tasks** — completing a daily task creates a next-day copy (with `done` reset and no stale time), weekly advances one week, and `once` does not recur.
- **Conflict detection** — tasks sharing a start time produce a warning naming both; distinct/unscheduled times produce none.

### Successful test run

```
============================= test session starts ==============================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0
rootdir: /Users/johnoyasodun/CodePath/ai110-module2show-pawpal-starter
collected 12 items

tests/test_pawpal.py ............                                        [100%]

============================== 12 passed in 0.01s ==============================
```

### Confidence Level

⭐⭐⭐⭐☆ (4 / 5)

All 12 tests pass and cover every core behavior — sorting, recurrence, conflict detection, slot packing, and filtering paths. I hold back the fifth star because a few edge cases are documented but not yet tested: exact-slot-fit boundaries, `next_occurrence()` with no due date, month/year rollover for recurrence, and combined `filter_tasks()` filters. The known limitation that conflict detection catches only exact same-time clashes (not overlapping durations) also caps full confidence.

## 📐 Smarter Scheduling

Beyond a basic priority sort, PawPal+ implements several "smarter" scheduling features. Each is listed below with the method that implements it (all in `pawpal_system.py`).

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Returns the scheduled `Task` objects ordered by their assigned start time. |
| Filtering | `Scheduler.filter_tasks()` | Filters by completion status (`done=True/False`) and/or `pet_name` (case-insensitive). |
| Conflict detection | `Scheduler.detect_conflicts()` | Warns about same-start-time clashes. |
| Recurring tasks | `Scheduler.mark_task_complete()` + `Task.next_occurrence()` | Completing a daily/weekly task auto-creates its next occurrence. |
| Time-aware scheduling | `Scheduler.build_timed_schedule()` | Packs tasks into real 60-min availability slots and stamps each with an `"HH:MM"` start. |

### Sorting behavior — `Scheduler.sort_by_time()`

The scheduler stamps each scheduled task with a start time in `"HH:MM"` form on `task.time`. `sort_by_time()` sorts those `Task` objects with `sorted(..., key=lambda task: task.time)`. Because zero-padded `"HH:MM"` strings sort the same way alphabetically as chronologically (`"08:30" < "12:00" < "18:05"`), sorting the raw string needs no date parsing.

### Filtering behavior — `Scheduler.filter_tasks(done=None, pet_name=None)`

Filters the owner's tasks by completion status and/or pet name. Pass `done=True` for completed tasks or `done=False` for pending ones; pass `pet_name` (case-insensitive) to keep only one pet's tasks. Either argument may be omitted; with none, it returns every task.

### Conflict detection logic — `Scheduler.detect_conflicts()`

A lightweight strategy: it groups every task that has an assigned start time by that `"HH:MM"` string, and any time claimed by more than one task produces a warning message. It works across the same pet *or* different pets. It only **reports** conflicts as human-readable strings — it never raises an exception or drops a task, so the program keeps running. **Tradeoff:** it flags only *exact* same-start-time clashes, not *overlapping durations* (a 30-min task at 08:00 and a task at 08:15 truly overlap but aren't flagged).

### Recurring task logic — `Scheduler.mark_task_complete()` and `Task.next_occurrence()`

When a `"daily"` or `"weekly"` task is completed via `mark_task_complete()`, it is marked done and a fresh, not-done copy is automatically created for the next occurrence and registered on the owner. `Task.next_occurrence()` computes the new due date with `datetime.timedelta` — `timedelta(days=1)` for daily, `timedelta(weeks=1)` for weekly — which correctly handles month and year boundaries. A `"once"` task returns `None` and does not repeat.

## 🎬 Demo Walkthrough

### Main UI features (Streamlit)

Run the app with `streamlit run app.py`. The interface lets a pet owner:

- **Enter owner and pet info** — owner name, pet name, and species.
- **Set availability** — pick which parts of the day you're free (Morning 8 AM–12 PM, Afternoon 12–7 PM, Evening 7 PM–12 AM). Tasks are scheduled into these windows, and times display in 12-hour AM/PM format.
- **Add tasks** — each with a title, duration (minutes), and importance (1–5, higher = more urgent).
- **View current tasks in a table**, with a **"Filter by pet"** dropdown that uses `Scheduler.filter_tasks()` to narrow the list to a single pet. A ✅/⬜️ column shows completion status.
- **Generate today's schedule** — a single button builds the timed plan.

### Example workflow

1. Enter the owner ("Alex") and add a pet ("Rex", a dog).
2. Add a few tasks — e.g. a 30-min "Morning walk" (importance 5) and a 10-min "Breakfast feeding" (importance 3).
3. Add a second pet ("Mochi", a cat) and a task for it, then use **Filter by pet** to view just one pet's tasks.
4. Click **Generate schedule** to see today's plan.

### Key Scheduler behaviors shown in the UI

- **Sorting** — the generated schedule is displayed as a table ordered by clock time (`Scheduler.sort_by_time()`).
- **Conflict warnings** — if two tasks share a start time, an `st.warning` appears **above** the schedule naming both clashing tasks and the time, so the owner knows exactly what to reschedule. The plan still renders — a conflict never crashes the app.
- **Success feedback** — an `st.success` banner confirms how many tasks were scheduled.
- **Explanations** — an expandable "Why was each task scheduled?" panel shows the plain-English reasoning from `Scheduler.explain_plan()`.

### Sample CLI output

The terminal demo shows the same logic end-to-end:

```bash
python main.py
```

```
========================================
           TODAY'S SCHEDULE
========================================
Care plan for Alex:
1. 8:00 AM — Morning walk for Rex (importance 5, 30 min) — scheduled at 8:00 AM to match its preferred time of day.
2. 8:30 AM — Feed Mochi for Mochi (importance 4, 5 min) — scheduled at 8:30 AM because it is among the most urgent tasks that fit.
3. 8:35 AM — Breakfast feeding for Rex (importance 4, 10 min) — scheduled at 8:35 AM to match its preferred time of day.
4. 8:45 AM — Litter box cleanup for Mochi (importance 3, 15 min) — scheduled at 8:45 AM because it is among the most urgent tasks that fit.
========================================
        SCHEDULE SORTED BY TIME
========================================
8:00 AM  Morning walk (Rex)
8:30 AM  Feed Mochi (Mochi)
8:35 AM  Breakfast feeding (Rex)
8:45 AM  Litter box cleanup (Mochi)
========================================
              FILTERS
========================================
Pending tasks (4):
  - Morning walk for Rex
  - Litter box cleanup for Mochi
  - Breakfast feeding for Rex
  - Feed Mochi for Mochi
Completed tasks (1):
  - Evening walk for Rex
Tasks for Rex (3):
  - Evening walk
  - Morning walk
  - Breakfast feeding
========================================
        RECURRENCE ON COMPLETE
========================================
Before: Breakfast feeding due 2026-07-04, done=False
After:  Breakfast feeding done=True
New occurrence created: Breakfast feeding due 2026-07-05
========================================
           CONFLICT CHECK
========================================
⚠️ Conflict at 09:00: 2 tasks scheduled at the same time — Give medicine (Rex), Brush Mochi (Mochi).
========================================
```
