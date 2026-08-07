/**
 * Enhanced features for SmartGov Health App
 * - Eligibility checker with localStorage namespace
 * - Document checklist with persistence
 * - WhatsApp + SMS sharing with CSRF headers
 * - Full page Telugu voice reading
 * - Issue reporting
 * - Privacy warnings
 * - Offline support with browser TTS fallback
 * - Event delegation for security hardening (no inline JS)
 */

// ==================== HTML Utilities ====================
window.escapeHtml = function(value) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    };
    return String(value || '').replace(/[&<>"']/g, char => map[char]);
};

// CSRF Header Helper
function getCsrfHeader() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? { 'X-CSRFToken': meta.getAttribute('content') } : {};
}

// ==================== Voice/Speech Features ====================

/**
 * Speak page aloud using Web Speech API with Telugu language support
 * Falls back to browser TTS if Web Speech not available
 */
function speakPageAloud() {
    if (!window.currentSchemeName) {
        alert('దయచేసి ముందుగా పథకం ఎంచుకోండి.');
        return;
    }

    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        speechSynthesis.cancel();

        // Collect all Telugu text from the page
        const schemeTitle = document.querySelector('.result-head h2')?.textContent || window.currentSchemeName;
        const infoCards = Array.from(document.querySelectorAll('.info-card')).map(card => {
            const title = card.querySelector('h3')?.textContent || '';
            const text = card.querySelector('p')?.textContent || '';
            return `${title}. ${text}`;
        }).join('. ');

        const fullText = `${schemeTitle}. ${infoCards}`;

        const utterance = new SpeechSynthesisUtterance(fullText);
        utterance.lang = 'te-IN';
        utterance.rate = 0.8; // Slower for rural users
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        utterance.onstart = () => {
            console.log('🔊 పేజీ చదువుతున్నాం...');
        };

        utterance.onerror = (event) => {
            console.error('Speech error:', event.error);
            showBrowserTTSFallback(schemeTitle, infoCards);
        };

        utterance.onend = () => {
            console.log('✅ చదవడం పూర్తయింది');
        };

        speechSynthesis.speak(utterance);
    } else {
        showBrowserTTSFallback(window.currentSchemeName, '');
    }
}

/**
 * Show fallback TTS button if Web Speech API fails
 */
function showBrowserTTSFallback(title, text) {
    const feedbackStatus = document.getElementById('feedbackStatus');
    if (feedbackStatus) {
        feedbackStatus.textContent = '⚠️ ఆడియో సమర్థన లేదు. అందుబాటులో ఉన్న ఆడియో ఫైలు వాయించండి.';
        feedbackStatus.style.color = 'var(--red)';
    }
}

/**
 * Legacy function for speaking text
 */
function speakText(text) {
    if ('speechSynthesis' in window) {
        speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'te-IN';
        utterance.rate = 0.8;
        speechSynthesis.speak(utterance);
    }
}

// ==================== Eligibility Checker ====================

function buildEligibilityChecker(scheme) {
    const questions = scheme.eligibility_questions || [];
    if (!questions.length) return '';

    let html = '<div class="eligibility-checker"><strong>🎯 అర్హత పరీక్ష</strong>';
    questions.forEach((q, idx) => {
        // Namespaced keys with fallback compatibility for existing users
        const saved = localStorage.getItem(`eligibility_${window.currentSchemeName}_q${idx}`) || 
                      localStorage.getItem(`eligibility_q${idx}`) || '';
        const yesClass = saved === 'yes' ? 'yes' : '';
        const noClass = saved === 'no' ? 'no' : '';
        
        html += `
            <div class="question-item">
                <p>${window.escapeHtml(q.question_te || q.question || '')}</p>
                <div class="yes-no-buttons">
                    <button class="yes-no-btn ${yesClass}" type="button" data-idx="${idx}" data-answer="yes">✓ అవును</button>
                    <button class="yes-no-btn ${noClass}" type="button" data-idx="${idx}" data-answer="no">✗ కాదు</button>
                </div>
            </div>
        `;
    });
    html += '</div>';
    return html;
}

function recordEligibilityAnswer(questionIdx, answer, event) {
    const target = event ? event.target : null;
    if (!target) return;
    const parentDiv = target.closest('.question-item');
    if (!parentDiv) return;
    
    const buttons = parentDiv.querySelectorAll('.yes-no-btn');
    buttons.forEach(btn => btn.classList.remove('yes', 'no'));
    target.classList.add(answer);
    
    // Save to namespaced key
    if (window.currentSchemeName) {
        localStorage.setItem(`eligibility_${window.currentSchemeName}_q${questionIdx}`, answer);
    } else {
        localStorage.setItem(`eligibility_q${questionIdx}`, answer);
    }
    
    // Provide haptic feedback if available
    if (navigator.vibrate) {
        navigator.vibrate(50);
    }
}

// ==================== Document Checklist ====================

function buildDocumentChecklist(scheme) {
    const docs = scheme.required_documents || [];
    if (!docs.length) return '';

    let html = '<div class="document-checklist"><strong>📋 డాక్యుమెంట్ చెక్‌లిస్ట్</strong>';
    docs.forEach((doc, idx) => {
        const optional = doc.optional ? ' (ఐచ్ఛికం)' : ' (తప్పనిసరి)';
        const docName = doc.name_te || doc.name || '';
        const schemeName = window.currentSchemeName || '';
        const saved = localStorage.getItem(`doc_check_${schemeName}_${idx}`) === 'true';
        const checkedAttr = saved ? 'checked' : '';
        
        html += `
            <div class="checklist-item">
                <input type="checkbox" id="doc_${idx}" ${checkedAttr} class="doc-check-box" data-idx="${idx}" data-scheme="${window.escapeHtml(schemeName)}">
                <label for="doc_${idx}">${window.escapeHtml(docName)}${optional}</label>
            </div>
        `;
    });
    html += '</div>';
    return html;
}

