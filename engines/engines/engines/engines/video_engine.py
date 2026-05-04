import requests
import random
import os
from pathlib import Path


class VideoEngine:

    def __init__(self):
        self.api_key = os.getenv("PEXELS_API_KEY")
        self.base_url = "https://api.pexels.com/videos/search"
        self.fallback_keywords = [
            "man silhouette dark",
            "warrior training night",
            "mountain fog cinematic",
            "rain city night",
            "ocean storm waves",
            "lion dark cinematic",
            "fire flames night",
            "stoic statue marble",
            "man walking alone",
            "boxing training dark",
            "forest fog dark",
            "eagle flying mountain"
        ]

    def get_clips(self, keywords, output_dir, need=6):
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        clips = []
        used_ids = set()

        all_keywords = list(keywords) + random.sample(
            self.fallback_keywords,
            min(5, len(self.fallback_keywords))
        )

        for keyword in all_keywords:
            if len(clips) >= need:
                break

            videos = self._search(keyword)

            for video in videos:
                if len(clips) >= need:
                    break

                vid_id = video.get("id")
                if vid_id in used_ids:
                    continue

                try:
                    path = os.path.join(
                        output_dir,
                        f"clip_{len(clips) + 1}.mp4"
                    )
                    self._download(video, path)
                    clips.append(path)
                    used_ids.add(vid_id)
                except Exception as e:
                    print(f"Erreur clip : {e}")
                    continue

        print(f"Total clips : {len(clips)}")
        return clips

    def _search(self, query):
        if not self.api_key:
            return []
        try:
            response = requests.get(
                self.base_url,
                headers={"Authorization": self.api_key},
                params={
                    "query": query,
                    "per_page": 5,
                    "orientation": "portrait",
                    "size": "medium"
                },
                timeout=30
            )
            if response.status_code == 200:
                return response.json().get("videos", [])
            return []
        except:
            return []

    def _download(self, video, path):
        files = video.get("video_files", [])
        if not files:
            raise Exception("Aucun fichier vidéo")

        portrait_files = [
            f for f in files
            if f.get("height", 0) > f.get("width", 0)
        ]

        target = portrait_files if portrait_files else files
        best = max(target, key=lambda x: x.get("height", 0))

        response = requests.get(
            best["link"],
            stream=True,
            timeout=120
        )
        response.raise_for_status()

        with open(path, "wb") as f:
            for chunk in response.iter_content(1024 * 1024):
                f.write(chunk)
