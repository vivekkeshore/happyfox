from app.models import FilterField
from app.db_layer.base_repo import BaseRepo
from app.models.enum_model import FieldType, Operation

column_values = [
	{
		"field_name": "from_address",
		"field_type": FieldType.STRING,
		"allowed_operations": [Operation.EQUALS, Operation.NOT_EQUALS, Operation.CONTAINS, Operation.NOT_CONTAINS],
		"is_column": True,
		"schema": "gmail",
		"table": "Message",
		"column": "from_address"
	},
	{
		"field_name": "to",
		"field_type": FieldType.STRING,
		"allowed_operations": [Operation.EQUALS, Operation.NOT_EQUALS, Operation.CONTAINS, Operation.NOT_CONTAINS],
		"is_column": True,
		"schema": "gmail",
		"table": "Message",
		"column": "to"
	},
	{
		"field_name": "cc",
		"field_type": FieldType.STRING,
		"allowed_operations": [Operation.EQUALS, Operation.NOT_EQUALS, Operation.CONTAINS, Operation.NOT_CONTAINS],
		"is_column": True,
		"schema": "gmail",
		"table": "Message",
		"column": "cc"
	},
	{
		"field_name": "bcc",
		"field_type": FieldType.STRING,
		"allowed_operations": [Operation.EQUALS, Operation.NOT_EQUALS, Operation.CONTAINS, Operation.NOT_CONTAINS],
		"is_column": True,
		"schema": "gmail",
		"table": "Message",
		"column": "bcc"
	},
	{
		"field_name": "subject",
		"field_type": FieldType.STRING,
		"allowed_operations": [Operation.EQUALS, Operation.NOT_EQUALS, Operation.CONTAINS, Operation.NOT_CONTAINS],
		"is_column": True,
		"schema": "gmail",
		"table": "Message",
		"column": "subject"
	},
	{
		"field_name": "received_at",
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
	{
		"field_name": "file_name",
		"field_type": FieldType.STRING,
		"allowed_operations": [Operation.EQUALS, Operation.NOT_EQUALS, Operation.CONTAINS, Operation.NOT_CONTAINS],
		"is_column": True,
		"schema": "gmail",
		"table": "MessageAttachment",
		"column": "file_name"
	},
	{
		"field_name": "size",
		"field_type": FieldType.NUMBER,
		"allowed_operations": [Operation.EQUALS, Operation.NOT_EQUALS, Operation.GREATER_THAN, Operation.LESS_THAN, Operation.GREATER_THAN_EQUALS, Operation.LESS_THAN_EQUALS],
		"is_column": True,
		"schema": "gmail",
		"table": "MessageAttachment",
		"column": "size"
	},
	{
		"field_name": "has_attachment",
		"field_type": FieldType.BOOLEAN,
		"allowed_operations": [Operation.EQUALS, Operation.NOT_EQUALS],
		"is_column": False,
		"schema": "gmail",
		"table": "MessageAttachment",
		"column": None
	},
	{
		"field_name": "label",
		"field_type": FieldType.STRING,
		"allowed_operations": [Operation.IN, Operation.NOT_IN],
		"is_column": True,
		"schema": "gmail",
		"table": "MessageLabel",
		"column": "name"
	},
	{
		"field_name": "text_body",
		"field_type": FieldType.STRING,
		"allowed_operations": [Operation.CONTAINS, Operation.NOT_CONTAINS],
		"is_column": True,
		"schema": "gmail",
		"table": "MessageDetail",
		"column": "text_body"
	}
]


def seed_filter_fields():
	repo = BaseRepo(FilterField)
	for column_value in column_values:
		item = repo.get_by_col("field_name", column_value["field_name"])
		if item:
			print(f"Filter Field {column_value['field_name']} already exists.")
			continue
		repo.create(column_value)
		print(f"Filter Field {column_value['field_name']} created successfully.")


if __name__ == "__main__":
	seed_filter_fields()
