# ai-character-sdk

A unified Python SDK for creating AI characters with memory, personality, and decision-making capabilities. Combines an escalation engine, hierarchical memory, and outcome learning into a simple API.

## Brand Line

> Characters that remember, learn, and decide — built for fleet members.

## Installation

```bash
pip install cocapn-ai-character-sdk
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

## Features

- **Unified Character API** — Simple, intuitive interface for character creation
- **6-Tier Memory System** — Hierarchical memory inspired by cognitive neuroscience
- **Intelligent Decision Routing** — Cost-effective escalation engine (BOT/BRAIN/HUMAN tiers)
- **Dynamic Personality** — Trait-based behavior system
- **Outcome Learning** — Reinforcement learning from experience
- **Persistence** — Save and load character state
- **Character Presets** — Pre-built archetypes to get started quickly

## Fleet Context

Part of the Cocapn fleet. Related repos:
- [bordercollie](https://github.com/SuperInstance/bordercollie) — Fleet task herding and orchestration
- [agentic-compiler](https://github.com/SuperInstance/agentic-compiler) — Markdown-to-runtime compilation
- [cudaclaw](https://github.com/SuperInstance/cudaclaw) — GPU-accelerated agent orchestration

---
🦐 Cocapn fleet — lighthouse keeper architecture