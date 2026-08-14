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

    const isEn = window.getLang && window.getLang() === 'en';
    const quizTitle = window.t ? window.t('quizTitle') : (isEn ? '🎯 Eligibility Check' : '🎯 అర్హత పరీక్ష');
    const btnYesLabel = window.t ? window.t('btnYes') : (isEn ? 'Yes' : 'అవును');
    const btnNoLabel = window.t ? window.t('btnNo') : (isEn ? 'No' : 'కాదు');

    let html = `<div class="eligibility-checker"><strong>${quizTitle}</strong>`;
    questions.forEach((q, idx) => {
        // Namespaced keys with fallback compatibility for existing users
        const saved = localStorage.getItem(`eligibility_${window.currentSchemeName}_q${idx}`) ||
                      localStorage.getItem(`eligibility_q${idx}`) || '';
        const yesClass = saved === 'yes' ? 'yes' : '';
        const noClass = saved === 'no' ? 'no' : '';
        const qText = isEn ? (q.question_en || q.question_te || q.question || '') : (q.question_te || q.question_en || q.question || '');

        html += `
            <div class="question-item">
                <p>${window.escapeHtml(qText)}</p>
                <div class="yes-no-buttons">
                    <button class="yes-no-btn ${yesClass}" type="button" data-idx="${idx}" data-answer="yes">✓ ${btnYesLabel}</button>
                    <button class="yes-no-btn ${noClass}" type="button" data-idx="${idx}" data-answer="no">✗ ${btnNoLabel}</button>
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

    const isEn = window.getLang && window.getLang() === 'en';
    const checklistTitle = window.t ? window.t('docChecklistTitle') : (isEn ? '📋 Document Checklist' : '📋 డాక్యుమెంట్ చెక్‌లిస్ట్');
    const optLabel = window.t ? ` ${window.t('docOptional')}` : (isEn ? ' (Optional)' : ' (ఐచ్ఛికం)');
    const mandLabel = window.t ? ` ${window.t('docMandatory')}` : (isEn ? ' (Mandatory)' : ' (తప్పనిసరి)');

    let html = `<div class="document-checklist"><strong>${checklistTitle}</strong>`;
    docs.forEach((doc, idx) => {
        const optional = doc.optional ? optLabel : mandLabel;
        const docName = isEn ? (doc.name || doc.name_te || '') : (doc.name_te || doc.name || '');
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

function printSchemeQRCard(schemeName, slug, schemeData) {
    if (!slug) {
        alert('QR కోడ్ అందుబాటులో లేదు.');
        return;
    }

    const printWindow = window.open('', '', 'width=700,height=900');
    if (!printWindow) {
        alert('పాప్‌అప్ బ్లాక్ చేయబడింది. దయచేసి పాప్‌అప్‌లను అనుమతించండి.');
        return;
    }

    const qrUrl = `/qr/${slug}.png`;

    printWindow.document.write(`
        <!DOCTYPE html>
        <html lang="te">
        <head>
            <meta charset="UTF-8">
            <title>${window.escapeHtml(schemeName)} - QR కార్డు</title>
            <style>
                @media print {
                    body { font-family: "Noto Sans Telugu", Arial, sans-serif; margin: 0; padding: 20px; }
                    .card-container {
                        border: 2px solid #176b5b;
                        border-radius: 12px;
                        padding: 30px;
                        max-width: 600px;
                        margin: 0 auto;
                        page-break-inside: avoid;
                    }
                    .header { text-align: center; border-bottom: 2px solid #eee; padding-bottom: 20px; margin-bottom: 20px; }
                    .header h1 { color: #176b5b; margin: 0; font-size: 24px; }
                    .header h2 { color: #555; margin: 10px 0 0 0; font-size: 16px; font-weight: normal; }
                    .section { margin-bottom: 15px; }
                    .section h3 { color: #0d4b40; margin: 0 0 5px 0; font-size: 18px; display: flex; align-items: center; gap: 8px; }
                    .section p { margin: 0; color: #333; line-height: 1.5; font-size: 14px; }
                    .qr-section { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px dashed #eee; }
                    .qr-section img { width: 180px; height: 180px; border: 4px solid #fff; outline: 1px solid #ccc; }
                    .qr-section p { margin-top: 10px; font-weight: bold; color: #176b5b; font-size: 16px; }
                    .footer { text-align: center; margin-top: 20px; color: #777; font-size: 12px; }
                    button, .no-print { display: none !important; }
                }
                /* Screen styles so it looks okay before print */
                body { font-family: "Noto Sans Telugu", Arial, sans-serif; background: #f9f9f9; padding: 20px; }
                .card-container { background: #fff; border: 2px solid #176b5b; border-radius: 12px; padding: 30px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
                .header { text-align: center; border-bottom: 2px solid #eee; padding-bottom: 20px; margin-bottom: 20px; }
                .header h1 { color: #176b5b; margin: 0; font-size: 24px; }
                .header h2 { color: #555; margin: 10px 0 0 0; font-size: 16px; font-weight: normal; }
                .section { margin-bottom: 15px; }
                .section h3 { color: #0d4b40; margin: 0 0 5px 0; font-size: 18px; }
                .section p { margin: 0; color: #333; line-height: 1.5; font-size: 14px; }
                .qr-section { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px dashed #eee; }
                .qr-section img { width: 180px; height: 180px; border: 4px solid #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
                .qr-section p { margin-top: 10px; font-weight: bold; color: #176b5b; font-size: 16px; }
                .footer { text-align: center; margin-top: 20px; color: #777; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="card-container">
                <div class="header">
                    <h2>SMARTGOVAI ఆరోగ్య / ప్రభుత్వ పథకం</h2>
                    <h1>${window.escapeHtml(schemeData.telugu_name || schemeName)}</h1>
                    <h2>${window.escapeHtml(schemeName)}</h2>
                </div>

                <div class="section">
                    <h3>👤 ఎవరికి? (Eligibility)</h3>
                    <p>${window.escapeHtml(schemeData.telugu.eligibility)}</p>
                </div>

                <div class="section">
                    <h3>🎁 ఏం లభిస్తుంది? (Benefits)</h3>
                    <p>${window.escapeHtml(schemeData.telugu.benefits)}</p>
                </div>

                <div class="section">
                    <h3>📋 ఏ పత్రాలు? (Documents)</h3>
                    <p>${window.escapeHtml(schemeData.telugu.documents)}</p>
                </div>

                <div class="section">
                    <h3>📝 ఎలా దరఖాస్తు చేసుకోవాలి? (Steps)</h3>
                    <p>${window.escapeHtml(schemeData.telugu.steps)}</p>
                </div>

                <div class="qr-section">
                    <img src="${qrUrl}" alt="Scheme QR Code">
                    <p>ఈ QR కోడ్ను స్కాన్ చేసి<br>పథకం పూర్తి వివరాలను చూడండి</p>
                </div>

                <div class="footer">
                    SmartGovAI - ${new Date().toLocaleDateString('te-IN')}
                </div>
            </div>
        </body>
        </html>
    `);
    printWindow.document.close();

    // Delay print to ensure content loads
    setTimeout(() => {
        printWindow.print();
    }, 500);
}

// ==================== Trust & Transparency ====================

function buildTrustInfo(scheme) {
    const isEn = window.getLang && window.getLang() === 'en';
    const lastUpdated = scheme.last_updated || (isEn ? 'Not specified' : 'తెలియదు');
    const confirmationSource = scheme.eligibility_confirmation || (isEn ? 'Government office / Empanelled hospital' : 'ప్రభుత్వ కార్యాలయం / ఆసుపత్రి');
    const officialWebsite = scheme.official_website || '#';

    const title = isEn ? '🔒 Trust & Transparency' : '🔒 విశ్వాస సమాచారం';
    const updatedLabel = isEn ? '📅 Last Updated:' : '📅 చివరిగా నవీకరించిన:';
    const verifyLabel = isEn ? '✔️ Verifying Authority:' : '✔️ సరిచేస్తారు:';
    const siteLabel = isEn ? '🌐 Official Portal:' : '🌐 అధికారిక సంచిక:';
    const visitText = isEn ? 'Visit Website' : 'సందర్శించండి';

    return `
        <div class="trust-info">
            <strong>${title}</strong><br>
            ${updatedLabel} ${window.escapeHtml(lastUpdated)}<br>
            ${verifyLabel} ${window.escapeHtml(confirmationSource)}<br>
            ${siteLabel} <a class="source-link" href="${window.escapeHtml(officialWebsite)}" target="_blank" rel="noopener noreferrer">${visitText}</a>
        </div>
    `;
}

function buildPrivacyWarning() {
    const isEn = window.getLang && window.getLang() === 'en';
    if (isEn) {
        return `
            <div class="privacy-warning">
                ⚠️ <strong>Privacy Notice:</strong><br>
                Do not upload Aadhaar numbers, private prescriptions, or personal medical records to this application.
            </div>
        `;
    }
    return `
        <div class="privacy-warning">
            ⚠️ <strong>గోప్యతా హెచ్చరిక:</strong><br>
            ఆధార్, ప్రెస్క్రిప్షన్లు లేదా వ్యక్తిగత ఆరోగ్య ఫైలులను ఈ యాప్‌కు అప్‌లోడ్ చేయవద్దు.
        </div>
    `;
}

// ==================== Sharing Features ====================

/**
 * Generate a canonical plain-text share message for a scheme
 */
function generateShareText(schemeName) {
    const scheme = window.schemesCatalog?.[schemeName] || {};
    const isEn = window.getLang && window.getLang() === 'en';

    if (isEn) {
        let text = `Scheme: ${schemeName}\n\n`;
        const elig = scheme.simplified?.eligibility || 'Check official guidelines';
        text += `Eligibility:\n${elig}\n\n`;
        const ben = scheme.simplified?.benefits || 'Check official guidelines';
        text += `Benefits:\n${ben}\n\n`;
        text += `Documents:\n`;
        if (scheme.required_documents && scheme.required_documents.length > 0) {
            text += scheme.required_documents.map(doc => doc.name || doc.name_te).join(', ');
        } else {
            text += scheme.simplified?.documents || 'Not specified';
        }
        text += `\n\nContact / Help:\n${scheme.contact_office || 'Government hospital / secretariat'}`;
        if (scheme.official_website) {
            text += `\n\nOfficial Website:\n${scheme.official_website}`;
        }
        return text;
    }

    // Telugu default
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
    const contact = scheme.telugu?.contact_office || scheme.eligibility_confirmation || scheme.contact_office || 'ప్రభుత్వ కార్యాలయం';
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

let previousFocusChat = null;

function appendChatMessage(text, role) {
    const messages = document.getElementById('chatMessages');
    if (!messages) return;

    const message = document.createElement('div');
    message.className = `chat-msg ${role}`;
    const paragraph = document.createElement('p');
    paragraph.textContent = text;
    message.appendChild(paragraph);
    messages.appendChild(message);
    messages.scrollTop = messages.scrollHeight;
}

function openChat(trigger) {
    const overlay = document.getElementById('chatOverlay');
    if (!overlay) return;

    const isEn = window.getLang && window.getLang() === 'en';
    const input = document.getElementById('chatInput');
    if (input) {
        input.placeholder = window.t ? window.t('chatPlaceholder') : (isEn ? 'Type your question in English or Telugu...' : 'మీ ప్రశ్నను ఇక్కడ రాయండి...');
    }

    const suggContainer = document.getElementById('chatSuggestionsContainer');
    if (suggContainer) {
        suggContainer.querySelectorAll('.chat-suggestion').forEach(btn => {
            const q = isEn ? (btn.dataset.questionEn || btn.dataset.questionTe) : (btn.dataset.questionTe || btn.dataset.questionEn);
            if (q) btn.dataset.question = q;
        });
    }

    previousFocusChat = trigger || document.activeElement;
    overlay.classList.remove('hidden');
    overlay.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    document.getElementById('chatInput')?.focus();
}

function closeChat() {
    const overlay = document.getElementById('chatOverlay');
    if (!overlay) return;

    overlay.classList.add('hidden');
    overlay.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    previousFocusChat?.focus();
}

async function sendChatQuestion(question) {
    const input = document.getElementById('chatInput');
    const trimmedQuestion = (question || input?.value || '').trim();
    if (!trimmedQuestion) return;

    const currentLang = window.getLang ? window.getLang() : 'te';
    const isEn = currentLang === 'en';

    appendChatMessage(trimmedQuestion, 'user');
    if (input) input.value = '';

    const messages = document.getElementById('chatMessages');
    const loading = document.createElement('div');
    loading.className = 'chat-msg bot loading';
    loading.textContent = window.t ? window.t('chatThinking') : (isEn ? 'Thinking...' : 'ఆలోచిస్తున్నాం...');
    messages?.appendChild(loading);

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...getCsrfHeader()
            },
            body: JSON.stringify({ question: trimmedQuestion, lang: currentLang })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Chat request failed');
        appendChatMessage(data.answer, 'bot');
    } catch (error) {
        appendChatMessage(window.t ? window.t('chatError') : (isEn ? 'Sorry, an error occurred while fetching the response.' : 'క్షమించండి, సమాధానం తీసుకురావడంలో లోపం ఏర్పడింది.'), 'bot');
        console.error('Chat request failed:', error);
    } finally {
        loading.remove();
    }
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
    // Auto-open scheme if provided by backend routing
    const autoOpenScheme = document.body.dataset.autoOpen;
    if (autoOpenScheme && window.fetchScheme) {
        setTimeout(() => window.fetchScheme(autoOpenScheme), 50);
    }

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

            // Print QR Card
            const printQrBtn = target.closest('[data-action="print-qr-card"]');
            if (printQrBtn) {
                const schemeName = printQrBtn.dataset.scheme;
                const slug = printQrBtn.dataset.slug;
                const schemeData = window.schemesCatalog ? window.schemesCatalog[schemeName] : null;
                printSchemeQRCard(schemeName, slug, schemeData || {});
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
            title_te: 'ఆసుపత్రి / అత్యవసర చికిత్స',
            title_en: 'Hospital / Emergency Treatment',
            categories: ['Hospital treatment', 'Emergency ambulance'],
            keywords: []
        },
        pregnancy: {
            title_te: 'గర్భం / ప్రసవం',
            title_en: 'Pregnancy / Maternity Care',
            categories: ['Pregnancy and newborn', 'Pregnancy cash support'],
            keywords: ['గర్భిణి', 'pregnancy', 'maternal']
        },
        child: {
            title_te: 'పిల్లల ఆరోగ్యం',
            title_en: 'Child Health / Immunization',
            categories: ['Child health', 'Vaccination'],
            keywords: ['పిల్లలు', 'child', 'pediatric', 'neonatal']
        },
        medicines: {
            title_te: 'మందులు / పరీక్షలు',
            title_en: 'Medicines / Diagnostics',
            categories: ['PHC and village care', 'Affordable Medicines', 'Primary Care Clinics'],
            keywords: []
        },
        eye_hearing: {
            title_te: 'కన్ను మరియు వినికిడి',
            title_en: 'Eye & Hearing Care',
            categories: ['Eye Care Services', 'Hearing Care Services'],
            keywords: []
        },
        nutrition_blood: {
            title_te: 'పోషణ / రక్తం',
            title_en: 'Nutrition & Blood Bank',
            categories: ['Nutritional Services', 'Blood Bank Services'],
            keywords: []
        },
        chronic: {
            title_te: 'దీర్ఘకాలిక వ్యాధులు',
            title_en: 'Chronic Disease Care',
            categories: ['TB support', 'TB Elimination Services', 'HIV & AIDS Services', 'Kidney dialysis', 'Leprosy Services', 'Malaria & Dengue Services', 'Rabies Prevention'],
            keywords: []
        },
        phone_digital: {
            title_te: 'ఫోన్ ద్వారా వైద్య సేవలు',
            title_en: 'Telehealth & Digital Services',
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
        if (banner) banner.style.display = 'none';
    }

    function closeSymptomFinder() {
        document.getElementById('symptomCategoryView').style.display = 'none';
        document.getElementById('symptomResultsView').style.display = 'none';
        document.getElementById('homeViewContainer').style.display = 'block';
        document.querySelector('.toolbar').style.display = '';
        const banner = document.getElementById('symptomEntryBanner');
        if (banner) banner.style.display = '';
    }

    function showSymptomCategories() {
        document.getElementById('symptomResultsView').style.display = 'none';
        document.getElementById('symptomCategoryView').style.display = 'block';
    }

    let activeSymptomCategory = null;

    function renderSymptomResults(categoryId) {
        if (categoryId) activeSymptomCategory = categoryId;
        const targetCategory = categoryId || activeSymptomCategory;
        if (!targetCategory) return;

        const mapping = symptomMappings[targetCategory];
        if (!mapping) return;

        const isEn = window.getLang && window.getLang() === 'en';
        document.getElementById('symptomCategoryView').style.display = 'none';
        document.getElementById('symptomResultsView').style.display = 'block';
        document.getElementById('symptomResultTitle').textContent = isEn ? mapping.title_en : mapping.title_te;

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
            countHeader.textContent = isEn ? `${matchedSchemes.length} Schemes Found` : `${matchedSchemes.length} పథకాలు`;

            grid.innerHTML = matchedSchemes.map(item => {
                const s = item.data;
                const name = window.escapeHtml(item.id);
                const primaryTitle = window.escapeHtml(isEn ? item.id : (s.telugu_name || item.id));
                const subTitle = window.escapeHtml(isEn ? (s.telugu_name || '') : item.id);
                const desc = window.escapeHtml(isEn ? (s.english_description || s.simplified?.eligibility || '') : (s.telugu_description || s.telugu?.eligibility || ''));

                const iconMap = {
                    hospital: '🏥', ambulance: '🚑', 'mobile-clinic': '🩺', shield: '🛡',
                    clinic: '➕', 'phone-doctor': '📱', 'mother-child': '🤱', pregnancy: '🤰',
                    vaccine: '💉', child: '🧒', kidney: '🧬', nutrition: '🥣'
                };
                const icon = iconMap[s.icon] || '🏥';
                const favTitle = isEn ? 'Favorite' : 'ఇష్టమైనది';

                return `
                    <button type="button" class="scheme-card" data-action="open-scheme" data-scheme="${name}">
                        <div class="favorite-btn ${isFavorite(item.id) ? 'active' : ''}" data-scheme="${name}" title="${favTitle}" aria-label="Favorite">⭐</div>
                        <div class="card-icon">${icon}</div>
                        <h2>${primaryTitle}</h2>
                        <p>${subTitle}</p>
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
            document.getElementById('guidedTitle')?.focus();
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
        const currentLang = window.getLang ? window.getLang() : 'te';
        const isEn = currentLang === 'en';

        const titleEl = document.getElementById('guidedTitle');
        const progressEl = document.getElementById('guidedProgressText');
        const bodyEl = document.getElementById('guidedBody');
        const prevBtn = document.getElementById('guidedPrevBtn');
        const nextBtn = document.getElementById('guidedNextBtn');
        const favContainer = document.getElementById('guidedFavoriteContainer');

        // Render Favorite Button
        const schemeNameSafe = window.escapeHtml(currentGuidedSchemeName);
        const favTitle = isEn ? 'Favorite' : 'ఇష్టమైనది';
        favContainer.innerHTML = `<button type="button" class="favorite-btn ${isFavorite(currentGuidedSchemeName) ? 'active' : ''}" data-scheme="${schemeNameSafe}" title="${favTitle}" aria-label="Favorite">⭐</button>`;

        titleEl.textContent = isEn ? currentGuidedSchemeName : (scheme.telugu_name || currentGuidedSchemeName);
        progressEl.textContent = window.t ? window.t('guidedStep', { step: step }) : (isEn ? `Step ${step} of 6` : `దశ ${step} / 6`);

        let stepHtml = '';

        if (step === 1) {
            let desc = isEn ? 'Details not available.' : 'వివరాలు అందుబాటులో లేవు.';
            if (isEn) {
                desc = scheme.english_description || scheme.simplified?.description || scheme.simplified?.benefits || scheme.original_complex_text || 'Details not available.';
            } else {
                desc = scheme.telugu_description || scheme.telugu?.description || scheme.telugu?.benefits || 'వివరాలు అందుబాటులో లేవు.';
            }

            const stepTitle = window.t ? window.t('guidedTitle1') : (isEn ? 'ℹ️ About This Scheme' : 'ℹ️ ఈ పథకం గురించి');

            stepHtml = `
                <h3 class="guided-step-title">${window.escapeHtml(stepTitle)}</h3>
                <div class="guided-step-content">
                    <p style="font-size: 1.15rem; line-height: 1.6;">${window.escapeHtml(desc)}</p>
                </div>
            `;
        } else if (step === 2) {
            let elig = isEn ? 'Eligibility details not available.' : 'అర్హత వివరాలు అందుబాటులో లేవు.';
            if (isEn) {
                if (scheme.simplified && scheme.simplified.eligibility) elig = scheme.simplified.eligibility;
                else if (scheme.telugu && scheme.telugu.eligibility) elig = scheme.telugu.eligibility;
            } else {
                if (scheme.telugu && scheme.telugu.eligibility) elig = scheme.telugu.eligibility;
                else if (scheme.simplified && scheme.simplified.eligibility) elig = scheme.simplified.eligibility;
            }

            const stepTitle = window.t ? window.t('guidedTitle2') : (isEn ? '👤 Who is Eligible?' : '👤 ఎవరు పొందవచ్చు?');

            stepHtml = `
                <h3 class="guided-step-title">${window.escapeHtml(stepTitle)}</h3>
                <div class="guided-step-content">
                    <p style="font-size: 1.1rem; line-height: 1.6;">${window.escapeHtml(elig)}</p>
                </div>
            `;
        } else if (step === 3) {
            let ben = isEn ? 'Benefits details not available.' : 'ప్రయోజనాల వివరాలు ప్రస్తుతం అందుబాటులో లేవు.';
            if (isEn) {
                if (scheme.simplified && scheme.simplified.benefits) ben = scheme.simplified.benefits;
                else if (scheme.telugu && scheme.telugu.benefits) ben = scheme.telugu.benefits;
            } else {
                if (scheme.telugu && scheme.telugu.benefits) ben = scheme.telugu.benefits;
                else if (scheme.simplified && scheme.simplified.benefits) ben = scheme.simplified.benefits;
            }

            const stepTitle = window.t ? window.t('guidedTitle3') : (isEn ? '🎁 Key Benefits' : '🎁 ఏమి లభిస్తుంది?');

            stepHtml = `
                <h3 class="guided-step-title">${window.escapeHtml(stepTitle)}</h3>
                <div class="guided-step-content">
                    <p style="font-size: 1.1rem; line-height: 1.6;">${window.escapeHtml(ben)}</p>
                </div>
            `;
        } else if (step === 4) {
            let docsHtml = isEn ? '<p>Documents details not available.</p>' : '<p>పత్రాల వివరాలు అందుబాటులో లేవు.</p>';
            if (scheme.required_documents && scheme.required_documents.length > 0) {
                docsHtml = `<ul>` + scheme.required_documents.map(d => {
                    const docName = isEn ? (d.name || d.name_te) : (d.name_te || d.name);
                    return `<li>✓ ${window.escapeHtml(docName)}</li>`;
                }).join('') + `</ul>`;
            } else if (isEn && scheme.simplified && scheme.simplified.documents) {
                docsHtml = `<p>${window.escapeHtml(scheme.simplified.documents)}</p>`;
            } else if (scheme.telugu && scheme.telugu.documents) {
                docsHtml = `<p>${window.escapeHtml(scheme.telugu.documents)}</p>`;
            }

            const stepTitle = window.t ? window.t('guidedTitle4') : (isEn ? '📄 Documents Required' : '📄 ఏమి తీసుకెళ్లాలి?');

            stepHtml = `
                <h3 class="guided-step-title">${window.escapeHtml(stepTitle)}</h3>
                <div class="guided-step-content">
                    ${docsHtml}
                </div>
            `;
        } else if (step === 5) {
            let stepsStr = isEn ? 'Application process not available. Please contact official authorities.' : 'దరఖాస్తు విధానం అందుబాటులో లేదు. అధికారులను సంప్రదించండి.';
            if (isEn) {
                if (scheme.simplified && scheme.simplified.steps) stepsStr = scheme.simplified.steps;
                else if (scheme.telugu && scheme.telugu.steps) stepsStr = scheme.telugu.steps;
            } else {
                if (scheme.telugu && scheme.telugu.steps) stepsStr = scheme.telugu.steps;
                else if (scheme.simplified && scheme.simplified.steps) stepsStr = scheme.simplified.steps;
            }

            const stepTitle = window.t ? window.t('guidedTitle5') : (isEn ? '📝 How to Apply' : '📝 ఎలా దరఖాస్తు చేయాలి?');

            stepHtml = `
                <h3 class="guided-step-title">${window.escapeHtml(stepTitle)}</h3>
                <div class="guided-step-content">
                    <p style="font-size: 1.1rem; line-height: 1.6;">${window.escapeHtml(stepsStr)}</p>
                </div>
            `;
        } else if (step === 6) {
            let contactInfo = isEn ? 'Details not available.' : 'వివరాలు అందుబాటులో లేవు.';
            if (scheme.contact_office) contactInfo = scheme.contact_office;
            else if (scheme.eligibility_confirmation) contactInfo = scheme.eligibility_confirmation;

            let websiteHtml = '';
            if (scheme.official_website) {
                const siteLabel = isEn ? '🌐 Official Website' : '🌐 అధికారిక వెబ్‌సైట్ (Official Website)';
                websiteHtml = `<p style="margin-top:1rem;"><a href="${window.escapeHtml(scheme.official_website)}" target="_blank" rel="noopener noreferrer">${siteLabel}</a></p>`;
            }

            let localHelp = '';
            if (scheme.local_help_locations && Object.values(scheme.local_help_locations).length > 0) {
                const helpTitle = isEn ? 'Local Help:' : 'స్థానిక సహాయం (Local Help):';
                localHelp = `<p style="margin-top:1rem;"><strong>${helpTitle}</strong><br>` + Object.values(scheme.local_help_locations).map(l => window.escapeHtml(l)).join('<br>') + `</p>`;
            }

            let mapHtml = `
                <div class="inline-map-container" id="inlineMapContainer" style="margin-top: 1.5rem;">
                    <div class="map-toolbar" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <h4 style="margin:0;">📍 ${isEn ? 'Nearby Healthcare Facilities' : 'దగ్గరలోని ఆరోగ్య కేంద్రాలు'}</h4>
                        <button class="action-btn" type="button" data-action="expand-map" style="padding: 4px 12px; min-height:36px; font-size:0.9rem;">${isEn ? 'Expand Map' : 'విస్తరించు (Expand)'}</button>
                    </div>
                    <div class="map-filters-ui" id="mapFiltersUi" style="padding: 10px; background: var(--surface-1); border-radius: 8px; margin-bottom: 8px;">
                        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 8px;">
                            <button type="button" class="secondary-btn" id="btnLocation" style="flex:1; font-size: 0.85rem; min-height: 36px; padding: 4px;">📍 ${isEn ? 'My Location' : 'నా స్థానం'}</button>
                            <button type="button" class="secondary-btn" id="btnMode" style="flex:1; font-size: 0.85rem; min-height: 36px; padding: 4px;">🗺️ ${isEn ? 'View All AP' : 'మొత్తం AP'}</button>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <input type="text" id="searchInput" class="map-select" placeholder="${isEn ? '🔍 Search name, village...' : '🔍 వెతకండి...'}" style="width:100%; box-sizing: border-box;">
                        </div>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                            <div style="flex: 1 1 45%;">
                                <label for="typeSelect" style="font-size: 0.85rem;">${isEn ? 'Type:' : 'రకం:'}</label>
                                <select id="typeSelect" class="map-select" style="width:100%;">
                                    <option value="all">${isEn ? 'All' : 'అన్నీ'}</option>
                                    <option value="PHC">PHC</option>
                                    <option value="CHC">CHC</option>
                                    <option value="Hospital">Hospital</option>
                                    <option value="none">${isEn ? 'Map Only' : 'కేవలం మ్యాప్'}</option>
                                </select>
                            </div>
                            <div style="flex: 1 1 45%;">
                                <label for="districtSelect" style="font-size: 0.85rem;">${isEn ? 'District:' : 'జిల్లా:'}</label>
                                <select id="districtSelect" class="map-select" style="width:100%;"><option value="">-- ${isEn ? 'Select' : 'ఎంచుకోండి'} --</option></select>
                            </div>
                            <div style="flex: 1 1 45%;">
                                <label for="mandalSelect" style="font-size: 0.85rem;">${isEn ? 'Mandal:' : 'మండలం:'}</label>
                                <select id="mandalSelect" class="map-select" style="width:100%;" disabled><option value="">-- ${isEn ? 'Select' : 'ఎంచుకోండి'} --</option></select>
                            </div>
                            <div style="flex: 1 1 45%;">
                                <label for="villageSelect" style="font-size: 0.85rem;">${isEn ? 'Village:' : 'గ్రామం:'}</label>
                                <select id="villageSelect" class="map-select" style="width:100%;" disabled><option value="">-- ${isEn ? 'Select' : 'ఎంచుకోండి'} --</option></select>
                            </div>
                        </div>
                        <div id="searchResults" style="margin-top: 8px; font-weight: bold; color: var(--primary);"></div>
                    </div>
                    <div id="inlineMap" class="map-container" style="height: 250px; border-radius: 8px; z-index:1; background: #e0e0e0; border: 1px solid #ccc;"></div>
                </div>
            `;

            const stepTitle = window.t ? window.t('guidedTitle6') : (isEn ? '📞 Where to Get Help' : '📞 ఎవరిని సంప్రదించాలి?');
            const officeLabel = isEn ? 'Office / Authority:' : 'కార్యాలయం / అధికారి:';
            const waShareText = isEn ? '📱 Share via WhatsApp' : '📱 WhatsApp ద్వారా షేర్ చేయండి';

            stepHtml = `
                <h3 class="guided-step-title">${window.escapeHtml(stepTitle)}</h3>
                <div class="guided-step-content">
                    <p><strong>${officeLabel}</strong> ${window.escapeHtml(contactInfo)}</p>
                    ${localHelp}
                    ${websiteHtml}
                    ${mapHtml}
                    <div style="margin-top:2rem;">
                        <button class="action-btn whatsapp share-whatsapp-btn" type="button" data-scheme="${schemeNameSafe}" style="width:100%; font-size:1.1rem; min-height:48px;">
                            ${waShareText}
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

        prevBtn.textContent = window.t ? window.t('guidedPrev') : (isEn ? '← Back' : '← వెనుకకు');

        if (step === 6) {
            nextBtn.textContent = window.t ? window.t('guidedFinish') : (isEn ? 'Finish' : 'ముగించు');
            nextBtn.dataset.action = 'guided-close';
            
            setTimeout(() => {
                if (window.initInlineMap) window.initInlineMap();
            }, 50);
        } else {
            nextBtn.textContent = window.t ? window.t('guidedNext') : (isEn ? 'Next →' : 'తర్వాత →');
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

            const chatBanner = e.target.closest('.chat-entry-banner');
            if (chatBanner) {
                openChat(chatBanner);
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
                if (action === 'expand-map') {
                    e.preventDefault();
                    window.expandMap();
                    return;
                }
                if (action === 'close-map') {
                    window.closeMapOverlay();
                    return;
                }
                if (action === 'open-chat') {
                    openChat(actionTarget);
                    return;
                }
                if (action === 'close-chat') {
                    closeChat();
                    return;
                }
                if (action === 'chat-suggestion') {
                    sendChatQuestion(actionTarget.dataset.question);
                    return;
                }
                if (action === 'send-chat') {
                    sendChatQuestion();
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
                const mapOverlay = document.getElementById('mapOverlay');
                if (mapOverlay && !mapOverlay.classList.contains('hidden')) {
                    window.closeMapOverlay();
                }
                const chatOverlay = document.getElementById('chatOverlay');
                if (chatOverlay && !chatOverlay.classList.contains('hidden')) {
                    closeChat();
                }
            }
        });

        document.getElementById('chatInput')?.addEventListener('keydown', event => {
            if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
                event.preventDefault();
                sendChatQuestion();
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

    // --- Tier 4 Map Logic ---
    let mapFacilities = [];
    let inlineMapObj = null;
    let fullMapObj = null;
    let inlineMarkers = [];
    let fullMarkers = [];
    let inlineUserMarker = null;
    let fullUserMarker = null;
    let userLat = null;
    let userLng = null;
    let isFetchingFacilities = false;
    let fetchPromise = null;

    let mapState = {
        mode: 'ANANTHAPURAMU', // 'ANANTHAPURAMU' or 'AP'
        type: 'all',
        district: 'Ananthapuramu',
        mandal: '',
        village: '',
        search: ''
    };

    function hasValidCoordinates(fac) {
        const lat = Number(fac?.lat);
        const lng = Number(fac?.lng);

        return (
            Number.isFinite(lat) &&
            Number.isFinite(lng) &&
            lat >= -90 &&
            lat <= 90 &&
            lng >= -180 &&
            lng <= 180
        );
    }

    function calculateHaversineDistance(lat1, lon1, lat2, lon2) {
        lat1 = Number(lat1);
        lon1 = Number(lon1);
        lat2 = Number(lat2);
        lon2 = Number(lon2);

        if (
            !Number.isFinite(lat1) ||
            !Number.isFinite(lon1) ||
            !Number.isFinite(lat2) ||
            !Number.isFinite(lon2)
        ) {
            return null;
        }

        const R = 6371;

        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;

        const a =
            Math.sin(dLat / 2) ** 2 +
            Math.cos(lat1 * Math.PI / 180) *
            Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) ** 2;

        const c =
            2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        return parseFloat((R * c).toFixed(2));
    }

    async function loadFacilities(forceDistanceRecalc = false) {
        if (mapFacilities.length === 0) {
            if (isFetchingFacilities) {
                try {
                    await fetchPromise;
                } catch (e) {
                    return [];
                }
            } else {
                isFetchingFacilities = true;

                fetchPromise = (async () => {
                    const response = await fetch('/api/facilities');

                    if (!response.ok) {
                        throw new Error(
                            `Facilities API failed: ${response.status}`
                        );
                    }

                    const data = await response.json();

                    mapFacilities = Array.isArray(data.data)
                        ? data.data
                        : [];

                    return mapFacilities;
                })();

                try {
                    await fetchPromise;
                } catch (e) {
                    console.error('Failed to load facilities', e);
                    mapFacilities = [];
                    return [];
                } finally {
                    isFetchingFacilities = false;
                }
            }
        }

        if (
            forceDistanceRecalc &&
            userLat !== null &&
            userLng !== null
        ) {
            mapFacilities.forEach(fac => {
                if (hasValidCoordinates(fac)) {
                    fac.distance_km = calculateHaversineDistance(
                        userLat,
                        userLng,
                        Number(fac.lat),
                        Number(fac.lng)
                    );
                } else {
                    delete fac.distance_km;
                }
            });

            mapFacilities.sort(
                (a, b) =>
                    (a.distance_km ?? Infinity) -
                    (b.distance_km ?? Infinity)
            );
        }

        populateDropdowns();
        syncUiFromState();

        return mapFacilities;
    }

    function populateDropdowns() {
        if (!mapFacilities || !mapFacilities.length) return;
        
        let availableFacilities = mapFacilities;
        if (mapState.mode === 'ANANTHAPURAMU') {
            availableFacilities = availableFacilities.filter(f => f.district === 'Ananthapuramu');
        }

        const districts = [...new Set(availableFacilities.map(f => f.district).filter(Boolean))].sort();
        let distHtml = '<option value="">-- ఎంచుకోండి (Select) --</option>';
        districts.forEach(d => distHtml += `<option value="${d}">${d}</option>`);
        ['districtSelect', 'districtSelectFull'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.innerHTML = distHtml;
        });

        const mandals = mapState.district 
            ? [...new Set(availableFacilities.filter(f => f.district === mapState.district).map(f => f.mandal).filter(Boolean))].sort()
            : [];
        let mandalHtml = '<option value="">-- ఎంచుకోండి (Select) --</option>';
        mandals.forEach(m => mandalHtml += `<option value="${m}">${m}</option>`);
        ['mandalSelect', 'mandalSelectFull'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.innerHTML = mandalHtml;
                el.disabled = !mapState.district;
            }
        });

        const villages = (mapState.district && mapState.mandal)
            ? [...new Set(availableFacilities.filter(f => f.district === mapState.district && f.mandal === mapState.mandal).map(f => f.village).filter(Boolean))].sort()
            : [];
        let villHtml = '<option value="">-- ఎంచుకోండి (Select) --</option>';
        villages.forEach(v => villHtml += `<option value="${v}">${v}</option>`);
        ['villageSelect', 'villageSelectFull'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.innerHTML = villHtml;
                el.disabled = !mapState.mandal;
            }
        });

        if (mapState.district && !districts.includes(mapState.district)) {
            if (mapState.mode === 'ANANTHAPURAMU') {
                mapState.district = 'Ananthapuramu';
            } else {
                mapState.district = '';
            }
        }
        if (mapState.mandal && !mandals.includes(mapState.mandal)) {
            mapState.mandal = '';
        }
        if (mapState.village && !villages.includes(mapState.village)) {
            mapState.village = '';
        }
    }

    function syncUiFromState() {
        ['typeSelect', 'typeSelectFull'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = mapState.type;
        });

        ['districtSelect', 'districtSelectFull'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = mapState.district;
        });

        ['mandalSelect', 'mandalSelectFull'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = mapState.mandal;
        });

        ['villageSelect', 'villageSelectFull'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = mapState.village;
        });

        ['searchInput', 'searchInputFull'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = mapState.search;
        });

        const nextModeLabel =
            mapState.mode === 'AP'
                ? '📍 అనంతపురం (View Ananthapuramu)'
                : '🗺️ మొత్తం AP (View All AP)';

        ['btnMode', 'btnModeFull'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.innerHTML = nextModeLabel;
        });
    }

    let listenersAttached = false;
    function setupEventListenersOnce() {
        if (listenersAttached) return;
        listenersAttached = true;

        const handleTypeChange = (e) => { 
            mapState.type = e.target.value; 
            syncUiFromState(); 
            applyFiltersAndRender(); 
        };
        const handleDistChange = (e) => { 
            mapState.district = e.target.value; 
            mapState.mandal = ''; 
            mapState.village = ''; 
            populateDropdowns(); 
            syncUiFromState(); 
            applyFiltersAndRender(); 
        };
        const handleMandalChange = (e) => {
            mapState.mandal = e.target.value;
            mapState.village = '';
            populateDropdowns();
            syncUiFromState();
            applyFiltersAndRender();
        };
        const handleVillageChange = (e) => { 
            mapState.village = e.target.value; 
            syncUiFromState(); 
            applyFiltersAndRender(); 
        };
        
        const handleSearch = (e) => {
            mapState.search = e.target.value.toLowerCase().trim();
            syncUiFromState();
            applyFiltersAndRender();
        };
        
        const handleModeToggle = () => {
            if (mapState.mode === 'ANANTHAPURAMU') {
                mapState.mode = 'AP';
                mapState.district = '';
                mapState.mandal = '';
                mapState.village = '';
                mapState.type = 'all';
                mapState.search = '';
            } else {
                mapState.mode = 'ANANTHAPURAMU';
                mapState.district = 'Ananthapuramu';
                mapState.mandal = '';
                mapState.village = '';
                mapState.type = 'all';
                mapState.search = '';
            }
            populateDropdowns();
            syncUiFromState();
            applyFiltersAndRender();
        };

        const handleLocation = () => {
            if (navigator.geolocation) {
                const btns = [document.getElementById('btnLocation'), document.getElementById('btnLocationFull')];
                btns.forEach(b => { if(b) b.innerHTML = '⏳ వెతుకుతోంది...'; });
                
                navigator.geolocation.getCurrentPosition(
                    async (pos) => {
                        userLat = pos.coords.latitude;
                        userLng = pos.coords.longitude;
                        await loadFacilities(true);
                        btns.forEach(b => { if(b) b.innerHTML = '📍 నా స్థానం (My Location)'; });
                        
                        if (inlineMapObj) {
                            if (inlineUserMarker) inlineMapObj.removeLayer(inlineUserMarker);
                            inlineUserMarker = L.circleMarker([userLat, userLng], {radius: 8, fillColor: '#228be6', color: '#fff', weight: 2, opacity: 1, fillOpacity: 0.8})
                                                .addTo(inlineMapObj).bindPopup("<b>మీ స్థానం (Your Location)</b>");
                        }
                        
                        if (fullMapObj) {
                            if (fullUserMarker) fullMapObj.removeLayer(fullUserMarker);
                            fullUserMarker = L.circleMarker([userLat, userLng], {radius: 8, fillColor: '#228be6', color: '#fff', weight: 2, opacity: 1, fillOpacity: 0.8})
                                              .addTo(fullMapObj).bindPopup("<b>మీ స్థానం (Your Location)</b>");
                        }
                        
                        applyFiltersAndRender();
                        
                        // Force a tight zoom to the user's location, like Google Maps
                        if (inlineMapObj) {
                            inlineMapObj.setView([userLat, userLng], 15);
                        }
                        if (fullMapObj) {
                            fullMapObj.setView([userLat, userLng], 15);
                        }
                    },
                    (err) => {
                        console.warn(`Geolocation Error [Code: ${err.code}]: ${err.message}`);
                        let errorMsg = '❌ స్థానం దొరకలేదు';
                        if (err.code === 1) errorMsg = '❌ అనుమతి నిరాకరించబడింది (Denied)';
                        else if (err.code === 2) errorMsg = '❌ స్థానం అందుబాటులో లేదు (Unavailable)';
                        else if (err.code === 3) errorMsg = '❌ సమయం ముగిసింది (Timeout)';
                        
                        btns.forEach(b => { if(b) b.innerHTML = errorMsg; });
                        setTimeout(() => { btns.forEach(b => { if(b) b.innerHTML = '📍 నా స్థానం (My Location)'; }); }, 3000);
                    },
                    { enableHighAccuracy: true, timeout: 15000 }
                );
            }
        };

        ['typeSelect', 'typeSelectFull'].forEach(id => { const el = document.getElementById(id); if (el) el.addEventListener('change', handleTypeChange); });
        ['districtSelect', 'districtSelectFull'].forEach(id => { const el = document.getElementById(id); if (el) el.addEventListener('change', handleDistChange); });
        ['mandalSelect', 'mandalSelectFull'].forEach(id => { const el = document.getElementById(id); if (el) el.addEventListener('change', handleMandalChange); });
        ['villageSelect', 'villageSelectFull'].forEach(id => { const el = document.getElementById(id); if (el) el.addEventListener('change', handleVillageChange); });
        ['searchInput', 'searchInputFull'].forEach(id => { const el = document.getElementById(id); if (el) el.addEventListener('input', handleSearch); });
        ['btnMode', 'btnModeFull'].forEach(id => { const el = document.getElementById(id); if (el) el.addEventListener('click', handleModeToggle); });
        ['btnLocation', 'btnLocationFull'].forEach(id => { const el = document.getElementById(id); if (el) el.addEventListener('click', handleLocation); });
    }

    function fitFacilitiesBounds(map, facilities) {
        if (!map) return;

        let minLat = 90;
        let maxLat = -90;
        let minLng = 180;
        let maxLng = -180;
        let hasPoints = false;

        const validFacilities = (facilities || []).filter(hasValidCoordinates);

        if (validFacilities.length > 0) {
            validFacilities.forEach(f => {
                const lat = Number(f.lat);
                const lng = Number(f.lng);
                if (lat < minLat) minLat = lat;
                if (lat > maxLat) maxLat = lat;
                if (lng < minLng) minLng = lng;
                if (lng > maxLng) maxLng = lng;
                hasPoints = true;
            });
        }

        if (userLat !== null && userLng !== null) {
            if (userLat < minLat) minLat = userLat;
            if (userLat > maxLat) maxLat = userLat;
            if (userLng < minLng) minLng = userLng;
            if (userLng > maxLng) maxLng = userLng;
            hasPoints = true;
        }

        if (!hasPoints) return;

        if (minLat === maxLat && minLng === maxLng) {
            map.setView([minLat, minLng], 14);
            return;
        }

        const bounds = [[minLat, minLng], [maxLat, maxLng]];
        map.fitBounds(bounds, { padding: [20, 20], maxZoom: 14 });
    }

    function applyFiltersAndRender() {
        if (!mapFacilities || !mapFacilities.length) return;
        
        let filtered = mapFacilities;
        
        if (mapState.mode === 'ANANTHAPURAMU') {
            filtered = filtered.filter(f => f.district === 'Ananthapuramu');
        }
        
        if (mapState.type !== 'all') {
            if (mapState.type === 'Hospital') {
                filtered = filtered.filter(f =>
                    typeof f.type === 'string' &&
                    f.type.toLowerCase().includes('hospital')
                );
            } else {
                filtered = filtered.filter(f => f.type === mapState.type);
            }
        }
        if (mapState.mode === 'AP' && mapState.district) {
            filtered = filtered.filter(f => f.district === mapState.district);
        }
        if (mapState.mandal) filtered = filtered.filter(f => f.mandal === mapState.mandal);
        if (mapState.village) filtered = filtered.filter(f => f.village === mapState.village);
        
        if (mapState.search) {
            filtered = filtered.filter(f => {
                return (f.name && f.name.toLowerCase().includes(mapState.search)) ||
                       (f.village && f.village.toLowerCase().includes(mapState.search)) ||
                       (f.mandal && f.mandal.toLowerCase().includes(mapState.search)) ||
                       (f.district && f.district.toLowerCase().includes(mapState.search));
            });
        }
        
        const resultText = `కనుగొనబడినవి: ${filtered.length}`;
        ['searchResults', 'searchResultsFull'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.innerText = resultText;
        });

        if (filtered.length > 0) {
            if (inlineMapObj) {
                fitFacilitiesBounds(inlineMapObj, filtered);
                renderFacilitiesOnMap(inlineMapObj, filtered, inlineMarkers);
            }
            if (fullMapObj) {
                fitFacilitiesBounds(fullMapObj, filtered);
                renderFacilitiesOnMap(fullMapObj, filtered, fullMarkers);
            }
        } else {
            if (inlineMapObj) {
                inlineMarkers.forEach(m => inlineMapObj.removeLayer(m));
                inlineMarkers.length = 0;
                fitFacilitiesBounds(inlineMapObj, []);
            }
            if (fullMapObj) {
                fullMarkers.forEach(m => fullMapObj.removeLayer(m));
                fullMarkers.length = 0;
                fitFacilitiesBounds(fullMapObj, []);
            }
        }
    }

    function getMarkerIcon(type) {
        let emoji = '🏥';
        if (type === 'PHC') emoji = '🩺';
        if (type === 'CHC') emoji = '🚑';
        
        return L.divIcon({
            html: `<div style="font-size:24px; text-shadow: 0 0 2px white; text-align:center;">${emoji}</div>`,
            className: 'custom-div-icon',
            iconSize: [30, 30],
            iconAnchor: [15, 15],
            popupAnchor: [0, -15]
        });
    }

    function renderFacilitiesOnMap(map, facilities, markersArray) {
        markersArray.forEach(m => map.removeLayer(m));
        markersArray.length = 0;
        
        let renderedCount = 0;
        let singleMarkerToOpen = null;
        
        facilities.forEach(fac => {
            if (!hasValidCoordinates(fac)) return;
            
            const marker = L.marker([Number(fac.lat), Number(fac.lng)], {
                icon: getMarkerIcon(fac.type)
            }).addTo(map);
            
            renderedCount++;
            singleMarkerToOpen = marker;
            
            const safeName = window.escapeHtml(fac.name || '');
            const safeType = window.escapeHtml(fac.type || '');
            const safeVillage = window.escapeHtml(fac.village || '');
            const safeMandal = window.escapeHtml(fac.mandal || '');
            const safeDistrict = window.escapeHtml(fac.district || '');
            const safeContact = window.escapeHtml(fac.contact || '');
            
            let popupContent = '';
            if (safeName) popupContent += `<b>${safeName}</b><br>`;
            if (safeType) popupContent += `<i>${safeType}</i><br>`;
            
            let locParts = [];
            if (safeVillage) locParts.push(safeVillage);
            if (safeMandal) locParts.push(`${safeMandal} (Mandal)`);
            if (safeDistrict) locParts.push(safeDistrict);
            
            if (locParts.length > 0) popupContent += locParts.join(', ') + '<br>';
            if (safeContact) popupContent += `<b>సంప్రదించండి (Contact):</b> ${safeContact}<br>`;
            if (fac.distance_km !== undefined && fac.distance_km !== null) {
                popupContent += `<b>దూరం (Distance):</b> ${fac.distance_km} km<br>`;
            }
            
            marker.bindPopup(popupContent);
            markersArray.push(marker);
        });
        
        if (renderedCount === 1 && singleMarkerToOpen) {
            setTimeout(() => {
                singleMarkerToOpen.openPopup();
            }, 200);
        }
    }

    window.initInlineMap = async function() {
        const container = document.getElementById('inlineMap');
        const containerWrap = document.getElementById('inlineMapContainer');
        if (!container || !containerWrap || !window.L) return;
        
        containerWrap.style.display = 'block';
        setupEventListenersOnce();
        
        if (inlineMapObj) {
            inlineMapObj.remove();
            inlineMapObj = null;
            inlineMarkers = [];
            inlineUserMarker = null;
        }
        
        inlineMapObj = L.map('inlineMap');
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(inlineMapObj);
        
        if (userLat !== null && userLng !== null) {
            inlineUserMarker = L.circleMarker([userLat, userLng], {
                radius: 8, fillColor: '#228be6', color: '#fff', weight: 2, opacity: 1, fillOpacity: 0.8
            }).addTo(inlineMapObj).bindPopup("<b>మీ స్థానం (Your Location)</b>");
        }

        setTimeout(() => inlineMapObj.invalidateSize(), 100);

        await loadFacilities();
        applyFiltersAndRender();
    };

    window.expandMap = async function() {
        const overlay = document.getElementById('mapOverlay');
        const mapDiv = document.getElementById('fullScreenMap');
        if (!overlay || !mapDiv || !window.L) return;
        
        overlay.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        setupEventListenersOnce();
        
        if (!fullMapObj) {
            fullMapObj = L.map('fullScreenMap');
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 18
            }).addTo(fullMapObj);
            
            if (userLat !== null && userLng !== null) {
                fullUserMarker = L.circleMarker([userLat, userLng], {
                    radius: 8, fillColor: '#228be6', color: '#fff', weight: 2, opacity: 1, fillOpacity: 0.8
                }).addTo(fullMapObj).bindPopup("<b>మీ స్థానం (Your Location)</b>");
            }
        }
        
        if (inlineMapObj) {
            fullMapObj.setView(inlineMapObj.getCenter(), inlineMapObj.getZoom());
        }
        
        setTimeout(() => fullMapObj.invalidateSize(), 300);

        await loadFacilities();
        applyFiltersAndRender();
    };

    window.closeMapOverlay = function() {
        const overlay = document.getElementById('mapOverlay');
        if (overlay) {
            overlay.classList.add('hidden');
            document.body.style.overflow = '';
            
            if (fullMapObj && inlineMapObj) {
                inlineMapObj.setView(fullMapObj.getCenter(), fullMapObj.getZoom());
            }
        }
    };

    // Listen for language change events to re-render active interactive views
    window.addEventListener('languagechange', () => {
        renderFavoritesAndRecent();
        if (currentGuidedSchemeName) {
            renderGuidedStep(currentGuidedStep);
        }
        if (activeSymptomCategory) {
            renderSymptomResults(activeSymptomCategory);
        }
    });

    return window.SmartGovUX;
})();
