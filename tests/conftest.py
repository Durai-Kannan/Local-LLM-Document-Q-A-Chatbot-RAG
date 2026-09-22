import sys
import os

# Add root directory to sys.path so 'app' module can be imported in tests
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
