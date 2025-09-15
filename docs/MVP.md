Primeiro entregar com os titulares 
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
- 10 publicações mais recentes da seção "**Artigos completos publicados em periódicos**"
-  10 publicações mais recentes na seção **Trabalhos completos publicados em anais de congressos**
- Seção **linhas de pesquisa**

obs: seções que tem na página HTML do lattes

Representar cada pesquisador em como um vetor usando Transformers e calcular a similaridade 

Tem que ter comparação de modelos, então poderíamos fazer:
- TF-IDF
- outros dois modelos de LLM

### Rank
O rank vai consistir numa lista ordenada pelo **final score**, que é uma métrica que juntar o similarity score e a distância no grafo de colaboração.
