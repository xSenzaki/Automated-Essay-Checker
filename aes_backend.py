import spacy
import language_tool_python
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class AESBackend:
    def __init__(self):
        # Load the English language model for tokenization
        self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize the LanguageTool for grammar and spell checking
        self.tool = language_tool_python.LanguageTool('en-US')

    def lemmatize_sentence(self, sentence):
        # Tokenize the sentence and lemmatize each token
        doc = self.nlp(sentence.lower())
        return " ".join([token.lemma_ for token in doc if not token.is_punct and not token.is_stop])

    def jaccard_similarity(self, sentence1, sentence2):
        # Lemmatize each sentence and calculate the Jaccard similarity
        lem_sentence1 = self.lemmatize_sentence(sentence1)
        lem_sentence2 = self.lemmatize_sentence(sentence2)
        
        # Use bigrams for the Jaccard similarit
        vectorizer = CountVectorizer(ngram_range=(1, 2), binary=True) #using bigrams 
        vectors = vectorizer.fit_transform([lem_sentence1, lem_sentence2])
        vectors = vectors.toarray()
        
        # Calculate the intersection and union of the vectors
        intersection = np.sum(np.minimum(vectors[0], vectors[1]))
        union = np.sum(np.maximum(vectors[0], vectors[1]))
        similarity = intersection / union if union != 0 else 0
        return similarity

    def cosine_sim_sections(self, sentence1, sentence2):
        # Split the sentences into sections and calculate the cosine similarity
        sections1 = [sec.strip() for sec in sentence1.split('.') if sec.strip()]
        sections2 = [sec.strip() for sec in sentence2.split('.') if sec.strip()]
        
        # Calculate the minimum number of sections
        min_len = min(len(sections1), len(sections2))
        similarities = []
        
        for i in range(min_len):
            # Lemmatize each section and calculate the cosine similarity
            lem_sec1 = self.lemmatize_sentence(sections1[i])
            lem_sec2 = self.lemmatize_sentence(sections2[i])
            vectorizer = TfidfVectorizer()
            try:
                # Calculate the TF-IDF vectors
                vectors = vectorizer.fit_transform([lem_sec1, lem_sec2])
                similarity_matrix = cosine_similarity(vectors)
                similarities.append(similarity_matrix[0, 1])
            except ValueError:
                # Skip sections that result in empty vocabulary
                continue
        
        # Calculate the average similarity
        return np.mean(similarities) if similarities else 0

    def evaluate_content(self, reference, essay):
        # Calculate the Jaccard similarity for content evaluation
        similarity = self.jaccard_similarity(reference, essay)
        similarity = round(similarity * 100)

        if similarity < 5:
            print(similarity)
            return 0
        else:
            print(similarity)
            return min(similarity * 8, 25)

    def evaluate_organization(self, reference, essay):
        # Calculate the cosine similarity for organization evaluation
        similarity = self.cosine_sim_sections(reference, essay)
        similarity = round(similarity * 100)

        if similarity < 5:
            print(similarity)
            return 0
        else:
            print(similarity)
            return min(similarity * 3, 10)

    def evaluate_grammar_mechanics(self, essay):
        # Check the essay for grammar and spelling errors
        doc = self.nlp(essay)
        total_tokens = len(doc)

        # Count the number of errors found by LanguageTool
        matches = self.tool.check(essay)
        lt_errors = len(matches)

        # Total errors found by LanguageTool
        total_errors = lt_errors

        # Calculate the score based on the number of errors
        score = (total_tokens - total_errors) / total_tokens if total_tokens > 0 else 0
        return score * 10  

    def evaluate_word_choice(self, essay):
        # Calculate the word choice score
        doc = self.nlp(essay)
        unique_tokens = len(set(token.text for token in doc if token.is_alpha))
        total_tokens = len(doc)
        score = unique_tokens / total_tokens if total_tokens > 0 else 0
        return score * 5  

    def grade_essay(self, reference, essay):
        # Evaluate the essay based on content, organization, grammar, and word choice
        content_score = round(self.evaluate_content(reference, essay))
        organization_score = round(self.evaluate_organization(reference, essay))
        grammar_mechanics_score = round(self.evaluate_grammar_mechanics(essay))
        word_choice_score = round(self.evaluate_word_choice(essay))
        
        # Print the scores
        print(f"Content Score: {content_score} / 25")
        print(f"Organization Score: {organization_score} / 10")
        print(f"Grammar/Mechanics Score: {grammar_mechanics_score} / 10")
        print(f"Word Choice Score: {word_choice_score} / 5")

        # Calculate the total score
        total_score = (content_score + organization_score + grammar_mechanics_score + word_choice_score)
        print(f"Total Score: {total_score} /50")
        return total_score