from http import HTTPStatus
from unittest.mock import patch

from fastapi.testclient import TestClient
from app.models.enum_model import RulePredicate, Operation, ActionType

from main import app

client = TestClient(app)

def test_list_rules():
	response = client.get("/rule/list", params={"page": "1", "per_page": "2", "count": False})
	assert response.status_code == HTTPStatus.OK
	assert len(response.json()) == 2

	response = client.get("/rule/list", params={"page": "1", "per_page": "2", "is_active": True, "count": False})
	assert response.status_code == HTTPStatus.OK
	assert len(response.json()) == 2


def test_list_rules_count():
	response = client.get("/rule/list", params={"count": True})
	# cannot pass both count and page/per_page query params
	assert response.status_code == HTTPStatus.OK

	response = client.get("/rule/list", params={"count": True, "is_active": True})
	# cannot pass both count and page/per_page query params
	assert response.status_code == HTTPStatus.OK


def test_list_rules_count_negative():
	response = client.get("/rule/list", params={"page": "1", "per_page": "2", "count": True})
	# cannot pass both count and page/per_page query params
	assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

def test_get_rule_by_id():
	response = client.get("/rule/list", params={"page": "1", "per_page": "1", "count": False})
	rule_uuid = response.json()[0]["id"]

	response = client.get(f"/rule/get_by_id/{rule_uuid}")
	assert response.status_code == HTTPStatus.OK
	assert response.json()["id"] == rule_uuid

def test_get_rule_by_id_negative():
	response = client.get("/rule/get_by_id/foobar")
	assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

	# dummy uuid
	response = client.get("/rule/get_by_id/00000000-0000-0000-0000-000000000000")
	assert response.status_code == HTTPStatus.BAD_REQUEST

def test_get_rule_by_name():
	response = client.get("/rule/list", params={"page": "1", "per_page": "1", "count": False})
	rule_name = response.json()[0]["name"]

	response = client.get(f"/rule/get_by_name/{rule_name}")
	assert response.status_code == HTTPStatus.OK
	assert response.json()["name"] == rule_name

def test_get_rule_by_name_negative():
	response = client.get("/rule/get_by_name/foobar")
	assert response.status_code == HTTPStatus.BAD_REQUEST

	# dummy name
	response = client.get("/rule/get_by_name/foobarfoobarfoobarfoob")
	assert response.status_code == HTTPStatus.BAD_REQUEST

def test_search_rules():
	response = client.get("/rule/list", params={"page": "1", "per_page": "1", "count": False})
	name = response.json()[0]["name"]

	response = client.get(
		"/rule/search", params={
			"col": "name", "value": name,
            "page": "1", "per_page": "1", "count": False
		}
	)
	assert response.status_code == HTTPStatus.OK
	assert len(response.json()) == 1
	assert response.json()[0]["name"] == name

	# upper case
	response = client.get(
		"/rule/search", params={
			"col": "name", "value": name.upper(),
			"page": "1", "per_page": "1", "count": False
		}
	)
	assert response.status_code == HTTPStatus.OK
	assert len(response.json()) == 1
	assert response.json()[0]["name"] == name

	response = client.get(
		"/rule/search", params={
			"col": "name", "value": "foobar",
			"page": "1", "per_page": "1", "count": False
		}
	)
	assert response.status_code == HTTPStatus.OK
	assert len(response.json()) == 0

def test_search_rules_count():
	response = client.get("/rule/list", params={"page": "1", "per_page": "1", "count": False})
	name = response.json()[0]["name"]

	response = client.get(
		"/rule/search", params={
			"col": "name", "value": name,
			"count": True
		}
	)
	assert response.status_code == HTTPStatus.OK
	assert response.json() == 1

	# upper case
	response = client.get(
		"/rule/search", params={
			"col": "name", "value": name.upper(),
			"count": True
		}
	)

	assert response.status_code == HTTPStatus.OK
	assert response.json() == 1

	# no search results
	response = client.get(
		"/rule/search", params={
			"col": "name", "value": "foobar",
			"count": True
		}
	)
	assert response.status_code == HTTPStatus.OK
	assert response.json() == 0


def test_search_rules_count_negative():
	response = client.get("/rule/search", params={"page": "1", "per_page": "1", "count": True})
	assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

	response = client.get("/rule/search", params={"col": "foobar", "value": "foobar", "count": True})
	assert response.status_code == HTTPStatus.BAD_REQUEST


