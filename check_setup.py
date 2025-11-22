"""
Quick setup verification script
Run this to check if all files are in the correct locations
"""
import os
from pathlib import Path

print("Checking project setup...\n")

# Check if required directories exist
required_dirs = ['templates', 'static']
for dir_name in required_dirs:
    if Path(dir_name).exists():
        print(f"✓ {dir_name}/ directory exists")
    else:
        print(f"✗ {dir_name}/ directory MISSING")

# Check if required files exist
required_files = {
    'app.py': 'Flask application',
    'main.py': 'CLI application',
    'static/style.css': 'Stylesheet',
    'templates/base.html': 'Base template',
    'requirements.txt': 'Dependencies file'
}

print("\nChecking required files...")
for file_path, description in required_files.items():
    if Path(file_path).exists():
        size = Path(file_path).stat().st_size
        print(f"✓ {file_path} ({description}) - {size} bytes")
    else:
        print(f"✗ {file_path} ({description}) MISSING")

# Check template files
print("\nChecking template files...")
template_files = [
    'dashboard.html', 'profile.html', 'courses.html', 
    'assignments.html', 'study_sessions.html', 'goals.html', 
    'progress.html', 'add_course.html', 'edit_course.html',
    'add_assignment.html', 'edit_assignment.html',
    'add_study_session.html', 'add_goal.html', 'edit_goal.html'
]

templates_dir = Path('templates')
if templates_dir.exists():
    for template in template_files:
        template_path = templates_dir / template
        if template_path.exists():
            print(f"✓ templates/{template}")
        else:
            print(f"✗ templates/{template} MISSING")

# Check CSS file content
print("\nChecking CSS file...")
css_path = Path('static/style.css')
if css_path.exists():
    with open(css_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if len(content) > 100:
            print(f"✓ CSS file has content ({len(content)} characters)")
            if ':root' in content and '--primary-color' in content:
                print("✓ CSS variables are defined")
            else:
                print("⚠ CSS might be incomplete")
        else:
            print("⚠ CSS file seems too small")
else:
    print("✗ CSS file MISSING")

print("\n" + "="*50)
print("Setup check complete!")
print("\nTo run the web application:")
print("  1. Install dependencies: pip install -r requirements.txt")
print("  2. Run Flask: python app.py")
print("  3. Open browser: http://localhost:5000")
print("\nIf CSS is still not loading:")
print("  - Clear browser cache (Ctrl+Shift+R or Ctrl+F5)")
print("  - Check browser console for errors (F12)")
print("  - Verify Flask is running and check terminal for errors")

