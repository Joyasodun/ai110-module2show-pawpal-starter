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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

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

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
