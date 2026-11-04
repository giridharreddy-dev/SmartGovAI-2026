"""Official-source decisions for the offline catalog rebuild."""

from services.scheme_revisions import document_id

PMJAY = "Ayushman Bharat PM-JAY (National Health Cover)"
NPCBVI = "National Programme for Control of Blindness (NPCBVI)"
DIALYSIS = "Pradhan Mantri National Dialysis Programme"
PMMVY = "Pradhan Mantri Matru Vandana Yojana (PMMVY)"
AP_HEALTH = "Dr. NTR Vaidya Seva (AP Cashless Hospital Care)"
PMJAY_MANUAL = "https://nha.gov.in/img/resources/Operation%20Manual%20for%20AB%20PM-JAY.pdf"
PMJAY_SENIORS = "https://nha.gov.in/img/resources/English_FAQs_related_to_the_benefits_for_senior_citizens.pdf"
EYE_GUIDANCE = "https://dghs.mohfw.gov.in/opthalmology-division.php"
DIALYSIS_GUIDANCE = "https://www.nhm.gov.in/New_Updates_2018/PMNDP/Guidelines_for_PMNDP.pdf"
MATERNITY_GUIDANCE = "https://www.wcd.gov.in/offerings/pradhan-mantri-matru-vandana-yojana"
AP_GUIDANCE = "https://hmfw.ap.gov.in/ntr-aarogyaseva-org.aspx"

PMJAY_DOCUMENT_NOTE = {
    "en": "Bring Aadhaar or a government photo ID accepted by your state, and a ration card or accepted family ID. If you do not have an Ayushman Card, ask the Ayushman Mitra desk at an empanelled hospital to start verification. The card is issued after approval. The separate 70+ enrolment route requires Aadhaar-based e-KYC.",
    "te": "ఆధార్ లేదా మీ రాష్ట్రం అంగీకరించే ప్రభుత్వ ఫోటో గుర్తింపు పత్రం, అలాగే రేషన్ కార్డు లేదా అంగీకరించిన కుటుంబ గుర్తింపు పత్రం తీసుకురండి. ఆయుష్మాన్ కార్డు లేకపోతే, పథకంలో నమోదైన ఆసుపత్రిలోని ఆయుష్మాన్ మిత్ర సహాయ కేంద్రంలో ధృవీకరణ ప్రారంభించమని అడగండి. ఆమోదం తర్వాత కార్డు జారీ అవుతుంది. 70 ఏళ్లు పైబడిన వారి ప్రత్యేక నమోదుకు ఆధార్ ఆధారిత ఈ-కేవైసీ అవసరం.",
}
NPCBVI_DOCUMENT_NOTE = {
    "en": "The national programme guidance does not specify a universal Aadhaar requirement or list of alternative IDs. Ask the treating eye facility which identification it accepts for registration.",
    "te": "జాతీయ కార్యక్రమ మార్గదర్శకాల్లో ఆధార్ అందరికీ తప్పనిసరి అని లేదా ప్రత్యామ్నాయ గుర్తింపు పత్రాల జాబితా ఇవ్వలేదు. నమోదుకు ఏ గుర్తింపు పత్రాలను అంగీకరిస్తారో చికిత్స అందించే నేత్ర వైద్య కేంద్రాన్ని అడగండి.",
}

DOCUMENT_REVIEWS = {
    PMJAY: {
        document_id("Ayushman Card"): {
            "status": "optional_at_initial_verification", "mandatory": False, "verification_status": "verified",
            "source_url": PMJAY_MANUAL,
        },
    },
    NPCBVI: {
        document_id("Aadhaar Card"): {
            "status": "facility_specific", "mandatory": None, "verification_status": "official_source_unspecified",
            "source_url": EYE_GUIDANCE,
        },
    },
}
DOCUMENT_NOTES = {PMJAY: PMJAY_DOCUMENT_NOTE, NPCBVI: NPCBVI_DOCUMENT_NOTE}


