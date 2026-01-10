"""
Basic tests for AI Character SDK
"""

import pytest
from ai_character_sdk import Character, create_preset, create_party, available_presets


def test_character_creation():
    """Test basic character creation"""
    hero = Character(
        name="Test Hero",
        character_class="warrior",
        personality={"bravery": 0.8},
    )
    assert hero.name == "Test Hero"
    assert hero.character_class == "warrior"
    assert hero.get_trait("bravery") == 0.8


def test_character_think():
    """Test character thinking"""
    hero = Character(
        name="Test",
        personality={"bravery": 0.9},
    )
    response = hero.think("A goblin appears", stakes=0.5)
    assert response.content is not None
    assert response.tier is not None


def test_character_remember():
    """Test memory storage"""
    hero = Character(name="Test")
    memory = hero.remember("This is a test memory", importance=7.0)
    assert memory.content == "This is a test memory"
    assert memory.importance == 7.0


def test_character_recall():
    """Test memory retrieval"""
    hero = Character(name="Test")
    hero.remember("Fought a dragon", importance=8.0)
    hero.remember("Ate lunch", importance=3.0)

    memories = hero.recall("dragon", top_k=5)
    assert len(memories) > 0
    assert any("dragon" in m.content.lower() for m in memories)


def test_character_learn():
    """Test learning from outcomes"""
    hero = Character(name="Test")
    signal = hero.learn(outcome="Won the battle", success=True, reward=10.0)

    summary = hero.get_learning_summary()
    assert summary["total_outcomes"] == 1
    assert summary["success_count"] == 1


def test_personality_traits():
    """Test personality trait management"""
    hero = Character(
        name="Test",
        personality={"bravery": 0.5, "kindness": 0.7}
    )

    assert hero.get_trait("bravery") == 0.5
    assert hero.get_trait("kindness") == 0.7

    hero.set_trait("bravery", 0.9)
    assert hero.get_trait("bravery") == 0.9

    hero.modify_trait("bravery", -0.2)
    assert hero.get_trait("bravery") == 0.7


def test_character_stats():
    """Test character statistics"""
    hero = Character(name="Test")
    hero.think("Test situation")

    stats = hero.get_stats()
    assert "name" in stats
    assert "memory" in stats
    assert "learning" in stats


def test_presets():
    """Test character presets"""
    presets = available_presets()
    assert len(presets) > 0
    assert "finn_paladin" in presets

    finn = create_preset("finn_paladin")
    assert finn.name == "Finn the Brave"
    assert finn.character_class == "paladin"


def test_party_creation():
    """Test party creation"""
    party = create_party()
    assert len(party) > 0
    assert "tank" in party
    assert "healer" in party


def test_trait_clamping():
    """Test that trait values are clamped to 0-1"""
    hero = Character(name="Test")
    hero.set_trait("bravery", 1.5)  # Above 1
    assert hero.get_trait("bravery") == 1.0

    hero.set_trait("bravery", -0.5)  # Below 0
    assert hero.get_trait("bravery") == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
