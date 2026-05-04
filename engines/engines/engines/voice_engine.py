import edge_tts
import asyncio
from pathlib import Path
from pydub import AudioSegment


class VoiceEngine:

    def __init__(self):
        self.voice = "fr-FR-HenriNeural"
        self.rate = "-8%"
        self.pitch = "-10Hz"

    def generate(self, text, output_path):
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        subtitles = asyncio.run(self._generate_async(text, output_path))
        return output_path, subtitles

    async def _generate_async(self, text, output_path):
        subtitles = []
        communicate = edge_tts.Communicate(
            text,
            self.voice,
            rate=self.rate,
            pitch=self.pitch
        )

        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                subtitles.append({
                    "word": chunk["text"],
                    "start": chunk["offset"] / 10_000_000,
                    "dur": chunk["duration"] / 10_000_000
                })

        with open(output_path, "wb") as f:
            for c in audio_chunks:
                f.write(c)

        return subtitles

    def get_duration(self, path):
        audio = AudioSegment.from_file(path)
        return len(audio) / 1000.0
