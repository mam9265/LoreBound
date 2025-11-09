#!/usr/bin/env python3
"""
Script to create profiles for users who don't have one.
Run this to fix existing users who registered before profiles were added.
"""

import asyncio
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.domain.models import User, Profile
from app.core.config import get_settings

async def create_missing_profiles():
    """Create profiles for users who don't have one."""
    settings = get_settings()
    
    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=False
    )
    
    # Create async session
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        # Get all users
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        print(f"\nFound {len(users)} users")
        
        created_count = 0
        for user in users:
            # Check if user has a profile
            profile_result = await session.execute(
                select(Profile).where(Profile.user_id == user.id)
            )
            profile = profile_result.scalar_one_or_none()
            
            if not profile:
                # Generate a handle from email or user ID
                if user.email:
                    base_handle = user.email.split('@')[0][:20]
                else:
                    base_handle = f"User{str(user.id)[:8]}"
                
                # Check if handle exists
                handle = base_handle
                counter = 1
                while True:
                    check_result = await session.execute(
                        select(Profile).where(Profile.handle == handle)
                    )
                    if check_result.scalar_one_or_none() is None:
                        break
                    handle = f"{base_handle}{counter}"
                    counter += 1
                
                # Create profile
                new_profile = Profile(
                    user_id=user.id,
                    handle=handle,
                    level=1,
                    xp=0,
                    avatar_layers={}
                )
                session.add(new_profile)
                created_count += 1
                print(f"✓ Created profile for user {user.id} with handle '{handle}'")
            else:
                print(f"  User {user.id} already has profile '{profile.handle}'")
        
        # Commit all changes
        await session.commit()
        
        print(f"\n✓ Created {created_count} new profiles")
        print(f"✓ {len(users) - created_count} users already had profiles")
    
    await engine.dispose()

if __name__ == "__main__":
    print("=" * 60)
    print("Creating Missing User Profiles")
    print("=" * 60)
    asyncio.run(create_missing_profiles())
    print("\n✓ Done!")
