# Student Academic Planner & Progress Tracker

A comprehensive web application for students to manage their courses, assignments, study sessions, and goals. Available as both a command-line interface and a modern web application.

## Features

- **Course Management**: Add, edit, and track courses with credits, target grades, and current grades
- **Assignment Tracking**: Manage assignments with due dates, weights, status, and grades
- **Study Session Logging**: Record study sessions with duration and notes
- **Goal Management**: Set and track progress toward academic and personal goals
- **Dashboard**: View overview statistics including GPA, study hours, and upcoming deadlines
- **Progress Reports**: Detailed progress tracking per course with completion statistics

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Web Application (Recommended)

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

3. **Features available in the web interface:**
   - Dashboard with statistics and quick actions
   - Forms for adding/editing courses, assignments, study sessions, and goals
   - Progress reports and detailed views
   - Responsive design that works on desktop and mobile

### Command-Line Interface

1. **Run the CLI version:**
   ```bash
   python main.py
   ```

2. **Follow the menu prompts to:**
   - Edit your student profile
   - Manage courses
   - Add and update assignments
   - Log study sessions
   - Set and track goals
   - View dashboard and progress reports

## Data Storage

All data is stored in `planner_data.json` in the project directory. Both the web application and CLI share the same data file, so you can use either interface interchangeably.

## Project Structure

```
.
├── app.py                 # Flask web application
├── main.py                # CLI application
├── requirements.txt       # Python dependencies
├── planner_data.json      # Data storage (auto-created)
├── templates/            # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── courses.html
│   ├── assignments.html
│   ├── study_sessions.html
│   ├── goals.html
│   ├── progress.html
│   └── ... (form templates)
└── static/
    └── style.css         # Stylesheet
```

## Web Application Routes

- `/` - Dashboard (home page)
- `/profile` - Edit student profile
- `/courses` - View all courses
- `/courses/add` - Add new course
- `/courses/<id>/edit` - Edit course
- `/assignments` - View all assignments
- `/assignments/add` - Add new assignment
- `/assignments/<id>/edit` - Edit assignment
- `/study-sessions` - View all study sessions
- `/study-sessions/add` - Log new study session
- `/goals` - View all goals
- `/goals/add` - Add new goal
- `/goals/<id>/edit` - Edit goal
- `/progress` - Detailed progress report

## Technologies Used

- **Python 3** - Backend logic
- **Flask** - Web framework
- **HTML/CSS** - Frontend interface
- **JSON** - Data storage

## Notes

- The web application runs in debug mode by default. For production, set `debug=False` in `app.py`
- Change the `secret_key` in `app.py` for production use
- All dates should be entered in `YYYY-MM-DD` format
- GPA calculation uses standard letter grade conversion (A=4.0, A-=3.7, etc.)

## License

This project is open source and available for educational purposes.

