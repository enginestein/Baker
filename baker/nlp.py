import re
import math
import time
from collections import Counter


STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'up', 'about', 'into', 'over', 'after',
    'is', 'am', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
    'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
    'might', 'shall', 'can', 'need', 'it', 'its',
    'i', 'me', 'my', 'myself', 'we', 'us', 'our', 'ours', 'ourselves',
    'you', 'your', 'yours', 'yourself', 'yourselves',
    'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
    'they', 'them', 'their', 'theirs', 'themselves',
    'this', 'that', 'these', 'those', 'some', 'any', 'no', 'every',
    'all', 'each', 'few', 'more', 'most', 'other', 'such',
    'what', 'which', 'who', 'whom', 'whose', 'when', 'where', 'why', 'how',
    'not', 'so', 'very', 'just', 'than', 'too', 'also',
    'if', 'then', 'else', 'as', 'until', 'while', 'because',
    'since', 'though', 'although', 'unless', 'except',
    'like', 'well', 'really', 'actually', 'basically',
    'probably', 'maybe', 'perhaps', 'quite', 'rather',
}

CONTRACTIONS = {
    "i'm": "i am", "you're": "you are", "he's": "he is", "she's": "she is",
    "it's": "it is", "we're": "we are", "they're": "they are",
    "i've": "i have", "you've": "you have", "we've": "we have", "they've": "they have",
    "i'll": "i will", "you'll": "you will", "he'll": "he will", "she'll": "she will",
    "we'll": "we will", "they'll": "they will",
    "i'd": "i would", "you'd": "you would", "he'd": "he would",
    "she'd": "she would", "we'd": "we would", "they'd": "they would",
    "don't": "do not", "doesn't": "does not", "didn't": "did not",
    "won't": "will not", "wouldn't": "would not", "couldn't": "could not",
    "shouldn't": "should not", "can't": "cannot", "isn't": "is not",
    "aren't": "are not", "wasn't": "was not", "weren't": "were not",
    "hasn't": "has not", "haven't": "have not", "hadn't": "had not",
    "let's": "let us", "what's": "what is", "who's": "who is",
    "that's": "that is", "there's": "there is", "here's": "here is",
}


class TextProcessor:
    def normalize(self, text):
        text = text.lower().strip()
        for contraction, expanded in CONTRACTIONS.items():
            text = text.replace(contraction, expanded)
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def tokenize(self, text):
        return self.normalize(text).split()

    def remove_stopwords(self, tokens):
        return [t for t in tokens if t not in STOP_WORDS]

    def char_ngrams(self, text, n_min=2, n_max=4):
        normalized = self.normalize(text)
        ngrams = set()
        for n in range(n_min, n_max + 1):
            for i in range(len(normalized) - n + 1):
                ngrams.add(normalized[i:i + n])
        return ngrams


class TfidfVectorizer:
    def __init__(self, use_stopwords=True):
        self.use_stopwords = use_stopwords
        self.processor = TextProcessor()
        self.idf = {}
        self.vocab = set()
        self.doc_count = 0
        self._fitted = False

    def fit(self, documents):
        self.doc_count = len(documents)
        doc_freq = Counter()
        for doc in documents:
            tokens = self._get_tokens(doc)
            for token in set(tokens):
                doc_freq[token] += 1
        self.vocab = set(doc_freq.keys())
        n = self.doc_count
        self.idf = {word: math.log((n + 1) / (freq + 1)) + 1
                    for word, freq in doc_freq.items()}
        self._fitted = True
        return self

    def transform(self, document):
        if not self._fitted:
            raise RuntimeError("fit() must be called before transform()")
        tokens = self._get_tokens(document)
        if not tokens:
            return {}
        tf = Counter(tokens)
        max_tf = max(tf.values())
        vec = {}
        for word in set(tokens):
            if word in self.idf:
                tf_val = 0.5 + 0.5 * (tf[word] / max_tf)
                vec[word] = tf_val * self.idf[word]
        return vec

    def _get_tokens(self, document):
        tokens = self.processor.tokenize(document)
        if self.use_stopwords:
            tokens = self.processor.remove_stopwords(tokens)
        return tokens

    @staticmethod
    def cosine_similarity(vec_a, vec_b):
        if not vec_a or not vec_b:
            return 0.0
        intersection = set(vec_a.keys()) & set(vec_b.keys())
        dot = sum(vec_a[w] * vec_b[w] for w in intersection)
        norm_a = math.sqrt(sum(v * v for v in vec_a.values()))
        norm_b = math.sqrt(sum(v * v for v in vec_b.values()))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


