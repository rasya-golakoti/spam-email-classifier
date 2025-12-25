// DOM Elements
const emailInput = document.getElementById('emailInput');
const charCount = document.getElementById('charCount');
const wordCount = document.getElementById('wordCount');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const formatBtn = document.getElementById('formatBtn');
const sampleBtns = document.querySelectorAll('.sample-btn');
const statusText = document.getElementById('statusText');
const statusDot = document.getElementById('statusDot');
const predictionContent = document.getElementById('predictionResult');
const predictionTitle = document.getElementById('predictionTitle');
const predictionSubtitle = document.getElementById('predictionSubtitle');
const confidenceValue = document.getElementById('confidenceValue');
const confidenceBadge = document.getElementById('confidenceBadge');
const hamPercent = document.getElementById('hamPercent');
const spamPercent = document.getElementById('spamPercent');
const hamBar = document.getElementById('hamBar');
const spamBar = document.getElementById('spamBar');
const urlCount = document.getElementById('urlCount');
const numberCount = document.getElementById('numberCount');
const suspiciousCount = document.getElementById('suspiciousCount');
const analysisTime = document.getElementById('analysisTime');
const toast = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');
const toastIcon = document.getElementById('toastIcon');
const toastClose = document.getElementById('toastClose');
const analyzeLoader = document.getElementById('analyzeLoader');
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingText = document.getElementById('loadingText');
const exportResultsBtn = document.getElementById('exportResults');
const refreshModelBtn = document.getElementById('refreshModel');
const resultsSection = document.getElementById('resultsSection');
const resultsHighlight = document.getElementById('resultsHighlight');
const featureURLs = document.getElementById('featureURLs');
const featureNumbers = document.getElementById('featureNumbers');
const featureSuspicious = document.getElementById('featureSuspicious');

// Sample Emails
const sampleEmails = {
    ham: `From: Sarah Johnson <sarah.johnson@company.com>
To: Team Members <team@company.com>
Subject: Weekly Meeting Agenda

Hi Team,

Our weekly meeting is scheduled for tomorrow at 2 PM in Conference Room B.

Agenda:
1. Project updates
2. Timeline review
3. Next steps

Please bring your status reports.

Looking forward to our discussion.

Best regards,

Sarah Johnson
Project Manager
Acme Corporation
Phone: (555) 123-4567
Email: sarah.johnson@acme.com
Website: https://www.acme.com`,

    spam: `From: "Prize Team" <noreply@prize-winner.com>
To: undisclosed-recipients
Subject: 🎉 CONGRATULATIONS! You've WON $10,000 CASH PRIZE! 🎉

Dear Winner,

YOU HAVE BEEN SELECTED AS OUR GRAND PRIZE WINNER!

💵 PRIZE: $10,000 CASH + Brand New iPhone 15 Pro Max!
🎁 BONUS: Free 1-Year Amazon Prime Subscription!

HURRY! This offer expires in 24 HOURS!

👉 CLAIM NOW: http://bit.ly/win-cash-now

ACT IMMEDIATELY to claim your prize!
Only the first 100 winners will be eligible.

To receive your prize, simply:
1. Click the link above NOW
2. Complete our 2-minute survey
3. Pay ONLY $2.99 shipping fee
4. Receive your prize in 3-5 days!

DON'T MISS THIS ONCE-IN-A-LIFETIME OPPORTUNITY!
This could change your life forever!

⚠️ OFFER EXPIRES SOON!
⏰ Time remaining: 23:59:59

CLICK HERE: http://bit.ly/win-cash-now

* Terms & conditions apply
* Must be 18+ years old
* Limited to first 100 responders
* $2.99 shipping fee applies`,

    phishing: `From: "Security Alert - PayPal" <security@paypal-security.com>
To: account-holder@email.com
Subject: 🔒 URGENT: Account Suspension Notice - Action Required

SECURITY ALERT - IMMEDIATE ATTENTION REQUIRED

Dear PayPal User,

We have detected unusual login activity on your PayPal account from an unrecognized device in a different location.

🚨 SECURITY THREAT DETECTED:
• Login attempt from: Singapore (IP: 203.0.113.25)
• Device: Unknown Windows PC
• Time: Today, 11:30 AM PST

Your account has been temporarily LIMITED to protect your security.

REQUIRED ACTION:
You MUST verify your identity within the next 12 HOURS to prevent permanent account suspension and potential financial loss.

👉 VERIFY YOUR ACCOUNT NOW: http://paypal-secure-verify.com/confirm-identity

VERIFICATION PROCESS:
1. Click the link above
2. Enter your PayPal login credentials
3. Confirm your personal information
4. Update your security questions
5. Review recent transactions

FAILURE TO VERIFY WILL RESULT IN:
• Permanent account suspension
• Loss of access to funds
• Inability to send or receive payments
• Account closure within 24 hours

CLICK TO VERIFY: http://paypal-secure-verify.com/confirm-identity

Note: This is a legitimate security measure from PayPal.

PayPal Security Team
1-888-221-1161
24/7 Customer Support`
};

