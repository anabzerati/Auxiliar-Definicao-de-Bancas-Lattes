import os
import argparse
import warnings
from commitee.professors import Member
from scraping.LattesParser import LattesParser
from similarity.similarity import SentenceTransformerSimilarity


def main():
    theme: str = input("Enter the title of your theme: ")

    summary_file = input(
        "Enter the path to the summary file (leave empty to skip): "
    ).strip()

    if summary_file:
        try:
            with open(summary_file, "r", encoding="utf-8") as file:
                resumo = file.read()
        except FileNotFoundError:
            raise FileNotFoundError("The specified file does not exist.")
    else:
        warnings.warn(
            "No summary file provided. Only the title will be used to find the TCC committee.",
            UserWarning,
        )

    print("\n=== Input Summary ===")
    print(f"Title: {theme}")
    if summary_file:
        print(f"Summary file: {summary_file}")
    else:
        print("Summary file: (none provided)")

    DATA_DIR = "../data/ppgcc"

    html_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".html")]

    member_list = []
    for html_file in html_files:
        file_path = os.path.join(DATA_DIR, html_file)
        base_name = os.path.splitext(html_file)[0]

        parser = LattesParser(file_path)
        prof_info = parser.get_info()

        similarity = SentenceTransformerSimilarity("all-mpnet-base-v2")
        score = similarity.similarity_score(theme, resumo, prof_info)

        member = Member(prof_info)
        member_list.append((member, score))

    member_list.sort(key=lambda x: x[1], reverse=True)

    for member, score in member_list[:5]:
        member.print_info()
        print(f"Score: {score}\n")


if __name__ == "__main__":
    main()
