#!/usr/bin/env python3
"""Make sure asyncio works as expected."""

import asyncio
import concurrent.futures
import time

import click

WRITER_TIME = 2
READER_TIME = 4
SPEAKER_TIME = 5


async def writer(paragraphs, story_queue):
    for index in range(paragraphs):
        print(f"> Generating paragraph {index}")
        await asyncio.sleep(WRITER_TIME)
        print(f"< Generating paragraph {index}")
        await story_queue.put(index)

    await story_queue.put(None)


async def synthesize(index):
    print(f">>> Synthesizing paragraph {index}")
    await asyncio.sleep(READER_TIME)
    print(f"<<< Synthesizing paragraph {index}")
    return index


async def reader(story_queue, reading_queue):
    while True:
        paragraph_index = await story_queue.get()
        if paragraph_index is None:
            await reading_queue.put(None)
            break

        audio_index = await synthesize(paragraph_index)

        await reading_queue.put(audio_index)


async def speaker(multithreaded, reading_queue):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        while True:
            audio_index = await reading_queue.get()
            if audio_index is None:
                break

            def speak():
                print(f">>>>> Speaking paragraph {audio_index}")
                time.sleep(SPEAKER_TIME)
                print(f"<<<<< Speaking paragraph {audio_index}")

            async def aspeak():
                speak()

            if multithreaded:
                await loop.run_in_executor(pool, speak)
            else:
                await aspeak()


async def async_main(multithreaded, paragraphs):
    story_queue = asyncio.Queue()
    reading_queue = asyncio.Queue()

    writer_task = asyncio.create_task(writer(paragraphs, story_queue))
    reader_task = asyncio.create_task(reader(story_queue, reading_queue))
    speaker_task = asyncio.create_task(speaker(multithreaded, reading_queue))

    await asyncio.gather(writer_task, reader_task, speaker_task)


@click.command()
@click.option(
    "--multithreaded/--singlethreaded",
    default=True,
    help="Whether to use multithreading or not.",
)
@click.option(
    "--paragraphs",
    default=5,
    help="The number of paragraphs to generate.",
    type=int,
)
def main(multithreaded, paragraphs):

    if multithreaded:
        print(f"Multi threaded. Generating {paragraphs} paragraphs...")
    else:
        print(f"Single threaded. Generating {paragraphs} paragraphs...")

    now = time.time()

    asyncio.run(async_main(multithreaded, paragraphs))

    elapsed = time.time() - now

    # In a perfect world, we only wait for the first paragraph to be generated
    # and its audio to be generated. After that, all writing and reading should
    # be done concurrently, not getting in the way of the speaker just
    # playing the synthetized audio files.
    #
    # NOTE: This assumes that playing the audio file is slower than generating its text
    # or synthetizing its audio.
    expected = WRITER_TIME + READER_TIME + paragraphs * SPEAKER_TIME

    # Here we see how close we get to what we desire.
    delta = elapsed - expected

    print(f"Done in {elapsed:.2f} seconds, {delta:.2f} seconds more than optimal.")


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
