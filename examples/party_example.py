"""
Party Example - Creating a balanced adventuring party

Demonstrates creating multiple characters and using them together.
"""

from ai_character_sdk import create_party, Character


def main():
    print("=" * 60)
    print("Adventuring Party - Multi-Character Demo")
    print("=" * 60)
    print()

    # ========================================================================
    # CREATE A PARTY
    # ========================================================================

    print("Creating a balanced adventuring party...")
    print()

    party = create_party()

    for role, character in party.items():
        print(f"{role.upper()}: {character.name} ({character.character_class})")

    print()

    # ========================================================================
    # PARTY INTERACTION - Combat scenario
    # ========================================================================

    print("SCENARIO: The party encounters a dragon!")
    print("-" * 40)
    print()

    # Each character responds to the situation
    for role, character in party.items():
        print(f"{character.name} ({role}):")
        response = character.think(
            "A massive dragon blocks our path, breathing fire!",
            stakes=0.95,  # Very high stakes!
        )
        print(f"  Response: {response.content}")
        print(f"  Action: {response.action}")
        print(f"  Confidence: {response.confidence:.2f}")
        print()

    # ========================================================================
    # AFTERMATH - Remember and learn
    # ========================================================================

    print("AFTERMATH: The party defeats the dragon together")
    print("-" * 40)
    print()

    for role, character in party.items():
        # Store the memory
        character.remember(
            f"We defeated a great dragon as a team!",
            importance=9.5,
            emotional_valence=0.9,
        )

        # Learn from the victory
        character.learn(
            outcome="Defeated the dragon through teamwork",
            success=True,
            reward=20.0,
        )

        print(f"{character.name}: {len(character.memory.memories)} memories")

    print()

    # ========================================================================
    # PARTY STATS
    # ========================================================================

    print("PARTY STATISTICS")
    print("-" * 40)
    print()

    total_interactions = sum(c.interaction_count for c in party.values())
    total_memories = sum(len(c.memory.memories) for c in party.values())
    total_successes = sum(
        c.get_learning_summary()['success_count']
        for c in party.values()
    )

    print(f"Total party interactions: {total_interactions}")
    print(f"Total party memories: {total_memories}")
    print(f"Total successful outcomes: {total_successes}")
    print()

    # ========================================================================
    # CREATE CUSTOM CHARACTER FOR THE PARTY
    # ========================================================================

    print("ADDING A NEW MEMBER")
    print("-" * 40)
    print()

    # Create a custom character
    druid = Character(
        name="Leaf",
        character_class="druid",
        personality={
            "wisdom": 0.9,
            "kindness": 0.85,
            "nature_affinity": 0.95,
        },
        backstory="Raised by spirits in an ancient forest, Leaf seeks to heal the land.",
        goals=["Protect nature", "Heal the wounded", "Restore balance"],
        quirks=["Talks to plants", "Barefoot always", "Hates metal"],
    )

    party["druid"] = druid

    print(f"Welcome, {druid.name} the {druid.character_class}!")
    print()

    # New character responds
    response = druid.think(
        "The party asks me to join their quest",
        stakes=0.6,
    )
    print(f"{druid.name}: {response.content}")
    print()

    print("=" * 60)
    print("Party complete! Ready for adventure.")
    print("=" * 60)


if __name__ == "__main__":
    main()
