"""
Learning System - Outcome tracking and reinforcement learning

Tracks outcomes and adjusts character behavior based on results.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


# ============================================================================
# LEARNING TYPES & ENUMS
# ============================================================================

class OutcomeType(Enum):
    """Type of outcome"""
    SUCCESS = "success"
    FAILURE = "failure"
    NEUTRAL = "neutral"
    PARTIAL = "partial"


# ============================================================================
# LEARNING DATA STRUCTURES
# ============================================================================

@dataclass
class Outcome:
    """A single outcome record"""
    id: str
    outcome: str                          # Description of what happened
    outcome_type: OutcomeType
    success: bool
    reward: float                         # Positive or negative
    timestamp: datetime
    notes: str = ""

    # Context
    situation: str = ""
    action_taken: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "outcome": self.outcome,
            "outcome_type": self.outcome_type.value,
            "success": self.success,
            "reward": self.reward,
            "timestamp": self.timestamp.isoformat(),
            "notes": self.notes,
            "situation": self.situation,
            "action_taken": self.action_taken,
            "metadata": self.metadata,
        }


@dataclass
class LearningSignal:
    """A signal that triggers learning/adjustment"""
    signal_type: str                      # What to adjust (e.g., "trait:bravery")
    delta: float                          # Amount to adjust
    confidence: float                     # How confident we are in this
    reason: str = ""                      # Why this adjustment


@dataclass
class LearningStats:
    """Statistics about learning progress"""
    total_outcomes: int
    success_count: int
    failure_count: int
    success_rate: float
    total_reward: float
    average_reward: float
    learning_trend: float                 # Positive = improving
    adjustments_made: int


# ============================================================================
# OUTCOME TRACKER
# ============================================================================

class OutcomeTracker:
    """
    Tracks outcomes and generates learning signals.

    Example:
        >>> tracker = OutcomeTracker(character_id="hero")
        >>> tracker.record("Defeated the goblin", success=True, reward=10)
        >>> summary = tracker.get_summary()
    """

    def __init__(
        self,
        character_id: str,
        learning_rate: float = 0.1,
        enabled: bool = True,
    ):
        """
        Initialize outcome tracker.

        Args:
            character_id: Character to track
            learning_rate: How fast to adjust (0-1)
            enabled: Whether learning is active
        """
        self.character_id = character_id
        self.learning_rate = learning_rate
        self.enabled = enabled

        # Outcome history
        self.outcomes: List[Outcome] = []

        # Learning adjustments
        self.adjustments: List[LearningSignal] = []

        # Pattern tracking
        self.success_patterns: Dict[str, int] = {}
        self.failure_patterns: Dict[str, int] = {}

    def record(
        self,
        outcome: str,
        success: Optional[bool] = None,
        reward: float = 0.0,
        outcome_type: Optional[OutcomeType] = None,
        notes: str = "",
        situation: str = "",
        action_taken: str = "",
    ) -> LearningSignal:
        """
        Record an outcome and generate learning signals.

        Args:
            outcome: Description of what happened
            success: Whether it was successful
            reward: Reward/punishment value
            outcome_type: Type of outcome
            notes: Additional notes
            situation: Context situation
            action_taken: What action was taken

        Returns:
            LearningSignal with adjustments to make
        """
        if not self.enabled:
            return LearningSignal("", 0, 0, "Learning disabled")

        # Determine success/type
        if success is None:
            success = reward > 0

        if outcome_type is None:
            if success:
                outcome_type = OutcomeType.SUCCESS
            elif reward < 0:
                outcome_type = OutcomeType.FAILURE
            else:
                outcome_type = OutcomeType.NEUTRAL

        # Create outcome record
        outcome_record = Outcome(
            id=self._generate_id(),
            outcome=outcome,
            outcome_type=outcome_type,
            success=success,
            reward=reward,
            timestamp=datetime.now(),
            notes=notes,
            situation=situation,
            action_taken=action_taken,
        )

        self.outcomes.append(outcome_record)

        # Generate learning signals
        signals = self._generate_learning_signals(outcome_record)
        self.adjustments.extend(signals)

        # Track patterns
        self._track_patterns(outcome_record)

        # Return primary signal
        return signals[0] if signals else LearningSignal("", 0, 0, "No learning needed")

    def _generate_learning_signals(self, outcome: Outcome) -> List[LearningSignal]:
        """Generate learning signals from an outcome"""
        signals = []

        # Success - reinforce the action
        if outcome.success and outcome.reward > 0:
            if outcome.action_taken:
                signals.append(LearningSignal(
                    signal_type=f"action:{outcome.action_taken}",
                    delta=outcome.reward * self.learning_rate * 0.1,
                    confidence=0.7,
                    reason=f"Successful outcome: {outcome.outcome}",
                ))

        # Failure - discourage the action
        if not outcome.success and outcome.reward < 0:
            if outcome.action_taken:
                signals.append(LearningSignal(
                    signal_type=f"action:{outcome.action_taken}",
                    delta=outcome.reward * self.learning_rate * 0.1,  # Negative
                    confidence=0.7,
                    reason=f"Failed outcome: {outcome.outcome}",
                ))

        # Extract situation-based learning
        if outcome.situation:
            situation_words = outcome.situation.lower().split()
            for word in ["combat", "social", "exploration"]:
                if word in situation_words:
                    signals.append(LearningSignal(
                        signal_type=f"situation:{word}",
                        delta=outcome.reward * self.learning_rate * 0.05,
                        confidence=0.5,
                        reason=f"Experience in {word}",
                    ))

        return signals

    def _track_patterns(self, outcome: Outcome) -> None:
        """Track patterns in successes and failures"""
        words = set(outcome.outcome.lower().split())
        words.update(outcome.situation.lower().split())

        for word in words:
            if len(word) < 4:
                continue

            if outcome.success:
                self.success_patterns[word] = self.success_patterns.get(word, 0) + 1
            else:
                self.failure_patterns[word] = self.failure_patterns.get(word, 0) + 1

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of learning outcomes"""
        if not self.outcomes:
            return {
                "total_outcomes": 0,
                "success_count": 0,
                "failure_count": 0,
                "success_rate": 0.0,
                "total_reward": 0.0,
                "average_reward": 0.0,
                "adjustments_made": len(self.adjustments),
            }

        success_count = sum(1 for o in self.outcomes if o.success)
        failure_count = len(self.outcomes) - success_count
        total_reward = sum(o.reward for o in self.outcomes)

        # Calculate trend (comparing recent to overall)
        recent_outcomes = self.outcomes[-10:] if len(self.outcomes) > 10 else self.outcomes
        recent_reward = sum(o.reward for o in recent_outcomes) / len(recent_outcomes)
        overall_reward = total_reward / len(self.outcomes)
        trend = recent_reward - overall_reward

        return {
            "total_outcomes": len(self.outcomes),
            "success_count": success_count,
            "failure_count": failure_count,
            "success_rate": success_count / len(self.outcomes),
            "total_reward": total_reward,
            "average_reward": total_reward / len(self.outcomes),
            "learning_trend": trend,
            "adjustments_made": len(self.adjustments),
            "success_patterns": dict(sorted(
                self.success_patterns.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),
            "failure_patterns": dict(sorted(
                self.failure_patterns.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]),
        }

    def get_recent_outcomes(self, count: int = 10) -> List[Outcome]:
        """Get recent outcomes"""
        return self.outcomes[-count:]

    def get_pending_adjustments(self) -> List[LearningSignal]:
        """Get pending learning adjustments"""
        return self.adjustments.copy()

    def clear_adjustments(self) -> None:
        """Clear applied adjustments"""
        self.adjustments.clear()

    def should_adjust_trait(self, trait: str) -> Optional[float]:
        """Get adjustment amount for a trait"""
        signal_type = f"trait:{trait}"
        total_delta = sum(s.delta for s in self.adjustments if s.signal_type == signal_type)
        return total_delta if total_delta != 0 else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "character_id": self.character_id,
            "learning_rate": self.learning_rate,
            "enabled": self.enabled,
            "outcomes": [o.to_dict() for o in self.outcomes],
            "success_patterns": self.success_patterns,
            "failure_patterns": self.failure_patterns,
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load from dictionary"""
        self.character_id = data.get("character_id", self.character_id)
        self.learning_rate = data.get("learning_rate", self.learning_rate)
        self.enabled = data.get("enabled", self.enabled)
        self.success_patterns = data.get("success_patterns", {})
        self.failure_patterns = data.get("failure_patterns", {})

        # Reconstruct outcomes
        self.outcomes = []
        for o_data in data.get("outcomes", []):
            outcome = Outcome(
                id=o_data["id"],
                outcome=o_data["outcome"],
                outcome_type=OutcomeType(o_data["outcome_type"]),
                success=o_data["success"],
                reward=o_data["reward"],
                timestamp=datetime.fromisoformat(o_data["timestamp"]),
                notes=o_data.get("notes", ""),
                situation=o_data.get("situation", ""),
                action_taken=o_data.get("action_taken", ""),
                metadata=o_data.get("metadata", {}),
            )
            self.outcomes.append(outcome)

    def _generate_id(self) -> str:
        """Generate unique ID"""
        return f"{self.character_id}_{len(self.outcomes)}_{datetime.now().timestamp()}"

    def __repr__(self) -> str:
        return f"OutcomeTracker(character={self.character_id}, outcomes={len(self.outcomes)})"
