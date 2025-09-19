import ply.lex as lex

# Dicionário de palavras reservadas.
reserved = {
    'program': 'PROGRAM',
    'var': 'VAR',
    'procedure': 'PROCEDURE',
    'function': 'FUNCTION',
    'begin': 'BEGIN',
    'end': 'END',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'while': 'WHILE',
    'do': 'DO',
    'read': 'READ',
    'write': 'WRITE',
    'div': 'DIV',
    'or': 'OR',
    'and': 'AND',
    'not': 'NOT',
    'true': 'TRUE',
    'false': 'FALSE'
}

tokens = [
    'IDENTIFICADOR',
    'NUMERO',
    'MAIS', 'MENOS', 'VEZES', 'ATRIB',
    'IGUAL', 'DIF', 'MENOR', 'MENORIG', 'MAIOR', 'MAIORIG',
    'PARE', 'PARD', 'PONTOV', 'PONTO', 'VIRG', 'DOISP'
] + list(reserved.values())

# Expressões Regulares para tokens simples (operadores e delimitadores)
t_MAIS      = r'\+'
t_MENOS     = r'-'
t_VEZES     = r'\*'
t_ATRIB     = r':='
t_IGUAL     = r'='
t_DIF       = r'<>'
t_MENOR     = r'<'
t_MENORIG   = r'<='
t_MAIOR     = r'>'
t_MAIORIG   = r'>='
t_PARE      = r'\('
t_PARD      = r'\)'
t_PONTOV    = r';'
t_PONTO     = r'\.'
t_VIRG      = r','
t_DOISP     = r':'

# Regra para ignorar comentários
def t_COMMENT(t):
    r'(\{(.|\n)*?\})|(\(\*(.|\n)*?\*\))'
    t.lexer.lineno += t.value.count('\n')
    pass 

# Regra garante que um identificador comece com uma letra
def t_IDENTIFICADOR_INVALIDO(t):
    r'\d+[a-zA-Z][a-zA-Z_0-9]*'
    print(f"Erro Léxico na Linha {t.lexer.lineno}: Identificador inválido '{t.value}' não pode começar com um número.")
    t.lexer.skip(len(t.value))

# Regra garante que um identificador comece com uma letra
def t_IDENTIFICADOR(t):
    r'[a-zA-Z][a-zA-Z_0-9]*'

    t.type = reserved.get(t.value, 'IDENTIFICADOR')
    return t

# Regra reconhece um ou mais numeros.
def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Regra para contar o número de linhas.
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignora espaços e tabs.
t_ignore = ' \t'

# Tratamento de erros.
def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' encontrado na linha {t.lexer.lineno}")
    # Pula o caractere ilegal para continuar a análise.
    t.lexer.skip(1)

lexer = lex.lex()

if __name__ == '__main__':
    test_code = """
program Fatorial;
var
   numero, resultado, integer: integer;
   finalizado : boolean;
   1arvore : integer;

begin
   read(numero);
   resultado := 1;
   while numero > 0 do
   begin {meu ammigo}
      resultado := {oce ta bao}resultado * numero;
      numero := numero {*tao ta bao*}- 1
   end;
   write(resultado, 2<>3, true)
end.
"""
    test_code2 = """
    program testeCompleto;

var
    a, b, resultado: integer;
    flag: boolean;

procedure meuProcedimento(x: integer; y: boolean);
begin
    write(x, y);
end;

function minhaFuncao(x: integer): integer;
begin
    x := x + 1;
    minhaFuncao := x;
end;

begin
    read(a, b);
    flag := true;

    if a < b then
        resultado := a * 2 + b div 3;
    else
        resultado := a - b;

    while resultado > 0 do
        resultado := resultado - 1;

    write(resultado, flag, a <> b, a <= b, a >= b, a = b, not flag, -a);

    meuProcedimento(a, false);
    resultado := minhaFuncao(a)
end.
"""
    
    lexer.input(test_code2)

    print("--- Análise Léxica ---")
    while True:
        tok = lexer.token()
        if not tok:
            break  # Fim dos tokens
        print(f"({tok.type}, {tok.value} )")
    print("--- Fim da Análise ---")
