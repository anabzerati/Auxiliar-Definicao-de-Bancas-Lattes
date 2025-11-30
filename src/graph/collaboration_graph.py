import os
import matplotlib.pyplot as plt
from collections import defaultdict
import itertools

from commitee.professors import Member
from scraping.LattesParser import LattesParser

import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities

def build_collaboration_graph(candidates):
    # dict: publication_title -> list of professor names
    pub_to_authors = defaultdict(list)

    for prof in candidates:
        name = prof.name

        all_pubs = (
            prof.periodic_papers +
            prof.congress_papers +
            prof.projects
        )

        for pub in all_pubs:
            pub_to_authors[pub].append(name)

    # graph
    G = nx.Graph()

    for prof in candidates:
        G.add_node(prof.name)

    # edges based on publications together
    for pub, authors in pub_to_authors.items():
        if len(authors) < 2:
            continue  

        for a, b in itertools.combinations(authors, 2):
            if a == b:
                continue  # avoid loops

            if G.has_edge(a, b):
                G[a][b]["weight"] += 1
                G[a][b]["publications"].append(pub)
            else:
                G.add_edge(a, b, weight=1, publications=[pub])

    return G

def plot_graph(G):
    pos = nx.spring_layout(G, seed=42, k=0.7)
    weights = [G[u][v]['weight'] for u, v in G.edges()]

    # defining colors based on communities
    communities = list(greedy_modularity_communities(G))
    node_color_map = {}
    for i, comm in enumerate(communities):
        for node in comm:
            node_color_map[node] = i
    node_colors = [node_color_map[node] for node in G.nodes()]

    plt.figure(figsize=(14, 14))
    plt.axis("off")

    nx.draw_networkx_nodes(
        G,
        pos,
        node_color=node_colors,
        cmap="tab20",
        alpha=0.9
    )

    nx.draw_networkx_edges(
        G,
        pos,
        width=weights,
        alpha=0.6
    )

    nx.draw_networkx_labels(
        G,
        pos
    )

    plt.title("Collaboration Graph - PPGCC Unesp", fontsize=16)
    plt.show()

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
    
    print("Professores:", graph.nodes())
    print("Colaborações:", graph.edges(data=True))

    plot_graph(graph)

if __name__ == "__main__":
    main()
