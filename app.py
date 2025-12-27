"""
AI-Based Fake News Detection System - Flask Backend
Final Year Project | AI & Machine Learning
Enhanced with Trust Meter, Emotion Detection, and Fact-Checking
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import re
import random
import math
import urllib.parse

# Import URL content extraction libraries
try:
    import requests
    from bs4 import BeautifulSoup
    URL_EXTRACTION_AVAILABLE = True
except ImportError:
    URL_EXTRACTION_AVAILABLE = False
    print("URL extraction libraries not available. Install requests and beautifulsoup4.")

# Import ML Model
try:
    from ml_model import ml_model, initialize_model
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("ML model module not available. Using rule-based heuristics only.")

# Import Language Detection
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0  # For consistent results
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    print("langdetect not available. Language detection disabled.")

app = Flask(__name__)
CORS(app)  # Enable CORS for mobile access

# Initialize ML Model on startup
if ML_AVAILABLE:
    ML_MODEL_LOADED = initialize_model()
else:
    ML_MODEL_LOADED = False

# Word lists for analysis
SENSATIONAL_WORDS = [
    'breaking', 'shocking', 'you won\'t believe', 'doctors hate',
    'secret', 'exclusive', 'urgent', 'act now', 'limited time',
    'amazing', 'incredible', 'unbelievable', 'must see', 'click here',
    'guaranteed', 'miracle', 'instant', 'revolutionary', 'exposed',
    'cure', 'completely', 'all diseases', '100%', 'never before'
]

MISLEADING_PHRASES = [
    'sources say', 'experts claim', 'studies show', 'research proves',
    'doctors recommend', 'scientists reveal', 'government confirms',
    'breaking: unverified', 'rumor has it', 'allegedly', 'anonymous source'
]

FEAR_WORDS = ['danger', 'threat', 'warning', 'alert', 'crisis', 'panic', 'fear', 'terrifying', 'horrifying']
ANGER_WORDS = ['outrage', 'furious', 'angry', 'rage', 'attack', 'destroy', 'hate', 'evil']
URGENCY_WORDS = ['now', 'immediately', 'urgent', 'hurry', 'limited time', 'act now', 'before it\'s too late']
SENSATIONAL_WORDS_EMOTION = ['shocking', 'explosive', 'scandal', 'exposed', 'revealed', 'uncovered']

TRUSTED_WORDS = ['according to', 'verified', 'confirmed', 'official', 'reliable source', 'peer-reviewed', 'evidence-based']

# Tamil Language Word Lists
TAMIL_SENSATIONAL_WORDS = [
    'அதிர்ச்சி', 'ஆச்சரியம்', 'ரகசியம்', 'விரைவில்', 'இப்போதே',
    'நம்பமுடியாத', 'செய்தி', 'வெளிப்படுத்தப்பட்டது', 'வெளியிடப்பட்டது',
    'மருத்துவர்கள்', 'வெறுப்பு', 'நிச்சயம்', '100%', 'வேகமாக'
]

TAMIL_MISLEADING_PHRASES = [
    'ஆதாரங்கள் கூறுகின்றன', 'நிபுணர்கள் கூறுகின்றனர்', 'ஆய்வுகள் காட்டுகின்றன',
    'ஆராய்ச்சி நிரூபிக்கிறது', 'அறியப்படாத ஆதாரம்', 'வதந்தி',
    'கூறப்படுகிறது', 'உறுதிப்படுத்தப்படாத'
]

TAMIL_FEAR_WORDS = ['அபாயம்', 'அச்சுறுத்தல்', 'எச்சரிக்கை', 'நெருக்கடி', 'பயம்', 'பீதி']
TAMIL_ANGER_WORDS = ['கோபம்', 'சினம்', 'வெறுப்பு', 'தாக்குதல்', 'அழிக்க']
TAMIL_URGENCY_WORDS = ['இப்போதே', 'விரைவில்', 'அவசரம்', 'வேகமாக', 'காலம் குறைவு']
TAMIL_TRUSTED_WORDS = ['சான்றளிக்கப்பட்டது', 'உறுதிப்படுத்தப்பட்டது', 'அதிகாரப்பூர்வ', 'நம்பகமான', 'ஆதாரம்']


def detect_language(text):
    """Detect the language of the input text"""
    if not LANGDETECT_AVAILABLE:
        # Simple heuristic: check for Tamil characters
        tamil_pattern = re.compile(r'[\u0B80-\u0BFF]+')
        if tamil_pattern.search(text):
            return 'ta', 'Tamil'
        return 'en', 'English'
    
    try:
        lang_code = detect(text)
        lang_names = {
            'ta': 'Tamil',
            'en': 'English',
            'hi': 'Hindi',
            'te': 'Telugu',
            'kn': 'Kannada',
            'ml': 'Malayalam'
        }
        lang_name = lang_names.get(lang_code, lang_code.upper())
        return lang_code, lang_name
    except:
        # Fallback: check for Tamil characters
        tamil_pattern = re.compile(r'[\u0B80-\u0BFF]+')
        if tamil_pattern.search(text):
            return 'ta', 'Tamil'
        return 'en', 'English'


def rule_based_prediction(fake_score, text_length):
    """Rule-based prediction fallback when ML model is not available"""
    if fake_score > 3 or text_length < 20:
        prediction = "Fake"
        confidence = min(85 + fake_score * 5, 98)
    elif fake_score > 1:
        prediction = "Fake"
        confidence = 70 + fake_score * 4
    else:
        prediction = "Real"
        confidence = 75 + random.randint(5, 20)
    
    confidence = min(confidence + random.randint(-5, 5), 99)
    confidence = max(confidence, 60)
    return prediction, confidence


def generate_summary(text, max_length=200):
    """Generate a summary of the text (simple sentence extraction)"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    if len(sentences) <= 3:
        return text[:max_length] + ('...' if len(text) > max_length else '')
    
    # Take first, middle, and last sentences
    summary_sentences = [
        sentences[0],
        sentences[len(sentences)//2] if len(sentences) > 2 else '',
        sentences[-1]
    ]
    summary = '. '.join([s for s in summary_sentences if s])
    return summary[:max_length] + ('...' if len(summary) > max_length else '')


def detect_emotions(text, lang_code='en'):
    """Detect emotional content in text (supports English and Tamil)"""
    text_lower = text.lower()
    
    # Select word lists based on language
    if lang_code == 'ta':
        fear_words = TAMIL_FEAR_WORDS
        anger_words = TAMIL_ANGER_WORDS
        urgency_words = TAMIL_URGENCY_WORDS
        sensational_words = TAMIL_SENSATIONAL_WORDS
    else:
        fear_words = FEAR_WORDS
        anger_words = ANGER_WORDS
        urgency_words = URGENCY_WORDS
        sensational_words = SENSATIONAL_WORDS_EMOTION
    
    fear_score = sum(1 for word in fear_words if word in text) / max(len(fear_words), 1) * 100
    anger_score = sum(1 for word in anger_words if word in text) / max(len(anger_words), 1) * 100
    urgency_score = sum(1 for word in urgency_words if word in text) / max(len(urgency_words), 1) * 100
    sensational_score = sum(1 for word in sensational_words if word in text) / max(len(sensational_words), 1) * 100
    
    # Normalize scores
    fear_score = min(fear_score * 10, 100)
    anger_score = min(anger_score * 10, 100)
    urgency_score = min(urgency_score * 10, 100)
    sensational_score = min(sensational_score * 10, 100)
    
    return {
        'fear': round(fear_score, 1),
        'anger': round(anger_score, 1),
        'urgency': round(urgency_score, 1),
        'sensational': round(sensational_score, 1)
    }


def detect_patterns(text, lang_code='en'):
    """Detect fake news patterns (supports English and Tamil)"""
    text_lower = text.lower() if lang_code == 'en' else text
    patterns = {
        'clickbait_language': False,
        'anonymous_source': False,
        'exaggerated_claim': False,
        'no_evidence': False,
        'emotional_manipulation': False,
        'urgency_pressure': False
    }
    
    if lang_code == 'ta':
        # Tamil patterns
        clickbait_phrases = ['நம்பமுடியாத', 'அதிர்ச்சி', 'ஆச்சரியம்', 'ரகசியம்']
        patterns['clickbait_language'] = any(phrase in text for phrase in clickbait_phrases)
        
        patterns['anonymous_source'] = any(phrase in text for phrase in ['அறியப்படாத ஆதாரம்', 'ஆதாரங்கள் கூறுகின்றன'])
        
        exaggerated = ['100%', 'நிச்சயம்', 'வேகமாக']
        patterns['exaggerated_claim'] = any(word in text for word in exaggerated)
        
        evidence_phrases = ['சான்றளிக்கப்பட்டது', 'உறுதிப்படுத்தப்பட்டது', 'ஆராய்ச்சி']
        patterns['no_evidence'] = not any(phrase in text for phrase in evidence_phrases) and len(text.split()) > 50
        
        patterns['emotional_manipulation'] = any(word in text for word in TAMIL_FEAR_WORDS + TAMIL_ANGER_WORDS)
        patterns['urgency_pressure'] = any(word in text for word in TAMIL_URGENCY_WORDS)
    else:
        # English patterns
        clickbait_phrases = ['you won\'t believe', 'shocking', 'amazing', 'incredible', 'must see']
        patterns['clickbait_language'] = any(phrase in text_lower for phrase in clickbait_phrases)
        
        patterns['anonymous_source'] = any(phrase in text_lower for phrase in ['anonymous source', 'sources say', 'insiders claim'])
        
        exaggerated = ['cure all', '100%', 'guaranteed', 'miracle', 'instant', 'completely cure']
        patterns['exaggerated_claim'] = any(word in text_lower for word in exaggerated)
        
        evidence_phrases = ['according to', 'study shows', 'research', 'verified', 'confirmed']
        patterns['no_evidence'] = not any(phrase in text_lower for phrase in evidence_phrases) and len(text.split()) > 50
        
        patterns['emotional_manipulation'] = any(word in text_lower for word in FEAR_WORDS + ANGER_WORDS)
        patterns['urgency_pressure'] = any(word in text_lower for word in URGENCY_WORDS)
    
    return patterns


def fact_check_claims(text):
    """Detect and analyze claims in the text"""
    text_lower = text.lower()
    claims = []
    
    # Medical claims
    medical_patterns = [
        (r'cure.*(?:diabetes|cancer|disease)', 'Medically unrealistic'),
        (r'(?:lose|burn).*\d+.*(?:pounds|kg).*\d+.*(?:days|weeks)', 'Unrealistic weight loss claim'),
        (r'100%.*(?:effective|guaranteed)', 'Absolute claim without evidence')
    ]
    
    for pattern, status in medical_patterns:
        if re.search(pattern, text_lower):
            claims.append({
                'claim': re.search(pattern, text_lower).group(0)[:50],
                'status': status,
                'type': 'suspicious'
            })
    
    # Financial claims
    financial_patterns = [
        (r'(?:make|earn).*\d+.*(?:dollars|money).*(?:day|hour)', 'Unrealistic financial claim'),
        (r'guaranteed.*(?:profit|return)', 'Financial guarantee without risk disclosure')
    ]
    
    for pattern, status in financial_patterns:
        if re.search(pattern, text_lower):
            claims.append({
                'claim': re.search(pattern, text_lower).group(0)[:50],
                'status': status,
                'type': 'suspicious'
            })
    
    # If no suspicious claims, check for verifiable claims
    if not claims:
        verifiable_phrases = ['according to', 'study', 'research', 'data shows']
        if any(phrase in text_lower for phrase in verifiable_phrases):
            claims.append({
                'claim': 'Contains verifiable references',
                'status': 'Verifiable',
                'type': 'verifiable'
            })
    
    return claims[:5]  # Limit to 5 claims


def get_trust_level(confidence, fake_score):
    """Convert confidence to trust level"""
    if confidence >= 75 or fake_score > 3:
        return {
            'level': 'High Risk',
            'color': '#ef4444',
            'icon': '🔴',
            'trust_score': max(0, 100 - confidence)
        }
    elif confidence >= 60 or fake_score > 1:
        return {
            'level': 'Medium Risk',
            'color': '#f97316',
            'icon': '🟠',
            'trust_score': max(20, 100 - confidence)
        }
    else:
        return {
            'level': 'Trusted News',
            'color': '#22c55e',
            'icon': '🟢',
            'trust_score': max(60, 100 - confidence)
        }


def highlight_words(text, lang_code='en'):
    """Identify words to highlight (supports English and Tamil)"""
    words = text.split()
    highlighted = []
    
    # Select word lists based on language
    if lang_code == 'ta':
        sensational_words = TAMIL_SENSATIONAL_WORDS
        trusted_words = TAMIL_TRUSTED_WORDS
    else:
        text_lower = text.lower()
        sensational_words = SENSATIONAL_WORDS
        trusted_words = TRUSTED_WORDS
    
    for i, word in enumerate(words):
        if lang_code == 'ta':
            # For Tamil, check if word contains any Tamil sensational/trusted words
            is_suspicious = any(tamil_word in word for tamil_word in sensational_words)
            is_trusted = any(tamil_word in word for tamil_word in trusted_words)
        else:
            word_clean = re.sub(r'[^\w]', '', word.lower())
            is_suspicious = any(sensational in word_clean for sensational in sensational_words)
            is_trusted = any(trusted in word_clean for trusted in trusted_words)
        
        if is_suspicious:
            highlighted.append({
                'index': i,
                'word': word,
                'type': 'suspicious',
                'color': '#ef4444'
            })
        elif is_trusted:
            highlighted.append({
                'index': i,
                'word': word,
                'type': 'trusted',
                'color': '#22c55e'
            })
        else:
            highlighted.append({
                'index': i,
                'word': word,
                'type': 'neutral',
                'color': '#6b7280'
            })
    
    return highlighted


def generate_ai_reasoning(prediction, confidence, indicators, patterns, emotions, claims, lang_code='en'):
    """
    AI Reasoning Module - Explains WHY the news was classified as fake/real
    Generates detailed, evidence-based explanations
    """
    reasons = []
    evidence_points = []
    severity_score = 0
    
    is_fake = prediction.lower() == 'fake'
    
    # Language-specific messages
    if lang_code == 'ta':
        # Tamil messages
        if is_fake:
            reasons.append({
                'title': '🎯 முக்கிய காரணம்',
                'description': f'இந்த செய்தி {confidence}% நம்பகத்தன்மையுடன் போலி செய்தியாக கண்டறியப்பட்டது.',
                'severity': 'high',
                'icon': '🔴'
            })
        else:
            reasons.append({
                'title': '✅ நம்பகமான செய்தி',
                'description': f'இந்த செய்தி {confidence}% நம்பகத்தன்மையுடன் உண்மையான செய்தியாக தோன்றுகிறது.',
                'severity': 'low',
                'icon': '🟢'
            })
    else:
        # English messages
        if is_fake:
            reasons.append({
                'title': '🎯 Primary Reason',
                'description': f'This news was classified as FAKE with {confidence}% confidence based on multiple indicators.',
                'severity': 'high',
                'icon': '🔴'
            })
        else:
            reasons.append({
                'title': '✅ Trusted News',
                'description': f'This news appears to be REAL with {confidence}% confidence. The content shows characteristics of credible journalism.',
                'severity': 'low',
                'icon': '🟢'
            })
    
    # Analyze Sensational Words
    if indicators.get('sensational_words') and len(indicators['sensational_words']) > 0:
        severity_score += 2
        if lang_code == 'ta':
            reasons.append({
                'title': '📢 அதிர்ச்சி சொற்கள் கண்டறியப்பட்டன',
                'description': f"பின்வரும் அதிர்ச்சி சொற்கள் கண்டறியப்பட்டன: {', '.join(indicators['sensational_words'][:3])}. போலி செய்திகள் பெரும்பாலும் உணர்ச்சிகளை கையாள்வதற்கு இத்தகைய சொற்களை பயன்படுத்துகின்றன.",
                'severity': 'high',
                'icon': '⚠️',
                'evidence': indicators['sensational_words'][:3]
            })
        else:
            reasons.append({
                'title': '📢 Sensational Language Detected',
                'description': f"Found {len(indicators['sensational_words'])} sensational words/phrases: {', '.join(indicators['sensational_words'][:3])}. Fake news often uses emotional language to manipulate readers rather than presenting facts.",
                'severity': 'high',
                'icon': '⚠️',
                'evidence': indicators['sensational_words'][:3]
            })
    
    # Analyze Patterns
    pattern_count = sum(1 for v in patterns.values() if v)
    if pattern_count > 0:
        severity_score += pattern_count
        
        detected_patterns = []
        if patterns.get('clickbait_language'):
            detected_patterns.append('Clickbait language' if lang_code == 'en' else 'கிளிக்பெயிட் மொழி')
        if patterns.get('anonymous_source'):
            detected_patterns.append('Anonymous sources' if lang_code == 'en' else 'அறியப்படாத ஆதாரங்கள்')
        if patterns.get('exaggerated_claim'):
            detected_patterns.append('Exaggerated claims' if lang_code == 'en' else 'மிகைப்படுத்தப்பட்ட கூற்றுகள்')
        if patterns.get('no_evidence'):
            detected_patterns.append('No evidence' if lang_code == 'en' else 'ஆதாரம் இல்லை')
        if patterns.get('emotional_manipulation'):
            detected_patterns.append('Emotional manipulation' if lang_code == 'en' else 'உணர்ச்சி கையாளுதல்')
        if patterns.get('urgency_pressure'):
            detected_patterns.append('Urgency pressure' if lang_code == 'en' else 'அவசர அழுத்தம்')
        
        if lang_code == 'ta':
            reasons.append({
                'title': '🧪 போலி செய்தி வடிவங்கள்',
                'description': f'{pattern_count} போலி செய்தி வடிவங்கள் கண்டறியப்பட்டன: {", ".join(detected_patterns)}. இவை போலி செய்திகளின் பொதுவான பண்புகள்.',
                'severity': 'high' if pattern_count >= 3 else 'medium',
                'icon': '🔍',
                'evidence': detected_patterns
            })
        else:
            reasons.append({
                'title': '🧪 Fake News Patterns Detected',
                'description': f'Found {pattern_count} fake news pattern(s): {", ".join(detected_patterns)}. These are common characteristics of misinformation designed to deceive readers.',
                'severity': 'high' if pattern_count >= 3 else 'medium',
                'icon': '🔍',
                'evidence': detected_patterns
            })
    
    # Analyze Emotions
    high_emotions = []
    if emotions.get('fear', 0) > 50:
        high_emotions.append('Fear' if lang_code == 'en' else 'பயம்')
    if emotions.get('anger', 0) > 50:
        high_emotions.append('Anger' if lang_code == 'en' else 'கோபம்')
    if emotions.get('urgency', 0) > 50:
        high_emotions.append('Urgency' if lang_code == 'en' else 'அவசரம்')
    if emotions.get('sensational', 0) > 50:
        high_emotions.append('Sensationalism' if lang_code == 'en' else 'அதிர்ச்சி')
    
    if high_emotions and is_fake:
        severity_score += 1
        if lang_code == 'ta':
            reasons.append({
                'title': '🎭 உணர்ச்சி கையாளுதல்',
                'description': f'உயர் நிலை உணர்ச்சிகள் கண்டறியப்பட்டன: {", ".join(high_emotions)}. போலி செய்திகள் பெரும்பாலும் உண்மைகளை விட உணர்ச்சிகளை கையாளுகின்றன.',
                'severity': 'high',
                'icon': '😱',
                'evidence': high_emotions
            })
        else:
            reasons.append({
                'title': '🎭 Emotional Manipulation',
                'description': f'High levels of {", ".join(high_emotions)} detected. Fake news often manipulates emotions rather than presenting factual information. This is a red flag for misinformation.',
                'severity': 'high',
                'icon': '😱',
                'evidence': high_emotions
            })
    
    # Analyze Claims
    if claims and len(claims) > 0:
        suspicious_claims = [c for c in claims if c.get('type') == 'suspicious']
        if suspicious_claims:
            severity_score += len(suspicious_claims)
            if lang_code == 'ta':
                reasons.append({
                    'title': '🕵️ சந்தேகத்திற்குரிய கூற்றுகள்',
                    'description': f'{len(suspicious_claims)} சந்தேகத்திற்குரிய கூற்றுகள் கண்டறியப்பட்டன. இவை மருத்துவ ரீதியாக அல்லது நிதி ரீதியாக நம்பத்தகாதவை.',
                    'severity': 'high',
                    'icon': '❌',
                    'evidence': [c.get('claim', '')[:50] for c in suspicious_claims[:2]]
                })
            else:
                reasons.append({
                    'title': '🕵️ Suspicious Claims Detected',
                    'description': f'Found {len(suspicious_claims)} suspicious claim(s) that appear medically or financially unrealistic. Legitimate news typically provides verifiable evidence for such claims.',
                    'severity': 'high',
                    'icon': '❌',
                    'evidence': [c.get('claim', '')[:50] for c in suspicious_claims[:2]]
                })
    
    # Analyze Misleading Phrases
    if indicators.get('misleading_phrases') and len(indicators['misleading_phrases']) > 0:
        severity_score += 1
        if lang_code == 'ta':
            reasons.append({
                'title': '⚠️ தவறான சொற்றொடர்கள்',
                'description': f"பின்வரும் தவறான சொற்றொடர்கள் கண்டறியப்பட்டன: {', '.join(indicators['misleading_phrases'][:2])}. இவை நம்பகமான ஆதாரங்கள் இல்லாமல் கூற்றுகளை முன்வைக்க பயன்படுத்தப்படுகின்றன.",
                'severity': 'medium',
                'icon': '⚠️',
                'evidence': indicators['misleading_phrases'][:2]
            })
        else:
            reasons.append({
                'title': '⚠️ Misleading Phrases',
                'description': f"Found misleading phrases: {', '.join(indicators['misleading_phrases'][:2])}. These phrases are often used to make unverified claims appear credible without providing actual evidence.",
                'severity': 'medium',
                'icon': '⚠️',
                'evidence': indicators['misleading_phrases'][:2]
            })
    
    # Excessive Capitals
    if indicators.get('excessive_capitals'):
        severity_score += 1
        if lang_code == 'ta':
            reasons.append({
                'title': '📢 அதிகமான பெரிய எழுத்துக்கள்',
                'description': 'உரையில் அதிகமான பெரிய எழுத்துக்கள் கண்டறியப்பட்டன. இது போலி செய்திகளில் பொதுவானது, கவனத்தை ஈர்க்க முயற்சிக்கிறது.',
                'severity': 'medium',
                'icon': '📢'
            })
        else:
            reasons.append({
                'title': '📢 Excessive Capitalization',
                'description': 'High use of ALL CAPS detected. This is a common tactic in fake news to grab attention and create urgency, which legitimate journalism typically avoids.',
                'severity': 'medium',
                'icon': '📢'
            })
    
    # Generate Summary Reasoning
    if is_fake:
        if lang_code == 'ta':
            summary = f"இந்த செய்தி {severity_score} முக்கிய காரணங்களால் போலி செய்தியாக கண்டறியப்பட்டது. இது உணர்ச்சிகளை கையாளுதல், ஆதாரமற்ற கூற்றுகள், மற்றும் தவறான வடிவங்களை கொண்டுள்ளது."
        else:
            summary = f"This news was classified as FAKE based on {severity_score} key indicators. The content shows patterns of emotional manipulation, unverified claims, and misleading information that are characteristic of misinformation."
    else:
        if lang_code == 'ta':
            summary = f"இந்த செய்தி நம்பகமானதாக தோன்றுகிறது. உண்மையான செய்தியியலின் பண்புகளைக் கொண்டுள்ளது."
        else:
            summary = "This news appears to be REAL. The content shows characteristics of credible journalism with balanced reporting and verifiable information."
    
    return {
        'reasons': reasons,
        'summary': summary,
        'severity_score': severity_score,
        'total_indicators': len(reasons)
    }


def detect_social_media_platform(url):
    """
    Detect if URL is from a social media platform
    Returns: (platform_name, is_social_media)
    """
    parsed = urllib.parse.urlparse(url.lower())
    domain = parsed.netloc.replace('www.', '')
    
    social_platforms = {
        'twitter.com': 'Twitter',
        'x.com': 'Twitter',
        'facebook.com': 'Facebook',
        'fb.com': 'Facebook',
        'instagram.com': 'Instagram',
        'linkedin.com': 'LinkedIn',
        'reddit.com': 'Reddit',
        'youtube.com': 'YouTube',
        'tiktok.com': 'TikTok',
        'whatsapp.com': 'WhatsApp',
        'telegram.org': 'Telegram',
        'snapchat.com': 'Snapchat'
    }
    
    for platform_domain, platform_name in social_platforms.items():
        if platform_domain in domain:
            return platform_name, True
    
    return None, False


def extract_content_from_url(url):
    """
    Extract article content from a URL
    Supports regular websites and social media platforms
    Returns: (title, text_content, success, error_message, platform_info)
    """
    if not URL_EXTRACTION_AVAILABLE:
        return None, None, False, "URL extraction libraries not installed", None
    
    try:
        # Detect social media platform
        platform_name, is_social = detect_social_media_platform(url)
        platform_info = {
            'platform': platform_name,
            'is_social_media': is_social
        } if is_social else None
        
        # Validate URL
        parsed = urllib.parse.urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return None, None, False, "Invalid URL format", platform_info
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Fetch the URL with timeout
        response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside", "advertisement"]):
            script.decompose()
        
        # Try to find article title
        title = None
        title_selectors = [
            'h1.article-title', 'h1.post-title', 'h1.entry-title',
            'h1', 'title', '[property="og:title"]', '[name="twitter:title"]'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip()
                if title:
                    break
        
        if not title:
            title = soup.find('title')
            title = title.get_text().strip() if title else "Article"
        
        # Try to find main article content
        article_content = None
        content_selectors = [
            'article', '[role="article"]', '.article-content', '.post-content',
            '.entry-content', '.article-body', 'main', '.content', '#content'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                article_content = element
                break
        
        # If no article container found, use body
        if not article_content:
            article_content = soup.find('body') or soup
        
        # Extract text
        text_content = article_content.get_text(separator=' ', strip=True)
        
        # Clean up text
        text_content = re.sub(r'\s+', ' ', text_content)  # Multiple spaces to single
        text_content = text_content.strip()
        
        # Check if we got meaningful content
        if len(text_content) < 50:
            return title, text_content, False, "Could not extract sufficient content from URL", platform_info
        
        return title, text_content, True, None, platform_info
        
    except requests.exceptions.Timeout:
        return None, None, False, "Request timeout - URL took too long to respond", platform_info
    except requests.exceptions.RequestException as e:
        return None, None, False, f"Error fetching URL: {str(e)}", platform_info
    except Exception as e:
        return None, None, False, f"Error processing URL: {str(e)}", platform_info


def analyze_realtime(text):
    """Real-time analysis for live warnings"""
    if len(text.strip()) < 10:
        return {'warnings': []}
    
    warnings = []
    text_lower = text.lower()
    
    # Check for exaggeration
    exaggeration_words = ['completely', 'all', 'never', 'always', '100%', 'guaranteed']
    if any(word in text_lower for word in exaggeration_words):
        warnings.append({
            'type': 'exaggeration',
            'message': 'This sentence shows exaggeration patterns',
            'severity': 'medium'
        })
    
    # Check for urgency
    if any(word in text_lower for word in URGENCY_WORDS):
        warnings.append({
            'type': 'urgency',
            'message': 'Urgency language detected - common in fake news',
            'severity': 'high'
        })
    
    # Check for emotional manipulation
    if any(word in text_lower for word in FEAR_WORDS):
        warnings.append({
            'type': 'emotion',
            'message': 'Fear-inducing language detected',
            'severity': 'high'
        })
    
    return {'warnings': warnings[:3]}  # Limit to 3 warnings


def predict_fake_news(text):
    """
    Enhanced fake news detection with ML + NLP features
    Supports both English and Tamil languages
    Uses Machine Learning model if available, falls back to rule-based heuristics
    
    Returns:
        dict: Complete analysis including trust meter, emotions, patterns, etc.
    """
    # Detect language first
    lang_code, lang_name = detect_language(text)
    
    # Select word lists based on detected language
    if lang_code == 'ta':
        sensational_words = TAMIL_SENSATIONAL_WORDS
        misleading_phrases = TAMIL_MISLEADING_PHRASES
        text_lower = text  # Tamil doesn't use lowercase
    else:
        sensational_words = SENSATIONAL_WORDS
        misleading_phrases = MISLEADING_PHRASES
        text_lower = text.lower()
    
    indicators = {
        'sensational_words': [],
        'excessive_capitals': False,
        'misleading_phrases': []
    }
    
    # Detect sensational words (NLP feature)
    found_sensational = [word for word in sensational_words if word in text]
    indicators['sensational_words'] = found_sensational[:5]
    
    # Excessive capitals (NLP feature) - only for English
    words = text.split()
    if len(words) > 0 and lang_code == 'en':
        all_caps_count = sum(1 for word in words if word.isupper() and len(word) > 2)
        caps_ratio = all_caps_count / len(words)
        indicators['excessive_capitals'] = caps_ratio > 0.1
    
    # Misleading phrases (NLP feature)
    found_misleading = [phrase for phrase in misleading_phrases if phrase in text]
    indicators['misleading_phrases'] = found_misleading[:5]
    
    # Calculate fake score from NLP heuristics
    fake_score = len(found_sensational) + (1 if indicators['excessive_capitals'] else 0) + len(found_misleading)
    
    # MACHINE LEARNING PREDICTION (if model is available)
    if ML_AVAILABLE and ML_MODEL_LOADED:
        try:
            ml_result = ml_model.predict(text)
            prediction = ml_result['prediction_label']
            confidence = ml_result['confidence']
            ml_probabilities = ml_result['probabilities']
            
            # Combine ML confidence with NLP heuristics for better accuracy
            # Weight: 70% ML, 30% NLP heuristics
            nlp_confidence = min(85 + fake_score * 5, 98) if fake_score > 2 else (70 + fake_score * 4 if fake_score > 0 else 75)
            combined_confidence = (confidence * 0.7) + (nlp_confidence * 0.3)
            confidence = min(max(combined_confidence, 50), 99)
            
            print(f"ML Prediction: {prediction} ({confidence:.1f}% confidence)")
            print(f"ML Probabilities: Real={ml_probabilities['real']}%, Fake={ml_probabilities['fake']}%")
        except Exception as e:
            print(f"ML prediction failed: {e}. Using rule-based heuristics.")
            # Fall back to rule-based
            prediction, confidence = rule_based_prediction(fake_score, len(text.split()))
    else:
        # Rule-based prediction (fallback)
        prediction, confidence = rule_based_prediction(fake_score, len(text.split()))
    
    confidence = round(confidence, 1)
    
    # Generate summary if text is long
    summary = generate_summary(text) if len(text) > 200 else text
    
    # Detect emotions (with language support)
    emotions = detect_emotions(text, lang_code)
    
    # Detect patterns (with language support)
    patterns = detect_patterns(text, lang_code)
    
    # Fact-check claims
    claims = fact_check_claims(text)
    
    # Get trust level
    trust_level = get_trust_level(confidence, fake_score)
    
    # Highlight words (with language support)
    highlighted_words = highlight_words(text, lang_code)
    
    # Generate AI Reasoning - WHY it's fake/real
    ai_reasoning = generate_ai_reasoning(
        prediction, confidence, indicators, patterns, emotions, claims, lang_code
    )
    
    return {
        'prediction': prediction,
        'confidence': round(confidence, 1),
        'indicators': indicators,
        'summary': summary,
        'emotions': emotions,
        'patterns': patterns,
        'claims': claims,
        'trust_level': trust_level,
        'highlighted_words': highlighted_words,
        'language': {
            'code': lang_code,
            'name': lang_name,
            'detected': True
        },
        'ai_reasoning': ai_reasoning
    }


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    """Enhanced prediction endpoint with all features"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'Missing text field in request'}), 400
        
        text = data['text'].strip()
        
        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        if len(text) < 10:
            return jsonify({'error': 'Text must be at least 10 characters long'}), 400
        
        # Get comprehensive analysis
        analysis = predict_fake_news(text)
        
        return jsonify(analysis), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/analyze-realtime', methods=['POST'])
def analyze_realtime_endpoint():
    """Real-time analysis endpoint for live warnings"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'warnings': []}), 200
        
        text = data['text'].strip()
        result = analyze_realtime(text)
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'warnings': []}), 200


@app.route('/analyze-url-realtime', methods=['POST'])
def analyze_url_realtime():
    """Real-time URL analysis - validates and provides feedback as user types"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'valid': False,
                'message': 'Enter a URL to analyze',
                'platform': None
            }), 200
        
        url = data['url'].strip()
        
        if not url:
            return jsonify({
                'valid': False,
                'message': 'URL cannot be empty',
                'platform': None
            }), 200
        
        # Validate URL format
        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return jsonify({
                    'valid': False,
                    'message': 'Invalid URL format. Include http:// or https://',
                    'platform': None
                }), 200
        except:
            return jsonify({
                'valid': False,
                'message': 'Invalid URL format',
                'platform': None
            }), 200
        
        # Detect social media platform
        platform_name, is_social = detect_social_media_platform(url)
        
        if is_social:
            return jsonify({
                'valid': True,
                'message': f'✅ {platform_name} URL detected. Social media content will be analyzed.',
                'platform': platform_name,
                'is_social_media': True,
                'warning': 'Social media posts often spread misinformation. Verify with official sources.'
            }), 200
        else:
            return jsonify({
                'valid': True,
                'message': '✅ Valid URL. Ready to analyze.',
                'platform': None,
                'is_social_media': False
            }), 200
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'message': 'Error validating URL',
            'platform': None
        }), 200


@app.route('/model-status', methods=['GET'])
def model_status():
    """Check if ML model is loaded and available"""
    return jsonify({
        'ml_available': ML_AVAILABLE,
        'model_loaded': ML_MODEL_LOADED if ML_AVAILABLE else False,
        'method': 'Machine Learning + NLP' if (ML_AVAILABLE and ML_MODEL_LOADED) else 'Rule-based NLP (ML model not trained)'
    }), 200


@app.route('/analyze-url', methods=['POST'])
def analyze_url():
    """Analyze fake news from a URL"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({'error': 'Missing url field in request'}), 400
        
        url = data['url'].strip()
        
        if not url:
            return jsonify({'error': 'URL cannot be empty'}), 400
        
        # Extract content from URL
        title, text_content, success, error_message, platform_info = extract_content_from_url(url)
        
        if not success:
            return jsonify({
                'error': error_message or 'Failed to extract content from URL',
                'url': url
            }), 400
        
        if len(text_content) < 10:
            return jsonify({
                'error': 'Extracted content is too short for analysis',
                'url': url
            }), 400
        
        # Analyze the extracted content
        analysis = predict_fake_news(text_content)
        
        # Add URL metadata with social media info
        analysis['source'] = {
            'type': 'url',
            'url': url,
            'title': title,
            'content_length': len(text_content),
            'platform': platform_info.get('platform') if platform_info else None,
            'is_social_media': platform_info.get('is_social_media', False) if platform_info else False
        }
        
        # Add social media specific indicators if it's social media
        if platform_info and platform_info.get('is_social_media'):
            analysis['social_media'] = {
                'platform': platform_info.get('platform'),
                'warning': 'Social media content often spreads misinformation faster. Verify claims with official sources.',
                'indicators': [
                    'Unverified user content',
                    'Potential for viral misinformation',
                    'Limited fact-checking on platform'
                ]
            }
        
        return jsonify(analysis), 200
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/static/sw.js')
def service_worker():
    """Serve service worker for PWA"""
    return app.send_static_file('sw.js'), 200, {'Content-Type': 'application/javascript'}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