function saveDocumentCheck(schemeName, docIdx) {
    const checkbox = document.querySelector(`.checklist-item input[type="checkbox"][data-idx="${docIdx}"]`);
    if (!checkbox) return;
    
    const key = `doc_check_${schemeName}_${docIdx}`;
    localStorage.setItem(key, checkbox.checked);
    
    // Provide haptic feedback
    if (navigator.vibrate) {
        navigator.vibrate([50, 30]);
    }
}

function printDocumentChecklist(schemeName) {
    const checklist = document.querySelector('.document-checklist');
    if (!checklist) {
        alert('డాక్యుమెంట్ చెక్‌లిస్ట్ ఉండదు');
        return;
    }
    
    const printWindow = window.open('', '', 'width=600,height=800');
    if (!printWindow) {
        alert('పాప్‌అప్ బ్లాక్ చేయబడింది. దయచేసి పాప్‌అప్‌లను అనుమతించండి.');
        return;
    }
    
    printWindow.document.write(`
        <!DOCTYPE html>
        <html lang="te">
        <head>
            <meta charset="UTF-8">
            <title>${window.escapeHtml(schemeName)} - చెక్‌లిస్ట్</title>
            <style>
                body { font-family: "Noto Sans Telugu", Arial; margin: 20px; }
                h1 { color: #176b5b; }
                h2 { color: #0d4b40; }
                .checklist-item { margin: 10px 0; }
            </style>
        </head>
        <body>
            <h1>${window.escapeHtml(schemeName)}</h1>
            <h2>📋 అవసరమైన డాక్యుమెంట్‌లు</h2>
            ${checklist.innerHTML}
            <p style="margin-top: 40px; color: #999; font-size: 12px;">
                మరిన్ని సమాచారం కోసం: SmartGov Health App
            </p>
        </body>
        </html>
    `);
    printWindow.document.close();
    
    // Delay print to ensure content loads
    setTimeout(() => {
        printWindow.print();
    }, 250);
}

// ==================== Trust & Transparency ====================

function buildTrustInfo(scheme) {
    const lastUpdated = scheme.last_updated || 'తెలియదు';
    const confirmationSource = scheme.eligibility_confirmation || 'Government office';
    const officialWebsite = scheme.official_website || '#';
    
    return `
        <div class="trust-info">
            <strong>🔒 విశ్వాస సమాచారం</strong><br>
            📅 చివరిగా నవీకరించిన: ${window.escapeHtml(lastUpdated)}<br>
            ✔️ సరిచేస్తారు: ${window.escapeHtml(confirmationSource)}<br>
            🌐 అధికారిక సంచిక: <a class="source-link" href="${window.escapeHtml(officialWebsite)}" target="_blank" rel="noopener noreferrer">సందర్శించండి</a>
        </div>
    `;
}

function buildPrivacyWarning() {
    return `
        <div class="privacy-warning">
            ⚠️ <strong>గోప్యతా హెచ్చరిక:</strong><br>
            ఆధార్, ప్రెస్క్రిప్షన్లు లేదా వ్యక్తిగత ఆరోగ్య ఫైలులను ఈ ఆ్యప్‌కు అప్‌లోడ్ చేయవద్దు.
            మీరు విశ్వసించే పరికరమైన తర్వాత మాత్రమే అప్‌లోడ్ చేయండి.
        </div>
    `;
}

// ==================== Sharing Features ====================

/**
 * Generate a canonical plain-text share message for a scheme
 */
function generateShareText(schemeName) {
    const scheme = window.schemesCatalog?.[schemeName] || {};
    
    // Scheme Name
    const teluguName = scheme.telugu_name;
    let text = '';
    if (teluguName && teluguName !== schemeName) {
        text += `${teluguName}\n\nపథకం: ${schemeName}\n\n`;
    } else {
        text += `పథకం: ${schemeName}\n\n`;
    }
    
    // Eligibility
    text += `అర్హత:\n`;
    const eligibility = scheme.telugu?.eligibility || scheme.simplified?.eligibility || 'వివరాలు చూడండి';
    text += `${eligibility}\n\n`;
    
    // Documents
    text += `పత్రాలు:\n`;
    if (scheme.telugu?.documents) {
        text += scheme.telugu.documents;
    } else if (scheme.required_documents && scheme.required_documents.length > 0) {
        text += scheme.required_documents.map(doc => doc.name_te || doc.name).join(', ');
    } else {
        text += 'వివరాలు లేవు';
    }
    
    // Contact
    text += `\n\nసంప్రదించండి:\n`;
    const contact = scheme.telugu?.contact_office || scheme.eligibility_confirmation || scheme.contact_office || 'Government office';
    text += contact;
    
    // URL
    if (scheme.official_website) {
        text += `\n\nమరిన్ని వివరాలు:\n${scheme.official_website}`;
    }
    
    return text;
}

/**
 * Share on WhatsApp with CSRF header protection
 */
