# 🔗 URL Extraction Libraries Installation

## ✅ Libraries Already Installed!

The required libraries are already installed in your system:
- ✅ `requests` - For HTTP requests
- ✅ `beautifulsoup4` - For HTML parsing
- ✅ `lxml` - For XML/HTML parsing

## 🔄 Solution: Restart Your Flask App

The error message appears because the Flask app was started **before** the libraries were installed. You need to **restart the Flask application** for it to detect the libraries.

### Steps:

1. **Stop the current Flask app** (if running)
   - Press `Ctrl+C` in the terminal where Flask is running

2. **Restart the Flask app**
   ```bash
   python app.py
   ```

3. **Verify it's working**
   - You should see the app start without the "URL extraction libraries not available" message
   - The URL input feature should now work

## 🧪 Test URL Feature

After restarting, test the URL feature:

1. Open the app: `http://localhost:5000`
2. Click the **"🔗 URL Input"** tab
3. Paste a news article URL
4. Click "Detect Fake News"

## 📦 Manual Installation (If Needed)

If you still get errors, manually install:

```bash
pip install requests beautifulsoup4 lxml
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## ✅ Verification

To verify libraries are installed:

```bash
python -c "import requests; from bs4 import BeautifulSoup; import lxml; print('✅ All libraries installed!')"
```

If this prints "✅ All libraries installed!" - you're good to go!

## 🎯 Quick Fix

**Just restart your Flask app and the URL feature will work!** 🚀

