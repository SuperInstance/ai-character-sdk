"""
Decision Engine - Intelligent decision routing for AI characters

Routes decisions through three tiers:
- BOT: Fast, deterministic, free (rules-based)
- BRAIN: Personality-driven, medium cost (local LLM or character logic)
- HUMAN: Critical decisions, higher cost (API LLM)

Provides cost-effective routing based on:
- Confidence levels
- Stakes assessment
- Novelty detection
- Time constraints
"""

import time
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


# ============================================================================
# DECISION TYPES & ENUMS
# ============================================================================

class DecisionTier(Enum):
    """Which tier handles the decision"""
    BOT = "bot"           # Fast, deterministic, free
    BRAIN = "brain"       # Personality-driven, local LLM
    HUMAN = "human"       # Critical, API LLM


class EscalationReason(Enum):
    """Why a decision was escalated"""
    LOW_CONFIDENCE = "low_confidence"
    HIGH_STAKES = "high_stakes"
    NOVEL_SITUATION = "novel_situation"
    TIME_CRITICAL = "time_critical"
    SAFETY_CONCERN = "safety_concern"
    CHARACTER_GROWTH = "character_growth"
    COST_LIMIT = "cost_limit"


# ============================================================================
# DECISION DATA STRUCTURES
# ============================================================================

@dataclass
class EscalationThresholds:
    """Thresholds for escalation decisions"""
    bot_min_confidence: float = 0.7        # Below this, escalate to brain
    brain_min_confidence: float = 0.5      # Below this, escalate to human
    high_stakes_threshold: float = 0.7     # Above this = high stakes
    critical_stakes_threshold: float = 0.9 # Above this = critical
    urgent_time_ms: int = 500             # Less than this = urgent
    critical_time_ms: int = 100           # Less than this = critical
    novelty_threshold: float = 0.6        # Above this = novel situation
    hp_critical_threshold: float = 0.2    # Below this HP = critical


@dataclass
class DecisionContext:
    """Context for a decision that needs routing"""
    character_id: str
    situation_type: str  # e.g., "combat", "social", "support", "planning"
    situation_description: str

    # Importance
    stakes: float = 0.5              # 0=trivial, 1=life-or-death
    urgency_ms: Optional[int] = None # Time available for decision

    # State
    character_hp_ratio: float = 1.0
    available_resources: Dict[str, int] = field(default_factory=dict)

    # History
    similar_decisions_count: int = 0  # How many times seen similar
    recent_failures: int = 0          # Recent failed decisions

    # Metadata
    timestamp: float = field(default_factory=time.time)
    custom_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionRouting:
    """Result of decision routing"""
    tier: DecisionTier
    reason: Optional[EscalationReason] = None
    confidence_required: float = 0.0
    time_budget_ms: Optional[int] = None
    allow_fallback: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionResult:
    """Result of a routed decision"""
    decision_id: str
    tier: DecisionTier
    action: str
    confidence: float
    time_taken_ms: float
    escalated_from: Optional[DecisionTier] = None
    escalation_reason: Optional[EscalationReason] = None
    success: Optional[bool] = None  # Set after outcome known
    metadata: Dict[str, Any] = field(default_factory=dict)
    cost_estimate: float = 0.0  # Estimated cost in USD

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "decision_id": self.decision_id,
            "tier": self.tier.value,
            "action": self.action,
            "confidence": self.confidence,
            "time_taken_ms": self.time_taken_ms,
            "escalated_from": self.escalated_from.value if self.escalated_from else None,
            "escalation_reason": self.escalation_reason.value if self.escalation_reason else None,
            "success": self.success,
            "metadata": self.metadata,
            "cost_estimate": self.cost_estimate,
        }


# ============================================================================
# DECISION ENGINE
# ============================================================================

