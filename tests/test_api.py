
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

TASK = {
    "id": 1,
    "title": "Automate CI/CD Pipeline",
    "description": "Build Docker images with Jenkins",
    "status": "pending",
    "priority": "high",
    "created_at": datetime(2026, 10, 14, tzinfo=timezone.utc),
    "updated_at": datetime(2026, 10, 14, tzinfo=timezone.utc),
}


def test_health():
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_dashboard():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_create_task():
    with patch(
        "app.api.tasks.task_service.create_task",
        return_value=TASK,
    ) as mock_create:
        response = client.post(
            "/api/v1/tasks",
            json={
                "title": "Automate CI/CD Pipeline",
                "description": "Build Docker images with Jenkins",
                "priority": "high",
            },
        )

    assert response.status_code == 201
    assert response.json()["title"] == TASK["title"]
    mock_create.assert_called_once()


@pytest.mark.parametrize(
    "title",
    ["", "ab", "x" * 151],
)
def test_invalid_task_title(title):
    response = client.post(
        "/api/v1/tasks",
        json={"title": title},
    )

    assert response.status_code == 422


def test_invalid_priority():
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Valid Task",
            "priority": "urgent",
        },
    )

    assert response.status_code == 422


def test_list_tasks():
    with patch(
        "app.api.tasks.task_service.get_tasks",
        return_value=[TASK],
    ) as mock_list:
        response = client.get(
            "/api/v1/tasks?limit=10&offset=0"
        )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == 1
    mock_list.assert_called_once_with(10, 0)


@pytest.mark.parametrize(
    "query",
    ["limit=0", "limit=101", "offset=-1"],
)
def test_invalid_pagination(query):
    response = client.get(f"/api/v1/tasks?{query}")

    assert response.status_code == 422


def test_get_task():
    with patch(
        "app.api.tasks.task_service.get_task",
        return_value=TASK,
    ):
        response = client.get("/api/v1/tasks/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_get_missing_task():
    with patch(
        "app.api.tasks.task_service.get_task",
        return_value=None,
    ):
        response = client.get("/api/v1/tasks/999")

    assert response.status_code == 404


def test_update_task():
    updated = {
        **TASK,
        "status": "completed",
    }

    with patch(
        "app.api.tasks.task_service.update_task",
        return_value=updated,
    ):
        response = client.patch(
            "/api/v1/tasks/1",
            json={"status": "completed"},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_update_null_status():
    response = client.patch(
        "/api/v1/tasks/1",
        json={"status": None},
    )

    assert response.status_code == 422


def test_update_missing_task():
    with patch(
        "app.api.tasks.task_service.update_task",
        return_value=None,
    ):
        response = client.patch(
            "/api/v1/tasks/999",
            json={"priority": "low"},
        )

    assert response.status_code == 404


def test_delete_task():
    with patch(
        "app.api.tasks.task_service.delete_task",
        return_value=True,
    ):
        response = client.delete("/api/v1/tasks/1")

    assert response.status_code == 204


def test_delete_missing_task():
    with patch(
        "app.api.tasks.task_service.delete_task",
        return_value=False,
    ):
        response = client.delete("/api/v1/tasks/999")

    assert response.status_code == 404