// Suspicious words for feature detection
const suspiciousWords = [
    'win', 'won', 'winner', 'prize', 'reward', 'award', 'gift', 'free',
    'congratulations', 'congrats', 'urgent', 'immediate', 'alert', 'warning',
    'limited', 'offer', 'deal', 'discount', 'sale', 'bonus', 'cash', 'money',
    'million', 'thousand', 'hundred', 'dollar', '£', '$', '€', 'click', 'link',
    'http', 'www', 'subscribe', 'unsubscribe', 'guaranteed', 'risk-free',
    'act now', 'don\'t miss', 'last chance', 'expire', 'expires', 'expiring',
    'claim', 'verify', 'confirm', 'validate', 'update', 'suspend', 'suspended',
    'compromise', 'compromised', 'hack', 'hacked', 'security', 'secure',
    'password', 'login', 'credentials', 'account', 'bank', 'credit', 'card'
];

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('Spam Detector Initialized');
    
    // Set up event listeners
    if (emailInput) {
        emailInput.addEventListener('input', updateCounters);
        emailInput.addEventListener('input', analyzeTextFeatures);
    }
    
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            if (emailInput) {
                emailInput.value = '';
                updateCounters();
                analyzeTextFeatures();
                resetResults();
                showToast('Email content cleared', 'info');
            }
        });
    }
    
    if (formatBtn) {
        formatBtn.addEventListener('click', function() {
            if (emailInput && emailInput.value.trim()) {
                const formatted = emailInput.value
                    .split('\n')
                    .map(line => line.trim())
                    .filter(line => line.length > 0)
                    .join('\n\n');
                emailInput.value = formatted;
                updateCounters();
                showToast('Email formatted', 'success');
            }
        });
    }
    
    // Sample buttons
    sampleBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const type = this.dataset.type;
            
            if (sampleEmails[type] && emailInput) {
                emailInput.value = sampleEmails[type];
                updateCounters();
                analyzeTextFeatures();
                
                // Add visual feedback
                this.classList.add('active');
                setTimeout(() => {
                    this.classList.remove('active');
                }, 300);
                
                showToast(`${type.charAt(0).toUpperCase() + type.slice(1)} email loaded`, 'success');
            }
        });
    });
    
    // Analyze button
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', analyzeEmail);
    }
    
    // Export results
    if (exportResultsBtn) {
        exportResultsBtn.addEventListener('click', exportResults);
    }
    
    // Refresh model
    if (refreshModelBtn) {
        refreshModelBtn.addEventListener('click', function() {
            showToast('Refreshing model...', 'info');
            setTimeout(() => showToast('Model ready', 'success'), 1000);
        });
    }
    
    // Toast close
    if (toastClose) {
        toastClose.addEventListener('click', hideToast);
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to analyze
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (analyzeBtn && !analyzeBtn.disabled) {
                analyzeEmail();
            }
        }
        
        // Ctrl/Cmd + L to clear
        if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
            e.preventDefault();
            if (clearBtn) clearBtn.click();
        }
        
        // Ctrl/Cmd + F to format
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            if (formatBtn) formatBtn.click();
        }
        
        // Escape to reset
        if (e.key === 'Escape') {
            resetResults();
        }
        
        // Number keys for sample emails (1, 2, 3)
        if (e.key >= '1' && e.key <= '3' && e.ctrlKey) {
            e.preventDefault();
            const index = parseInt(e.key) - 1;
            const sampleBtn = sampleBtns[index];
            if (sampleBtn) sampleBtn.click();
        }
    });
    
    // Initialize UI
    updateCounters();
    analyzeTextFeatures();
    setStatus('ready', 'Ready to analyze');
    
    // Auto-hide toast
    setInterval(() => {
        if (toast && toast.classList.contains('show')) {
            hideToast();
        }
    }, 5000);
    
    console.log('UI Ready');
});

// Update character and word count
function updateCounters() {
    if (!emailInput || !charCount || !wordCount) return;
    
    const text = emailInput.value;
    const chars = text.length;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    
    charCount.textContent = chars;
    wordCount.textContent = words;
    
    if (analyzeBtn) {
        analyzeBtn.disabled = chars < 20;
    }
}

