# AI Character SDK

A unified Python SDK for creating AI characters with memory, personality, and decision-making capabilities.

## Features

- **Unified Character API** - Simple, intuitive interface for character creation
- **6-Tier Memory System** - Hierarchical memory inspired by cognitive neuroscience
- **Intelligent Decision Routing** - Cost-effective escalation engine
- **Dynamic Personality** - Trait-based behavior system
- **Outcome Learning** - Reinforcement learning from experience
- **Persistence** - Save and load character state
- **Character Presets** - Pre-built archetypes to get started quickly

## Installation

```bash
# From source
cd ai-character-sdk
pip install -e .

# With optional LLM support
pip install -e ".[llm]"
```

## Quick Start

```python
from ai_character_sdk import Character

# Create a character
hero = Character(
    name="Finn the Brave",
    character_class="paladin",
    personality={"bravery": 0.9, "kindness": 0.8}
)

# Use the character
response = hero.think("I see a goblin approaching")
print(response.content)

# Remember experiences
hero.remember("The goblin was actually friendly", importance=7.0)

# Learn from outcomes
hero.learn(outcome="Made a new ally", success=True, reward=10.0)
```

## Character API

### Creating Characters

```python
from ai_character_sdk import Character, create_character, create_preset

# Method 1: Direct creation
hero = Character(
    name="Luna",
    character_class="ranger",
    personality={"bravery": 0.8, "curiosity": 0.9},
    backstory="A wanderer from the northern forests...",
    goals=["Protect the forest", "Help those in need"],
    quirks=["Talks to animals", "Hates cities"],
)

# Method 2: Factory function
hero = create_character(
    name="Luna",
    archetype="ranger",
)

# Method 3: From preset
hero = create_preset("finn_paladin")
```

### Available Presets

- `finn_paladin` - Noble warrior with unwavering justice
- `sage_wizard` - Elderly scholar seeking knowledge
- `shadow_rogue` - Mysterious figure with a dark past
- `melody_bard` - Charismatic performer
- `thok_barbarian` - Towering warrior from the frozen north
- `aria_cleric` - Gentle healer with divine power
- `echo_warlock` - Shadow-touched seeker of redemption

### Think - Generate Responses

```python
response = hero.think(
    situation="A merchant needs help with bandits",
    stakes=0.7,  # 0-1 scale
    urgency_ms=5000,  # Optional time constraint
)

print(response.content)  # What the character says
print(response.action)   # What action they take
print(response.tier)     # BOT, BRAIN, or HUMAN
print(response.confidence)  # Confidence level
```

### Remember - Store Memories

```python
# Store different types of memories
hero.remember(
    "Helped the merchant defeat the bandits",
    importance=7.0,  # 1-10 scale
    emotional_valence=0.8,  # -1 (bad) to +1 (good)
    memory_type="episodic",  # working, mid_term, episodic, semantic, procedural
    participants=["merchant", "bandits"],
    location="Trade Road",
)

# Shortcut methods
hero.store_working("Currently watching the road")  # Current attention
hero.store_episodic("Fought bandits on the trade road")  # Specific event
hero.store_semantic("I always help those in need")  # Fact/belief
hero.store_procedural("I fight best with a bow")  # Skill
```

### Recall - Retrieve Memories

```python
# Search by relevance
memories = hero.recall("bandit fight", top_k=5)

# Get recent memories
recent = hero.get_recent_memories(hours=24, top_k=10)

# Get important memories
important = hero.get_important_memories(threshold=6.0)

# Access memory details
for memory in memories:
    print(f"{memory.content}")
    print(f"  Importance: {memory.importance}")
    print(f"  Accessed: {memory.access_count} times")
```

### Learn - From Outcomes

```python
# Record an outcome
hero.learn(
    outcome="Successfully defended the merchant",
    success=True,
    reward=10.0,
    notes="Gained a reputation as a protector",
)

# Get learning summary
summary = hero.get_learning_summary()
print(f"Success rate: {summary['success_rate']:.1%}")
print(f"Total outcomes: {summary['total_outcomes']}")
```

### Personality - Manage Traits

```python
# View personality
personality = hero.get_personality_summary()
print(personality['traits'])  # All traits

# Get/set individual traits
bravery = hero.get_trait("bravery")
hero.set_trait("bravery", 0.95)

# Modify traits gradually
hero.modify_trait("bravery", 0.05)  # Increase by 0.05

# Available trait categories:
# - Social: charisma, kindness, empathy, diplomacy, loyalty
# - Intellectual: intelligence, curiosity, wisdom, caution, cunning
# - Emotional: bravery, optimism, patience, humor, aggression
# - Moral: honor, justice, honesty, devotion, mercy
# - Behavioral: initiative, discipline, ambition, independence, adaptability
```

### Persistence - Save and Load

```python
# Save character
hero.save("/path/to/hero.json")

# Load character
hero = Character(name="Hero")
hero.load("/path/to/hero.json")

# Get full stats
stats = hero.get_stats()
print(stats)
```

## Architecture

### Decision Tiers

The SDK uses intelligent routing through three decision tiers:

| Tier | Use Case | Cost | Speed |
|------|----------|------|-------|
| **BOT** | Routine situations, high familiarity | Free | Fastest |
| **BRAIN** | Novel situations, personality-driven | Low | Medium |
| **HUMAN** | Critical decisions, high stakes | High | Slowest |

Routing is based on:
- Stakes assessment
- Novelty detection
- Time constraints
- Historical performance

### Memory System

Six-tier hierarchical memory:

1. **Working** - Current attention (seconds to minutes)
2. **Mid-Term** - Session buffer (1-6 hours)
3. **Long-Term** - Consolidated storage (1+ weeks)
4. **Episodic** - Specific events ("what-where-when")
5. **Semantic** - Consolidated patterns & facts
6. **Procedural** - Skills & learned behaviors

Memory retrieval uses weighted scoring:
- Recency score (exponential decay)
- Importance score (1-10 scale)
- Relevance score (word overlap)

## Examples

See the `examples/` directory for more:

```bash
# Quick start demo
python examples/quickstart.py

# Preset character demo
python examples/finn_the_paladin.py

# Party-based multi-character demo
python examples/party_example.py
```

## Advanced Usage

### Custom LLM Integration

```python
def llm_think_handler(character, situation, context, high_stakes=False):
    # Your LLM integration here
    response = call_llm(
        system=f"You are {character.name}, a {character.character_class}",
        user=context,
    )
    return {
        "content": response,
        "action": "talk",
        "confidence": 0.8,
        "thoughts": "Generated via LLM",
    }

hero = Character(
    name="Wizard",
    on_think=llm_think_handler,
)
```

### Multi-Agent Coordination

```python
from ai_character_sdk import create_party

# Create a balanced party
party = create_party()

# Each character responds to the same situation
for role, character in party.items():
    response = character.think("A dragon appears!")
    print(f"{character.name}: {response.content}")
```

## Project Structure

```
ai-character-sdk/
├── src/ai_character_sdk/
│   ├── __init__.py          # Main exports
│   ├── core/
│   │   ├── character.py     # Character class
│   │   ├── presets.py       # Character presets
│   │   └── factory.py       # Factory functions
│   ├── memory/
│   │   └── hierarchical.py  # Memory system
│   ├── decision/
│   │   └── engine.py        # Decision routing
│   ├── personality/
│   │   └── traits.py        # Personality system
│   └── learning/
│       └── outcomes.py      # Learning system
├── examples/
│   ├── quickstart.py
│   ├── finn_the_paladin.py
│   └── party_example.py
├── pyproject.toml
└── README.md
```

## License

MIT

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.
