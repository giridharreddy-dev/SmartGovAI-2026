#!/usr/bin/env python3
"""Enhance schemes_complex.json with new fields for trust, eligibility, documents, local help."""

import json
import os
from datetime import datetime

schemes_enhancements = {
    "Dr. NTR Vaidya Seva (AP Cashless Hospital Care)": {
        "last_updated": "2026-06-03",
        "official_website": "https://apfinance.gov.in/",
        "contact_office": "District Health Office, Andhra Pradesh",
        "eligibility_confirmation": "Hospital Aarogya Mithra / Help Desk",
        "eligibility_questions": [
            {"question_te": "మీరు AP లో బీపీఎల్ కుటుంబానికి చెందుతున్నారా?", "question_en": "Are you from a BPL family in AP?", "weight": "high"},
            {"question_te": "నెట్‌వర్క్ ఆసుపత్రిలో చికిత్స అవసరమైనదా?", "question_en": "Do you need hospital treatment?", "weight": "high"},
            {"question_te": "ఆధార్ లేదా రేషన్ కార్డు ఉందా?", "question_en": "Do you have Aadhaar or ration card?", "weight": "medium"}
        ],
        "required_documents": [
            {"name": "Aadhaar", "name_te": "ఆధార్ కార్డు", "optional": False},
            {"name": "Ration Card / Health Card", "name_te": "రేషన్ కార్డు / ఆరోగ్య కార్డు", "optional": False},
            {"name": "Phone Number", "name_te": "ఫోన్ నంబర్", "optional": False},
            {"name": "Medical Reports", "name_te": "వైద్య రిపోర్టులు", "optional": True}
        ],
        "local_help_locations": {
            "phc": "Government PHC in your mandal",
            "chc": "CHC (Community Health Centre) in your district",
            "hospital": "Network hospital listed for Dr. NTR Vaidya Seva",
            "office": "District Health Office",
            "contact": "Aarogya Mithra at any network hospital"
        }
    },
    "AP 108 Emergency Ambulance Service": {
        "last_updated": "2026-06-03",
        "official_website": "https://apfinance.gov.in/",
        "contact_office": "108 Emergency Command Centre, AP",
        "eligibility_confirmation": "Call 108 directly - no eligibility check needed",
        "eligibility_questions": [
            {"question_te": "ఇది అత్యవసర పరిస్థితి?", "question_en": "Is this an emergency?", "weight": "critical"},
            {"question_te": "అంబులెన్స్ సేవ కావాలనుకుంటున్నారా?", "question_en": "Do you need ambulance?", "weight": "critical"}
        ],
        "required_documents": [
            {"name": "None required", "name_te": "ఏది అవసరం లేదు", "optional": True}
        ],
        "local_help_locations": {
            "ambulance": "Call 108 from anywhere",
            "hospital": "Nearest government hospital will receive patient",
            "contact": "108 (24/7)"
        }
    },
    "AP 104 Mobile Medical Units": {
        "last_updated": "2026-06-03",
        "official_website": "https://apfinance.gov.in/",
        "contact_office": "PHC/ASHA Worker in your village",
        "eligibility_confirmation": "ASHA / ANM / Village Secretariat",
        "eligibility_questions": [
            {"question_te": "మీరు గ్రామీణ ప్రాంతంలో ఉన్నారా?", "question_en": "Are you in a rural area?", "weight": "high"},
            {"question_te": "104 యూనిట్ సందర్శన తేదీ మీకు తెలుసా?", "question_en": "Do you know the 104 visit date?", "weight": "medium"}
        ],
        "required_documents": [
            {"name": "Aadhaar", "name_te": "ఆధార్", "optional": True},
            {"name": "Old Prescriptions", "name_te": "పాత మందుల చీటి", "optional": True},
            {"name": "MCP Card (if pregnant)", "name_te": "MCP కార్డు (గర్భిణీ అయితే)", "optional": True}
        ],
        "local_help_locations": {
            "phc": "PHC in your mandal",
            "asha": "ASHA worker in your village",
            "anm": "ANM / Health Worker",
            "village_office": "Village Secretariat"
        }
    },
    "Ayushman Bharat PM-JAY (National Health Cover)": {
        "last_updated": "2026-06-03",
        "official_website": "https://nha.gov.in/PM-JAY",
        "contact_office": "PM-JAY Help Centre / Common Service Centre",
        "eligibility_confirmation": "CSC / PM-JAY Counter / Hospital",
        "eligibility_questions": [
            {"question_te": "మీరు పేద కుటుంబానికి చెందుతున్నారా?", "question_en": "Are you from a poor family?", "weight": "high"},
            {"question_te": "SECC జాబితాలో ఉన్నారా?", "question_en": "Are you listed in SECC data?", "weight": "high"},
            {"question_te": "రేషన్ కార్డు ఉందా?", "question_en": "Do you have ration card?", "weight": "medium"}
        ],
        "required_documents": [
            {"name": "Aadhaar", "name_te": "ఆధార్ కార్డు", "optional": False},
            {"name": "Ration Card", "name_te": "రేషన్ కార్డు", "optional": False},
            {"name": "Mobile Number", "name_te": "ఫోన్ నంబర్", "optional": False},
            {"name": "Medical Reports", "name_te": "వైద్య రిపోర్టులు", "optional": True}
        ],
        "local_help_locations": {
            "csc": "Common Service Centre (CSC)",
            "hospital": "Empanelled hospital with PM-JAY counter",
            "pm_jay_counter": "PM-JAY help desk at hospital",
            "district_office": "District PM-JAY coordination office"
        }
    },
    "Ayushman Arogya Mandir (Free Primary Health Care)": {
        "last_updated": "2026-06-03",
        "official_website": "https://aam.mohfw.gov.in/",
        "contact_office": "Nearest Ayushman Arogya Mandir / PHC / Sub-centre",
        "eligibility_confirmation": "Automatic - open to all",
        "eligibility_questions": [
            {"question_te": "మీకు ప్రాథమిక ఆరోగ్య సేవ అవసరమైనదా?", "question_en": "Do you need basic health care?", "weight": "high"},
            {"question_te": "మీ దగ్గరలో PHC లేదా సబ్‌సెంటర్ ఉందా?", "question_en": "Is there a PHC/Sub-centre near you?", "weight": "high"}
        ],
        "required_documents": [
            {"name": "Aadhaar (optional)", "name_te": "ఆధార్ (ఐచ్ఛికం)", "optional": True},
            {"name": "Old Prescriptions", "name_te": "పాత చీటులు", "optional": True}
        ],
        "local_help_locations": {
            "aap_mandir": "Ayushman Arogya Mandir",
            "phc": "PHC (Primary Health Centre)",
            "sub_centre": "Sub-centre in your village",
            "health_worker": "ASHA / ANM health worker"
        }
    },
    "eSanjeevani National Telemedicine Service": {
        "last_updated": "2026-06-03",
        "official_website": "https://esanjeevani.mohfw.gov.in/",
        "contact_office": "PHC / Health Centre / Online Portal",
        "eligibility_confirmation": "Automatic - for anyone with phone/internet",
        "eligibility_questions": [
            {"question_te": "ఫోన్ లేదా ఇంటర్నెట్ కనెక్షన్ ఉందా?", "question_en": "Do you have phone or internet?", "weight": "high"},
            {"question_te": "డాక్టర్ సలహా చाहते हैं?", "question_en": "Do you want doctor advice?", "weight": "high"}
        ],
        "required_documents": [
            {"name": "Mobile Number", "name_te": "ఫోన్ నంబర్", "optional": False},
            {"name": "Aadhaar (optional)", "name_te": "ఆధార్ (ఐచ్ఛికం)", "optional": True}
        ],
        "local_help_locations": {
            "online_portal": "https://esanjeevani.mohfw.gov.in/",
            "phc": "PHC for teleconsultation",
            "health_centre": "Health and Wellness Centre"
        }
    },
    "Janani Shishu Suraksha Karyakram (Free Delivery Care)": {
        "last_updated": "2026-06-03",
        "official_website": "https://nhm.gov.in/",
        "contact_office": "Government Hospital / PHC",
        "eligibility_confirmation": "Hospital / ANM / ASHA Worker",
        "eligibility_questions": [
            {"question_te": "గర్భిణీ స్త్రీ లేదా నవజాత శిశువు?", "question_en": "Pregnant woman or newborn baby?", "weight": "critical"},
            {"question_te": "ప్రసవానికి సహాయం కావాలనుకుంటున్నారా?", "question_en": "Need delivery support?", "weight": "critical"}
        ],
        "required_documents": [
            {"name": "MCP Card", "name_te": "MCP కార్డు", "optional": False},
            {"name": "Aadhaar", "name_te": "ఆధార్", "optional": False},
            {"name": "Hospital Records", "name_te": "ఆసుపత్రి రిపోర్టులు", "optional": True}
        ],
        "local_help_locations": {
            "hospital": "Government hospital / PHC with delivery unit",
            "asha": "ASHA worker in your village",
            "anm": "ANM (Auxiliary Nurse Midwife)",
            "health_centre": "Nearest health centre"
        }
    },
    "Janani Suraksha Yojana (Safe Motherhood Cash Support)": {
        "last_updated": "2026-06-03",
        "official_website": "https://nhm.gov.in/",
        "contact_office": "Government Hospital / District Hospital",
        "eligibility_confirmation": "Hospital Finance Department",
        "eligibility_questions": [
            {"question_te": "గర్భిణీ స్త్రీ?", "question_en": "Are you pregnant?", "weight": "critical"},
            {"question_te": "ఆధార్ / రేషన్ కార్డు ఉందా?", "question_en": "Have Aadhaar or ration card?", "weight": "high"}
        ],
        "required_documents": [
            {"name": "Aadhaar", "name_te": "ఆధార్ కార్డు", "optional": False},
            {"name": "Ration Card", "name_te": "రేషన్ కార్డు", "optional": False},
            {"name": "MCP Card", "name_te": "MCP కార్డు", "optional": True},
            {"name": "Bank Account", "name_te": "బ్యాంక్ ఖాతా", "optional": False}
        ],
        "local_help_locations": {
            "hospital": "Government hospital",
            "district_office": "District Hospital Finance",
            "asha": "ASHA worker"
        }
    },
    "Mission Indradhanush / Universal Immunization": {
        "last_updated": "2026-06-03",
        "official_website": "https://mis.dghs.gov.in/",
        "contact_office": "PHC / Sub-centre / ASHA Worker",
        "eligibility_confirmation": "ASHA / ANM - free for all children",
        "eligibility_questions": [
            {"question_te": "0-5 సంవత్సరాల పిల్లవారు ఉన్నారా?", "question_en": "Do you have children aged 0-5 years?", "weight": "high"},
            {"question_te": "టీకాలు లేవటం అవసరమైనదా?", "question_en": "Do vaccines need to be given?", "weight": "high"}
        ],
        "required_documents": [
            {"name": "Immunization Card", "name_te": "టీకాकरण కార్డు", "optional": True},
            {"name": "Aadhaar (child)", "name_te": "ఆధార్ (పిల్లవాడు)", "optional": True}
        ],
        "local_help_locations": {
            "phc": "PHC",
            "sub_centre": "Sub-centre",
            "asha": "ASHA worker",
            "immunization_camp": "Village immunization camp"
        }
    },
    "Rashtriya Bal Swasthya Karyakram (Child Health Screening)": {
        "last_updated": "2026-06-03",
        "official_website": "https://nhm.gov.in/",
        "contact_office": "School / PHC / Health Worker",
        "eligibility_confirmation": "School screening / PHC automatic",
        "eligibility_questions": [
            {"question_te": "పిల్లవాడు 6-18 సంవత్సరాలు?", "question_en": "Is child aged 6-18 years?", "weight": "high"},
            {"question_te": "ఆరోగ్య పరీక్ష కావాలనుకుంటున్నారా?", "question_en": "Want health screening?", "weight": "medium"}
        ],
        "required_documents": [
            {"name": "School ID (if student)", "name_te": "పాఠశాల ID", "optional": True},
            {"name": "Aadhaar", "name_te": "ఆధార్", "optional": True}
        ],
        "local_help_locations": {
            "school": "School health program",
            "phc": "PHC screening camp",
            "health_worker": "ASHA / ANM"
        }
    },
    "Pradhan Mantri National Dialysis Programme": {
        "last_updated": "2026-06-03",
        "official_website": "https://nhm.gov.in/",
        "contact_office": "District Hospital / Dialysis Centre",
        "eligibility_confirmation": "Hospital Nephrologist / Dialysis Centre",
        "eligibility_questions": [
            {"question_te": "TB రోగి?", "question_en": "Is patient a TB patient?", "weight": "high"},
            {"question_te": "డయాలిసిస్ చికిత్స అవసరమైనదా?", "question_en": "Does patient need dialysis?", "weight": "critical"}
        ],
        "required_documents": [
            {"name": "Medical Diagnosis Report", "name_te": "వైద్య నిర్ధారణ", "optional": False},
            {"name": "Aadhaar", "name_te": "ఆధార్", "optional": True},
            {"name": "Doctor Referral", "name_te": "డాక్టర్ సిఫారిష్", "optional": False}
        ],
        "local_help_locations": {
            "district_hospital": "District Hospital",
            "dialysis_centre": "Empanelled dialysis centre",
            "nephrologist": "Nephrologist consultation"
        }
    },
    "Ni-kshay Poshan Yojana (TB Nutrition Support)": {
        "last_updated": "2026-06-03",
        "official_website": "https://nikshay.gov.in/",
        "contact_office": "TB Centre / PHC / District TB Officer",
        "eligibility_confirmation": "TB Centre / Hospital confirmed TB patient",
        "eligibility_questions": [
            {"question_te": "TB రోగి?", "question_en": "Are you a TB patient?", "weight": "critical"},
            {"question_te": "చికిత్స కోసం నమోదు చేసినారా?", "question_en": "Registered for TB treatment?", "weight": "critical"}
        ],
        "required_documents": [
            {"name": "TB Registration", "name_te": "TB నమోదు", "optional": False},
            {"name": "Aadhaar", "name_te": "ఆధార్", "optional": True},
            {"name": "Medical Certificate", "name_te": "వైద్య సర్టిఫికేట్", "optional": True}
        ],
        "local_help_locations": {
            "tb_centre": "TB Centre",
            "phc": "PHC with TB services",
            "district_tb": "District TB Officer",
            "nikshay": "https://nikshay.gov.in/"
        }
    }
}

