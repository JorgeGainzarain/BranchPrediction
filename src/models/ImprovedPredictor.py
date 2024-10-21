from src.models.Predictor import Predictor

class ImprovedPredictor(Predictor):

    taken_branches = 0
    not_taken_branches = 0

    def __init__(self, size):
        super().__init__(size)

    def predict(self, address):
        if address in self.history:
            return self.history[address][0] # Return the current prediction
        else:
            return None # No prediction available for this address yet

    def update(self, address, outcome):
        self.taken_branches += 1 if outcome == 'T' else 0
        self.not_taken_branches += 1 if outcome == 'N' else 0
        self.default_prediction_state = 'T' if self.taken_branches > self.not_taken_branches else 'N'

        # Update total_since_added for all entries
        for key in self.history:
            self.history[key] = (*self.history[key][:3], self.history[key][3] + 1)

        if address in self.history:
            prediction, accuracy, total_appearances, total_since_added = self.history[address]

            correct_predictions = accuracy * total_appearances

            total_appearances += 1
            correct_predictions += 1 if outcome == prediction else 0

            accuracy = correct_predictions / total_appearances

            if prediction != outcome and accuracy < 0.5:
                prediction = outcome

            self.history[address] = (prediction, accuracy, total_appearances, total_since_added)
        else:
            if len(self.history) >= self.MAX_HISTORY_SIZE:
                least_used_key = min(self.history, key=lambda k: self.history[k][1]/self.history[k][2])
                del self.history[least_used_key]

            self.history[address] = (outcome, 1, 1, 1)
