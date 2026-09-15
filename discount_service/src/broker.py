from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue, ExchangeType

broker = RabbitBroker()

accounts_exchange = RabbitExchange("accounts", type=ExchangeType.TOPIC, durable=True)
account_created_queue = RabbitQueue(
    "orders.account_created", routing_key="account.created", durable=True
)
orders_exchange = RabbitExchange("orders", type=ExchangeType.TOPIC, durable=True)
