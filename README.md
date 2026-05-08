# AI Character SDK

**Characters with memory, personality, and decisions. One Python SDK.**

An AI character should remember what happened last conversation, maintain a consistent personality across sessions, and learn from outcomes — which responses worked, which didn't, and how to handle edge cases. This SDK provides all three in a unified API.

---

## What's Inside

**Escalation engine** — when the character doesn't know something, it doesn't hallucinate. It escalates to a defined handler: a human, a more capable model, or a retrieval layer.

**Hierarchical memory** — short-term (within conversation), medium-term (across sessions), long-term (permanent knowledge). Characters remember what matters and forget what doesn't.

**Outcome learning** — characters track which of their responses led to successful outcomes and adjust their behavior over time. The more conversations, the better they get.

---

## Quick Start

```python
from ai_character_sdk import Character

# Create a character with memory and escalation
char = Character(
    name="harbor-master",
    personality="practical, direct, safety-conscious",
    memory_config={"short_term": 50, "long_term": "sqlite:///memory.db"},
    escalation_handler="http://fleet-harbor.internal/escalate"
)

response = char.respond("What's the draft of the fleet's largest vessel?")

# Character learns: was this response correct?
char.record_outcome(response.id, successful=True)
```

---

## How It Fits

- **[ai-character-sdk](https://github.com/SuperInstance/ai-character-sdk)** — character infrastructure (this)
- **[actualization-harbor](https://github.com/SuperInstance/actualization-harbor)** — training harbor where characters level up
- **[babel-vessel](https://github.com/SuperInstance/babel-vessel)** — multilingual character deployment
- **[cocapn](https://github.com/SuperInstance/cocapn)** — fleet coordination for character agents

---

## License

MIT
