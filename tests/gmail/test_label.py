import pytest
from fastapi.testclient import TestClient
from http import HTTPStatus
from main import app  # Import your FastAPI app

client = TestClient(app)

def test_list_label():
    response = client.get("label/list", params={"page": "1", "per_page": "8", "count": False})
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 8

    response = client.get("label/list", params={"page": "1", "per_page": "8", "is_active": True, "count": False})
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 8

def test_list_label_count():
    response = client.get("label/list", params={"count": True})
    # cannot pass both count and page/per_page query params
    assert response.status_code == HTTPStatus.OK

    response = client.get("label/list", params={"count": True, "is_active": True})
    # cannot pass both count and page/per_page query params
    assert response.status_code == HTTPStatus.OK

def test_list_label_count_negative():
    response = client.get("label/list", params={"page": "1", "per_page": "8", "count": True})
    # cannot pass both count and page/per_page query params
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

def test_get_label_by_label_id():
    response = client.get("label/get_by_label_id/INBOX")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["label_id"] == "INBOX"
    assert response.json()["name"] == "INBOX"

    response = client.get("label/get_by_label_id/Label_3")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["label_id"] == "Label_3"
    assert response.json()["name"] == "Travel"

def test_get_label_by_label_id_negative():
    response = client.get("label/get_by_label_id/foobar")
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_get_label_by_name():
    response = client.get("label/get_by_name/INBOX")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["label_id"] == "INBOX"
    assert response.json()["name"] == "INBOX"

    response = client.get("label/get_by_name/Travel")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["label_id"] == "Label_3"
    assert response.json()["name"] == "Travel"

def test_get_label_by_name_negative():
    response = client.get("label/get_by_name/foobar")
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_get_label_by_id():
    response = client.get("label/get_by_name/INBOX")
    label_uuid = response.json()["id"]
    response = client.get(f"label/get_by_id/{label_uuid}")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["label_id"] == "INBOX"
    assert response.json()["name"] == "INBOX"
    assert response.json()["id"] == label_uuid


def test_get_label_by_id_negative():
    # Ill-formatted uuid
    response = client.get("label/get_by_id/foobar")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    # record does not exist
    response = client.get("label/get_by_id/e095bbf1-b16d-4a66-846b-0d051c8f681e")
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_search_label():
    response = client.get(
        "label/search", params={
            "col": "name", "value": "INBOX", "page": "1",
            "per_page": "8", "count": False
        }
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "INBOX"

    # Lower case
    response = client.get(
        "label/search", params={
            "col": "name", "value": "inbox", "page": "1",
            "per_page": "8", "count": False
        }
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "INBOX"

    # Partial match case
    response = client.get(
        "label/search", params={
            "col": "name", "value": "INB", "page": "1",
            "per_page": "8", "count": False
        }
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "INBOX"

    # Get count
    response = client.get(
        "label/search", params={
            "col": "name", "value": "INBOX", "count": True
        }
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == 1

    # No search results
    response = client.get(
        "label/search", params={
            "col": "name", "value": "foobar", "page": "1",
            "per_page": "8", "count": False
        }
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 0

def test_search_label_negative():
    # Invalid column name
    response = client.get(
        "label/search", params={
            "col": "foobar", "value": "INBOX", "page": "1",
            "per_page": "8", "count": False
        }
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST

    # Count with per page
    response = client.get(
        "label/search", params={
            "col": "name", "value": "INBOX", "page": "1",
            "per_page": "8", "count": True
        }
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

def test_label_deactivate_activate():
    response = client.get("label/get_by_name/INBOX")
    label_uuid = response.json()["id"]

    response = client.put(f"label/deactivate", json={"id": label_uuid})
    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "Label deactivated successfully."

    response = client.put(f"label/activate", json={"id": label_uuid})
    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "Label activated successfully."

def test_label_deactivate_activate_negative():
    # Ill-formatted uuid
    response = client.put("label/deactivate", json={"id": "foobar"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    # record does not exist
    response = client.put("label/deactivate", json={"id": "e095bbf1-b16d-4a66-846b-0d051c8f681e"})
    assert response.status_code == HTTPStatus.BAD_REQUEST

    # Ill-formatted uuid
    response = client.put("label/activate", json={"id": "foobar"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    # record does not exist
    response = client.put("label/activate", json={"id": "e095bbf1-b16d-4a66-846b-0d051c8f681e"})
    assert response.status_code == HTTPStatus.BAD_REQUEST
