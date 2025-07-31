#!/usr/bin/env python3
"""
EPUB Editor Launcher
A simple launcher script for the EPUB Editor application.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from epub_editor import main
    main()
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure you have installed all required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"Error starting EPUB Editor: {e}")
    sys.exit(1) 