class DecisionEngine:
    """
    Decision engine for intelligent routing.

    Routes decisions through the optimal path based on context.
    """

    def __init__(
        self,
        confidence_threshold: float = 0.7,
        enable_escalation: bool = True,
        enable_learning: bool = True,
    ):
        """Initialize decision engine"""
        self.confidence_threshold = confidence_threshold
        self.enable_escalation = enable_escalation
        self.enable_learning = enable_learning

        # Character-specific thresholds
        self.thresholds: Dict[str, EscalationThresholds] = {}

        # Decision history
        self.decision_history: List[DecisionResult] = {}
        self.decisions_by_character: Dict[str, List[DecisionResult]] = {}

        # Pattern recognition for novelty detection
        self.situation_patterns: Dict[str, List[str]] = {}

        # Statistics
        self.stats = {
            "total_decisions": 0,
            "bot_decisions": 0,
            "brain_decisions": 0,
            "human_decisions": 0,
            "escalations": 0,
            "avg_confidence": 0.0,
            "total_cost": 0.0,
        }

    def get_thresholds(self, character_id: str) -> EscalationThresholds:
        """Get thresholds for a character, creating defaults if needed"""
        if character_id not in self.thresholds:
            self.thresholds[character_id] = EscalationThresholds()
        return self.thresholds[character_id]

    def set_thresholds(
        self,
        character_id: str,
        thresholds: EscalationThresholds
    ) -> None:
        """Set custom thresholds for a character"""
        self.thresholds[character_id] = thresholds

    def route(self, context: DecisionContext) -> DecisionRouting:
        """
        Route a decision to the appropriate tier.

        Args:
            context: Decision context

        Returns:
            DecisionRouting with routing information
        """
        start_time = time.time()

        character_id = context.character_id
        thresholds = self.get_thresholds(character_id)

        # Check for critical overrides first
        critical_override = self._check_critical_override(context, thresholds)
        if critical_override:
            return critical_override

        # Check if situation is novel
        is_novel = self._is_novel_situation(context, thresholds)

        # Check stakes level
        is_high_stakes = context.stakes >= thresholds.high_stakes_threshold
        is_critical_stakes = context.stakes >= thresholds.critical_stakes_threshold

        # Check urgency
        is_urgent = (context.urgency_ms is not None and
                    context.urgency_ms <= thresholds.urgent_time_ms)
        is_time_critical = (context.urgency_ms is not None and
                           context.urgency_ms <= thresholds.critical_time_ms)

        # Determine routing
        decision = None

        # Critical situations -> Human
        if is_critical_stakes or is_time_critical:
            decision = DecisionRouting(
                tier=DecisionTier.HUMAN,
                reason=EscalationReason.HIGH_STAKES if is_critical_stakes else EscalationReason.TIME_CRITICAL,
                confidence_required=0.9,
                time_budget_ms=context.urgency_ms,
                allow_fallback=True
            )

        # Novel situations with high stakes -> Brain (or Human if very high)
        elif is_novel and is_high_stakes:
            decision = DecisionRouting(
                tier=DecisionTier.BRAIN if not is_critical_stakes else DecisionTier.HUMAN,
                reason=EscalationReason.NOVEL_SITUATION,
                confidence_required=thresholds.brain_min_confidence,
                time_budget_ms=context.urgency_ms,
                allow_fallback=True
            )

        # Novel situations with low stakes -> Brain
        elif is_novel:
            decision = DecisionRouting(
                tier=DecisionTier.BRAIN,
                reason=EscalationReason.NOVEL_SITUATION,
                confidence_required=thresholds.brain_min_confidence,
                time_budget_ms=context.urgency_ms,
                allow_fallback=True
            )

        # High stakes but familiar -> Brain
        elif is_high_stakes:
            decision = DecisionRouting(
                tier=DecisionTier.BRAIN,
                reason=EscalationReason.HIGH_STAKES,
                confidence_required=thresholds.brain_min_confidence + 0.1,
                time_budget_ms=context.urgency_ms,
                allow_fallback=True
            )

        # Urgent but familiar -> Bot (fast response)
        elif is_urgent:
            decision = DecisionRouting(
                tier=DecisionTier.BOT,
                reason=None,
                confidence_required=thresholds.bot_min_confidence - 0.1,
                time_budget_ms=context.urgency_ms,
                allow_fallback=True
            )

        # Routine situation -> Bot
        else:
            decision = DecisionRouting(
                tier=DecisionTier.BOT,
                reason=None,
                confidence_required=thresholds.bot_min_confidence,
                time_budget_ms=context.urgency_ms,
                allow_fallback=True
            )

        # Add metadata
        decision.metadata = {
            "is_novel": is_novel,
            "is_high_stakes": is_high_stakes,
            "is_critical_stakes": is_critical_stakes,
            "is_urgent": is_urgent,
            "is_time_critical": is_time_critical,
            "routing_time_ms": (time.time() - start_time) * 1000
        }

        return decision

    def _check_critical_override(
        self,
        context: DecisionContext,
        thresholds: EscalationThresholds
    ) -> Optional[DecisionRouting]:
        """Check for critical situations that override normal routing"""

        # Critical HP -> Human
        if context.character_hp_ratio <= thresholds.hp_critical_threshold:
            return DecisionRouting(
                tier=DecisionTier.HUMAN,
                reason=EscalationReason.SAFETY_CONCERN,
                confidence_required=0.95,
                time_budget_ms=context.urgency_ms,
                allow_fallback=False,
                metadata={"critical_hp": True}
            )

        # Critical resources -> Human
        for resource, amount in context.available_resources.items():
            if resource in ["spell_slots", "hp_potions", "resurrection", "credits", "tokens"]:
                if amount <= 1:  # Last of critical resource
                    return DecisionRouting(
                        tier=DecisionTier.HUMAN,
                        reason=EscalationReason.SAFETY_CONCERN,
                        confidence_required=0.95,
                        time_budget_ms=context.urgency_ms,
                        allow_fallback=False,
                        metadata={"critical_resource": resource}
                    )

        # Recent failures -> Brain or Human
        if context.recent_failures >= 3:
            return DecisionRouting(
                tier=DecisionTier.BRAIN,
                reason=EscalationReason.LOW_CONFIDENCE,
                confidence_required=0.8,
                time_budget_ms=context.urgency_ms,
                allow_fallback=True,
                metadata={"recent_failures": context.recent_failures}
            )

        return None

    def _is_novel_situation(
        self,
        context: DecisionContext,
        thresholds: EscalationThresholds
    ) -> bool:
        """Determine if situation is novel (unseen or rare)"""

        # Check if we've seen this situation type before
        situation_key = f"{context.character_id}:{context.situation_type}"

        if situation_key not in self.situation_patterns:
            self.situation_patterns[situation_key] = []

        patterns = self.situation_patterns[situation_key]

        # If we haven't seen many similar situations, it's novel
        if len(patterns) < 5:
            return True

        # Check if description is similar to known patterns
        description_lower = context.situation_description.lower()
        description_words = set(description_lower.split())

        max_similarity = 0.0
        for pattern in patterns:
            pattern_words = set(pattern.lower().split())
            if not pattern_words:
                continue

            common_words = description_words & pattern_words
            similarity = len(common_words) / len(pattern_words)
            max_similarity = max(max_similarity, similarity)

        # If max similarity is low, situation is novel
        is_novel = max_similarity < (1.0 - thresholds.novelty_threshold)

        # Store pattern if novel
        if is_novel or len(patterns) < 20:
            patterns.append(context.situation_description[:100])

        return is_novel

    def record_decision(self, result: DecisionResult) -> None:
        """Record a decision for history and learning"""
        # Add to history
        if "decisions" not in self.decision_history:
            self.decision_history = []

        self.decision_history.append(result)

        # Add to character history
        char_id = result.metadata.get("character_id")
        if char_id:
            if char_id not in self.decisions_by_character:
                self.decisions_by_character[char_id] = []
            self.decisions_by_character[char_id].append(result)

        # Update stats
        self.stats["total_decisions"] += 1

        if result.tier == DecisionTier.BOT:
            self.stats["bot_decisions"] += 1
        elif result.tier == DecisionTier.BRAIN:
            self.stats["brain_decisions"] += 1
        elif result.tier == DecisionTier.HUMAN:
            self.stats["human_decisions"] += 1

        if result.escalated_from is not None:
            self.stats["escalations"] += 1

        # Track cost
        self.stats["total_cost"] += result.cost_estimate

    def get_character_stats(self, character_id: str) -> Dict[str, Any]:
        """Get decision statistics for a character"""
        if character_id not in self.decisions_by_character:
            return {"total_decisions": 0}

        decisions = self.decisions_by_character[character_id]

        bot_decisions = sum(1 for d in decisions if d.tier == DecisionTier.BOT)
        brain_decisions = sum(1 for d in decisions if d.tier == DecisionTier.BRAIN)
        human_decisions = sum(1 for d in decisions if d.tier == DecisionTier.HUMAN)
        escalations = sum(1 for d in decisions if d.escalated_from is not None)

        successes = sum(1 for d in decisions if d.success is True)
        failures = sum(1 for d in decisions if d.success is False)

        if decisions:
            avg_confidence = sum(d.confidence for d in decisions) / len(decisions)
            avg_time = sum(d.time_taken_ms for d in decisions) / len(decisions)
            total_cost = sum(d.cost_estimate for d in decisions)
        else:
            avg_confidence = 0.0
            avg_time = 0.0
            total_cost = 0.0

        return {
            "total_decisions": len(decisions),
            "bot_decisions": bot_decisions,
            "brain_decisions": brain_decisions,
            "human_decisions": human_decisions,
            "escalations": escalations,
            "escalation_rate": escalations / len(decisions) if decisions else 0,
            "successes": successes,
            "failures": failures,
            "success_rate": successes / (successes + failures) if (successes + failures) > 0 else 0,
            "avg_confidence": avg_confidence,
            "avg_time_ms": avg_time,
            "total_cost": total_cost,
        }

    def get_global_stats(self) -> Dict[str, Any]:
        """Get global decision statistics"""
        stats = self.stats.copy()

        # Add computed stats
        if stats["total_decisions"] > 0:
            if "decisions" in self.decision_history:
                stats["avg_confidence"] = (
                    sum(d.confidence for d in self.decision_history) / stats["total_decisions"]
                )
                stats["avg_time_ms"] = (
                    sum(d.time_taken_ms for d in self.decision_history) / stats["total_decisions"]
                )

        # Calculate cost savings
        if stats["total_decisions"] > 0:
            baseline_cost = stats["total_decisions"] * 0.02  # $0.02 per decision baseline
            actual_cost = stats["total_cost"]
            stats["cost_savings"] = baseline_cost - actual_cost
            stats["cost_reduction_ratio"] = baseline_cost / actual_cost if actual_cost > 0 else float('inf')

        return stats

    def create_decision_id(self) -> str:
        """Create a unique decision ID"""
        return str(uuid.uuid4())
