from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np

class SentenceTransformerSimilarity:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def similarity_score(self, theme: str, summary: str, info: dict) -> float:
        theme_embedding = self._calculate_embedding_theme(theme, summary)

        area_embedding = self._calculate_embedding_area(info.get("research_areas", []))
        periodic_embedding = self._calculate_embedding_periodic(info.get("periodic_papers", []))
        congress_embedding = self._calculate_embedding_congress(info.get("congress_papers", []))
        projects_embedding = self._calculate_embedding_project(info.get("projects", []))

        section_embeddings = [
            e for e in [
                area_embedding,
                periodic_embedding,
                congress_embedding,
                projects_embedding,
            ] if e is not None
        ]

        if not section_embeddings:
            return None  

        # average embeddings from sections
        prof_embedding = np.mean(section_embeddings, axis=0)

        return float(self.model.similarity(theme_embedding, prof_embedding))

        # scores = []

        # area_similarity = self._similarity_with_areas(theme_embedding, info.get("research_areas", []))
        # if area_similarity is not None:
        #     scores.append(area_similarity)

        # periodic_similarity = self._similarity_with_periodic_papers(theme_embedding, info.get("periodic_papers", []))
        # if periodic_similarity is not None:
        #     scores.append(periodic_similarity)

        # congress_similarity = self._similarity_with_congress_papers(theme_embedding, info.get("congress_papers", []))
        # if congress_similarity is not None:
        #     scores.append(congress_similarity)

        # projects_similarity = self._similarity_with_projects(theme_embedding, info.get("projects", []))
        # if projects_similarity is not None:
        #     scores.append(projects_similarity)

        # return float(np.mean(scores)) if scores else 0.0

    def _calculate_embedding_theme(self, theme_text: str, summary_text: str) -> np.ndarray:
        theme_embedding = self.model.encode(theme_text)
        summary_embedding = self.model.encode(summary_text)
        return np.mean([theme_embedding, summary_embedding], axis=0)

    def _calculate_embedding_area(self, research_areas: List[str]) -> float | None:
        if not research_areas:
            return None
        return np.mean([self.model.encode(area) for area in research_areas], axis=0)

    def _calculate_embedding_periodic(self, periodic_papers: List[str]) -> float | None:
        if not periodic_papers:
            return None
        return np.mean([self.model.encode(paper) for paper in periodic_papers], axis=0)
        
    def _calculate_embedding_congress(self, congress_papers: List[str]) -> float | None:
        if not congress_papers:
            return None
        return np.mean([self.model.encode(paper) for paper in congress_papers], axis=0)
        
    def _calculate_embedding_project(self, project_list: List[str]) -> float | None:
        if not project_list:
            return None
        return np.mean([self.model.encode(project) for project in project_list], axis=0)
        
    def _similarity_with_areas(self, theme_embedding: np.ndarray, research_areas: List[str]) -> float | None:
        if not research_areas:
            return None
        return self.model.similarity(theme_embedding, self._calculate_embedding_area(research_areas))

    def _similarity_with_periodic_papers(self, theme_embedding: np.ndarray, periodic_papers: List[str]) -> float | None:
        if not periodic_papers:
            return None
        return self.model.similarity(theme_embedding, self._calculate_embedding_periodic(periodic_papers))

    def _similarity_with_congress_papers(self, theme_embedding: np.ndarray, congress_papers: List[str]) -> float | None:
        if not congress_papers:
            return None
        return self.model.similarity(theme_embedding, self._calculate_embedding_congress(congress_papers))

    def _similarity_with_projects(self, theme_embedding: np.ndarray, project_list: List[str]) -> float | None:
        if not project_list:
            return None
        return self.model.similarity(theme_embedding, self._calculate_embedding_project(project_list))
