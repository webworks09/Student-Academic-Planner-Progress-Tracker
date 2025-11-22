import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional
from uuid import uuid4

DATA_FILE = Path("planner_data.json")
DATE_FMT = "%Y-%m-%d"


@dataclass
class Course:
    id: str
    name: str
    credits: float
    target_grade: float
    current_grade: Optional[float] = None


@dataclass
class Assignment:
    id: str
    title: str
    course_id: str
    due_date: str
    weight: float
    status: str = "pending"
    grade: Optional[float] = None


@dataclass
class StudySession:
    id: str
    course_id: str
    date: str
    duration_hours: float
    notes: str = ""


@dataclass
class Goal:
    id: str
    description: str
    progress: float
    target_date: Optional[str] = None


@dataclass
class PlannerData:
    student_name: str = ""
    term: str = ""
    courses: List[Course] = field(default_factory=list)
    assignments: List[Assignment] = field(default_factory=list)
    study_sessions: List[StudySession] = field(default_factory=list)
    goals: List[Goal] = field(default_factory=list)

    @staticmethod
    def from_json(payload: Dict) -> "PlannerData":
        def build_list(data, cls):
            return [cls(**item) for item in data]

        return PlannerData(
            student_name=payload.get("student_name", ""),
            term=payload.get("term", ""),
            courses=build_list(payload.get("courses", []), Course),
            assignments=build_list(payload.get("assignments", []), Assignment),
            study_sessions=build_list(payload.get("study_sessions", []), StudySession),
            goals=build_list(payload.get("goals", []), Goal),
        )

    def to_json(self) -> Dict:
        def serialize(items):
            return [asdict(item) for item in items]

        return {
            "student_name": self.student_name,
            "term": self.term,
            "courses": serialize(self.courses),
            "assignments": serialize(self.assignments),
            "study_sessions": serialize(self.study_sessions),
            "goals": serialize(self.goals),
        }


def load_data() -> PlannerData:
    if DATA_FILE.exists():
        with DATA_FILE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
            return PlannerData.from_json(data)
    return PlannerData()


def save_data(planner: PlannerData) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as fh:
        json.dump(planner.to_json(), fh, indent=2)


def prompt(text: str, allow_blank: bool = False) -> str:
    while True:
        value = input(text).strip()
        if value or allow_blank:
            return value
        print("Input cannot be blank.")


def prompt_float(text: str, minimum: Optional[float] = None, maximum: Optional[float] = None) -> float:
    while True:
        try:
            value = float(prompt(text))
            if minimum is not None and value < minimum:
                raise ValueError
            if maximum is not None and value > maximum:
                raise ValueError
            return value
        except ValueError:
            print("Enter a valid number within the accepted range.")


def prompt_date(text: str) -> str:
    while True:
        try:
            value = prompt(text)
            datetime.strptime(value, DATE_FMT)
            return value
        except ValueError:
            print(f"Use date format {DATE_FMT}.")


def choose_course(planner: PlannerData) -> Optional[Course]:
    if not planner.courses:
        print("No courses available. Add a course first.")
        return None

    for idx, course in enumerate(planner.courses, start=1):
        grade = course.current_grade if course.current_grade is not None else "N/A"
        print(f"{idx}. {course.name} (Credits: {course.credits}, Grade: {grade})")
    choice = prompt_float("Select course #: ", 1, len(planner.courses))
    return planner.courses[int(choice) - 1]


def add_course(planner: PlannerData) -> None:
    print("\n--- Add Course ---")
    name = prompt("Course name: ")
    credits = prompt_float("Credits: ", 0.5)
    target = prompt_float("Target grade (0-100): ", 0, 100)
    course = Course(id=str(uuid4()), name=name, credits=credits, target_grade=target)
    planner.courses.append(course)
    print(f"Added course {name}.")


def update_course_grade(planner: PlannerData) -> None:
    print("\n--- Update Course Grade ---")
    course = choose_course(planner)
    if not course:
        return
    course.current_grade = prompt_float("Current grade (0-100): ", 0, 100)
    print(f"Updated {course.name} grade to {course.current_grade}.")


def remove_course(planner: PlannerData) -> None:
    print("\n--- Remove Course ---")
    course = choose_course(planner)
    if not course:
        return
    planner.assignments = [a for a in planner.assignments if a.course_id != course.id]
    planner.study_sessions = [s for s in planner.study_sessions if s.course_id != course.id]
    planner.courses.remove(course)
    print(f"Removed {course.name} and related records.")


