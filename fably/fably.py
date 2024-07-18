"""
Main Fably logic.
"""

import asyncio
import concurrent.futures
import logging
import shutil
import time
import threading
from ai import OpenAIClient

try:
    from gpiozero import Button
except (ImportError, NotImplementedError):
    Button = None

from fably import utils


def generate_story(ctx, query, prompt):
    """
    Generates a story stream based on a given query and prompt using the OpenAI API and persists the information
    about the models used to generate the story to a file.
    """

    return ctx.ai.chat(query, prompt)


async def synthesize_audio(ctx, story_path, index, text=None):
    """
    Fetches TTS audio for a given paragraph of a story and saves it to a file.
    """
    logging.debug("Synthesizing audio for paragraph %i...", index)

    audio_file_path = story_path / f"paragraph_{index}.{ctx.tts_format}"

    if audio_file_path.exists():
        logging.debug("Paragraph %i audio already exists at %s", index, audio_file_path)
        return audio_file_path

    if not text:
        text_file_path = story_path / f"paragraph_{index}.txt"
        if text_file_path.exists():
            logging.debug(
                "Reading paragraph %i text from %s ...", index, text_file_path
            )
            text = utils.read_from_file(text_file_path)
        else:
            raise ValueError(f"No text found for paragraph {index} in {story_path}")

    await ctx.ai.speech(text, audio_file_path, index)
    return audio_file_path


async def writer(ctx, story_queue, query=None):
    """
    Creates a story based on a voice query.

    If a textual query is given, it is used. If not, it records sound until silence,
    then transcribes the voice query.

    Then it uses a large generative language model to create a story based on the query,
    processes the returned content as a stream, chunks it into paragraphs and appends them
    to the queue for downstream processing.
    """
    if query:
        query_local = "n/a"
        voice_query_file = None
    else:
        utils.play_sound("what_story", audio_driver=ctx.sound_driver)

        voice_query, query_sample_rate, query_local = utils.record_until_silence(
            ctx.recognizer, ctx.trim_first_frame
        )
        query, voice_query_file = await utils.transcribe(
            ctx.ai,
            voice_query,
            query_sample_rate,
            ctx.queries_path,
        )
        logging.info("Voice query: %s [%s]", query, query_local)

    if not query.lower().startswith(ctx.query_guard):
        logging.warning(
            "Sorry, I can only run queries that start with '%s' and '%s' does not",
            ctx.query_guard,
            query,
        )
        utils.play_sound("sorry", audio_driver=ctx.sound_driver)
        await story_queue.put(None)  # Indicates that we're done
        return

    story_path = ctx.stories_path / utils.query_to_filename(
        query, prefix=ctx.query_guard
    )
    if ctx.ignore_cache or (
        not ctx.ignore_cache and not story_path.exists() and not story_path.is_dir()
    ):
        logging.debug("Creating story folder at %s", story_path)
        story_path.mkdir(parents=True, exist_ok=True)

        logging.debug("Writing model info to disk...")
        ctx.persist_runtime_params(
            story_path / "info.yaml",
            query=query,
            query_local=query_local,
        )

        # This file will not exist when the query is passed as an argument
        if voice_query_file:
            logging.debug("Copying the original voice query...")
            shutil.move(voice_query_file, story_path / "voice_query.wav")

        logging.debug("Reading prompt...")
        prompt = utils.read_from_file(ctx.prompt_file)

        logging.debug("Creating story...")
        story_stream = generate_story(ctx, query, prompt)

        index = 0
        paragraph = []

        logging.debug("Iterating over the story stream to capture paragraphs...")
        async for chunk in story_stream:
            fragment = chunk

            paragraph.append(fragment)

            if fragment.endswith("\n\n"):
                paragraph_str = "".join(paragraph)
                logging.info("Paragraph %i: %s", index, paragraph_str)
                utils.write_to_file(
                    story_path / f"paragraph_{index}.txt", paragraph_str
                )
                await story_queue.put((story_path, index, paragraph_str))
                index += 1
                paragraph = []

        logging.debug("Finished processing the story stream.")
    else:
        logging.debug("Reading cached story at %s", story_path)
        for index in range(len(list(story_path.glob("paragraph_*.txt")))):
            await story_queue.put((story_path, index, None))

    logging.debug("Done processing the story.")
    await story_queue.put(None)  # Indicates that we're done


