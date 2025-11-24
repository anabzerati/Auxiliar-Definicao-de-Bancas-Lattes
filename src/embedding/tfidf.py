import numpy as np
import pandas as pd
import os
from collections import defaultdict

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from deep_translator import GoogleTranslator

from ..scraping.LattesParser import LattesParser

try:
    nltk.data.find("corpora/stopwords")
except:
    nltk.download("stopwords")
stopwords_pt = stopwords.words("portuguese")

def translate_block(text: str, max_chars: int = 4000) -> str:
    """
    Translates a long text by splitting it into blocks of size max_chars

    Parameters
        text: the full text to be translated.
        max_chars : maximum number of characters per block. Optional, default = 4000.

    Return
        str: translation of text
    """

    if not text.strip():
        return ""
    
    translator = GoogleTranslator(source='auto', target='pt')

    blocks = []
    start = 0
    while start < len(text):
        # block of size max_chars
        end = min(start + max_chars, len(text))
        
        # splits between two words
        if end < len(text):
            while end > start and text[end] != " ":
                end -= 1

        block = text[start:end].strip()
        blocks.append(block)
        start = end

    translated_blocks = []
    for b in blocks:
        try:
            translated = translator.translate(b)
            translated_blocks.append(translated)
        except Exception as e:
            print("Translation error:", e)            
            translated_blocks.append(b)  # keep original block

    return " ".join(translated_blocks)


# def lattes_embedding(lattes_list: list, vectorizer: TfidfVectorizer) -> dict:
#     """
#     Builds TF-IDF embeddings for each Lattes researcher profile.

#     Parameters
#         lattes_list : list of dictionaries from LattesParser
#         vectorizer : TfidfVectorizer

#     Return
#         dict: researcher ID to TF-IDF vector 
#     """    

#     corpus = []
#     metadata = []

#     for entry in lattes_list:
#         sections = []

#         # relevant text fields = papers, projects and areas
#         for field in ["congress_papers", "periodic_papers", "projects", "research_areas"]:
#             content = entry.get(field, [])
#             sections.extend(content)

#         full_text = " ".join(sections)

#         print("Translating Lattes profile…")
#         full_text_pt = translate_block(full_text)
#         print("Translation completed.")

#         corpus.append(full_text_pt)
#         metadata.append({
#             "lattes_id": entry["lattes_id"],
#             "name": entry["name"],
#         })

#     # embeddings
#     tfidf_matrix = vectorizer.fit_transform(corpus)

#     final_embeddings = {}
#     for vec, info in zip(tfidf_matrix, metadata):
#         final_embeddings[info["lattes_id"]] = vec.toarray()[0]

#     return final_embeddings

DELIM_ITEM = "\n<ITEM_SPLIT>\n"
DELIM_SECTION = "\n<SECTION_SPLIT>\n"

def create_corpus(candidates):
    """
    Build a text corpus and lists of translated content for each candidate professor. 

    Parameters
        candidates : list of professor entries: "congress_papers", "periodic_papers",
        "projects", "research_areas"

    Return
        corpus : list of all items across all candidates
        congress_list : for each candidate, a list of translated congress paper titles
        periodic_list a list of translated periodic paper titles
        projects_list : list of projects
        areas_list : list of research areas
    """
    corpus = []

    congress_list = []
    periodic_list = []
    projects_list = []
    areas_list = []

    # creating corpus
    for entry in candidates:
        congress = entry.get("congress_papers", [])[:10] # 10 newest papers
        periodic = entry.get("periodic_papers", [])[:10]

        # create one block for fast translation (one API call)
        block_congress = DELIM_ITEM.join(congress)
        block_periodic = DELIM_ITEM.join(periodic)

        big_block = block_congress + DELIM_SECTION + block_periodic
        translated_big = translate_block(big_block)
        translated_sections = translated_big.split(DELIM_SECTION)

        if congress:
            translated_congress = translated_sections[0].split(DELIM_ITEM)
        else:
            translated_congress = []

        if periodic:
            translated_periodic = translated_sections[-1].split(DELIM_ITEM)
        else:
            translated_periodic = []

        congress_list.append(translated_congress)
        periodic_list.append(translated_periodic)

        corpus.extend(translated_congress)
        corpus.extend(translated_periodic)

        projects = entry.get("projects", [])[:10]
        projects_list.append(projects)
        corpus.extend(projects)

        research_areas = entry.get("research_areas", [])[:10]
        areas_list.append(research_areas)
        corpus.extend(research_areas)

    return corpus, congress_list, periodic_list, projects_list, areas_list

def embed_professor_sections(candidates, vectorizer):
    """
    Create a TF-IDF embedding for each professor's section

    Parameters
        candidates : list of dicts of candidate professors from LattesParser
        vectorizer : TfidfVectorizer

    Returns
        section_vectors : list, one dictionary per professor with one embedding per section
    """

    corpus, congress_list, periodic_list, projects_list, areas_list = create_corpus(candidates)    

    # fit TF-IDF on corpus
    vectorizer.fit(corpus)

    section_vectors = []

    # create embeddings per section per professor
    for i, entry in enumerate(candidates):
        section_vector = {
            "lattes_id": entry["lattes_id"],
            "name": entry["name"],
        }

        if congress_list[i]:
            vecs = vectorizer.transform(congress_list[i]).toarray()
            section_vector["congress_papers"] = vecs.mean(axis=0)
        else:
            section_vector["congress_papers"] = None

        if periodic_list[i]:
            vecs = vectorizer.transform(periodic_list[i]).toarray()
            section_vector["periodic_papers"] = vecs.mean(axis=0)
        else:
            section_vector["periodic_papers"] = None
            
        if projects_list[i]:
            vecs = vectorizer.transform(projects_list[i]).toarray()
            section_vector["projects"] = vecs.mean(axis=0)
        else:
            section_vector["projects"] = None

        if areas_list[i]:
            vecs = vectorizer.transform(areas_list[i]).toarray()
            section_vector["research_areas"] = vecs.mean(axis=0)
        else:
            section_vector["research_areas"] = None
            
        section_vectors.append(section_vector)

    return section_vectors


