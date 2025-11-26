from typing import Dict, Tuple, List
import re
from bs4 import BeautifulSoup
import os
from pprint import pprint, pformat


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
                if not area_text.startswith("Objetivo:"):

                    area_return_list.append(area_text)

            return area_return_list
        else:
            # print(
            #     f"Researcher from {self.filename} does not have research area sections in lattes"
            # )
            return []

    def _get_research_projects(self) -> List[str]:
        """Extracts research projects from the loaded reseracher

        Returns:
            List[str]: A list of the research projects. Returns an empty list if the section is not found.
        """
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

                if not area_text.startswith(("Descrição:", "Situação:")):
                    area_return_list.append(area_text)

            return area_return_list
        else:
            print(
                f"Researcher from {self.filename} does not have research area sections in lattes"
            )
            return []

    def _get_periodicals_papers(self) -> List[str]:
        """
        Extracts the titles of the 10 latest periodical papers from the HTML document

        Returns:
            List[str]: a list of up to 10 paper titles.
        """

        periodicals_div = self.soup.find("div", id="artigos-completos")
        # 10 latest papers
        papers = periodicals_div.findAll("span", class_="transform")[:10]

        titles = []
        for paper in papers:
            paper_text: str = paper.get_text(strip=True)
            last_part: str = paper_text.split(";")[-1]

            authors_title = last_part[last_part.find(".") : -1]

            authors_title_split = authors_title.split(".")

            for i in range(0, len(authors_title_split)):
                if len(authors_title_split[i]) > 3:
                    title = authors_title_split[i]
                    break
            titles.append(title)
        return titles

    def _get_congress_papers(self) -> List[str]:
        """Extracts the titles of the 10 latest congress papers from the HTML document.


        Returns:
            List[str]: a list of up to 10 paper titles
        """

        congress_link = self.soup.find(
            "a", attrs={"name": "TrabalhosPublicadosAnaisCongresso"}
        )

        if congress_link is None:
            return []

        papers = congress_link.find_all_next(name="span", attrs={"class": "transform"})[
            :10
        ]

        titles = []

        for paper in papers:
            paper_text: str = paper.get_text(strip=True)
            last_part: str = paper_text.split(";")[-1]

            authors_title = last_part[last_part.find(".") : -1]

            if len(authors_title) == 0:
                continue
            authors_title_split = authors_title.split(".")
            for i in range(0, len(authors_title_split)):
                if len(authors_title_split[i]) > 3:
                    title = authors_title_split[i]
                    break
            titles.append(title)

        return titles

    def _extract_information(self) -> None:
        """Extract and store all relevant info in self.info.

        Side Effects:
            Populates `self.info` with keys: 'name', 'lattes_id', 'research_areas', 'research_areas','periodic papers', 'congress papers' and 'projects'
        """

        name, lattes_id_lattes = self._get_personal_info()

        areas = self._get_research_areas()

        periodic = self._get_periodicals_papers()

        congress = self._get_congress_papers()

        projects = self._get_research_projects()

        self.info = {
            "name": name,
            "lattes_id": lattes_id_lattes,
            "research_areas": areas,
            "periodic_papers": periodic,
            "congress_papers": congress,
            "projects": projects,
        }

    def get_info(self) -> Dict:
        """
        Retrieve the parsed information from the Lattes CV HTML document.

        This method returns a dictionary populated by `_extract_information()`,
        containing key biographical and research-related data extracted from
        the individual's Lattes CV.

        Returns:
            Dict: A dictionary with the following structure:

                {
                    "name": str,
                        # Full name of the researcher.

                    "lattes_id": str,
                        # The unique Lattes platform identifier (usually a numeric string).

                    "research_areas": List[str],
                        # List of declared research areas.

                    "periodic_papers": List[str],
                        # Titles of papers published in academic journals or periodicals.

                    "congress_papers": List[str],
                        # Titles of papers presented at academic conferences or congresses.

                    "projects": List[str]
                        # Titles or descriptions of research projects the person participates in.
                }

        Notes:
            - The dictionary is only available after `_extract_information()` has been executed.
            - If the extraction process failed or was incomplete, some fields may be empty lists or `None`.
        """
        return self.info


def test_output():

    DATA_DIR = "../../data/ppgcc"
    OUTPUT_DIR = "outputs"

    html_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".html")]

    for html_file in html_files:
        file_path = os.path.join(DATA_DIR, html_file)
        base_name = os.path.splitext(html_file)[0]
        output_path = os.path.join(OUTPUT_DIR, f"{base_name}.txt")

        print(f"→ Processando: {html_file}")

        parser = LattesParser(file_path)
        prof_info = parser.get_info()

        # Gera string formatada bonitinha
        output_text = pformat(prof_info, indent=2, width=100)

        # Salva em arquivo .txt
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_text)

        print(f"   ✅ Salvo em {output_path}")


    print("\nProcessamento concluído!")
 


if __name__ == "__main__":

 #   parser = LattesParser("/home/willao/docs/Github/Auxiliar-Definicao-de-Bancas-Lattes/data/ppgcc/8884890472193474.html")
  #  pprint(parser.get_info())
    test_output()