async function shareOnWhatsApp(schemeName) {
    if (!navigator.onLine && !window.offlineMode) {
        alert('నెట్‌వర్క్ కనెక్షన్ లేదు. WhatsApp శేయర్ ఇంటర్నెట్ అవసరం.');
        return;
    }

    try {
        const text = generateShareText(schemeName);
        const encodedMessage = encodeURIComponent(text);
        
        // Log asynchronously without blocking
        fetch('/whatsapp-share', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                ...getCsrfHeader()
            },
            body: JSON.stringify({ scheme_name: schemeName })
        }).catch(() => {});
        
        window.open(`https://wa.me/?text=${encodedMessage}`, '_blank');
    } catch (error) {
        console.error('WhatsApp share error:', error);
        alert(`లోపం: ${error.message}`);
    }
}

/**
 * Share on SMS using sms: protocol
 */
async function shareOnSMS(schemeName) {
    try {
        const text = generateShareText(schemeName);
        const encodedMessage = encodeURIComponent(text);
        window.location.href = `sms:?body=${encodedMessage}`;
    } catch (error) {
        console.error('SMS share error:', error);
        alert(`లోపం: ${error.message}`);
    }
}

/**
 * Report an issue with the scheme information
 */
async function reportIssue(schemeName) {
    if (!schemeName && typeof window.currentSchemeName === 'undefined') {
        alert('దయచేసి పథకం ఎంచుకోండి.');
        return;
    }
    openFeedbackModal(document.activeElement);
}

/**
 * Open detailed report form
 */
function openReportForm() {
    openFeedbackModal(document.activeElement);
}

/**
 * Send report to server with CSRF header protection
 */
// ==================== Enhanced Feedback (Tier 2C) ====================

let currentRating = 0;
let previousFocusFeedback = null;

function openFeedbackModal(triggerBtn) {
    if (!window.currentRequestId && typeof window.currentSchemeName === 'undefined') {
        const statusEl = document.getElementById('feedbackStatus');
        if (statusEl) {
            statusEl.textContent = 'దయచేసి ముందుగా పథకం ఎంచుకోండి.';
            statusEl.className = 'feedback-status error';
        }
    }
    previousFocusFeedback = triggerBtn || document.activeElement;
    const modal = document.getElementById('feedbackOverlay');
    if (!modal) return;
    
    modal.classList.remove('hidden');
    modal.setAttribute('aria-hidden', 'false');
    
    // Reset state
    currentRating = 0;
    document.querySelectorAll('.star-rating button').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
    });
    document.querySelectorAll('.feedback-chips .chip').forEach(c => {
        c.classList.remove('selected');
        c.setAttribute('aria-pressed', 'false');
    });
    const commentBox = document.getElementById('feedbackComment');
    if (commentBox) commentBox.value = '';
    
    const status = document.getElementById('feedbackStatus');
    if (status) {
        status.textContent = '';
        status.className = 'feedback-status';
    }
    
    const title = document.getElementById('feedbackTitle');
    if (title) title.focus();
}

function closeFeedbackModal() {
    const modal = document.getElementById('feedbackOverlay');
    if (modal) {
        modal.classList.add('hidden');
        modal.setAttribute('aria-hidden', 'true');
    }
    if (previousFocusFeedback) {
        previousFocusFeedback.focus();
    }
}

function setRating(val) {
    currentRating = parseInt(val, 10);
    document.querySelectorAll('.star-rating button').forEach(b => {
        const bVal = parseInt(b.dataset.value, 10);
        const isActive = bVal <= currentRating;
        b.classList.toggle('active', isActive);
        b.setAttribute('aria-pressed', isActive ? 'true' : 'false');
    });
}

function setFeedbackChip(btn) {
    const isSelected = btn.classList.toggle('selected');
    btn.setAttribute('aria-pressed', isSelected ? 'true' : 'false');
}

async function submitFeedback() {
    const statusEl = document.getElementById('feedbackStatus');
    if (!statusEl) return;
    
    if (!window.currentRequestId && typeof window.currentSchemeName === 'undefined') {
        statusEl.textContent = 'దయచేసి ముందుగా పథకం ఎంచుకోండి.';
        statusEl.className = 'feedback-status error';
        return;
    }
    if (currentRating === 0) {
        statusEl.textContent = 'దయచేసి రేటింగ్ ఎంచుకోండి (Please select a rating).';
        statusEl.className = 'feedback-status error';
        return;
    }
    
    statusEl.textContent = 'పంపుతున్నాం (Submitting)...';
    statusEl.className = 'feedback-status';
    
    const selectedChips = Array.from(document.querySelectorAll('.feedback-chips .chip.selected')).map(c => c.dataset.value);
    const commentBox = document.getElementById('feedbackComment');
    const comment = commentBox ? commentBox.value.trim() : '';
    
    const combinedComment = [...selectedChips, comment].filter(Boolean).join(' | ');

    try {
        const payload = window.currentRequestId ? {
            request_id: window.currentRequestId,
            rating: currentRating,
            was_clear: combinedComment.includes('సమాచారం') ? 'yes' : 'N/A',
            got_benefit: 'unknown',
            village: 'Unknown',
            problem: combinedComment
        } : {
            scheme_name: window.currentSchemeName || 'Unknown',
            feedback_type: 'user_reported_issue',
            village: 'Self-reported',
            feedback_text: `Rating: ${currentRating}. Comments: ${combinedComment}`
        };

        const endpoint = window.currentRequestId ? '/enhanced-feedback' : '/staff-report';

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                ...(typeof getCsrfHeader === 'function' ? getCsrfHeader() : {})
            },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            statusEl.textContent = '✅ ధన్యవాదాలు! మీ అభిప్రాయం నమోదు చేయబడింది.';
            statusEl.className = 'feedback-status success';
            setTimeout(closeFeedbackModal, 2000);
        } else {
            throw new Error(data.error || 'Server error');
        }
    } catch (error) {
        statusEl.textContent = `❌ అభిప్రాయం పంపలేకపోయాము. దయచేసి మళ్లీ ప్రయత్నించండి.`;
        statusEl.className = 'feedback-status error';
        console.error('Feedback submission error:', error);
    }
}