class CharNgramVectorizer:
    def __init__(self, n_min=2, n_max=4):
        self.n_min = n_min
        self.n_max = n_max
        self.processor = TextProcessor()
        self._fitted = False

    def fit(self, documents):
        self.doc_count = len(documents)
        doc_freq = Counter()
        for doc in documents:
            for ngram in self._get_ngrams(doc):
                doc_freq[ngram] += 1
        self.vocab = set(doc_freq.keys())
        n = self.doc_count
        self.idf = {ng: math.log((n + 1) / (freq + 1)) + 1
                    for ng, freq in doc_freq.items()}
        self._fitted = True
        return self

    def transform(self, document):
        if not self._fitted:
            raise RuntimeError("fit() must be called before transform()")
        ngrams = self._get_ngrams(document)
        if not ngrams:
            return {}
        tf = Counter(ngrams)
        max_tf = max(tf.values())
        vec = {}
        for ng in set(ngrams):
            if ng in self.idf:
                tf_val = 0.5 + 0.5 * (tf[ng] / max_tf)
                vec[ng] = tf_val * self.idf[ng]
        return vec

    def _get_ngrams(self, document):
        normalized = self.processor.normalize(document)
        ngrams = set()
        for n in range(self.n_min, self.n_max + 1):
            for i in range(len(normalized) - n + 1):
                ngrams.add(normalized[i:i + n])
        return ngrams

    @staticmethod
    def cosine_similarity(vec_a, vec_b):
        return TfidfVectorizer.cosine_similarity(vec_a, vec_b)


class Matcher:
    def __init__(self, word_weight=0.6, char_weight=0.4, threshold=0.3):
        self.word_weight = word_weight
        self.char_weight = char_weight
        self.threshold = threshold
        self.word_vectorizer = TfidfVectorizer()
        self.char_vectorizer = CharNgramVectorizer()
        self.keys = []
        self._word_vectors = []
        self._char_vectors = []
        self._fitted = False

    def fit(self, keys):
        self.keys = list(keys)
        self.word_vectorizer.fit(self.keys)
        self.char_vectorizer.fit(self.keys)
        self._word_vectors = [self.word_vectorizer.transform(k) for k in self.keys]
        self._char_vectors = [self.char_vectorizer.transform(k) for k in self.keys]
        self._fitted = True
        return self

    def best_match(self, query):
        if not self._fitted or not self.keys:
            return None, 0.0
        word_vec = self.word_vectorizer.transform(query)
        char_vec = self.char_vectorizer.transform(query)
        best_idx = -1
        best_score = 0.0
        for i, key in enumerate(self.keys):
            word_sim = TfidfVectorizer.cosine_similarity(word_vec, self._word_vectors[i])
            char_sim = CharNgramVectorizer.cosine_similarity(char_vec, self._char_vectors[i])
            combined = self.word_weight * word_sim + self.char_weight * char_sim
            if combined > best_score:
                best_score = combined
                best_idx = i
        if best_score >= self.threshold:
            return self.keys[best_idx], round(best_score, 4)
        return None, round(best_score, 4)

    def add_key(self, key):
        self.keys.append(key)
        self._word_vectors.append(self.word_vectorizer.transform(key))
        self._char_vectors.append(self.char_vectorizer.transform(key))

    def remove_key(self, key):
        if key in self.keys:
            idx = self.keys.index(key)
            self.keys.pop(idx)
            self._word_vectors.pop(idx)
            self._char_vectors.pop(idx)

    def refit(self):
        self.fit(self.keys)


