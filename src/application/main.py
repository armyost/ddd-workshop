from dataclasses import asdict

from domain.dropped_fraction import FractionType
from domain.invoicing.invoice_handler import InvoiceHandler
from domain.price import Currency, Price
from domain.prices import (
    ExcemptionPricePolicy,
    FixedPricePolicy,
    PriceCatalog,
    PriceKey,
)
from domain.visits import VisitorType
from domain.weight import Weight
from flask import Flask, request
from infrastructure.http_external_users import HttpExternalUsers
from infrastructure.in_memory_message_bus import InMemoryMessageBus
from infrastructure.in_memory_visit_histories import (
    InMemoryVisitHistories,
)
from messaging.subscriber import Subscriber

from .context import Context
from .price_calculator import PriceCalculator

app = Flask(__name__)

prices = (
    PriceCatalog()
    .add(
        PriceKey(FractionType.GREEN_WASTE, VisitorType.PRIVATE, "Pineville"),
        FixedPricePolicy(Price(0.10, Currency.EUR), FractionType.GREEN_WASTE),
    )
    .add(
        PriceKey(FractionType.CONSTRUCTION_WASTE, VisitorType.PRIVATE, "Pineville"),
        FixedPricePolicy(Price(0.15, Currency.EUR), FractionType.CONSTRUCTION_WASTE),
    )
    .add(
        PriceKey(FractionType.GREEN_WASTE, VisitorType.PRIVATE, "Oak City"),
        FixedPricePolicy(Price(0.08, Currency.EUR), FractionType.GREEN_WASTE),
    )
    .add(
        PriceKey(FractionType.CONSTRUCTION_WASTE, VisitorType.PRIVATE, "Oak City"),
        FixedPricePolicy(Price(0.19, Currency.EUR), FractionType.CONSTRUCTION_WASTE),
    )
    .add(
        PriceKey(FractionType.GREEN_WASTE, VisitorType.BUSINESS, "Pineville"),
        FixedPricePolicy(Price(0.12, Currency.EUR), FractionType.GREEN_WASTE),
    )
    .add(
        PriceKey(FractionType.CONSTRUCTION_WASTE, VisitorType.BUSINESS, "Pineville"),
        FixedPricePolicy(Price(0.13, Currency.EUR), FractionType.CONSTRUCTION_WASTE),
    )
    .add(
        PriceKey(FractionType.GREEN_WASTE, VisitorType.BUSINESS, "Oak City"),
        FixedPricePolicy(Price(0.08, Currency.EUR), FractionType.GREEN_WASTE),
    )
    .add(
        PriceKey(FractionType.CONSTRUCTION_WASTE, VisitorType.BUSINESS, "Oak City"),
        ExcemptionPricePolicy(
            FractionType.CONSTRUCTION_WASTE,
            tiers={
                Weight(0): Price(0.21, Currency.EUR),
                Weight(1000): Price(0.29, Currency.EUR),
            },
        ),
    )
)

context = Context(
    external_users=HttpExternalUsers(),
    visit_histories=InMemoryVisitHistories(prices=prices),
    message_bus=InMemoryMessageBus()
)


@app.route("/")
def hello_world():
    return {"status": "OK"}


# This is run every time a scenario starts, in case you need to reset certain
# things at the beginning of a scenario
@app.post("/startScenario")
def start_scenario():
    app.logger.info("starting scenario")
    global context
    context = Context(
        external_users=HttpExternalUsers(),
        visit_histories=InMemoryVisitHistories(prices=prices),
        message_bus=InMemoryMessageBus()
    )

    invoice_handler = InvoiceHandler()
    sub = getattr(invoice_handler, "handle")
    context.message_bus.subscribe(sub)

    return {}


@app.post("/calculatePrice")
def calculate_price():
    visit_data = request.get_json()
    app.logger.info(f"calculate price request: {visit_data}")

    response = PriceCalculator(
        external_users=context.external_users,
        visit_histories=context.visit_histories,
        message_bus=context.message_bus
    ).calculate(visit_data)

    app.logger.info(f"calculate price response: {response}")
    return asdict(response)
