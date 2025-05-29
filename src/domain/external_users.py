from __future__ import annotations
import abc
from dataclasses import dataclass


@dataclass(frozen=True)
class ExternalUser:
    type: str
    id: str
    address: str
    city: str
    email: str


class ExternalUsers(abc.ABC):
    @abc.abstractmethod
    def get_user_by_id(self, user: str) -> ExternalUser:
        raise NotImplementedError
