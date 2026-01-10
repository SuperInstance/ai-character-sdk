"""
Core Character Module

The main Character class that unifies all AI character components:
- Memory system for storing and retrieving experiences
- Decision engine for intelligent routing
- Personality system for consistent behavior
- Learning system for outcome-based improvement
"""

from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path

from ..memory.hierarchical import HierarchicalMemory, MemoryType, Memory
from ..decision.engine import DecisionEngine, DecisionContext, DecisionResult, DecisionTier
from ..personality.traits import Personality, PersonalityProfile
from ..learning.outcomes import OutcomeTracker, Outcome, LearningSignal


class CharacterState(Enum):
    """Possible states of a character"""
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    RESTING = "resting"
    INCAPACITATED = "incapacitated"


@dataclass
class CharacterConfig:
    """Configuration for creating a Character"""
    name: str
    character_class: str = "adventurer"
    description: str = ""
    personality: Dict[str, float] = field(default_factory=dict)
    backstory: str = ""
    goals: List[str] = field(default_factory=list)
    fears: List[str] = field(default_factory=list)
    quirks: List[str] = field(default_factory=list)

    # Memory settings
    memory_storage_path: Optional[str] = None
    max_working_memories: int = 10
    memory_importance_threshold: float = 5.0

    # Decision settings
    decision_confidence_threshold: float = 0.7
    enable_escalation: bool = True

    # Learning settings
    enable_learning: bool = True
    learning_rate: float = 0.1

    # Callbacks for LLM integration
    on_think: Optional[Callable] = None
    on_act: Optional[Callable] = None


@dataclass
class ThoughtContext:
    """Context provided to the character for thinking"""
    situation: str
    stakes: float = 0.5
    urgency_ms: Optional[int] = None
    location: str = ""
    participants: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CharacterResponse:
    """Response from a character action"""
    content: str
    action: str = "talk"
    tier: DecisionTier = DecisionTier.BRAIN
    confidence: float = 0.0
    time_taken_ms: float = 0.0
    thoughts: str = ""
    emotions: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "content": self.content,
            "action": self.action,
            "tier": self.tier.value if isinstance(self.tier, DecisionTier) else self.tier,
            "confidence": self.confidence,
            "time_taken_ms": self.time_taken_ms,
            "thoughts": self.thoughts,
            "emotions": self.emotions,
            "metadata": self.metadata,
        }


class Character:
    """
    Unified AI Character with memory, personality, and learning.

    The Character class combines all SDK components into a simple,
    cohesive API for creating intelligent AI characters.

    Example:
        >>> character = Character(
        ...     name="Finn the Brave",
        ...     character_class="paladin",
        ...     personality={"bravery": 0.9, "kindness": 0.8}
        ... )
        >>>
        >>> response = character.think("I see a goblin approaching")
        >>> character.remember("The goblin was actually friendly")
        >>> character.learn(outcome="positive")
    """

    def __init__(
        self,
        name: str,
        character_class: str = "adventurer",
        personality: Optional[Dict[str, float]] = None,
        backstory: str = "",
        description: str = "",
        goals: Optional[List[str]] = None,
        fears: Optional[List[str]] = None,
        quirks: Optional[List[str]] = None,
        config: Optional[CharacterConfig] = None,
        storage_path: Optional[str] = None,
    ):
        """
        Initialize a Character.

        Args:
            name: Character's name
            character_class: Character class/type
            personality: Dict of trait names to values (0-1)
            backstory: Character's background story
            description: Visual/behavioral description
            goals: List of character goals
            fears: List of character fears
            quirks: List of character quirks
            config: Full configuration (overrides other params)
            storage_path: Path for persistent storage
        """
        # Handle configuration
        if config is None:
            config = CharacterConfig(
                name=name,
                character_class=character_class,
                description=description,
                personality=personality or {},
                backstory=backstory,
                goals=goals or [],
                fears=fears or [],
                quirks=quirks or [],
                memory_storage_path=storage_path,
            )
        else:
            # Override config with direct params if provided
            if name: config.name = name
            if character_class: config.character_class = character_class
            if personality: config.personality = personality
            if backstory: config.backstory = backstory
            if description: config.description = description
            if goals: config.goals = goals
            if fears: config.fears = fears
            if quirks: config.quirks = quirks
            if storage_path: config.memory_storage_path = storage_path

        self.config = config
        self.name = config.name
        self.character_class = config.character_class
        self.description = config.description
        self.backstory = config.backstory
        self.goals = config.goals
        self.fears = config.fears
        self.quirks = config.quirks

        # Initialize state
        self.state = CharacterState.IDLE
        self.created_at = datetime.now()
        self.interaction_count = 0

        # Initialize components
        self._init_memory()
        self._init_personality()
        self._init_decision()
        self._init_learning()

    def _init_memory(self):
        """Initialize memory system"""
        storage_path = None
        if self.config.memory_storage_path:
            storage_path = Path(self.config.memory_storage_path) / f"{self.name}_memory.json"

        self.memory = HierarchicalMemory(
            character_id=self.name,
            storage_path=storage_path,
            config={
                "max_working_memories": self.config.max_working_memories,
            }
        )

        # Store core identity as semantic memory
        if self.backstory:
            self.memory.store_semantic(
                f"I am {self.name}. {self.backstory}",
                importance=10.0,
            )

        for goal in self.goals:
            self.memory.store_semantic(
                f"My goal: {goal}",
                importance=8.0,
            )

    def _init_personality(self):
        """Initialize personality system"""
        self.personality = Personality(
            traits=self.config.personality,
            profile=PersonalityProfile(
                character_class=self.character_class,
                description=self.description,
                quirks=self.quirks,
            )
        )

    def _init_decision(self):
        """Initialize decision engine"""
        self.decision_engine = DecisionEngine(
            confidence_threshold=self.config.decision_confidence_threshold,
            enable_escalation=self.config.enable_escalation,
        )

    def _init_learning(self):
        """Initialize learning system"""
        self.outcomes = OutcomeTracker(
            character_id=self.name,
            learning_rate=self.config.learning_rate,
            enabled=self.config.enable_learning,
        )

    # ========================================================================
    # THINKING - Generate responses to situations
    # ========================================================================

    def think(
        self,
        situation: str,
        stakes: float = 0.5,
        urgency_ms: Optional[int] = None,
        context: Optional[ThoughtContext] = None,
    ) -> CharacterResponse:
        """
        Generate a response to a situation.

        Args:
            situation: Description of the current situation
            stakes: Importance level (0-1)
            urgency_ms: Time available for decision
            context: Full thought context (overrides other params)

        Returns:
            CharacterResponse with the character's reaction
        """
        import time
        start_time = time.time()

        # Build context
        if context is None:
            context = ThoughtContext(
                situation=situation,
                stakes=stakes,
                urgency_ms=urgency_ms,
            )
        else:
            context.situation = situation

        self.state = CharacterState.THINKING
        self.interaction_count += 1

        # Get relevant memories
        relevant_memories = self.memory.retrieve(situation, top_k=5)

        # Build character context
        character_context = self._build_context(relevant_memories)

        # Route decision
        decision_context = DecisionContext(
            character_id=self.name,
            situation_type=self._classify_situation(situation),
            situation_description=situation,
            stakes=stakes,
            urgency_ms=urgency_ms,
        )

        decision = self.decision_engine.route(decision_context)

        # Generate response based on tier
        if decision.tier == DecisionTier.BOT:
            response = self._generate_bot_response(context, character_context)
        elif decision.tier == DecisionTier.BRAIN:
            response = self._generate_brain_response(context, character_context)
        else:  # HUMAN
            response = self._generate_human_response(context, character_context)

        # Apply personality modifiers
        response = self.personality.apply_to_response(response)

        response.tier = decision.tier
        response.confidence = decision.confidence_required
        response.time_taken_ms = (time.time() - start_time) * 1000

        # Store interaction in working memory
        self.memory.store_working(
            f"Responded to: {situation[:100]}",
            importance=3.0 + stakes * 3,
        )

        self.state = CharacterState.IDLE

        return response

    def _build_context(self, memories: List[Memory]) -> str:
        """Build context string from memories and character info"""
        parts = [
            f"I am {self.name}, a {self.character_class}.",
        ]

        if self.description:
            parts.append(self.description)

        if self.personality.traits:
            traits_str = ", ".join(f"{k}:{v:.1f}" for k, v in self.personality.traits.items())
            parts.append(f"My personality: {traits_str}")

        if self.goals:
            parts.append(f"My goals: {', '.join(self.goals[:3])}")

        if memories:
            parts.append("\nRelevant memories:")
            for m in memories[:3]:
                parts.append(f"  - {m.content[:80]}")

        return "\n".join(parts)

    def _classify_situation(self, situation: str) -> str:
        """Classify the type of situation"""
        situation_lower = situation.lower()

        if any(w in situation_lower for w in ["attack", "fight", "combat", "enemy", "threat"]):
            return "combat"
        elif any(w in situation_lower for w in ["talk", "speak", "discuss", "negotiate"]):
            return "social"
        elif any(w in situation_lower for w in ["explore", "search", "look", "find"]):
            return "exploration"
        elif any(w in situation_lower for w in ["help", "heal", "support", "protect"]):
            return "support"
        elif any(w in situation_lower for w in ["buy", "sell", "trade", "shop"]):
            return "commerce"
        else:
            return "general"

    def _generate_bot_response(
        self,
        context: ThoughtContext,
        character_context: str,
    ) -> CharacterResponse:
        """Generate a simple rule-based response"""
        situation_lower = context.situation.lower()

        # Simple rule-based responses
        if "attack" in situation_lower or "fight" in situation_lower:
            if self.personality.get_trait("bravery", 0.5) > 0.7:
                response = f"I stand ready to face this threat!"
                action = "attack"
            else:
                response = f"I assess the situation carefully before acting."
                action = "defend"
        elif "talk" in situation_lower or "speak" in situation_lower:
            response = f"I listen attentively and respond thoughtfully."
            action = "talk"
        elif "help" in situation_lower:
            response = f"I offer my assistance."
            action = "help"
        else:
            response = f"I consider {context.situation[:50]}..."
            action = "wait"

        return CharacterResponse(
            content=response,
            action=action,
            tier=DecisionTier.BOT,
            confidence=0.8,
            thoughts="Quick assessment based on rules",
        )

    def _generate_brain_response(
        self,
        context: ThoughtContext,
        character_context: str,
    ) -> CharacterResponse:
        """Generate a personality-driven response (can use LLM callback)"""
        # If callback is provided, use it
        if self.config.on_think:
            try:
                result = self.config.on_think(
                    character=self,
                    situation=context.situation,
                    context=character_context,
                )
                if isinstance(result, str):
                    return CharacterResponse(
                        content=result,
                        action="talk",
                        tier=DecisionTier.BRAIN,
                        confidence=0.7,
                    )
                elif isinstance(result, dict):
                    return CharacterResponse(
                        content=result.get("content", ""),
                        action=result.get("action", "talk"),
                        tier=DecisionTier.BRAIN,
                        confidence=result.get("confidence", 0.7),
                        thoughts=result.get("thoughts", ""),
                    )
            except Exception:
                pass  # Fall through to default

        # Default personality-based response
        traits = self.personality.traits
        dominant_trait = max(traits.items(), key=lambda x: x[1]) if traits else ("neutral", 0.5)

        responses = {
            "bravery": "I step forward confidently to address this.",
            "kindness": "I approach with compassion and care.",
            "curiosity": "I'm intrigued! Let me learn more about this.",
            "caution": "I carefully consider the risks before proceeding.",
            "aggression": "I confront this challenge head-on.",
            "diplomacy": "I seek a peaceful resolution through dialogue.",
        }

        response = responses.get(
            dominant_trait[0],
            f"I consider the situation and respond as {self.name} would."
        )

        return CharacterResponse(
            content=response,
            action="talk",
            tier=DecisionTier.BRAIN,
            confidence=0.7,
            thoughts=f"Based on my dominant trait: {dominant_trait[0]}",
        )

    def _generate_human_response(
        self,
        context: ThoughtContext,
        character_context: str,
    ) -> CharacterResponse:
        """Generate a high-stakes response (can use LLM callback)"""
        # If callback is provided, use it
        if self.config.on_think:
            try:
                result = self.config.on_think(
                    character=self,
                    situation=context.situation,
                    context=character_context,
                    high_stakes=True,
                )
                if isinstance(result, str):
                    return CharacterResponse(
                        content=result,
                        action="talk",
                        tier=DecisionTier.HUMAN,
                        confidence=0.9,
                    )
                elif isinstance(result, dict):
                    return CharacterResponse(
                        content=result.get("content", ""),
                        action=result.get("action", "talk"),
                        tier=DecisionTier.HUMAN,
                        confidence=result.get("confidence", 0.9),
                        thoughts=result.get("thoughts", ""),
                    )
            except Exception:
                pass  # Fall through to default

        # Default high-stakes response
        return CharacterResponse(
            content=f"This is a critical moment. I, {self.name}, must choose wisely.",
            action="think",
            tier=DecisionTier.HUMAN,
            confidence=0.9,
            thoughts="This requires careful consideration",
        )

    # ========================================================================
    # MEMORY - Store and retrieve experiences
    # ========================================================================

    def remember(
        self,
        content: str,
        importance: float = 5.0,
        emotional_valence: float = 0.0,
        memory_type: Union[MemoryType, str] = MemoryType.EPISODIC,
        participants: Optional[List[str]] = None,
        location: str = "",
    ) -> Memory:
        """
        Store a memory.

        Args:
            content: What happened/was learned
            importance: 1-10 scale
            emotional_valence: -1 (bad) to +1 (good)
            memory_type: Type of memory
            participants: Who was involved
            location: Where it happened

        Returns:
            The created Memory
        """
        return self.memory.store(
            content=content,
            memory_type=memory_type,
            importance=importance,
            emotional_valence=emotional_valence,
            participants=participants or [],
            location=location,
        )

    def recall(self, query: str, top_k: int = 5) -> List[Memory]:
        """
        Retrieve relevant memories.

        Args:
            query: Search query
            top_k: Maximum results

        Returns:
            List of relevant memories
        """
        return self.memory.retrieve(query, top_k=top_k)

    def forget(self, memory_id: str) -> bool:
        """Remove a memory by ID"""
        if memory_id in self.memory.memories:
            del self.memory.memories[memory_id]
            return True
        return False

    def get_recent_memories(self, hours: int = 24, top_k: int = 10) -> List[Memory]:
        """Get recent memories"""
        return self.memory.get_recent(hours=hours, top_k=top_k)

    def get_important_memories(self, threshold: float = 6.0, top_k: int = 10) -> List[Memory]:
        """Get important memories"""
        return self.memory.get_important(threshold=threshold, top_k=top_k)

    # ========================================================================
    # LEARNING - Learn from outcomes
    # ========================================================================

    def learn(
        self,
        outcome: str,
        success: Optional[bool] = None,
        reward: float = 0.0,
        notes: str = "",
    ) -> LearningSignal:
        """
        Learn from an outcome.

        Args:
            outcome: Description of what happened
            success: Whether it was successful
            reward: Reward/punishment value
            notes: Additional notes

        Returns:
            LearningSignal
        """
        if success is None:
            success = reward > 0

        # Store as memory
        emotional_valence = 0.5 if success else -0.5
        self.remember(
            f"Outcome: {outcome}",
            importance=5.0 + abs(reward),
            emotional_valence=emotional_valence,
            memory_type=MemoryType.EPISODIC,
        )

        # Track outcome for learning
        return self.outcomes.record(
            outcome=outcome,
            success=success,
            reward=reward,
            notes=notes,
        )

    def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of learning outcomes"""
        return self.outcomes.get_summary()

    # ========================================================================
    # PERSONALITY - Manage traits
    # ========================================================================

    def set_trait(self, trait: str, value: float) -> None:
        """Set a personality trait value (0-1)"""
        self.personality.set_trait(trait, value)

    def get_trait(self, trait: str, default: float = 0.5) -> float:
        """Get a personality trait value"""
        return self.personality.get_trait(trait, default)

    def modify_trait(self, trait: str, delta: float) -> None:
        """Modify a personality trait by delta amount"""
        self.personality.modify_trait(trait, delta)

    def get_personality_summary(self) -> Dict[str, Any]:
        """Get personality profile summary"""
        return self.personality.get_summary()

    # ========================================================================
    # STATE & PERSISTENCE
    # ========================================================================

    def save(self, path: Optional[str] = None) -> None:
        """Save character state to file"""
        save_path = Path(path or f"{self.name}_character.json")

        # Save memory first
        self.memory.save()

        # Save character state
        state_data = {
            "name": self.name,
            "character_class": self.character_class,
            "description": self.description,
            "backstory": self.backstory,
            "goals": self.goals,
            "fears": self.fears,
            "quirks": self.quirks,
            "personality": dict(self.personality.traits),
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "interaction_count": self.interaction_count,
            "outcomes": self.outcomes.to_dict(),
        }

        with open(save_path, "w") as f:
            json.dump(state_data, f, indent=2)

    def load(self, path: Optional[str] = None) -> None:
        """Load character state from file"""
        load_path = Path(path or f"{self.name}_character.json")

        with open(load_path, "r") as f:
            data = json.load(f)

        self.name = data["name"]
        self.character_class = data["character_class"]
        self.description = data.get("description", "")
        self.backstory = data.get("backstory", "")
        self.goals = data.get("goals", [])
        self.fears = data.get("fears", [])
        self.quirks = data.get("quirks", [])
        self.state = CharacterState(data.get("state", "idle"))
        self.created_at = datetime.fromisoformat(data["created_at"])
        self.interaction_count = data.get("interaction_count", 0)

        # Restore personality
        self.personality.traits = data.get("personality", {})

        # Restore outcomes
        if "outcomes" in data:
            self.outcomes.from_dict(data["outcomes"])

        # Load memory
        self.memory.load()

    def get_stats(self) -> Dict[str, Any]:
        """Get character statistics"""
        memory_stats = self.memory.get_stats()
        outcome_stats = self.outcomes.get_summary()

        return {
            "name": self.name,
            "character_class": self.character_class,
            "state": self.state.value,
            "created_at": self.created_at.isoformat(),
            "interaction_count": self.interaction_count,
            "personality": dict(self.personality.traits),
            "memory": memory_stats,
            "learning": outcome_stats,
        }

    def __repr__(self) -> str:
        traits_str = ", ".join(f"{k}:{v:.1f}" for k, v in list(self.personality.traits.items())[:3])
        return f"Character(name={self.name!r}, class={self.character_class!r}, traits={traits_str})"
