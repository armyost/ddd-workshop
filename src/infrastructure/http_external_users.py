import os
from typing import Iterator

import requests
from domain.external_users import ExternalUser, ExternalUsers


class HttpExternalUsers(ExternalUsers):
    def get_user_by_id(self, id: str) -> ExternalUser:
        all_users = self.__get_users()

        return next(user for user in all_users if user.id == id)

    def __get_users(self) -> Iterator[ExternalUser]:
        auth_token = os.environ["DDD_AUTH_TOKEN"]
        workshop_id = os.environ["WORKSHOP_ID"]
        workshop_server_url = os.environ["WORKSHOP_SERVER_URL"]
        r = requests.get(
            f"{workshop_server_url}/api/users",
            headers={"x-auth-token": auth_token, "x-workshop-id": workshop_id},
        )
        return (
            ExternalUser(
                json_user["type"],
                json_user["id"],
                json_user["address"],
                json_user["city"],
                json_user.get("email", ""),
            )
            for json_user in r.json()
        )
