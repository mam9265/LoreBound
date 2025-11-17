"""
Compatibility wrapper for scripts.seeding.populate_questions
Maintains backward compatibility with existing references.

Usage:
    python -m scripts.populate_questions
    python -m scripts.populate_questions --category music --count 100
"""
import sys
from scripts.seeding.populate_questions import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())

