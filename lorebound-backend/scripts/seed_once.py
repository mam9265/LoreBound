"""
Compatibility wrapper for scripts.seeding.seed_once
Maintains backward compatibility with existing references.
"""
import sys
from scripts.seeding.seed_once import *  # noqa

# The seed_once script executes on import, so we just import it

