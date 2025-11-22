from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
from statistics import mean
from main import (
    PlannerData, Course, Assignment, StudySession, Goal,
    load_data, save_data, grade_to_gpa, DATA_FILE, DATE_FMT
)
from uuid import uuid4

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = 'your-secret-key-change-in-production'


def get_planner() -> PlannerData:
    """Load planner data"""
    return load_data()


def save_planner(planner: PlannerData):
    """Save planner data"""
    save_data(planner)


@app.route('/')
def index():
    """Home page - Dashboard"""
    planner = get_planner()
    
    # Calculate dashboard stats
    total_courses = len(planner.courses)
    completed_assignments = sum(1 for a in planner.assignments if a.status == "completed")
    pending_assignments = sum(1 for a in planner.assignments if a.status != "completed")
    
    grades = [course.current_grade for course in planner.courses if course.current_grade is not None]
    gpa = round(mean(grade_to_gpa(g) for g in grades), 2) if grades else 0.0
    
    last_week = datetime.today() - timedelta(days=7)
    study_hours = sum(
        session.duration_hours
        for session in planner.study_sessions
        if datetime.strptime(session.date, DATE_FMT) >= last_week
    )
    
    goals_avg = mean(goal.progress for goal in planner.goals) if planner.goals else 0
    
    # Upcoming assignments
    upcoming = [
        a for a in planner.assignments
        if datetime.strptime(a.due_date, DATE_FMT) >= datetime.today()
    ]
    upcoming.sort(key=lambda a: a.due_date)
    
    # Get course names for assignments
    course_map = {c.id: c.name for c in planner.courses}
    for assignment in upcoming:
        assignment.course_name = course_map.get(assignment.course_id, "Unknown")
    
    return render_template('dashboard.html', 
                         planner=planner,
                         total_courses=total_courses,
                         completed_assignments=completed_assignments,
                         pending_assignments=pending_assignments,
                         gpa=gpa,
                         study_hours=study_hours,
                         goals_avg=goals_avg,
                         upcoming=upcoming[:5])


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """Edit student profile"""
    planner = get_planner()
    if request.method == 'POST':
        planner.student_name = request.form.get('student_name', '')
        planner.term = request.form.get('term', '')
        save_planner(planner)
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('profile.html', planner=planner)


@app.route('/courses')
def courses():
    """View all courses"""
    planner = get_planner()
    return render_template('courses.html', planner=planner)


@app.route('/courses/add', methods=['GET', 'POST'])
def add_course():
    """Add a new course"""
    planner = get_planner()
    if request.method == 'POST':
        try:
            course = Course(
                id=str(uuid4()),
                name=request.form.get('name', '').strip(),
                credits=float(request.form.get('credits', 0)),
                target_grade=float(request.form.get('target_grade', 0)),
                current_grade=float(request.form.get('current_grade')) if request.form.get('current_grade') else None
            )
            planner.courses.append(course)
            save_planner(planner)
            flash(f'Course "{course.name}" added successfully!', 'success')
            return redirect(url_for('courses'))
        except ValueError as e:
            flash('Invalid input. Please check your values.', 'error')
    return render_template('add_course.html')


@app.route('/courses/<course_id>/edit', methods=['GET', 'POST'])
def edit_course(course_id):
    """Edit a course"""
    planner = get_planner()
    course = next((c for c in planner.courses if c.id == course_id), None)
    if not course:
        flash('Course not found.', 'error')
        return redirect(url_for('courses'))
    
    if request.method == 'POST':
        try:
            course.name = request.form.get('name', '').strip()
            course.credits = float(request.form.get('credits', 0))
            course.target_grade = float(request.form.get('target_grade', 0))
            course.current_grade = float(request.form.get('current_grade')) if request.form.get('current_grade') else None
            save_planner(planner)
            flash('Course updated successfully!', 'success')
            return redirect(url_for('courses'))
        except ValueError:
            flash('Invalid input. Please check your values.', 'error')
    
    return render_template('edit_course.html', course=course)


