import gradio as gr
import openai
import soundfile as sf

from fably import fably
from fably import utils

API_KEY = "ignored"
STT_URL = "http://127.0.0.1:5000/v1"
STT_MODEL = "ignored"
LLM_URL = "http://192.168.86.36:11434/v1"
LLM_MODEL = "mistral:latest"
TTS_URL = "http://127.0.0.1:5001/v1"
TTS_MODEL = "ignored"
TTS_VOICE = "ignored"  # for now
LANGUAGE = "en"


class Context:
    def __init__(self) -> None:
        self.stt_client = openai.Client(base_url=STT_URL, api_key=API_KEY)
        self.llm_client = openai.Client(base_url=LLM_URL, api_key=API_KEY)
        self.tts_client = openai.Client(base_url=TTS_URL, api_key=API_KEY)
        self.llm_model = LLM_MODEL
        self.temperature = 1.0
        self.max_tokens = 2000
        self.tts_model = TTS_MODEL
        self.tts_voice = TTS_VOICE


ctx = Context()


def transcribe(audio_file):
    with open(audio_file, "rb") as query:
        response = ctx.stt_client.audio.transcriptions.create(
            model=STT_MODEL, language=LANGUAGE, file=query
        )
        return response.text


def generate_story(query, prompt, temperature, max_tokens):
    ctx.temperature = temperature
    ctx.max_tokens = max_tokens
    chunks = []
    for chunk in fably.generate_story(ctx, query, prompt):
        fragment = chunk.choices[0].delta.content
        if fragment is None:
            break
        chunks.append(fragment)
    return "".join(chunks)


def read_story(story):
    response = ctx.tts_client.audio.speech.create(
        input=story,
        model=ctx.tts_model,
        voice=ctx.tts_voice,
        response_format="wav",
    )
    file_name = "story.wav"
    response.write_to_file(file_name)
    data, samplerate = sf.read(file_name)
    return samplerate, data


with gr.Blocks() as demo:

    prompt_text = utils.read_from_file(utils.resolve("prompt.txt"))

    gr.Markdown("# Fably Local Stack Test")

    voice_query = gr.Audio(
        label="Voice Query",
        sources=["microphone"],
        type="filepath",
        waveform_options=gr.WaveformOptions(
            waveform_color="#01C6FF",
            waveform_progress_color="#0066B4",
            skip_length=2,
            show_controls=False,
        ),
    )

    transcribe_button = gr.Button("Transcribe voice query")

    transcribed_query = gr.Textbox(
        lines=1,
        label="Transcribed Voice Query",
    )

    transcribe_button.click(
        fn=transcribe,
        inputs=[voice_query],
        outputs=[transcribed_query],
    )

    prompt_input = gr.Textbox(
        lines=4,
        label="Prompt",
        value=prompt_text,
    )

    temperature_slider = gr.Slider(0, 2.0, value=1.0, label="Temperature")
    max_tokens_slider = gr.Slider(0, 2000, value=100, label="Max Tokens")

    generate_story_button = gr.Button("Generate Story")

    story_input = gr.Textbox(
        lines=30,
        label="Generated Story",
    )

    generate_story_button.click(
        fn=generate_story,
        inputs=[transcribed_query, prompt_input, temperature_slider, max_tokens_slider],
        outputs=[story_input],
    )

    read_story_button = gr.Button("Read the story to me")

    story_audio = gr.Audio(
        label="Story Audio",
        interactive=False,
    )

    read_story_button.click(
        fn=read_story,
        inputs=[story_input],
        outputs=[story_audio],
    )


if __name__ == "__main__":
    demo.launch()
