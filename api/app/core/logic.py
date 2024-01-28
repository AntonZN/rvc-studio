import json

import aio_pika
from aio_pika import DeliveryMode, Message, connect
from loguru import logger


from app.core.config import get_settings

settings = get_settings()


async def publish(message: Message, key):
    logger.debug(f"Publishing message: {message.body}")

    connection = await connect(
        f"amqp://{settings.RABBITMQ_USERNAME}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}/"
    )
    message.headers = {"expiration": "600000"}
    async with connection:
        channel = await connection.channel()

        try:
            exchange = await channel.get_exchange(key, ensure=True)
        except Exception:
            exchange = await channel.declare_exchange(key, aio_pika.ExchangeType.DIRECT)

        await exchange.publish(message, routing_key=key)


async def publish_record(
    key,
    message_data,
):
    message_body = json.dumps(message_data).encode()
    message = Message(
        message_body,
        delivery_mode=DeliveryMode.PERSISTENT,
    )
    await publish(message, key=key)
