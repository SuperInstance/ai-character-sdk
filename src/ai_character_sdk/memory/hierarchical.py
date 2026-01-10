"""
Hierarchical Memory System for AI Characters

A simplified 6-tier memory architecture inspired by cognitive neuroscience:
- WORKING: Current attention/context (seconds to minutes)
- MID_TERM: Session buffer (1-6 hours)
- LONG_TERM: Consolidated storage (1+ weeks)
- EPISODIC: Specific events "what-where-when"
- SEMANTIC: Consolidated patterns & facts
- PROCEDURAL: Skills & learned behaviors
"""

import json
import hashlib
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import math


# ============================================================================
# MEMORY TYPES & ENUMS
# ============================================================================

class MemoryType(Enum):
    """Hierarchical memory tiers (inspired by neuroscience)"""
    WORKING = "working"              # Current attention (LLM context)
    MID_TERM = "mid_term"            # Session buffer (1-6 hours)
    LONG_TERM = "long_term"          # Consolidated storage (1+ weeks)
    EPISODIC = "episodic"            # Specific events "what-where-when"
    SEMANTIC = "semantic"            # Consolidated patterns & facts
    PROCEDURAL = "procedural"        # Skills & learned behaviors


class MemoryImportance(Enum):
    """Importance scoring (affects consolidation priority)"""
    FORGOTTEN = 1.0     # Low priority
    ROUTINE = 3.0       # Normal daily memory
    NOTABLE = 6.0       # Worth remembering
    SIGNIFICANT = 8.0   # Life-changing
    CORE_IDENTITY = 10.0 # Defines who they are


# ============================================================================
# MEMORY DATA STRUCTURES
# ============================================================================

@dataclass
class Memory:
    """Individual memory unit"""
    id: str
    content: str                          # What happened/was learned
    memory_type: MemoryType
    timestamp: datetime

    # Metadata
    importance: float = 5.0                # 1-10 scale
    emotional_valence: float = 0.0         # -1 (bad) to +1 (good)
    participants: List[str] = field(default_factory=list)  # Who was involved
    location: str = ""                    # Where it happened

    # Consolidation tracking
    access_count: int = 0                 # Times retrieved (boosts importance)
    last_accessed: Optional[datetime] = None
    consolidated: bool = False            # Has it moved to semantic?

    # Relationships
    related_memory_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance,
            "emotional_valence": self.emotional_valence,
            "participants": self.participants,
            "location": self.location,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "consolidated": self.consolidated,
            "related_memory_ids": self.related_memory_ids,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        """Create from dictionary"""
        data = data.copy()
        data["memory_type"] = MemoryType(data["memory_type"])
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        if data.get("last_accessed"):
            data["last_accessed"] = datetime.fromisoformat(data["last_accessed"])
        return cls(**data)


# ============================================================================
# CORE MEMORY SYSTEM
# ============================================================================

class HierarchicalMemory:
    """
    Main hierarchical memory system implementing 6-tier architecture.

    Features:
    - Memory storage with tier management
    - Importance-based retrieval
    - Access count boosting
    - Persistent storage (JSON)
    - Memory relationship tracking

    Example:
        >>> memory = HierarchicalMemory(character_id="agent_001")
        >>> memory.store("Met the team to discuss Q1 goals",
        ...              importance=7.0,
        ...              emotional_valence=0.5)
        >>> relevant = memory.retrieve("team meeting", top_k=5)
    """

    DEFAULT_CONFIG = {
        "max_working_memories": 10,
        "max_mid_term_memories": 100,
        "recency_decay_rate": 0.995,      # Per hour
        "consolidation_threshold": 150.0,
    }

    def __init__(
        self,
        character_id: str,
        storage_path: Optional[Union[str, Path]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize hierarchical memory system.

        Args:
            character_id: Unique identifier for this character/entity
            storage_path: Path for persistent storage (None = in-memory only)
            config: Configuration overrides
        """
        self.character_id = character_id
        self.storage_path = Path(storage_path) if storage_path else None
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}

        # Memory storage
        self.memories: Dict[str, Memory] = {}

        # Consolidation tracking
        self.importance_accumulator: float = 0.0
        self.last_consolidation_time: datetime = datetime.now()

        # Load existing data if available
        if self.storage_path:
            self._load()

    # ======================================================================
    # MEMORY STORAGE
    # ======================================================================

    def store(
        self,
        content: str,
        memory_type: Union[MemoryType, str] = MemoryType.EPISODIC,
        importance: float = 5.0,
        emotional_valence: float = 0.0,
        participants: Optional[List[str]] = None,
        location: str = "",
    ) -> Memory:
        """
        Store a new memory.

        Args:
            content: What happened/was learned
            memory_type: Type tier (MemoryType enum or string)
            importance: 1-10 scale, affects retrieval and consolidation
            emotional_valence: -1 (bad) to +1 (good)
            participants: List of who was involved
            location: Where it happened

        Returns:
            The created Memory object
        """
        if isinstance(memory_type, str):
            memory_type = MemoryType(memory_type)

        memory_id = self._generate_memory_id(content)

        memory = Memory(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            timestamp=datetime.now(),
            importance=importance,
            emotional_valence=emotional_valence,
            participants=participants or [],
            location=location,
        )

        self.memories[memory_id] = memory
        self.importance_accumulator += importance

        # Manage tier capacity
        self._manage_tier_capacity(memory_type)

        # Auto-save if enabled
        if self.storage_path:
            self._save()

        return memory

    def store_working(self, content: str, **kwargs) -> Memory:
        """Store in working memory (current attention)."""
        return self.store(content, MemoryType.WORKING, **kwargs)

    def store_mid_term(self, content: str, **kwargs) -> Memory:
        """Store in mid-term memory (session buffer)."""
        return self.store(content, MemoryType.MID_TERM, **kwargs)

    def store_episodic(self, content: str, **kwargs) -> Memory:
        """Store as episodic memory (specific event)."""
        return self.store(content, MemoryType.EPISODIC, **kwargs)

    def store_semantic(self, content: str, **kwargs) -> Memory:
        """Store as semantic memory (fact/pattern)."""
        return self.store(content, MemoryType.SEMANTIC, **kwargs)

    def store_procedural(self, content: str, **kwargs) -> Memory:
        """Store as procedural memory (skill)."""
        return self.store(content, MemoryType.PROCEDURAL, **kwargs)

    # ======================================================================
    # MEMORY RETRIEVAL
    # ======================================================================

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        memory_type: Optional[Union[MemoryType, str]] = None,
        alpha_recency: float = 1.0,
        alpha_importance: float = 1.0,
        alpha_relevance: float = 1.0
    ) -> List[Memory]:
        """
        Retrieve memories with weighted scoring.

        Args:
            query: Search query text
            top_k: Maximum number of results
            memory_type: Filter by memory type (None = all)
            alpha_recency: Weight for recency
            alpha_importance: Weight for importance
            alpha_relevance: Weight for semantic relevance

        Returns:
            List of retrieved memories
        """
        if isinstance(memory_type, str):
            memory_type = MemoryType(memory_type)

        # Filter by type if specified
        memories = list(self.memories.values())
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]

        # Score each memory
        results = []
        current_time = datetime.now()

        for memory in memories:
            # Recency score (exponential decay per hour)
            hours_ago = (current_time - memory.timestamp).total_seconds() / 3600
            recency = self.config["recency_decay_rate"] ** hours_ago

            # Importance score (normalized)
            importance = memory.importance / 10.0

            # Relevance score (word overlap)
            relevance = self._calculate_relevance(query, memory.content)

            # Combined score
            total_weight = alpha_recency + alpha_importance + alpha_relevance
            score = (
                alpha_recency * recency +
                alpha_importance * importance +
                alpha_relevance * relevance
            ) / total_weight if total_weight > 0 else 0

            results.append((score, memory))

        # Sort by score and return top_k
        results.sort(reverse=True, key=lambda x: x[0])
        retrieved = [m for _, m in results[:top_k]]

        # Update access counts
        for memory in retrieved:
            memory.access_count += 1
            memory.last_accessed = datetime.now()
            # Slight importance boost on retrieval
            memory.importance = min(memory.importance * 1.05, 10.0)

        return retrieved

    def get_by_id(self, memory_id: str) -> Optional[Memory]:
        """Get a specific memory by ID."""
        return self.memories.get(memory_id)

    def get_memories_by_type(self, memory_type: Union[MemoryType, str]) -> List[Memory]:
        """Get all memories of a specific type."""
        if isinstance(memory_type, str):
            memory_type = MemoryType(memory_type)
        return [m for m in self.memories.values() if m.memory_type == memory_type]

    def get_recent(self, hours: int = 24, top_k: int = 10) -> List[Memory]:
        """Get recent memories within specified hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [m for m in self.memories.values() if m.timestamp > cutoff]
        recent.sort(key=lambda x: x.timestamp, reverse=True)
        return recent[:top_k]

    def get_important(self, threshold: float = 6.0, top_k: int = 10) -> List[Memory]:
        """Get memories above importance threshold."""
        important = [m for m in self.memories.values() if m.importance >= threshold]
        important.sort(key=lambda x: x.importance, reverse=True)
        return important[:top_k]

    # ======================================================================
    # MEMORY RELATIONSHIPS
    # ======================================================================

    def relate_memories(self, memory_id_1: str, memory_id_2: str):
        """Mark two memories as related."""
        if memory_id_1 in self.memories and memory_id_2 in self.memories:
            if memory_id_2 not in self.memories[memory_id_1].related_memory_ids:
                self.memories[memory_id_1].related_memory_ids.append(memory_id_2)
            if memory_id_1 not in self.memories[memory_id_2].related_memory_ids:
                self.memories[memory_id_2].related_memory_ids.append(memory_id_1)

    def get_related_memories(self, memory_id: str) -> List[Memory]:
        """Get memories related to the given memory."""
        if memory_id not in self.memories:
            return []
        related_ids = self.memories[memory_id].related_memory_ids
        return [self.memories[rid] for rid in related_ids if rid in self.memories]

    # ======================================================================
    # PERSISTENCE
    # ======================================================================

    def save(self):
        """Save to persistent storage."""
        if self.storage_path:
            self._save()

    def load(self):
        """Load from persistent storage."""
        if self.storage_path:
            self._load()

    def _save(self):
        """Internal save method."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "character_id": self.character_id,
            "memories": [m.to_dict() for m in self.memories.values()],
            "importance_accumulator": self.importance_accumulator,
            "last_consolidation_time": self.last_consolidation_time.isoformat(),
            "config": self.config,
        }

        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def _load(self):
        """Internal load method."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)

            self.memories = {
                m["id"]: Memory.from_dict(m)
                for m in data.get("memories", [])
            }

            self.importance_accumulator = data.get("importance_accumulator", 0.0)

            if ct := data.get("last_consolidation_time"):
                self.last_consolidation_time = datetime.fromisoformat(ct)

        except Exception as e:
            print(f"Error loading memory: {e}")

    def export(self) -> Dict[str, Any]:
        """Export all memory data as dictionary."""
        return {
            "character_id": self.character_id,
            "memories": [m.to_dict() for m in self.memories.values()],
        }

    # ======================================================================
    # STATS & HEALTH
    # ======================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        from collections import Counter

        memory_counts = Counter(m.memory_type.value for m in self.memories.values())

        consolidated = sum(1 for m in self.memories.values() if m.consolidated)

        avg_importance = 0.0
        if self.memories:
            avg_importance = sum(m.importance for m in self.memories.values()) / len(self.memories)

        return {
            "character_id": self.character_id,
            "total_memories": len(self.memories),
            "by_type": dict(memory_counts),
            "consolidated": consolidated,
            "unconsolidated": len(self.memories) - consolidated,
            "average_importance": avg_importance,
            "importance_accumulator": self.importance_accumulator,
        }

    # ======================================================================
    # PRIVATE HELPER METHODS
    # ======================================================================

    def _generate_memory_id(self, content: str) -> str:
        """Generate unique memory ID."""
        seed = f"{self.character_id}{content}{datetime.now().isoformat()}"
        return hashlib.md5(seed.encode()).hexdigest()[:16]

    def _manage_tier_capacity(self, memory_type: MemoryType):
        """Evict old memories when tier is at capacity."""
        if memory_type == MemoryType.WORKING:
            max_memories = self.config.get("max_working_memories", 10)
            self._evict_from_tier(memory_type, max_memories)
        elif memory_type == MemoryType.MID_TERM:
            max_memories = self.config.get("max_mid_term_memories", 100)
            self._evict_from_tier(memory_type, max_memories)

    def _evict_from_tier(self, memory_type: MemoryType, max_count: int):
        """Evict least important memories from tier."""
        tier_memories = [m for m in self.memories.values() if m.memory_type == memory_type]
        if len(tier_memories) > max_count:
            # Sort by importance * recency
            tier_memories.sort(
                key=lambda m: m.importance * (0.5 if m.access_count == 0 else 1.0)
            )
            # Evict the least important
            to_evict = tier_memories[:-max_count]
            for m in to_evict:
                del self.memories[m.id]

    def _calculate_relevance(self, text1: str, text2: str) -> float:
        """Simple relevance calculation (word overlap)."""
        words1 = set(w.lower() for w in text1.split() if len(w) > 2)
        words2 = set(w.lower() for w in text2.split() if len(w) > 2)

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0
