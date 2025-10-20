from lex import tokens
import ply.yacc as yacc 
import sys
import json

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('nonassoc', 'IGUAL', 'DIF', 'MENOR', 'MENORIG', 'MAIOR', 'MAIORIG'),
    ('left', 'MAIS', 'MENOS'),
    ('left', 'VEZES', 'DIV'),
    ('right', 'UMENOS'), 
    ('nonassoc', 'THEN'),
    ('nonassoc', 'ELSE'),
)

# --- Regras da Gramática ---
def p_programa(p):
    'programa : PROGRAM IDENTIFICADOR PONTOV bloco PONTO'
    p[0] = {'tipo': 'programa', 'nome': p[2], 'corpo': p[4]}

def p_bloco(p):
    'bloco : secao_declara_vars_opt secao_declara_subrotinas comando_composto'
    p[0] = {'tipo': 'bloco', 'vars': p[1], 'subrotinas': p[2], 'comandos': p[3]}

# --- DECLARAÇÕES ---
def p_secao_declara_vars_opt(p):
    '''
    secao_declara_vars_opt : VAR declaracao_vars_lista
                           | empty
    '''
    p[0] = p[2] if len(p) > 2 else []

def p_declaracao_vars_lista(p):
    '''
    declaracao_vars_lista : declaracao_vars_lista declaracao_vars PONTOV
                          | declaracao_vars PONTOV
    '''
    if len(p) == 4:
        p[0] = p[1] + p[2]
    else:
        p[0] = p[1]

def p_declaracao_vars(p):
    'declaracao_vars : lista_ids DOISP tipo'
    p[0] = [{'tipo': 'decl_var', 'id': {'tipo': 'id', 'nome': id_nome}, 'tipo_var': p[3]} for id_nome in p[1]]

def p_lista_ids(p):
    '''
    lista_ids : lista_ids VIRG IDENTIFICADOR
              | IDENTIFICADOR
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_tipo(p):
    '''
    tipo : TIPO_INTEIRO
         | TIPO_BOLEANO
    '''
    p[0] = p[1]

# --- SUB-ROTINAS (PROCEDURE E FUNCTION) ---
def p_secao_declara_subrotinas(p):
    '''
    secao_declara_subrotinas : secao_declara_subrotinas declaracao_subrotina PONTOV
                             | empty
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_declaracao_subrotina(p):
    '''
    declaracao_subrotina : declaracao_procedimento
                         | declaracao_funcao
    '''
    p[0] = p[1]

def p_declaracao_procedimento(p):
    'declaracao_procedimento : PROCEDURE IDENTIFICADOR parametros_formais_opt PONTOV bloco_subrot'
    p[0] = {'tipo': 'decl_proc', 'nome': p[2], 'params': p[3], 'corpo': p[5]}

def p_declaracao_funcao(p):
    'declaracao_funcao : FUNCTION IDENTIFICADOR parametros_formais_opt DOISP tipo PONTOV bloco_subrot'
    p[0] = {'tipo': 'decl_func', 'nome': p[2], 'params': p[3], 'retorno': p[5], 'corpo': p[7]}

def p_bloco_subrot(p):
    'bloco_subrot : secao_declara_vars_opt comando_composto'
    p[0] = {'tipo': 'bloco', 'vars': p[1], 'subrotinas': [], 'comandos': p[2]}

def p_parametros_formais_opt(p):
    '''
    parametros_formais_opt : parametros_formais
                           | empty
    '''
    p[0] = p[1] if p[1] else []

def p_parametros_formais(p):
    'parametros_formais : PARE lista_parametros PARD'
    p[0] = p[2]

def p_lista_parametros(p):
    '''
    lista_parametros : lista_parametros PONTOV declaracao_parametros
                     | declaracao_parametros
    '''
    if len(p) == 4:
        p[0] = p[1] + p[3]
    else:
        p[0] = p[1]

def p_declaracao_parametros(p):
    'declaracao_parametros : lista_ids DOISP tipo'
    p[0] = [{'tipo': 'decl_param', 'id': {'tipo': 'id', 'nome': id_nome}, 'tipo_var': p[3]} for id_nome in p[1]]

# --- COMANDOS ---
def p_comando_composto(p):
    'comando_composto : BEGIN comando_lista_opt END'
    p[0] = p[2]

def p_comando_lista_opt(p):
    '''
    comando_lista_opt : comando_lista
                      | empty
    '''
    p[0] = p[1] if p[1] else {'tipo': 'seq_comandos', 'primeiro': None, 'resto': None}

def p_comando_lista(p):
    '''
    comando_lista : comando_lista PONTOV comando
                  | comando
    '''
    if len(p) == 4:
        node = p[1]
        while node and node.get('resto'):
            node = node['resto']
        if node and node.get('primeiro'):
             node['resto'] = {'tipo': 'seq_comandos', 'primeiro': p[3], 'resto': None}
        else:
            p[1]['primeiro'] = p[3]
        p[0] = p[1]
    else:
        p[0] = {'tipo': 'seq_comandos', 'primeiro': p[1], 'resto': None}

def p_comando(p):
    '''
    comando : atribuicao
            | chamada_procedimento
            | condicional
            | repeticao
            | escrita
            | leitura
            | comando_composto
    '''
    p[0] = p[1]

