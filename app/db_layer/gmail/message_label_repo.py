from app.db_layer.base_repo import BaseRepo
from app.db_layer.sql_context import SqlContext
from app.lib.singleton import Singleton
from app.models.gmail.message_label import MessageLabel


class MessageLabelRepo(BaseRepo, metaclass=Singleton):
	def __init__(self):
		super().__init__(MessageLabel)

	def get_message_label_by_message_and_label_id(self, label_id: str, message_id: str) -> MessageLabel:
		query = self.query.where(
			self.model.label_id == label_id,
			self.model.message_id == message_id
		)

		with SqlContext() as sql_context:
			result = sql_context.execute(query)

		return result.scalar()
