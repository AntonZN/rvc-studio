import asyncio
import json
from pathlib import Path

import aio_pika
import loguru
from aio_pika import exceptions
from aio_pika.abc import AbstractRobustConnection
from aio_pika.pool import Pool
from tortoise import Tortoise

from cfg import get_settings
from db_models import Status, RVCModel, Record, TTS

from services.cover import create_cover
from services.cloning import clone_only
from services.splitter import split_only
from services.tts import tts as create_tts

settings = get_settings()


def process_tts(tts_obj, text, lang, speaker, model_name):
    loguru.logger.debug("RUN TTS")
    result = create_tts(
        tts_obj.id,
        model_name,
        text,
        lang,
        speaker,
    )

    if result:
        tts_obj.status = Status.DONE
        tts_obj.voice_path = result
        loguru.logger.debug(result)
    else:
        tts_obj.status = Status.ERROR


def process(queue_name, record, model_name, clone_type):
    if queue_name == "cover":
        result = create_cover(
            record.id,
            record.file_path,
            model_name,
            clone_type,
        )
        if result:
            record.status = Status.DONE
            record.cover_path = result
            loguru.logger.debug(result)
        else:
            record.status = Status.ERROR
    elif queue_name == "split":
        result = split_only(record.id, record.file_path)
        if result:
            record.status = Status.DONE
            record.vocal_path = result[0]
            record.instrumental_path = result[1]
        else:
            record.status = Status.ERROR
    elif queue_name == "clone":
        result = clone_only(
            record.id,
            record.file_path,
            model_name,
            clone_type,
        )
        if result:
            record.status = Status.DONE
            record.clone_path = result
            loguru.logger.debug(result)
        else:
            record.status = Status.ERROR

    return record


async def handle(queue_name, amq_message: str) -> None:
    loguru.logger.debug(f"HANDLE {queue_name}")
    try:
        message_data = json.loads(amq_message)
    except json.JSONDecodeError:
        return None

    if queue_name != "tts":
        record = await Record.get(id=message_data["record_id"])

        if queue_name in ["cover", "clone"]:
            try:
                model = await RVCModel.get(id=message_data["model_id"])
            except Exception as e:
                record.status = Status.ERROR
                await record.save()
                return
            model_name = Path(model.file).stem
            clone_type = message_data["type"]
        else:
            model_name = None
            clone_type = None

        try:
            process(queue_name, record, model_name, clone_type)
        except Exception:
            record.status = Status.ERROR

        await record.save()
    else:
        loguru.logger.debug(f"TTS {message_data}")
        tts_obj = await TTS.get(id=message_data["tts_id"])

        try:
            model = await RVCModel.get(id=message_data["model_id"])
        except Exception as e:
            tts_obj.status = Status.ERROR
            await tts_obj.save()
            return

        model_name = Path(model.file).stem

        try:
            process_tts(
                tts_obj,
                message_data["text"],
                message_data["lang"],
                message_data["speaker"],
                model_name,
            )
        except Exception:
            tts_obj.status = Status.ERROR

        await tts_obj.save()


async def get_connection() -> AbstractRobustConnection:
    return await aio_pika.connect_robust(
        host=settings.RABBITMQ_HOST,
        login=settings.RABBITMQ_USERNAME,
        password=settings.RABBITMQ_PASSWORD,
        timeout=3600,
    )

async def get_channel(connection_pool) -> aio_pika.Channel:
    await asyncio.sleep(10)
    async with connection_pool.acquire() as connection:
        return await connection.channel()


async def consume(loop, queue_name: str, worker) -> None:
    await Tortoise.init(db_url=settings.DATABASE_URI, modules={"models": ["db_models"]})

    connection_pool: Pool = Pool(get_connection, max_size=5, loop=loop)
    channel_pool: Pool = Pool(get_channel, connection_pool, max_size=5, loop=loop)


    while True:
        async with channel_pool.acquire() as channel:
            await channel.set_qos(1)
            exchange = await channel.declare_exchange(
                queue_name, aio_pika.ExchangeType.DIRECT
            )

            queue = await channel.declare_queue(
                queue_name,
                durable=True,
                auto_delete=False,
            )
            await queue.bind(exchange, queue_name)

            loguru.logger.debug(f"# Worker [{worker}] Start listing queue {queue_name}")

            while True:
                try:
                    message = await queue.get(no_ack=False)
                except exceptions.QueueEmpty:
                    await asyncio.sleep(5)
                    continue

                if message is None:
                    await asyncio.sleep(5)
                    continue

                loguru.logger.debug(f"Worker[{worker}][{queue_name}] New message {message})")
                await handle(queue_name, message.body.decode())
                loguru.logger.debug(f"Worker[{worker}][{queue_name}] Message ACK")
                await message.ack()


