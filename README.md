# Compilador para a Linguagem Rascal

Este repositório contém o código-fonte de um compilador para Rascal, uma linguagem de programação didática com sintaxe inspirada em Pascal. O projeto foi desenvolvido em Python utilizando a biblioteca PLY (Python Lex-Yacc) e abrange as fases de análise léxica, sintática, semântica, construção de uma Árvore Sintática Abstrata (AST) e sua visualização gráfica.

## A Linguagem Rascal

Rascal é uma linguagem imperativa e estruturada, projetada para fins educacionais. Suas principais características são:

-   **Tipagem Estática:** Suporta apenas os tipos primitivos `integer` e `boolean`.
    
-   **Sintaxe Pascal-like:** Utiliza palavras-chave como `program`, `var`, `begin`, `end`, `if-then-else` e `while-do`.
    
-   **Operadores:** Inclui operadores aritméticos (`+`, `-`, `*`, `div`), lógicos (`and`, `or`, `not`) e relacionais (`=`, `<>`, `<`, `>`, `<=`, `>=`).
        
-   **Comentários:** Suporta comentários no estilo Pascal, delimitados por `{ ... }` ou `(* ... *)`.
    

## Estrutura do Projeto

O compilador está organizado nos seguintes arquivos principais:

### 1. `lex.py` (Analisador Léxico)

Este arquivo é responsável pela primeira fase da compilação, a **Análise Léxica**.  Ele lê o código-fonte Rascal como uma sequência de caracteres e o converte em uma sequência de "tokens".

-   **Funcionalidade:** Utiliza expressões regulares para identificar palavras-chave (`program`, `if`, etc.), identificadores, números, operadores e símbolos de pontuação.
    
-   **Tratamento de Erros:** É capaz de identificar e reportar caracteres inválidos e identificadores malformados.
    
-   **Ignora:** Espaços em branco, tabulações e comentários são descartados nesta fase.

### 2. `yacc.py` (Analisador Sintático)

Este arquivo é responsável pela **Análise Sintática** (ou _parsing_). Ele recebe a lista de tokens do analisador léxico e verifica se eles formam uma sequência válida de acordo com a gramática formal da linguagem Rascal.

-   **Funcionalidade:** Implementa a gramática da linguagem, definindo a estrutura de programas, declarações, comandos e expressões.
    
-   **Construção da AST:** Se a sintaxe do programa estiver correta, o analisador constrói uma **Árvore Sintática Abstrata (AST)**. A AST é uma representação hierárquica e estruturada do código, muito mais fácil de ser processada nas fases seguintes do que o código-fonte original. A AST gerada é salva no formato JSON no arquivo `ast.json`.
    
-   **Tratamento de Erros:** Reporta erros de sintaxe, como a falta de um ponto e vírgula, um `end` ausente ou uma expressão malformada.
    
### Pré-requisitos

1.  **Python 3.x**
    
2.  **Biblioteca PLY:**  `pip install ply` 
