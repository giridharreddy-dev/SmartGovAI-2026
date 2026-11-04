from unittest.mock import patch

from flask import Flask
from flask_wtf.csrf import CSRFProtect

from app import app
from services.studio_narration import studio_audio_asset
from services.studio_search import SearchUnavailable
from studio import make_studio


def test_public_catalog_is_bilingual_cacheable_and_excludes_raw_content():
    client = app.test_client()
    result = client.get("/studio/catalog.json")
    assert result.status_code == 200
    assert result.cache_control.public and result.cache_control.max_age == 300
    entries = result.get_json()["schemes"]
    assert entries and len({entry["id"] for entry in entries}) == len(entries)
    assert any(entry["en"] and entry["te"] and entry["questions"] for entry in entries)
    assert all("original_complex_text" not in entry for entry in entries)
    assert all(not entry["source"]["url"] or entry["source"]["url"].startswith(("https://", "http://")) for entry in entries)
    assert client.get("/studio/catalog.json", headers={"If-None-Match": result.headers["ETag"]}).status_code == 304


def test_catalog_only_advertises_available_recordings_by_language(tmp_path):
    static = tmp_path / "static"
    server = Flask(__name__, static_folder=str(static))
    slug = "test-scheme"
    server.register_blueprint(make_studio(tmp_path, {"Test Scheme": {"slug": slug}}, []))
    client = server.test_client()

    def recordings():
        return client.get("/studio/catalog.json").get_json()["schemes"][0]["recordings"]

    assert recordings() == {}
    for language in ("te", "en"):
        path = static / studio_audio_asset(slug, language)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"ID3" + bytes(1024))
        urls = recordings()
        assert set(urls) == ({"te"} if language == "te" else {"te", "en"})
        assert f"/{slug}.{language}.mp3?v=" in urls[language]
        assert client.get(urls[language], headers={"Range": "bytes=0-2"}).data == b"ID3"


def test_meaning_search_uses_filtered_catalog_ids_and_handles_missing_model(tmp_path):
    server = Flask(__name__)
    server.config["SECRET_KEY"] = "search-test"
    CSRFProtect(server)
    schemes = {
        "Rural skills": {"slug": "skills", "sector": "employment", "level": "National",
                         "simplified": {"description": "Work training"}, "telugu": {"description": "వృత్తి శిక్షణ"}},
        "Housing": {"slug": "housing", "sector": "housing", "simplified": {"description": "Housing aid"}},
    }
    server.register_blueprint(make_studio(tmp_path, schemes, []))
    client = server.test_client()
    query = {"query": "గ్రామీణ యువతకు పని నేర్పే పథకం", "sector": "employment"}
    assert client.post("/studio/search", json=query).status_code == 400
    headers = {"X-CSRFToken": client.get("/studio/session").get_json()["csrfToken"]}
    assert client.post("/studio/search", json={"query": []}, headers=headers).status_code == 400
    with patch("studio.semantic_ids", return_value=["skills"]) as rank:
        response = client.post("/studio/search", json=query, headers=headers)
    assert response.get_json() == {"ids": ["skills"]}
    assert response.cache_control.no_store
    assert rank.call_args.args[-1] == {"skills"}
    with patch("studio.semantic_ids", side_effect=SearchUnavailable):
        assert client.post("/studio/search", json=query, headers=headers).status_code == 503


def test_studio_serves_only_supported_public_assets(tmp_path):
    dist = tmp_path / "frontend" / "dist"
    assets = dist / "assets"
    assets.mkdir(parents=True)
    (dist / "index.html").write_text("<h1>Citizen Studio</h1>", encoding="utf-8")
    (dist / "private.txt").write_text("unlisted", encoding="utf-8")
    (dist / "font-licenses.txt").write_text("SIL Open Font License", encoding="utf-8")
    (assets / "index-stub.js").write_text("export {};", encoding="utf-8")
    server = Flask(__name__)
    server.register_blueprint(make_studio(tmp_path, {}, []))
    client = server.test_client()
    shell = client.get("/studio/")
    assert b"Citizen Studio" in shell.data
    assert "frame-ancestors 'none'" in shell.headers["Content-Security-Policy"]
    assert client.get("/studio/assets/index-stub.js").cache_control.max_age == 31_536_000
    assert b"SIL Open Font License" in client.get("/studio/font-licenses.txt").data
    assert client.get("/studio/private.txt").status_code == 404
    assert client.get("/studio/assets/../private.txt").status_code == 404


def test_studio_session_token_is_private_and_accepted_by_csrf():
    server = Flask(__name__)
    server.config["SECRET_KEY"] = "test-only"
    CSRFProtect(server)
    server.register_blueprint(make_studio(server.root_path, {}, []))

    @server.post("/protected")
    def protected():
        return "", 204

    client = server.test_client()
    result = client.get("/studio/session")
    assert result.cache_control.no_store
    assert client.post("/protected").status_code == 400
    token = result.get_json()["csrfToken"]
    assert client.post("/protected", headers={"X-CSRFToken": token}).status_code == 204
    assert server.test_client().post("/protected", headers={"X-CSRFToken": token}).status_code == 400


def test_facility_directory_returns_only_public_location_fields():
    entries = app.test_client().get("/studio/facilities.json").get_json()["facilities"]
    assert entries and any(entry["district"] and entry["lat"] and entry["lng"] for entry in entries)
    assert set(entries[0]) == {"id", "name", "type", "district", "mandal", "village", "contact", "lat", "lng"}


def test_cross_sector_entries_keep_official_links_and_do_not_invent_eligibility():
    rows = app.test_client().get("/studio/catalog.json").get_json()["schemes"]
    entries = {entry["id"]: entry for entry in rows if entry["directoryEntry"]}
    assert {entry["sector"] for entry in rows} >= {"health", "education", "housing", "agriculture", "welfare"}
    assert entries["welfare-ntr-bharosa"]["region"] == "Andhra Pradesh"
    kisan = entries["welfare-pm-kisan"]
    assert kisan["source"]["url"] == "https://pmkisan.gov.in/"
    assert kisan["source"]["reviewed"]
    assert kisan["en"]["description"] and kisan["te"]["description"]
    assert not kisan["documents"] and not kisan["questions"] and "eligibility" not in kisan["en"]
    assert kisan["operations"]["required_documents"][0]["name"]["te"] == "ఆధార్ సంఖ్య"
    assert kisan["operations"]["application_process"]["official_url"] == "https://pmkisan.gov.in/RegistrationFormupdated.aspx"
    assert kisan["operations"]["eligibility"]["income_ceiling"] is None
    assert entries["welfare-ntr-bharosa"]["operations"] is None


@patch("app.generate_chat_response", return_value=None)
def test_studio_chat_can_find_cross_sector_entries_without_changing_classic_catalog(_mock):
    client = app.test_client()
    question = {"question": "PM-KISAN", "lang": "en"}
    studio = client.post("/chat", json={**question, "catalog": "studio"}).get_json()
    classic = client.post("/chat", json=question).get_json()
    assert studio["matched_schemes"][0]["scheme_name"] == "PM-KISAN"
    assert not studio["used_ai"]
    assert "PM-KISAN" not in [item["scheme_name"] for item in classic["matched_schemes"]]
