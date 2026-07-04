"""PawPal+ logic layer.

Backend classes for the pet care planning assistant. These classes mirror
diagrams/uml.mmd.
"""

from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import List, Optional, Tuple


@dataclass
class Pet:
    """Stores pet details and a list of its care tasks."""

    name: str
    species: str
    preferences: List[str] = field(default_factory=list)
    tasks: List["Task"] = field(default_factory=list)

    def get_preferences(self) -> List[str]:
        """Return this pet's care preferences."""
        return self.preferences

    def add_task(self, task: "Task") -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> List["Task"]:
        """Return all tasks for this pet."""
        return self.tasks


@dataclass
class Task:
    """Represents a single care activity for a pet."""

    todo: str
    importance: int  # 1-5, higher = more urgent
    duration_minutes: int
    pet: "Pet"
    care_type: str = ""  # "feed" | "walk" | "shower" | "" maps to a PetCare flag
    frequency: str = "daily"  # e.g. "daily", "weekly", "once"
    done: bool = False
    time: str = ""  # scheduled start time in "HH:MM"; set by the Scheduler
    due_date: Optional[date] = None  # the day this task is due

    # How far ahead the next occurrence of a recurring task is due.
    _RECURRENCE = {
        "daily": timedelta(days=1),
        "weekly": timedelta(weeks=1),
    }

    def mark_done(self) -> None:
        """Mark this task as completed."""
        self.done = True

    def is_complete(self) -> bool:
        """Return the task's completion status."""
        return self.done

    def next_occurrence(self) -> Optional["Task"]:
        """Build the next occurrence of this task, or None if it doesn't recur.

        For a "daily" task the next due date is this task's due date (or today
        if it has none) plus one day; for "weekly" it's plus one week, computed
        with ``timedelta`` so month and year boundaries are handled correctly.
        A "once" task returns None because it does not repeat.
        """
        step = self._RECURRENCE.get(self.frequency)
        if step is None:
            return None
        base = self.due_date or date.today()
        return replace(self, done=False, time="", due_date=base + step)


@dataclass
class PetCare:
    """Tracks the concrete care state (food, feeding, shower, walk) for a pet."""

    food: str
    ounces_of_food: int
    shower: bool = False
    walk: bool = False
    fed: bool = False

    def feed(self, ounces: int) -> None:
        """Record a feeding: mark fed and store the amount."""
        self.ounces_of_food = ounces
        self.fed = True

    def all_done(self) -> bool:
        """Return True if every care item (fed, shower, walk) is complete."""
        return self.fed and self.shower and self.walk


class Owner:
    """Manages multiple pets and provides access to all of their tasks."""

    def __init__(self, name: str, available_hours: Optional[List[str]] = None):
        self.name = name
        self.pets: List[Pet] = []
        self.tasks: List[Task] = []
        self.available_hours: List[str] = available_hours or []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        if pet not in self.pets:
            self.pets.append(pet)

    def add_task(self, task: Task) -> None:
        """Add a care task to this owner's plan and to its pet."""
        self.tasks.append(task)
        if task.pet is not None and task not in task.pet.tasks:
            task.pet.add_task(task)

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all of this owner's pets."""
        all_tasks: List[Task] = list(self.tasks)
        for pet in self.pets:
            for task in pet.get_tasks():
                if task not in all_tasks:
                    all_tasks.append(task)
        return all_tasks

    def get_availability(self) -> List[str]:
        """Return the hours the owner is available for care tasks."""
        return self.available_hours


