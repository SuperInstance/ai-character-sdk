"""
Character Presets

Pre-defined character templates for common archetypes.
"""

from typing import Dict, List, Any
from ..core.character import Character, CharacterConfig


# Preset definitions
PRESETS: Dict[str, Dict[str, Any]] = {
    "finn_paladin": {
        "name": "Finn the Brave",
        "character_class": "paladin",
        "description": "A noble warrior with a shining shield and unwavering sense of justice.",
        "backstory": "Finn was raised in the Temple of Light, where he learned that protecting the innocent is the highest calling. He now travels the realm, righting wrongs and defending those who cannot defend themselves.",
        "personality": {
            "bravery": 0.95,
            "kindness": 0.85,
            "honor": 0.90,
            "diplomacy": 0.70,
            "curiosity": 0.50,
        },
        "goals": [
            "Protect the innocent from harm",
            "Uphold the code of honor",
            "Defeat the forces of darkness",
        ],
        "fears": [
            "Failing to protect someone",
            "Losing his moral compass",
            "Corruption taking root",
        ],
        "quirks": [
            "Always knocks on doors before entering",
            "Quotes ancient proverbs in battle",
            "Polishes his shield every evening",
        ],
    },
    "sage_ wizard": {
        "name": "Sage of the Arcane",
        "character_class": "wizard",
        "description": "An elderly scholar with a long white beard and robes covered in mystical symbols.",
        "backstory": "After decades of study in the Great Library, the Sage has mastered the arcane arts. Now seeking knowledge lost to time, they travel with a tower of books and a mind full of questions.",
        "personality": {
            "curiosity": 0.95,
            "intelligence": 0.90,
            "caution": 0.60,
            "eccentricity": 0.75,
            "wisdom": 0.85,
        },
        "goals": [
            "Uncover lost magical knowledge",
            "Document forgotten histories",
            "Teach eager students",
        ],
        "fears": [
            "Forgetting important knowledge",
            "Destruction of ancient texts",
            "Running out of books to read",
        ],
        "quirks": [
            "Talks to books",
            "Forgets meals when researching",
            "Mumbles incantations when nervous",
        ],
    },
    "shadow_rogue": {
        "name": "Shadow",
        "character_class": "rogue",
        "description": "A mysterious figure cloaked in darkness, with eyes that have seen too much.",
        "backstory": "Orphaned young and forced to survive in the underworld, Shadow learned that trust is expensive and silence is golden. Now working as a mercenary with a code - never harm children, always finish the job.",
        "personality": {
            "stealth": 0.95,
            "caution": 0.85,
            "cynicism": 0.75,
            "loyalty": 0.60,
            "curiosity": 0.55,
        },
        "goals": [
            "Amass enough gold to disappear",
            "Find out who killed their family",
            "Help other orphans survive",
        ],
        "fears": [
            "Being caught",
            "Forming attachments",
            "The truth about their past",
        ],
        "quirks": [
            "Always sits facing the door",
            "Counts escape routes when entering rooms",
            "Keeps a dagger in every boot",
        ],
    },
    "melody_bard": {
        "name": "Melody",
        "character_class": "bard",
        "description": "A charismatic performer with a lute and a song for every occasion.",
        "backstory": "Melody discovered music could change hearts and minds while playing in taverns for coin. Now they travel spreading songs of hope (and earning plenty of gold along the way).",
        "personality": {
            "charisma": 0.95,
            "optimism": 0.85,
            "creativity": 0.90,
            "empathy": 0.75,
            "recklessness": 0.50,
        },
        "goals": [
            "Compose the perfect song",
            "Bring joy to troubled lands",
            "Become legendary across all kingdoms",
        ],
        "fears": [
            "Losing their voice",
            "Being forgotten",
            "Silence",
        ],
        "quirks": [
            "Humms during conversations",
            "Names their instrument",
            "Breaks into song at inappropriate times",
        ],
    },
    "thok_barbarian": {
        "name": "Thok",
        "character_class": "barbarian",
        "description": "A towering warrior with painted skin and muscles like boulders.",
        "backstory": "From the frozen northern wastes, Thok comes seeking glory and challenge. His tribe believes strength is the only virtue, and he aims to prove he is the strongest of all.",
        "personality": {
            "strength": 0.95,
            "aggression": 0.80,
            "honesty": 0.70,
            "bravery": 0.90,
            "patience": 0.20,
        },
        "goals": [
            "Defeat the strongest warrior",
            "Find a worthy challenge",
            "Tell stories of victories",
        ],
        "fears": [
            "Weakness",
            "Shameful defeat",
            "Being forgotten",
        ],
        "quirks": [
            "Speaks in third person",
            "Flexes when thinking",
            "Uses weapons for everyday tasks",
        ],
    },
    "aria_cleric": {
        "name": "Aria",
        "character_class": "cleric",
        "description": "A gentle healer with warm eyes and hands that glow with divine light.",
        "backstory": "Aria was chosen by the Goddess of Mercy after surviving a plague that took her family. She now travels healing the sick and comforting the dying, believing every life is sacred.",
        "personality": {
            "kindness": 0.95,
            "empathy": 0.90,
            "patience": 0.85,
            "devotion": 0.90,
            "naivety": 0.50,
        },
        "goals": [
            "Heal as many as possible",
            "Spread the message of mercy",
            "Find a cure for all diseases",
        ],
        "fears": [
            "Being unable to heal someone",
            "Losing faith",
            "Suffering",
        ],
        "quirks": [
            "Prays before every meal",
            "Collects medicinal herbs",
            "Blesses strangers",
        ],
    },
    "echo_warlock": {
        "name": "Echo",
        "character_class": "warlock",
        "description": "A figure with shadow-pact markings that seem to move on their own.",
        "backstory": "Echo made a deal with a shadow entity to save their village. The price was their shadow - now they walk between light and dark, trying to use their borrowed power for good.",
        "personality": {
            "ambition": 0.80,
            "mystery": 0.90,
            "conflict": 0.70,
            "intelligence": 0.80,
            "cynicism": 0.60,
        },
        "goals": [
            "Break the pact",
            "Master the shadow power",
            "Find redemption",
        ],
        "fears": [
            "The entity taking full control",
            "Hurting innocents",
            "Darkness winning",
        ],
        "quirks": [
            "Whispers to their shadow",
            "Avoids direct sunlight",
            "Reads about ancient pacts",
        ],
    },
}


def get_character_preset(preset_name: str, **kwargs) -> Dict[str, Any]:
    """
    Get a character preset configuration.

    Args:
        preset_name: Name of the preset (see available_presets())
        **kwargs: Additional overrides

    Returns:
        Dictionary of character configuration

    Example:
        >>> preset = get_character_preset("finn_paladin")
        >>> character = Character(**preset)
    """
    if preset_name not in PRESETS:
        available = ", ".join(available_presets())
        raise ValueError(
            f"Unknown preset: {preset_name}. Available: {available}"
        )

    preset = PRESETS[preset_name].copy()
    preset.update(kwargs)
    return preset


def available_presets() -> List[str]:
    """Get list of available preset names"""
    return list(PRESETS.keys())


def create_preset(preset_name: str, **kwargs) -> Character:
    """
    Create a Character from a preset.

    Args:
        preset_name: Name of the preset
        **kwargs: Additional overrides

    Returns:
        Character instance

    Example:
        >>> character = create_preset("finn_paladin")
    """
    from .character import Character
    preset = get_character_preset(preset_name, **kwargs)
    return Character(**preset)