def similarity_prof_student(student_vec, prof_sections):
    sim_values = []

    for field in ["congress_papers", "periodic_papers", "projects", "research_areas"]:
        vec = prof_sections.get(field)

        if vec is None:
            continue

        sim = float(cosine_similarity(
            [student_vec],
            [vec]
        )[0][0])

        sim_values.append(sim)

    # total sim = mean of section sims
    return float(np.mean(sim_values)) if sim_values else 0.0


def student_embedding(theme: str, abstract: str, vectorizer, type="mean"):
    """
    Builds a TF-IDF embedding for the student based on theme and abstract.

    Parameters
        theme
        abstract
        vectorizer : TfidfVectorizer
        type: 'mean' or 'concatenate'. Default = 'mean'

    Return
        np.ndarray: TF-IDF vector
    """

    theme_pt = translate_block(theme)
    abstract_pt = translate_block(abstract)
    
    if type == "mean":
        embeddings = vectorizer.transform([theme_pt, abstract_pt]).toarray()
        student_vec = embeddings.mean(axis=0)

    elif type == "concatenate":
        text = theme_pt + " " + abstract_pt
        student_vec = vectorizer.transform([text]).toarray()[0]

    else:
        raise ValueError("Unknown parameter. Options: 'mean' or 'concatenate'")
    
    return student_vec

if __name__ == "__main__":
    DATA_DIR = "data/ppgcc"
    html_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".html")]

    print("Parsing Lattes files")

    candidates = []
    for html_file in html_files:
        file_path = os.path.join(DATA_DIR, html_file)

        parser = LattesParser(file_path)
        candidates.append(parser.get_info())

    aluno = {
        'theme': "Aprendizado de representações multivisão para análise de imagens com aplicações em biossensores",
        'abstract': "Diante da crescente complexidade e diversidade das imagens capturadas por diferentes dispositivos, surge a necessidade de métodos de análise de imagens mais sofisticados. As imagens capturadas por biossensores são exemplos de dados contemporâneos e ainda pouco estudados. Elas são compostas por padrões complexos que demandam métodos altamente discriminativos, capazes de descrever sua complexidade para efetuar tarefas de reconhecimento. Atualmente, muitas técnicas de análise de imagens concentram-se numa única perspectiva da imagem, limitando a capacidade de extrair informações complexas e robustas. Nesse sentido, o principal objetivo deste projeto é desenvolver métodos baseados em aprendizado de representações multivisão para análise de imagens. Tal abordagem permite a integração de múltiplas perspectivas da mesma imagem, aumentando assim a complementariedade de informações e a robustez da representação. Assim, este projeto foca em três pontos-chaves de pesquisa para desenvolvimento de métodos: (i) estudo, obtenção e gerações de visões de imagens. (ii) aprendizado de representações multivisão; (iii) agregação de características multivisão. Além da frente teórica, este projeto objetiva aplicar os métodos desenvolvidos na caracterização e classificação de imagens de biossensores visando novas estratégias para aplicações como diagnóstico precoce de câncer e detecção de vírus ou contaminações. Essas imagens são fornecidas por colaboradores do projeto temático (processo, 2018/22214-6) em que este projeto de mestrado está vinculado. Desta forma, espera-se que os métodos desenvolvidos contribuam com avanços na área análise de imagens com métodos mais robustos, além de novas estratégias de detecção e diagnóstico nas áreas de físico-química e medicina. "
    }

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words=stopwords_pt,
        max_features=8000,
        ngram_range=(1,2)
    )

    print("Creating Lattes Profile's Embeddings")
    prof_sections = []
    # lattes_embeddings = lattes_embedding(candidates, vectorizer)
    prof_sections = embed_professor_sections(candidates, vectorizer)

    print("Creating Students's Embedding")
    student_vec = student_embedding(aluno["theme"], aluno["abstract"], vectorizer)

    print("Creating Lattes Profile's Embeddings")
    ranking = []
    # lattes_embeddings = lattes_embedding(candidates, vectorizer)
    for prof in prof_sections:
        print(prof["name"])
        score = similarity_prof_student(student_vec, prof)

        ranking.append((prof["lattes_id"], prof["name"], score))

    # Ordena por maior similaridade
    ranking.sort(key=lambda x: x[2], reverse=True)

    # print("Calculating Cosine Similarity")
    # scores = {
    #     pid: float(cosine_similarity([student_vec], [emb])[0][0])
    #     for pid, emb in lattes_embeddings.items()
    # }

    # ranking = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    print("Ranking")
    for pid, name, score in ranking:
        # name = next(p["name"] for p in candidates if p["lattes_id"] == pid)
        print(f"{name:40s}({pid})  ->  {score:.4f}")
