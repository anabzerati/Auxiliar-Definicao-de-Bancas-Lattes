Primeiro entregar com os titulares utilizando somente membros do ICT 
## Input
- [ ] Interface simples no terminal para receber o título do tema + lattes do orientador


## Processamento

Construir grafo de colaboração, cada nó contém **Nome, Lattes, similarity score, isFromICT, IsFromUnesp**
- [ ] Construir grafo até distância com orientador no máximo K
- [ ] Remover duplicadas (Orientador colaborou com Y e Z, mas Y também colaborou com Z)
- [ ] Calcular similarity score 
- [ ] Adiciona ao rank


### Similarity score
Considera: 
- 10 publicações mais recentes de periódicos e anais de congresso
- Seção **linhas de pesquisa**
- Seção ** projetos de pesquisa**

obs: seções que tem na página HTML do lattes

Representar cada pesquisador em como um vetor usando Transformers e calcular a similaridade 

Tem que ter comparação de modelos, então poderíamos fazer para calcular embedding:
- TF-IDF
- outros dois modelos de LLM
  
  Para modelos de LLM, temos a biblioteca:
  https://sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html


Para o caso dos vetores não terem o tamanho requirido pelo modelo, calcular o vetor de embeddings para cada seção e fazer a média (se juntar todas seções em um único texto, não serve de entrada no modelo porque gera tokens maior que o número suportado).
### Rank
O rank vai consistir numa lista ordenada pelo **final score**, que é a similaridade semântica 
