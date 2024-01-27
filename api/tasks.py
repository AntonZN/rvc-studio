import argparse
import asyncio
import aiofiles.os
import arrow

from tortoise import Tortoise
from app.core.config import get_settings
from app.models.records import Record, TTS

settings = get_settings()

TASKS = ["remover"]


async def init_db():
    await Tortoise.init(
        db_url=settings.DATABASE_URI,
        modules={"models": settings.MODELS},
    )


async def remove_files(files):
    for file in files:
        try:
            print(f"remove {file}")
            await aiofiles.os.remove(file)
        except FileNotFoundError:
            pass


async def remove_records_older_than_24_hours():
    await init_db()

    async for record in Record.filter(
        created_at__lte=str(arrow.utcnow().shift(hours=-24))
    ).values_list(
        "id", "file_path", "vocal_path", "instrumental_path", "clone_path", "cover_path"
    ):
        files = [
            record.get("file_path"),
            record.get("vocal_path"),
            record.get("instrumental_path"),
            record.get("clone_path"),
            record.get("cover_path"),
        ]

        files = [file for file in files if file is not None and file != ""]

        await remove_files(files)
        await Record.filter(id=record.get("id")).delete()


async def remove_tts_older_than_24_hours():
    files = []

    async for tts in TTS.filter(created_at__lte=str(arrow.utcnow().shift(hours=-24))):
        files.append(tts.voice_path)
        await tts.delete()

    await remove_files(files)


async def main(task):
    if task == "remover":
        await remove_records_older_than_24_hours()
        await remove_tts_older_than_24_hours()
    else:
        raise ValueError(
            f'Unknown task name: {task}. Available tasks are {", ".join(TASKS)}'
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tasks")
    parser.add_argument("task", type=str, help="Input task name")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.task))
    except ValueError as e:
        print(e)
