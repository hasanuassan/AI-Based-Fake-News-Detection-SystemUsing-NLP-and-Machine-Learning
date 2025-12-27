/**
 * AI-Based Fake News Detection System - Enhanced Frontend
 * All 10 WOW Features Implemented
 */

// DOM Elements
const newsInput = document.getElementById('newsInput');
const urlInput = document.getElementById('urlInput');
const detectBtn = document.getElementById('detectBtn');
const clearBtn = document.getElementById('clearBtn');
const charCount = document.getElementById('charCount');
const resultSection = document.getElementById('resultSection');
const loadingSpinner = document.getElementById('loadingSpinner');
const btnText = document.getElementById('btnText');
const themeToggle = document.getElementById('themeToggle');
const themeSelector = document.getElementById('themeSelector');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');
const analyzeAnotherBtn = document.getElementById('analyzeAnotherBtn');
const liveWarning = document.getElementById('liveWarning');
const liveWarningText = document.getElementById('liveWarningText');
const summaryCard = document.getElementById('summaryCard');
const summaryText = document.getElementById('summaryText');
const speedometerNeedle = document.getElementById('speedometerNeedle');
const trustLevel = document.getElementById('trustLevel');
const highlightedText = document.getElementById('highlightedText');
const emotionBars = document.getElementById('emotionBars');
const patternChecklist = document.getElementById('patternChecklist');
const factCheckClaims = document.getElementById('factCheckClaims');
const confidenceCountUp = document.getElementById('confidenceCountUp');
const confidenceBar = document.getElementById('confidenceBar');
const body = document.getElementById('body');
const languageCard = document.getElementById('languageCard');
const languageText = document.getElementById('languageText');
const reasoningSummary = document.getElementById('reasoningSummary');
const reasoningSummaryText = document.getElementById('reasoningSummaryText');
const reasoningDetails = document.getElementById('reasoningDetails');
const textModeBtn = document.getElementById('textModeBtn');
const urlModeBtn = document.getElementById('urlModeBtn');
const textInputSection = document.getElementById('textInputSection');
const urlInputSection = document.getElementById('urlInputSection');

// Constants
const MAX_CHARS = 5000;
const API_URL = '/predict';
const URL_API_URL = '/analyze-url';
const REALTIME_URL = '/analyze-realtime';
const URL_REALTIME_URL = '/analyze-url-realtime';

// Input mode: 'text' or 'url'
let inputMode = 'text';

// Real-time URL analysis debounce
let urlRealtimeTimeout;

// Real-time analysis debounce
let realtimeTimeout;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
    setupEventListeners();
    updateCharCount();
    checkPWAInstall();
});

// PWA Install Prompt
function checkPWAInstall() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js', { scope: '/' }).catch(() => {});
    }
}

// Theme Management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme');
    const savedStyle = localStorage.getItem('themeStyle') || 'default';
    
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
    }
    
    applyThemeStyle(savedStyle);
    themeSelector.value = savedStyle;
}

function applyThemeStyle(style) {
    body.className = body.className.replace(/theme-\w+/g, '');
    if (style !== 'default') {
        body.classList.add(`theme-${style}`);
    }
}

// Event Listeners
function setupEventListeners() {
    newsInput.addEventListener('input', handleInputChange);
    newsInput.addEventListener('input', handleRealtimeAnalysis);
    urlInput.addEventListener('input', handleUrlInputChange);
    detectBtn.addEventListener('click', handleDetect);
    clearBtn.addEventListener('click', handleClear);
    analyzeAnotherBtn.addEventListener('click', handleAnalyzeAnother);
    themeToggle.addEventListener('click', toggleTheme);
    themeSelector.addEventListener('change', (e) => {
        applyThemeStyle(e.target.value);
        localStorage.setItem('themeStyle', e.target.value);
    });
    
    // Mode toggle buttons
    textModeBtn.addEventListener('click', () => switchMode('text'));
    urlModeBtn.addEventListener('click', () => switchMode('url'));
}

// Switch between text and URL input modes
function switchMode(mode) {
    inputMode = mode;
    
    if (mode === 'text') {
        textInputSection.classList.remove('hidden');
        urlInputSection.classList.add('hidden');
        textModeBtn.className = 'flex-1 py-2 px-4 rounded-md font-medium transition-all bg-purple-600 text-white';
        urlModeBtn.className = 'flex-1 py-2 px-4 rounded-md font-medium transition-all text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600';
        detectBtn.disabled = newsInput.value.trim().length < 10;
    } else {
        textInputSection.classList.add('hidden');
        urlInputSection.classList.remove('hidden');
        urlModeBtn.className = 'flex-1 py-2 px-4 rounded-md font-medium transition-all bg-purple-600 text-white';
        textModeBtn.className = 'flex-1 py-2 px-4 rounded-md font-medium transition-all text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600';
        detectBtn.disabled = !isValidUrl(urlInput.value);
    }
}

