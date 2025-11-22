# CSS Not Loading - Troubleshooting Guide

If the CSS styles are not showing in your web application, try these steps:

## Quick Fixes

### 1. Clear Browser Cache
- **Chrome/Edge**: Press `Ctrl + Shift + R` or `Ctrl + F5` to hard refresh
- **Firefox**: Press `Ctrl + Shift + R` or `Ctrl + F5`
- Or clear cache manually: Settings → Privacy → Clear browsing data

### 2. Check Browser Console
- Press `F12` to open Developer Tools
- Go to the "Console" tab
- Look for any red error messages
- Go to the "Network" tab and refresh the page
- Check if `style.css` is loading (should show status 200)

### 3. Verify Flask is Running
- Make sure Flask server is running: `python app.py`
- Check terminal for any error messages
- Server should show: `Running on http://127.0.0.1:5000`

### 4. Test Static File Access
- Open: `http://localhost:5000/static/style.css`
- You should see the CSS code
- If you see "404 Not Found", the static folder path is wrong

### 5. Verify File Structure
Make sure your project has this structure:
```
CSE Project/
├── app.py
├── static/
│   └── style.css
├── templates/
│   └── base.html
│   └── (other templates)
└── planner_data.json
```

## Common Issues

### Issue: CSS file returns 404
**Solution**: 
- Verify `static/style.css` exists in the project root
- Check Flask app has: `app = Flask(__name__, static_folder='static')`
- Restart Flask server

### Issue: CSS loads but styles don't apply
**Solution**:
- Check browser console for CSS errors
- Verify CSS syntax is correct
- Try hard refresh (Ctrl+Shift+R)

### Issue: Styles work in one browser but not another
**Solution**:
- Clear cache in the problematic browser
- Check browser compatibility
- Try incognito/private mode

## Manual Verification

1. **Check if CSS file exists:**
   ```powershell
   Test-Path "static\style.css"
   ```
   Should return: `True`

2. **Check CSS file size:**
   ```powershell
   (Get-Item "static\style.css").Length
   ```
   Should be > 10,000 bytes

3. **View CSS in browser:**
   - Navigate to: `http://localhost:5000/static/style.css`
   - You should see CSS code, not an error

4. **Check Flask static folder:**
   - In `app.py`, verify: `app = Flask(__name__, static_folder='static')`

## Still Not Working?

1. **Restart Flask server completely**
   - Stop the server (Ctrl+C)
   - Start again: `python app.py`

2. **Try a different browser**
   - Sometimes browser extensions interfere

3. **Check file permissions**
   - Make sure CSS file is readable

4. **Verify template is loading CSS:**
   - View page source (Ctrl+U)
   - Look for: `<link rel="stylesheet" href="/static/style.css?v=1.0">`
   - Click the link to see if CSS loads

## Test Route

Visit: `http://localhost:5000/test-static`
This will show if static files are configured correctly.

