import json

import loguru

from pathlib import Path

from asgiref.sync import async_to_sync

from db_models import Status, RVCModel, Record
from services.cover import create_cover
from services.cloning import clone_only
from services.splitter import split_only


def process(topic, record, model_name, clone_type):
    if topic == "cover":
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
    elif topic == "split":
        result = split_only(record.id, record.file_path)
        if result:
            record.status = Status.DONE
            record.vocal_path = result[0]
            record.instrumental_path = result[1]
        else:
            record.status = Status.ERROR
    elif topic == "clone":
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


async def handle(poll, amq_message: str) -> None:
    loguru.logger.debug("HANDLE START")
    try:
        message_data = json.loads(amq_message)
    except json.JSONDecodeError:
        return None

    try:
        topic = message_data.pop("topic")
    except AttributeError:
        loguru.logger.error(
            f"Message content type must be dict, not {type(message_data)}"
        )
        return None

    record = await Record.get(id=message_data["record_id"])

    if topic in ["cover", "clone"]:
        model = await RVCModel.get(id=message_data["model_id"])
        model_name = Path(model.file).stem
        clone_type = message_data["type"]
    else:
        model_name = None
        clone_type = None

        poll.apply_async(process, args=(topic, record, model_name, clone_type))
        loguru.logger.debug("HANDLE Process Start")
