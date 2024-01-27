import asyncio
import multiprocessing

from consumer import consume
from cfg import get_settings

settings = get_settings()


def run_async_task(queue_name, worker):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(consume(queue_name, worker))
    loop.run_until_complete(future)


if __name__ == "__main__":
    clone_process = 3
    splitter_process = 3
    cover_process = 2
    tts_process = 4

    processes = cover_process + splitter_process + clone_process + tts_process

    pool = multiprocessing.Pool(processes=processes)

    tts_consumers = [
        pool.apply_async(
            run_async_task,
            args=(
                "tts",
                i,
            ),
        )
        for i in range(tts_process)
    ]

    clone_consumers = [
        pool.apply_async(
            run_async_task,
            args=(
                "clone",
                i,
            ),
        )
        for i in range(clone_process)
    ]

    splitter_consumers = [
        pool.apply_async(
            run_async_task,
            args=(
                "split",
                i,
            ),
        )
        for i in range(splitter_process)
    ]

    cover_consumers = [
        pool.apply_async(
            run_async_task,
            args=(
                "cover",
                i,
            ),
        )
        for i in range(splitter_process)
    ]

    tasks = splitter_consumers + cover_consumers + clone_consumers

    pool.close()
    pool.join()

    for task in tasks:
        task.get()
