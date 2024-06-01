# Servers

This folder contains servers that can be used to run the OPENAI API but on a local device.

## STT Server

The speech-to-text server uses the faster-whisper model which works well and it's fast.

## LLM Server

Here we expect to run [Ollama](https://ollama.com/) which is fast and works on both environments with GPU or CPU only.

## TTS Server

The text-to-speech server uses WhisperSpeech which is an inverted model from Whisper and work very well with prosody even with a low parameter count. This is very fast on a GPU but it's not fast enough on pure CPU and I honestly don't know why.

## How to run

There are three servers so that you can run them on different machines if you don't have enough compute available on a single one. Or you can run them all on the same machine and that's fine as long as you use different ports for them.

By default we expect:

* STT server to be running at port 5000
* LLM server to be running at port 11434 (Ollama's default)
* TTS server to be running at port 5001

To use in Fably, you have to change the startup parameters like this

```bash
fably --loop --stt-url=http://mygpu.local:5000/v1 --llm-url=http://mygpu.local:11434/v1 --llm-model=llama3:latest --tts-url=http://mygpu.local:5001/v1
```

change `mygpu.local` to the address of the machine that you're using to run the servers. Note that they can be on different machines and that's totally fine.