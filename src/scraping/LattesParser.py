from typing import Dict, Tuple, List
import re
from bs4 import BeautifulSoup


class LattesParser:
    """
    Parses a HTML file of a Lattes CV to extract key information
    """

    def __init__(self, filename: str):
        """Initializes the LattesParser.

        Args:
            filename (str): The file path to the HTML Lattes CV.
        """

        self.filename = filename
        self.soup = self._load_html()
        self.info: Dict = {}
        self._extract_information()

    def _load_html(self) -> BeautifulSoup:
        """Loads and parses the HTML file into a BeautifulSoap object.

        Uses 'latin-1' encoding because there are portuguese texts.

        Returns:
            BeautifulSoup: _description_
        """
        with open(self.filename, encoding="latin-1") as fp:
            return BeautifulSoup(fp, "html.parser")

    def _get_personal_info(self) -> Tuple[str, str]:
        """Get information from the 'personal information' section in a Lattes CV


        Returns:
            Tuple[str, str]: A tuple containing the researcher's Name and Lattes ID
        """

        # parses the div 'infPessoa'
        div_personal_info = self.soup.find("div", class_="infpessoa")

        # finds h2 tag with class nome, which contains the name
        name = div_personal_info.find("h2", class_="nome").get_text(strip=True)

        # kind of a hacky to get the ID by using the style from the span within the infPessoa
        lattes_id = div_personal_info.find(
            "span", style="font-weight: bold; color: #326C99;"
        ).get_text(strip=True)

        return name, lattes_id

    def _get_research_areas(self) -> List[str]:
        """Extracts the researcher's research areas (Linhas de Pesquisa).


        Returns:
            List[str]: A list of research area titles. Returns an empty list
                       if the section is not found.
        """

        reasearch_line_link = self.soup.find("a", attrs={"name": "LinhaPesquisa"})

        # yes it is possible to not have a "Linhas de Pesquisa" section
        if reasearch_line_link:
            main_div_area = (
                reasearch_line_link.parent
            )  # get the parent div from the LinhaPesquisa link section

            # hacky filter to filters only divs with the name 'layout-cell-pad-5' and nothing else, as observed by the website
            # those obtain the titles
            areas = [
                div
                for div in main_div_area.find_all("div")
                if div.get("class") == ["layout-cell-pad-5"]
            ]

            area_return_list = []
            for area in areas:
                area_text = area.get_text(strip=True)

                # some Linhas de Pesquisa may have an "Objetivo" field with useless information
                # dude i really wish that i had  conceived a better idea to solve this.
                if not area_text.startswith("Objetivo: "):

                    area_return_list.append(area_text)

            return area_return_list
        else:
            print(
                f"Researcher from {self.filename} does not have research area sections in lattes"
            )
            return []


    def _get_research_projects(self) -> List[str]:
        research_project_link = self.soup.find("a", attrs={"name": "ProjetosPesquisa"}) 
    
        if research_project_link:
            main_div_area = (
                research_project_link.parent
            )  # get the parent div from the ProjetosPesquisa link section

            # hacky filter to filters only divs with the name 'layout-cell-pad-5' and nothing else, as observed by the website
            # those obtain the titles
            areas = [
                div
                for div in main_div_area.find_all("div")
                if div.get("class") == ["layout-cell-pad-5"]
            ]

            area_return_list = []
            for area in areas:
                area_text = area.get_text(strip=True)
                        

                if not area_text.startswith("Descrição:"):
                    print(area_text)
                    area_return_list.append(area_text)

            return area_return_list
        else:
            print(
                f"Researcher from {self.filename} does not have research area sections in lattes"
            )
            return []


    def _get_periodicals_papers(self) -> List[str]:
        """
        Incomplete
        """

        periodicals_div = self.soup.find("div", id="artigos-completos")

        papers = periodicals_div.findAll("span", class_="transform")

        titles = []
        for paper in papers:
            paper_text: str = paper.get_text(strip=True)
            last_part: str = paper_text.split(';')[-1]
            
            authors_title = last_part[last_part.find("."):-1]

            authors_title_split = authors_title.split(".")

            for i in range(0,4):
                if len(authors_title_split[i]) > 3:
                    title = authors_title_split[i]
                    break

            titles.append(title)

        return titles 
    def _extract_information(self) -> None:
        """Extract and store all relevant info in self.info.

        Side Effects:
            Populates `self.info` with keys: 'name', 'lattes_id', 'research_areas', 'papers'
        """

        name, lattes_id_lattes = self._get_personal_info()

        areas = self._get_research_areas()

        periodic = self._get_periodicals_papers()

        projects = self._get_research_projects()

    def get_info(self) -> Dict:
        """Public getter for the extracted information from .html lattes cv

        Returns:
            Dict: A dictionary containing all extracted Lattes information.
        """
        return self.info


if __name__ == "__main__":
    parser = LattesParser("/home/willao/docs/Github/Auxiliar-Definicao-de-Bancas-Lattes/data/ppgcc/2740441033907310.html")
