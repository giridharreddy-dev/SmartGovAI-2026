"""Extract source passages and explicitly labeled fields into a pending draft."""

import re

from services.scheme_operations import Application, Benefits, Document, Eligibility, SchemeOperations, Text

BLOCK_PATTERNS = {
    "eligibility": r"\beligib\w*\b|\bincome ceiling\b|\bage limit\b|\bexclusions?\b|అర్హత|ఆదాయ పరిమితి|వయోపరిమితి",
    "required_documents": r"\b(?:required documents|documents required|must submit|must provide proof)\b|అవసరమైన పత్రాలు|సమర్పించాల్సిన పత్రాలు",
    "benefits": r"\b(?:coverage|financial assistance|subsidy|grant of|cashless|instal+l?ments?)\b|ఆర్థిక సహాయం|రాయితీ|వాయిదా|బీమా",
    "application_process": r"\b(?:apply online|how to apply|application process|register on|submit an application|nodal agency)\b|దరఖాస్తు విధానం|దరఖాస్తు చేసుకోవాలి|నోడల్ సంస్థ",
}
LABELS = {
    "eligibility": {
        "age_range": ("age range", "age limit", "వయోపరిమితి"),
        "income_ceiling": ("income ceiling", "income limit", "ఆదాయ పరిమితి"),
        "residence": ("residence", "domicile", "నివాసం"),
        "target_group": ("target group", "లక్ష్య వర్గం"),
    },
    "benefits": {
        "coverage_amount": ("coverage amount", "సహాయం మొత్తం"),
        "coverage_type": ("coverage type", "సహాయం రకం"),
        "subsidy_percentage": ("subsidy percentage", "రాయితీ శాతం"),
        "disbursement": ("disbursement", "చెల్లింపు విధానం"),
    },
    "application_process": {
        "mode": ("application mode", "దరఖాస్తు విధానం"),
        "nodal_agency": ("nodal agency", "నోడల్ సంస్థ"),
        "offline_office": ("offline office", "దరఖాస్తు కార్యాలయం"),
        "verification": ("verification", "ధ్రువీకరణ"),
    },
}


def _labeled_fields(bodies, labels):
    fields = {}
    for key, aliases in labels.items():
        values = {}
        for language, body in bodies.items():
            pattern = "|".join(map(re.escape, aliases))
            matches = re.findall(rf"^[ \t]*(?:{pattern})[ \t]*[:：][ \t]*([^\n]+)$", body, re.I | re.M)
            matches = {match.strip() for match in matches if match.strip()}
            if len(matches) == 1:
                value = matches.pop()
                if len(value.split()) <= 25:
                    values[language] = value
        if values:
            fields[key] = Text(**values)
    return fields


def _labeled_documents(bodies):
    # Separate only explicit, short lists. Alternative or conditional
    # requirements stay in the source passages for a reviewer to interpret.
    for lang, body in bodies.items():
        lists = re.findall(
            r"^(?:required documents|documents required|అవసరమైన పత్రాలు)\s*[:：]\s*([^\n]+)$",
            body, re.I | re.M,
        )
        if len(set(lists)) != 1:
            continue
        text = lists[0]
        if len(text.split()) > 25 or re.search(
            r"\b(?:or|any|if|where|applicable|optional|none|nil|refer|see|no documents|not required)\b"
            r"|లేదా|వర్తిస్తే|అవసరం లేదు", text, re.I,
        ):
            continue
        names = re.split(r"[,;]|\s+(?:and|మరియు)\s+", text)
        names = [name.strip(" .") for name in names]
        if all(name and len(name.split()) <= 8 for name in names):
            return [Document(name=Text(**{lang: name}), mandatory=True) for name in names]
    return []


def extract_operations(articles):
    # Only official article bodies feed these blocks. A machine translation
    # of the introduction is never evidence for a requirement.
    bodies = {lang: articles.get(lang, {}).get("article_body_text", "") for lang in ("en", "te")}
    passages = {block: [] for block in BLOCK_PATTERNS}
    for lang, body in bodies.items():
        for block, pattern in BLOCK_PATTERNS.items():
            for line in body.splitlines():
                match = re.search(pattern, line, re.I)
                if match:
                    # Preserve nearby context even when the matched term is
                    # later in a long paragraph.
                    words = line.split()
                    start = max(0, len(line[:match.start()].split()) - 6)
                    passages[block].append({
                        "language": lang, "text": " ".join(words[start:start + 25]),
                        "url": articles[lang]["url"],
                    })
                if sum(item["language"] == lang for item in passages[block]) == 2:
                    break
    return SchemeOperations(
        eligibility=Eligibility(**_labeled_fields(bodies, LABELS["eligibility"])),
        required_documents=_labeled_documents(bodies),
        benefits=Benefits(**_labeled_fields(bodies, LABELS["benefits"])),
        application_process=Application(**_labeled_fields(bodies, LABELS["application_process"])),
    ), passages
