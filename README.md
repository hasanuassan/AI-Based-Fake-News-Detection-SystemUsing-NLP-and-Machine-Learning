# AI-Based Fake News Detection System

A modern, professional web application for detecting fake news using Machine Learning and NLP techniques.

## Features

- 🎨 **Premium UI/UX**: Modern, clean, and attractive interface
- 📱 **Mobile-First**: Fully responsive design optimized for mobile devices
- 🌓 **Dark/Light Mode**: Toggle between themes with smooth transitions
- ⚡ **Real-time Analysis**: Instant fake news detection with confidence scores
- 📊 **Visual Feedback**: Animated progress bars and result badges
- 🎯 **Smart Validation**: Character counter and input validation

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **ML Model**: Placeholder classifier (ready for your trained model)

## Project Structure

```
.
├── app.py                 # Flask backend server
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
└── static/
    └── js/
        └── script.js     # Frontend JavaScript
```

## Installation & Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Flask Server

```bash
python app.py
```

The server will start on `http://0.0.0.0:5000`

### 3. Access the Application

#### On Your Computer:
- Open browser and go to: `http://localhost:5000`

#### On Mobile Device (Same Network):
1. Find your computer's local IP address:
   - **Windows**: Open Command Prompt and type `ipconfig`
   - **Mac/Linux**: Open Terminal and type `ifconfig`
   - Look for IPv4 address (e.g., `192.168.1.100`)

2. On your mobile device, open browser and go to:
   ```
   http://YOUR_LOCAL_IP:5000
   ```
   Example: `http://192.168.1.100:5000`

## Usage

1. **Enter News Text**: Paste or type the news article in the text area
2. **Click Detect**: Press the "Detect Fake News" button
3. **View Results**: See the prediction (Fake/Real) with confidence score
4. **Analyze More**: Click "Analyze Another Article" to test more news

## API Endpoint

### POST `/predict`

**Request:**
```json
{
  "text": "Your news article text here..."
}
```

**Response:**
```json
{
  "prediction": "Fake",
  "confidence": 92.5
}
```

## Customizing the ML Model

Replace the `predict_fake_news()` function in `app.py` with your actual trained model:

```python
def predict_fake_news(text):
    # Load your model
    model = load_model('your_model.pkl')
    
    # Preprocess text
    processed_text = preprocess(text)
    
    # Get prediction
    prediction = model.predict([processed_text])[0]
    confidence = model.predict_proba([processed_text])[0].max() * 100
    
    return ("Fake" if prediction == 1 else "Real", confidence)
```

## Features Breakdown

### UI Components
- ✅ Premium card-based layout
- ✅ Large text input area with character counter
- ✅ Modern gradient buttons with hover effects
- ✅ Loading spinner during prediction
- ✅ Animated confidence progress bar
- ✅ Color-coded result badges (Red for Fake, Green for Real)
- ✅ Smooth animations and transitions
- ✅ Toast notifications for errors

### Functionality
- ✅ Input validation (min 10 chars, max 5000 chars)
- ✅ Disable button when input is empty
- ✅ Smooth scroll to results
- ✅ Dark/Light mode toggle with persistence
- ✅ Mobile-responsive design
- ✅ Error handling and user feedback

## Browser Compatibility

- Chrome/Edge (Recommended)
- Firefox
- Safari
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### Cannot access from mobile device:
1. Ensure both devices are on the same Wi-Fi network
2. Check Windows Firewall settings (allow port 5000)
3. Verify the local IP address is correct
4. Try disabling VPN if active

### Server not starting:
1. Check if port 5000 is already in use
2. Ensure Flask is installed: `pip install Flask flask-cors`
3. Check Python version (3.7+ required)

## License

Final Year Project | AI & Machine Learning

## Notes

- The current ML model is a placeholder. Replace it with your trained model for production use.
- For production deployment, consider using a proper WSGI server like Gunicorn.
- Add authentication and rate limiting for production use.

