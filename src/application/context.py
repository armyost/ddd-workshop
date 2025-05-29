from attrs import define, field
from domain.external_users import ExternalUsers
from domain.visit_history import VisitHistories
from messaging.message_bus import MessageBus


@define
class Context:
    external_users: ExternalUsers = field(kw_only=True)
    visit_histories: VisitHistories = field(kw_only=True)
    message_bus: MessageBus = field(kw_only=True)
