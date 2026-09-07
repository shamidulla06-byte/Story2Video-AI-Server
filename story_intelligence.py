from typing import Dict, List


class StoryIntelligence:

    def __init__(self):
        self.engine_name = "Story2Video Story Intelligence"
        self.version = "1.0.0"

    def analyze_story(self, story: str) -> Dict:

        if not story or not story.strip():
            raise ValueError("Story cannot be empty.")

        story = story.strip()

        # গল্পকে বাক্যে ভাগ করার প্রাথমিক ব্যবস্থা
        sentences = []

        for part in story.replace("!", ".").replace("?", ".").split("."):
            part = part.strip()

            if part:
                sentences.append(part)

        # যদি বাক্য ভাগ করা না যায়
        if not sentences:
            sentences = [story]

        scenes: List[Dict] = []

        for index, sentence in enumerate(sentences):

            scene = {
                "scene_number": index + 1,
                "story_part": sentence,
                "emotion": self.detect_emotion(sentence),
                "environment": self.detect_environment(sentence),
                "action": self.detect_action(sentence)
            }

            scenes.append(scene)

        return {
            "engine": self.engine_name,
            "version": self.version,
            "story": story,
            "total_scenes": len(scenes),
            "scenes": scenes
        }

    def detect_emotion(self, text: str) -> str:

        text = text.lower()

        angry_words = [
            "রাগ", "রেগে", "চিৎকার",
            "angry", "anger"
        ]

        happy_words = [
            "খুশি", "হাসি", "আনন্দ",
            "happy", "smile"
        ]

        sad_words = [
            "কাঁদ", "দুঃখ", "কষ্ট",
            "sad", "cry"
        ]

        fear_words = [
            "ভয়", "ভয়", "ভূত",
            "অন্ধকার", "fear", "scared"
        ]

        for word in angry_words:
            if word in text:
                return "angry"

        for word in happy_words:
            if word in text:
                return "happy"

        for word in sad_words:
            if word in text:
                return "sad"

        for word in fear_words:
            if word in text:
                return "fear"

        return "neutral"

    def detect_environment(self, text: str) -> str:

        text = text.lower()

        environments = {

            "night": ["রাতে", "রাত", "night"],

            "city": ["শহর", "city"],

            "forest": ["জঙ্গল", "বন", "forest"],

            "castle": ["দুর্গ", "castle"],

            "sea": ["সমুদ্র", "sea"],

            "road": ["রাস্তা", "road"]
        }

        for environment, words in environments.items():

            for word in words:

                if word in text:
                    return environment

        return "auto"

    def detect_action(self, text: str) -> str:

        text = text.lower()

        actions = {

            "running": [
                "দৌড়", "দৌড়", "ছুট",
                "run", "running"
            ],

            "walking": [
                "হাঁট", "হেটে",
                "walk", "walking"
            ],

            "flying": [
                "উড়ে", "উড়ে", "উড়ল",
                "fly", "flying"
            ],

            "fighting": [
                "লড়াই", "লড়াই",
                "fight", "fighting"
            ]

        }

        for action, words in actions.items():

            for word in words:

                if word in text:
                    return action

        return "auto"


story_intelligence = StoryIntelligence()
