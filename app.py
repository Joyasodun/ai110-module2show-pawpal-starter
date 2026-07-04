import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["Dog", "Cat", "Other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

# Create the Owner once and keep it in the session "vault" so tasks persist.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name, available_hours=["Morning", "Afternoon", "Evening"])

owner = st.session_state.owner

# Let the user choose which parts of the day they're available for care.
st.markdown("### Availability")
st.caption("Pick the parts of the day you're free. Tasks are scheduled into these windows.")
availability = st.multiselect(
    "Available parts of day",
    options=["Morning", "Afternoon", "Evening"],
    default=owner.get_availability() or ["Morning", "Afternoon", "Evening"],
    help="Morning: 5:00 AM–12:00 PM · Afternoon: 12:00 PM–7:00 PM · Evening: 7:00 PM–12:00 AM",
)
owner.available_hours = availability

# Make sure a Pet with this name exists on the owner; reuse it if it's already there.
pet = next((p for p in owner.pets if p.name == pet_name), None)
if pet is None:
    pet = Pet(pet_name, species)
    owner.add_pet(pet)

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    # Importance is a 1-5 scale (higher = more urgent), matching Task.importance.
    importance = st.number_input("Importance (1-5)", min_value=1, max_value=5, value=5)

if st.button("Add task"):
    task = Task(
        todo=task_title,
        importance=int(importance),
        duration_minutes=int(duration),
        pet=pet,
    )
    owner.add_task(task)  # calls your method; also attaches the task to the pet

scheduler = Scheduler(owner)  # the "brain" that reads the owner and its tasks

# --- Current tasks, filterable by pet ---
all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")

    pet_names = ["All pets"] + [p.name for p in owner.pets]
    chosen_pet = st.selectbox("Filter by pet", pet_names)

    if chosen_pet == "All pets":
        shown = all_tasks
    else:
        shown = scheduler.filter_tasks(pet_name=chosen_pet)

    st.table(
        [
            {
                "title": t.todo,
                "pet": t.pet.name,
                "duration_minutes": t.duration_minutes,
                "importance": t.importance,
                "done": "✅" if t.done else "⬜️",
            }
            for t in shown
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Today's Schedule")
st.caption("Builds a timed plan from your tasks, sorted by clock time, and flags conflicts.")

if st.button("Generate schedule"):
    if not scheduler.pending_tasks():
        st.info("No pending tasks to schedule. Add a task above first.")
    else:
        # Conflict warnings first — surface problems before the plan itself.
        conflicts = scheduler.detect_conflicts()
        for warning in conflicts:
            st.warning(warning)

        # The sorted, timed plan as a clean table.
        sorted_tasks = scheduler.sort_by_time()
        if sorted_tasks:
            st.success(f"Scheduled {len(sorted_tasks)} task(s) for {owner.name}.")
            st.table(
                [
                    {
                        "time": t.time,
                        "task": t.todo,
                        "pet": t.pet.name,
                        "duration_minutes": t.duration_minutes,
                        "importance": t.importance,
                    }
                    for t in sorted_tasks
                ]
            )
        else:
            st.warning("No tasks fit into the available hours.")

        # The human-readable explanation of why each task was placed.
        with st.expander("Why was each task scheduled?"):
            st.text(scheduler.explain_plan())
