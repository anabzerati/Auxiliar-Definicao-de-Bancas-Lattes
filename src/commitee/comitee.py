from typing import Optional, Tuple
from professors import Member  

class Committee:
    def __init__(
        self,
        title: str,
        summary: Optional[str],
        advisor: Tuple[Member, float],
        titular1: Tuple[Member, float],
        titular2: Tuple[Member, float],
        substitute: Tuple[Member, float]
    ):
        """
        Initialize a Committee instance with members paired with similarity scores.

        Args:
            title (str): The title of the TCC or research theme.
            summary (Optional[str]): The summary or abstract of the project.
            advisor (Tuple[Member, float]): The advisor and their similarity score.
            titular1 (Tuple[Member, float]): The first titular member and their similarity score.
            titular2 (Tuple[Member, float]): The second titular member and their similarity score.
            substitute (Tuple[Member, float]): The substitute member and their similarity score.
        """
        self.title: str
        self.summary: Optional[str]

        self.advisor: Tuple[Member, float]
        self.titular1: Tuple[Member, float]
        self.titular2: Tuple[Member, float]
        self.substitute: Tuple[Member, float]
