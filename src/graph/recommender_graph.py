import os
import networkx as nx
from networkx.algorithms.link_prediction import adamic_adar_index

from graph.collaboration_graph import build_collaboration_graph
from commitee.professors import Member
from scraping.LattesParser import LattesParser

def recommend_pr(G, orientador, k=3, alpha=0.15):
    pr = nx.pagerank(G, alpha=1-alpha, personalization={orientador: 1})
    
    candidatos = [
        (n, score) for n, score in pr.items()
        if n != orientador and not G.has_edge(n, orientador)
    ]

    candidatos.sort(key=lambda x: x[1], reverse=True)
    return candidatos[:k]

def recommend_adamic(G, orientador, k=3):
    scores = []
    for n in G.nodes():
        if n == orientador or G.has_edge(orientador, n):
            continue
        score = list(adamic_adar_index(G, [(orientador, n)]))[0][2]
        scores.append((n, score))
    
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:k]


def main():
    DATA_DIR = "../data/ppgcc"

    html_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".html")]

    member_list = []
    for html_file in html_files:
        file_path = os.path.join(DATA_DIR, html_file)

        parser = LattesParser(file_path)
        prof_info = parser.get_info()

        member = Member(prof_info)
        member_list.append(member)

    graph = build_collaboration_graph(member_list)

    print("Professores carregados:")
    for n in graph.nodes:
        print(" -", n)

    orientador = "Lucas Correia Ribas"

    recomendados = recommend_adamic(graph, orientador)
    print("\nRecomendações:")
    for prof, score in recomendados:
        print(f"{prof}: {score:.4f}")

if __name__ == "__main__":
    main()