// Validate URL
function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

// Handle URL input change with real-time analysis
function handleUrlInputChange() {
    const url = urlInput.value.trim();
    detectBtn.disabled = !isValidUrl(url);
    
    // Real-time URL analysis
    clearTimeout(urlRealtimeTimeout);
    
    if (url.length < 5) {
        liveWarning.classList.remove('show');
        return;
    }
    
    urlRealtimeTimeout = setTimeout(async () => {
        try {
            const response = await fetch(URL_REALTIME_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            
            const data = await response.json();
            
            if (data.valid) {
                liveWarningText.textContent = data.message;
                liveWarning.classList.add('show');
                
                // Change warning color for social media
                const warningDiv = liveWarning.querySelector('div');
                if (data.is_social_media) {
                    warningDiv.className = 'bg-orange-500 text-white px-4 py-3 rounded-lg shadow-xl';
                    if (data.warning) {
                        liveWarningText.textContent = `${data.message} ⚠️ ${data.warning}`;
                    }
                } else {
                    warningDiv.className = 'bg-green-500 text-white px-4 py-3 rounded-lg shadow-xl';
                }
            } else {
                liveWarningText.textContent = data.message;
                const warningDiv = liveWarning.querySelector('div');
                warningDiv.className = 'bg-yellow-500 text-white px-4 py-3 rounded-lg shadow-xl';
                liveWarning.classList.add('show');
            }
        } catch (error) {
            // Silent fail for real-time
        }
    }, 500);
}

// Real-time Analysis (Feature 10)
async function handleRealtimeAnalysis() {
    clearTimeout(realtimeTimeout);
    
    const text = newsInput.value.trim();
    if (text.length < 20) {
        liveWarning.classList.remove('show');
        return;
    }
    
    realtimeTimeout = setTimeout(async () => {
        try {
            const response = await fetch(REALTIME_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            
            const data = await response.json();
            if (data.warnings && data.warnings.length > 0) {
                const warning = data.warnings[0];
                liveWarningText.textContent = warning.message;
                liveWarning.classList.add('show');
            } else {
                liveWarning.classList.remove('show');
            }
        } catch (error) {
            // Silent fail for real-time
        }
    }, 500);
}

// Input Handling
function handleInputChange() {
    const text = newsInput.value.trim();
    const length = text.length;
    
    charCount.textContent = length;
    detectBtn.disabled = length < 10 || length > MAX_CHARS;
    
    if (length > MAX_CHARS) {
        newsInput.value = newsInput.value.substring(0, MAX_CHARS);
        charCount.textContent = MAX_CHARS;
    }
}

function updateCharCount() {
    charCount.textContent = newsInput.value.length;
}

// Main Detection
async function handleDetect() {
    setLoadingState(true);
    resultSection.classList.add('hidden');
    summaryCard.classList.add('hidden');
    
    try {
        let response;
        let data;
        let textContent;
        
        if (inputMode === 'url') {
            // URL mode
            const url = urlInput.value.trim();
            
            if (!isValidUrl(url)) {
                showToast('Please enter a valid URL');
                setLoadingState(false);
                return;
            }
            
            btnText.textContent = 'Fetching & Analyzing...';
            
            response = await fetch(URL_API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: url })
            });
            
            data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch or analyze URL');
            }
            
            // Display URL source info
            if (data.source) {
                displayUrlSource(data.source);
            }
            
            textContent = data.source?.title || 'Article content';
        } else {
            // Text mode
            const text = newsInput.value.trim();
            
            if (text.length < 10) {
                showToast('Please enter at least 10 characters');
                setLoadingState(false);
                return;
            }
            
            response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });
            
            data = await response.json();
            textContent = text;
        }
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to get prediction');
        }
        
        displayAllResults(data, textContent);
        
        setTimeout(() => {
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 100);
        
    } catch (error) {
        showToast(error.message || 'Failed to connect to server');
    } finally {
        setLoadingState(false);
    }
}

