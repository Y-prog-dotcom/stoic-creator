from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ColorClip
)
from pathlib import Path


class EditorEngine:

    def __init__(self):
        self.W = 1080
        self.H = 1920
        self.FPS = 30

    def assemble(self, clips_paths, voice_path, script, output_path, subtitle_data):
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        voice = AudioFileClip(voice_path)
        duration = voice.duration

        video_clips = []
        for path in clips_paths:
            try:
                clip = VideoFileClip(path)
                clip = self._resize(clip)
                video_clips.append(clip)
            except Exception as e:
                print(f"Clip ignoré : {e}")
                continue

        if not video_clips:
            video_clips = [
                ColorClip(
                    size=(self.W, self.H),
                    color=(10, 10, 30),
                    duration=duration
                )
            ]

        video = self._fit_duration(video_clips, duration)

        if subtitle_data:
            subs = self._word_subtitles(subtitle_data, duration)
        else:
            subs = self._chunk_subtitles(script, duration)

        final = CompositeVideoClip(
            [video] + subs,
            size=(self.W, self.H)
        )
        final = final.set_audio(voice)
        final = final.set_duration(duration)

        final.write_videofile(
            output_path,
            fps=self.FPS,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            threads=2,
            logger=None
        )

        final.close()
        voice.close()
        for c in video_clips:
            try:
                c.close()
            except:
                pass

        return output_path

    def _resize(self, clip):
        target = self.W / self.H
        ratio = clip.w / clip.h

        if ratio > target:
            new_w = int(clip.h * target)
            x1 = (clip.w - new_w) // 2
            clip = clip.crop(x1=x1, x2=x1 + new_w)
        elif ratio < target:
            new_h = int(clip.w / target)
            y1 = (clip.h - new_h) // 2
            clip = clip.crop(y1=y1, y2=y1 + new_h)

        return clip.resize((self.W, self.H))

    def _fit_duration(self, clips, target):
        result = []
        remaining = target
        i = 0

        while remaining > 0:
            clip = clips[i % len(clips)].copy()
            if clip.duration <= remaining:
                result.append(clip)
                remaining -= clip.duration
            else:
                result.append(clip.subclip(0, remaining))
                remaining = 0
            i += 1

        return concatenate_videoclips(result, method="compose")

    def _word_subtitles(self, data, duration):
        clips = []
        group_size = 4

        for i in range(0, len(data), group_size):
            group = data[i:i + group_size]
            if not group:
                continue

            text = " ".join(w["word"] for w in group).upper()
            start = group[0]["start"]

            if i + group_size < len(data):
                end = data[i + group_size]["start"]
            else:
                end = duration

            dur = max(0.3, end - start)

            try:
                txt = TextClip(
                    text,
                    fontsize=58,
                    font="Arial-Bold",
                    color="white",
                    stroke_color="black",
                    stroke_width=3,
                    method="caption",
                    size=(self.W - 80, None),
                    align="center"
                )
                txt = (
                    txt
                    .set_position(("center", self.H * 0.62))
                    .set_start(start)
                    .set_duration(dur)
                )
                clips.append(txt)
            except:
                continue

        return clips

    def _chunk_subtitles(self, script, duration):
        words = script.split()
        chunks = [
            " ".join(words[i:i + 5])
            for i in range(0, len(words), 5)
        ]
        chunk_dur = duration / max(len(chunks), 1)
        clips = []

        for i, chunk in enumerate(chunks):
            try:
                txt = TextClip(
                    chunk.upper(),
                    fontsize=58,
                    font="Arial-Bold",
                    color="white",
                    stroke_color="black",
                    stroke_width=3,
                    method="caption",
                    size=(self.W - 80, None),
                    align="center"
                )
                txt = (
                    txt
                    .set_position(("center", self.H * 0.62))
                    .set_start(i * chunk_dur)
                    .set_duration(chunk_dur)
                )
                clips.append(txt)
            except:
                continue

        return clips
