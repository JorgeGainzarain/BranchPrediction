from typing import OrderedDict


class History(OrderedDict[str,str]):
    maxSize: int

    def __init__(self, maxSize: int):
        super().__init__()
        self.maxSize = maxSize


    def set(self, address: str, outcome: str):
        if len(self) >= self.maxSize:
            self.popitem(last=False)
        self[address] = outcome

    def get(self, address: str) -> str:
        if address in self:
            return self[address]
        else:
            return 'N'