# Compilador para a Linguagem Rascal

Este repositório contém o código-fonte de um compilador para Rascal, uma linguagem de programação didática com sintaxe inspirada em Pascal. O projeto foi desenvolvido em Python utilizando a biblioteca PLY (Python Lex-Yacc) e abrange as fases de análise léxica e sintática (por enquanto),  construção de uma Árvore Sintática Abstrata (AST) e sua visualização gráfica.

## A Linguagem Rascal

Rascal é uma linguagem imperativa e estruturada, projetada para fins educacionais. Suas principais características são:

-   **Tipagem Estática:** Suporta apenas os tipos primitivos `integer` e `boolean`.
    
-   **Sintaxe Pascal-like:** Utiliza palavras-chave como `program`, `var`, `begin`, `end`, `if-then-else` e `while-do`.
    
-   **Operadores:** Inclui operadores aritméticos (`+`, `-`, `*`, `div`), lógicos (`and`, `or`, `not`) e relacionais (`=`, `<>`, `<`, `>`, `<=`, `>=`).
    
-   **Estrutura Rígida:** Um programa é sempre definido por um bloco principal, com seções opcionais para declaração de variáveis e sub-rotinas (procedimentos e funções).
    
-   **Comentários:** Suporta comentários no estilo Pascal, delimitados por `{ ... }` ou `(* ... *)`.
    

## Estrutura do Projeto

O compilador está organizado nos seguintes arquivos principais:

### 1. `lex.py` (Analisador Léxico)

Este módulo é responsável pela primeira fase da compilação, a **Análise Léxica**.  Ele lê o código-fonte Rascal como uma sequência de caracteres e o converte em uma sequência de "tokens" (unidades léxicas).

-   **Funcionalidade:** Utiliza expressões regulares para identificar palavras-chave (`program`, `if`, etc.), identificadores, números, operadores e símbolos de pontuação.
    
-   **Tratamento de Erros:** É capaz de identificar e reportar caracteres inválidos e identificadores malformados.
    
-   **Ignora:** Espaços em branco, tabulações e comentários são descartados nesta fase.

### 2. `yacc.py` (Analisador Sintático)

Este é o coração do projeto, responsável pela **Análise Sintática** (ou _parsing_). Ele recebe a lista de tokens do analisador léxico e verifica se eles formam uma sequência válida de acordo com a gramática formal da linguagem Rascal.

-   **Funcionalidade:** Implementa a gramática da linguagem, definindo a estrutura de programas, declarações, comandos e expressões.
    
-   **Construção da AST:** Se a sintaxe do programa estiver correta, o analisador constrói uma **Árvore Sintática Abstrata (AST)**. A AST é uma representação hierárquica e estruturada do código, muito mais fácil de ser processada nas fases seguintes do que o código-fonte original. A AST gerada é salva no formato JSON no arquivo `ast.json`.
    
-   **Tratamento de Erros:** Reporta erros de sintaxe, como a falta de um ponto e vírgula, um `end` ausente ou uma expressão malformada.
    

### 3. `ver-ast.py` (Visualizador da AST)

Para facilitar a depuração e o entendimento da estrutura gerada pelo parser, este script lê o arquivo `ast.json` e gera uma representação gráfica da árvore.

Utiliza a biblioteca `graphviz` para desenhar a árvore de forma automática e legível.
    
-   **Saída:** Gera um arquivo de imagem (`ast_visualizada.png`) com nós e arestas que representam a estrutura do programa analisado.
    

## Como Executar

### Pré-requisitos

1.  **Python 3.x**
    
2.  **Biblioteca PLY:**  `pip install ply`
    
3.  **Graphviz:**
    
    -   **Instale a biblioteca Python:**  `pip install graphviz`
        
    -   **Instale o software Graphviz:** É necessário ter o Graphviz instalado no seu sistema operacional. [Visite o site oficial para downloads e instruções](https://graphviz.org/download/ "null").
        

### Passos para Execução

O processo ocorre em duas etapas:

**1. Gerar a AST a partir de um arquivo txt ue contêm código-fonte Rascal:**

Execute o analisador sintático, passando o caminho para o seu arquivo de código-fonte `.txt` como argumento.

```
python yacc.py /caminho/para/seu/teste.txt

```

Se a análise for bem-sucedida, uma mensagem de sucesso será exibida e o arquivo `ast.json` será criado no diretório.

**2. Visualizar a AST gerada:**

Execute o script de visualização, que irá ler o `ast.json` e gerar a imagem.

```
python ver-ast.py ast.json

```

Após a execução, um arquivo de imagem chamado `ast_visualizada.png` será salvo na mesma pasta, contendo a representação gráfica da árvore gerada.
