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
    st.session_state.owner = Owner(owner_name, available_hours=["08:00", "12:00", "18:00"])

owner = st.session_state.owner

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
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

# Translate the UI's word-based priority into the 1-5 importance your Task class expects.
importance_map = {"low": 1, "medium": 3, "high": 5}

if st.button("Add task"):
    task = Task(
        todo=task_title,
        importance=importance_map[priority],
        duration_minutes=int(duration),
        pet=pet,
    )
    owner.add_task(task)  # calls your method; also attaches the task to the pet

if owner.get_all_tasks():
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": t.todo,
                "pet": t.pet.name,
                "duration_minutes": t.duration_minutes,
                "importance": t.importance,
            }
            for t in owner.get_all_tasks()
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)  # hand your brain the owner and its tasks
    plan = scheduler.explain_plan()  # your method returns the human-readable plan
    st.text(plan)
