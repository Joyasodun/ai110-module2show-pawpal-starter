"""Basic tests for the PawPal+ logic layer."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_task_completion():
    """Calling mark_done() should change the task's status to done."""
    pet = Pet("Rex", "dog")
    task = Task("Morning walk", importance=5, duration_minutes=30, pet=pet)

    assert task.done is False
    task.mark_done()
    assert task.done is True


def test_task_addition_increases_pet_task_count():
    """Adding a task to a Pet should increase that pet's task count."""
    pet = Pet("Mochi", "cat")
    assert len(pet.get_tasks()) == 0

    task = Task("Feed Mochi", importance=4, duration_minutes=5, pet=pet)
    pet.add_task(task)

    assert len(pet.get_tasks()) == 1


def test_timed_schedule_assigns_sequential_start_times():
    """Tasks packed into one slot should get back-to-back clock times."""
    owner = Owner("Alex", available_hours=["08:00"])
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    owner.add_task(Task("Walk", importance=5, duration_minutes=30, pet=pet))
    owner.add_task(Task("Feed", importance=4, duration_minutes=10, pet=pet))

    timed = Scheduler(owner).build_timed_schedule()

    assert [start for start, _ in timed] == ["08:00", "08:30"]
    assert [task.todo for _, task in timed] == ["Walk", "Feed"]


def test_oversized_task_is_dropped_without_blocking_others():
    """A task too big for any single 60-min slot is skipped, not a blocker."""
    owner = Owner("Alex", available_hours=["08:00"])
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    owner.add_task(Task("Huge grooming", importance=5, duration_minutes=90, pet=pet))
    owner.add_task(Task("Quick feed", importance=4, duration_minutes=10, pet=pet))

    scheduled = Scheduler(owner).build_schedule()
    titles = [task.todo for task in scheduled]

    assert "Huge grooming" not in titles
    assert "Quick feed" in titles


def test_build_schedule_matches_timed_schedule():
    """The ordered list and the timed view must never disagree on what fits."""
    owner = Owner("Alex", available_hours=["08:00", "12:00"])
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    owner.add_task(Task("Big", importance=5, duration_minutes=50, pet=pet))
    owner.add_task(Task("Medium", importance=4, duration_minutes=45, pet=pet))
    owner.add_task(Task("Small", importance=3, duration_minutes=10, pet=pet))

    scheduler = Scheduler(owner)
    from_schedule = scheduler.build_schedule()
    from_timed = [task for _, task in scheduler.build_timed_schedule()]

    assert from_schedule == from_timed


def test_preference_biases_matching_task_to_its_time_window():
    """An "evening walks" preference should push the walk into the evening slot.

    A non-matching task (feeding) should be unaffected and take the earliest
    slot, confirming the preference targets only its related activity.
    """
    owner = Owner("Alex", available_hours=["08:00", "18:00"])
    rex = Pet("Rex", "dog", preferences=["evening walks"])
    owner.add_pet(rex)
    owner.add_task(Task("Walk", importance=2, duration_minutes=30, pet=rex, care_type="walk"))
    owner.add_task(Task("Feed", importance=5, duration_minutes=10, pet=rex, care_type="feed"))

    timed = dict((task.todo, start) for start, task in Scheduler(owner).build_timed_schedule())

    assert timed["Walk"] == "18:00"
    assert timed["Feed"] == "08:00"


def test_completing_daily_task_creates_next_day_occurrence():
    """Completing a daily task auto-registers a copy due one day later."""
    owner = Owner("Alex")
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    task = Task("Feed", importance=5, duration_minutes=10, pet=pet,
                frequency="daily", due_date=date(2026, 7, 4))
    owner.add_task(task)

    scheduler = Scheduler(owner)
    new_task = scheduler.mark_task_complete(task)

    assert task.done is True
    assert new_task is not None
    assert new_task.done is False
    assert new_task.due_date == date(2026, 7, 5)
    assert new_task in owner.get_all_tasks()
    # The fresh copy must not inherit the original's stamped start time,
    # otherwise it would immediately clash with the completed task.
    assert new_task.time == ""


def test_completing_weekly_task_advances_by_one_week():
    """A weekly task's next occurrence is due seven days later."""
    pet = Pet("Rex", "dog")
    task = Task("Nail trim", importance=3, duration_minutes=20, pet=pet,
                frequency="weekly", due_date=date(2026, 7, 4))

    new_task = task.next_occurrence()

    assert new_task.due_date == date(2026, 7, 4) + timedelta(weeks=1)


def test_completing_once_task_does_not_recur():
    """A one-off task returns no next occurrence when completed."""
    owner = Owner("Alex")
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    task = Task("Vet visit", importance=5, duration_minutes=60, pet=pet,
                frequency="once")
    owner.add_task(task)

    scheduler = Scheduler(owner)
    new_task = scheduler.mark_task_complete(task)

    assert task.done is True
    assert new_task is None
    assert len(owner.get_all_tasks()) == 1


def test_sort_by_time_returns_tasks_in_chronological_order():
    """sort_by_time() must return scheduled tasks ordered earliest-first.

    We give the owner three availability slots and three tasks. The scheduler
    assigns each a start time, and sort_by_time() should hand them back in
    chronological order regardless of the order they were added or scheduled.
    """
    owner = Owner("Alex", available_hours=["08:00", "12:00", "18:00"])
    rex = Pet("Rex", "dog")
    owner.add_pet(rex)
    # Add tasks whose importance would NOT already place them in time order,
    # so we know the ordering comes from sort_by_time(), not the add order.
    owner.add_task(Task("Big morning", importance=5, duration_minutes=55, pet=rex))
    owner.add_task(Task("Big noon", importance=4, duration_minutes=55, pet=rex))
    owner.add_task(Task("Big evening", importance=3, duration_minutes=55, pet=rex))

    ordered = Scheduler(owner).sort_by_time()
    times = [task.time for task in ordered]

    # Each task lands in its own slot; the returned list is earliest-first.
    assert times == ["08:00", "12:00", "18:00"]
    # And the times are sorted (defensive check that it's truly chronological).
    assert times == sorted(times)


def test_detect_conflicts_flags_same_time_tasks():
    """Two tasks at the same start time produce one warning; program continues."""
    owner = Owner("Alex")
    rex = Pet("Rex", "dog")
    mochi = Pet("Mochi", "cat")
    owner.add_pet(rex)
    owner.add_pet(mochi)
    owner.add_task(Task("Medicine", importance=5, duration_minutes=5, pet=rex, time="09:00"))
    owner.add_task(Task("Brush", importance=2, duration_minutes=10, pet=mochi, time="09:00"))

    warnings = Scheduler(owner).detect_conflicts()

    assert len(warnings) == 1
    assert "09:00" in warnings[0]
    # Both clashing tasks should be named in the single warning message.
    assert "Medicine" in warnings[0]
    assert "Brush" in warnings[0]


def test_detect_conflicts_empty_when_times_differ():
    """Distinct start times (and unscheduled tasks) yield no warnings."""
    owner = Owner("Alex")
    rex = Pet("Rex", "dog")
    owner.add_pet(rex)
    owner.add_task(Task("Walk", importance=5, duration_minutes=30, pet=rex, time="08:00"))
    owner.add_task(Task("Feed", importance=4, duration_minutes=10, pet=rex, time="09:00"))
    owner.add_task(Task("Unscheduled", importance=1, duration_minutes=5, pet=rex))

    assert Scheduler(owner).detect_conflicts() == []