@app.route('/courses/<course_id>/delete', methods=['POST'])
def delete_course(course_id):
    """Delete a course"""
    planner = get_planner()
    course = next((c for c in planner.courses if c.id == course_id), None)
    if course:
        # Remove related assignments and study sessions
        planner.assignments = [a for a in planner.assignments if a.course_id != course.id]
        planner.study_sessions = [s for s in planner.study_sessions if s.course_id != course.id]
        planner.courses.remove(course)
        save_planner(planner)
        flash(f'Course "{course.name}" and related records deleted.', 'success')
    else:
        flash('Course not found.', 'error')
    return redirect(url_for('courses'))


@app.route('/assignments')
def assignments():
    """View all assignments"""
    planner = get_planner()
    course_map = {c.id: c.name for c in planner.courses}
    for assignment in planner.assignments:
        assignment.course_name = course_map.get(assignment.course_id, "Unknown")
    # Sort by due date
    sorted_assignments = sorted(planner.assignments, key=lambda a: a.due_date)
    return render_template('assignments.html', assignments=sorted_assignments, planner=planner)


@app.route('/assignments/add', methods=['GET', 'POST'])
def add_assignment():
    """Add a new assignment"""
    planner = get_planner()
    if request.method == 'POST':
        try:
            assignment = Assignment(
                id=str(uuid4()),
                title=request.form.get('title', '').strip(),
                course_id=request.form.get('course_id', ''),
                due_date=request.form.get('due_date', ''),
                weight=float(request.form.get('weight', 0)),
                status=request.form.get('status', 'pending'),
                grade=float(request.form.get('grade')) if request.form.get('grade') else None
            )
            planner.assignments.append(assignment)
            save_planner(planner)
            flash('Assignment added successfully!', 'success')
            return redirect(url_for('assignments'))
        except ValueError:
            flash('Invalid input. Please check your values.', 'error')
    return render_template('add_assignment.html', courses=planner.courses)


@app.route('/assignments/<assignment_id>/edit', methods=['GET', 'POST'])
def edit_assignment(assignment_id):
    """Edit an assignment"""
    planner = get_planner()
    assignment = next((a for a in planner.assignments if a.id == assignment_id), None)
    if not assignment:
        flash('Assignment not found.', 'error')
        return redirect(url_for('assignments'))
    
    if request.method == 'POST':
        try:
            assignment.title = request.form.get('title', '').strip()
            assignment.course_id = request.form.get('course_id', '')
            assignment.due_date = request.form.get('due_date', '')
            assignment.weight = float(request.form.get('weight', 0))
            assignment.status = request.form.get('status', 'pending')
            assignment.grade = float(request.form.get('grade')) if request.form.get('grade') else None
            save_planner(planner)
            flash('Assignment updated successfully!', 'success')
            return redirect(url_for('assignments'))
        except ValueError:
            flash('Invalid input. Please check your values.', 'error')
    
    return render_template('edit_assignment.html', assignment=assignment, courses=planner.courses)


@app.route('/assignments/<assignment_id>/delete', methods=['POST'])
def delete_assignment(assignment_id):
    """Delete an assignment"""
    planner = get_planner()
    assignment = next((a for a in planner.assignments if a.id == assignment_id), None)
    if assignment:
        planner.assignments.remove(assignment)
        save_planner(planner)
        flash('Assignment deleted successfully!', 'success')
    else:
        flash('Assignment not found.', 'error')
    return redirect(url_for('assignments'))


@app.route('/study-sessions')
def study_sessions():
    """View all study sessions"""
    planner = get_planner()
    course_map = {c.id: c.name for c in planner.courses}
    for session in planner.study_sessions:
        session.course_name = course_map.get(session.course_id, "Unknown")
    # Sort by date (newest first)
    sorted_sessions = sorted(planner.study_sessions, key=lambda s: s.date, reverse=True)
    return render_template('study_sessions.html', sessions=sorted_sessions, planner=planner)


@app.route('/study-sessions/add', methods=['GET', 'POST'])
def add_study_session():
    """Add a new study session"""
    planner = get_planner()
    if request.method == 'POST':
        try:
            session = StudySession(
                id=str(uuid4()),
                course_id=request.form.get('course_id', ''),
                date=request.form.get('date', ''),
                duration_hours=float(request.form.get('duration_hours', 0)),
                notes=request.form.get('notes', '').strip()
            )
            planner.study_sessions.append(session)
            save_planner(planner)
            flash('Study session logged successfully!', 'success')
            return redirect(url_for('study_sessions'))
        except ValueError:
            flash('Invalid input. Please check your values.', 'error')
    return render_template('add_study_session.html', courses=planner.courses)


