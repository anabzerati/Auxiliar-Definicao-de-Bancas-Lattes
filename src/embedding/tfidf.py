import os
import numpy as np
from typing import List, Dict, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from deep_translator import GoogleTranslator
import nltk
from nltk.corpus import stopwords

try:
    nltk.data.find("corpora/stopwords")
except:
    nltk.download("stopwords")

stopwords_pt = stopwords.words("portuguese")


class TFIDFSimilarity:
    """
    TF-IDF based similarity engine to compare a student's (theme + summary)
    against professor profiles.

    The class supports two usage patterns:
    1) Incremental / immediate usage in a loop: if no global corpus was fitted,
       similarity_score will fit the vectorizer on a mini-corpus composed of
       the query (theme+summary) and the professor's texts and compute similarity.
    2) Pre-fit usage: call embed_professors(candidates) to fit the TF-IDF
       vectorizer on a full corpus of all candidates and compute per-section
       embeddings once. After that, similarity_score will use precomputed
       section vectors (faster and consistent).
    """

    DELIM_ITEM = "\n<ITEM_SPLIT>\n"
    DELIM_SECTION = "\n<SECTION_SPLIT>\n"

    def __init__(self, max_features: int = 8000, candidates: Optional[List[Dict]] = None):
        """
        Initialize the engine.

        Parameters
        ----------
        max_features : int
            Maximum number of TF-IDF features.
        candidates : Optional[List[Dict]]
            Optional list of professor dicts. If provided, the vectorizer
            is fitted and section embeddings are precomputed.
        """
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words=stopwords_pt,
            max_features=max_features,
            ngram_range=(1, 2),
        )
        self._fitted = False
        self.prof_sections = None
        if candidates:
            self.prof_sections = self.embed_professors(candidates)

    def translate_block(self, text: str, max_chars: int = 4000) -> str:
        """
        Translate a long text into Portuguese by splitting it into chunks.

        Parameters
        ----------
        text : str
            Text to translate.
        max_chars : int
            Maximum characters per chunk.

        Returns
        -------
        str
            Translated text.
        """
        if not text or not text.strip():
            return ""

        translator = GoogleTranslator(source="auto", target="pt")
        blocks = []
        start = 0
        L = len(text)
        while start < L:
            end = min(start + max_chars, L)
            if end < L:
                while end > start and text[end] != " ":
                    end -= 1
            block = text[start:end].strip()
            blocks.append(block)
            start = end

        translated = []
        for b in blocks:
            try:
                translated.append(translator.translate(b))
            except:
                translated.append(b)
        return " ".join(translated)

    def create_corpus(self, candidates: List[Dict]):
        """
        Build corpus and per-professor section lists from candidates.

        Parameters
        ----------
        candidates : List[Dict]
            List of professor dictionaries containing keys:
            'congress_papers', 'periodic_papers', 'projects', 'research_areas'.

        Returns
        -------
        tuple
            (corpus, congress_list, periodic_list, projects_list, areas_list)
        """
        corpus = []
        congress_list = []
        periodic_list = []
        projects_list = []
        areas_list = []

        for entry in candidates:
            congress = entry.get("congress_papers", [])[:10]
            periodic = entry.get("periodic_papers", [])[:10]

            block_congress = self.DELIM_ITEM.join(congress)
            block_periodic = self.DELIM_ITEM.join(periodic)
            big_block = block_congress + self.DELIM_SECTION + block_periodic
            translated_big = self.translate_block(big_block)
            sections = translated_big.split(self.DELIM_SECTION)

            translated_congress = sections[0].split(self.DELIM_ITEM) if congress else []
            translated_periodic = sections[-1].split(self.DELIM_ITEM) if periodic else []

            congress_list.append(translated_congress)
            periodic_list.append(translated_periodic)

            corpus.extend(translated_congress)
            corpus.extend(translated_periodic)

            projects = entry.get("projects", [])[:10]
            projects_list.append(projects)
            corpus.extend(projects)

            areas = entry.get("research_areas", [])[:10]
            areas_list.append(areas)
            corpus.extend(areas)

        return corpus, congress_list, periodic_list, projects_list, areas_list

    def embed_professors(self, candidates: List[Dict]):
        """
        Fit the TF-IDF vectorizer on a corpus built from candidates and
        compute per-section embeddings (mean TF-IDF vectors) for each professor.

        Parameters
        ----------
        candidates : List[Dict]
            List of professor dictionaries.

        Returns
        -------
        List[Dict]
            One dictionary per professor containing keys:
            'lattes_id', 'name', 'congress_papers', 'periodic_papers',
            'projects', 'research_areas' where section values are np.ndarray or None.
        """
        corpus, congress_list, periodic_list, projects_list, areas_list = self.create_corpus(candidates)
        if not corpus:
            self._fitted = False
            return []

        self.vectorizer.fit(corpus)
        self._fitted = True
        section_vectors = []

        for i, entry in enumerate(candidates):
            vec = {"lattes_id": entry.get("lattes_id"), "name": entry.get("name")}
            def _mean_vec(lst):
                if not lst:
                    return None
                mat = self.vectorizer.transform(lst).toarray()
                return mat.mean(axis=0)

            vec["congress_papers"] = _mean_vec(congress_list[i])
            vec["periodic_papers"] = _mean_vec(periodic_list[i])
            vec["projects"] = _mean_vec(projects_list[i])
            vec["research_areas"] = _mean_vec(areas_list[i])
            section_vectors.append(vec)

        return section_vectors

    def _fit_on_mini_corpus(self, theme: str, summary: str, info: Dict):
        """
        Internal helper to fit the vectorizer on a small corpus composed of
        the query (theme + summary) and professor fields. This enables
        immediate usage inside a loop without pre-fitting.
        """
        fields = []
        fields.extend(info.get("research_areas", []))
        fields.extend(info.get("periodic_papers", []))
        fields.extend(info.get("congress_papers", []))
        fields.extend(info.get("projects", []))
        query_text = (theme or "") + " " + (summary or "")
        corpus = [query_text, " ".join(fields) if fields else ""]
        self.vectorizer.fit(corpus)
        self._fitted = True
        return corpus

    def embed_student(self, theme: str, summary: str, method: str = "mean"):
        """
        Compute TF-IDF embedding for a student's theme + summary using the
        currently fitted vectorizer.

        Parameters
        ----------
        theme : str
        summary : str
        method : str
            'mean' or 'concatenate'

        Returns
        -------
        np.ndarray
        """
        theme_pt = self.translate_block(theme) if theme else ""
        summary_pt = self.translate_block(summary) if summary else ""
        if method == "mean":
            arr = self.vectorizer.transform([theme_pt, summary_pt]).toarray()
            return arr.mean(axis=0)
        if method == "concatenate":
            text = theme_pt + " " + summary_pt
            return self.vectorizer.transform([text]).toarray()[0]
        raise ValueError("method must be 'mean' or 'concatenate'")

    def similarity_score(self, theme: str, summary: str, info: Dict) -> float:
        """
        Compute similarity between a student's work and a professor profile.

        The method accepts either:
        - info as the raw professor dict (with textual lists), or
        - info as a precomputed section-vector dict produced by embed_professors().

        Parameters
        ----------
        theme : str
        summary : str
        info : Dict

        Returns
        -------
        float
            Mean cosine similarity across available sections (0.0 - 1.0).
        """
        if not self._fitted:
            _ = self._fit_on_mini_corpus(theme, summary, info)

        student_vec = self.embed_student(theme, summary)

        # If info contains precomputed numpy vectors (from embed_professors)
        if all(k in info and (info[k] is None or isinstance(info[k], np.ndarray)) for k in ["congress_papers", "periodic_papers", "projects", "research_areas"]):
            section_vals = [info.get("congress_papers"), info.get("periodic_papers"), info.get("projects"), info.get("research_areas")]
        else:
            fields = []
            fields.extend(info.get("research_areas", []))
            fields.extend(info.get("periodic_papers", []))
            fields.extend(info.get("congress_papers", []))
            fields.extend(info.get("projects", []))
            if not fields:
                return 0.0
            professor_text = " ".join(fields)
            prof_vec = self.vectorizer.transform([professor_text]).toarray()[0]
            section_vals = [prof_vec]

        scores = []
        for vec in section_vals:
            if vec is None:
                continue
            sim = cosine_similarity([student_vec], [vec])[0][0]
            scores.append(float(sim))

        return float(np.mean(scores)) if scores else 0.0

 