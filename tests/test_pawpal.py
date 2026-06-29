"""Basic tests for the PawPal+ logic layer."""

from pawpal_system import Pet, Task


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
