from collections import OrderedDict
from typing import Tuple


class History(OrderedDict[str,Tuple[str,int,int]]):


    def __init__(self, maxSize: int):
        super().__init__()
        self.maxSize = maxSize

    def __setitem__(self, address: str, value: tuple[str,int,int]):

        if address in self:
            # Move the existing item to the end (most recently used)
            self.move_to_end(address)
        elif len(self) >= self.maxSize:
            # Remove the least recently used item
            lessAccuracy = self.find_least_accurate()
            self.pop(lessAccuracy[0])

        # Add or update the item
        super().__setitem__(address, value)

    def __getitem__(self, address: str):
        return super().__getitem__(address)

    def get(self, address: str, default='') -> str:
        try:
            return self[address][0]
        except KeyError:
            return default

    def set(self, address: str, prediction: str, outcome: str):


        lastValue = ''
        if address in self:
            lastValue, predicted, total = self[address]
        else:
            predicted, total = 0, 0

        predicted += 1 if prediction == outcome else 0
        total += 1

        if predicted / total > 0.5:
            value = lastValue if lastValue != '' else outcome
        else :
            # If we are changing the value we invert the accuracy
            value = outcome
            predicted = total - predicted

        value = lastValue if lastValue != '' and predicted / total > 0.5 else outcome

        currSize = len(self)

        self[address] = value, predicted, total

        return currSize == self.maxSize, lastValue != '' and predicted / total > 0.5

    def find_least_accurate(self):
        if not self:
            return None  # Return None if the dictionary is empty

        return min(self.items(), key=lambda item: item[1][1] / item[1][2] if item[1][2] > 0 else float('inf'))