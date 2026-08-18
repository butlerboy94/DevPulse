# Tests for the /analyze, /results/{id}, and /history endpoints — the full
# pipeline wired through the HTTP layer.
SIMPLE_CODE = "def add(a, b):\n    return a + b\n\nprint(add(2, 3))\n"


def test_anonymous_analyze_succeeds(client):
    response = client.post(
        "/api/v1/analyze",
        json={"language": "python", "source_code": SIMPLE_CODE, "iterations": 2},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "complete"
    assert data["quality_score"] == 100.0
    assert data["execution_time_ms"] is not None


def test_unsupported_language_is_rejected(client):
    response = client.post(
        "/api/v1/analyze",
        json={"language": "javascript", "source_code": "console.log(1)", "iterations": 2},
    )
    assert response.status_code == 400


def test_get_result_for_anonymous_analysis_is_public(client):
    create_response = client.post(
        "/api/v1/analyze",
        json={"language": "python", "source_code": SIMPLE_CODE, "iterations": 2},
    )
    public_id = create_response.json()["public_id"]

    response = client.get(f"/api/v1/results/{public_id}")
    assert response.status_code == 200
    assert response.json()["public_id"] == public_id


def test_get_result_missing_id_returns_404(client):
    response = client.get("/api/v1/results/999999")
    assert response.status_code == 404


def test_analysis_ids_are_not_sequentially_guessable(client):
    # Two different submissions must get two different, non-numeric public
    # tokens — guards against ever silently falling back to the old
    # sequential database id, which would reopen the enumeration gap this
    # endpoint was changed to close.
    first = client.post(
        "/api/v1/analyze",
        json={"language": "python", "source_code": SIMPLE_CODE, "iterations": 2},
    ).json()
    second = client.post(
        "/api/v1/analyze",
        json={"language": "python", "source_code": SIMPLE_CODE, "iterations": 2},
    ).json()

    assert first["public_id"] != second["public_id"]
    assert not first["public_id"].isdigit()

    # Trying to look an anonymous analysis up by a guessed small number
    # (what the old sequential id would have looked like) must not work.
    assert client.get("/api/v1/results/1").status_code == 404


def test_history_requires_login(client):
    response = client.get("/api/v1/history")
    assert response.status_code == 401


def test_history_lists_logged_in_users_analyses(client, auth_headers):
    client.post(
        "/api/v1/analyze",
        json={"language": "python", "source_code": SIMPLE_CODE, "iterations": 2},
        headers=auth_headers,
    )

    response = client.get("/api/v1/history", headers=auth_headers)
    assert response.status_code == 200
    history = response.json()
    assert len(history) == 1
    assert history[0]["status"] == "complete"


def test_history_does_not_include_other_users_analyses(client, auth_headers):
    # Anonymous submission — should not show up in the logged-in user's history.
    client.post(
        "/api/v1/analyze",
        json={"language": "python", "source_code": SIMPLE_CODE, "iterations": 2},
    )

    response = client.get("/api/v1/history", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []
