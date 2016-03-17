import os

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
PACKAGE_DIR = os.path.normpath(os.path.join(THIS_DIR, '../../..'))
MODEL_DIR = os.path.normpath(os.path.join(PACKAGE_DIR, 'model'))
DATA_DIR = os.path.normpath(os.path.join(PACKAGE_DIR, 'data'))
