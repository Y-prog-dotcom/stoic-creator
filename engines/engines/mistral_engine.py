from mistralai import Mistral
import os


class MistralEngine:

    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY manquante dans les Secrets HF")
        self.client = Mistral(api_key=api_key)
        self.model = "open-mistral-nemo"

    def generate_idea(self, topic=""):
        if topic:
            sujet = f"Thème imposé : {topic}"
        else:
            sujet = """Choisis UN thème parmi :
- Citations de Marc Aurèle, Épictète ou Sénèque
- La discipline du matin
- La solitude masculine et sa puissance
- Transformer la douleur en force
- Le silence comme arme secrète
- Ne rien attendre des autres
- L'échec comme professeur"""

        prompt = f"""Tu es un expert en contenu viral stoïcisme et discipline masculine.

{sujet}

Génère UNE idée de vidéo courte de 60 secondes, virale et puissante.

Réponds EXACTEMENT dans ce format (pas de texte avant ou après) :
TITRE: [titre accrocheur et puissant]
HOOK: [phrase choc de 3 secondes qui arrête le scroll]
EMOTION: [Détermination / Douleur / Fierté / Révélation]
KEYWORDS: [3 mots-clés anglais pour Pexels séparés par virgule]
"""

        response = self.client.chat.complete(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=300
        )

        return self._parse_idea(response.choices[0].message.content)

    def generate_script(self, idea):
        prompt = f"""Tu es un scénariste expert en vidéos stoïques virales.

Concept : {idea['titre']}
Hook : {idea['hook']}
Émotion : {idea['emotion']}

Écris un script de 50 à 70 secondes.

RÈGLES ABSOLUES :
- Maximum 130 mots
- Phrases très courtes (max 10 mots par phrase)
- Ton grave, direct, sans bullshit
- Pauses marquées par "..."
- Une citation de Marc Aurèle, Sénèque ou Épictète
- Tutoiement obligatoire
- Commence DIRECTEMENT par le hook

Retourne UNIQUEMENT le texte brut du script.
Pas de titres, pas de commentaires, juste le texte.
"""

        response = self.client.chat.complete(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )

        return self._clean(response.choices[0].message.content.strip())

    def _parse_idea(self, text):
        result = {
            "titre": "La discipline silencieuse",
            "hook": "Écoute bien. Cela va tout changer.",
            "emotion": "Détermination",
            "keywords": ["man warrior dark", "mountain fog", "stoic statue"]
        }

        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("TITRE:"):
                result["titre"] = line.split(":", 1)[1].strip()
            elif line.startswith("HOOK:"):
                result["hook"] = line.split(":", 1)[1].strip()
            elif line.startswith("EMOTION:"):
                result["emotion"] = line.split(":", 1)[1].strip()
            elif line.startswith("KEYWORDS:"):
                kws = line.split(":", 1)[1].strip()
                result["keywords"] = [k.strip() for k in kws.split(",")][:3]

        return result

    def _clean(self, text):
        bad = ["hook:", "tension:", "leçon:", "climax:", "fin:", "**", "##", "---", "section"]
        lines = []
        for line in text.split("\n"):
            l = line.strip()
            if l and not any(b in l.lower() for b in bad):
                lines.append(l)
        return " ".join(lines)
