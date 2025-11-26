import os
import argparse
import warnings
from commitee.professors import Member
from logger import init_logger, log
from scraping.LattesParser import LattesParser
from similarity.similarity import SentenceTransformerSimilarity

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m", "--model",
        type=str,
        default="all-mpnet-base-v2",
        help="Nome do modelo SentenceTransformer"
        # Algumas sugestões de modelos:
        # paraphrase-multilingual-mpnet-base-v2
        # distiluse-base-multilingual-cased-v2
        # sentence-transformers/LaBSE
        # paraphrase-multilingual-MiniLM-L12-v2
    )

    parser.add_argument(
        "-t", "--theme",
        type=str,
        default="Analise de Modelos de Lingua de Baixo Custo",
        help="Título do trabalho a ser apresentado"
    )
    parser.add_argument(
        "-s", "--summary",
        type=str,
        default="./sum.txt",
        help="Caminho do arquivo com o resumo"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="ranking_output",
        help="Caminho pro arquivo de saída"
    )

    return parser.parse_args()


def main():

    args = parse_args()
    output = args.output + '_' + args.model + '.txt'

    init_logger(output)   # txt com as saídas
    # theme: str = input("Enter the title of your theme: ")
    theme = args.theme
    summary_file = args.summary.strip()
    # summary_file = input(
    #     "Enter the path to the summary file (leave empty to skip): "
    # ).strip()

    if summary_file:
        try:
            with open(summary_file, "r", encoding="utf-8") as file:
                resumo = file.read()
        except FileNotFoundError:
            raise FileNotFoundError("The specified file does not exist.")
    else:
        resumo = ''
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
    
    similarity = SentenceTransformerSimilarity(args.model)

    member_list = []
    for html_file in html_files:
        file_path = os.path.join(DATA_DIR, html_file)

        parser = LattesParser(file_path)
        prof_info = parser.get_info()

        score = similarity.similarity_score(theme, resumo, prof_info)

        member = Member(prof_info)
        member_list.append((member, score))

    member_list.sort(key=lambda x: x[1], reverse=True)

    log(f'Título do trabalho: {args.theme}')
    log(f'Resumo do trabalho: {resumo}')
    log('\n')
    log("Ranking")
    for member, score in member_list:
        log(f"{member.name:40s}  ->  {score:.4f}")

    log("\nTop 5")

    for member, score in member_list[:5]:
        log('\n')
        member.log_info()
        log('\n')
    
    print(f'Logs salvos em {output}')

if __name__ == "__main__":
    main()
