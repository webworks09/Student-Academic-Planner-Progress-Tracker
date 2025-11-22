# Quick Start Guide - CSS Not Showing Fix

## ⚠️ IMPORTANT: You're opening the file directly!

**The Problem:** You're opening `base.html` directly in the browser (file:// path), which means:
- Flask server is NOT running
- CSS won't load (no server to serve static files)
- Templates won't render (Jinja2 syntax shows as text)

## ✅ Solution: Run Flask Server

### Step 1: Start the Flask Server

**Option A: Using the batch file (Easiest)**
1. Double-click `run_server.bat`
2. Wait for "Running on http://127.0.0.1:5000"

**Option B: Using Command Line**
1. Open PowerShell or Command Prompt
2. Navigate to project folder:
   ```powershell
   cd "C:\Users\jayga\OneDrive\Desktop\CSE Project"
   ```
3. Run Flask:
   ```powershell
   python app.py
   ```

### Step 2: Open in Browser

**DO NOT** open the HTML file directly!

Instead:
1. Open your browser
2. Go to: **http://localhost:5000**
3. Or: **http://127.0.0.1:5000**

### Step 3: Verify CSS is Loading

1. Press `F12` to open Developer Tools
2. Go to "Network" tab
3. Refresh the page (F5)
4. Look for `style.css` - should show status `200`

## What You Should See

✅ **Correct URL:** `http://localhost:5000` or `http://127.0.0.1:5000`  
❌ **Wrong URL:** `file:///C:/Users/jayga/.../base.html`

✅ **Correct:** Beautiful styled page with colors, navigation, cards  
❌ **Wrong:** Plain white page with black text and visible `{% %}` code

## Still Not Working?

1. **Check if Flask is running:**
   - Terminal should show: "Running on http://127.0.0.1:5000"
   - If you see errors, install Flask: `pip install -r requirements.txt`

2. **Clear browser cache:**
   - Press `Ctrl + Shift + R` (hard refresh)

3. **Check the URL:**
   - Must start with `http://localhost:5000`
   - NOT `file:///` or `C:/`

4. **Test CSS directly:**
   - Go to: `http://localhost:5000/static/style.css`
   - Should see CSS code, not an error

## Need Help?

If you see errors when running `python app.py`, make sure:
- Python is installed
- Flask is installed: `pip install Flask`
- You're in the correct directory

