"""PawPal+ testing ground.

A small script to exercise the logic layer in pawpal_system.py and print a
human-readable daily care schedule to the terminal.

Run with: python main.py
"""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    # Create an owner with a few hours of availability.
    owner = Owner("Alex", available_hours=["08:00", "12:00", "18:00"])

    # Create at least two pets.
    rex = Pet("Rex", "dog", preferences=["morning walks", "chicken kibble"])
    mochi = Pet("Mochi", "cat", preferences=["quiet feeding spot"])
    owner.add_pet(rex)
    owner.add_pet(mochi)

    # Add tasks deliberately out of chronological order so we can see the
    # sorting method put them back in order.
    owner.add_task(Task("Evening walk", importance=3, duration_minutes=20, pet=rex, care_type="walk"))
    owner.add_task(Task("Morning walk", importance=5, duration_minutes=30, pet=rex, care_type="walk"))
    owner.add_task(Task("Litter box cleanup", importance=3, duration_minutes=15, pet=mochi, care_type="shower"))
    owner.add_task(Task("Breakfast feeding", importance=4, duration_minutes=10, pet=rex, care_type="feed", due_date=date.today()))
    owner.add_task(Task("Feed Mochi", importance=4, duration_minutes=5, pet=mochi, care_type="feed"))

    # Mark one task complete so the completion filter has something to filter.
    owner.get_all_tasks()[0].mark_done()  # "Evening walk" is now done

    # Build and print today's schedule.
    scheduler = Scheduler(owner)
    print("=" * 40)
    print("           TODAY'S SCHEDULE")
    print("=" * 40)
    print(scheduler.explain_plan())

    # Sorting: show scheduled tasks ordered by their "HH:MM" start time.
    print("=" * 40)
    print("        SCHEDULE SORTED BY TIME")
    print("=" * 40)
    for task in scheduler.sort_by_time():
        print(f"{task.time}  {task.todo} ({task.pet.name})")

    # Filtering: by completion status, then by pet name.
    print("=" * 40)
    print("              FILTERS")
    print("=" * 40)
    pending = scheduler.filter_tasks(done=False)
    print(f"Pending tasks ({len(pending)}):")
    for task in pending:
        print(f"  - {task.todo} for {task.pet.name}")

    completed = scheduler.filter_tasks(done=True)
    print(f"Completed tasks ({len(completed)}):")
    for task in completed:
        print(f"  - {task.todo} for {task.pet.name}")

    rex_tasks = scheduler.filter_tasks(pet_name="Rex")
    print(f"Tasks for Rex ({len(rex_tasks)}):")
    for task in rex_tasks:
        print(f"  - {task.todo}")
    print("=" * 40)

    # Recurrence: completing a daily task auto-creates tomorrow's occurrence.
    print("        RECURRENCE ON COMPLETE")
    print("=" * 40)
    breakfast = next(t for t in owner.get_all_tasks() if t.todo == "Breakfast feeding")
    print(f"Before: {breakfast.todo} due {breakfast.due_date}, done={breakfast.done}")
    next_task = scheduler.mark_task_complete(breakfast)
    print(f"After:  {breakfast.todo} done={breakfast.done}")
    if next_task is not None:
        print(f"New occurrence created: {next_task.todo} due {next_task.due_date}")
    print("=" * 40)

    # Conflict detection: two tasks pinned to the same start time.
    print("           CONFLICT CHECK")
    print("=" * 40)
    owner.add_task(Task("Give medicine", importance=5, duration_minutes=5, pet=rex, care_type="feed", time="09:00"))
    owner.add_task(Task("Brush Mochi", importance=2, duration_minutes=10, pet=mochi, care_type="shower", time="09:00"))
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(warning)
    else:
        print("No scheduling conflicts found.")
    print("=" * 40)


if __name__ == "__main__":
    main()
