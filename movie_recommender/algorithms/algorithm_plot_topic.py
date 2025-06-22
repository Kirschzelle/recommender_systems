import os, json, re
import nltk
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from gensim import corpora, models
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer

def setup_nltk():
    nltk.download("wordnet")
    nltk.download("omw-1.4")
    nltk.download("stopwords")
    nltk.download("averaged_perceptron_tagger")
    global STOP_WORDS, LEMMATIZER
    STOP_WORDS = set(stopwords.words("english"))
    LEMMATIZER = WordNetLemmatizer()

def clean_text(text: str) -> str:
    text = re.sub(r"[^\w\s]", " ", text.lower())
    text = re.sub(r"\d+", "", text)
    tokens = [w for w in text.split() if w not in STOP_WORDS and len(w) > 2]
    return " ".join(tokens)

def get_pos(w):
    tag = nltk.pos_tag([w])[0][1][0].upper()
    return {
      "J": wordnet.ADJ,
      "V": wordnet.VERB,
      "N": wordnet.NOUN,
      "R": wordnet.ADV
    }.get(tag, wordnet.NOUN)

def lemma_pos(txt):
    return " ".join(LEMMATIZER.lemmatize(w, get_pos(w)) for w in txt.split())


def load_movies(data_dir: str):
    raw_texts, titles, movie_ids = [], [], []
    for fn in os.listdir(data_dir):
        if not fn.endswith(".json"):
            continue
        path = os.path.join(data_dir, fn)
        try:
            m = json.load(open(path, "r"))
            md   = m.get("movielens", {})
            title = md.get("title", "").strip()
            plot  = md.get("plotSummary", "").strip()
            mid   = md.get("movieId")
            if title and plot and mid is not None:
                raw_texts.append(f"{title.lower()} {plot}")
                titles.append(title)
                movie_ids.append(mid)
        except Exception:
            # skip malformed
            continue
    return raw_texts, titles, movie_ids

def preprocess(raw_texts, titles, movie_ids, drop_pct=2):
    # clean + lemmatize
    cleaned = [lemma_pos(clean_text(txt)) for txt in raw_texts]
    lengths = sorted(len(doc.split()) for doc in cleaned)
    min_len = int(np.percentile(lengths, drop_pct))
    out_docs, out_titles, out_ids = [], [], []
    for doc, t, mid in zip(cleaned, titles, movie_ids):
        if len(doc.split()) >= min_len:
            out_docs.append(doc)
            out_titles.append(t)
            out_ids.append(mid)
    return out_docs, out_titles, out_ids


def build_corpus(docs, no_below=20, no_above=0.8, keep_n=5000):
    texts = [doc.split() for doc in docs]
    dct   = corpora.Dictionary(texts)
    dct.filter_extremes(no_below=no_below, no_above=no_above, keep_n=keep_n)
    corpus = [dct.doc2bow(t) for t in texts]
    return dct, corpus

def train_lda(corpus, id2word, num_topics=50, passes=10):
    lda = models.LdaModel(
        corpus=corpus,
        id2word=id2word,
        num_topics=num_topics,
        random_state=100,
        update_every=1,
        chunksize=100,
        passes=passes,
        alpha="auto",
        eta="auto"
    )
    return lda

def vectorize_docs(lda_model, corpus, num_docs, num_topics):
    all_topics = lda_model.get_document_topics(corpus, minimum_probability=0.0)
    mat = np.zeros((num_docs, num_topics))
    for i, doc_topics in enumerate(all_topics):
        for tid, prob in doc_topics:
            mat[i, tid] = prob
    return mat

def build_similarity(lda_vectors):
    sim = cosine_similarity(lda_vectors, lda_vectors)
    return sim

class LdaData:
    _instance = None

    def __new__(cls, data_dir):
        if cls._instance is None:
            # first‐time only: build everything
            cls._instance = super().__new__(cls)
            cls._instance._init(data_dir)
        return cls._instance

    def _init(self, data_dir):
        setup_nltk()
        raw_texts, self.titles, self.movie_ids = load_movies(data_dir)
        docs, self.titles, self.movie_ids = preprocess(raw_texts, self.titles, self.movie_ids)
        self.dictionary, corpus = build_corpus(docs)
        self.lda_model = train_lda(corpus, self.dictionary)
        lda_vecs = vectorize_docs(self.lda_model, corpus, len(self.titles), self.lda_model.num_topics)
        self.similarity_matrix = build_similarity(lda_vecs)


this_dir = os.path.dirname(__file__)
data_dir = os.path.abspath(os.path.join(this_dir, "..", "datasets", "information"))
_lda_data = LdaData(data_dir)


def get_plot_based_recommendation(movie_id: int, recommendation_amount: int):
    """
    Returns the top‐N movie IDs by LDA‐plot similarity.
    """
    sims = _lda_data.similarity_matrix
    ids  = _lda_data.movie_ids

    idx = ids.index(movie_id)
    row = sims[idx].copy()
    row[idx] = -1.0
    top = np.argsort(row)[-recommendation_amount:][::-1]
    return [ids[i] for i in top]

