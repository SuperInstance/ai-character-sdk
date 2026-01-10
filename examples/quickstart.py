"""
Quick Start Example - AI Character SDK

This example shows the simplest way to create and use a character.
"""

from ai_character_sdk import Character


def main():
    print("=" * 60)
    print("AI Character SDK - Quick Start")
    print("=" * 60)
    print()

    # ========================================================================
    # 1. CREATE A CHARACTER
    # ========================================================================
    print("1. Creating a character...")
    print()

    hero = Character(
        name="Luna",
        character_class="ranger",
        personality={
            "bravery": 0.8,
            "curiosity": 0.9,
            "kindness": 0.7,
        },
        backstory="A wanderer from the northern forests who seeks to protect nature.",
        goals=["Protect the forest", "Help those in need", "Find ancient knowledge"],
    )

    print(f"Created: {hero}")
    print()

    # ========================================================================
    # 2. THINK - Generate responses
    # ========================================================================
    print("2. Think - Respond to situations")
    print()

    situations = [
        ("A merchant needs help with bandits", 0.7),
        ("An injured animal is by the road", 0.5),
        ("A mysterious artifact glows in the ruins", 0.6),
    ]

    for situation, stakes in situations:
        print(f"Situation: {situation}")
        response = hero.think(situation, stakes=stakes)
        print(f"  Response: {response.content}")
        print(f"  Action: {response.action}")
        print()

    # ========================================================================
    # 3. REMEMBER - Store experiences
    # ========================================================================
    print("3. Remember - Store memories")
    print()

    hero.remember(
        "Helped the merchant defeat the bandits",
        importance=7.0,
        emotional_valence=0.8,
    )

    hero.remember(
        "Healed the animal and it became a companion",
        importance=8.0,
        emotional_valence=0.9,
    )

    hero.remember(
        "The artifact was part of an ancient druid circle",
        importance=9.0,
        emotional_valence=0.7,
    )

    print(f"Stored {len(hero.memory.memories)} memories")
    print()

    # ========================================================================
    # 4. RECALL - Retrieve memories
    # ========================================================================
    print("4. Recall - Retrieve relevant memories")
    print()

    query = "artifact druid ancient"
    relevant = hero.recall(query, top_k=3)

    print(f"Memories about '{query}':")
    for i, memory in enumerate(relevant, 1):
        print(f"  {i}. {memory.content}")
    print()

    # ========================================================================
    # 5. LEARN - Learn from outcomes
    # ========================================================================
    print("5. Learn - Outcome-based learning")
    print()

    hero.learn(
        outcome="Successfully protected the forest from loggers",
        success=True,
        reward=15.0,
    )

    learning = hero.get_learning_summary()
    print(f"Total outcomes: {learning['total_outcomes']}")
    print(f"Success rate: {learning['success_rate']:.1%}")
    print()

    # ========================================================================
    # 6. SAVE - Persist character
    # ========================================================================
    print("6. Save - Persist character state")
    print()

    hero.save("/tmp/luna_character.json")
    print("Character saved!")
    print()

    print("=" * 60)
    print("That's it! You've created your first AI character.")
    print("=" * 60)


if __name__ == "__main__":
    main()
