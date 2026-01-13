"""Offset generation and management for hackmud memory scanner

Handles Core.dll decompilation and offset extraction.
"""

import subprocess
import re
import json
import shutil
from pathlib import Path
from typing import Dict, Optional


# Default decompilation output directory
DEFAULT_OUTPUT_DIR = Path("/tmp/hackmud_decompiled")


def decompile_dll(core_dll: Path, output_dir: Optional[Path] = None) -> Optional[Path]:
    """Decompile Core.dll using ilspycmd

    Args:
        core_dll: Path to Core.dll
        output_dir: Output directory (defaults to /tmp/hackmud_decompiled)

    Returns:
        Path to decompiled .cs file, or None if failed
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    # Clean and recreate output directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "Core.decompiled.cs"

    print(f"Decompiling {core_dll}...")

    # Find ilspycmd (check ~/.dotnet/tools first, then PATH)
    ilspycmd = Path.home() / ".dotnet/tools/ilspycmd"
    if not ilspycmd.exists():
        ilspycmd = "ilspycmd"  # Try PATH

    result = subprocess.run(
        [str(ilspycmd), str(core_dll), "-o", str(output_file)],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None

    # ilspycmd creates a directory with the same name, containing the .cs file
    actual_file = output_file / "Core.decompiled.cs"
    if actual_file.exists():
        print(f"Decompiled to {actual_file}")
        return actual_file
    elif output_file.is_file():
        print(f"Decompiled to {output_file}")
        return output_file
    else:
        print(f"Error: Could not find decompiled file")
        return None


def find_window_class(code: str) -> Dict[str, str]:
    """Find the Window class and its output field type

    Args:
        code: Decompiled C# source code

    Returns:
        Dictionary with window_class, window_namespace, and output_class
    """
    offsets = {}

    # Look for hackmud.Window class specifically
    # Pattern: namespace hackmud { ... public class Window : MonoBehaviour ... }
    window_match = re.search(
        r'namespace hackmud\s*\{[^}]*?public class Window\s*:\s*MonoBehaviour.*?public TextMeshProUGUI gui_text;.*?public (\w+) output;',
        code, re.DOTALL
    )

    if window_match:
        offsets['window_class'] = 'Window'
        offsets['window_namespace'] = 'hackmud'
        offsets['output_class'] = window_match.group(1)
        print(f"Found Window class: hackmud.Window")
        print(f"Found output type: {offsets['output_class']}")
    else:
        # Alternative: Find any class with gui_text field
        gui_text_match = re.search(
            r'public class (\w+)\s*:\s*MonoBehaviour.*?public TextMeshProUGUI gui_text;.*?public (\w+) output;',
            code, re.DOTALL
        )
        if gui_text_match:
            offsets['window_class'] = gui_text_match.group(1)
            offsets['output_class'] = gui_text_match.group(2)
            print(f"Found Window class: {offsets['window_class']}")
            print(f"Found output type: {offsets['output_class']}")

    return offsets


def find_queue_class(code: str, output_class: str) -> Dict[str, str]:
    """Find the Queue<string> field in the output class

    Args:
        code: Decompiled C# source code
        output_class: Name of the output class to search in

    Returns:
        Dictionary with queue_field
    """
    offsets = {}

    # Find the output class definition
    pattern = rf'public class {output_class}\s*\{{.*?public Queue<string> (\w+)\s*='
    match = re.search(pattern, code, re.DOTALL)

    if match:
        offsets['queue_field'] = match.group(1)
        print(f"Found Queue<string> field: {offsets['queue_field']}")

    return offsets


def generate_offsets(core_dll: Path, output_dir: Optional[Path] = None) -> Dict[str, any]:
    """Generate offset information from Core.dll

    Args:
        core_dll: Path to Core.dll
        output_dir: Output directory for decompilation (optional)

    Returns:
        Dictionary with class names and offset information

    Raises:
        RuntimeError: If decompilation fails or class names not found
    """
    # Decompile
    output_file = decompile_dll(core_dll, output_dir)
    if not output_file or not output_file.exists():
        raise RuntimeError("Decompilation failed")

    # Read decompiled code
    code = output_file.read_text()

    # Find class names
    class_info = {}
    class_info.update(find_window_class(code))

    if 'output_class' not in class_info:
        raise RuntimeError("Could not find Window class in decompiled code")

    class_info.update(find_queue_class(code, class_info['output_class']))

    if 'queue_field' not in class_info:
        raise RuntimeError("Could not find Queue<string> field in output class")

    return class_info


def save_offsets(class_info: Dict[str, str], offsets_file: Path) -> None:
    """Save offset information to mono_offsets.json

    Args:
        class_info: Dictionary with class names
        offsets_file: Path to mono_offsets.json
    """
    # Read existing offsets to preserve version/metadata
    if offsets_file.exists():
        with open(offsets_file, 'r') as f:
            offsets = json.load(f)
    else:
        offsets = {}

    # Update class names only
    offsets['class_names'] = {
        'window_class': class_info.get('window_class'),
        'window_namespace': class_info.get('window_namespace'),
        'output_class': class_info.get('output_class'),
        'queue_field': class_info.get('queue_field'),
        'kernel_class': offsets.get('class_names', {}).get('kernel_class', 'Kernel'),
        'tmp_class': offsets.get('class_names', {}).get('tmp_class', 'TextMeshProUGUI'),
        'tmp_namespace': offsets.get('class_names', {}).get('tmp_namespace', 'TMPro'),
        'hardline_class': offsets.get('class_names', {}).get('hardline_class', 'HardlineCoordinator'),
        'hardline_ip_field': offsets.get('class_names', {}).get('hardline_ip_field')
    }

    # Save offsets
    with open(offsets_file, 'w') as f:
        json.dump(offsets, f, indent=2)

    print(f"Offsets saved to {offsets_file}")


def load_offsets(offsets_file: Path) -> Dict:
    """Load offsets from mono_offsets.json

    Args:
        offsets_file: Path to mono_offsets.json

    Returns:
        Offsets dictionary

    Raises:
        FileNotFoundError: If offsets file doesn't exist
        json.JSONDecodeError: If offsets file is invalid
    """
    with open(offsets_file, 'r') as f:
        return json.load(f)
