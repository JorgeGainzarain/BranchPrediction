from src.models.Predictor import Predictor

class OneBitPredictor(Predictor):
    def __init__(self, size):
        super().__init__(size)

    def predict(self, address):
        return self.history.get(address, None)  # Default prediction is 'T' (Taken)

    def update(self, address, outcome):
        if address in self.history:
            del self.history[address]  # Remove to update its position (LRU)
        elif len(self.history) >= self.MAX_HISTORY_SIZE:
            self.history.popitem(last=False)  # Remove least recently used item

        self.history[address] = outcome  # Add/Update the prediction