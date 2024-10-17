from typing import List, Tuple


class Branch(List[Tuple[str, str]]):

    def __init__(self, filePath: str):
        super().__init__()
        with open(filePath, 'r') as file:
            for line in file:
                address, taken = line.strip().split()
                self.append((address, taken))
