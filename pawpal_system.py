"""PawPal+ logic layer.

Backend classes for the pet care planning assistant. These class skeletons
mirror diagrams/uml.mmd. Method bodies are left as stubs to be implemented.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Pet:
    name: str
    species: str
    preferences: List[str] = field(default_factory=list)

    def get_preferences(self) -> List[str]:
        """Return this pet's care preferences."""
        raise NotImplementedError


@dataclass
class Task:
    todo: str
    importance: int
    status: str = "todo"

    def mark_done(self) -> None:
        """Mark this task as completed."""
        raise NotImplementedError


@dataclass
class PetCare:
    food: str
    ounces_of_food: int
    shower: bool = False
    walk: bool = False
    fed: bool = False

    def feed(self, ounces: int) -> None:
        """Record a feeding: mark fed and store the amount."""
        raise NotImplementedError

    def all_done(self) -> bool:
        """Return True if every care item (fed, shower, walk) is complete."""
        raise NotImplementedError


class Owner:
    def __init__(self, name: str, available_hours: Optional[List[str]] = None):
        self.name = name
        self.pets: List[Pet] = []
        self.available_hours: List[str] = available_hours or []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        raise NotImplementedError

    def get_availability(self) -> List[str]:
        """Return the hours the owner is available for care tasks."""
        raise NotImplementedError
