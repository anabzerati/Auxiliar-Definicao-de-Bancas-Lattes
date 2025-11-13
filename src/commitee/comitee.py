from typing import Optional
from professors import Member  # supondo que a classe Member está definida em member.py

class Committee:
    def __init__(self, title: str, summary: Optional[str], advisor: Member, titular1: Member, titular2: Member, substitute: Member):
        """
        Initialize a Committee instance.

        Args:
            title (str): The title of the TCC or research theme.
            summary (Optional[str]): The summary or abstract of the project.
            advisor (Member): The advisor (orientador) of the committee.
            titular1 (Member): The first titular member.
            titular2 (Member): The second titular member.
            substitute (Member): The substitute (suplente) member.
        """
        self.title: str
        self.summary: Optional[str]
        self.advisor: Member
        self.titular1: Member
        self.titular2: Member
        self.substitute: Member