def component(parent, id_, en, te, summary_en, summary_te, source_url):
    return parent, {
        "id": id_, "title": {"en": en, "te": te},
        "summary": {"en": summary_en, "te": summary_te}, "source_url": source_url,
    }


# Only entries with an explicit programme relationship in the cited guidance.
COMPONENT_REVIEWS = {
    "Pradhan Mantri National Dialysis Programme - Hemodialysis": component(
        DIALYSIS, "haemodialysis", "Haemodialysis", "హీమోడయాలసిస్",
        "The national programme includes haemodialysis at dialysis centres. Ask your treating team about a referral and local availability.",
        "జాతీయ కార్యక్రమంలో డయాలసిస్ కేంద్రాల్లో హీమోడయాలసిస్ సేవలు ఉన్నాయి. రిఫరల్ మరియు స్థానికంగా అందుబాటులో ఉన్న సేవల గురించి వైద్య బృందాన్ని అడగండి.",
        DIALYSIS_GUIDANCE,
    ),
    "Pradhan Mantri National Dialysis Programme - Peritoneal Dialysis": component(
        DIALYSIS, "peritoneal-dialysis", "Peritoneal dialysis", "పెరిటోనియల్ డయాలసిస్",
        "The national programme includes peritoneal dialysis. Ask your treating team whether it is appropriate and available locally.",
        "జాతీయ కార్యక్రమంలో పెరిటోనియల్ డయాలసిస్ కూడా ఉంది. అది మీకు అనుకూలమా, స్థానికంగా అందుబాటులో ఉందా అని వైద్య బృందాన్ని అడగండి.",
        DIALYSIS_GUIDANCE,
    ),
    "PMMVY Scheme Second Child Financial Assistance": component(
        PMMVY, "second-child-girl", "Second-child benefit for a girl", "రెండో సంతానంగా ఆడపిల్లకు ప్రయోజనం",
        "PMMVY 2.0 covers an eligible woman's second living child if the child is a girl. Check the ministry's conditions before applying.",
        "పీఎంఎంవీవై 2.0లో అర్హత ఉన్న మహిళకు రెండో సంతానం ఆడపిల్ల అయితే ప్రయోజనం వర్తిస్తుంది. దరఖాస్తు చేసే ముందు మంత్రిత్వ శాఖ నిబంధనలు చూడండి.",
        MATERNITY_GUIDANCE,
    ),
    "Pradhan Mantri National Health Protection Mission - Senior Citizen Cover": component(
        PMJAY, "senior-citizen-70-plus", "Senior citizen enrolment (70+)", "70 ఏళ్లు పైబడిన వారి నమోదు",
        "NHA describes a separate enrolment route for people aged 70 or older, with Aadhaar-based e-KYC and a distinct Ayushman Card.",
        "70 ఏళ్లు లేదా అంతకంటే ఎక్కువ వయస్సు ఉన్నవారికి ఆధార్ ఆధారిత ఈ-కేవైసీతో ప్రత్యేక నమోదు, ప్రత్యేక ఆయుష్మాన్ కార్డు ఉంటాయని జాతీయ ఆరోగ్య ప్రాధికార సంస్థ తెలిపింది.",
        PMJAY_SENIORS,
    ),
    "AP Free Cochlear Implant Scheme (Child Hearing Restoration)": component(
        AP_HEALTH, "cochlear-implant", "Cochlear implant services for eligible children", "అర్హత ఉన్న పిల్లలకు కాక్‌లియర్ ఇంప్లాంట్ సేవలు",
        "Andhra Pradesh lists a cochlear implant programme under Dr. NTR Vaidya Seva. Ask the scheme help desk about current assessment and referral requirements.",
        "ఆంధ్రప్రదేశ్ ప్రభుత్వం డాక్టర్ ఎన్టీఆర్ వైద్య సేవలో కాక్‌లియర్ ఇంప్లాంట్ కార్యక్రమాన్ని పేర్కొంది. తాజా పరీక్ష, రిఫరల్ అవసరాల గురించి పథకం సహాయ కేంద్రాన్ని అడగండి.",
        AP_GUIDANCE,
    ),
}
