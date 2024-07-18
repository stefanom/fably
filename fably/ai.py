import openai
import logging


class AIBase(object):

    def __init__(self, ctx):
        self.ctx = ctx

    async def chat(self, query, prompt):
        raise NotImplementedError()

    async def speech(self, text, audio_file_path, index=0):
        raise NotImplementedError()

    async def transcriptions(self, audio_file):
        raise NotImplementedError()


class OpenAIClient(AIBase):

    def __init__(self, ctx):
        AIBase.__init__(self, ctx)
        self.stt_client = openai.AsyncClient(base_url=ctx.stt_url,
                                             api_key=ctx.api_key)
        self.llm_client = openai.AsyncClient(base_url=ctx.llm_url,
                                             api_key=ctx.api_key)
        self.tts_client = openai.AsyncClient(base_url=ctx.tts_url,
                                             api_key=ctx.api_key)

    async def chat(self, query, prompt):
        completion = await self.llm_client.chat.completions.create(
            stream=True,
            model=self.ctx.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": query
                },
            ],
            temperature=self.ctx.temperature,
            max_tokens=self.ctx.max_tokens,
        )

        async for chunk in completion:
            if len(chunk.choices) == 0:
                continue

            fragment = chunk.choices[0].delta.content
            if fragment is None:
                break

            yield fragment

    async def speech(self, text, audio_file_path, index=0):
        response = await self.tts_client.audio.speech.create(
            input=text,
            model=self.ctx.tts_model,
            voice=self.ctx.tts_voice,
            response_format=self.ctx.tts_format,
        )

        logging.debug("Saving audio for paragraph %i...", index)
        response.write_to_file(audio_file_path)
        logging.debug("Paragraph %i audio saved at %s", index, audio_file_path)

    async def transcriptions(self, audio_file):
        with open(audio_file, "rb") as query:
            response = await self.stt_client.audio.transcriptions.create(
                model=self.ctx.stt_model,
                language=self.ctx.language,
                file=query,
            )

            return response.text