async def reader(ctx, story_queue, reading_queue):
    """
    Processes the queue of paragraphs and sends them off to be read
    and synthezized into audio files to be read by the speaker.
    """
    while ctx.talking:
        item = await story_queue.get()
        if item is None:
            logging.debug("Done reading the story.")
            await reading_queue.put(None)
            break

        story_path, index, paragraph = item

        audio_file = await synthesize_audio(ctx, story_path, index, paragraph)
        await reading_queue.put(audio_file)


async def speaker(ctx, reading_queue):
    """
    Processes the queue of audio files and plays them.
    """
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        while ctx.talking:
            audio_file = await reading_queue.get()
            if audio_file is None:
                logging.debug("Done playing the story.")
                break

            def speak():
                ctx.leds.stop()
                utils.play_audio_file(audio_file, ctx.sound_driver)

            await loop.run_in_executor(pool, speak)


async def run_story_loop(ctx, query=None, terminate=False):
    """
    The main loop for running the story.
    """
    ctx.talking = True
    ctx.leds.start()

    story_queue = asyncio.Queue()
    reading_queue = asyncio.Queue()

    writer_task = asyncio.create_task(writer(ctx, story_queue, query))
    reader_task = asyncio.create_task(reader(ctx, story_queue, reading_queue))
    speaker_task = asyncio.create_task(speaker(ctx, reading_queue))

    await asyncio.gather(writer_task, reader_task, speaker_task)

    ctx.leds.stop()
    ctx.talking = False

    if terminate:
        ctx.running = False


def tell_story(ctx, query=None, terminate=False):
    """
    Forks off a thread to tell the story.
    """

    def tell_story_wrapper():
        asyncio.run(run_story_loop(ctx, query, terminate))

    threading.Thread(target=tell_story_wrapper).start()


def main(ctx, query=None):
    """
    The main Fably loop.
    """

    ctx.ai = OpenAIClient(ctx)

    # If a query is not present, introduce ourselves
    if not query:
        ctx.recognizer = utils.get_speech_recognizer(ctx.models_path, ctx.sound_model)

    if ctx.loop and Button:
        ctx.leds.start()
        utils.play_sound("startup", audio_driver=ctx.sound_driver)

        # Let's introduce ourselves
        utils.play_sound("hi", audio_driver=ctx.sound_driver)

        def pressed(ctx):
            ctx.press_time = time.time()
            logging.debug("Button pressed")

        def released(ctx):
            release_time = time.time()
            pressed_for = release_time - ctx.press_time
            logging.debug("Button released after %f seconds", pressed_for)

            if pressed_for < ctx.button.hold_time:
                if not ctx.talking:
                    logging.info("This is a short press. Telling a story...")
                    tell_story(ctx, terminate=False)
                    logging.debug("Forked the storytelling thread")
                else:
                    logging.debug(
                        "This is a short press, but we are already telling a story."
                    )

        def held(ctx):
            logging.info("This is a hold press. Shutting down.")
            ctx.running = False

        ctx.button = Button(pin=ctx.button_gpio_pin, hold_time=ctx.hold_time)
        ctx.button.when_pressed = lambda: pressed(ctx)
        ctx.button.when_released = lambda: released(ctx)
        ctx.button.when_held = lambda: held(ctx)

        # Give instruction for loop mode
        utils.play_sound("instructions", audio_driver=ctx.sound_driver)

        # Stop the LEDs once we're ready.
        ctx.leds.stop()
    else:
        # Here the query can be None, but it's ok.
        # We will record one from the user in that case.
        tell_story(ctx, query=query, terminate=True)

    # Keep the main thread from existing until we're done.
    while ctx.running:
        time.sleep(1.0)

    utils.play_sound("bye", audio_driver=ctx.sound_driver)

    logging.debug("Shutting down... bye!")
