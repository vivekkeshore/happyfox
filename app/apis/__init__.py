from fastapi import APIRouter, status
from app.apis.gmail.message import message_router
from app.apis.gmail.message_detail import message_body_router
from app.apis.gmail.label import label_router
from app.apis.gmail.message_label import message_label_router
from app.apis.gmail.message_attachment import message_attachment_router
from app.apis.workflow.filter_field import filter_field_router
from app.apis.workflow.rule import rule_router


ping_router = APIRouter()


@ping_router.get(
	"/ping",
	status_code=status.HTTP_200_OK, tags=["Health Check"],
	summary="Health Check API",
)
async def ping():
	return "pong ... !"


API_ROUTERS = [
	(ping_router, {"prefix": ""}),
	(message_router, {"prefix": "/message"}),
	(message_body_router, {"prefix": "/message_body"}),
	(label_router, {"prefix": "/label"}),
	(message_label_router, {"prefix": "/message_label"}),
	(message_attachment_router, {"prefix": "/message_attachment"}),
	(filter_field_router, {"prefix": "/filter_field"}),
	(rule_router, {"prefix": "/rule"}),
]