// ==================== Offline Support ====================

/**
 * Cache all essential data for offline access
 */
async function cacheForOffline() {
    try {
        const response = await fetch('/offline-cache');
        const data = await response.json();
        localStorage.setItem('smartgov_offline_data', JSON.stringify(data));
        localStorage.setItem('smartgov_offline_timestamp', new Date().toISOString());
        console.log('✅ ऑफलाइन संचयन अद्यतन: ' + data.schemes + ' పథక');
    } catch (error) {
        console.warn('Offline caching failed:', error);
    }
}

/**
 * Load offline data when no internet connection
 */
function loadOfflineData() {
    const offlineData = localStorage.getItem('smartgov_offline_data');
    if (offlineData) {
        console.log('📱 ఆఫ్‌లైన్ సమాచారం ఉపయోగం చేస్తున్నాం');
        window.offlineMode = true;
        return JSON.parse(offlineData);
    }
    return null;
}

// ==================== Initialization ====================

document.addEventListener('DOMContentLoaded', () => {
    // Cache data for offline access
    cacheForOffline();
    
    // Check if offline
    if (!navigator.onLine) {
        loadOfflineData();
        console.log('📡 ఆఫ్‌లైన్ మోడ్ చేతనం');
    }
    
    // Listen for connection changes
    window.addEventListener('offline', () => {
        console.log('📡 ఇంటర్నెట్ కనెక్షన్ కోల్పోయారు');
        const indicator = document.getElementById('offlineIndicator');
        if (indicator) {
            indicator.style.display = 'block';
        }
    });
    
    window.addEventListener('online', () => {
        console.log('📡 ఇంటర్నెట్ కనెక్షన్ పునరుద్ధరించారు');
        const indicator = document.getElementById('offlineIndicator');
        if (indicator) {
            indicator.style.display = 'none';
        }
        // Re-cache when online
        cacheForOffline();
    });

    // Event delegation on resultArea to handle click events of dynamic elements securely
    const resultArea = document.getElementById('resultArea');
    if (resultArea) {
        resultArea.addEventListener('click', event => {
            const target = event.target;
            
            // Speak custom text (slowly)
            const speakTextBtn = target.closest('.speak-text-btn');
            if (speakTextBtn) {
                const text = speakTextBtn.dataset.text;
                speakText(text);
                return;
            }
            
            // Speak page aloud
            const speakPageBtn = target.closest('.speak-page-btn');
            if (speakPageBtn) {
                speakPageAloud();
                return;
            }
            
            // Share on WhatsApp
            const shareWhatsappBtn = target.closest('.share-whatsapp-btn');
            if (shareWhatsappBtn) {
                const schemeName = shareWhatsappBtn.dataset.scheme;
                shareOnWhatsApp(schemeName);
                return;
            }
            
            // Share on SMS
            const shareSmsBtn = target.closest('.share-sms-btn');
            if (shareSmsBtn) {
                const schemeName = shareSmsBtn.dataset.scheme;
                shareOnSMS(schemeName);
                return;
            }
            
            // Print Document Checklist
            const printChecklistBtn = target.closest('.print-checklist-btn');
            if (printChecklistBtn) {
                const schemeName = printChecklistBtn.dataset.scheme;
                printDocumentChecklist(schemeName);
                return;
            }
            
            // Report Issue (scheme details)
            const reportIssueBtn = target.closest('.report-issue-btn');
            if (reportIssueBtn) {
                const schemeName = reportIssueBtn.dataset.scheme;
                openFeedbackModal(reportIssueBtn);
                return;
            }
            
            // Open Detailed Feedback Form
            const openFeedbackBtn = target.closest('.open-feedback-btn');
            if (openFeedbackBtn) {
                openFeedbackModal(openFeedbackBtn);
                return;
            }
            
            // Yes/No Eligibility Buttons
            const yesNoBtn = target.closest('.yes-no-btn');
            if (yesNoBtn) {
                const idx = parseInt(yesNoBtn.dataset.idx, 10);
                const answer = yesNoBtn.dataset.answer;
                recordEligibilityAnswer(idx, answer, event);
                return;
            }
        });

        // Event delegation on resultArea for input change events (checkboxes)
        resultArea.addEventListener('change', event => {
            const target = event.target;
            // Document Checklist Checkboxes
            if (target.matches('.checklist-item input[type="checkbox"]')) {
                const idx = parseInt(target.dataset.idx, 10);
                const schemeName = target.dataset.scheme;
                saveDocumentCheck(schemeName, idx);
            }
        });
    }
});

// ==================== Export for global use ====================
window.SmartGovEnhanced = {
    buildEligibilityChecker,
    buildDocumentChecklist,
    buildTrustInfo,
    buildPrivacyWarning,
    recordEligibilityAnswer,
    saveDocumentCheck,
    printDocumentChecklist,
    shareOnWhatsApp,
    shareOnSMS,
    speakText,
    speakPageAloud,
    reportIssue,
    openReportForm,
    openFeedbackModal,
    closeFeedbackModal,
    cacheForOffline,
    loadOfflineData
};

// ==================== UX Enhancements (Tier 1) ====================