// Display URL source information
function displayUrlSource(source) {
    // Create or update URL source card
    let urlSourceCard = document.getElementById('urlSourceCard');
    if (!urlSourceCard) {
        urlSourceCard = document.createElement('div');
        urlSourceCard.id = 'urlSourceCard';
        urlSourceCard.className = 'bg-blue-50 dark:bg-blue-900/20 rounded-xl p-4 mb-6 border-l-4 border-blue-500';
        resultSection.insertBefore(urlSourceCard, resultSection.firstChild);
    }
    
    const platformIcon = source.is_social_media ? '📱' : '🔗';
    const platformBadge = source.is_social_media ? `
        <div class="mt-2 inline-block px-3 py-1 bg-orange-100 dark:bg-orange-900/30 rounded-full">
            <span class="text-sm font-semibold text-orange-800 dark:text-orange-200">
                📱 ${source.platform} - Social Media
            </span>
        </div>
    ` : '';
    
    urlSourceCard.innerHTML = `
        <div class="flex items-start gap-3">
            <span class="text-2xl">${platformIcon}</span>
            <div class="flex-1">
                <div class="font-semibold text-blue-900 dark:text-blue-100 mb-1">Source URL</div>
                <a href="${source.url}" target="_blank" class="text-sm text-blue-700 dark:text-blue-300 hover:underline break-all">
                    ${source.url}
                </a>
                ${platformBadge}
                ${source.title ? `
                    <div class="font-semibold text-blue-900 dark:text-blue-100 mt-2 mb-1">Article Title</div>
                    <div class="text-sm text-blue-800 dark:text-blue-200">${source.title}</div>
                ` : ''}
                <div class="text-xs text-blue-600 dark:text-blue-400 mt-2">
                    Content extracted: ${source.content_length} characters
                </div>
            </div>
        </div>
    `;
    urlSourceCard.classList.remove('hidden');
}

// Display All Results
function displayAllResults(data, originalText) {
    // 0. Language Detection
    if (data.language && data.language.detected) {
        displayLanguage(data.language);
    }
    
    // Social Media Warning (if applicable)
    if (data.social_media) {
        displaySocialMediaWarning(data.social_media);
    }
    
    // 1. Trust Meter (Feature 1)
    updateTrustMeter(data.trust_level, data.confidence);
    
    // AI Reasoning Module (NEW!)
    if (data.ai_reasoning) {
        displayAIReasoning(data.ai_reasoning);
    }
    
    // 2. Word Highlighting (Feature 2)
    highlightWords(originalText, data.highlighted_words);
    
    // 3. Emotion Detector (Feature 3)
    displayEmotions(data.emotions);
    
    // 4. AI Summary (Feature 4)
    if (data.summary && data.summary !== originalText) {
        summaryText.textContent = data.summary;
        summaryCard.classList.remove('hidden');
    }
    
    // 5. Real-time Confidence (Feature 5)
    animateConfidence(data.confidence);
    
    // 6. Fact-Check (Feature 6)
    displayFactChecks(data.claims);
    
    // 8. Pattern Score (Feature 8)
    displayPatterns(data.patterns);
    
    resultSection.classList.remove('hidden');
}

// AI Reasoning Display
function displayAIReasoning(reasoning) {
    // Display summary
    reasoningSummaryText.textContent = reasoning.summary;
    
    // Display detailed reasons
    reasoningDetails.innerHTML = '';
    
    if (reasoning.reasons && reasoning.reasons.length > 0) {
        reasoning.reasons.forEach((reason, index) => {
            const severityColor = reason.severity === 'high' ? 'border-red-500 bg-red-50 dark:bg-red-900/20' :
                                 reason.severity === 'medium' ? 'border-yellow-500 bg-yellow-50 dark:bg-yellow-900/20' :
                                 'border-green-500 bg-green-50 dark:bg-green-900/20';
            
            const reasonCard = document.createElement('div');
            reasonCard.className = `p-4 rounded-xl border-l-4 ${severityColor} mb-3 fade-in`;
            reasonCard.style.animationDelay = `${index * 0.1}s`;
            
            let evidenceHTML = `
                <div class="flex items-start gap-3">
                    <span class="text-2xl">${reason.icon || '📌'}</span>
                    <div class="flex-1">
                        <h4 class="font-bold text-gray-900 dark:text-gray-100 mb-2">${reason.title}</h4>
                        <p class="text-sm text-gray-700 dark:text-gray-300 mb-2">${reason.description}</p>
            `;
            
            // Add evidence if available
            if (reason.evidence && reason.evidence.length > 0) {
                evidenceHTML += `
                    <div class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-600">
                        <div class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Evidence:</div>
                        <div class="flex flex-wrap gap-2">
                `;
                reason.evidence.forEach(ev => {
                    evidenceHTML += `<span class="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded text-xs">${ev}</span>`;
                });
                evidenceHTML += `</div></div>`;
            }
            
            evidenceHTML += `</div></div>`;
            reasonCard.innerHTML = evidenceHTML;
            reasoningDetails.appendChild(reasonCard);
        });
    }
}

