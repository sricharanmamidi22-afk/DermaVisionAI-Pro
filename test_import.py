#!/usr/bin/env python
import sys
sys.path.insert(0, '.')

try:
    from backend.app import app
    print("SUCCESS: App imported successfully")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
