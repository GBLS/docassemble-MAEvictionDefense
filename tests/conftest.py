"""
Pytest configuration for MAEvictionDefense tests.

Handles Python path manipulation to allow importing pip-installed
docassemble packages without conflicts from the local workspace namespace.
"""

import sys
import os

# Remove workspace docassemble directory from path to avoid
# conflicts with the namespace package declaration
def pytest_configure(config):
    """Called after command line options have been parsed."""
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docassemble_local = os.path.join(workspace_root, 'docassemble')
    
    # Store paths to remove
    paths_to_remove = []
    for p in sys.path:
        # Remove workspace root and docassemble subdirectory
        if workspace_root in p or p == '.':
            paths_to_remove.append(p)
    
    for p in paths_to_remove:
        if p in sys.path:
            sys.path.remove(p)
