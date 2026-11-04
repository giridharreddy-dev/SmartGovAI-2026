"""Extract short, attributed review excerpts from official PIB release pages."""

import re
from html.parser import HTMLParser
from datetime import datetime
from urllib.parse import parse_qs, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, build_opener

HOSTS = {"pib.gov.in", "www.pib.gov.in"}
PAGE_LIMIT = 1_500_000


def release_id(url):
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError:
        return None
    if (parts.scheme != "https" or parts.hostname not in HOSTS or port not in {None, 443} or parts.username or parts.password
            or parts.path.lower() not in {"/pressreleasepage.aspx", "/pressreleaseiframepage.aspx"}):
        return None
    parameters = {key.lower(): values for key, values in parse_qs(parts.query).items()}
    value = parameters.get("prid", [""])[0]
    return value if re.fullmatch(r"[0-9]+", value) else None


class _ReleasePage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.body_depth = 0
        self.language_depth = 0
        self.paragraphs = []
        self.block = None
        self.href = None
        self.label = []
        self.telugu_url = None
        self.body_text = []
        self.metadata = {}
        self.metadata_field = None
        self.ignored = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"script", "style"}:
            self.ignored = tag
            return
        if tag == "div":
            if self.body_depth or attrs.get("id") == "pibReleaseBody":
                self.body_depth += 1
            if self.language_depth or "ReleaseLang" in (attrs.get("class") or "").split():
                self.language_depth += 1
            if attrs.get("id") in {"MinistryName", "PrDateTime"}:
                self.metadata_field = attrs["id"]
                self.metadata[self.metadata_field] = []
        if self.body_depth and tag in {"p", "li", "tr", "br", "h2", "h3"}:
            self.body_text.append("\n")
        if self.body_depth and tag in {"p", "li"}:
            self.finish_block()
            self.block = []
        if self.body_depth and tag == "br" and self.block is not None:
            self.block.append(" ")
        if self.language_depth and tag == "a":
            self.href = attrs.get("href")
            self.label = []

    def finish_block(self):
        if self.block is not None:
            text = " ".join("".join(self.block).split())
            if text:
                self.paragraphs.append(text)
            self.block = None

    def handle_endtag(self, tag):
        if self.ignored == tag:
            self.ignored = None
            return
        if self.body_depth and tag in {"p", "li"}:
            self.finish_block()
        if tag == "div":
            self.metadata_field = None
            if self.body_depth:
                self.body_depth -= 1
                if not self.body_depth:
                    self.finish_block()
            if self.language_depth:
                self.language_depth -= 1
        if tag == "a" and self.href is not None:
            if "".join(self.label).strip().casefold() in {"telugu", "తెలుగు"}:
                self.telugu_url = self.href
            self.href = None

    def handle_data(self, data):
        if self.ignored:
            return
        if self.body_depth:
            self.body_text.append(data)
        if self.metadata_field:
            self.metadata[self.metadata_field].append(data)
        if self.body_depth and self.block is not None:
            self.block.append(data)
        if self.href is not None:
            self.label.append(data)


def parse_article(html, url, language):
    page = _ReleasePage()
    page.feed(html)
    page.close()
    for paragraph in page.paragraphs:
        letters = [character for character in paragraph if character.isalpha()]
        words = paragraph.split()
        matching = sum(
            ("\u0c00" <= character <= "\u0c7f") if language == "te" else character.isascii()
            for character in letters
        )
        if len(words) >= 8 and letters and matching >= len(letters) * 0.65:
            posted_text = " ".join(page.metadata.get("PrDateTime", []))
            stamp = re.search(r"\b\d{1,2} [A-Z]{3} \d{4} \d{1,2}:\d{2}\s*[AP]M\b", posted_text, re.I)
            posted = None
            if stamp:
                try:
                    posted = datetime.strptime(re.sub(r"\s+(?=[AP]M$)", "", stamp[0].upper()), "%d %b %Y %I:%M%p").isoformat()
                except ValueError:
                    pass
            article = {
                "excerpt": " ".join(words[:25]) + ("…" if len(words) > 25 else ""),
                "translation_source": " ".join(words[:100]),
                "article_body_text": "\n".join(" ".join(line.split()) for line in "".join(page.body_text).splitlines() if line.strip()),
                "url": url,
                "ministry": " ".join("".join(page.metadata.get("MinistryName", [])).split()),
                "posted_at_ist": posted,
            }
            return article, urljoin(url, page.telugu_url) if page.telugu_url else None
    return None, urljoin(url, page.telugu_url) if page.telugu_url else None


def parse_release(html, url, language):
    article, link = parse_article(html, url, language)
    return article["excerpt"] if article else None, link


class _PIBRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if release_id(newurl) != release_id(req.full_url):
            raise ValueError("PIB redirected to a different release.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _fetch(url):
    if not release_id(url):
        raise ValueError("Only official PIB release URLs are supported.")
    with build_opener(_PIBRedirect()).open(url, timeout=8) as response:
        payload = response.read(PAGE_LIMIT + 1)
        if len(payload) > PAGE_LIMIT:
            raise ValueError("The PIB release exceeded the expected page size.")
        if release_id(response.url) != release_id(url):
            raise ValueError("PIB returned a different release.")
        return payload.decode(response.headers.get_content_charset() or "utf-8", errors="replace")


def release_excerpts(prid):
    url = f"https://www.pib.gov.in/PressReleasePage.aspx?PRID={prid}&lang=1&reg=48"
    english, telugu_link = parse_article(_fetch(url), url, "en")
    result = {}
    if english:
        result["en"] = english
    if telugu_link and release_id(telugu_link):
        try:
            telugu = regional_article(telugu_link)
        except (OSError, ValueError):
            telugu = None
        if telugu:
            result["te"] = dict(telugu, match_method="pib_link")
    return result


def regional_article(url):
    article, _ = parse_article(_fetch(url), url, "te")
    return article
