"""PawPal+ testing ground.

A small script to exercise the logic layer in pawpal_system.py and print a
human-readable daily care schedule to the terminal.

Run with: python main.py
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    # Create an owner with a few hours of availability.
    owner = Owner("Alex", available_hours=["08:00", "12:00", "18:00"])

    # Create at least two pets.
    rex = Pet("Rex", "dog", preferences=["morning walks", "chicken kibble"])
    mochi = Pet("Mochi", "cat", preferences=["quiet feeding spot"])
    owner.add_pet(rex)
    owner.add_pet(mochi)

    # Add at least three tasks with different durations and importance.
    owner.add_task(Task("Morning walk", importance=5, duration_minutes=30, pet=rex, care_type="walk"))
    owner.add_task(Task("Breakfast feeding", importance=4, duration_minutes=10, pet=rex, care_type="feed"))
    owner.add_task(Task("Feed Mochi", importance=4, duration_minutes=5, pet=mochi, care_type="feed"))
    owner.add_task(Task("Litter box cleanup", importance=3, duration_minutes=15, pet=mochi, care_type="shower"))

    # Build and print today's schedule.
    scheduler = Scheduler(owner)
    print("=" * 40)
    print("           TODAY'S SCHEDULE")
    print("=" * 40)
    print(scheduler.explain_plan())
    print("=" * 40)


if __name__ == "__main__":
    main()
