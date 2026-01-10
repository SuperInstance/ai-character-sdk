"""
Personality System for AI Characters

Manages personality traits and their influence on character behavior.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


# ============================================================================
# PERSONALITY DATA STRUCTURES
# ============================================================================

class TraitCategory(Enum):
    """Categories of personality traits"""
    SOCIAL = "social"          # How they interact with others
    INTELLECTUAL = "intellectual"  # How they think and learn
    EMOTIONAL = "emotional"    # How they feel and express
    MORAL = "moral"            # Their ethical framework
    BEHAVIORAL = "behavioral"  # How they act


@dataclass
class Trait:
    """A personality trait with value and metadata"""
    name: str
    value: float  # 0.0 to 1.0
    category: TraitCategory = TraitCategory.BEHAVIORAL
    description: str = ""

    def __post_init__(self):
        self.value = max(0.0, min(1.0, self.value))


@dataclass
class PersonalityProfile:
    """Profile information about a personality"""
    character_class: str = ""
    description: str = ""
    quirks: List[str] = field(default_factory=list)
    virtues: List[str] = field(default_factory=list)
    vices: List[str] = field(default_factory=list)


# ============================================================================
# DEFAULT TRAIT DEFINITIONS
# ============================================================================

DEFAULT_TRAITS = {
    # Social traits
    "charisma": {"category": TraitCategory.SOCIAL, "description": "Ability to charm and persuade"},
    "kindness": {"category": TraitCategory.SOCIAL, "description": "Tendency to help others"},
    "empathy": {"category": TraitCategory.SOCIAL, "description": "Understanding others' feelings"},
    "diplomacy": {"category": TraitCategory.SOCIAL, "description": "Skill in resolving conflicts"},
    "loyalty": {"category": TraitCategory.SOCIAL, "description": "Faithfulness to allies"},

    # Intellectual traits
    "intelligence": {"category": TraitCategory.INTELLECTUAL, "description": "Mental acuity"},
    "curiosity": {"category": TraitCategory.INTELLECTUAL, "description": "Desire to learn"},
    "wisdom": {"category": TraitCategory.INTELLECTUAL, "description": "Accumulated knowledge"},
    "caution": {"category": TraitCategory.INTELLECTUAL, "description": "Carefulness in decisions"},
    "cunning": {"category": TraitCategory.INTELLECTUAL, "description": "Clever problem-solving"},

    # Emotional traits
    "bravery": {"category": TraitCategory.EMOTIONAL, "description": "Courage in facing fear"},
    "optimism": {"category": TraitCategory.EMOTIONAL, "description": "Positive outlook"},
    "patience": {"category": TraitCategory.EMOTIONAL, "description": "Ability to wait"},
    "humor": {"category": TraitCategory.EMOTIONAL, "description": "Tendency to joke"},
    "aggression": {"category": TraitCategory.EMOTIONAL, "description": "Tendency toward hostility"},

    # Moral traits
    "honor": {"category": TraitCategory.MORAL, "description": "Adherence to principles"},
    "justice": {"category": TraitCategory.MORAL, "description": "Fairness and equity"},
    "honesty": {"category": TraitCategory.MORAL, "description": "Truthfulness"},
    "devotion": {"category": TraitCategory.MORAL, "description": "Commitment to beliefs"},
    "mercy": {"category": TraitCategory.MORAL, "description": "Willingness to forgive"},

    # Behavioral traits
    "initiative": {"category": TraitCategory.BEHAVIORAL, "description": "Tendency to act first"},
    "discipline": {"category": TraitCategory.BEHAVIORAL, "description": "Self-control"},
    "ambition": {"category": TraitCategory.BEHAVIORAL, "description": "Drive for achievement"},
    "independence": {"category": TraitCategory.BEHAVIORAL, "description": "Self-reliance"},
    "adaptability": {"category": TraitCategory.BEHAVIORAL, "description": "Flexibility in change"},
}


# ============================================================================
# PERSONALITY CLASS
# ============================================================================

class Personality:
    """
    Manages a character's personality traits and their effects.

    Example:
        >>> personality = Personality(
        ...     traits={"bravery": 0.9, "kindness": 0.8}
        ... )
        >>> personality.get_trait("bravery")
        0.9
        >>> personality.modify_trait("bravery", 0.1)
        >>> personality.get_trait("bravery")
        1.0
    """

    def __init__(
        self,
        traits: Optional[Dict[str, float]] = None,
        profile: Optional[PersonalityProfile] = None,
    ):
        """
        Initialize personality.

        Args:
            traits: Dict of trait names to values (0-1)
            profile: Personality profile with metadata
        """
        self.traits: Dict[str, float] = traits or {}
        self.profile = profile or PersonalityProfile()
        self._trait_history: Dict[str, List[float]] = {}

        # Initialize history
        for trait, value in self.traits.items():
            self._trait_history[trait] = [value]

    def set_trait(self, trait: str, value: float) -> None:
        """Set a trait value (clamped to 0-1)"""
        clamped_value = max(0.0, min(1.0, value))
        self.traits[trait] = clamped_value

        if trait not in self._trait_history:
            self._trait_history[trait] = []
        self._trait_history[trait].append(clamped_value)

    def get_trait(self, trait: str, default: float = 0.5) -> float:
        """Get a trait value, returning default if not set"""
        return self.traits.get(trait, default)

    def modify_trait(self, trait: str, delta: float) -> None:
        """Modify a trait by delta amount (clamped to 0-1)"""
        current = self.get_trait(trait, 0.5)
        self.set_trait(trait, current + delta)

    def has_trait(self, trait: str) -> bool:
        """Check if a trait is defined"""
        return trait in self.traits

    def get_dominant_trait(self, min_value: float = 0.6) -> Optional[tuple[str, float]]:
        """Get the highest-value trait above minimum"""
        qualified = {k: v for k, v in self.traits.items() if v >= min_value}
        if not qualified:
            return None
        return max(qualified.items(), key=lambda x: x[1])

    def get_traits_by_category(self, category: TraitCategory) -> Dict[str, float]:
        """Get all traits in a category"""
        result = {}
        for trait, value in self.traits.items():
            trait_info = DEFAULT_TRAITS.get(trait, {})
            if trait_info.get("category") == category:
                result[trait] = value
        return result

    def get_summary(self) -> Dict[str, Any]:
        """Get personality summary"""
        dominant = self.get_dominant_trait()

        return {
            "traits": dict(self.traits),
            "dominant_trait": dominant[0] if dominant else None,
            "dominant_value": dominant[1] if dominant else None,
            "profile": {
                "character_class": self.profile.character_class,
                "description": self.profile.description,
                "quirks": self.profile.quirks,
            },
            "trait_count": len(self.traits),
        }

    def apply_to_response(self, response):
        """
        Apply personality modifiers to a response.

        This is called by Character to adjust responses based on traits.
        """
        # Modify response based on key traits
        if self.get_trait("humor", 0) > 0.7:
            # Add humorous elements
            if not any(q in response.content.lower() for q in ["!", "?", "..."]):
                response.content = response.content.rstrip(".") + "!"

        if self.get_trait("caution", 0) > 0.7:
            # Add cautious elements
            if "carefully" not in response.content.lower():
                response.content = "I carefully " + response.content.lower()

        if self.get_trait("aggression", 0) > 0.7:
            response.action = "attack"

        # Add emotional coloring based on traits
        if self.get_trait("optimism", 0) > 0.7:
            response.emotions["hope"] = response.emotions.get("hope", 0) + 0.5

        if self.get_trait("bravery", 0) > 0.7:
            response.emotions["confidence"] = response.emotions.get("confidence", 0) + 0.5

        return response

    def get_trait_description(self, trait: str) -> str:
        """Get description of a trait"""
        if trait in DEFAULT_TRAITS:
            return DEFAULT_TRAITS[trait].get("description", "")
        return ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "traits": self.traits,
            "profile": {
                "character_class": self.profile.character_class,
                "description": self.profile.description,
                "quirks": self.profile.quirks,
                "virtues": self.profile.virtues,
                "vices": self.profile.vices,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Personality":
        """Create from dictionary"""
        profile_data = data.get("profile", {})
        profile = PersonalityProfile(
            character_class=profile_data.get("character_class", ""),
            description=profile_data.get("description", ""),
            quirks=profile_data.get("quirks", []),
            virtues=profile_data.get("virtues", []),
            vices=profile_data.get("vices", []),
        )

        return cls(
            traits=data.get("traits", {}),
            profile=profile,
        )

    def __repr__(self) -> str:
        traits_str = ", ".join(f"{k}:{v:.1f}" for k, v in list(self.traits.items())[:3])
        return f"Personality({traits_str})"