// Analyze text features
function analyzeTextFeatures() {
    if (!emailInput || !urlCount || !numberCount || !suspiciousCount) return;
    
    const text = emailInput.value.toLowerCase();
    
    // Count URLs
    const urls = (text.match(/https?:\/\/[^\s]+/g) || []).length;
    if (urlCount) urlCount.textContent = urls;
    
    // Count numbers
    const numbers = (text.match(/\d+/g) || []).length;
    if (numberCount) numberCount.textContent = numbers;
    
    // Count suspicious words
    let suspicious = 0;
    suspiciousWords.forEach(word => {
        const regex = new RegExp(`\\b${word}\\b`, 'i');
        if (regex.test(text)) {
            suspicious++;
        }
    });
    if (suspiciousCount) suspiciousCount.textContent = suspicious;
}

// Set status
function setStatus(type, message) {
    if (statusDot) statusDot.className = 'status-dot ' + type;
    if (statusText) statusText.textContent = message;
}

// Show toast notification
function showToast(message, type = 'success') {
    if (!toast || !toastMessage || !toastIcon) return;
    
    toastMessage.textContent = message;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    toastIcon.className = `fas ${icons[type] || icons.success}`;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(hideToast, 4000);
}

function hideToast() {
    if (toast) toast.classList.remove('show');
}

// Show loading overlay
function showLoading(text = 'Analyzing email...') {
    if (loadingText) loadingText.textContent = text;
    if (loadingOverlay) loadingOverlay.classList.add('active');
}

function hideLoading() {
    if (loadingOverlay) loadingOverlay.classList.remove('active');
}

// Highlight results section
function highlightResults() {
    // Show highlight indicator
    if (resultsHighlight) {
        resultsHighlight.style.display = 'block';
        setTimeout(() => {
            if (resultsHighlight) resultsHighlight.style.display = 'none';
        }, 3000);
    }
    
    // Highlight results section
    if (resultsSection) {
        resultsSection.classList.add('highlighted');
        
        setTimeout(() => {
            resultsSection.classList.remove('highlighted');
        }, 2000);
    }
    
    // Highlight confidence badge
    if (confidenceBadge) {
        confidenceBadge.classList.add('highlighted');
        
        setTimeout(() => {
            confidenceBadge.classList.remove('highlighted');
        }, 1000);
    }
    
    // Highlight probability bars with animation
    if (hamBar && spamBar) {
        setTimeout(() => {
            if (hamBar) hamBar.classList.add('highlighted');
            if (spamBar) spamBar.classList.add('highlighted');
            
            setTimeout(() => {
                if (hamBar) hamBar.classList.remove('highlighted');
                if (spamBar) spamBar.classList.remove('highlighted');
            }, 1000);
        }, 300);
    }
    
    // Highlight features one by one
    const features = [featureURLs, featureNumbers, featureSuspicious];
    features.forEach((feature, index) => {
        if (feature) {
            setTimeout(() => {
                feature.classList.add('highlighted');
                
                setTimeout(() => {
                    feature.classList.remove('highlighted');
                }, 800);
            }, index * 200);
        }
    });
}

// Analyze email
async function analyzeEmail() {
    if (!emailInput || emailInput.value.length < 20) {
        showToast('Please enter at least 20 characters', 'warning');
        return;
    }
    
    const startTime = Date.now();
    
    // Update UI state
    setStatus('processing', 'Analyzing...');
    if (analyzeBtn) analyzeBtn.disabled = true;
    if (analyzeLoader) analyzeLoader.style.display = 'block';
    showLoading('Processing email with AI model');
    
    try {
        // Send to backend
        const formData = new FormData();
        formData.append('email', emailInput.value);
        
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        // Calculate analysis time
        const endTime = Date.now();
        const duration = ((endTime - startTime) / 1000).toFixed(2);
        if (analysisTime) analysisTime.textContent = duration;
        
        // Update results
        updateResults(data);
        highlightResults();
        setStatus('success', 'Analysis complete');
        
        hideLoading();
        showToast(`Analysis complete in ${duration}s`, 'success');
        
    } catch (error) {
        console.error('Analysis error:', error);
        
        hideLoading();
        setStatus('error', 'Analysis failed');
        showToast('Could not connect to server. Using demo mode.', 'error');
        
        // Use mock data for demo
        const mockData = generateMockData(emailInput.value);
        updateResults(mockData);
        highlightResults();
        setStatus('success', 'Demo analysis');
        showToast('Using demo analysis', 'warning');
        
    } finally {
        if (analyzeBtn) analyzeBtn.disabled = false;
        if (analyzeLoader) analyzeLoader.style.display = 'none';
    }
}

