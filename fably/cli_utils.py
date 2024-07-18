"""
Utility functions for command lines.
"""

import click

from fably import utils


class Context:
    """
    Context object used to store configuration parameters for the command line interface.

    This object is used to store parameters that are used across multiple commands.
    """

    def __init__(self):
        self.debug = False
        self.trim_first_frame = False
        self.sounds_path = utils.resolve("sounds")
        self.sound_driver = "alsa"
        self.sample_rate = 16000
        self.language = "en"
        self.stt_url = None
        self.stt_model = None
        self.llm_url = None
        self.llm_model = None
        self.temperature = 0
        self.max_tokens = 0
        self.tts_url = None
        self.tts_model = None
        self.tts_voice = None
        self.ai = None
        self.running = True

    def persist_runtime_params(self, output_file, **kwargs):
        """
        Writes information about the models used to generate the story to a file.
        """
        info = {
            "language": self.language,
            "stt_url": self.stt_url,
            "stt_model": self.stt_model,
            "llm_url": self.llm_url,
            "llm_model": self.llm_model,
            "llm_temperature": self.temperature,
            "llm_max_tokens": self.max_tokens,
            "tts_url": self.tts_url,
            "tts_model": self.tts_model,
            "tts_voice": self.tts_voice,
        }
        for key, value in kwargs.items():
            info[key] = value
        utils.write_to_yaml(output_file, info)


pass_context = click.make_pass_decorator(Context, ensure=True)
