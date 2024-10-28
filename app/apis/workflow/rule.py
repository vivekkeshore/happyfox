from typing import List, Union

from fastapi import APIRouter, status, Depends

from app.lib.exception_handler import error_handler
from app.lib.pydantic_helper import make_dependable
from app.schema_models import CreateRuleRequest, GetByNameRequest, ExecuteByNameRequest
from app.schema_models import ListRequest, RuleResponse, GetByIdRequest, MessageMinimalResponse
from app.schema_models import SearchRequest, ExecuteByIdRequest
from app.services import RuleService

rule_router = APIRouter()


@rule_router.get(
	"/list", response_model=Union[List[RuleResponse], int],
	status_code=status.HTTP_200_OK, tags=["Rule APIs"],
	summary="Get all rules"
)
@error_handler
async def get_all_rules(query_params: ListRequest = Depends(make_dependable(ListRequest))):
	"""
	Get all rules. This API will return all the rules in the system.
	"""
	rules = RuleService().get_all_rules(query_params)

	return rules


@rule_router.get(
	"/get_by_id/{id}", response_model=RuleResponse,
	status_code=status.HTTP_200_OK, tags=["Rule APIs"],
	summary="Get rule by rule id"
)
@error_handler
async def get_rule_by_id(path_params: GetByIdRequest = Depends()):
	"""
	Get message attachment by message attachment uuid. This API will return the message attachment for the given message attachment uuid.
	"""
	rule = RuleService().get_rule_by_id(path_params.id)

	return rule


@rule_router.get(
	"/get_by_name/{name}", response_model=RuleResponse,
	status_code=status.HTTP_200_OK, tags=["Rule APIs"],
	summary="Get rule by rule name"
)
@error_handler
async def get_rule_by_name(path_params: GetByNameRequest = Depends()):
	"""
	Get rule by rule name. This API will return the rule for the given rule name.
	"""
	rule = RuleService().get_rule_by_name(path_params.name)

	return rule


@rule_router.get(
	"/search", response_model=Union[List[RuleResponse], int],
	status_code=status.HTTP_200_OK, tags=["Rule APIs"],
	summary="Search rules"
)
@error_handler
async def search_rule(query_params: SearchRequest = Depends(make_dependable(SearchRequest))):
	"""
	Search rules. This API will search for the rules based on the search query.
	"""
	rule = RuleService().search_rule(query_params)

	return rule


@rule_router.post(
	"/create", response_model=RuleResponse,
	status_code=status.HTTP_201_CREATED, tags=["Rule APIs"],
	summary="Create rule"
)
@error_handler
async def create_rule(request_body: CreateRuleRequest):
	"""
	Create rule. This API will create a new rule in the system.
	"""
	rule = RuleService().create_rule(request_body)

	return rule

@rule_router.post(
	"/execute_by_name", response_model=List[MessageMinimalResponse],
	status_code=status.HTTP_200_OK, tags=["Rule APIs"],
	summary="Execute rule by rule name"
)
@error_handler
async def execute_rule_by_name(request_body: ExecuteByNameRequest):
	"""
	Execute rule by rule name. This API will execute the rule for the given rule name.
	"""
	messages = RuleService().execute_rule_by_id_or_name(
		rule_name=request_body.name, execute_actions=request_body.execute_actions
	)
	return messages


@rule_router.post(
	"/execute_by_id", response_model=List[MessageMinimalResponse],
	status_code=status.HTTP_200_OK, tags=["Rule APIs"],
	summary="Execute rule by rule id"
)
@error_handler
async def execute_rule_by_id(request_body: ExecuteByIdRequest):
	"""
	Execute rule by rule id. This API will execute the rule for the given rule id.
	"""
	messages = RuleService().execute_rule_by_id_or_name(
		rule_id=request_body.id, execute_actions=request_body.execute_actions
	)
	return messages


@rule_router.delete(
	"/delete/{id}", status_code=status.HTTP_204_NO_CONTENT,
	tags=["Rule APIs"], summary="Deletes the rule from the system"
)
@error_handler
async def delete_rule(path_params: GetByIdRequest = Depends()):
	"""
	Delete rule. This API will delete the rule from the system.
	"""
	RuleService().delete_rule(path_params.id)
