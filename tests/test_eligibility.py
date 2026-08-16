import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_eligibility_states(client):
    """Test the four eligibility states in /eligibility-check."""
    from app import schemes

    # Mock a scheme with 2 questions
    schemes["test_elig"] = {
        "eligibility_questions": [
            {"question_en": "Q1?", "weight": "medium"},
            {"question_en": "Q2?", "weight": "medium"}
        ]
    }

    # 1. Eligible (All yes)
    resp = client.post("/eligibility-check", json={"scheme_name": "test_elig", "answers": {"0": "yes", "1": "yes"}})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "eligible"
    assert len(data["matched_criteria"]) == 2
    assert len(data["unknown_criteria"]) == 0
    assert len(data["unmatched_criteria"]) == 0
    assert data["likely_eligible"] is True

    # 2. Likely Eligible (Partial yes)
    # 1/2 is 50%, wait, my logic said 60%? Yes, 60% for likely_eligible. Let's make Q1 high, Q2 medium.
    schemes["test_elig"]["eligibility_questions"][0]["weight"] = "high"
    resp = client.post("/eligibility-check", json={"scheme_name": "test_elig", "answers": {"0": "yes", "1": "unknown"}})
    assert resp.status_code == 200
    data = resp.get_json()
    # Score 2/3 = 66% >= 60% => likely_eligible
    assert data["status"] == "likely_eligible"
    assert len(data["matched_criteria"]) == 1
    assert len(data["unknown_criteria"]) == 1
    assert len(data["unmatched_criteria"]) == 0
    assert data["likely_eligible"] is True

    # 3. Not Eligible (All no, or < 60%)
    resp = client.post("/eligibility-check", json={"scheme_name": "test_elig", "answers": {"0": "no", "1": "yes"}})
    assert resp.status_code == 200
    data = resp.get_json()
    # Score 1/3 = 33% < 60% => not_eligible
    assert data["status"] == "not_eligible"
    assert data["likely_eligible"] is False
    assert len(data["matched_criteria"]) == 1
    assert len(data["unmatched_criteria"]) == 1

    # 4. Insufficient Information (All unknown)
    resp = client.post("/eligibility-check", json={"scheme_name": "test_elig", "answers": {}})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "insufficient_information"
    assert data["likely_eligible"] is False
    assert len(data["unknown_criteria"]) == 2

    # Cleanup
    del schemes["test_elig"]
