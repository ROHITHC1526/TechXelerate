"""
Motivational tech quotes for hackathon ID cards and emails.
Curated for TechXelarate Hackathon 2026.
"""
import random

TECH_QUOTES = [
    # Primary hackathon quotes (as requested)
    "Code the future.",
    "Innovate beyond limits.",
    "Build. Break. Repeat.",
    "AI is the new electricity.",
    "Think. Build. Lead.",
    
    # Extended set for variety
    "Innovation is not about inventing something new, but solving a problem creatively.",
    "The only way to do great work is to love what you do.",
    "Code is poetry written in logic.",
    "Every bug is a chance to learn something new.",
    "Great things never come from comfort zones.",
    "In technology, there are no limits, only challenges.",
    "Dream big, code bigger.",
    "Build what you believe in.",
    "Your code is your legacy.",
    "Hack today, lead tomorrow.",
    "Think different, code different.",
    "The future is built by those who dare to create.",
    "Every line of code is a step towards excellence.",
    "Innovation starts here.",
    "Be the change you wish to code.",
    "Imagination is more important than knowledge.",
    "The art of programming is the art of solving problems.",
    "Make it work, make it right, make it fast.",
    "Commit to excellence, push to success.",
    "Your idea could change the world.",
    "Ship it, measure it, improve it.",
    "Persistence is the key to mastery.",
    "Create value, deliver impact.",
    "Technology without humanity is just mechanics.",
    "Build solutions, not just code.",
    "The best way to predict the future is to build it.",
    "Keep learning, keep coding, keep winning.",
    "Your potential is unlimited.",
    "Transform ideas into reality.",
    "Be bold, be brave, be brilliant."
]

def get_random_quote() -> str:
    """Get a random motivational tech quote."""
    return random.choice(TECH_QUOTES)

def get_quote_by_index(index: int) -> str:
    """Get a specific quote by index (for consistency)."""
    return TECH_QUOTES[index % len(TECH_QUOTES)]