// Update results display
function updateResults(data) {
    // Update prediction
    if (predictionContent) {
        predictionContent.className = 'prediction-content ' + (data.is_spam ? 'spam' : 'ham');
        
        const icon = predictionContent.querySelector('.prediction-icon i');
        if (icon) {
            icon.className = data.is_spam ? 'fas fa-exclamation-triangle fa-2x' : 'fas fa-check-circle fa-2x';
        }
    }
    
    if (predictionTitle) {
        predictionTitle.textContent = data.is_spam ? 'SPAM DETECTED' : 'LEGITIMATE EMAIL';
    }
    
    if (predictionSubtitle) {
        predictionSubtitle.textContent = data.is_spam ? 'High probability of spam content' : 'Email appears to be safe and legitimate';
    }
    
    // Update confidence
    const confidence = data.confidence || (data.is_spam ? 88 : 92);
    if (confidenceValue) {
        confidenceValue.textContent = `${confidence}%`;
    }
    
    // Update probabilities
    const hamProb = data.ham_probability || (data.is_spam ? 12 : 88);
    const spamProb = data.spam_probability || (data.is_spam ? 88 : 12);
    
    if (hamPercent) hamPercent.textContent = `${hamProb}%`;
    if (spamPercent) spamPercent.textContent = `${spamProb}%`;
    
    // Animate bars
    setTimeout(() => {
        if (hamBar) hamBar.style.width = `${hamProb}%`;
        if (spamBar) spamBar.style.width = `${spamProb}%`;
    }, 100);
    
    // Smooth scroll to results
    if (resultsSection) {
        resultsSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start'
        });
    }
}

// Generate mock data for demo
function generateMockData(text) {
    const lowercase = text.toLowerCase();
    let spamScore = 0;
    
    // Analyze text for spam indicators
    if (lowercase.includes('win') || lowercase.includes('won') || lowercase.includes('prize')) spamScore += 35;
    if (lowercase.includes('free') || lowercase.includes('gift') || lowercase.includes('card')) spamScore += 30;
    if (lowercase.includes('http') || lowercase.includes('click') || lowercase.includes('link')) spamScore += 25;
    if (lowercase.includes('urgent') || lowercase.includes('immediate') || lowercase.includes('alert')) spamScore += 20;
    if (lowercase.includes('limited') || lowercase.includes('offer') || lowercase.includes('expire')) spamScore += 15;
    if (lowercase.includes('congratulation') || lowercase.includes('winner')) spamScore += 10;
    if (lowercase.includes('$') || lowercase.includes('dollar') || lowercase.includes('money')) spamScore += 10;
    
    // Legitimate indicators reduce score
    if (lowercase.includes('meeting') || lowercase.includes('agenda') || lowercase.includes('schedule')) spamScore -= 25;
    if (lowercase.includes('regards') || lowercase.includes('sincerely') || lowercase.includes('best')) spamScore -= 20;
    if (lowercase.includes('project') || lowercase.includes('team') || lowercase.includes('report')) spamScore -= 15;
    if (lowercase.includes('attachment') || lowercase.includes('attached') || lowercase.includes('document')) spamScore -= 10;
    
    // Normalize score
    spamScore = Math.max(5, Math.min(95, spamScore));
    const hamProb = 100 - spamScore;
    
    // Add some randomness
    const confidence = Math.floor(Math.random() * 15) + 80;
    
    return {
        is_spam: spamScore > 60,
        ham_probability: Math.round(hamProb),
        spam_probability: Math.round(spamScore),
        confidence: confidence
    };
}

// Reset results
function resetResults() {
    if (predictionContent) {
        predictionContent.className = 'prediction-content';
        const icon = predictionContent.querySelector('.prediction-icon i');
        if (icon) icon.className = 'fas fa-question-circle fa-2x';
    }
    
    if (predictionTitle) predictionTitle.textContent = 'Waiting for Analysis';
    if (predictionSubtitle) predictionSubtitle.textContent = 'Enter email text and click Analyze';
    if (confidenceValue) confidenceValue.textContent = '--%';
    if (hamPercent) hamPercent.textContent = '0%';
    if (spamPercent) spamPercent.textContent = '0%';
    if (hamBar) hamBar.style.width = '0%';
    if (spamBar) spamBar.style.width = '0%';
    if (analysisTime) analysisTime.textContent = '0.00';
    
    setStatus('ready', 'Ready to analyze');
}

// Export results
function exportResults() {
    const results = {
        email: emailInput ? emailInput.value.substring(0, 200) + (emailInput.value.length > 200 ? '...' : '') : '',
        prediction: predictionTitle ? predictionTitle.textContent : 'No analysis',
        confidence: confidenceValue ? confidenceValue.textContent : '--%',
        hamProbability: hamPercent ? hamPercent.textContent : '0%',
        spamProbability: spamPercent ? spamPercent.textContent : '0%',
        analysisTime: analysisTime ? analysisTime.textContent : '0.00',
        features: {
            urls: urlCount ? urlCount.textContent : '0',
            numbers: numberCount ? numberCount.textContent : '0',
            suspiciousWords: suspiciousCount ? suspiciousCount.textContent : '0'
        },
        timestamp: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `spam-analysis-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('Results exported successfully', 'success');
}