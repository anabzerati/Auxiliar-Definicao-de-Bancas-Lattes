# Auxiliar-Definicao-de-Bancas-Lattes

Trabalho realizado para a disciplina de “Aprendizado Profundo” do [“Programa de Pós-Graduação em Ciência da Computação
(PPGCC) da Unesp”](https://www.ibilce.unesp.br/#!/pos-graduacao/programas-de-pos-graduacao/ciencia-da-computacao/informacoes-para-candidatos/selecao-de-mestrado-2023/), ministrada pelo “Prof. Dr. Denis Henrique Pinheiro Salvadeo".

O presente trabalho é um projeto exploratório com o objetivo de testar a viabilidade de um algoritmo de recomendação para trabalhos acadêmicos (como TCC, dissertações ou projetos similares).
A recomendação é feita com base em conteúdo, a partir do título e resumo de um trabalho, comparando-os com currículos Lattes de docentes do PPGCC Unesp.

## Descrição geral do sistema 
O sistema realiza as seguintes etapas:
1. Parsing dos currículos Lattes: currículos HTML são processados para extrair informações relevantes de produção bibliográfica dos docentes
2. Geração dos em _embeddings_:  Transformação dos textos via TF-IDF e Sentence Transformers
3. Cálculo de similaridade: Similaridade do cosseno entre o _embedding_ do aluno (média entre título e reumo) e dos currículos (média das seções)
4. Geração de ranking de docentes: O sistema retorna um arquivo de saída indicando os professores mais relacionados ao tema do trabalho, acompanhado de resumos dos currículos Lattes deles

## Estrutura do projeto
- data/ppgcc - contém o código HTML de currículos Lattes extraídos manualmente e individualmente de docentes do PPGCC da Unesp  
- docs - rascunhos e documentos auxiliares
- src - o código em si, incluindo o parsing dos currículos, geração de embeddings, cálculo de similaridade e o pipeline principal (main.py)

## Como rodar
### Instalando dependências
Dentro do diretório principal do projeto:
```
  pip install .
```
Isso instala todos os pacotes usados para rodar o trabalho. É recomendado fazer isso num ambiente isolado, como um ambiente `conda`

### Rodando o código
Dentro do diretório src/:
```
  python main.py
```
### Argumentos (opcional)
É possível colocar alguns argumentos no _script_, abaixo segue um exemplo com todos os argumentos possíveis. Todos os argumentos são opcionais, e todos são abreviáveis com sua primeira letra (-m, -t, -s, -o)
```
python main.py \
  --model 'paraphrase-multilingual-mpnet-base-v2' \
  --theme 'meu titulo de trabalho' \
  --summary './meu_resumo.txt' \
  --output './meu_output'
```
- model é uma _string_ com o nome do modelo de _embedding_ a ser utilizado para calcular os embeddings. Dentro do ```main.py``` tem algumas sugestões de modelos. O _default_ é o ```all-mpnet-base-v2```
- theme é uma _string_ com o título do trabalho a ser pesquisado. O _default_ é "Analise de Modelos de Lingua de Baixo Custo"
- summary é uma _string_ com o caminho até um arquivo de texto com o resumo do trabalho. O _default_ é "./sum.txt"
- output é uma _string_ com o caminho do arquivo de saída a ser gerado pelo _script_. Arquivos de saída seguem o formato (nome de saída)_(modelo de embedding).txt. O _default_ é "ranking_output"
