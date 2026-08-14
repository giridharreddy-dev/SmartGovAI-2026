/**
 * SmartGovAI Localization Engine (i18n.js)
 * Global Telugu ↔ English localization system.
 * Defaults to Telugu ('te') on initial visit, with persistent localStorage support.
 */

(function () {
    'use strict';

    const STORAGE_KEY = 'smartgov_lang';
    const DEFAULT_LANG = 'te';

    const TRANSLATIONS = {
        te: {
            // App Shell & Header
            appTitle: 'SmartGov Health',
            appEyebrow: 'ఆంధ్రప్రదేశ్ ఆరోగ్య సహాయం',
            appSubhead: 'జాతీయ మరియు రాష్ట్ర ఆరోగ్య పథకాలు',
            langToggleTe: 'తెలుగు',
            langToggleEn: 'English',
            langToggleTeTitle: 'తెలుగులోకి మార్చండి',
            langToggleEnTitle: 'Switch to English',
            fontSizeSmall: 'చిన్న అక్షరాలు',
            fontSizeNormal: 'సాధారణ అక్షరాలు',
            fontSizeLarge: 'పెద్ద అక్షరాలు',
            themeToggle: 'థీమ్ మార్చండి',
            installApp: 'ఇన్‌స్టాల్ చేయండి',

            // Emergency Strip
            emergency: 'అత్యవసరం',
            healthAdvice: 'ఆరోగ్య సలహా',
            nearbyPhc: 'దగ్గర సేవ',

            // Search & Filters
            searchPlaceholder: 'పథకం పేరు లేదా సమస్య రాయండి...',
            voiceBtnAria: 'పథకం పేరు మాట్లాడండి',
            clearSearchAria: 'శోధన తొలగించండి',
            voiceStatusDefault: 'పథకం వెతకండి లేదా మైక్ నొక్కండి',
            voiceListening: 'వింటున్నాం... మాట్లాడండి',
            filterAll: 'అన్నీ',
            filterAp: 'ఆంధ్రప్రదేశ్',
            filterNational: 'జాతీయ',

            // Entry Banners
            symptomTitle: 'నా సమస్య',
            symptomSubtitle: 'మీ సమస్యకు సరిపోయే పథకాలను కనుగొనండి',
            symptomStartBtn: 'ప్రారంభించండి',
            chatTitle: 'పథకాల గురించి అడగండి',
            chatSubtitle: 'తెలుగులో ప్రశ్నలు అడగండి, AI సహాయం పొందండి',
            chatBtn: 'AI సహాయం',

            // Lists & Favorites
            favoritesTitle: '⭐ ఇష్టమైన పథకాలు (Favorites)',
            recentlyViewedTitle: '🕒 ఇటీవల చూసినవి (Recently Viewed)',
            emptyResultsTitle: 'ఫలితాలు లేవు',
            emptyResultsMsg: 'మరో పదంతో వెతకండి.',
            levelAp: 'ఆంధ్రప్రదేశ్',
            levelNational: 'జాతీయ',
            favoriteBtnTitle: 'ఇష్టమైనది (Favorite)',

            // Scheme Detail Panel
            loadingDetails: 'వివరాలు తెస్తున్నాం...',
            errorLoading: 'సమాచారం లోడ్ కాలేదు.',
            eligibilityTitle: 'అర్హత',
            benefitsTitle: 'ప్రయోజనాలు',
            documentsTitle: 'కావలసిన పత్రాలు',
            stepsTitle: 'దరఖాస్తు విధానం',
            aboutSchemeTitle: 'ఈ పథకం గురించి',
            sourceLabel: 'మూలం:',
            officialSource: 'అధికారిక మూలం',
            uploadedSource: 'అప్‌లోడ్ చేసిన పత్రం',
            audioTitle: '🎙️ తెలుగు ఆడియో',
            speakPageBtn: '🔊 ఈ పేజీ చదవండి',
            speakSlowBtn: '🔊 మెల్లగా చదవండి',
            audioNotAvailable: 'ఆడియో అందుబాటులో లేదు',
            startGuidedModeBtn: '👉 సులభంగా ఒక్కొక్కటిగా చూడండి',
            shareResultBtn: '📤 ఫలితాన్ని షేర్ చేయండి',
            printChecklistBtn: '🖨️ ముద్రణ',
            qrCardBtn: '📄 QR కార్డు',
            reportIssueBtn: '⚠️ సమస్య',
            feedbackGood: '👍 ఇష్టమైనది',
            feedbackImprove: '👎 మెరుగుపర్చండి',
            trustVerified: 'ధృవీకరించిన అధికారి:',
            trustLastUpdated: 'చివరిగా నవీకరించబడింది:',
            trustOfficialSite: '🌐 అధికారిక వెబ్‌సైట్',
            trustConfirmation: 'అర్హత ధృవీకరణ:',
            privacyWarning: '🔒 గోప్యతా నోటీసు: ఆధార్ కార్డు నంబర్లు లేదా వ్యక్తిగత వైద్య పత్రాలను ఇక్కడ అప్‌లోడ్ చేయవద్దు.',

            // Eligibility Checker
            quizTitle: '🎯 అర్హత పరీక్ష',
            quizSubtitle: 'సులభమైన ప్రశ్నలకు సమాధానం ఇవ్వండి:',
            btnYes: 'అవును',
            btnNo: 'కాదు',
            quizScore: 'మీ అర్హత అవకాశం:',
            quizHigh: 'మీరు ఈ పథకానికి అర్హత పొందే అవకాశం చాలా ఉంది.',
            quizMedium: 'మీరు కొన్ని నిబంధనలతో అర్హత పొందవచ్చు.',
            quizLow: 'ఈ పథకానికి అర్హత తక్కువగా ఉండవచ్చు.',
            quizDisclaimer: 'అధికారిక కార్యాలయంలో లేదా ఆసుపత్రిలో ధృవీకరించుకోండి.',

            // Document Checklist
            docChecklistTitle: '📋 డాక్యుమెంట్ చెక్‌లిస్ట్',
            docChecklistSubtitle: 'కార్యాలయానికి వెళ్లేముందు సరిచూసుకోండి:',
            docOptional: '(ఐచ్ఛికం)',
            docMandatory: '(తప్పనిసరి)',
            docProgress: '{count} / {total} పత్రాలు సిద్ధంగా ఉన్నాయి',

            // Guided Mode (Slide by Slide)
            guidedStep: 'దశ {step} / 6',
            guidedTitle1: 'ℹ️ ఈ పథకం గురించి',
            guidedTitle2: '👤 ఎవరు పొందవచ్చు?',
            guidedTitle3: '🎁 ఏమి లభిస్తుంది?',
            guidedTitle4: '📄 ఏమి తీసుకెళ్లాలి?',
            guidedTitle5: '📝 ఎలా దరఖాస్తు చేయాలి?',
            guidedTitle6: '📍 ఎక్కడ సహాయం పొందాలి?',
            guidedPrev: '← వెనుకకు',
            guidedNext: 'తరువాత →',
            guidedFinish: 'పూర్తయింది',
            guidedClose: 'మూసివేయి',
            localHelp: 'స్థానిక సహాయం:',
            nearbyCentres: 'దగ్గరలోని ఆరోగ్య కేంద్రాలు:',

            // Symptom Finder
            symptomNavBack: '← వెనుకకు',
            symptomNavCategories: '← సమస్యలు',
            symptomNavAll: 'అన్ని పథకాలు',
            symptomHeaderTitle: 'నా సమస్య ఏమిటి?',
            symptomHeaderSubtitle: 'మీకు ఏ రకమైన సహాయం కావాలి?',
            symptomResultsTitle: 'సరిపోయే పథకాలు ({count})',
            catHospital: 'ఆసుపత్రి / అత్యవసర చికిత్స',
            catPregnancy: 'గర్భం / ప్రసవం',
            catChild: 'పిల్లల ఆరోగ్యం',
            catMedicines: 'మందులు / పరీక్షలు',
            catEyeHearing: 'కన్ను మరియు వినికిడి',
            catNutrition: 'పోషణ / రక్తం',
            catChronic: 'దీర్ఘకాలిక వ్యాధులు',
            catTelehealth: 'ఫోన్ ద్వారా వైద్య సేవలు',

            // Facilities GIS Map
            mapHeader: '📍 దగ్గరలోని ఆరోగ్య కేంద్రాలు',
            mapExpand: 'విస్తరించు (Expand)',
            mapCollapse: 'కుదించు (Collapse)',
            mapLocationBtn: '📍 నా స్థానం (My Location)',
            mapViewAllBtn: '🗺️ మొత్తం AP (View All AP)',
            mapRadiusLabel: 'దూరం: {km} కి.మీ',
            mapTypeAll: 'అన్నీ',
            mapTypePhc: 'PHC',
            mapTypeChc: 'CHC',
            mapTypeHospital: 'ఆసుపత్రి',
            mapTypeDistrict: 'డిస్ట్రిక్ట్ ఆసుపత్రి',
            mapTypeArea: 'ఏరియా ఆసుపత్రి',
            mapDist: 'దూరం:',
            mapType: 'రకం:',
            mapDistrict: 'జిల్లా:',
            mapMandal: 'మండలం:',
            mapVillage: 'గ్రామం:',
            mapContact: 'సంప్రదించండి:',
            mapKm: 'కి.మీ',

            // AI Chat
            chatModalTitle: '💬 SmartGov AI సహాయకుడు',
            chatModalSubtitle: 'ఆరోగ్య పథకాల గురించి అడగండి',
            chatPlaceholder: 'మీ ప్రశ్నను ఇక్కడ రాయండి...',
            chatSendBtn: 'పంపండి',
            chatCloseAria: 'చాట్ మూసివేయి',
            chatWelcome: 'నమస్కారం! నేను SmartGov AI సహాయకుడిని. ఆంధ్రప్రదేశ్ ప్రభుత్వ ఆరోగ్య పథకాల గురించి మీరు ఏమైనా అడగవచ్చు.',
            chatDisclaimer: '⚠️ AI సమాచారం కేవలం మార్గదర్శకత్వం కొరకు మాత్రమే. అధికారిక ధృవీకరణ కోసం సమీప కార్యాలయాన్ని సంప్రదించండి.',
            chatSugg1: 'ఉచిత చికిత్స ఎలా పొందాలి?',
            chatSugg2: 'గర్భిణీ స్త్రీలకు ఏ పథకాలు ఉన్నాయి?',
            chatSugg3: 'ఆరోగ్యశ్రీకి అర్హత ఏమిటి?',
            chatSugg4: '108 అంబులెన్స్ సేవ ఎలా పొందాలి?',
            chatThinking: 'ఆలోచిస్తున్నాం...',
            chatError: 'క్షమించండి, సమాధానం తీసుకురావడంలో లోపం ఏర్పడింది.',

            // Secretariat / Staff Tools
            staffToolsSummary: 'సచివాలయం / ఆరోగ్య సిబ్బంది సాధనాలు',
            pdfSimplifyTitle: '📄 పాలసీ పత్రాన్ని సరళీకరించండి (PDF Simplification)',
            pdfConsent: 'నేను వ్యక్తిగత డేటాను అప్‌లోడ్ చేయడం లేదని ధృవీకరిస్తున్నాను (I consent to document processing without PII)',
            pdfSimplifyBtn: 'PDF ను సరళీకరించు',
            staffReportTitle: 'సమస్య నివేదించండి',
            staffVillage: 'గ్రామం',
            staffDetails: 'వివరాలు',
            staffSubmit: 'సమర్పించండి',

            // Modals
            feedbackTitle: 'మీ అభిప్రాయం చెప్పండి',
            feedbackRating: 'రేటింగ్:',
            feedbackComment: 'వ్యాఖ్యలు:',
            feedbackSubmit: 'పంపండి',
            feedbackCancel: 'రద్దు',
            shareSuccess: 'ఫలితం కాపీ చేయబడింది!',
            qrCardTitle: 'పథకం కరపత్రం (QR Card)',
            qrPrintBtn: '🖨️ ముద్రించండి',
            qrCloseBtn: 'మూసివేయి'
        },

        en: {
            // App Shell & Header
            appTitle: 'SmartGov Health',
            appEyebrow: 'Andhra Pradesh Healthcare Assistance',
            appSubhead: 'National & State Health Welfare Schemes',
            langToggleTe: 'తెలుగు',
            langToggleEn: 'English',
            langToggleTeTitle: 'తెలుగులోకి మార్చండి',
            langToggleEnTitle: 'Switch to English',
            fontSizeSmall: 'Small Text',
            fontSizeNormal: 'Normal Text',
            fontSizeLarge: 'Large Text',
            themeToggle: 'Toggle Theme',
            installApp: 'Install App',

            // Emergency Strip
            emergency: 'Emergency',
            healthAdvice: 'Health Advice',
            nearbyPhc: 'Nearby PHC',

            // Search & Filters
            searchPlaceholder: 'Search scheme name or health condition...',
            voiceBtnAria: 'Speak scheme name',
            clearSearchAria: 'Clear search',
            voiceStatusDefault: 'Search schemes or tap microphone',
            voiceListening: 'Listening... please speak',
            filterAll: 'All Schemes',
            filterAp: 'Andhra Pradesh',
            filterNational: 'National',

            // Entry Banners
            symptomTitle: 'Symptom Finder',
            symptomSubtitle: 'Find government schemes matching your health condition',
            symptomStartBtn: 'Get Started',
            chatTitle: 'Ask About Schemes',
            chatSubtitle: 'Ask questions in English, get instant AI guidance',
            chatBtn: 'AI Help',

            // Lists & Favorites
            favoritesTitle: '⭐ Favorite Schemes',
            recentlyViewedTitle: '🕒 Recently Viewed Schemes',
            emptyResultsTitle: 'No Schemes Found',
            emptyResultsMsg: 'Try searching with different keywords.',
            levelAp: 'Andhra Pradesh',
            levelNational: 'National',
            favoriteBtnTitle: 'Favorite',

            // Scheme Detail Panel
            loadingDetails: 'Loading scheme details...',
            errorLoading: 'Failed to load details.',
            eligibilityTitle: 'Eligibility',
            benefitsTitle: 'Benefits',
            documentsTitle: 'Required Documents',
            stepsTitle: 'How to Apply',
            aboutSchemeTitle: 'About This Scheme',
            sourceLabel: 'Source:',
            officialSource: 'Official Source',
            uploadedSource: 'Uploaded Document',
            audioTitle: '🎙️ Audio Guide',
            speakPageBtn: '🔊 Read Page Aloud',
            speakSlowBtn: '🔊 Read Aloud',
            audioNotAvailable: 'Audio not available',
            startGuidedModeBtn: '👉 Guided Step-by-Step View',
            shareResultBtn: '📤 Share Result',
            printChecklistBtn: '🖨️ Print Checklist',
            qrCardBtn: '📄 QR Flyer',
            reportIssueBtn: '⚠️ Report Issue',
            feedbackGood: '👍 Helpful',
            feedbackImprove: '👎 Needs Improvement',
            trustVerified: 'Verifying Authority:',
            trustLastUpdated: 'Last Updated:',
            trustOfficialSite: '🌐 Official Website',
            trustConfirmation: 'Eligibility Confirmation:',
            privacyWarning: '🔒 Privacy Notice: Do not upload Aadhaar card numbers or private medical prescriptions here.',

            // Eligibility Checker
            quizTitle: '🎯 Eligibility Check',
            quizSubtitle: 'Answer simple questions to check eligibility:',
            btnYes: 'Yes',
            btnNo: 'No',
            quizScore: 'Estimated Eligibility:',
            quizHigh: 'You are highly likely to be eligible for this scheme.',
            quizMedium: 'You may be eligible subject to specific conditions.',
            quizLow: 'Eligibility criteria may not be fully met.',
            quizDisclaimer: 'Please verify with the official government office or hospital.',

            // Document Checklist
            docChecklistTitle: '📋 Document Checklist',
            docChecklistSubtitle: 'Verify before visiting the government office:',
            docOptional: '(Optional)',
            docMandatory: '(Mandatory)',
            docProgress: '{count} of {total} documents ready',

            // Guided Mode (Slide by Slide)
            guidedStep: 'Step {step} of 6',
            guidedTitle1: 'ℹ️ About This Scheme',
            guidedTitle2: '👤 Who is Eligible?',
            guidedTitle3: '🎁 What Benefits are Provided?',
            guidedTitle4: '📄 What Documents to Carry?',
            guidedTitle5: '📝 How to Apply?',
            guidedTitle6: '📍 Where to Get Help?',
            guidedPrev: '← Previous',
            guidedNext: 'Next →',
            guidedFinish: 'Done',
            guidedClose: 'Close',
            localHelp: 'Local Assistance:',
            nearbyCentres: 'Nearby Healthcare Facilities:',

            // Symptom Finder
            symptomNavBack: '← Back',
            symptomNavCategories: '← Categories',
            symptomNavAll: 'All Schemes',
            symptomHeaderTitle: 'What is your health concern?',
            symptomHeaderSubtitle: 'What type of assistance do you need?',
            symptomResultsTitle: 'Matching Health Schemes ({count})',
            catHospital: 'Hospital / Emergency Care',
            catPregnancy: 'Pregnancy & Maternity',
            catChild: 'Child & Infant Health',
            catMedicines: 'Medicines & Diagnostics',
            catEyeHearing: 'Eye & Hearing Care',
            catNutrition: 'Nutrition & Anemia',
            catChronic: 'Chronic Diseases',
            catTelehealth: 'Telemedicine & Digital Health',

            // Facilities GIS Map
            mapHeader: '📍 Nearby Healthcare Facilities',
            mapExpand: 'Expand Map',
            mapCollapse: 'Collapse Map',
            mapLocationBtn: '📍 My Location',
            mapViewAllBtn: '🗺️ View All AP',
            mapRadiusLabel: 'Radius: {km} km',
            mapTypeAll: 'All Types',
            mapTypePhc: 'PHC',
            mapTypeChc: 'CHC',
            mapTypeHospital: 'Hospital',
            mapTypeDistrict: 'District Hospital',
            mapTypeArea: 'Area Hospital',
            mapDist: 'Distance:',
            mapType: 'Type:',
            mapDistrict: 'District:',
            mapMandal: 'Mandal:',
            mapVillage: 'Village:',
            mapContact: 'Contact:',
            mapKm: 'km',

            // AI Chat
            chatModalTitle: '💬 SmartGov AI Assistant',
            chatModalSubtitle: 'Ask questions about health schemes',
            chatPlaceholder: 'Type your question in English or Telugu...',
            chatSendBtn: 'Send',
            chatCloseAria: 'Close chat',
            chatWelcome: 'Hello! I am the SmartGov AI Assistant. You can ask me anything about Andhra Pradesh government health schemes in English or Telugu.',
            chatDisclaimer: '⚠️ AI responses are for guidance only. Please verify with the official government department for formal eligibility.',
            chatSugg1: 'How to get free hospital treatment?',
            chatSugg2: 'What schemes are available for pregnant women?',
            chatSugg3: 'What is the eligibility for Aarogyasri?',
            chatSugg4: 'How to call the 108 emergency ambulance?',
            chatThinking: 'Thinking...',
            chatError: 'Sorry, an error occurred while fetching the response.',

            // Secretariat / Staff Tools
            staffToolsSummary: 'Village Secretariat / Health Staff Tools',
            pdfSimplifyTitle: '📄 Simplify Policy Document (PDF Simplification)',
            pdfConsent: 'I confirm this document contains no personal data / PII and consent to processing',
            pdfSimplifyBtn: 'Simplify PDF Document',
            staffReportTitle: 'Report Scheme Discrepancy',
            staffVillage: 'Village / Mandal',
            staffDetails: 'Details',
            staffSubmit: 'Submit Report',

            // Modals
            feedbackTitle: 'Share Your Feedback',
            feedbackRating: 'Rating:',
            feedbackComment: 'Comments:',
            feedbackSubmit: 'Submit Feedback',
            feedbackCancel: 'Cancel',
            shareSuccess: 'Result link copied!',
            qrCardTitle: 'Scheme Flyer (QR Card)',
            qrPrintBtn: '🖨️ Print Flyer',
            qrCloseBtn: 'Close'
        }
    };

    // Category translations mapping
    const CATEGORIES = {
        'Hospital treatment': { te: 'ఆసుపత్రి చికిత్స', en: 'Hospital Treatment' },
        'Maternal & Child': { te: 'తల్లీ బిడ్డల సంరక్షణ', en: 'Maternal & Child Care' },
        'Emergency Medical': { te: 'అత్యవసర వైద్య సేవలు', en: 'Emergency Medical Services' },
        'National Health': { te: 'జాతీయ ఆరోగ్య పథకం', en: 'National Health Scheme' },
        'De-addiction Services': { te: 'వ్యసన విముక్తి సేవలు', en: 'De-addiction Services' },
        'Leprosy Services': { te: 'కుష్టు నివారణ సేవలు', en: 'Leprosy Eradication Services' },
        'Malaria & Dengue Services': { te: 'మలేరియా & డెంగ్యూ నివారణ', en: 'Vector Borne Disease Services' },
        'Eye Care Services': { te: 'నేత్ర చికిత్స సేవలు', en: 'Eye Care Services' },
        'Dental Health': { te: 'దంత ఆరోగ్యం', en: 'Dental Healthcare' },
        'Nutrition Services': { te: 'పోషకాహార సేవలు', en: 'Nutrition Services' },
        'Cancer Care': { te: 'క్యాన్సర్ చికిత్స సేవలు', en: 'Cancer Care' },
        'Mental Health': { te: 'మానసిక ఆరోగ్య సేవలు', en: 'Mental Healthcare' },
        'Elderly Care': { te: 'వృద్ధుల సంరక్షణ', en: 'Elderly Care' },
        'Palliative Care': { te: 'ఉపశమన సంరక్షణ', en: 'Palliative Care' },
        'Adolescent Health': { te: 'కౌమార ఆరోగ్య సేవలు', en: 'Adolescent Health' },
        'TB Services': { te: 'క్షయ వ్యాధి నివారణ', en: 'TB Elimination Services' },
        'Disability Welfare': { te: 'దివ్యాంగుల సంక్షేమం', en: 'Disability Welfare' },
        'Ayurveda & AYUSH': { te: 'ఆయుష్ & ఆయుర్వేదం', en: 'AYUSH & Traditional Medicine' },
        'Occupational Health': { te: 'వృత్తిపరమైన ఆరోగ్యం', en: 'Occupational Health' },
        'Rabies Control': { te: 'రేబీస్ నివారణ', en: 'Rabies Control' },
        'Dialysis & Kidney Care': { te: 'డయాలసిస్ & కిడ్నీ సంరక్షణ', en: 'Dialysis & Renal Care' },
        'Blood Transfusion': { te: 'రక్తనిధి సేవలు', en: 'Blood Bank Services' },
        'Tele-Medicine': { te: 'టెలి-మెడిసిన్ సేవలు', en: 'Telemedicine Services' },
        'Vaccination / Immunization': { te: 'టీకాల కార్యక్రమం', en: 'Vaccination & Immunization' }
    };

    let currentLang = DEFAULT_LANG;

    // Initialize language from localStorage (defaults to Telugu)
    function initLanguage() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            if (saved === 'en' || saved === 'te') {
                currentLang = saved;
            } else {
                currentLang = DEFAULT_LANG;
            }
        } catch (e) {
            currentLang = DEFAULT_LANG;
        }
        document.documentElement.setAttribute('lang', currentLang);
    }

    // Get current language code ('te' or 'en')
    function getLang() {
        return currentLang;
    }

    // Translate string key with optional param replacement {param}
    function t(key, params) {
        const langDict = TRANSLATIONS[currentLang] || TRANSLATIONS[DEFAULT_LANG];
        let text = langDict[key] || TRANSLATIONS[DEFAULT_LANG][key] || key;
        if (params && typeof params === 'object') {
            Object.keys(params).forEach(function (param) {
                text = text.replace(new RegExp('\\{' + param + '\\}', 'g'), params[param]);
            });
        }
        return text;
    }

    // Translate category
    function translateCategory(cat) {
        if (!cat) return '';
        if (CATEGORIES[cat]) {
            return CATEGORIES[cat][currentLang] || cat;
        }
        return cat;
    }

    // Translate level badge
    function translateLevel(level) {
        if (level === 'Andhra Pradesh') {
            return currentLang === 'te' ? 'ఆంధ్రప్రదేశ్' : 'Andhra Pradesh';
        }
        return currentLang === 'te' ? 'జాతీయ' : 'National';
    }

    // Set active language and apply across DOM
    function setLang(lang) {
        if (lang !== 'te' && lang !== 'en') return;
        currentLang = lang;
        try {
            localStorage.setItem(STORAGE_KEY, lang);
        } catch (e) {
            // ignore localStorage quota/privacy errors
        }

        document.documentElement.setAttribute('lang', lang);

        // Update toggle button states
        const teBtn = document.getElementById('langTeBtn');
        const enBtn = document.getElementById('langEnBtn');
        if (teBtn && enBtn) {
            if (lang === 'te') {
                teBtn.classList.add('active');
                teBtn.setAttribute('aria-pressed', 'true');
                enBtn.classList.remove('active');
                enBtn.setAttribute('aria-pressed', 'false');
            } else {
                enBtn.classList.add('active');
                enBtn.setAttribute('aria-pressed', 'true');
                teBtn.classList.remove('active');
                teBtn.setAttribute('aria-pressed', 'false');
            }
        }

        applyStaticTranslations();

        // Dispatch language change event for dynamic views
        window.dispatchEvent(new CustomEvent('languagechange', { detail: { lang: lang } }));
    }

    // Apply translations to all DOM elements with data-i18n attributes
    function applyStaticTranslations() {
        document.querySelectorAll('[data-i18n]').forEach(function (el) {
            const key = el.getAttribute('data-i18n');
            if (key) {
                el.textContent = t(key);
            }
        });

        document.querySelectorAll('[data-i18n-placeholder]').forEach(function (el) {
            const key = el.getAttribute('data-i18n-placeholder');
            if (key) {
                el.setAttribute('placeholder', t(key));
            }
        });

        document.querySelectorAll('[data-i18n-title]').forEach(function (el) {
            const key = el.getAttribute('data-i18n-title');
            if (key) {
                el.setAttribute('title', t(key));
            }
        });

        document.querySelectorAll('[data-i18n-aria]').forEach(function (el) {
            const key = el.getAttribute('data-i18n-aria');
            if (key) {
                el.setAttribute('aria-label', t(key));
            }
        });
    }

    // Expose global API
    initLanguage();

    window.SmartGovI18n = {
        getLang: getLang,
        setLang: setLang,
        t: t,
        translateCategory: translateCategory,
        translateLevel: translateLevel,
        applyStaticTranslations: applyStaticTranslations,
        TRANSLATIONS: TRANSLATIONS,
        CATEGORIES: CATEGORIES
    };

    // Shorthand helpers
    window.t = t;
    window.getLang = getLang;
    window.setLang = setLang;

})();
