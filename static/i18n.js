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
            voiceBtnAria: 'వాయిస్ ద్వారా వెతకండి',
            voiceBtnTitle: 'వాయిస్ ద్వారా వెతకండి',
            clearSearchAria: 'శోధన తొలగించండి',
            voiceStatusDefault: 'పథకం వెతకండి లేదా మైక్ నొక్కండి',
            voiceListening: 'వింటున్నాం... మాట్లాడండి',
            voiceNotSupported: 'ఈ బ్రౌజర్ వాయిస్ సెర్చ్‌కు మద్దతు ఇవ్వదు.',
            voiceStartError: 'మైక్ ప్రారంభం కాలేదు. మళ్లీ ప్రయత్నించండి.',
            voiceErrNotAllowed: 'మైక్రోఫోన్ అనుమతి నిరాకరించబడింది. దయచేసి బ్రౌజర్ సెట్టింగ్స్‌లో మైక్ అనుమతించండి.',
            voiceErrNoSpeech: 'మాట వినిపించలేదు. దయచేసి మళ్లీ మాట్లాడండి.',
            voiceErrAudioCapture: 'మైక్రోఫోన్ కనుగొనబడలేదు లేదా ఆడియో రికార్డింగ్ విఫలమైంది.',
            voiceErrNetwork: 'వాయిస్ గుర్తింపులో నెట్‌వర్క్ సమస్య ఏర్పడింది.',
            voiceErrAborted: 'వాయిస్ ఇన్‌పుట్ రద్దు చేయబడింది.',
            voiceErrGeneric: 'మైక్ లోపం: {error}',
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
            favoritesTitle: '⭐ ఇష్టమైన పథకాలు',
            recentlyViewedTitle: '🕒 ఇటీవల చూసిన పథకాలు',
            emptyResultsTitle: 'ఫలితాలు లేవు',
            emptyResultsMsg: 'మరో పదంతో వెతకండి.',
            levelAp: 'ఆంధ్రప్రదేశ్',
            levelNational: 'జాతీయ',
            favoriteBtnTitle: 'ఇష్టమైనదిగా గుర్తించండి',

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
            feedbackSaving: 'సేవ్ చేస్తున్నాం...',
            feedbackSuccess: '✅ ధన్యవాదాలు! మీ అభిప్రాయం నమోదు చేయబడింది.',
            feedbackError: '❌ అభిప్రాయం పంపలేకపోయాము. దయచేసి మళ్లీ ప్రయత్నించండి.',
            networkError: 'నెట్‌వర్క్ లోపం: {error}',
            selectSchemeError: 'దయచేసి పథకం ఎంచుకోండి.',
            selectPdfError: 'దయచేసి PDF ఫైల్ ఎంచుకోండి.',
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
            quizDisclaimer: 'అధికారిక ఆసుపత్రి, PHC, ASHA/ANM లేదా గ్రామ సచివాలయం వద్ద చివరి అర్హతను తప్పక ధృవీకరించండి.',

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
            guidedNext: 'తర్వాత →',
            guidedFinish: 'ముగించు',
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
            mapExpand: 'విస్తరించు',
            mapCollapse: 'కుదించు',
            mapLocationBtn: '📍 నా స్థానం',
            mapViewAllBtn: '🗺️ మొత్తం AP',
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
            mapSelectDistrict: '-- జిల్లాను ఎంచుకోండి --',
            mapSelectMandal: '-- మండలాన్ని ఎంచుకోండి --',
            mapSelectVillage: '-- గ్రామాన్ని ఎంచుకోండి --',
            mapLocationFinding: '⏳ వెతుకుతోంది...',
            mapYourLocationPopup: 'మీ స్థానం',
            mapErrDenied: '❌ అనుమతి నిరాకరించబడింది',
            mapErrUnavailable: '❌ స్థానం అందుబాటులో లేదు',
            mapErrTimeout: '❌ సమయం ముగిసింది',
            mapErrNotFound: '❌ స్థానం దొరకలేదు',
            mapFoundCount: 'కనుగొనబడినవి: {count}',

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
            selectSchemeFromList: 'జాబితా నుండి పథకం',
            selectDropdownPlaceholder: '-- ఎంచుకోండి --',
            showDetailsBtn: 'వివరాలు చూపించు',
            pdfDocumentLabel: 'PDF పత్రం',
            pdfSimplifyTitle: '📄 పాలసీ పత్రాన్ని సరళీకరించండి',
            pdfConsent: 'నేను వ్యక్తిగత డేటాను అప్‌లోడ్ చేయడం లేదని ధృవీకరిస్తున్నాను (I consent to document processing without PII)',
            pdfSimplifyBtn: 'PDF ను సరళీకరించు',
            offlineModeNotice: '📡 ఆఫ్‌లైన్ మోడ్ - కాష్‌ చేసిన సమాచారం చూపిస్తున్నాం',
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
            shareSuccess: '✅ ఫలితం కాపీ చేయబడింది!',
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
            voiceBtnAria: 'Search by voice',
            voiceBtnTitle: 'Search by voice',
            clearSearchAria: 'Clear search',
            voiceStatusDefault: 'Search schemes or tap microphone',
            voiceListening: 'Listening... please speak',
            voiceNotSupported: 'Voice search is not supported on this browser.',
            voiceStartError: 'Could not start microphone. Please try again.',
            voiceErrNotAllowed: 'Microphone permission was denied. Please allow microphone access in browser settings.',
            voiceErrNoSpeech: 'No speech was detected. Please try speaking again.',
            voiceErrAudioCapture: 'No microphone found or audio capture failed.',
            voiceErrNetwork: 'Network error during voice recognition.',
            voiceErrAborted: 'Voice input was cancelled.',
            voiceErrGeneric: 'Microphone error: {error}',
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
            favoriteBtnTitle: 'Toggle favorite',

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
            feedbackSaving: 'Saving...',
            feedbackSuccess: '✅ Thank you! Your feedback has been recorded.',
            feedbackError: '❌ Could not submit feedback. Please try again.',
            networkError: 'Network error: {error}',
            selectSchemeError: 'Please select a scheme.',
            selectPdfError: 'Please select a PDF file.',
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
            quizDisclaimer: 'Please verify final eligibility at an official hospital, PHC, ASHA/ANM or Village Secretariat.',

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
            mapSelectDistrict: '-- Select District --',
            mapSelectMandal: '-- Select Mandal --',
            mapSelectVillage: '-- Select Village --',
            mapLocationFinding: '⏳ Locating...',
            mapYourLocationPopup: 'Your Location',
            mapErrDenied: '❌ Location permission denied',
            mapErrUnavailable: '❌ Location unavailable',
            mapErrTimeout: '❌ Location request timed out',
            mapErrNotFound: '❌ Location not found',
            mapFoundCount: 'Found: {count}',

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
            selectSchemeFromList: 'Select Scheme From List',
            selectDropdownPlaceholder: '-- Select Scheme --',
            showDetailsBtn: 'Show Details',
            pdfDocumentLabel: 'PDF Document',
            pdfSimplifyTitle: '📄 Simplify Policy Document',
            pdfConsent: 'I confirm this document contains no personal data / PII and consent to processing',
            pdfSimplifyBtn: 'Simplify PDF Document',
            offlineModeNotice: '📡 Offline Mode - Showing cached data',
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
            shareSuccess: '✅ Result copied to clipboard!',
            qrCardTitle: 'Scheme Flyer (QR Card)',
            qrPrintBtn: '🖨️ Print Flyer',
            qrCloseBtn: 'Close'
        }
    };

    // Category translations mapping
    const CATEGORIES = {
        'Hospital treatment': { te: 'ఆసుపత్రి చికిత్స', en: 'Hospital Treatment' },
        'Hospital Treatment': { te: 'ఆసుపత్రి చికిత్స', en: 'Hospital Treatment' },
        'Hospital Care': { te: 'ఆసుపత్రి చికిత్స', en: 'Hospital Care' },
        'Maternal & Child': { te: 'తల్లీ బిడ్డల సంరక్షణ', en: 'Maternal & Child Care' },
        'Maternal Health': { te: 'తల్లీ బిడ్డల ఆరోగ్యం', en: 'Maternal Health' },
        'Maternal Cash Support': { te: 'గర్భిణులకు నగదు ప్రోత్సాహం', en: 'Maternal Cash Support' },
        'Emergency Medical': { te: 'అత్యవసర వైద్య సేవలు', en: 'Emergency Medical Services' },
        'National Health': { te: 'జాతీయ ఆరోగ్య పథకం', en: 'National Health Scheme' },
        'De-addiction Services': { te: 'వ్యసన విముక్తి సేవలు', en: 'De-addiction Services' },
        'Leprosy Services': { te: 'కుష్టు నివారణ సేవలు', en: 'Leprosy Eradication Services' },
        'Leprosy Eradication Services': { te: 'కుష్టు నివారణ సేవలు', en: 'Leprosy Eradication Services' },
        'Malaria & Dengue Services': { te: 'మలేరియా & డెంగ్యూ నివారణ', en: 'Vector Borne Disease Services' },
        'Vector Borne Disease Services': { te: 'మలేరియా & డెంగ్యూ నివారణ', en: 'Vector Borne Disease Services' },
        'Eye Care Services': { te: 'నేత్ర చికిత్స సేవలు', en: 'Eye Care Services' },
        'Hearing Care Services': { te: 'వినికిడి సంరక్షణ సేవలు', en: 'Hearing Care Services' },
        'Dental Health': { te: 'దంత ఆరోగ్యం', en: 'Dental Healthcare' },
        'Nutrition Services': { te: 'పోషకాహార సేవలు', en: 'Nutrition Services' },
        'Nutritional Services': { te: 'పోషకాహార సేవలు', en: 'Nutritional Services' },
        'Cancer Care': { te: 'క్యాన్సర్ చికిత్స సేవలు', en: 'Cancer Care' },
        'Mental Health': { te: 'మానసిక ఆరోగ్య సేవలు', en: 'Mental Healthcare' },
        'Mental Health Services': { te: 'మానసిక ఆరోగ్య సేవలు', en: 'Mental Health Services' },
        'Elderly Care': { te: 'వృద్ధుల సంరక్షణ', en: 'Elderly Care' },
        'Elderly Care Services': { te: 'వృద్ధుల సంరక్షణ', en: 'Elderly Care Services' },
        'Palliative Care': { te: 'ఉపశమన సంరక్షణ', en: 'Palliative Care' },
        'Adolescent Health': { te: 'కౌమార ఆరోగ్య సేవలు', en: 'Adolescent Health' },
        'TB Services': { te: 'క్షయ వ్యాధి నివారణ', en: 'TB Elimination Services' },
        'TB Elimination Services': { te: 'క్షయ వ్యాధి నివారణ', en: 'TB Elimination Services' },
        'TB support': { te: 'క్షయ పోషణ సహాయం', en: 'TB Nutrition Support' },
        'HIV & AIDS Services': { te: 'హెచ్‌ఐవి & ఎయిడ్స్ సేవలు', en: 'HIV & AIDS Services' },
        'Kidney dialysis': { te: 'డయాలసిస్ & కిడ్నీ సంరక్షణ', en: 'Kidney Dialysis Services' },
        'Disability Welfare': { te: 'దివ్యాంగుల సంక్షేమం', en: 'Disability Welfare' },
        'Ayurveda & AYUSH': { te: 'ఆయుష్ & ఆయుర్వేదం', en: 'AYUSH & Traditional Medicine' },
        'Occupational Health': { te: 'వృత్తిపరమైన ఆరోగ్యం', en: 'Occupational Health' },
        'Rabies Control': { te: 'రేబీస్ నివారణ', en: 'Rabies Control' },
        'Rabies Prevention': { te: 'రేబీస్ నివారణ', en: 'Rabies Prevention' },
        'Dialysis & Kidney Care': { te: 'డయాలసిస్ & కిడ్నీ సంరక్షణ', en: 'Dialysis & Renal Care' },
        'Blood Bank Services': { te: 'రక్తనిధి సేవలు', en: 'Blood Bank Services' },
        'Blood Transfusion': { te: 'రక్తనిధి సేవలు', en: 'Blood Bank Services' },
        'Tele-Medicine': { te: 'టెలి-మెడిసిన్ సేవలు', en: 'Telemedicine Services' },
        'Digital Health Services': { te: 'డిజిటల్ ఆరోగ్య సేవలు', en: 'Digital Health Services' },
        'Doctor by phone': { te: 'ఫోన్ ద్వారా డాక్టర్ సలహా', en: 'Doctor by Phone' },
        'PHC and village care': { te: 'గ్రామ ప్రాథమిక ఆరోగ్య సేవలు', en: 'Primary Healthcare & Village Clinics' },
        'Village health service': { te: 'గ్రామ ఆరోగ్య సేవలు', en: 'Village Health Service' },
        'Primary Care Clinics': { te: 'పట్టణ & ప్రాథమిక ఆరోగ్య కేంద్రాలు', en: 'Primary Care Clinics' },
        'Affordable Medicines': { te: 'తక్కువ ధరల మందులు (జన ఔషధి)', en: 'Affordable Generic Medicines' },
        'Pregnancy and newborn': { te: 'గర్భిణి & నవజాత శిశు సంరక్షణ', en: 'Pregnancy & Newborn Care' },
        'Pregnancy cash support': { te: 'గర్భిణులకు నగదు ప్రోత్సాహం', en: 'Maternity Cash Assistance' },
        'Child health': { te: 'పిల్లల ఆరోగ్య సేవలు', en: 'Child Health & Screening' },
        'Vaccination': { te: 'టీకాల కార్యక్రమం', en: 'Vaccination & Immunization' },
        'Vaccination / Immunization': { te: 'టీకాల కార్యక్రమం', en: 'Vaccination & Immunization' },
        'Emergency ambulance': { te: 'అత్యవసర అంబులెన్స్ సేవ', en: 'Emergency Ambulance Service' },
        'Organ Donation Services': { te: 'అవయవ దాన సేవలు', en: 'Organ Donation Services' }
    };

    let currentLang = DEFAULT_LANG;

    // Initialize language from localStorage (defaults to Telugu)
    function initLanguage() {
        try {
            const storage = (typeof window !== 'undefined' && window.localStorage) ? window.localStorage : (typeof localStorage !== 'undefined' ? localStorage : null);
            const saved = storage ? (storage.getItem(STORAGE_KEY) || storage.getItem('smartgov_language')) : null;
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

    // Translate string key with optional param replacement {param} and optional lang override
    function t(key, params, lang) {
        const l = lang || currentLang;
        const langDict = TRANSLATIONS[l] || TRANSLATIONS[DEFAULT_LANG];
        let text = langDict[key] || (TRANSLATIONS[DEFAULT_LANG] ? TRANSLATIONS[DEFAULT_LANG][key] : '') || key;
        if (params && typeof params === 'object') {
            Object.keys(params).forEach(function (param) {
                text = text.replace(new RegExp('\\{' + param + '\\}', 'g'), params[param]);
            });
        }
        return text;
    }

    // Translate category with optional lang override
    function translateCategory(cat, lang) {
        if (!cat) return '';
        const l = lang || currentLang;
        if (CATEGORIES[cat]) {
            return CATEGORIES[cat][l] || cat;
        }
        for (const k in CATEGORIES) {
            if (CATEGORIES[k].en === cat || CATEGORIES[k].te === cat) {
                return CATEGORIES[k][l] || cat;
            }
        }
        return cat;
    }

    // Translate level badge with optional lang override
    function translateLevel(level, lang) {
        const l = lang || currentLang;
        if (level === 'Andhra Pradesh') {
            return l === 'te' ? 'ఆంధ్రప్రదేశ్' : 'AP';
        }
        return l === 'te' ? 'జాతీయ' : 'National';
    }

    function findSchemeInCatalog(schemeOrName) {
        if (!schemeOrName) return null;
        if (typeof schemeOrName === 'object') return schemeOrName;
        if (!window.schemesCatalog) return { name: schemeOrName };
        if (window.schemesCatalog[schemeOrName]) {
            return Object.assign({ name: schemeOrName }, window.schemesCatalog[schemeOrName]);
        }
        for (const key in window.schemesCatalog) {
            const item = window.schemesCatalog[key];
            if (key === schemeOrName || item.telugu_name === schemeOrName || item.name === schemeOrName) {
                return Object.assign({ name: key }, item);
            }
        }
        return { name: schemeOrName };
    }

    // Central Scheme Name Resolver
    function getLocalizedSchemeName(schemeOrName, lang) {
        if (!schemeOrName) return '';
        const l = lang || currentLang;
        const scheme = findSchemeInCatalog(schemeOrName);
        if (l === 'en') {
            return scheme.name || scheme.scheme_name || (typeof schemeOrName === 'string' ? schemeOrName : '');
        }
        return scheme.telugu_name || scheme.name || scheme.scheme_name || (typeof schemeOrName === 'string' ? schemeOrName : '');
    }

    // Central Scheme Subtitle Resolver
    function getLocalizedSchemeSubtitle(schemeOrName, lang) {
        if (!schemeOrName) return '';
        const l = lang || currentLang;
        const scheme = findSchemeInCatalog(schemeOrName);
        if (l === 'en') {
            // In English mode, show localized category (NO TELUGU)
            return scheme.category ? translateCategory(scheme.category, 'en') : '';
        }
        // In Telugu mode, show English name as secondary reference
        return scheme.name || scheme.scheme_name || (typeof schemeOrName === 'string' ? schemeOrName : '');
    }

    // Central Scheme Description Resolver
    function getLocalizedSchemeDescription(schemeOrName, lang) {
        if (!schemeOrName) return '';
        const l = lang || currentLang;
        const scheme = findSchemeInCatalog(schemeOrName);
        if (l === 'en') {
            return scheme.english_description || scheme.simplified?.description || scheme.simplified?.benefits || '';
        }
        return scheme.telugu_description || scheme.telugu?.description || scheme.telugu?.benefits || '';
    }

    // Microphone error localization
    function getLocalizedMicError(errorType, lang) {
        const l = lang || currentLang;
        const err = (errorType || '').toLowerCase();
        if (err.includes('not-allowed') || err.includes('permission') || err.includes('denied')) {
            return t('voiceErrNotAllowed', null, l);
        }
        if (err.includes('no-speech')) {
            return t('voiceErrNoSpeech', null, l);
        }
        if (err.includes('audio-capture')) {
            return t('voiceErrAudioCapture', null, l);
        }
        if (err.includes('network')) {
            return t('voiceErrNetwork', null, l);
        }
        if (err.includes('aborted')) {
            return t('voiceErrAborted', null, l);
        }
        return t('voiceErrGeneric', { error: errorType || 'unknown' }, l);
    }

    // Set active language and apply across DOM
    function setLang(lang) {
        if (lang !== 'te' && lang !== 'en') return;
        currentLang = lang;
        try {
            const storage = (typeof window !== 'undefined' && window.localStorage) ? window.localStorage : (typeof localStorage !== 'undefined' ? localStorage : null);
            if (storage) {
                storage.setItem(STORAGE_KEY, lang);
                storage.setItem('smartgov_language', lang);
            }
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
        initLanguage: initLanguage,
        t: t,
        translateCategory: translateCategory,
        translateLevel: translateLevel,
        getLocalizedSchemeName: getLocalizedSchemeName,
        getLocalizedSchemeSubtitle: getLocalizedSchemeSubtitle,
        getLocalizedSchemeDescription: getLocalizedSchemeDescription,
        getLocalizedMicError: getLocalizedMicError,
        applyStaticTranslations: applyStaticTranslations,
        TRANSLATIONS: TRANSLATIONS,
        CATEGORIES: CATEGORIES
    };

    // Shorthand helpers
    window.t = t;
    window.getLang = getLang;
    window.setLang = setLang;
    window.getLocalizedSchemeName = getLocalizedSchemeName;
    window.getLocalizedSchemeSubtitle = getLocalizedSchemeSubtitle;
    window.getLocalizedSchemeDescription = getLocalizedSchemeDescription;
    window.getLocalizedMicError = getLocalizedMicError;

})();
