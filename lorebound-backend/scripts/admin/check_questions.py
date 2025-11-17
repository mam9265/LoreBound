#!/usr/bin/env python3
"""Quick script to check question counts per dungeon."""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from app.repositories.base import get_session
from app.domain.models import Question, Dungeon
from sqlalchemy import select, func

async def main():
    async for session in get_session():
        try:
            result = await session.execute(select(Dungeon))
            dungeons = list(result.scalars().all())
            
            print("\nDungeon Question Counts:")
            print("=" * 60)
            
            total = 0
            for d in dungeons:
                count_result = await session.execute(
                    select(func.count(Question.id)).where(Question.dungeon_id == d.id)
                )
                count = count_result.scalar() or 0
                total += count
                status = "✓" if count > 0 else "⚠"
                print(f"{status} {d.title:30} ({d.category:12}): {count:4} questions")
            
            print("=" * 60)
            print(f"Total: {total} questions")
            print()
            
        finally:
            await session.close()
            break

if __name__ == "__main__":
    asyncio.run(main())

