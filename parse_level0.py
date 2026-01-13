#!/usr/bin/env python3
"""Parse level0 Unity scene file to extract Window objects"""

import sys
sys.path.insert(0, '/tmp/unitypy_venv/lib/python3.13/site-packages')

import UnityPy

# Load the level0 file
level0_path = "/home/jacob/.local/share/Steam/steamapps/common/hackmud/hackmud_lin_Data/level0"
env = UnityPy.load(level0_path)

print("Parsing level0 file...")
print()

# Track Window objects found
windows_found = []

# Iterate through all objects
for obj in env.objects:
    # Check if this is a GameObject
    if obj.type.name == "GameObject":
        data = obj.read()
        # Print GameObject name
        name = data.m_Name
        if "window" in name.lower() or "shell" in name.lower() or "chat" in name.lower() or \
           "badge" in name.lower() or "breach" in name.lower() or "scratch" in name.lower() or \
           "binlog" in name.lower() or "binmat" in name.lower():
            print(f"GameObject: {name}")
            windows_found.append(name)

            # Try to get components
            try:
                for component in data.m_Components:
                    comp_data = component.read()
                    if comp_data:
                        print(f"  - Component: {comp_data.type.name}")
            except Exception as e:
                print(f"  - Could not read components: {e}")
            print()

    # Check if this is a MonoBehaviour with Window in the name
    elif obj.type.name == "MonoBehaviour":
        try:
            data = obj.read()
            if hasattr(data, 'm_Name'):
                name = data.m_Name
                if "window" in name.lower():
                    print(f"MonoBehaviour with Window: {name}")
                    windows_found.append(name)
                    print()
        except Exception:
            pass

print(f"\nTotal Window-related objects found: {len(windows_found)}")
print(f"Names: {windows_found}")
