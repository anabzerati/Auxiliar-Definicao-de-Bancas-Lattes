from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np


class SentenceTransformerSimilarity:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def similarity_score(self, theme: str, summary: str, info: dict) -> float:
        theme_embedding = self._calculate_embedding_theme(theme, summary)

        scores = []

        area_similarity = self._similarity_with_areas(theme_embedding, info.get("research_areas", []))
        if area_similarity is not None:
            scores.append(area_similarity)

        periodic_similarity = self._similarity_with_periodic_papers(theme_embedding, info.get("periodic_papers", []))
        if periodic_similarity is not None:
            scores.append(periodic_similarity)

        congress_similarity = self._similarity_with_congress_papers(theme_embedding, info.get("congress_papers", []))
        if congress_similarity is not None:
            scores.append(congress_similarity)

        projects_similarity = self._similarity_with_projects(theme_embedding, info.get("projects", []))
        if projects_similarity is not None:
            scores.append(projects_similarity)

        return float(np.mean(scores)) if scores else 0.0

    def _calculate_embedding_theme(self, theme_text: str, summary_text: str) -> np.ndarray:
        theme_embedding = self.model.encode(theme_text)
        summary_embedding = self.model.encode(summary_text)
        return np.mean([theme_embedding, summary_embedding], axis=0)

    def _similarity_with_areas(self, theme_embedding: np.ndarray, research_areas: List[str]) -> float | None:
        if not research_areas:
            return None
        area_embeddings = np.mean([self.model.encode(area) for area in research_areas], axis=0)
        return self.model.similarity(theme_embedding, area_embeddings)

    def _similarity_with_periodic_papers(self, theme_embedding: np.ndarray, periodic_papers: List[str]) -> float | None:
        if not periodic_papers:
            return None
        periodic_embeddings = np.mean([self.model.encode(paper) for paper in periodic_papers], axis=0)
        return self.model.similarity(theme_embedding, periodic_embeddings)

    def _similarity_with_congress_papers(self, theme_embedding: np.ndarray, congress_papers: List[str]) -> float | None:
        if not congress_papers:
            return None
        congress_embeddings = np.mean([self.model.encode(paper) for paper in congress_papers], axis=0)
        return self.model.similarity(theme_embedding, congress_embeddings)

    def _similarity_with_projects(self, theme_embedding: np.ndarray, project_list: List[str]) -> float | None:
        if not project_list:
            return None
        projects_embeddings = np.mean([self.model.encode(project) for project in project_list], axis=0)
        return self.model.similarity(theme_embedding, projects_embeddings)
