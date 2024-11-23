import os
import sys

# Add the ml mopdule to the path so that we can use relative
# dot syntax for django compatibility
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use an absolute import since we have loaded the module
from ml.train import train

if __name__ == "__main__":
    train()
