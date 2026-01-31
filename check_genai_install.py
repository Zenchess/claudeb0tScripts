
import importlib.util
import sys

# Check if the module is available
spec = importlib.util.find_spec("google.generativeai")
if spec is None:
    print("google.generativeai is not installed.")
    print("Please install it using: pip install google-generativeai")
    sys.exit(1)
else:
    print("google.generativeai is installed.")
