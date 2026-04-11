class DeepFaceMock:
    @staticmethod
    def analyze(img_path, actions=['emotion'], enforce_detection=False):
        print(f"DeepFace Mock: Skipping behavioral analysis for {img_path}")
        return {
            'dominant_emotion': 'neutral',
            'emotion': {'neutral': 100.0}
        }

DeepFace = DeepFaceMock()
