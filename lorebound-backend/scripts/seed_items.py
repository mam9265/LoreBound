"""
Compatibility wrapper for scripts.seeding.seed_items
Maintains backward compatibility with existing references.
"""
import asyncio
from scripts.seeding.seed_items import seed_items

if __name__ == "__main__":
    asyncio.run(seed_items())

