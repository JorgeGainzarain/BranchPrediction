from src.models.Predictor import Predictor

class TwoBitPredictor(Predictor):
    def __init__(self, size):
        super().__init__(size)

    def predict(self, address):
        state = self.history.get(address, None)

        if state is None: return state
        else: return 'T' if state >= 2 else 'N'

    def update(self, address, outcome):
        if address in self.history:
            state = self.history[address]
            del self.history[address]  # Remove to update its position (LRU)
        elif len(self.history) >= self.MAX_HISTORY_SIZE:
            self.history.popitem(last=False)  # Remove least recently used item
            state = 0  # New state for new address
        else:
            state = 0  # New state for new address

        if outcome == 'T':
            state = min(3, state + 1)  # Increment state, max is 3 (Strongly Taken)
        else:
            state = max(0, state - 1)  # Decrement state, min is 0 (Strongly Not Taken)

        self.history[address] = state  # Add/Update the prediction state