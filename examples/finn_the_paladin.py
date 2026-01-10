"""
Finn the Paladin - Example Character

A noble warrior with unwavering sense of justice.
Demonstrates the full Character API.
"""

from ai_character_sdk import Character, create_preset


def main():
    print("=" * 60)
    print("Finn the Paladin - Character Demo")
    print("=" * 60)
    print()

    # Create Finn from preset
    finn = create_preset("finn_paladin")

    print(f"Created: {finn}")
    print()

    # ========================================================================
    # THINK - Respond to situations
    # ========================================================================

    print("SITUATION: A goblin approaches the village")
    print("-" * 40)

    response = finn.think(
        "A goblin is approaching the village gates",
        stakes=0.6,
    )

    print(f"Response: {response.content}")
    print(f"Action: {response.action}")
    print(f"Tier: {response.tier.value}")
    print(f"Confidence: {response.confidence:.2f}")
    print()

    # ========================================================================
    # REMEMBER - Store experiences
    # ========================================================================

    print("STORING MEMORIES")
    print("-" * 40)

    finn.remember(
        "The goblin was actually a messenger",
        importance=7.0,
        emotional_valence=0.3,
        memory_type="episodic",
    )

    finn.remember(
        "I always try diplomacy before combat",
        importance=8.0,
        emotional_valence=0.7,
        memory_type="semantic",
    )

    print(f"Stored {len(finn.memory.memories)} memories")
    print()

    # ========================================================================
    # RECALL - Retrieve memories
    # ========================================================================

    print("RECALLING MEMORIES")
    print("-" * 40)

    relevant = finn.recall("goblin diplomacy", top_k=3)
    for i, memory in enumerate(relevant, 1):
        print(f"{i}. [{memory.memory_type.value}] {memory.content}")
    print()

    # ========================================================================
    # LEARN - Learn from outcomes
    # ========================================================================

    print("LEARNING")
    print("-" * 40)

    finn.learn(
        outcome="Diplomacy worked! The goblin became an ally.",
        success=True,
        reward=10.0,
    )

    summary = finn.get_learning_summary()
    print(f"Success rate: {summary['success_rate']:.1%}")
    print()

    # ========================================================================
    # PERSONALITY - View and modify traits
    # ========================================================================

    print("PERSONALITY")
    print("-" * 40)

    personality = finn.get_personality_summary()
    print("Traits:")
    for trait, value in personality['traits'].items():
        print(f"  {trait}: {value:.2f}")
    print()

    # ========================================================================
    # STATS - View full character stats
    # ========================================================================

    print("CHARACTER STATS")
    print("-" * 40)

    stats = finn.get_stats()
    print(f"Name: {stats['name']}")
    print(f"Class: {stats['character_class']}")
    print(f"Interactions: {stats['interaction_count']}")
    print(f"Total memories: {stats['memory']['total_memories']}")
    print()

    # ========================================================================
    # SAVE - Persist character
    # ========================================================================

    print("PERSISTENCE")
    print("-" * 40)

    finn.save("/tmp/finn_character.json")
    print("Character saved to /tmp/finn_character.json")
    print()

    print("=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
