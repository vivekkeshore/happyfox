from helpers.enum_models import FieldType, Operation

FIELD_RULE = {
	"from_address": {
		"field_type": FieldType.STRING,
		"allowed_operations": [Operation.EQUALS, Operation.NOT_EQUALS, Operation.CONTAINS, Operation.NOT_CONTAINS],
		"is_column": True,
		"schema": "gmail",
		"table": "Message",
		"column": "from_address"
	},
	"to": {
		"field_type": FieldType.STRING,
		"allowed_operations": [Operation.EQUALS, Operation.NOT_EQUALS, Operation.CONTAINS, Operation.NOT_CONTAINS],
		"is_column": True,
		"schema": "gmail",
		"table": "Message",
		"column": "to"
	},
	"cc": {
		"field_type": FieldType.STRING,
		"allowed_operations": [Operation.EQUALS, Operation.NOT_EQUALS, Operation.CONTAINS, Operation.NOT_CONTAINS],
		"is_column": True,
		"schema": "gmail",
		"table": "Message",
		"column": "cc"
	},
	"bcc": {
		"field_type": FieldType.STRING,
		"allowed_operations": [Operation.EQUALS, Operation.NOT_EQUALS, Operation.CONTAINS, Operation.NOT_CONTAINS],
		"is_column": True,
		"schema": "gmail",
		"table": "Message",
		"column": "bcc"
	},
	"subject": {
		"field_type": FieldType.STRING,
		"allowed_operations": [Operation.EQUALS, Operation.NOT_EQUALS, Operation.CONTAINS, Operation.NOT_CONTAINS],
		"is_column": True,
		"schema": "gmail",
		"table": "Message",
		"column": "subject"
	},
	"received_at": {
		"field_type": FieldType.NUMBER,
		"allowed_operations": [
			Operation.EQUALS, Operation.NOT_EQUALS, Operation.GREATER_THAN, Operation.LESS_THAN,
			Operation.GREATER_THAN_EQUALS, Operation.LESS_THAN_EQUALS
		],
		"is_column": True,
		"schema": "gmail",
		"table": "Message",
		"column": "received_at"
	},
	"file_name": {
		"field_type": FieldType.STRING,
		"allowed_operations": [Operation.EQUALS, Operation.NOT_EQUALS, Operation.CONTAINS, Operation.NOT_CONTAINS],
		"is_column": True,
		"schema": "gmail",
		"table": "MessageAttachment",
		"column": "file_name"
	},
	"size": {
		"field_type": FieldType.NUMBER,
		"allowed_operations": [Operation.EQUALS, Operation.NOT_EQUALS, Operation.GREATER_THAN, Operation.LESS_THAN, Operation.GREATER_THAN_EQUALS, Operation.LESS_THAN_EQUALS],
		"is_column": True,
		"schema": "gmail",
		"table": "MessageAttachment",
		"column": "size"
	},
	"has_attachment": {
		"field_type": FieldType.BOOLEAN,
		"allowed_operations": [Operation.EQUALS, Operation.NOT_EQUALS],
		"is_column": False,
		"schema": "gmail",
		"table": "MessageAttachment",
		"column": None
	},
	"label": {
		"field_type": FieldType.STRING,
		"allowed_operations": [Operation.IN, Operation.NOT_IN],
		"is_column": True,
		"schema": "gmail",
		"table": "MessageLabel",
		"column": "name"
	},
	"text_body": {
		"field_type": FieldType.STRING,
		"allowed_operations": [Operation.CONTAINS, Operation.NOT_CONTAINS],
		"is_column": True,
		"schema": "gmail",
		"table": "MessageDetail",
		"column": "text_body"
	}
}