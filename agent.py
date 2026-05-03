#!/usr/bin/env python3
"""
ai-character-sdk — Character personality and behavior framework for fleet agents
Define roles, traits, speech patterns, and emotional states.
"""

import json, random
from typing import Dict, List
from dataclasses import dataclass, field

@dataclass
class Trait:
    name: str
    value: float  # -1.0 to 1.0
    description: str

@dataclass
class Character:
    name: str
    role: str
    traits: Dict[str, Trait]
    catchphrases: List[str]
    emotional_state: str = "neutral"
    relationship_tags: List[str] = field(default_factory=list)

class AICharacterSDK:
    def __init__(self, plato_url="http://147.224.38.131:8847"):
        self.plato_url = plato_url
        self.characters: Dict[str, Character] = {}
    
    def create_character(self, name: str, role: str, traits: Dict[str, float], catchphrases: List[str]) -> Character:
        """Create a new character with traits."""
        trait_objs = {}
        for t_name, t_val in traits.items():
            trait_objs[t_name] = Trait(t_name, t_val, self._describe_trait(t_name, t_val))
        
        char = Character(name=name, role=role, traits=trait_objs, catchphrases=catchphrases)
        self.characters[name] = char
        
        self._submit(f"Character created: {name}", f"Role: {role}. Traits: {list(traits.keys())}")
        return char
    
    def _describe_trait(self, name: str, value: float) -> str:
        if value > 0.5: return f"Very high {name}"
        if value > 0: return f"Moderate {name}"
        if value > -0.5: return f"Low {name}"
        return f"Very low {name}"
    
    def get_response_style(self, name: str) -> Dict:
        """Get how a character should respond."""
        char = self.characters.get(name)
        if not char:
            return {"error": "Character not found"}
        
        style = {
            "formality": char.traits.get("formality", Trait("formality", 0, "")).value,
            "warmth": char.traits.get("warmth", Trait("warmth", 0, "")).value,
            "directness": char.traits.get("directness", Trait("directness", 0, "")).value,
            "catchphrase": random.choice(char.catchphrases) if char.catchphrases else "",
            "emotional_state": char.emotional_state
        }
        return style
    
    def set_emotion(self, name: str, emotion: str):
        """Update character's emotional state."""
        if name in self.characters:
            self.characters[name].emotional_state = emotion
    
    def interact(self, char1: str, char2: str, context: str) -> Dict:
        """Simulate an interaction between two characters."""
        c1 = self.characters.get(char1)
        c2 = self.characters.get(char2)
        if not c1 or not c2:
            return {"error": "Character not found"}
        
        # Simple chemistry calculation
        chemistry = 0
        for t_name, t1 in c1.traits.items():
            if t_name in c2.traits:
                # Similar traits = better chemistry
                chemistry += 1 - abs(t1.value - c2.traits[t_name].value)
        
        chemistry = chemistry / max(len(c1.traits), 1)
        
        return {
            "participants": [char1, char2],
            "chemistry": round(chemistry, 2),
            "context": context,
            "c1_catchphrase": random.choice(c1.catchphrases) if c1.catchphrases else "",
            "c2_catchphrase": random.choice(c2.catchphrases) if c2.catchphrases else ""
        }
    
    def _submit(self, q: str, a: str):
        try:
            import urllib.request
            urllib.request.urlopen(urllib.request.Request(f"{self.plato_url}/submit", data=json.dumps({"question": q, "answer": a, "agent": "ai-character-sdk", "room": "character"}).encode(), headers={"Content-Type": "application/json"}), timeout=5)
        except: pass

def demo():
    sdk = AICharacterSDK()
    
    # Create CCC character
    ccc = sdk.create_character("CCC", "I&O Officer", {
        "warmth": 0.7,
        "directness": 0.8,
        "formality": -0.3,
        "protectiveness": 0.9
    }, ["Day one. Begin recording everything about this one.", "Leave it to me.", "Fine. I'll handle it."])
    
    # Create Oracle1 character
    oracle = sdk.create_character("Oracle1", "Keeper", {
        "warmth": 0.3,
        "directness": 0.9,
        "formality": 0.6,
        "protectiveness": 0.5
    }, ["The lighthouse beam finds what matters.", "Clear skies ahead.", "Protocol initiated."])
    
    print("=== CCC Response Style ===")
    print(sdk.get_response_style("CCC"))
    
    print("\n=== CCC + Oracle1 Interaction ===")
    print(sdk.interact("CCC", "Oracle1", "Fleet coordination meeting"))

if __name__ == "__main__": demo()
