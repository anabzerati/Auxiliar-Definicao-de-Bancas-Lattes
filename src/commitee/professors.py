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

        self.name = info["name"]
        self.lattes_id = info["lattes_id"]
        self.research_areas = info["research_areas"]
        self.periodic_papers = info["periodic_papers"]
        self.congress_papers = info["congress_papers"]
        self.projects = info["projects"]

    def print_info(self) -> None:
        print(f"--- Professor Information ---")
        print(f"Name: {self.name}")
        print(f"Lattes ID: {self.lattes_id}")
        print("\nResearch Areas:")
        for area in self.research_areas:
            print(f"  - {area}")

        print("\nPeriodic Papers:")
        for paper in self.periodic_papers:
            print(f"  - {paper}")

        print("\nCongress Papers:")
        for paper in self.congress_papers:
            print(f"  - {paper}")

        print("\nProjects:")
        for project in self.projects:
            print(f"  - {project}")
