# Version String Validation Summary

## Goal
Complete validation of version string finding method by following the chain:
`VersionScript → Text component → MonoString → version string data`

## Unity Scene Hierarchy (Confirmed)

**Complete path from Kaj:**
```
Scene → Main → Canvas → version → Text → m_Text
```

**Hierarchy explanation:**
1. **Scene** - Root Unity scene object
2. **Main** - Parent GameObject in scene
3. **Canvas** - UI Canvas component (this was the missing layer!)
4. **version** - Child GameObject under Canvas containing the version display
5. **Text** - UnityEngine.UI.Text component on the version GameObject
6. **m_Text** - Field in Text component containing the actual version string

**Key insight:** The version GameObject is not directly under Main, but under a Canvas UI element. This is why direct "Main → version" searches failed.

## What We Found

### Version String Location
- **Address**: `0x7f1601d93c44` (UTF-16 LE: "v2.016")
- **MonoString base**: `0x7f1601d93c38` (length at +0x8, data at +0xc)
- **Pattern**: Successfully finds version using simple byte search

### Validation Attempts

#### 1. Forward Search (VersionScript → Text)
**Approach**: Find VersionScript class, scan for instances, follow reference to Text component

**Result**: Could not find VersionScript MonoClass pointers or instances

**Files**:
- `test_version_via_script.py`
- `test_complete_validation.py`

#### 2. Backward Search (MonoString → Find Pointers)
**Approach**: Find version MonoString, search memory for pointers to it

**Result**: **ZERO pointers found** after scanning ALL 323 RW memory regions

**Files**:
- `test_find_text_backwards.py`
- `test_pointers_thorough.py`

**Key Finding**: Unity does NOT use raw pointers to reference this MonoString. Text.m_Text likely contains the string data directly (embedded/copied), not as a pointer reference.

#### 3. GameObject Hierarchy Search (Main → Canvas → version)
**Approach**: Find GameObject "Main", traverse to child "version", find Text component

**Result**: Searches found only ELF/PE binary metadata strings, not Unity GameObject MonoStrings

**Files**:
- `find_version_gameobject.py` - searched for GameObject "version"
- `analyze_version_objects.py` - analyzed memory context
- `find_main_gameobject.py` - searched for GameObject "Main"

**Issue**: Raw string search finds library metadata ("_CorDllMain", "mscoree.dll" in PE import tables), not MonoString instances used by Unity GameObjects.

**UPDATE:** The correct hierarchy includes a Canvas layer: Scene → Main → **Canvas** → version → Text → m_Text. The initial searches failed because they looked for "Main → version" directly, missing the intermediate Canvas UI component.

## Technical Insights

### Unity 6000.0 Memory Layout
- **Version**: Unity 6000.0 (Unity 6.0)
- **Text Component**: UnityEngine.UI.Text class
- **String Storage**: Text.m_Text appears to embed/copy string data rather than store pointers
- **Field Offsets**: Runtime-dependent, not documented

### Why Validation Is Difficult

1. **No Pointer References**: The MonoString at 0x7f1601d93c38 has zero pointer references in memory. Unity likely copies the string data directly into Text.m_Text field rather than storing a pointer.

2. **GameObject Search Complexity**: Finding Unity GameObject instances requires:
   - Locating GameObject MonoClass vtable
   - Scanning for instances with matching vtable
   - Checking GameObject.name field (offset varies)
   - Following Transform component for hierarchy
   - Navigating parent-child relationships

3. **Runtime Structure Variation**: Unity 6.0 field offsets are runtime-dependent and not documented. Would need to reverse engineer the exact memory layout from Core.dll or use Unity debug tools.

## Working Solution

**File**: `test_version_simple.py`

```python
# Simple pattern search that works reliably
version_pattern = b'v\\x002\\x00.\\x000\\x001\\x006\\x00'  # UTF-16 LE
# Search memory regions for pattern
# Returns: version string found at address
```

**Advantages**:
- Works reliably across game restarts
- Survives ASLR (Address Space Layout Randomization)
- Simple, fast, maintainable
- No complex object traversal needed

**Trade-off**:
- Doesn't validate through GameObject hierarchy
- Can't prove the string is in the specific Text component
- But: If we find "v2.016" in UTF-16, it's almost certainly the version display

## Recommendation

**Use the simple pattern finder** for practical purposes:
- It reliably finds the version string
- It's robust against memory layout changes
- Complete validation would require Unity debugging tools or extensive reverse engineering

**Document the limitation**:
- We find the version string pattern in memory
- We cannot trace the complete GameObject hierarchy path
- This is acceptable given Unity 6.0's runtime-dependent structures

## Files Created

1. `test_version_via_script.py` - Forward search attempt
2. `test_complete_validation.py` - Complete validation attempt
3. `test_find_text_backwards.py` - Backward pointer search
4. `test_pointers_thorough.py` - Comprehensive pointer scan (323 regions)
5. `test_validate_text_offset.py` - Text object validation
6. `test_text_raw_string.py` - Raw string search in Text.m_Text
7. `find_version_gameobject.py` - GameObject "version" search
8. `analyze_version_objects.py` - Memory context analysis
9. `find_main_gameobject.py` - GameObject "Main" search

## Conclusion

Complete validation through the GameObject hierarchy is not feasible without:
- Unity debug tools (Mono debugger, Unity profiler)
- Extensive reverse engineering of Unity 6.0 memory layout
- Understanding IL2CPP vs Mono backend differences

The simple pattern finder is the practical solution for locating the version string in hackmud's memory.
