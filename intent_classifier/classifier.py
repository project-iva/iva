class IntentClassifier:
    def classify(self, utterance: str) -> dict:
        return {
            'INTRODUCTION': 0.7,
            'GET_TIME': 0.2,
            'SAY': 0.1
        }
