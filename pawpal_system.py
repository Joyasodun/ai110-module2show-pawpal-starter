"""PawPal+ logic layer.

Backend classes for the pet care planning assistant. These classes mirror
diagrams/uml.mmd.
"""

from dataclasses import dataclass, field
from typing import List, Optional


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

    def mark_done(self) -> None:
        """Mark this task as completed."""
        self.done = True

    def is_complete(self) -> bool:
        """Return the task's completion status."""
        return self.done


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

    def build_schedule(self) -> List[Task]:
        """Choose and order tasks based on importance, duration, and availability.

        Pending tasks are sorted by importance (most urgent first), then by
        shorter duration so quick wins come earlier. Only as many tasks as fit
        in the owner's available hours are scheduled.
        """
        ordered = sorted(
            self.pending_tasks(),
            key=lambda task: (-task.importance, task.duration_minutes),
        )

        # Each available hour slot offers 60 minutes of care time.
        available_minutes = len(self.owner.get_availability()) * 60
        if available_minutes <= 0:
            return ordered

        scheduled: List[Task] = []
        remaining = available_minutes
        for task in ordered:
            if task.duration_minutes <= remaining:
                scheduled.append(task)
                remaining -= task.duration_minutes
        return scheduled

    def explain_plan(self) -> str:
        """Explain why each task was chosen and when it happens."""
        schedule = self.build_schedule()
        if not schedule:
            return f"No tasks scheduled for {self.owner.name}."

        lines = [f"Care plan for {self.owner.name}:"]
        for position, task in enumerate(schedule, start=1):
            lines.append(
                f"{position}. {task.todo} for {task.pet.name} "
                f"(importance {task.importance}, {task.duration_minutes} min) "
                f"— scheduled because it is among the most urgent tasks that "
                f"fit the available time."
            )
        return "\n".join(lines)
