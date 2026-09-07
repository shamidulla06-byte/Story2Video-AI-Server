from typing import Dict, List


class ScenePlanner:

    def __init__(self):
        self.engine_name = "Story2Video Scene Planner"
        self.version = "1.0.0"

    def create_scene_plan(
        self,
        story_analysis: Dict
    ) -> Dict:

        scenes = story_analysis.get("scenes", [])

        if not scenes:
            raise ValueError(
                "No scenes were found in the story analysis."
            )

        planned_scenes: List[Dict] = []

        previous_scene = None

        for scene in scenes:

            scene_number = scene.get(
                "scene_number"
            )

            story_part = scene.get(
                "story_part",
                ""
            )

            emotion = scene.get(
                "emotion",
                "neutral"
            )

            environment = scene.get(
                "environment",
                "auto"
            )

            action = scene.get(
                "action",
                "auto"
            )

            camera_style = self.choose_camera_style(
                emotion,
                action
            )

            movement_style = self.choose_movement_style(
                emotion,
                action
            )

            continuity = self.create_continuity(
                previous_scene,
                scene
            )

            planned_scene = {
                "scene_number": scene_number,

                "story_part": story_part,

                "emotion": emotion,

                "environment": environment,

                "action": action,

                "camera_style": camera_style,

                "movement_style": movement_style,

                "continuity": continuity,

                "video_prompt": self.create_video_prompt(
                    story_part,
                    emotion,
                    environment,
                    action,
                    camera_style,
                    movement_style
                )
            }

            planned_scenes.append(
                planned_scene
            )

            previous_scene = planned_scene

        return {
            "planner": self.engine_name,
            "version": self.version,
            "total_scenes": len(planned_scenes),
            "scenes": planned_scenes
        }

    # =================================================
    # CAMERA STYLE
    # =================================================

    def choose_camera_style(
        self,
        emotion: str,
        action: str
    ) -> str:

        if action in [
            "running",
            "fighting",
            "flying"
        ]:

            return "dynamic cinematic tracking shot"

        if emotion == "fear":

            return "slow suspenseful cinematic camera"

        if emotion == "sad":

            return "slow emotional cinematic close-up"

        if emotion == "angry":

            return "intense dramatic handheld camera"

        if emotion == "happy":

            return "smooth bright cinematic camera"

        return "natural cinematic camera"

    # =================================================
    # MOVEMENT STYLE
    # =================================================

    def choose_movement_style(
        self,
        emotion: str,
        action: str
    ) -> str:

        if action == "running":

            return "fast character movement"

        if action == "walking":

            return "natural walking movement"

        if action == "flying":

            return "fast aerial movement"

        if action == "fighting":

            return "intense action movement"

        if emotion == "fear":

            return "careful nervous movement"

        if emotion == "sad":

            return "slow emotional movement"

        if emotion == "happy":

            return "energetic joyful movement"

        return "natural realistic movement"

    # =================================================
    # CONTINUITY
    # =================================================

    def create_continuity(
        self,
        previous_scene,
        current_scene
    ) -> Dict:

        if previous_scene is None:

            return {
                "previous_scene": None,
                "connection": (
                    "This is the first scene."
                )
            }

        return {
            "previous_scene": previous_scene.get(
                "scene_number"
            ),

            "connection": (
                "Continue naturally from the previous "
                "scene while maintaining character, "
                "environment and story continuity."
            )
        }

    # =================================================
    # VIDEO PROMPT
    # =================================================

    def create_video_prompt(
        self,
        story_part: str,
        emotion: str,
        environment: str,
        action: str,
        camera_style: str,
        movement_style: str
    ) -> str:

        prompt = f"""
Create a realistic cinematic video scene.

Story event:
{story_part}

Emotion:
{emotion}

Environment:
{environment}

Character action:
{action}

Camera:
{camera_style}

Movement:
{movement_style}

Maintain realistic motion, cinematic lighting,
natural character behavior and visual continuity.
"""

        return prompt.strip()


scene_planner = ScenePlanner()
