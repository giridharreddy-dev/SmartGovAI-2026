from flask import Flask
from flask_wtf.csrf import CSRFProtect

from app import app
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
