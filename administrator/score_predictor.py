from sentence_transformers import SentenceTransformer, util

class SimilarityScorer:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def score(self, sent1: str, sent2: str) -> float:
        """
        Compare two answers and return a similarity score (0 to 100).

        :param sent1: First sentence (original/reference)
        :param sent2: Second sentence (submitted/user answer)
        :return: Similarity score as a float (0 to 100)
        """
        embedding1 = self.model.encode(sent1, convert_to_tensor=True)
        embedding2 = self.model.encode(sent2, convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(embedding1, embedding2).item()
        return round(similarity * 100, 2)