class SemanticMatcher:
    def __init__(self, model_name='all-MiniLM-L6-v2', threshold=0.5):
        self.model_name = model_name
        self.threshold = threshold
        self.keys = []
        self._key_vectors = None
        self._model = None
        self._fitted = False

    def fit(self, keys):
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for the 'semantic' backend. "
                "Install it with: pip install sentence-transformers"
            )
        self.keys = list(keys)
        self._model = SentenceTransformer(self.model_name)
        self._key_vectors = self._model.encode(self.keys, convert_to_numpy=True)
        self._fitted = True
        return self

    def best_match(self, query):
        import numpy as np
        if not self._fitted or not self.keys:
            return None, 0.0
        query_vec = self._model.encode([query], convert_to_numpy=True)[0]
        scores = np.dot(self._key_vectors, query_vec) / (
            np.linalg.norm(self._key_vectors, axis=1) * np.linalg.norm(query_vec) + 1e-10
        )
        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])
        if best_score >= self.threshold:
            return self.keys[best_idx], round(best_score, 4)
        return None, round(best_score, 4)

    def add_key(self, key):
        import numpy as np
        self.keys.append(key)
        new_vec = self._model.encode([key], convert_to_numpy=True)
        if self._key_vectors is None:
            self._key_vectors = new_vec
        else:
            self._key_vectors = np.vstack([self._key_vectors, new_vec])

    def remove_key(self, key):
        import numpy as np
        if key in self.keys:
            idx = self.keys.index(key)
            self.keys.pop(idx)
            self._key_vectors = np.delete(self._key_vectors, idx, axis=0)

    def refit(self):
        self.fit(self.keys)


class IntentClassifier:
    _NEGATION = re.compile(r'\b(not|n\'t|never|no|nothing|nowhere|nobody|neither|nor)\b', re.IGNORECASE)

    def __init__(self, threshold=0.3):
        self.threshold = threshold
        self.intents = {}
        self._examples = []
        self._negative_examples = []
        self._vectorizer = TfidfVectorizer()
        self._intent_example_vecs = []
        self._neg_example_vecs = []
        self._fitted = False
        self._neg_fitted = False

    def add_intent(self, name, examples, responses, negative_examples=None):
        self.intents[name] = {
            'examples': list(examples),
            'responses': list(responses),
            'negative_examples': list(negative_examples) if negative_examples else [],
        }
        for ex in examples:
            self._examples.append((ex, name))
        for ex in (negative_examples or []):
            self._negative_examples.append((ex, name))
        self._fitted = False
        self._neg_fitted = False

    def remove_intent(self, name):
        if name in self.intents:
            del self.intents[name]
            self._examples = [(ex, n) for ex, n in self._examples if n != name]
            self._negative_examples = [(ex, n) for ex, n in self._negative_examples if n != name]
            self._fitted = False
            self._neg_fitted = False

    def fit(self):
        if not self._examples:
            self._fitted = True
            return
        texts = [ex for ex, _ in self._examples]
        self._vectorizer.fit(texts)
        self._intent_example_vecs = [self._vectorizer.transform(ex) for ex, _ in self._examples]
        self._fitted = True

    def _fit_negative(self):
        if not self._negative_examples:
            self._neg_fitted = True
            return
        texts = [ex for ex, _ in self._negative_examples]
        self._neg_example_vecs = [self._vectorizer.transform(ex) for ex, _ in self._negative_examples]
        self._neg_fitted = True

    def _has_negation(self, text):
        return bool(self._NEGATION.search(text))

    def classify(self, text):
        if not self._fitted:
            self.fit()
        if not self._examples:
            return None, 0.0

        if not self._neg_fitted:
            self._fit_negative()

        has_neg = self._has_negation(text)
        vec = self._vectorizer.transform(text)
        best_score = 0.0
        best_intent = None

        for i, (ex_text, intent_name) in enumerate(self._examples):
            sim = TfidfVectorizer.cosine_similarity(vec, self._intent_example_vecs[i])
            if has_neg and not self._has_negation(ex_text):
                sim *= 0.01
            if sim > best_score:
                best_score = sim
                best_intent = intent_name

        if best_intent and best_score >= self.threshold:
            for i, (neg_text, intent_name) in enumerate(self._negative_examples):
                if intent_name == best_intent:
                    neg_sim = TfidfVectorizer.cosine_similarity(vec, self._neg_example_vecs[i])
                    if neg_sim > best_score:
                        return None, round(best_score, 4)

        if best_score >= self.threshold:
            return best_intent, round(best_score, 4)
        return None, round(best_score, 4)

    def intents_list(self):
        return list(self.intents.keys())

    def has_intent(self, name):
        return name in self.intents

    def get_responses(self, intent_name):
        if intent_name in self.intents:
            return self.intents[intent_name]['responses']
        return []


