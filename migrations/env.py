import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gapfinder import app
from models import db
target_metadata = db.metadata
