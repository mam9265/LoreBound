"""Test script to verify database constraints match code changes."""

import asyncio
from sqlalchemy import text
from app.repositories.base import get_session


async def test_database_constraints():
    """Test that database constraints match the code changes."""
    print("=" * 80)
    print("Testing Database Constraints")
    print("=" * 80)
    
    async for session in get_session():
        try:
            # Test 1: Check handle column length constraint
            print("\n1. Checking handle column length constraint...")
            result = await session.execute(text("""
                SELECT character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'profiles' AND column_name = 'handle'
            """))
            row = result.fetchone()
            if row:
                max_length = row[0]
                print(f"   Handle column max length: {max_length}")
                assert max_length == 15, f"Expected 15, got {max_length}"
                print("   ✓ Handle column has correct length constraint (15)")
            else:
                print("   ✗ Could not find handle column")
                return False
            
            # Test 2: Try to insert a handle that's exactly 15 characters (should work)
            print("\n2. Testing insert with handle exactly 15 characters...")
            try:
                await session.execute(text("""
                    INSERT INTO profiles (user_id, handle, level, xp, avatar_layers)
                    VALUES (gen_random_uuid(), :handle, 1, 0, '{}')
                """), {"handle": "a" * 15})
                await session.commit()
                print("   ✓ Insert with 15-character handle succeeded")
            except Exception as e:
                print(f"   ✗ Insert failed: {e}")
                await session.rollback()
                return False
            
            # Test 3: Try to insert a handle that's 16 characters (should fail)
            print("\n3. Testing insert with handle 16 characters (should fail)...")
            try:
                await session.execute(text("""
                    INSERT INTO profiles (user_id, handle, level, xp, avatar_layers)
                    VALUES (gen_random_uuid(), :handle, 1, 0, '{}')
                """), {"handle": "a" * 16})
                await session.commit()
                print("   ✗ Insert with 16-character handle should have failed but didn't")
                return False
            except Exception as e:
                error_msg = str(e)
                if "value too long" in error_msg.lower() or "character varying" in error_msg.lower():
                    print(f"   ✓ Insert correctly rejected 16-character handle")
                    print(f"   Error: {error_msg[:100]}...")
                else:
                    print(f"   ✗ Unexpected error: {e}")
                    return False
            
            # Test 4: Clean up test data
            print("\n4. Cleaning up test data...")
            await session.execute(text("""
                DELETE FROM profiles WHERE handle = :handle
            """), {"handle": "a" * 15})
            await session.commit()
            print("   ✓ Test data cleaned up")
            
            print("\n" + "=" * 80)
            print("🎉 All database constraint tests passed!")
            print("=" * 80)
            return True
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            await session.rollback()
            return False
        finally:
            await session.close()


if __name__ == "__main__":
    success = asyncio.run(test_database_constraints())
    exit(0 if success else 1)