class ResponseSelector:
    def __init__(self, recency_penalty=0.3, diversity_window=5):
        self.recency_penalty = recency_penalty
        self.diversity_window = diversity_window
        self._recent = []

    def select(self, responses, entities=None):
        if not responses:
            return None
        if len(responses) == 1 and not entities:
            return responses[0]
        scored = []
        for r in responses:
            score = 1.0
            recent_count = sum(1 for prev in self._recent[-self.diversity_window:] if prev == r)
            score -= recent_count * self.recency_penalty
            if entities:
                for key, value in entities.items():
                    if isinstance(value, str) and value and value.lower() in r.lower():
                        score += 0.15
                    elif isinstance(value, list):
                        for v in value:
                            if isinstance(v, str) and v.lower() in r.lower():
                                score += 0.1
            if '{' in r and '}' in r:
                score += 0.05
            scored.append((score, r))
        scored.sort(key=lambda x: -x[0])
        best = scored[0][1]
        self._recent.append(best)
        if len(self._recent) > 100:
            self._recent = self._recent[-50:]
        return best

    def reset(self):
        self._recent.clear()


class TemplateEngine:
    def __init__(self):
        self._fallback = re.compile(r'\{(\w+)\}')

    def render(self, template, context=None):
        if not template or '{' not in template:
            return template
        ctx = context or {}

        def replace(match):
            key = match.group(1)
            if key in ctx:
                val = ctx[key]
                if isinstance(val, str):
                    return val
                if isinstance(val, (int, float)):
                    return str(val)
                if isinstance(val, list) and val:
                    return str(val[0])
            return match.group(0)

        return self._fallback.sub(replace, template)


class EntityExtractor:
    def extract(self, text):
        entities = {}
        name = re.search(
            r'(?i:my name is|i am|i\'m|call me|name\'s|i go by)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
            text
        )
        if name:
            entities['name'] = name.group(1)
        age = re.search(r'(?i:i am|i\'m)\s+(\d+)\s*(?i:years old|year old|yrs old)', text)
        if age:
            entities['age'] = age.group(1)
        numbers = re.findall(r'\b\d+\b', text)
        if numbers:
            entities['numbers'] = numbers
        email = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
        if email:
            entities['email'] = email.group(0)
        return entities


class SentimentAnalyzer:
    def __init__(self):
        self.positive = {
            'good', 'great', 'awesome', 'nice', 'happy', 'love', 'wonderful',
            'fantastic', 'excellent', 'amazing', 'best', 'beautiful', 'glad',
            'perfect', 'brilliant', 'super', 'fun', 'delightful', 'joy', 'lovely',
            'cool', 'excited', 'grateful', 'welcome', 'fantastic',
        }
        self.negative = {
            'bad', 'terrible', 'awful', 'hate', 'horrible', 'sad', 'angry',
            'worst', 'ugly', 'poor', 'lousy', 'depressed', 'miserable',
            'dreadful', 'annoying', 'stupid', 'cry', 'pain', 'hurt',
            'boring', 'disappointed', 'upset', 'frustrated',
        }

    def analyze(self, text):
        processor = TextProcessor()
        tokens = set(processor.tokenize(text))
        pos_count = len(tokens & self.positive)
        neg_count = len(tokens & self.negative)
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'