def add_assignment(planner: PlannerData) -> None:
    print("\n--- Add Assignment ---")
    course = choose_course(planner)
    if not course:
        return
    title = prompt("Assignment title: ")
    due_date = prompt_date("Due date (YYYY-MM-DD): ")
    weight = prompt_float("Weight (percentage of course grade): ", 0, 100)
    assignment = Assignment(
        id=str(uuid4()),
        title=title,
        course_id=course.id,
        due_date=due_date,
        weight=weight,
    )
    planner.assignments.append(assignment)
    print(f"Added assignment {title} for {course.name}.")


def update_assignment_status(planner: PlannerData) -> None:
    print("\n--- Update Assignment ---")
    if not planner.assignments:
        print("No assignments to update.")
        return
    idx_map = {}
    for idx, assignment in enumerate(planner.assignments, start=1):
        course_name = next((c.name for c in planner.courses if c.id == assignment.course_id), "Unknown")
        print(
            f"{idx}. {assignment.title} ({course_name}) - Due {assignment.due_date} - Status: {assignment.status}"
        )
        idx_map[idx] = assignment
    choice = prompt_float("Select assignment #: ", 1, len(planner.assignments))
    selected = idx_map[int(choice)]
    status = prompt("Status (pending/in-progress/completed): ")
    grade_input = prompt("Grade (blank to skip): ", allow_blank=True)
    selected.status = status
    if grade_input:
        try:
            selected.grade = float(grade_input)
        except ValueError:
            print("Invalid grade. Keeping previous value.")
    print("Assignment updated.")


def add_study_session(planner: PlannerData) -> None:
    print("\n--- Log Study Session ---")
    course = choose_course(planner)
    if not course:
        return
    date = prompt_date("Study date (YYYY-MM-DD): ")
    duration = prompt_float("Duration in hours: ", 0.25)
    notes = prompt("Notes (optional): ", allow_blank=True)
    planner.study_sessions.append(
        StudySession(
            id=str(uuid4()),
            course_id=course.id,
            date=date,
            duration_hours=duration,
            notes=notes,
        )
    )
    print("Study session logged.")


def add_goal(planner: PlannerData) -> None:
    print("\n--- Add Goal ---")
    description = prompt("Goal description: ")
    target_date = prompt("Target date (YYYY-MM-DD, blank to skip): ", allow_blank=True)
    progress = prompt_float("Current progress (0-100): ", 0, 100)
    goal = Goal(id=str(uuid4()), description=description, progress=progress, target_date=target_date or None)
    planner.goals.append(goal)
    print("Goal added.")


def update_goal(planner: PlannerData) -> None:
    if not planner.goals:
        print("No goals to update.")
        return
    print("\n--- Update Goal ---")
    for idx, goal in enumerate(planner.goals, start=1):
        print(f"{idx}. {goal.description} - {goal.progress}% complete")
    choice = prompt_float("Select goal #: ", 1, len(planner.goals))
    goal = planner.goals[int(choice) - 1]
    goal.progress = prompt_float("New progress (0-100): ", 0, 100)
    print("Goal progress updated.")


def delete_goal(planner: PlannerData) -> None:
    if not planner.goals:
        print("No goals to delete.")
        return
    print("\n--- Delete Goal ---")
    for idx, goal in enumerate(planner.goals, start=1):
        print(f"{idx}. {goal.description} - {goal.progress}% complete")
    choice = prompt_float("Select goal #: ", 1, len(planner.goals))
    goal = planner.goals.pop(int(choice) - 1)
    print(f"Deleted goal '{goal.description}'.")


def grade_to_gpa(grade: float) -> float:
    if grade >= 93:
        return 4.0
    if grade >= 90:
        return 3.7
    if grade >= 87:
        return 3.3
    if grade >= 83:
        return 3.0
    if grade >= 80:
        return 2.7
    if grade >= 77:
        return 2.3
    if grade >= 73:
        return 2.0
    if grade >= 70:
        return 1.7
    if grade >= 67:
        return 1.3
    if grade >= 65:
        return 1.0
    return 0.0