def enhance_schemes():
    """Load schemes and add new fields."""
    with open(os.path.join('data', 'health.json'), 'r', encoding='utf-8') as f:
        schemes = json.load(f)
    
    for scheme_name, scheme_data in schemes.items():
        if scheme_name in schemes_enhancements:
            enhancements = schemes_enhancements[scheme_name]
            scheme_data.update(enhancements)
        else:
            # Add default enhancements for any missing schemes
            scheme_data["last_updated"] = "2026-06-03"
            scheme_data["official_website"] = scheme_data.get("source_url", "")
            scheme_data["contact_office"] = "Contact official source"
            scheme_data["eligibility_confirmation"] = "Verify at government office"
            scheme_data["eligibility_questions"] = []
            scheme_data["required_documents"] = []
            scheme_data["local_help_locations"] = {}
    
    # Save enhanced schemes
    with open(os.path.join('data', 'health.json'), 'w', encoding='utf-8') as f:
        json.dump(schemes, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Enhanced {len(schemes)} schemes with new fields")
    print("   - last_updated: Timestamp for information freshness")
    print("   - eligibility_questions: Yes/No flow for users")
    print("   - required_documents: Checklist items")
    print("   - local_help_locations: Where to find services")

if __name__ == '__main__':
    enhance_schemes()
