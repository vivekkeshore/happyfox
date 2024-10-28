from http import HTTPStatus
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_list_messages():
    response = client.get("/message/list", params={"page": "1", "per_page": "8", "count": False})
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 8

    response = client.get("/message/list", params={"page": "1", "per_page": "8", "is_active": True, "count": False})
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 8

def test_list_messages_count():
    response = client.get("/message/list", params={"count": True})
    # cannot pass both count and page/per_page query params
    assert response.status_code == HTTPStatus.OK

    response = client.get("/message/list", params={"count": True, "is_active": True})
    # cannot pass both count and page/per_page query params
    assert response.status_code == HTTPStatus.OK

def test_list_messages_count_negative():
    response = client.get("/message/list", params={"page": "1", "per_page": "8", "count": True})
    # cannot pass both count and page/per_page query params
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

def test_get_message_by_message_id():
    response = client.get("/message/list", params={"page": "1", "per_page": "1", "count": False})
    message_id = response.json()[0]["message_id"]

    response = client.get(f"/message/get_by_message_id/{message_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["message_id"] == message_id

def test_get_message_by_message_id_negative():
    response = client.get("/message/get_by_message_id/foobar")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    # message_id is not valid
    response = client.get("/message/get_by_message_id/foobarfoobarfoobarfoob")
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_get_message_by_id():
    response = client.get("/message/list", params={"page": "1", "per_page": "1", "count": False})
    message_uuid = response.json()[0]["id"]

    response = client.get(f"/message/get_by_id/{message_uuid}")
    assert response.status_code == HTTPStatus.OK
    assert response.json()["id"] == message_uuid

def test_get_message_by_id_negative():
    response = client.get("/message/get_by_id/foobar")
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    # non existent uuid
    response = client.get("/message/get_by_id/e095bbf1-b16d-4a66-846b-0d051c8f681f")
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_search_messages():
    response = client.get("/message/list", params={"page": "1", "per_page": "1", "count": False})
    subject = response.json()[0]["subject"]

    response = client.get(
        "/message/search", params={
            "col": "subject", "value": subject,
            "page": "1", "per_page": "8", "count": False
        }
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1
    assert response.json()[0]["subject"] == subject

    # upper case
    response = client.get(
        "/message/search", params={
            "col": "subject", "value": subject.upper(),
            "page": "1", "per_page": "8", "count": False
        }
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 1
    assert response.json()[0]["subject"] == subject

    # no search results
    response = client.get(
        "/message/search", params={
            "col": "subject", "value": "foobar",
            "page": "1", "per_page": "8", "count": False
        }
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()) == 0


def test_search_messages_count():
    response = client.get("/message/list", params={"page": "1", "per_page": "1", "count": False})
    subject = response.json()[0]["subject"]

    response = client.get(
        "/message/search", params={
            "col": "subject", "value": subject,
            "count": True
        }
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == 1

    # upper case
    response = client.get(
        "/message/search", params={
            "col": "subject", "value": subject.upper(),
            "count": True
        }
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == 1

    # no search results
    response = client.get(
        "/message/search", params={
            "col": "subject", "value": "foobar",
            "count": True
        }
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == 0

def test_search_messages_negative():
    response = client.get(
        "/message/search", params={
            "col": "foobar", "value": "INBOX",
            "page": "1", "per_page": "8", "count": False
        }
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST

    response = client.get(
        "/message/search", params={
            "col": "subject", "value": "INBOX",
            "page": "1", "per_page": "8", "count": True
        }
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

@patch('app.services.workflow.gmail_service.GmailService.__init__', lambda self: None)
@patch('app.services.workflow.gmail_service.GmailService.move_labels')
def test_move_to_trash_untrash(unused_move_labels):
    response = client.get("/message/list", params={"page": "1", "per_page": "1", "count": False})
    message_uuid = response.json()[0]["id"]

    response = client.put("/message/trash", json={"id": message_uuid})
    assert response.status_code == HTTPStatus.OK
    assert response.json()["status"] == "success"

    # Trashing already trashed message
    response = client.put("/message/trash", json={"id": message_uuid})
    assert response.status_code == HTTPStatus.BAD_REQUEST

    response = client.put("/message/untrash", json={"id": message_uuid})
    assert response.status_code == HTTPStatus.OK
    assert response.json()["status"] == "success"

    # untrashing already untrashed message
    response = client.put("/message/untrash", json={"id": message_uuid})
    assert response.status_code == HTTPStatus.BAD_REQUEST

def test_move_to_trash_untrash_negative():
    response = client.put("/message/trash", json={"id": "foobar"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    response = client.put("/message/untrash", json={"id": "foobar"})
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    response = client.put("/message/trash", json={"id": "e095bbf1-b16d-4a66-846b-0d051c8f681f"})
    assert response.status_code == HTTPStatus.BAD_REQUEST

    response = client.put("/message/untrash", json={"id": "e095bbf1-b16d-4a66-846b-0d051c8f681f"})
    assert response.status_code == HTTPStatus.BAD_REQUEST