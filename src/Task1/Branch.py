import fileinput
from typing import List, Tuple
import csv
from io import StringIO

class Branch(List[Tuple[str, str]]):
    def __init__(self, filePath: str):
        super().__init__()

        for lines in fileinput.input(filePath):
            address, taken = lines.strip().split()
            self.append((address, taken))