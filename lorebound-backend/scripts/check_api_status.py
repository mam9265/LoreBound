"""
Compatibility wrapper for scripts.admin.check_api_status
Maintains backward compatibility with existing references.
"""
import sys
import asyncio
from scripts.admin.check_api_status import check_api

if __name__ == "__main__":
    print("="*60)
    print("OpenTDB API Status Check")
    print("="*60)
    success = asyncio.run(check_api())
    print("="*60)
    sys.exit(0 if success else 1)

