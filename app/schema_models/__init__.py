from app.schema_models.base_schema import BaseRequest, ListRequest, SearchRequest
from app.schema_models.base_schema import GetByNameRequest, GetByIdRequest
from app.schema_models.base_schema import ListRequestWithIsActive, SearchRequestWithIsActive
from app.schema_models.gmail.message_attachment import MessageAttachmentResponse
from app.schema_models.gmail.message import GetByMessageIdRequest, MessageResponse, MessageMinimalResponse
from app.schema_models.gmail.message_body import MessageBodyResponse
from app.schema_models.gmail.label import LabelResponse, GetByLabelIdRequest
from app.schema_models.gmail.message_label import MessageLabelResponse
from app.schema_models.workflow.rule import CreateRuleRequest, RuleResponse, ExecuteByNameRequest, ExecuteByIdRequest
from app.schema_models.workflow.filter_field import FilterFieldResponse
