from typing import List, Dict

class Member:
    def __init__(self, info: Dict):
        """
        Initialize a Member instance with information parsed from a Lattes CV.

        Args:
            info (Dict): A dictionary containing the member's data, as returned by `get_info()`.
        """
        self.name: str
        self.lattes_id: str
        self.research_areas: List[str]
        self.periodic_papers: List[str]
        self.congress_papers: List[str]
        self.projects: List[str]

    def calculate_sim_score(self, theme: str, title: str) -> float:
        """
        Calculate a similarity score between the given theme/title and the member's profile.

        Args:
            theme (str): The research theme or topic title.
            title (str): The title of the TCC or project.

        Returns:
            float: The calculated similarity score.
        """
        pass
