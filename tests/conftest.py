import sys
import os

# Make controller_overlay package importable from src/
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
