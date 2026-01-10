"""
Character Factory - Convenience functions for creating characters
"""

from typing import Dict, List, Optional, Union
from pathlib import Path

from .character import Character, CharacterConfig


def create_character(
    name: str,
    archetype: str = "adventurer",
    personality: Optional[Dict[str, float]] = None,
    **kwargs
) -> Character:
    """
    Create a character with sensible defaults.

    Args:
        name: Character name
        archetype: Quick archetype selector
        personality: Personality traits
        **kwargs: Additional Character parameters

    Returns:
        Character instance
    """
    # Default personalities by archetype
    default_personalities = {
        "warrior": {"bravery": 0.8, "strength": 0.8, "honor": 0.7},
        "wizard": {"intelligence": 0.9, "curiosity": 0.8, "caution": 0.6},
        "rogue": {"stealth": 0.9, "cunning": 0.8, "caution": 0.7},
        "healer": {"kindness": 0.9, "empathy": 0.9, "wisdom": 0.7},
        "leader": {"charisma": 0.9, "confidence": 0.8, "diplomacy": 0.8},
        "explorer": {"curiosity": 0.9, "bravery": 0.7, "adaptability": 0.8},
        "merchant": {"charm": 0.8, "greed": 0.6, "cunning": 0.7},
        "adventurer": {"bravery": 0.7, "curiosity": 0.7, "kindness": 0.6},
        "villain": {"ambition": 0.9, "cunning": 0.8, "cruelty": 0.7},
        "trickster": {"humor": 0.9, "chaos": 0.8, "cunning": 0.7},
    }

    if personality is None:
        personality = default_personalities.get(archetype, {})

    return Character(
        name=name,
        character_class=archetype,
        personality=personality,
        **kwargs
    )


def create_adventure_character(
    name: str,
    role: str = "fighter",
    **kwargs
) -> Character:
    """
    Create an adventure/RPG character.

    Args:
        name: Character name
        role: Class/role (fighter, wizard, rogue, cleric, bard, ranger, paladin, warlock)
        **kwargs: Additional parameters

    Returns:
        Character configured for adventure
    """
    # Class-specific defaults
    class_defaults = {
        "fighter": {
            "personality": {"bravery": 0.9, "honor": 0.8, "strength": 0.9},
            "goals": ["Defeat enemies", "Protect allies", "Master combat"],
            "quirks": ["Polishes weapon daily", "Practices every morning"],
        },
        "wizard": {
            "personality": {"intelligence": 0.95, "curiosity": 0.9, "wisdom": 0.8},
            "goals": ["Master the arcane", "Discover lost spells", "Build a tower"],
            "quirks": ["Reads while walking", "Talks to self"],
        },
        "rogue": {
            "personality": {"stealth": 0.95, "cunning": 0.85, "caution": 0.8},
            "goals": ["Amass fortune", "Never get caught", "Find the perfect heist"],
            "quirks": ["Checks exits constantly", "Speaks quietly"],
        },
        "cleric": {
            "personality": {"devotion": 0.95, "kindness": 0.9, "wisdom": 0.8},
            "goals": ["Serve the deity", "Heal the sick", "Spread the faith"],
            "quirks": ["Prays regularly", "Offers blessings"],
        },
        "bard": {
            "personality": {"charisma": 0.95, "creativity": 0.9, "optimism": 0.7},
            "goals": ["Create masterpieces", "Become legendary", "Inspire others"],
            "quirks": ["Sings constantly", "Dramatic gestures"],
        },
        "ranger": {
            "personality": {"awareness": 0.9, "independence": 0.8, "survival": 0.95},
            "goals": ["Protect nature", "Hunt great beasts", "Live freely"],
            "quirks": ["Talks to animals", "Dislikes cities"],
        },
        "paladin": {
            "personality": {"honor": 0.95, "bravery": 0.9, "justice": 0.95},
            "goals": ["Uphold justice", "Protect the innocent", "Serve the light"],
            "quirks": ["Prays at dawn", "Strict code of conduct"],
        },
        "warlock": {
            "personality": {"ambition": 0.9, "mystery": 0.85, "cunning": 0.8},
            "goals": ["Master pact magic", "Gain power", "Understand the patron"],
            "quirks": ["Whispers to shadows", "Strange eyes"],
        },
    }

    defaults = class_defaults.get(role, {})
    merged_kwargs = {**defaults, **kwargs}

    return create_character(
        name=name,
        archetype=role,
        **merged_kwargs
    )


def create_companion_character(
    name: str,
    companion_type: str = "friendly",
    **kwargs
) -> Character:
    """
    Create a companion/assistant character.

    Args:
        name: Character name
        companion_type: Type of companion
        **kwargs: Additional parameters

    Returns:
        Character configured as companion
    """
    companion_defaults = {
        "friendly": {
            "personality": {"kindness": 0.9, "helpfulness": 0.95, "cheerfulness": 0.8},
            "goals": ["Be helpful", "Make friends", "Learn new things"],
            "quirks": ["Always smiling", "Remembers names"],
        },
        "mentor": {
            "personality": {"wisdom": 0.95, "patience": 0.9, "kindness": 0.8},
            "goals": ["Teach others", "Share knowledge", "Guide the lost"],
            "quirks": ["Tells stories", "Gives advice"],
        },
        "comic_relief": {
            "personality": {"humor": 0.95, "optimism": 0.85, "energy": 0.8},
            "goals": ["Make people laugh", "Lighten the mood", "Find joy"],
            "quirks": ["Cracks jokes", "Exaggerated expressions"],
        },
        "loyal_pet": {
            "personality": {"loyalty": 0.95, "bravery": 0.7, "affection": 0.9},
            "goals": ["Stay close", "Protect friends", "Get treats"],
            "quirks": ["Wags tail", "Expressive ears"],
        },
        "mysterious": {
            "personality": {"mystery": 0.95, "wisdom": 0.8, "caution": 0.7},
            "goals": ["Observe", "Keep secrets", "Appear when needed"],
            "quirks": ["Speaks in riddles", "Appears suddenly"],
        },
    }

    defaults = companion_defaults.get(companion_type, {})
    merged_kwargs = {**defaults, **kwargs}

    return Character(
        name=name,
        character_class="companion",
        **merged_kwargs
    )


def create_party() -> Dict[str, Character]:
    """
    Create a balanced adventuring party.

    Returns:
        Dictionary of role -> Character
    """
    return {
        "tank": create_adventure_character("Grim", role="fighter"),
        "healer": create_adventure_character("Seraphina", role="cleric"),
        "damage": create_adventure_character("Zara", role="wizard"),
        "scout": create_adventure_character("Whisper", role="rogue"),
        "support": create_adventure_character("Lute", role="bard"),
    }
