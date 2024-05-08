"""
Main Fably logic.
"""

import asyncio
import concurrent.futures
import logging
import shutil

from fably import utils


def generate_story(ctx, query, prompt):
    """
    Generates a story stream based on a given query and prompt using the OpenAI API and persists the information
    about the models used to generate the story to a file.
    """

    return ctx.async_client.chat.completions.create(
        stream=True,
        model=ctx.llm_model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": query},
        ],
        temperature=ctx.temperature,
        max_tokens=ctx.max_tokens,
    )


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

    response = await ctx.async_client.audio.speech.create(
        input=text,
        model=ctx.tts_model,
        voice=ctx.tts_voice,
        response_format=ctx.tts_format,
    )

    logging.debug("Saving audio for paragraph %i...", index)
    response.write_to_file(audio_file_path)
    logging.debug("Paragraph %i audio saved at %s", index, audio_file_path)

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
    if not query:
        voice_query, query_sample_rate, query_local = utils.record_until_silence(
            ctx.recognizer, ctx.trim_first_frame
        )
        query, voice_query_file = utils.transcribe(
            ctx.sync_client, voice_query, ctx.stt_model, ctx.language, query_sample_rate
        )
        logging.info("Voice query: %s [%s]", query, query_local)

    logging.debug("Transcription of voice query: %s", query)

    if not query.lower().startswith(ctx.query_guard):
        print(
            f"Sorry, I can only run queries that start with '{ctx.query_guard}' and '{query}' does not"
        )
        await story_queue.put(None)  # Indicates that we're done
        return

    story_path = ctx.stories_home / utils.query_to_filename(
        query, prefix=ctx.query_guard
    )
    if ctx.ignore_cache or (
        not ctx.ignore_cache and not story_path.exists() and not story_path.is_dir()
    ):
        logging.debug("Creating story folder at %s", story_path)
        story_path.mkdir(parents=True, exist_ok=True)

        logging.debug("Writing model info to disk...")
        ctx.persist_runtime_params(
            story_path / "info.yaml", query=query, query_local=query_local
        )

        logging.debug("Copying the original voice query...")
        shutil.move(voice_query_file, story_path / "voice_query.wav")

        logging.debug("Reading prompt...")
        prompt = utils.read_from_file(ctx.prompt_file)

        logging.debug("Creating story...")
        story_stream = await generate_story(ctx, query, prompt)

        index = 0
        paragraph = []

        logging.debug("Iterating over the story stream to capture paragraphs...")
        async for chunk in story_stream:
            fragment = chunk.choices[0].delta.content
            if fragment is None:
                break

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
    while True:
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
        while True:
            audio_file = await reading_queue.get()
            if audio_file is None:
                logging.debug("Done playing the story.")
                break

            def speak():
                utils.play_audio_file(audio_file, ctx.audio_driver)

            await loop.run_in_executor(pool, speak)


async def main(ctx, query):
    story_queue = asyncio.Queue()
    reading_queue = asyncio.Queue()

    writer_task = asyncio.create_task(writer(ctx, story_queue, query))
    reader_task = asyncio.create_task(reader(ctx, story_queue, reading_queue))
    speaker_task = asyncio.create_task(speaker(ctx, reading_queue))

    await asyncio.gather(writer_task, reader_task, speaker_task)