// Language Detection Display
function displayLanguage(languageInfo) {
    const langName = languageInfo.name;
    const langCode = languageInfo.code;
    
    let emoji = '🌐';
    if (langCode === 'ta') emoji = '🇮🇳';
    else if (langCode === 'en') emoji = '🇬🇧';
    else if (langCode === 'hi') emoji = '🇮🇳';
    
    languageText.textContent = `${emoji} ${langName} (${langCode.toUpperCase()})`;
    
    if (langCode === 'ta') {
        languageText.textContent += ' - Tamil language detected and analyzed!';
    }
    
    languageCard.classList.remove('hidden');
}

// Display Social Media Warning
function displaySocialMediaWarning(socialMedia) {
    // Create or update social media warning card
    let socialCard = document.getElementById('socialMediaCard');
    if (!socialCard) {
        socialCard = document.createElement('div');
        socialCard.id = 'socialMediaCard';
        socialCard.className = 'bg-orange-50 dark:bg-orange-900/20 rounded-xl p-5 mb-6 border-l-4 border-orange-500';
        // Insert after language card or at start of results
        const languageCard = document.getElementById('languageCard');
        if (languageCard && !languageCard.classList.contains('hidden')) {
            languageCard.parentNode.insertBefore(socialCard, languageCard.nextSibling);
        } else {
            resultSection.insertBefore(socialCard, resultSection.firstChild);
        }
    }
    
    socialCard.innerHTML = `
        <div class="flex items-start gap-3">
            <span class="text-3xl">📱</span>
            <div class="flex-1">
                <div class="font-bold text-orange-900 dark:text-orange-100 mb-2">
                    ${socialMedia.platform} Content Detected
                </div>
                <p class="text-sm text-orange-800 dark:text-orange-200 mb-3">
                    ${socialMedia.warning}
                </p>
                <div class="bg-orange-100 dark:bg-orange-900/30 rounded-lg p-3">
                    <div class="text-xs font-semibold text-orange-900 dark:text-orange-100 mb-2">Key Indicators:</div>
                    <ul class="text-xs text-orange-800 dark:text-orange-200 space-y-1">
                        ${socialMedia.indicators.map(ind => `<li>• ${ind}</li>`).join('')}
                    </ul>
                </div>
            </div>
        </div>
    `;
    socialCard.classList.remove('hidden');
}

// Feature 1: Trust Meter Speedometer
function updateTrustMeter(trustLevel, confidence) {
    const isFake = confidence >= 70;
    const trustScore = trustLevel.trust_score;
    
    // Calculate needle rotation (-90deg to 90deg for 0-100%)
    const rotation = -90 + (trustScore / 100) * 180;
    speedometerNeedle.style.transform = `translateX(-50%) rotate(${rotation}deg)`;
    
    trustLevel.innerHTML = `
        <span style="color: ${trustLevel.color}">${trustLevel.icon} ${trustLevel.level}</span>
        <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">Trust Score: ${trustScore.toFixed(1)}%</div>
    `;
}

// Feature 2: Word Highlighting
function highlightWords(text, highlightedWords) {
    const words = text.split(/\s+/);
    let html = '';
    
    words.forEach((word, index) => {
        const highlight = highlightedWords.find(h => h.index === index);
        if (highlight) {
            const className = highlight.type === 'suspicious' ? 'word-suspicious' : 
                            highlight.type === 'trusted' ? 'word-trusted' : 'word-neutral';
            html += `<span class="${className}">${word}</span> `;
        } else {
            html += `<span class="word-neutral">${word}</span> `;
        }
    });
    
    highlightedText.innerHTML = html;
}

// Feature 3: Emotion Detector
function displayEmotions(emotions) {
    const emotionData = [
        { name: 'Fear', emoji: '😨', value: emotions.fear, color: '#ef4444' },
        { name: 'Anger', emoji: '😡', value: emotions.anger, color: '#f97316' },
        { name: 'Urgency', emoji: '⏰', value: emotions.urgency, color: '#eab308' },
        { name: 'Sensational', emoji: '📢', value: emotions.sensational, color: '#ec4899' }
    ];
    
    emotionBars.innerHTML = emotionData.map(emotion => `
        <div>
            <div class="flex justify-between items-center mb-1">
                <span class="text-sm font-medium">${emotion.emoji} ${emotion.name}</span>
                <span class="text-sm font-bold">${emotion.value}%</span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                <div class="h-3 rounded-full transition-all duration-1000" 
                     style="width: ${emotion.value}%; background-color: ${emotion.color}"></div>
            </div>
        </div>
    `).join('');
}