@app.route('/study-sessions/<session_id>/delete', methods=['POST'])
def delete_study_session(session_id):
    """Delete a study session"""
    planner = get_planner()
    session = next((s for s in planner.study_sessions if s.id == session_id), None)
    if session:
        planner.study_sessions.remove(session)
        save_planner(planner)
        flash('Study session deleted successfully!', 'success')
    else:
        flash('Study session not found.', 'error')
    return redirect(url_for('study_sessions'))


@app.route('/goals')
def goals():
    """View all goals"""
    planner = get_planner()
    return render_template('goals.html', planner=planner)


@app.route('/goals/add', methods=['GET', 'POST'])
def add_goal():
    """Add a new goal"""
    planner = get_planner()
    if request.method == 'POST':
        try:
            goal = Goal(
                id=str(uuid4()),
                description=request.form.get('description', '').strip(),
                progress=float(request.form.get('progress', 0)),
                target_date=request.form.get('target_date') or None
            )
            planner.goals.append(goal)
            save_planner(planner)
            flash('Goal added successfully!', 'success')
            return redirect(url_for('goals'))
        except ValueError:
            flash('Invalid input. Please check your values.', 'error')
    return render_template('add_goal.html')


@app.route('/goals/<goal_id>/edit', methods=['GET', 'POST'])
def edit_goal(goal_id):
    """Edit a goal"""
    planner = get_planner()
    goal = next((g for g in planner.goals if g.id == goal_id), None)
    if not goal:
        flash('Goal not found.', 'error')
        return redirect(url_for('goals'))
    
    if request.method == 'POST':
        try:
            goal.description = request.form.get('description', '').strip()
            goal.progress = float(request.form.get('progress', 0))
            goal.target_date = request.form.get('target_date') or None
            save_planner(planner)
            flash('Goal updated successfully!', 'success')
            return redirect(url_for('goals'))
        except ValueError:
            flash('Invalid input. Please check your values.', 'error')
    
    return render_template('edit_goal.html', goal=goal)


@app.route('/goals/<goal_id>/delete', methods=['POST'])
def delete_goal(goal_id):
    """Delete a goal"""
    planner = get_planner()
    goal = next((g for g in planner.goals if g.id == goal_id), None)
    if goal:
        planner.goals.remove(goal)
        save_planner(planner)
        flash('Goal deleted successfully!', 'success')
    else:
        flash('Goal not found.', 'error')
    return redirect(url_for('goals'))


@app.route('/test-static')
def test_static():
    """Test route to verify static files are being served"""
    return f"""
    <h1>Static Files Test</h1>
    <p>If you can see this page, Flask is working.</p>
    <p>CSS file should be at: <a href="{url_for('static', filename='style.css')}">style.css</a></p>
    <p>Try accessing: <a href="/">Dashboard</a></p>
    """


@app.route('/progress')
def progress():
    """View detailed progress report"""
    planner = get_planner()
    
    # Calculate progress for each course
    course_progress = []
    for course in planner.courses:
        course_assignments = [a for a in planner.assignments if a.course_id == course.id]
        completed = sum(1 for a in course_assignments if a.status == "completed")
        avg_grade = mean(a.grade for a in course_assignments if a.grade is not None) if course_assignments else None
        
        # Calculate study hours for this course
        course_study_hours = sum(
            s.duration_hours for s in planner.study_sessions if s.course_id == course.id
        )
        
        course_progress.append({
            'course': course,
            'assignments': course_assignments,
            'completed': completed,
            'total': len(course_assignments),
            'avg_grade': avg_grade,
            'study_hours': course_study_hours
        })
    
    total_hours = sum(s.duration_hours for s in planner.study_sessions)
    
    return render_template('progress.html', 
                         planner=planner,
                         course_progress=course_progress,
                         total_hours=total_hours)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

