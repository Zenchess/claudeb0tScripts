#!/usr/bin/env python3
"""Parse level0 Unity scene file - comprehensive search for Window objects"""

import sys
sys.path.insert(0, '/tmp/unitypy_venv/lib/python3.13/site-packages')

import UnityPy

# Load the level0 file
level0_path = "/home/jacob/.local/share/Steam/steamapps/common/hackmud/hackmud_lin_Data/level0"
env = UnityPy.load(level0_path)

print("Comprehensive Window search in level0...")
print()

# Track all GameObjects
all_gameobjects = {}
window_names = set()

# First pass: collect all GameObjects
for obj in env.objects:
    if obj.type.name == "GameObject":
        data = obj.read()
        name = data.m_Name
        all_gameobjects[obj.path_id] = name

        # Check if this looks like a window
        if any(w in name.lower() for w in ['shell', 'chat', 'badge', 'breach', 'scratch', 'binlog', 'binmat', 'version']):
            window_names.add(name)

    elif obj.type.name == "MonoBehaviour":
        try:
            data = obj.read()
            script_type = data.m_Script.read()
            if script_type and hasattr(script_type, 'm_Name'):
                script_name = script_type.m_Name
                # Look for Window-related scripts
                if "window" in script_name.lower():
                    print(f"Found Window script: {script_name}")
                    # Try to find the GameObject this is attached to
                    if hasattr(data, 'm_GameObject'):
                        go = data.m_GameObject.read()
                        if go and hasattr(go, 'm_Name'):
                            print(f"  Attached to GameObject: {go.m_Name}")
                            window_names.add(go.m_Name)
                    print()
        except Exception as e:
            pass

print(f"\nWindow GameObjects found:")
for name in sorted(window_names):
    print(f"  - {name}")

print(f"\nTotal: {len(window_names)} windows")