const SmartGovUX = (function() {
    // Keys
    const KEYS = {
        FONT_SIZE: 'app_font_size',
        THEME: 'app_theme',
        FAVORITES: 'app_favorites',
        RECENT: 'app_recently_viewed'
    };

    // Safe Storage Wrapper
    const Storage = {
        get: (key, def) => {
            try {
                const val = localStorage.getItem(key);
                return val ? JSON.parse(val) : def;
            } catch(e) {
                return def;
            }
        },
        set: (key, val) => {
            try {
                localStorage.setItem(key, JSON.stringify(val));
            } catch(e) {}
        }
    };

    // --- Font Size ---
    const fontSizes = ['font-small', 'font-default', 'font-large', 'font-extra-large'];
    let currentFontIndex = 1;

    function applyFontSize(index) {
        document.body.classList.remove(...fontSizes);
        if (index >= 0 && index < fontSizes.length) {
            document.body.classList.add(fontSizes[index]);
            currentFontIndex = index;
            Storage.set(KEYS.FONT_SIZE, index);
        }
    }

    function initFontSize() {
        let savedIndex = Storage.get(KEYS.FONT_SIZE, 1);
        if (savedIndex < 0 || savedIndex >= fontSizes.length) savedIndex = 1;
        applyFontSize(savedIndex);

        document.getElementById('fontDecBtn')?.addEventListener('click', () => {
            if (currentFontIndex > 0) applyFontSize(currentFontIndex - 1);
        });
        document.getElementById('fontIncBtn')?.addEventListener('click', () => {
            if (currentFontIndex < fontSizes.length - 1) applyFontSize(currentFontIndex + 1);
        });
        document.getElementById('fontResetBtn')?.addEventListener('click', () => {
            applyFontSize(1); // default
        });
    }

    // --- Theme ---
    const themes = ['light', 'dark-mode', 'high-contrast'];
    let currentThemeIndex = 0;

    function applyTheme(index) {
        document.body.classList.remove('dark-mode', 'high-contrast');
        if (index === 1) document.body.classList.add('dark-mode');
        else if (index === 2) document.body.classList.add('high-contrast');
        currentThemeIndex = index;
        Storage.set(KEYS.THEME, index);
    }

    function initTheme() {
        let savedIndex = Storage.get(KEYS.THEME, 0);
        if (savedIndex < 0 || savedIndex >= themes.length) savedIndex = 0;
        applyTheme(savedIndex);

        document.getElementById('themeToggleBtn')?.addEventListener('click', () => {
            applyTheme((currentThemeIndex + 1) % themes.length);
        });
    }

    // --- Favorites ---
    function getFavorites() {
        return Storage.get(KEYS.FAVORITES, []);
    }

    function isFavorite(schemeName) {
        return getFavorites().includes(schemeName);
    }

    function toggleFavorite(schemeName, buttonEl) {
        let favs = getFavorites();
        if (favs.includes(schemeName)) {
            favs = favs.filter(s => s !== schemeName);
            if (buttonEl) {
                buttonEl.classList.remove('active');
                buttonEl.textContent = '☆';
            }
        } else {
            favs.push(schemeName);
            if (buttonEl) {
                buttonEl.classList.add('active');
                buttonEl.textContent = '★';
            }
            if (navigator.vibrate) navigator.vibrate(50);
        }
        Storage.set(KEYS.FAVORITES, favs);
        renderFavoritesAndRecent();
    }

    // --- Recently Viewed ---
    function getRecent() {
        return Storage.get(KEYS.RECENT, []);
    }

    function addRecent(schemeName) {
        if (!schemeName) return;
        let recent = getRecent();
        recent = recent.filter(s => s !== schemeName);
        recent.unshift(schemeName);
        if (recent.length > 10) recent = recent.slice(0, 10);
        Storage.set(KEYS.RECENT, recent);
        renderFavoritesAndRecent();
    }

    // --- Render Favorites and Recent ---
    function renderFavoritesAndRecent() {
        const favs = getFavorites();
        const recents = getRecent();
        const favSec = document.getElementById('favoritesSection');
        const favList = document.getElementById('favoritesList');
        const recSec = document.getElementById('recentlyViewedSection');
        const recList = document.getElementById('recentlyViewedList');

        if (favSec && favList) {
            if (favs.length > 0) {
                favSec.style.display = 'block';
                favList.innerHTML = favs.map(name => `<a href="javascript:void(0)" class="recent-chip" data-scheme="${window.escapeHtml(name)}">${window.escapeHtml(window.schemesCatalog?.[name]?.telugu_name || name)}</a>`).join('');
            } else {
                favSec.style.display = 'none';
            }
        }

        if (recSec && recList) {
            if (recents.length > 0) {
                recSec.style.display = 'block';
                recList.innerHTML = recents.map(name => `<a href="javascript:void(0)" class="recent-chip" data-scheme="${window.escapeHtml(name)}">${window.escapeHtml(window.schemesCatalog?.[name]?.telugu_name || name)}</a>`).join('');
            } else {
                recSec.style.display = 'none';
            }
        }
    }

    // --- Share Result ---
    async function shareResult(schemeName) {
        if (!schemeName) return;
        
        const text = window.generateShareText ? window.generateShareText(schemeName) : generateShareText(schemeName);
        
        if (navigator.share) {
            try {
                await navigator.share({
                    title: 'SmartGov Health Eligibility',
                    text: text,
                    url: window.location.origin
                });
                return;
            } catch (err) {
                // If user canceled, just return quietly
                if (err.name !== 'AbortError') console.error('Share error:', err);
            }
        }
        
        // Fallback: Clipboard
        try {
            await navigator.clipboard.writeText(text);
            alert('✅ ఫలితం కాపీ చేయబడింది! (Copied to clipboard)');
        } catch (err) {
            // Fallback 2: Manual copy prompt
            window.prompt('కాపీ చేయడానికి కింద ఉన్న వచనాన్ని ఉపయోగించండి (Copy the text below):', text);
        }
    }

    // --- Symptom Finder Logic (Tier 2A) ---
    const symptomMappings = {
        hospital: {
            title: 'ఆసుపత్రి / అత్యవసర చికిత్స',
            categories: ['Hospital treatment', 'Emergency ambulance'],
            keywords: []
        },
        pregnancy: {
            title: 'గర్భం / ప్రసవం',
            categories: ['Pregnancy and newborn', 'Pregnancy cash support'],
            keywords: ['గర్భిణి', 'pregnancy', 'maternal']
        },
        child: {
            title: 'పిల్లల ఆరోగ్యం',
            categories: ['Child health', 'Vaccination'],
            keywords: ['పిల్లలు', 'child', 'pediatric', 'neonatal']
        },
        medicines: {
            title: 'మందులు / పరీక్షలు',
            categories: ['PHC and village care', 'Affordable Medicines', 'Primary Care Clinics'],
            keywords: []
        },
        eye_hearing: {
            title: 'కన్ను మరియు వినికిడి',
            categories: ['Eye Care Services', 'Hearing Care Services'],
            keywords: []
        },
        nutrition_blood: {
            title: 'పోషణ / రక్తం',
            categories: ['Nutritional Services', 'Blood Bank Services'],
            keywords: []
        },
        chronic: {
            title: 'దీర్ఘకాలిక వ్యాధులు',
            categories: ['TB support', 'TB Elimination Services', 'HIV & AIDS Services', 'Kidney dialysis', 'Leprosy Services', 'Malaria & Dengue Services', 'Rabies Prevention'],
            keywords: []
        },
        phone_digital: {
            title: 'ఫోన్ ద్వారా వైద్య సేవలు',
            categories: ['Doctor by phone', 'Digital Health Services'],
            keywords: []
        }
    };

    function openSymptomFinder() {
        document.getElementById('homeViewContainer').style.display = 'none';
        document.getElementById('symptomResultsView').style.display = 'none';
        document.getElementById('symptomCategoryView').style.display = 'block';
        document.querySelector('.toolbar').style.display = 'none';
        const banner = document.getElementById('symptomEntryBanner');
        if(banner) banner.style.display = 'none';
    }

    function closeSymptomFinder() {
        document.getElementById('symptomCategoryView').style.display = 'none';
        document.getElementById('symptomResultsView').style.display = 'none';
        document.getElementById('homeViewContainer').style.display = 'block';
        document.querySelector('.toolbar').style.display = ''; 
        const banner = document.getElementById('symptomEntryBanner');
        if(banner) banner.style.display = '';
    }

    function showSymptomCategories() {
        document.getElementById('symptomResultsView').style.display = 'none';
        document.getElementById('symptomCategoryView').style.display = 'block';
    }

    function renderSymptomResults(categoryId) {
        const mapping = symptomMappings[categoryId];
        if (!mapping) return;

        document.getElementById('symptomCategoryView').style.display = 'none';
        document.getElementById('symptomResultsView').style.display = 'block';
        document.getElementById('symptomResultTitle').textContent = mapping.title;

        const catalog = window.schemesCatalog || {};
        const matchedSchemes = [];

        for (const [schemeId, data] of Object.entries(catalog)) {
            let matched = false;
            
            // Priority 1: Exact scheme category match
            if (mapping.categories.includes(data.category)) {
                matched = true;
            }
            
            // Priority 2: Keyword match
            if (!matched && mapping.keywords.length > 0) {
                const schemeKeywords = (data.keywords || []).map(k => k.toLowerCase());
                for (const kw of mapping.keywords) {
                    if (schemeKeywords.includes(kw.toLowerCase())) {
                        matched = true;
                        break;
                    }
                }
            }
            
            if (matched) {
                matchedSchemes.push({ id: schemeId, data });
            }
        }
        
        const grid = document.getElementById('symptomSchemeGrid');
        const emptyState = document.getElementById('symptomNoResults');
        const countHeader = document.getElementById('symptomResultCount');

        if (matchedSchemes.length === 0) {
            grid.innerHTML = '';
            grid.style.display = 'none';
            emptyState.style.display = 'block';
            countHeader.textContent = '';
        } else {
            emptyState.style.display = 'none';
            grid.style.display = 'grid';
            countHeader.textContent = `${matchedSchemes.length} పథకాలు`;
            
            grid.innerHTML = matchedSchemes.map(item => {
                const s = item.data;
                const name = window.escapeHtml(item.id);
                const teluguName = window.escapeHtml(s.telugu_name || item.id);
                const desc = window.escapeHtml((s.telugu && s.telugu.eligibility) ? s.telugu.eligibility : (s.simplified && s.simplified.eligibility) ? s.simplified.eligibility : '');
                
                const iconMap = {
                    hospital: '🏥', ambulance: '🚑', 'mobile-clinic': '🩺', shield: '🛡',
                    clinic: '➕', 'phone-doctor': '📱', 'mother-child': '🤱', pregnancy: '🤰',
                    vaccine: '💉', child: '🧒', kidney: '🧬', nutrition: '🥣'
                };
                const icon = iconMap[s.icon] || '🏥';
                
                return `
                    <button type="button" class="scheme-card" data-action="open-scheme" data-scheme="${name}">
                        <div class="favorite-btn ${isFavorite(item.id) ? 'active' : ''}" data-scheme="${name}" title="Mark as favorite" aria-label="Favorite">⭐</div>
                        <div class="card-icon">${icon}</div>
                        <h2>${teluguName}</h2>
                        <p>${desc.substring(0, 80)}...</p>
                    </button>
                `;
            }).join('');
        }
    }

    // --- Guided Mode (Tier 2B) ---
    let currentGuidedSchemeName = null;
    let currentGuidedStep = 1;
    let previousFocusElement = null;

    function startGuidedMode() {
        if (!window.currentSchemeName || !window.schemesCatalog) return;
        currentGuidedSchemeName = window.currentSchemeName;
        currentGuidedStep = 1;
        previousFocusElement = document.activeElement;

        document.getElementById('guidedModeOverlay').style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        renderGuidedStep(currentGuidedStep);
        
        // Ensure focus moves to the dialog
        setTimeout(() => {
            document.getElementById('guidedTitle').focus();
        }, 50);
    }

    function exitGuidedMode() {
        document.getElementById('guidedModeOverlay').style.display = 'none';
        document.body.style.overflow = '';
        currentGuidedSchemeName = null;
        if (previousFocusElement) previousFocusElement.focus();
    }

    function renderGuidedStep(step) {
        if (!currentGuidedSchemeName) return;
        const scheme = window.schemesCatalog[currentGuidedSchemeName] || {};
        
        const titleEl = document.getElementById('guidedTitle');
        const progressEl = document.getElementById('guidedProgressText');
        const bodyEl = document.getElementById('guidedBody');
        const prevBtn = document.getElementById('guidedPrevBtn');
        const nextBtn = document.getElementById('guidedNextBtn');
        const favContainer = document.getElementById('guidedFavoriteContainer');

        // Render Favorite Button
        const schemeNameSafe = window.escapeHtml(currentGuidedSchemeName);
        favContainer.innerHTML = `<button type="button" class="favorite-btn ${isFavorite(currentGuidedSchemeName) ? 'active' : ''}" data-scheme="${schemeNameSafe}" title="Mark as favorite" aria-label="Favorite">⭐</button>`;

        titleEl.textContent = scheme.telugu_name || currentGuidedSchemeName;
        progressEl.textContent = `దశ ${step} / 6`;

        let stepHtml = '';
        
        if (step === 1) {
            let desc = 'వివరాలు అందుబాటులో లేవు.';
            if (scheme.original_complex_text) desc = scheme.original_complex_text;
            
            stepHtml = `
                <h3 class="guided-step-title">ℹ️ ఈ పథకం గురించి</h3>
                <div class="guided-step-content">
                    <p style="font-size: 1.2rem;">${window.escapeHtml(desc)}</p>
                </div>
            `;
        } else if (step === 2) {
            let elig = 'అర్హత వివరాలు అందుబాటులో లేవు.';
            if (scheme.telugu && scheme.telugu.eligibility) elig = scheme.telugu.eligibility;
            else if (scheme.simplified && scheme.simplified.eligibility) elig = scheme.simplified.eligibility;

            stepHtml = `
                <h3 class="guided-step-title">👤 ఎవరు పొందవచ్చు?</h3>
                <div class="guided-step-content">
                    <p>${window.escapeHtml(elig)}</p>
                </div>
            `;
        } else if (step === 3) {
            let ben = 'ప్రయోజనాల వివరాలు ప్రస్తుతం అందుబాటులో లేవు.';
            if (scheme.telugu && scheme.telugu.benefits) ben = scheme.telugu.benefits;
            else if (scheme.simplified && scheme.simplified.benefits) ben = scheme.simplified.benefits;

            stepHtml = `
                <h3 class="guided-step-title">🎁 ఏమి లభిస్తుంది?</h3>
                <div class="guided-step-content">
                    <p>${window.escapeHtml(ben)}</p>
                </div>
            `;
        } else if (step === 4) {
            let docsHtml = '<p>పత్రాల వివరాలు అందుబాటులో లేవు.</p>';
            if (scheme.required_documents && scheme.required_documents.length > 0) {
                docsHtml = `<ul>` + scheme.required_documents.map(d => `<li>✓ ${window.escapeHtml(d.name_te || d.name)}</li>`).join('') + `</ul>`;
            } else if (scheme.telugu && scheme.telugu.documents) {
                docsHtml = `<p>${window.escapeHtml(scheme.telugu.documents)}</p>`;
            }

            stepHtml = `
                <h3 class="guided-step-title">📄 ఏమి తీసుకెళ్లాలి?</h3>
                <div class="guided-step-content">
                    ${docsHtml}
                </div>
            `;
        } else if (step === 5) {
            let stepsStr = 'దరఖాస్తు విధానం అందుబాటులో లేదు. అధికారులను సంప్రదించండి.';
            if (scheme.telugu && scheme.telugu.steps) stepsStr = scheme.telugu.steps;
            else if (scheme.simplified && scheme.simplified.steps) stepsStr = scheme.simplified.steps;

            stepHtml = `
                <h3 class="guided-step-title">📝 ఎలా దరఖాస్తు చేయాలి?</h3>
                <div class="guided-step-content">
                    <p>${window.escapeHtml(stepsStr)}</p>
                </div>
            `;
        } else if (step === 6) {
            let contactInfo = 'వివరాలు అందుబాటులో లేవు.';
            if (scheme.contact_office) contactInfo = scheme.contact_office;
            else if (scheme.eligibility_confirmation) contactInfo = scheme.eligibility_confirmation;

            let websiteHtml = '';
            if (scheme.official_website) {
                websiteHtml = `<p style="margin-top:1rem;"><a href="${window.escapeHtml(scheme.official_website)}" target="_blank" rel="noopener noreferrer">🌐 అధికారిక వెబ్‌సైట్ (Official Website)</a></p>`;
            }
            
            let localHelp = '';
            if (scheme.local_help_locations && Object.values(scheme.local_help_locations).length > 0) {
                localHelp = `<p style="margin-top:1rem;"><strong>స్థానిక సహాయం (Local Help):</strong><br>` + Object.values(scheme.local_help_locations).map(l => window.escapeHtml(l)).join('<br>') + `</p>`;
            }

            stepHtml = `
                <h3 class="guided-step-title">📞 ఎవరిని సంప్రదించాలి?</h3>
                <div class="guided-step-content">
                    <p><strong>కార్యాలయం / అధికారి:</strong> ${window.escapeHtml(contactInfo)}</p>
                    ${localHelp}
                    ${websiteHtml}
                    <div style="margin-top:2rem;">
                        <button class="action-btn whatsapp share-whatsapp-btn" type="button" data-scheme="${schemeNameSafe}" style="width:100%; font-size:1.1rem; min-height:48px;">
                            📱 WhatsApp ద్వారా షేర్ చేయండి
                        </button>
                    </div>
                </div>
            `;
        }
        
        bodyEl.innerHTML = stepHtml;

        if (step === 1) {
            prevBtn.style.visibility = 'hidden';
        } else {
            prevBtn.style.visibility = 'visible';
        }

        if (step === 6) {
            nextBtn.textContent = 'ముగించు';
            nextBtn.dataset.action = 'guided-close';
        } else {
            nextBtn.textContent = 'తర్వాత →';
            nextBtn.dataset.action = 'guided-next';
        }
    }

    function nextGuidedStep() {
        if (currentGuidedStep < 6) {
            currentGuidedStep++;
            renderGuidedStep(currentGuidedStep);
            setTimeout(() => {
                document.getElementById('guidedTitle')?.focus();
            }, 50);
        }
    }

    function prevGuidedStep() {
        if (currentGuidedStep > 1) {
            currentGuidedStep--;
            renderGuidedStep(currentGuidedStep);
            setTimeout(() => {
                document.getElementById('guidedTitle')?.focus();
            }, 50);
        }
    }

    // --- Initialize ---
    document.addEventListener('DOMContentLoaded', () => {
        initFontSize();
        initTheme();
        renderFavoritesAndRecent();

        // Event delegations for new UI elements
        document.body.addEventListener('click', e => {
            const favBtn = e.target.closest('.favorite-btn');
            if (favBtn) {
                e.stopPropagation();
                toggleFavorite(favBtn.dataset.scheme, favBtn);
                return;
            }

            const chip = e.target.closest('.recent-chip');
            if (chip && window.fetchScheme) {
                window.fetchScheme(chip.dataset.scheme);
                return;
            }
            
            const shareBtn = e.target.closest('.share-result-btn');
            if (shareBtn) {
                shareResult(shareBtn.dataset.scheme);
                return;
            }

            // Symptom Finder entry points
            const symptomBanner = e.target.closest('.symptom-entry-banner');
            if (symptomBanner) {
                openSymptomFinder();
                return;
            }

            const symptomCategoryBtn = e.target.closest('.category-card');
            if (symptomCategoryBtn) {
                renderSymptomResults(symptomCategoryBtn.dataset.category);
                return;
            }

            // Centralized CSP-safe event delegation via data-action
            const actionTarget = e.target.closest('[data-action]');
            if (actionTarget) {
                const action = actionTarget.dataset.action;
                if (action === 'start-guided-mode') {
                    startGuidedMode();
                    return;
                }
                if (action === 'guided-next') {
                    nextGuidedStep();
                    return;
                }
                if (action === 'guided-prev') {
                    prevGuidedStep();
                    return;
                }
                if (action === 'guided-close') {
                    exitGuidedMode();
                    return;
                }
                if (action === 'show-symptom-categories') {
                    showSymptomCategories();
                    return;
                }
                if (action === 'close-symptom-finder') {
                    closeSymptomFinder();
                    return;
                }
                if (action === 'open-scheme') {
                    if (window.fetchScheme) {
                        window.fetchScheme(actionTarget.dataset.scheme);
                    }
                    return;
                }
                if (action === 'close-feedback') {
                    closeFeedbackModal();
                    return;
                }
                if (action === 'submit-feedback') {
                    submitFeedback();
                    return;
                }
                if (action === 'set-rating') {
                    setRating(actionTarget.dataset.value);
                    return;
                }
                if (action === 'set-feedback-chip') {
                    setFeedbackChip(actionTarget);
                    return;
                }
            }
        });

        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') {
                const guidedOverlay = document.getElementById('guidedModeOverlay');
                if (guidedOverlay && guidedOverlay.style.display === 'flex') {
                    exitGuidedMode();
                }
                const feedbackOverlay = document.getElementById('feedbackOverlay');
                if (feedbackOverlay && !feedbackOverlay.classList.contains('hidden')) {
                    closeFeedbackModal();
                }
            }
        });
        
        // Expose functions globally so HTML inline handlers and app.js can call them
        window.SmartGovUX = { 
            addRecent, 
            isFavorite,
            openSymptomFinder,
            closeSymptomFinder,
            showSymptomCategories,
            startGuidedMode,
            exitGuidedMode,
            nextGuidedStep,
            prevGuidedStep
        };
    });

    return window.SmartGovUX;
})();
