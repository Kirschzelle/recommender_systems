import os, json, re
import nltk
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from gensim import corpora, models
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from tqdm import tqdm
from annoy import AnnoyIndex
from recommender.models import Movie, MoviePlotRecommendation


def setup_nltk():
    """Download required NLTK data packages."""
    nltk.download("wordnet")
    nltk.download("omw-1.4")
    nltk.download("stopwords")
    nltk.download("averaged_perceptron_tagger")

def clean_text(text: str, stop_words: set) -> str:
    """Clean text by removing punctuation, numbers, and stop words."""
    text = re.sub(r"[^\w\s]", " ", text.lower())
    text = re.sub(r"\d+", "", text)
    tokens = [w for w in text.split() if w not in stop_words and len(w) > 2]
    return " ".join(tokens)

def get_pos(w):
    """Get part-of-speech tag for a word."""
    tag = nltk.pos_tag([w])[0][1][0].upper()
    return {
      "J": wordnet.ADJ,
      "V": wordnet.VERB,
      "N": wordnet.NOUN,
      "R": wordnet.ADV
    }.get(tag, wordnet.NOUN)

def lemma_pos(txt: str, lemmatizer: WordNetLemmatizer) -> str:
    """Lemmatize text using part-of-speech aware lemmatization."""
    return " ".join(lemmatizer.lemmatize(w, get_pos(w)) for w in txt.split())


def load_movies(data_dir: str):
    raw_texts, titles, movie_ids = [], [], []
    files = [f for f in os.listdir(data_dir) if f.endswith(".json")]
    
    print(f"Loading {len(files)} movie files...")
    for fn in tqdm(files, desc="Loading movies"):
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

def preprocess(raw_texts, titles, movie_ids, stop_words: set, lemmatizer: WordNetLemmatizer, drop_pct=2):
    # clean + lemmatize
    print("Preprocessing text data...")
    cleaned = []
    for txt in tqdm(raw_texts, desc="Cleaning and lemmatizing"):
        cleaned.append(lemma_pos(clean_text(txt, stop_words), lemmatizer))
    
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
    print("Building corpus...")
    texts = [doc.split() for doc in docs]
    dct   = corpora.Dictionary(texts)
    dct.filter_extremes(no_below=no_below, no_above=no_above, keep_n=keep_n)
    corpus = [dct.doc2bow(t) for t in tqdm(texts, desc="Creating document-term matrix")]
    return dct, corpus

def train_lda(corpus, id2word, num_topics=50, passes=10):
    print(f"Training LDA model with {num_topics} topics...")
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
    print("Vectorizing documents...")
    all_topics = lda_model.get_document_topics(corpus, minimum_probability=0.0)
    mat = np.zeros((num_docs, num_topics))
    for i, doc_topics in enumerate(tqdm(all_topics, desc="Creating document vectors")):
        for tid, prob in doc_topics:
            mat[i, tid] = prob
    return mat

def build_similarity(lda_vectors):
    print("Computing similarity matrix...")
    sim = cosine_similarity(lda_vectors, lda_vectors)
    return sim

def get_plot_based_recommendation(movie_id: int, recommendation_amount: int):
    """
    Returns the top‐N movie IDs by LDA‐plot similarity, as stored in the database.
    """
    try:
        movie = Movie.objects.get(movie_id=movie_id)
        plot_rec = MoviePlotRecommendation.objects.get(movie=movie)
        return plot_rec.recommended_movies[:recommendation_amount]
    except (Movie.DoesNotExist, MoviePlotRecommendation.DoesNotExist):
        return []

# --- The following class is for offline precomputation only (management command use) ---
class LdaData:
    def __init__(self, data_dir, num_topics=50, passes=10):
        print("Initializing LDA-based recommendation system for offline computation...")
        setup_nltk()
        self.stop_words = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()
        raw_texts, self.titles, self.movie_ids = load_movies(data_dir)
        docs, self.titles, self.movie_ids = preprocess(
            raw_texts, self.titles, self.movie_ids, self.stop_words, self.lemmatizer
        )
        self.dictionary, corpus = build_corpus(docs)
        self.lda_model = train_lda(corpus, self.dictionary, num_topics=num_topics, passes=passes)
        lda_vecs = vectorize_docs(self.lda_model, corpus, len(self.titles), self.lda_model.num_topics)
        self.annoy_index = AnnoyIndex(lda_vecs.shape[1], 'angular')
        for i, vec in enumerate(lda_vecs):
            self.annoy_index.add_item(i, vec)
        self.annoy_index.build(50)
        self.movie_id_to_index = {mid: idx for idx, mid in enumerate(self.movie_ids)}
        print("LDA-based recommendation system ready for offline computation!")

    def get_recommendations(self, movie_id, top_k):
        if movie_id not in self.movie_id_to_index:
            return []
        idx = self.movie_id_to_index[movie_id]
        # Get top_k+1 because the first result is the movie itself
        top_indices = self.annoy_index.get_nns_by_item(idx, top_k + 1)[1:top_k+1]
        return [self.movie_ids[i] for i in top_indices]