// Feature 5: Count-Up Animation
function animateConfidence(confidence) {
    let current = 0;
    const increment = confidence / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= confidence) {
            current = confidence;
            clearInterval(timer);
        }
        confidenceCountUp.textContent = `${Math.round(current)}%`;
        confidenceBar.style.width = `${current}%`;
    }, 30);
}

// Feature 6: Fact-Check Assistant
function displayFactChecks(claims) {
    if (!claims || claims.length === 0) {
        factCheckClaims.innerHTML = '<p class="text-gray-600 dark:text-gray-400">No specific claims detected.</p>';
        return;
    }
    
    factCheckClaims.innerHTML = claims.map(claim => {
        const icon = claim.type === 'suspicious' ? '❌' : claim.type === 'verifiable' ? '✅' : '⚠️';
        const color = claim.type === 'suspicious' ? 'text-red-600' : 
                     claim.type === 'verifiable' ? 'text-green-600' : 'text-yellow-600';
        
        return `
            <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div class="flex items-start gap-3">
                    <span class="text-2xl">${icon}</span>
                    <div class="flex-1">
                        <div class="font-semibold mb-1">${claim.claim}</div>
                        <div class="text-sm ${color}">Status: ${claim.status}</div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Feature 8: Pattern Score Checklist
function displayPatterns(patterns) {
    const patternList = [
        { key: 'clickbait_language', label: 'Clickbait language', icon: '📰' },
        { key: 'anonymous_source', label: 'Anonymous source', icon: '👤' },
        { key: 'exaggerated_claim', label: 'Exaggerated claim', icon: '📈' },
        { key: 'no_evidence', label: 'No evidence', icon: '📋' },
        { key: 'emotional_manipulation', label: 'Emotional manipulation', icon: '🎭' },
        { key: 'urgency_pressure', label: 'Urgency pressure', icon: '⏱️' }
    ];
    
    patternChecklist.innerHTML = patternList.map(pattern => {
        const detected = patterns[pattern.key];
        const icon = detected ? '✅' : '⚪';
        const color = detected ? 'text-red-600' : 'text-gray-400';
        
        return `
            <div class="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <span class="text-xl">${icon}</span>
                <span class="flex-1 ${color}">${pattern.icon} ${pattern.label}</span>
            </div>
        `;
    }).join('');
}

// Utility Functions
function setLoadingState(isLoading) {
    if (isLoading) {
        detectBtn.disabled = true;
        loadingSpinner.classList.remove('hidden');
        btnText.textContent = 'Analyzing...';
    } else {
        detectBtn.disabled = newsInput.value.trim().length < 10;
        loadingSpinner.classList.add('hidden');
        btnText.textContent = 'Detect Fake News';
    }
}

function handleClear() {
    if (inputMode === 'text') {
        newsInput.value = '';
        newsInput.focus();
        handleInputChange();
    } else {
        urlInput.value = '';
        urlInput.focus();
        handleUrlInputChange();
    }
    resultSection.classList.add('hidden');
    summaryCard.classList.add('hidden');
    liveWarning.classList.remove('show');
    
    // Remove URL source card if exists
    const urlSourceCard = document.getElementById('urlSourceCard');
    if (urlSourceCard) {
        urlSourceCard.remove();
    }
    
    // Remove social media card if exists
    const socialCard = document.getElementById('socialMediaCard');
    if (socialCard) {
        socialCard.remove();
    }
}

function handleAnalyzeAnother() {
    handleClear();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function toggleTheme() {
    const isDark = document.documentElement.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

function showToast(message, type = 'error') {
    toastMessage.textContent = message;
    const toastContent = toast.querySelector('div');
    toastContent.className = type === 'error' ? 
        'bg-red-500 text-white px-6 py-4 rounded-lg shadow-xl flex items-center gap-3' :
        'bg-green-500 text-white px-6 py-4 rounded-lg shadow-xl flex items-center gap-3';
    
    toast.classList.remove('translate-x-96');
    toast.classList.add('-translate-x-0');
    
    setTimeout(() => {
        toast.classList.add('translate-x-96');
        toast.classList.remove('-translate-x-0');
    }, 3000);
}