def p_atribuicao(p):
    'atribuicao : IDENTIFICADOR ATRIB expressao'
    p[0] = {'tipo': 'cmd_atrib', 'id': {'tipo': 'id', 'nome': p[1]}, 'exp': p[3]}

def p_chamada_procedimento(p):
    'chamada_procedimento : IDENTIFICADOR PARE lista_expressoes_opt PARD'
    p[0] = {'tipo': 'chamada_proc', 'nome': p[1], 'args': p[3]}

def p_condicional(p):
    '''
    condicional : IF expressao THEN comando %prec THEN
                | IF expressao THEN comando ELSE comando
    '''
    if len(p) == 5:
        p[0] = {'tipo': 'cmd_condicional', 'condicao': p[2], 'corpo': p[4]}
    else:
        p[0] = {'tipo': 'cmd_condicional', 'condicao': p[2], 'corpo': p[4], 'senao': p[6]}

def p_repeticao(p):
    'repeticao : WHILE expressao DO comando'
    p[0] = {'tipo': 'cmd_repeticao', 'condicao': p[2], 'corpo': p[4]}

def p_escrita(p):
    'escrita : WRITE PARE lista_expressoes PARD'
    p[0] = {'tipo': 'cmd_escrita', 'expressoes': p[3]}

def p_leitura(p):
    'leitura : READ PARE lista_ids PARD'
    lista_id_nodes = [{'tipo': 'id', 'nome': id_nome} for id_nome in p[3]]
    p[0] = {'tipo': 'cmd_leitura', 'vars': lista_id_nodes}

def p_lista_expressoes_opt(p):
    '''
    lista_expressoes_opt : lista_expressoes
                         | empty
    '''
    p[0] = p[1] if p[1] else []

def p_lista_expressoes(p):
    '''
    lista_expressoes : lista_expressoes VIRG expressao
                     | expressao
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

# --- EXPRESSÕES ---
def p_expressao(p):
    '''
    expressao : expressao_simples relacao expressao_simples
              | expressao_simples
    '''
    if len(p) == 4:
        p[0] = {'tipo': 'exp_binaria', 'op': p[2], 'esq': p[1], 'dir': p[3]}
    else:
        p[0] = p[1]

def p_relacao(p):
    '''relacao : IGUAL 
                | DIF 
                | MENOR 
                | MENORIG 
                | MAIOR 
                | MAIORIG'''
    p[0] = p[1]

def p_expressao_simples(p):
    '''
    expressao_simples : expressao_simples MAIS termo
                      | expressao_simples MENOS termo
                      | expressao_simples OR termo
    '''
    p[0] = {'tipo': 'exp_binaria', 'op': p[2], 'esq': p[1], 'dir': p[3]}

def p_expressao_simples_termo(p):
    'expressao_simples : termo'
    p[0] = p[1]

def p_termo(p):
    '''
    termo : termo VEZES fator
          | termo DIV fator
          | termo AND fator
    '''
    p[0] = {'tipo': 'exp_binaria', 'op': p[2], 'esq': p[1], 'dir': p[3]}

def p_termo_fator(p):
    'termo : fator'
    p[0] = p[1]

def p_fator(p):
    '''
    fator : variavel
          | chamada_funcao
          | NUMERO
          | logico
          | PARE expressao PARD
          | NOT fator
          | MENOS fator %prec UMENOS
    '''
    if len(p) == 2:
        if isinstance(p[1], dict):
             p[0] = p[1]
        else: 
             p[0] = {'tipo': 'exp_num', 'valor': p[1]}
    elif len(p) == 3:
        p[0] = {'tipo': 'exp_unaria', 'op': p[1], 'exp': p[2]}
    else:
        p[0] = p[2]

def p_logico(p):
    '''
    logico : TRUE
           | FALSE
    '''
    p[0] = {'tipo': 'logico', 'valor': p[1]}

def p_variavel(p):
    'variavel : IDENTIFICADOR'
    p[0] = {'tipo': 'exp_var', 'id': {'tipo': 'id', 'nome': p[1]}}

def p_chamada_funcao(p):
    'chamada_funcao : IDENTIFICADOR PARE lista_expressoes_opt PARD'
    p[0] = {'tipo': 'chamada_func', 'nome': p[1], 'args': p[3]}

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"Erro de sintaxe no token '{p.value}' (tipo: {p.type}) na linha {p.lineno}")
    else:
        print("Erro de sintaxe: Fim inesperado do arquivo (EOF).")
    sys.exit(1)

parser = yacc.yacc(debug=True)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Como usar: python yacc.py caminho_do_arq_test.txt")
        sys.exit(1)

    arquivo_teste = sys.argv[1]
    nome_saida_ast = "ast.json"

    try:
        with open(arquivo_teste, "r") as f:
            codigo = f.read()
            
            ast_result = parser.parse(codigo)
            
            if ast_result:
                with open(nome_saida_ast, "w") as ast_file:
                    json.dump(ast_result, ast_file, indent=2, ensure_ascii=False)
                print(f"Análise sintática concluída com sucesso! AST salva em '{nome_saida_ast}'")
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo_teste}' não encontrado.")