def show_dashboard(planner: PlannerData) -> None:
    total_courses = len(planner.courses)
    completed_assignments = sum(1 for a in planner.assignments if a.status == "completed")
    pending_assignments = sum(1 for a in planner.assignments if a.status != "completed")
    grades = [course.current_grade for course in planner.courses if course.current_grade is not None]
    gpa = (
        round(mean(grade_to_gpa(g) for g in grades), 2)
        if grades
        else 0.0
    )

    last_week = datetime.today() - timedelta(days=7)
    study_hours = sum(
        session.duration_hours
        for session in planner.study_sessions
        if datetime.strptime(session.date, DATE_FMT) >= last_week
    )

    print("\n=== Academic Dashboard ===")
    print(f"Student: {planner.student_name or 'N/A'} (Term: {planner.term or 'N/A'})")
    print(f"Courses: {total_courses}")
    print(f"Assignments - Pending: {pending_assignments}, Completed: {completed_assignments}")
    print(f"GPA (est.): {gpa:.2f}")
    print(f"Study hours (last 7 days): {study_hours:.1f}")
    goals_avg = mean(goal.progress for goal in planner.goals) if planner.goals else 0
    print(f"Goal progress avg: {goals_avg:.1f}%")
    upcoming = [
        a for a in planner.assignments
        if datetime.strptime(a.due_date, DATE_FMT) >= datetime.today()
    ]
    upcoming.sort(key=lambda a: a.due_date)
    print("\nNext 3 deadlines:")
    for assignment in upcoming[:3]:
        course_name = next((c.name for c in planner.courses if c.id == assignment.course_id), "Unknown")
        print(f"- {assignment.title} ({course_name}) due {assignment.due_date}")
    if not upcoming:
        print("No upcoming deadlines.")


def progress_report(planner: PlannerData) -> None:
    print("\n=== Progress Report ===")
    for course in planner.courses:
        course_assignments = [a for a in planner.assignments if a.course_id == course.id]
        completed = sum(1 for a in course_assignments if a.status == "completed")
        avg_grade = mean(a.grade for a in course_assignments if a.grade is not None) if course_assignments else None
        print(f"\n{course.name}")
        print(f" - Assignments completed: {completed}/{len(course_assignments)}")
        if avg_grade is not None:
            print(f" - Avg assignment grade: {avg_grade:.1f}")
        if course.current_grade is not None:
            print(f" - Current grade: {course.current_grade:.1f} (Target: {course.target_grade})")

    total_hours = sum(session.duration_hours for session in planner.study_sessions)
    print(f"\nTotal study hours logged: {total_hours:.1f}")

    if planner.goals:
        print("\nGoals:")
        for goal in planner.goals:
            target = f" by {goal.target_date}" if goal.target_date else ""
            print(f" - {goal.description}: {goal.progress}% complete{target}")
    else:
        print("\nNo goals set.")


def manage_courses(planner: PlannerData) -> None:
    options = {
        "1": ("Add course", add_course),
        "2": ("Update course grade", update_course_grade),
        "3": ("Remove course", remove_course),
        "0": ("Back", None),
    }
    while True:
        print("\n--- Course Menu ---")
        for key, (label, _) in options.items():
            print(f"{key}. {label}")
        choice = prompt("Select option: ")
        if choice == "0":
            break
        if choice in options:
            options[choice][1](planner)
        else:
            print("Invalid selection.")


def manage_assignments(planner: PlannerData) -> None:
    options = {
        "1": ("Add assignment", add_assignment),
        "2": ("Update assignment", update_assignment_status),
        "0": ("Back", None),
    }
    while True:
        print("\n--- Assignment Menu ---")
        for key, (label, _) in options.items():
            print(f"{key}. {label}")
        choice = prompt("Select option: ")
        if choice == "0":
            break
        if choice in options:
            options[choice][1](planner)
        else:
            print("Invalid selection.")


def manage_goals(planner: PlannerData) -> None:
    options = {
        "1": ("Add goal", add_goal),
        "2": ("Update goal", update_goal),
        "3": ("Delete goal", delete_goal),
        "0": ("Back", None),
    }
    while True:
        print("\n--- Goals Menu ---")
        for key, (label, _) in options.items():
            print(f"{key}. {label}")
        choice = prompt("Select option: ")
        if choice == "0":
            break
        if choice in options:
            options[choice][1](planner)
        else:
            print("Invalid selection.")


def edit_student_profile(planner: PlannerData) -> None:
    print("\n--- Student Profile ---")
    planner.student_name = prompt("Student name: ")
    planner.term = prompt("Term/Semester: ")
    print("Profile updated.")


def main_menu(planner: PlannerData) -> None:
    actions = {
        "1": ("View dashboard", show_dashboard),
        "2": ("Edit student profile", edit_student_profile),
        "3": ("Manage courses", manage_courses),
        "4": ("Manage assignments", manage_assignments),
        "5": ("Log study session", add_study_session),
        "6": ("Manage goals", manage_goals),
        "7": ("View progress report", progress_report),
        "0": ("Save & exit", None),
    }

    while True:
        print("\n=== Student Academic Planner ===")
        for key, (label, _) in actions.items():
            print(f"{key}. {label}")
        choice = prompt("Choose an option: ")
        if choice == "0":
            save_data(planner)
            print("Progress saved. Goodbye!")
            break
        action = actions.get(choice)
        if action:
            action[1](planner)
        else:
            print("Invalid choice.")

        save_data(planner)


if __name__ == "__main__":
    planner_data = load_data()
    main_menu(planner_data)