class Scheduler:
    """The "brain": retrieves, organizes, and manages tasks across pets."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self.tasks: List[Task] = owner.get_all_tasks()

    def pending_tasks(self) -> List[Task]:
        """Retrieve all tasks that still need to be completed."""
        return [task for task in self.owner.get_all_tasks() if not task.done]

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Mark a task complete and auto-create its next occurrence.

        Marks ``task`` done. If it is a recurring ("daily"/"weekly") task, a
        fresh, not-done copy is created with its due date advanced by one
        period and registered on the owner (and its pet). Returns the new task,
        or None for a one-off ("once") task that doesn't repeat.
        """
        task.mark_done()
        next_task = task.next_occurrence()
        if next_task is not None:
            self.owner.add_task(next_task)
        return next_task

    def build_schedule(self) -> List[Task]:
        """Choose and order tasks based on importance, duration, and availability.

        Pending tasks are sorted by importance (most urgent first), then by
        shorter duration so quick wins come earlier. Only the tasks that
        actually fit into a real availability slot are scheduled.

        This delegates to :meth:`build_timed_schedule` so the ordered list and
        the timed view can never disagree about what fits.
        """
        return [task for _start, task in self.build_timed_schedule()]

    @staticmethod
    def _to_minutes(clock: str) -> int:
        """Convert an "HH:MM" string into minutes past midnight."""
        hours, minutes = clock.split(":")
        return int(hours) * 60 + int(minutes)

    @staticmethod
    def _to_clock(total_minutes: int) -> str:
        """Convert minutes past midnight back into an "HH:MM" string."""
        hours, minutes = divmod(total_minutes, 60)
        return f"{hours:02d}:{minutes:02d}"

    # Time-of-day words -> the [start, end) minute window they prefer.
    _TIME_WINDOWS = {
        "morning": (0, 12 * 60),
        "breakfast": (6 * 60, 10 * 60),
        "noon": (11 * 60, 14 * 60),
        "lunch": (11 * 60, 14 * 60),
        "midday": (11 * 60, 14 * 60),
        "afternoon": (12 * 60, 17 * 60),
        "evening": (17 * 60, 21 * 60),
        "dinner": (17 * 60, 20 * 60),
        "night": (20 * 60, 24 * 60),
    }

    @classmethod
    def _window_for_text(cls, text: str) -> Optional[Tuple[int, int]]:
        """Return the time window named by a time-of-day word in ``text``."""
        lowered = text.lower()
        for word, window in cls._TIME_WINDOWS.items():
            if word in lowered:
                return window
        return None

    @classmethod
    def _preferred_window(cls, task: "Task") -> Optional[Tuple[int, int]]:
        """Return the (start, end) minute window this task prefers, if any.

        A time-of-day word in the task's own text (e.g. "Morning walk") always
        applies. A pet preference (e.g. "evening walks") only applies when it
        also mentions the task's activity — its ``care_type`` or a word from its
        title — so "evening walks" biases walk tasks but not, say, feeding.
        Returns None when nothing matches.
        """
        # A time word in the task's own name applies directly.
        own = cls._window_for_text(task.todo)
        if own is not None:
            return own

        # Otherwise, borrow a preference's window only if that preference is
        # about this task's activity.
        activity_words = {task.care_type.lower()} | set(task.todo.lower().split())
        activity_words.discard("")
        for pref in task.pet.get_preferences():
            window = cls._window_for_text(pref)
            if window is not None and any(word in pref.lower() for word in activity_words):
                return window
        return None

    def build_timed_schedule(self) -> List[Tuple[str, Task]]:
        """Assign each scheduled task a real start time.

        Pending tasks are considered most-urgent first. Each slot (e.g. "08:00")
        offers 60 minutes of care time. Every task is placed in the *earliest
        slot that still has room for it* (first fit), and the running clock in
        that slot advances by its duration. A task that fits in no single slot
        is skipped, but — unlike a single running pointer — it does not block
        the tasks after it from being placed.

        Returns a list of ("HH:MM", Task) pairs in chronological order.
        """
        ordered = sorted(
            self.pending_tasks(),
            key=lambda task: (-task.importance, task.duration_minutes),
        )
        slots = [self._to_minutes(hour) for hour in self.owner.get_availability()]
        if not slots or not ordered:
            return []

        # Each slot offers 60 minutes of care time.
        slot_ends = [start + 60 for start in slots]
        # Track the running clock (next free minute) within each slot.
        clocks = list(slots)

        placed: List[Tuple[int, Task]] = []
        for task in ordered:
            # Bias placement toward the task's preferred time of day: try slots
            # inside its window first, then fall back to any slot with room.
            window = self._preferred_window(task)
            if window is not None:
                low, high = window
                preferred = [i for i, s in enumerate(slots) if low <= s < high]
                order = preferred + [i for i in range(len(slots)) if i not in preferred]
            else:
                order = range(len(slots))

            for index in order:
                if clocks[index] + task.duration_minutes <= slot_ends[index]:
                    placed.append((clocks[index], task))
                    clocks[index] += task.duration_minutes
                    break

        # Sort by start time so the plan reads chronologically.
        placed.sort(key=lambda pair: pair[0])
        timed: List[Tuple[str, Task]] = []
        for start, task in placed:
            clock = self._to_clock(start)
            task.time = clock  # record the assigned start time on the task
            timed.append((clock, task))
        return timed

    def detect_conflicts(self) -> List[str]:
        """Return warning messages for tasks that share the same start time.

        Lightweight strategy: group every task that has a start time by that
        "HH:MM" string; any time claimed by more than one task is a conflict.
        This just *reports* problems as human-readable strings — it never raises
        or drops a task, so the program keeps running. Returns an empty list
        when there are no conflicts.
        """
        by_time: defaultdict = defaultdict(list)
        for task in self.owner.get_all_tasks():
            if task.time:  # only tasks with an assigned start time can clash
                by_time[task.time].append(task)

        warnings: List[str] = []
        for start in sorted(by_time):
            tasks = by_time[start]
            if len(tasks) > 1:
                names = ", ".join(f"{t.todo} ({t.pet.name})" for t in tasks)
                warnings.append(
                    f"⚠️ Conflict at {start}: {len(tasks)} tasks scheduled "
                    f"at the same time — {names}."
                )
        return warnings

    def explain_plan(self) -> str:
        """Explain why each task was chosen and when it happens."""
        timed = self.build_timed_schedule()
        if not timed:
            return f"No tasks scheduled for {self.owner.name}."

        lines = [f"Care plan for {self.owner.name}:"]
        for position, (start, task) in enumerate(timed, start=1):
            if self._preferred_window(task) is not None:
                reason = "to match its preferred time of day"
            else:
                reason = "because it is among the most urgent tasks that fit"
            lines.append(
                f"{position}. {start} — {task.todo} for {task.pet.name} "
                f"(importance {task.importance}, {task.duration_minutes} min) "
                f"— scheduled at {start} {reason}."
            )
        return "\n".join(lines)

    def sort_by_time(self) -> List[Task]:
        """Return the scheduled Task objects ordered by their ``time`` attribute.

        Building the schedule stamps each scheduled task with a start time in
        "HH:MM" form on ``task.time``. We then sort those Task objects with
        ``sorted()`` and a ``key`` lambda that reads ``task.time``. Because
        zero-padded "HH:MM" strings sort the same way alphabetically as they do
        chronologically ("08:30" < "12:00" < "18:05"), sorting the raw string is
        enough — no time parsing needed.
        """
        scheduled = [task for _start, task in self.build_timed_schedule()]
        return sorted(scheduled, key=lambda task: task.time)

    def filter_tasks(
        self,
        done: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> List[Task]:
        """Return tasks filtered by completion status and/or pet name.

        Pass ``done=True`` for completed tasks or ``done=False`` for pending
        ones; leave it as ``None`` to ignore completion. Pass ``pet_name`` to
        keep only tasks for that pet (case-insensitive); leave it ``None`` to
        include every pet. With no arguments, returns all tasks.
        """
        tasks = self.owner.get_all_tasks()
        if done is not None:
            tasks = [task for task in tasks if task.done == done]
        if pet_name is not None:
            tasks = [task for task in tasks if task.pet.name.lower() == pet_name.lower()]
        return tasks
