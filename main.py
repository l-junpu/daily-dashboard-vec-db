import os
from src.api import ApiHandler


if __name__ == "__main__":
    handler = ApiHandler(name=__name__, rootDir=os.path.dirname(__file__))
    handler.run()