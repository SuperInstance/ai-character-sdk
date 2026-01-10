"""
AI Character SDK - Unified Character Creation Framework

A comprehensive toolkit for creating AI characters with:
- Hierarchical memory (6-tier cognitive architecture)
- Intelligent decision routing (escalation engine)
- Dynamic personality system
- Outcome-based learning
- Multi-agent coordination

Basic Usage:
-------------
>>> from ai_character_sdk import Character
>>>
>>> # Create a character
>>> character = Character(
...     name="Finn the Brave",
...     character_class="paladin",
...     personality={"bravery": 0.9, "kindness": 0.8}
... )
>>>
>>> # Use the character
>>> response = character.think("I see a goblin approaching")
>>> character.remember("The goblin was actually friendly")
>>> character.learn(outcome="positive")
"""

__version__ = "0.1.0"
__author__ = "Casey"
__license__ = "MIT"

# Core Character class
from ai_character_sdk.core.character import (
    Character,
    CharacterConfig,
    CharacterResponse,
    ThoughtContext,
    CharacterState,
)

# Personality system
from ai_character_sdk.personality.traits import (
    Personality,
    Trait,
    PersonalityProfile,
)

# Memory system
from ai_character_sdk.memory.hierarchical import (
    HierarchicalMemory,
    Memory,
    MemoryType,
)

# Decision system
from ai_character_sdk.decision.engine import (
    DecisionEngine,
    DecisionContext,
    DecisionResult,
    DecisionTier,
)

# Learning system
from ai_character_sdk.learning.outcomes import (
    OutcomeTracker,
    Outcome,
    LearningSignal,
)

# Presets
from ai_character_sdk.core.presets import (
    get_character_preset,
    available_presets,
)

# Convenience factories
from ai_character_sdk.core.factory import (
    create_character,
    create_adventure_character,
    create_companion_character,
    create_party,
)
from ai_character_sdk.core.presets import (
    create_preset,
)

__all__ = [
    # Version
    "__version__",
    "__author__",
    "__license__",

    # Core
    "Character",
    "CharacterConfig",
    "CharacterResponse",
    "ThoughtContext",
    "CharacterState",

    # Personality
    "Personality",
    "Trait",
    "PersonalityProfile",

    # Memory
    "HierarchicalMemory",
    "Memory",
    "MemoryType",

    # Decision
    "DecisionEngine",
    "DecisionContext",
    "DecisionResult",
    "DecisionTier",

    # Learning
    "OutcomeTracker",
    "Outcome",
    "LearningSignal",

    # Presets
    "get_character_preset",
    "available_presets",
    "create_preset",

    # Factories
    "create_character",
    "create_adventure_character",
    "create_companion_character",
    "create_party",
]
