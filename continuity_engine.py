from typing import Dict, List


class ContinuityEngine:

    def __init__(self):

        self.engine_name = (
            "Story2Video Continuity Engine"
        )

        self.version = "1.0.0"

    # =================================================
    # BUILD CONTINUITY MEMORY
    # =================================================

    def build_continuity(
        self,
        story_analysis: Dict,
        scene_plan: Dict
    ) -> Dict:

        scenes = scene_plan.get(
            "scenes",
            []
        )

        if not scenes:

            raise ValueError(
                "No planned scenes were found."
            )

        characters = self.extract_characters(
            story_analysis
        )

        continuity_scenes: List[Dict] = []

        previous_scene = None

        for scene in scenes:

            scene_number = scene.get(
                "scene_number"
            )

            continuity_data = {
                "scene_number": scene_number,

                "character_memory": characters,

                "previous_scene": (
                    previous_scene.get("scene_number")
                    if previous_scene
                    else None
                ),

                "continuity_instruction": (
                    self.create_continuity_instruction(
                        previous_scene,
                        scene
                    )
                ),

                "scene_state": (
                    self.create_scene_state(
                        scene,
                        previous_scene
                    )
                )
            }

            continuity_scenes.append(
                continuity_data
            )

            previous_scene = scene

        return {
            "engine": self.engine_name,

            "version": self.version,

            "total_scenes": len(
                continuity_scenes
            ),

            "character_memory": characters,

            "continuity_scenes": (
                continuity_scenes
            )
        }

    # =================================================
    # EXTRACT CHARACTER MEMORY
    # =================================================

    def extract_characters(
        self,
        story_analysis: Dict
    ) -> List[Dict]:

        characters = story_analysis.get(
            "characters",
            []
        )

        character_memory = []

        for character in characters:

            if isinstance(character, str):

                character_memory.append(
                    {
                        "name": character,

                        "identity_instruction": (
                            f"Keep {character} visually "
                            "consistent across all scenes."
                        )
                    }
                )

            elif isinstance(character, dict):

                name = character.get(
                    "name",
                    "Unknown Character"
                )

                character_memory.append(
                    {
                        "name": name,

                        "appearance": character.get(
                            "appearance",
                            "Maintain the same appearance."
                        ),

                        "clothing": character.get(
                            "clothing",
                            "Keep clothing consistent "
                            "unless the story changes it."
                        ),

                        "identity_instruction": (
                            f"Keep {name} visually "
                            "consistent across all scenes."
                        )
                    }
                )

        return character_memory

    # =================================================
    # CONTINUITY INSTRUCTION
    # =================================================

    def create_continuity_instruction(
        self,
        previous_scene,
        current_scene
    ) -> str:

        if previous_scene is None:

            return (
                "This is the first scene. "
                "Establish character appearance, "
                "environment and cinematic style."
            )

        previous_environment = (
            previous_scene.get(
                "environment",
                "previous environment"
            )
        )

        current_environment = (
            current_scene.get(
                "environment",
                "current environment"
            )
        )

        if (
            previous_environment ==
            current_environment
        ):

            environment_instruction = (
                "Maintain the same environment "
                "and location continuity."
            )

        else:

            environment_instruction = (
                "Transition naturally from the "
                "previous location to the new "
                "story location."
            )

        return (
            "Continue naturally from the previous "
            "scene. Maintain the same character "
            "identity, appearance and visual style. "
            + environment_instruction
        )

    # =================================================
    # SCENE STATE
    # =================================================

    def create_scene_state(
        self,
        scene: Dict,
        previous_scene
    ) -> Dict:

        state = {
            "emotion": scene.get(
                "emotion",
                "neutral"
            ),

            "environment": scene.get(
                "environment",
                "auto"
            ),

            "action": scene.get(
                "action",
                "auto"
            )
        }

        if previous_scene:

            state[
                "previous_emotion"
            ] = previous_scene.get(
                "emotion",
                "neutral"
            )

            state[
                "previous_action"
            ] = previous_scene.get(
                "action",
                "auto"
            )

        return state

    # =================================================
    # CREATE FINAL VIDEO INSTRUCTION
    # =================================================

    def create_video_continuity_prompt(
        self,
        scene: Dict,
        continuity_data: Dict
    ) -> str:

        character_memory = (
            continuity_data.get(
                "character_memory",
                []
            )
        )

        character_text = ""

        for character in character_memory:

            character_text += (
                f"{character.get('name')}: "
                f"{character.get('identity_instruction')} "
            )

        continuity_instruction = (
            continuity_data.get(
                "continuity_instruction",
                ""
            )
        )

        return (
            "VISUAL CONTINUITY RULES:\n\n"

            f"{character_text}\n\n"

            f"{continuity_instruction}\n\n"

            "Keep the story visually connected to "
            "the previous scene. Maintain realistic "
            "character identity, natural movement, "
            "environment continuity and cinematic style."
        )


continuity_engine = ContinuityEngine()
