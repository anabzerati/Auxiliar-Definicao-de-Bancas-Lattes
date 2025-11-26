import os
import argparse
import warnings
from commitee.professors import Member
from scraping.LattesParser import LattesParser
from similarity.similarity import SentenceTransformerSimilarity

import warnings
warnings.filterwarnings("ignore")

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

    print("\n--- Input Summary ---")
    print(f"Title: {theme}\n")
    if summary_file:
        print(f"Summary file: {summary_file}")
        print(f"Summary content: {resumo}")
    else:
        print("Summary file: (none provided)")

    print("\n\n--- Analyzing Lattes profiles and calculating recommendations ---")

    DATA_DIR = "../data/ppgcc"

    html_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".html")]

    member_list = []
    for html_file in html_files:
        file_path = os.path.join(DATA_DIR, html_file)

        parser = LattesParser(file_path)
        prof_info = parser.get_info()

        similarity = SentenceTransformerSimilarity("all-mpnet-base-v2")
        score = similarity.similarity_score(theme, resumo, prof_info)

        member = Member(prof_info)
        member_list.append((member, score))

    member_list.sort(key=lambda x: x[1], reverse=True)

    print("\n\n--- Ranking ---")
    for member, score in member_list:
        print(f"{member.name:40s}  ->  {score:.4f}")

    print("\n\n --- Lattes profile information for the top 5 recommendations ---")
    for member, score in member_list[:5]:
        print()
        member.print_info()
        print()

if __name__ == "__main__":
    main()
