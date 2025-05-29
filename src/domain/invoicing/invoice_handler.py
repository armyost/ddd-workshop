import os
import requests

from domain.events.event import Event
from domain.events.price_was_calculated import PriceWasCalculated
from domain.visits import VisitorType


class InvoiceHandler:
    def handle(self, ev: Event) -> None:
        if isinstance(ev, PriceWasCalculated):
            auth_token = os.environ["DDD_AUTH_TOKEN"]
            workshop_id = os.environ["WORKSHOP_ID"]
            workshop_server_url = os.environ["WORKSHOP_SERVER_URL"]

            priceWasCalculated = ev

            if priceWasCalculated.visitor.type == VisitorType.BUSINESS:
                payload = {'email': priceWasCalculated.visitor.email, 'invoice_amount': priceWasCalculated.price.amount,
                           'invoice_currency': str(priceWasCalculated.price.currency)}
                r = requests.post(f"{workshop_server_url}/api/invoice",
                                  json=payload,
                                  headers={"x-auth-token": auth_token, "x-workshop-id": workshop_id},
                                  )