from typing import Dict, Tuple, List
import re
from bs4 import BeautifulSoup


class LattesParser:
    def __init__(self, filename: str):
        self.filename = filename
        self.soup = self._load_html()
        self.info: Dict = {}
        self._extract_information()

    def _load_html(self) -> BeautifulSoup:
        with open(self.filename, encoding="latin-1") as fp:
            return BeautifulSoup(fp, "html.parser")




    def _get_personal_info(self) -> Tuple[str, str]:

        div_personal_info = self.soup.find("div", class_="infpessoa")

        name = div_personal_info.find("h2", class_="nome").get_text(strip=True)

        lattes_id = div_personal_info.find(
            "span", style="font-weight: bold; color: #326C99;"
        ).get_text(strip=True)

        return name, lattes_id



    def _get_research_areas(self) -> List[str]:
        reasearch_line_link = self.soup.find("a", attrs={"name": "LinhaPesquisa"})

        # yes it is possible to not have a "Linhas de Pesquisa" section
        if reasearch_line_link:
            main_div_area = reasearch_line_link.parent

            # filters only divs with the name 'layout-cell-pad-5' and nothing else, as observed by the website
            # those obtain the titles
            areas = [
                div
                for div in main_div_area.find_all("div")
                if div.get("class") == ["layout-cell-pad-5"]
            ]

            area_return_list = []
            for area in areas:
                area_text = area.get_text(strip=True)

                if not area_text.startswith("Objetivo: "):

                    area_return_list.append(area_text)

            return area_return_list
        else:
            print(
                f"Researcher from {self.filename} does not have research area sections in lattes"
            )
            return "null"
        


    def _get_periodicals_papers(self) -> List[str]:

        periodicals_div = self.soup.find("div", id="artigos-completos")

        papers = periodicals_div.findAll("span", class_="transform")


        for paper in papers:
            print(paper.get_text(strip=True))
            print("\n\n")

    def _extract_information(self) -> None:
        """Extract and store all relevant info in self.info."""

        name, lattes_id_lattes = self._get_personal_info()

        areas = self._get_research_areas()

        periodic = self._get_periodicals_papers()

    def get_info(self) -> Dict:
        """Return the stored dictionary."""
        return self.info


if __name__ == "__main__":
    parser = LattesParser(
        # "/home/willao/docs/Github/Auxiliar-Definicao-de-Bancas-Lattes/data/ppgcc/4644812253875832.html"
        "/home/willao/docs/Github/Auxiliar-Definicao-de-Bancas-Lattes/data/ppgcc/8031012573259361.html"
    )
