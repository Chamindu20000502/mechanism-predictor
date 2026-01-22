import os
import sys

def get_app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def model_path(filename):
    return os.path.join(get_app_dir(), "models", filename)
