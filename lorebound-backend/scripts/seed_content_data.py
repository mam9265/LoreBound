"""
Compatibility wrapper for scripts.seeding.seed_content_data
Maintains backward compatibility with existing references.
"""
import sys
import asyncio
from scripts.seeding.seed_content_data import main

if __name__ == "__main__":
    asyncio.run(main())

