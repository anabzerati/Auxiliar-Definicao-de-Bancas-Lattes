from typing import List, Dict
import argparse
from logger import log


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

        self.name = info["name"]
        self.lattes_id = info["lattes_id"]
        self.research_areas = info["research_areas"]
        self.periodic_papers = info["periodic_papers"]
        self.congress_papers = info["congress_papers"]
        self.projects = info["projects"]

    def log_info(self) -> None:
        log(f"--- Professor Information ---")
        log(f"Name: {self.name}")
        log(f"Lattes ID: {self.lattes_id}")
        log("\nResearch Areas:")
        for area in self.research_areas:
            log(f"  - {area}")

        log("\nPeriodic Papers:")
        for paper in self.periodic_papers:
            log(f"  - {paper}")

        log("\nCongress Papers:")
        for paper in self.congress_papers:
            log(f"  - {paper}")

        log("\nProjects:")
        for project in self.projects:
            log(f"  - {project}")
