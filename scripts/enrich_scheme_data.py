"""
Script to enrich all 36 schemes in data/*.json with complete, faithful
Telugu and English descriptions, ensuring full symmetry and detail for Guided Mode Slide 1
and all localized views.
"""

import json
import os

DESCRIPTIONS = {
    # ── health.json (12 schemes) ──────────────────────────
    "Dr. NTR Vaidya Seva (AP Cashless Hospital Care)": {
        "telugu_description": "డా. ఎన్.టి.ఆర్ వైద్య సేవ అనేది ఆంధ్రప్రదేశ్ రాష్ట్రంలో దారిద్య్రరేఖకు దిగువన ఉన్న (బీపీఎల్) పేద కుటుంబాలకు ఉచిత మరియు నగదు రహిత ఆసుపత్రి చికిత్స అందించే ప్రధాన ఆరోగ్య రక్షణ పథకం. ఎంపిక చేసిన పెద్ద వ్యాధులు, శస్త్రచికిత్సలు మరియు చికిత్సల కోసం కుటుంబానికి ఏటా రూ. 25 లక్షల వరకు ఆర్థిక రక్షణ లభిస్తుంది. నెట్‌వర్క్ ఆసుపత్రులలోని ఆరోగ్య మిత్ర సహాయంతో రోగులు నేరుగా నగదు రహిత సేవలు పొందవచ్చు.",
        "english_description": "Dr. NTR Vaidya Seva is the flagship healthcare assurance scheme of the Government of Andhra Pradesh for below poverty line (BPL) families. It provides comprehensive cashless hospitalization, surgical interventions, and post-operative therapies up to Rs. 25 lakh per family per year for identified major illnesses through empanelled public and private network hospitals with on-site Aarogya Mithra assistance."
    },
    "AP 108 Emergency Ambulance Service": {
        "telugu_description": "108 అత్యవసర అంబులెన్స్ సేవ అనేది ఆంధ్రప్రదేశ్ వ్యాప్తంగా 24 గంటలు ఉచితంగా లభించే అత్యవసర స్పందన వైద్య వాహన సేవ. ప్రమాదాలు, గుండెపోటు, తీవ్ర అనారోగ్యం మరియు గర్భిణీ స్త్రీల అత్యవసర సమయాల్లో 108 కి డయల్ చేయడం ద్వారా ప్రాథమిక చికిత్సతో కూడిన అంబులెన్స్ త్వరితగతిన చేరుకుని సమీప ప్రభుత్వ లేదా నెట్‌వర్క్ ఆసుపత్రికి చేరుస్తుంది.",
        "english_description": "The AP 108 Emergency Ambulance Service is a 24/7 toll-free emergency medical response service operating throughout Andhra Pradesh. Dialing 108 dispatches a GPS-equipped emergency ambulance with trained emergency medical technicians and essential life support equipment to provide pre-hospital care and rapid transit to the nearest hospital."
    },
    "AP 104 Mobile Medical Units": {
        "telugu_description": "104 మొబైల్ మెడికల్ యూనిట్స్ (సంచార వైద్య వాహనాలు) గ్రామీణ మరియు మారుమూల ప్రాంతాల ప్రజల వద్దకే వెళ్లి ఉచిత ప్రాథమిక ఆరోగ్య సేవలు, దీర్ఘకాలిక వ్యాధుల పరీక్షలు (బీపీ, షుగర్), గర్భిణీల తనిఖీలు మరియు ఉచిత మందులను పంపిణీ చేసే సంచార వైద్య సేవా కార్యక్రమం.",
        "english_description": "The AP 104 Mobile Medical Units deliver doorstep primary healthcare services to rural and remote habitations on fixed monthly schedules. Medical teams provide free consultations, diagnostic screening for chronic diseases like hypertension and diabetes, maternal and child health checks, and free essential medicines."
    },
    "Ayushman Bharat PM-JAY (National Health Cover)": {
        "telugu_description": "ఆయుష్మాన్ భారత్ ప్రధాన మంత్రి జన్ ఆరోగ్య యోజన (PM-JAY) అనేది భారతదేశంలోని నిరుపేద కుటుంబాలకు ద్వితీయ మరియు తృతీయ స్థాయి ఆసుపత్రి చికిత్సల కోసం ఏటా కుటుంబానికి రూ. 5 లక్షల వరకు ఉచిత నగదు రహిత చికిత్స కల్పించే జాతీయ ఆరోగ్య రక్షణ పథకం.",
        "english_description": "Ayushman Bharat PM-JAY is the world's largest government-funded health assurance initiative, providing cashless coverage of up to Rs. 5 lakh per eligible family per year for secondary and tertiary care hospitalization across empanelled public and private hospitals nationwide."
    },
    "Ayushman Arogya Mandir (Free Primary Health Care)": {
        "telugu_description": "ఆయుష్మాన్ ఆరోగ్య మందిర్ (గతంలో హెల్త్ అండ్ వెల్నెస్ సెంటర్లు) గ్రామీణ మరియు పట్టణ ప్రాంతాల్లో ప్రజలకు ఉచిత ప్రాథమిక ఆరోగ్య సేవలు, సమగ్ర వ్యాధి నిర్ధారణ పరీక్షలు, ఉచిత మందులు, యోగా మరియు టెలిమెడిసిన్ ద్వారా స్పెషలిస్ట్ వైద్యుల సలహాలను చేరువ చేసే సమగ్ర ఆరోగ్య కేంద్రాలు.",
        "english_description": "Ayushman Arogya Mandir (formerly Health and Wellness Centres) deliver Comprehensive Primary Health Care (CPHC) directly within local communities, providing free essential medicines, diagnostic tests, screening for non-communicable diseases, maternal and child healthcare, and tele-consultations with specialist doctors."
    },
    "eSanjeevani National Telemedicine Service": {
        "telugu_description": "ఈ-సంజీవని అనేది కేంద్ర ప్రభుత్వ ఉచిత జాతీయ టెలిమెడిసిన్ పోర్టల్ మరియు యాప్. ప్రజలు తమ ఇంటి నుంచే లేదా సమీప హెల్త్ సెంటర్ ద్వారా వీడియో కాల్‌లో ప్రభుత్వ మరియు స్పెషలిస్ట్ వైద్యులను నేరుగా సంప్రదించి అధికారిక డిజిటల్ ప్రిస్క్రిప్షన్ పొందవచ్చు.",
        "english_description": "eSanjeevani is the national telemedicine platform of the Ministry of Health and Family Welfare, enabling citizens to connect with qualified doctors and medical specialists for free online video consultations, clinical advice, and digital prescriptions without traveling to distant hospitals."
    },
    "Janani Shishu Suraksha Karyakram (Free Delivery Care)": {
        "telugu_description": "జనని శిశు సురక్ష కార్యక్రమం (JSSK) ద్వారా ప్రభుత్వ ఆసుపత్రులలో ప్రసవించే గర్భిణీ స్త్రీలకు మరియు అనారోగ్యంతో ఉన్న నవజాత శిశువులకు (పుట్టిన 30 రోజుల వరకు) ఉచిత సాధారణ లేదా సిజేరియన్ డెలివరీ, ఉచిత మందులు, రక్త పరీక్షలు, ఆహారం మరియు ఉచిత అంబులెన్స్ ప్రయాణ సదుపాయం కల్పిస్తారు.",
        "english_description": "Janani Shishu Suraksha Karyakram (JSSK) guarantees completely cashless and free delivery care (including C-sections) for all pregnant women delivering in public health institutions, along with free treatment for sick infants up to 30 days of life, covering diagnostics, medications, blood, hospital diet, and transport."
    },
    "Janani Suraksha Yojana (Safe Motherhood Cash Support)": {
        "telugu_description": "జనని సురక్ష యోజన (JSY) అనేది సురక్షిత ప్రసవాలను ప్రోత్సహించడానికి మరియు మాతా-శిశు మరణాలను తగ్గించడానికి ప్రభుత్వ ఆసుపత్రులలో ప్రసవించిన పేద/బీపీఎల్ గర్భిణీ స్త్రీలకు నేరుగా వారి బ్యాంక్ ఖాతాలో నగదు ప్రోత్సాహకం (గ్రామీణ ప్రాంతాల్లో రూ. 1400, పట్టణ ప్రాంతాల్లో రూ. 1000) అందించే పథకం.",
        "english_description": "Janani Suraksha Yojana (JSY) is a safe motherhood scheme under the National Health Mission that promotes institutional deliveries among low-income pregnant women by providing direct cash financial assistance (Rs. 1,400 for rural areas, Rs. 1,000 for urban areas) transferred directly into the mother's bank account."
    },
    "Mission Indradhanush / Universal Immunization": {
        "telugu_description": "మిషన్ ఇంద్రధనుష్ మరియు సార్వత్రిక టీకాల కార్యక్రమం ద్వారా పిల్లలు మరియు గర్భిణీ స్త్రీలకు పోలియో, ధనుర్వాతం, డిఫ్తీరియా, క్షయ, హెపటైటిస్ బి, మీజిల్స్-రుబెల్లా వంటి 12 ప్రాణాంతక వ్యాధుల నుండి రక్షణ కల్పించేందుకు వయస్సు ప్రకారం పూర్తి ఉచిత టీకాలు మరియు వ్యాక్సిన్ కార్డు అందించబడతాయి.",
        "english_description": "Mission Indradhanush and the Universal Immunization Programme provide universal, free vaccination coverage against 12 life-threatening vaccine-preventable diseases for all pregnant women, infants, and children according to the national immunization schedule, complete with tracked immunization cards."
    },
    "Rashtriya Bal Swasthya Karyakram (Child Health Screening)": {
        "telugu_description": "రాష్ట్రీయ బాల స్వాస్థ్య కార్యక్రమం (RBSK) అనేది పుట్టినప్పటి నుండి 18 సంవత్సరాల వయస్సు వరకు ఉన్న పిల్లలకు జన్యుపరమైన లోపాలు, తీవ్ర వ్యాధులు, పోషకాహార లోపాలు మరియు ఎదుగుదల లోపాలను (4Ds) గుర్తించడానికి మొబైల్ హెల్త్ టీమ్‌ల ద్వారా అంగన్‌వాడీలు మరియు ప్రభుత్వ పాఠశాలల్లో ఉచిత స్క్రీనింగ్ మరియు ఉచిత రిఫరల్ చికిత్స అందించే పథకం.",
        "english_description": "Rashtriya Bal Swasthya Karyakram (RBSK) conducts systematic, free health screening for children from birth to 18 years in Anganwadi centres and government schools to detect the 4Ds (Defects at birth, Diseases, Deficiencies, and Development delays), arranging free surgical correction and early intervention."
    },
    "Pradhan Mantri National Dialysis Programme": {
        "telugu_description": "ప్రధాన మంత్రి జాతీయ డయాలిసిస్ కార్యక్రమం ద్వారా కిడ్నీ వైఫల్యంతో బాధపడుతున్న నిరుపేద/బీపీఎల్ రోగులకు జిల్లా కేంద్ర ఆసుపత్రులలోని ప్రత్యేక డయాలిసిస్ కేంద్రాలలో ఉచితంగా లేదా రాయితీపై హీమోడయాలసిస్ మరియు పెరిటోనియల్ డయాలిసిస్ సేవలను అందిస్తారు.",
        "english_description": "The Pradhan Mantri National Dialysis Programme provides free and subsidized life-sustaining hemodialysis and peritoneal dialysis services for poor and BPL patients suffering from end-stage renal disease (kidney failure) through dedicated dialysis units established in district hospitals."
    },
    "Ni-kshay Poshan Yojana (TB Nutrition Support)": {
        "telugu_description": "నిక్షయ్ పోషణ యోజన పథకం ద్వారా ప్రభుత్వంలో నమోదైన క్షయ (టీబీ) రోగులందరికీ చికిత్స కాలంలో పోషకాహార అవసరాల కోసం ప్రతి నెలా వారి బ్యాంక్ ఖాతాకు నేరుగా డీబీటీ (DBT) ద్వారా ఆర్థిక సహాయం జమ చేయబడుతుంది.",
        "english_description": "Ni-kshay Poshan Yojana is a direct benefit transfer (DBT) scheme under the National Tuberculosis Elimination Programme, providing monthly financial support directly into the bank accounts of all notified TB patients to fulfill their nutritional needs throughout the active treatment period."
    },

    # ── extra_schemes.json (18 schemes) ───────────────────
    "National Tobacco Control Programme (NTCP)": {
        "telugu_description": "జాతీయ పొగాకు నియంత్రణ పథకం (NTCP) అనేది పొగాకు, సిగరెట్లు, గుట్కా అలవాటు నుండి విముక్తి పొందాలనుకునే పౌరులకు జిల్లా ఆసుపత్రులలోని పొగాకు నివారణ కేంద్రాల (TCC) ద్వారా ఉచిత కౌన్సిలింగ్, బిహేవియరల్ థెరపీ మరియు ఉచిత నికోటిన్ గమ్స్/ప్యాచీలను అందించే కార్యక్రమం.",
        "english_description": "The National Tobacco Control Programme (NTCP) establishes Tobacco Cessation Centres (TCCs) in district hospitals to provide free de-addiction counseling, behavioral therapy, and free Nicotine Replacement Therapy (NRT gums and patches) to help individuals quit tobacco consumption."
    },
    "National Leprosy Eradication Programme (NLEP)": {
        "telugu_description": "జాతీయ కుష్టువ్యాధి నివారణ పథకం (NLEP) కుష్టువ్యాధిని ప్రారంభ దశలోనే గుర్తించి, ప్రాథమిక ఆరోగ్య కేంద్రాల ద్వారా ఉచిత మల్టీ-డ్రగ్ థెరపీ (MDT) మందుల పంపిణీ, వైకల్యాలు నివారించడానికి ఉచిత ఆపరేషన్లు మరియు పునరావాస సహాయాన్ని అందిస్తుంది.",
        "english_description": "The National Leprosy Eradication Programme (NLEP) delivers free Multi-Drug Therapy (MDT) blister packs across all primary health centres, provides free reconstructive surgery for deformities, and offers welfare support for patients diagnosed with leprosy."
    },
    "National Vector Borne Disease Control Programme (NVBDCP)": {
        "telugu_description": "జాతీయ దోమల ద్వారా సంక్రమించే వ్యాధుల నివారణ పథకం (NVBDCP) మలేరియా, డెంగ్యూ, చికెన్‌గున్యా, జపనీస్ ఎన్సెఫాలిటిస్ వంటి వ్యాధుల నివారణకు ఉచిత రక్త పరీక్షలు, ఉచిత మందులు మరియు స్థానిక ప్రాంతాల్లో క్రిమిసంహారక దోమతెరల (LLINs) పంపిణీని చేపడుతుంది.",
        "english_description": "The National Vector Borne Disease Control Programme (NVBDCP) provides free rapid diagnostic testing, free treatment medicines for Malaria, Dengue, and Chikungunya, and distributes Long-Lasting Insecticidal Nets (LLINs) in endemic rural areas to control vector transmission."
    },
    "National Programme for Control of Blindness (NPCBVI)": {
        "telugu_description": "జాతీయ అంధత్వ నివారణ పథకం (NPCBVI) అంధత్వాన్ని తగ్గించడానికి వృద్ధులకు ఉచిత శుక్లాల (క్యాటరాక్ట్) శస్త్రచికిత్సలు, ఇంట్రాఓక్యులర్ లెన్స్ అమరిక, పాఠశాల విద్యార్థులకు ఉచిత కంటి పరీక్షలు, ఉచిత కళ్ళజోళ్ల పంపిణీ మరియు కార్నియల్ అంధత్వానికి ఉచిత సేవలను అందిస్తుంది.",
        "english_description": "The National Programme for Control of Blindness and Visual Impairment (NPCBVI) provides free cataract surgeries with intraocular lens (IOL) implantation, free eye screenings in government schools, free prescription spectacles for children, and corneal transplantation support."
    },
    "National Oral Health Programme": {
        "telugu_description": "జాతీయ దంత ఆరోగ్య పథకం కమ్యూనిటీ హెల్త్ సెంటర్లు (CHC) మరియు జిల్లా ఆసుపత్రులలోని డెంటల్ యూనిట్ల ద్వారా పౌరులందరికీ ఉచిత దంత పరీక్షలు, పిప్పి పళ్ళు తీసివేయడం, పళ్ళు క్లీనింగ్, ఫిల్లింగ్ మరియు నోటి పరిశుభ్రత సంరక్షణ సేవలను అందిస్తుంది.",
        "english_description": "The National Oral Health Programme provides integrated, accessible oral healthcare services through dental clinics at CHCs and District Hospitals, offering free dental checkups, extractions, fillings, scaling, oral cancer screening, and oral hygiene education."
    },
    "Anaemia Mukt Bharat": {
        "telugu_description": "అనీమియా ముక్త్ భారత్ వ్యూహం ద్వారా గర్భిణీలు, పాలిచ్చే తల్లులు, కిశోర బాలికలు మరియు పిల్లల్లో రక్తహీనతను నివారించడానికి ఐరన్ మరియు ఫోలిక్ యాసిడ్ (IFA) మాత్రలు/సిరప్‌ల ఉచిత పంపిణీ, ఉచిత రక్తహీనత పరీక్షలు మరియు నట్టల నివారణ (డీవార్మింగ్) మాత్రలను అందిస్తారు.",
        "english_description": "Anaemia Mukt Bharat is an intensive national strategy to reduce anemia across vulnerable groups through routine Iron and Folic Acid (IFA) supplementation, bi-annual deworming with Albendazole, digital point-of-care hemoglobin testing, and nutritional counseling."
    },
    "Poshan Abhiyaan": {
        "telugu_description": "పోషణ్ అభియాన్ (జాతీయ పోషకాహార మిషన్) అంగన్‌వాడీ కేంద్రాల ద్వారా చిన్న పిల్లలు, గర్భిణీలు మరియు పాలిచ్చే తల్లులకు పౌష్టికాహారం, గ్రోత్ మానిటరింగ్, పోషక లోప నివారణ మరియు మహిళా సాధికారతకు సంబంధించిన సేవలను అందిస్తుంది.",
        "english_description": "POSHAN Abhiyaan (National Nutrition Mission) targets the reduction of stunting, wasting, and under-nutrition among young children, pregnant women, and lactating mothers through Anganwadi-based supplementary nutrition, growth tracking, and maternal health education."
    },
    "National AIDS Control Programme (NACP)": {
        "telugu_description": "జాతీయ ఎయిడ్స్ నియంత్రణ పథకం (NACP) ప్రభుత్వ ఆసుపత్రులలోని ICTC కేంద్రాల ద్వారా ఉచిత హెచ్‌ఐవీ పరీక్షలు, గోప్యమైన కౌన్సిలింగ్ మరియు ART కేంద్రాల ద్వారా జీవితాంతం ఉచిత యాంటీరెట్రోవైరల్ థెరపీ (ART) మందుల పంపిణీని అందిస్తుంది.",
        "english_description": "The National AIDS Control Programme (NACP) provides free and strictly confidential HIV testing and counseling at ICTC centres, free lifelong Anti-Retroviral Therapy (ART) medication, opportunistic infection management, and prevention of mother-to-child transmission."
    },
    "Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP)": {
        "telugu_description": "ప్రధాన మంత్రి భారతీయ జనౌషధి పరియోజన (PMBJP) ద్వారా జనౌషధి కేంద్రాలలో బ్రాండెడ్ మందులతో సమానమైన నాణ్యత కలిగిన జెనరిక్ మందులు, శానిటరీ ప్యాడ్‌లు మరియు వైద్య పరికరాలను 50% నుండి 90% తక్కువ ధరకు సామాన్య ప్రజలకు అందుబాటులో ఉంచుతారు.",
        "english_description": "Pradhan Mantri Bhartiya Janaushadhi Pariyojana (PMBJP) operates dedicated Jan Aushadhi Kendras to provide high-quality generic medicines, surgical consumables, and sanitary napkins at prices 50% to 90% lower than branded market alternatives."
    },
    "Ayushman Bharat Health Account (ABHA)": {
        "telugu_description": "ఆయుష్మాన్ భారత్ హెల్త్ అకౌంట్ (ABHA) అనేది ప్రతి పౌరుడికి 14 అంకెల ప్రత్యేక డిజిటల్ ఆరోగ్య గుర్తింపు సంఖ్యను అందిస్తుంది. దీని ద్వారా రోగి వైద్య రికార్డులు, ల్యాబ్ రిపోర్టులు మరియు ప్రిస్క్రిప్షన్‌లను డిజిటల్‌గా సురక్షితంగా నిల్వ చేసుకుని భారతదేశంలోని ఏ ఆసుపత్రిలోనైనా సులభంగా పంచుకోవచ్చు.",
        "english_description": "Ayushman Bharat Health Account (ABHA) creates a secure 14-digit digital health ID for citizens, enabling seamless, consent-based digital storage and sharing of personal medical records, prescriptions, and lab diagnostic reports across healthcare providers nationwide."
    },
    "National Rabies Control Programme (NRCP)": {
        "telugu_description": "జాతీయ రేబీస్ నియంత్రణ పథకం (NRCP) ద్వారా కుక్క, పిల్లి లేదా జంతువుల కాటుకు గురైన వారికి అన్ని ప్రభుత్వ ఆసుపత్రులు మరియు పీహెచ్‌సీలలో ప్రాణరక్షక యాంటీ-రేబీస్ వ్యాక్సిన్ (ARV) మరియు యాంటీ-రేబీస్ సీరంను పూర్తి ఉచితంగా అందిస్తారు.",
        "english_description": "The National Rabies Control Programme (NRCP) provides free Anti-Rabies Vaccines (ARV) and Rabies Immunoglobulin (RIG) post-exposure prophylaxis across all public health facilities to prevent fatal rabies infections following animal bites."
    },
    "National Programme for Prevention of Deafness (NPPCD)": {
        "telugu_description": "జాతీయ వినికిడి లోప నివారణ పథకం (NPPCD) ద్వారా వినికిడి సమస్యలు ఉన్న పిల్లలు మరియు వృద్ధులకు ఉచిత ఆడియోమెట్రీ పరీక్షలు, వినికిడి చికిత్సలు, ఉచిత శ్రవణ యంత్రాల (హియరింగ్ ఎయిడ్స్) పంపిణీ మరియు అవసరమైన వారికి శస్త్రచికిత్స సహాయాన్ని అందిస్తారు.",
        "english_description": "The National Programme for the Prevention and Control of Deafness (NPPCD) offers free hearing assessments, audiometry screenings, early intervention for hearing impairment, free distribution of hearing aids, and surgical referral for deafness."
    },
    "National Organ Transplant Programme (NOTP)": {
        "telugu_description": "జాతీయ అవయవ మార్పిడి పథకం (NOTP) ద్వారా అవయవ దానం చేయాలనుకునే దాతల నమోదు, అవయవ మార్పిడి అవసరమైన రోగుల వెయిటింగ్ లిస్ట్ నిర్వహణ మరియు పేద రోగులకు అవయవ మార్పిడి ప్రక్రియలో సహాయం అందించబడుతుంది.",
        "english_description": "The National Organ Transplant Programme (NOTP) manages ethical organ retrieval, donor registration, national organ sharing registries, and supports financial assistance for life-saving organ transplantations among disadvantaged patients."
    },
    "National Iodine Deficiency Disorders Control Programme (NIDDCP)": {
        "telugu_description": "జాతీయ అయోడిన్ లోప నివారణ పథకం (NIDDCP) గొంతువాపు (గాయిటర్), మానసిక ఎదుగుదల లోపాలు మరియు అయోడిన్ లోప సంబంధిత సమస్యలను నివారించడానికి అయోడైజ్డ్ ఉప్పు వాడకంపై అవగాహన మరియు ఉచిత అయోడిన్ స్థాయి పరీక్షలను నిర్వహిస్తుంది.",
        "english_description": "The National Iodine Deficiency Disorders Control Programme (NIDDCP) prevents goiter, cretinism, and cognitive impairments by ensuring 100% household access to adequately iodized salt and conducting community-level iodine deficiency surveillance."
    },
    "YSR Urban Health Clinics": {
        "telugu_description": "వైఎస్ఆర్ అర్బన్ హెల్త్ క్లినిక్స్ ఆంధ్రప్రదేశ్‌లోని మున్సిపాలిటీలు మరియు నగరాల్లోని పేదలు, మురికివాడల నివాసితుల సమీపంలో ఉచిత ఓపీడీ సేవలు, ప్రాథమిక పరీక్షలు, ఉచిత మందులు మరియు టెలిమెడిసిన్ ద్వారా ప్రత్యేక వైద్యుల సేవలను అందిస్తాయి.",
        "english_description": "YSR Urban Health Clinics provide comprehensive, accessible outpatient healthcare services to urban poor and slum populations across Andhra Pradesh towns and cities, featuring free consultations, diagnostic screenings, free medications, and telemedicine."
    },
    "AP Blood Bank Services": {
        "telugu_description": "ఆంధ్రప్రదేశ్ బ్లడ్ బ్యాంక్ సర్వీసెస్ రాష్ట్రంలోని ప్రభుత్వ ఆసుపత్రులు మరియు రెడ్‌క్రాస్ ద్వారా అవసరమైన రోగులకు (ప్రసవాలు, ప్రమాదాలు, తలసేమియా) స్వచ్ఛంద రక్తదానం ద్వారా సురక్షితమైన రక్తం మరియు రక్త భాగాలను నిరంతరం అందుబాటులో ఉంచుతుంది.",
        "english_description": "AP Blood Bank Services coordinate voluntary blood donation and testing to ensure 24/7 availability of safe, screened whole blood and blood components for pregnant women, trauma victims, and thalassemia patients across government blood banks."
    },
    "National TB Elimination Programme (NTEP)": {
        "telugu_description": "జాతీయ క్షయ నిర్మూలన పథకం (NTEP) ద్వారా ఉచిత సీబీ-నాట్ (CB-NAAT) కఫ పరీక్షలు, ఛాతీ ఎక్స్-రే, డ్రగ్ రెసిస్టెంట్ టీబీ పరీక్షలు మరియు సంపూర్ణ ఉచిత టీబీ మందుల కోర్సు (DOTS) అందించబడుతుంది.",
        "english_description": "The National TB Elimination Programme (NTEP) provides free advanced molecular diagnostics (CB-NAAT/Truenat), digital chest X-rays, free fixed-dose combination anti-TB medication courses under DOTS, and household contact screening."
    },
    "Integrated Child Development Services (ICDS)": {
        "telugu_description": "సమగ్ర శిశు అభివృద్ధి సేవల పథకం (ICDS) అంగన్‌వాడీ కేంద్రాల ద్వారా 6 సంవత్సరాల లోపు పిల్లలకు, గర్భిణీలకు మరియు బాలింతలకు పౌష్టికాహార భోజనం, ప్రీ-స్కూల్ విద్య, రోగనిరోధక టీకాలు మరియు క్రమం తప్పని ఆరోగ్య పరీక్షలను అందిస్తుంది.",
        "english_description": "Integrated Child Development Services (ICDS) provides early childhood care through Anganwadi centres, offering supplementary hot cooked nutrition, pre-school non-formal education, routine immunization monitoring, and maternal health support."
    },

    # ── national_and_ap_schemes.json (6 schemes) ──────────
    "Pradhan Mantri Surakshit Matritva Abhiyan (PMSMA)": {
        "telugu_description": "ప్రధానమంత్రి సురక్షిత మాతృత్వ అభియాన్ (PMSMA) కింద ప్రతి నెలా 9వ తేదీన ప్రభుత్వ ఆసుపత్రులు మరియు పీహెచ్‌సీలలో గర్భిణీ స్త్రీలకు (రెండవ, మూడవ త్రైమాసికంలో) స్పెషలిస్ట్ గైనకాలజిస్టుల ద్వారా ఉచిత సమగ్ర వైద్య పరీక్షలు, అల్ట్రాసౌండ్ మరియు మందులను అందిస్తారు.",
        "english_description": "Pradhan Mantri Surakshit Matritva Abhiyan (PMSMA) guarantees free, comprehensive antenatal checkups conducted by specialist gynecologists on the 9th of every month for pregnant women in their 2nd and 3rd trimesters across government health facilities."
    },
    "Pradhan Mantri Matru Vandana Yojana (PMMVY)": {
        "telugu_description": "ప్రధానమంత్రి మాతృ వందన యోజన (PMMVY) మొదటి సంతానం కోసం గర్భిణీలకు మరియు బాలింతలకు వేతన నష్టాన్ని భర్తీ చేయడానికి మరియు మెరుగైన పోషకాహారం కొరకు నేరుగా తల్లి బ్యాంక్ ఖాతాలో రూ. 5,000 నగదును రెండు విడతల్లో జమ చేసే పథకం.",
        "english_description": "Pradhan Mantri Matru Vandana Yojana (PMMVY) is a direct benefit transfer maternity incentive providing Rs. 5,000 in two installments into the mother's Aadhaar-linked bank account to support nutrition and partial wage compensation during first pregnancy."
    },
    "YSR Village Health Clinics": {
        "telugu_description": "వైఎస్ఆర్ విలేజ్ హెల్త్ క్లినిక్స్ ఆంధ్రప్రదేశ్‌లోని ప్రతి గ్రామ పంచాయతీ పరిధిలో 105 రకాల ఉచిత మందులు, 14 రకాల ఉచిత పరీక్షలు, మిడ్-లెవల్ హెల్త్ ప్రొవైడర్ (MLHP) సేవలు మరియు టెలిమెడిసిన్ ద్వారా వైద్యుల సంప్రదింపులను గ్రామంలోనే అందిస్తాయి.",
        "english_description": "YSR Village Health Clinics operate at the village secretariat level across Andhra Pradesh, delivering round-the-clock primary health services by Mid-Level Health Providers (MLHPs), 105 free essential medicines, 14 diagnostic tests, and specialist tele-consultations."
    },
    "AP Organ Donation Programme (Jeevandan)": {
        "telugu_description": "జీవన్‌దాన్ అవయవ దానం పథకం ఆంధ్రప్రదేశ్ ప్రభుత్వ పర్యవేక్షణలో బ్రెయిన్ డెడ్ వ్యక్తుల నుండి అవయవ దానాలను సమన్వయం చేస్తూ, కిడ్నీ, లివర్, గుండె వంటి అవయవాలు అవసరమైన నిరుపేద రోగులకు పారదర్శక వెయిటింగ్ లిస్ట్ ద్వారా అవయవ మార్పిడి సహాయాన్ని అందిస్తుంది.",
        "english_description": "The AP Jeevandan Cadaver Organ Donation Programme is the Andhra Pradesh government's nodal initiative regulating deceased organ donations, coordinating transparent allocation of kidneys, livers, hearts, and lungs to waitlisted patients in registered transplant centres."
    },
    "National Mental Health Programme (NMHP)": {
        "telugu_description": "జాతీయ మానసిక ఆరోగ్య పథకం (NMHP) జిల్లా ఆసుపత్రులలోని మానసిక ఆరోగ్య విభాగాల (DMHP) ద్వారా మానసిక ఒత్తిడి, ఆందోళన, డిప్రెషన్ మరియు మానసిక సమస్యలతో బాధపడే పౌరులకు ఉచిత కౌన్సిలింగ్, సైకియాట్రిస్ట్ చికిత్స మరియు ఉచిత మందులను అందిస్తుంది.",
        "english_description": "The National Mental Health Programme (NMHP) provides decentralized mental healthcare through District Mental Health Programme (DMHP) clinics, offering free psychiatric evaluations, clinical counseling, therapy, and free psychotropic medications."
    },
    "National Programme for Health Care of the Elderly (NPHCE)": {
        "telugu_description": "జాతీయ వృద్ధుల ఆరోగ్య సంరక్షణ పథకం (NPHCE) 60 ఏళ్లు పైబడిన వృద్ధులకు ప్రభుత్వ ఆసుపత్రులలో ప్రత్యేక వృద్ధుల ఓపీడీ కౌంటర్లు, ఉచిత ఫిజియోథెరపీ, వయస్సు సంబంధిత దీర్ఘకాలిక వ్యాధుల ఉచిత పరీక్షలు మరియు ఉచిత మందులను అందిస్తుంది.",
        "english_description": "The National Programme for Health Care of the Elderly (NPHCE) provides dedicated, accessible geriatric services for senior citizens aged 60+, including dedicated clinic queues, free chronic disease management, specialized physiotherapy, and mobility assistive devices."
    }
}

def enrich():
    files = ["data/health.json", "data/extra_schemes.json", "data/national_and_ap_schemes.json"]
    total_updated = 0
    
    for fpath in files:
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            
        for name, scheme in data.items():
            if name in DESCRIPTIONS:
                scheme["telugu_description"] = DESCRIPTIONS[name]["telugu_description"]
                scheme["english_description"] = DESCRIPTIONS[name]["english_description"]
                
                # Also ensure telugu.description and simplified.description are populated
                if "telugu" in scheme and isinstance(scheme["telugu"], dict):
                    scheme["telugu"]["description"] = DESCRIPTIONS[name]["telugu_description"]
                if "simplified" in scheme and isinstance(scheme["simplified"], dict):
                    scheme["simplified"]["description"] = DESCRIPTIONS[name]["english_description"]
                    
                total_updated += 1
                
        with open(fpath, "w", encoding="utf-8") as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)
            
        print(f"Updated {fpath} with enriched descriptions.")
        
    print(f"\nSuccessfully enriched {total_updated} / 36 schemes.")

if __name__ == "__main__":
    enrich()