def test_search_rules_negative():
	response = client.get(
		"/rule/search", params={
			"col": "foobar", "value": "foobar",
			"page": "1", "per_page": "1", "count": False
		}
	)
	assert response.status_code == HTTPStatus.BAD_REQUEST

	response = client.get(
		"/rule/search", params={
			"col": "name", "value": "foobar",
			"page": "1", "per_page": "1", "count": True
		}
	)
	assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_create_rule():
	response = client.post(
		"/rule/create", json={
			"name": "Test Rule 1",
			"predicate": "ANY",
			"rule_details": [
				{
					"field_name": "has_attachment",
					"operation": "EQUALS",
					"value": "True",
				},
				{
					"field_name": "subject",
					"operation": "CONTAINS",
					"value": "foobar",
				}
			],
			"actions": [
				{
					"action": "MOVE",
					"value": "Travel"
				},
				{
					"action": "MOVE",
					"value": "INBOX"
				},
				{
					"action": "MARK_AS_UNREAD"
				}
			],
		}
	)
	assert response.status_code == HTTPStatus.CREATED
	assert response.json()["name"] == "Test Rule 1"
	assert len(response.json()["rule_details"]) == 2
	assert len(response.json()["actions"]) == 3
	rule_uuid = response.json()["id"]

	# Trying to recreate the rule with same name
	response = client.post(
		"/rule/create", json={
			"name": "Test Rule 1",
			"predicate": "ANY",
			"rule_details": [
				{
					"field_name": "has_attachment",
					"operation": "EQUALS",
					"value": "True"
				},
				{
					"field_name": "subject",
					"operation": "CONTAINS",
					"value": "foobar"
				}
			],
			"actions": [
				{
					"action": "MOVE",
					"value": "Travel"
				},
				{
					"action": "MOVE",
					"value": "INBOX"
				},
				{
					"action": "MARK_AS_UNREAD"
				}
			]
		}
	)
	assert response.status_code == HTTPStatus.CONFLICT

	# Delete the rule
	response = client.delete(f"/rule/delete/{rule_uuid}")
	assert response.status_code == HTTPStatus.NO_CONTENT

def test_create_rule_negative():
	response = client.post(
		"/rule/create", json={
			"name": "Test Rule 1",
			"predicate": "FOO",  # Unknown predicate
			"rule_details": [
				{
					"field_name": "has_attachment",
					"operation": "EQUALS",
					"value": "True"
				}
			],
			"actions": [
				{
					"action": "MOVE",
					"value": "Travel"
				}
			],
		}
	)
	assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

	response = client.post(
		"/rule/create", json={
			"name": "", # No name
			"predicate": "ANY",
			"rule_details": [
				{
					"field_name": "has_attachment",
					"operation": "EQUALS",
					"value": "True"
				}
			],
			"actions": [
				{
					"action": "MOVE",
					"value": "Travel"
				}
			],
		}
	)
	assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

	response = client.post(
		"/rule/create", json={
			"name": "Rule 1",
			"predicate": "ANY",
			"rule_details": [],  # No rules
			"actions": [
				{
					"action": "MOVE",
					"value": "Travel"
				}
			],
		}
	)
	assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

	response = client.post(
		"/rule/create", json={
			"name": "Rule 1",
			"predicate": "ANY",
			"rule_details": [
				{
					"field_name": "has_attachment",
					"operation": "EQUALS",
					"value": "True"
				}
			],
			"actions": []  # No Actions
		}
	)
	assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

	response = client.post(
		"/rule/create", json={
			"name": "Test Rule 1",
			"predicate": "ANY",  # Unknown predicate
			"rule_details": [
				{
					"field_name": "has_attachment",
					"operation": "IN",  # Invalid operation
					"value": "True"
				}
			],
			"actions": [
				{
					"action": "MOVE",
					"value": "Travel"
				}
			],
		}
	)
	assert response.status_code == HTTPStatus.BAD_REQUEST

	response = client.post(
		"/rule/create", json={
			"name": "Test Rule 1",
			"predicate": "ANY",  # Unknown predicate
			"rule_details": [
				{
					"field_name": "has_attachment",
					"operation": "EQUALS",
					"value": "True"
				}
			],
			"actions": [
				{
					"action": "MOVE",   # No value or label for move action
				}
			],
		}
	)
	assert response.status_code == HTTPStatus.BAD_REQUEST

	response = client.post(
		"/rule/create", json={
			"name": "Test Rule 1",
			"predicate": "ANY",  # Unknown predicate
			"rule_details": [
				{
					"field_name": "has_attachment",
					"operation": "EQUALS",
					"value": "True"
				}
			],
			"actions": [
				{
					"action": "MOVE",
					"value": "Foo" # Invalid label for move action
				}
			],
		}
	)
	assert response.status_code == HTTPStatus.BAD_REQUEST

	response = client.post(
		"/rule/create", json={
			"name": "Test Rule 1",
			"predicate": "ANY",  # Unknown predicate
			"rule_details": [
				{
					"field_name": "size",
					"operation": "EQUALS",
					"value": "foo"  # Invalid value for size. size should be an int.
				}
			],
			"actions": [
				{
					"action": "MOVE",
					"value": "INBOX"
				}
			],
		}
	)
	assert response.status_code == HTTPStatus.BAD_REQUEST

def test_execute_rule_by_name():
	test_rule_response = client.post(
		"/rule/create", json={
			"name": "Test Rule 1",
			"predicate": "ANY",
			"rule_details": [
				{
					"field_name": "has_attachment",
					"operation": "EQUALS",
					"value": "True",
				},
				{
					"field_name": "subject",
					"operation": "CONTAINS",
					"value": "foobar",
				}
			],
			"actions": [
				{
					"action": "MOVE",
					"value": "Travel"
				},
				{
					"action": "MOVE",
					"value": "INBOX"
				},
				{
					"action": "MARK_AS_UNREAD"
				}
			],
		}
	)

	response = client.post(
		"/rule/execute_by_name", json={
			"name": "Test Rule 1",
			"execute_actions": True
		}
	)
	assert response.status_code == HTTPStatus.OK

	response = client.post(
		"/rule/execute_by_id", json={
			"id": test_rule_response.json()["id"],
			"execute_actions": False
		}
	)
	assert response.status_code == HTTPStatus.OK

	# Delete the rule
	response = client.delete(f"/rule/delete/{test_rule_response.json()['id']}")
	assert response.status_code == HTTPStatus.NO_CONTENT