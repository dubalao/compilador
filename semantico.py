import sys
import json

class TabelaSimbolos:
    def __init__(self):
        self.escopos = []
        self.entrar_escopo() 
        # Instala tipos primitivos
        self.definir('integer', 'tipo', None)
        self.definir('boolean', 'tipo', None)
        self.definir('true', 'const', 'boolean')
        self.definir('false', 'const', 'boolean')

    def entrar_escopo(self):
        self.escopos.append({})

    def sair_escopo(self):
        self.escopos.pop()

    def definir(self, nome, categoria, tipo, params=None):
        escopo_atual = self.escopos[-1]
        if nome in escopo_atual:
            return False
        escopo_atual[nome] = {'categoria': categoria, 'tipo': tipo, 'params': params}
        return True

    def buscar(self, nome):
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        return None

class AnalisadorSemantico:
    def __init__(self):
        self.tabela = TabelaSimbolos()
        self.erros = []
        self.funcao_atual = None # Para verificar retorno de função

    def erro(self, msg):
        self.erros.append(f"Erro Semântico: {msg}")

    def visitar(self, no):
        if not no: return
        
        # Visita cada nó da lista
        if isinstance(no, list):
            for n in no:
                self.visitar(n)
            return

        if not isinstance(no, dict): 
            return
        
        metodo_nome = f"visitar_{no['tipo']}"
        visitante = getattr(self, metodo_nome, self.visitar_generico)
        return visitante(no)

    def visitar_generico(self, no):
        pass # Ignora nós desconhecidos ou sem tratamento específico

    # --- PROGRAMA E BLOCOS ---
    def visitar_programa(self, no):
        self.tabela.definir(no['nome'], 'programa', None) # O identificador do programa deve ser instalado na tabela de símbolos na categoria "programa".
        self.visitar(no['corpo']) # Visita o bloco principal

    def visitar_bloco(self, no):
        # Visita declarações de variáveis
        if 'vars' in no and no['vars']:
            self.visitar_decl_vars(no['vars'])
        
        # Visita sub-rotinas
        if 'subrotinas' in no and no['subrotinas']:
            for sub in no['subrotinas']:
                self.visitar(sub)
        
        # Visita comandos
        if 'comandos' in no:
            self.visitar(no['comandos'])

    # --- DECLARAÇÕES ---
    def visitar_decl_vars(self, lista_decls):
        for decl in lista_decls:
            nome = decl['id']['nome']
            tipo = decl['tipo_var']
            # Verifica redeclaração
            if not self.tabela.definir(nome, 'var', tipo):
                self.erro(f"Variável '{nome}' já declarada neste escopo.")

    def visitar_decl_proc(self, no):
        nome = no['nome']
        params = no['params'] # Lista de parâmetros
        
        # Extrai tipos dos parâmetros para assinatura
        tipos_params = [p['tipo_var'] for p in params]
        
        # Instala procedimento no escopo atual (antes de entrar no novo)
        if not self.tabela.definir(nome, 'proc', None, params=tipos_params):
             self.erro(f"Procedimento '{nome}' já declarado.")

        # Novo escopo para a sub-rotina
        self.tabela.entrar_escopo()
        
        # Instala parâmetros como variáveis locais
        for p in params:
            p_nome = p['id']['nome']
            p_tipo = p['tipo_var']
            self.tabela.definir(p_nome, 'param', p_tipo)

        self.visitar(no['corpo'])
        self.tabela.sair_escopo()

    def visitar_decl_func(self, no):
        nome = no['nome']
        tipo_retorno = no['retorno']
        params = no['params']
        tipos_params = [p['tipo_var'] for p in params]

        if not self.tabela.definir(nome, 'func', tipo_retorno, params=tipos_params):
            self.erro(f"Função '{nome}' já declarada.")

        self.tabela.entrar_escopo()
        
        self.funcao_atual = {'nome': nome, 'tipo': tipo_retorno}
        
        for p in params:
            self.tabela.definir(p['id']['nome'], 'param', p['tipo_var'])
            
        self.visitar(no['corpo'])
        
        self.funcao_atual = None
        self.tabela.sair_escopo()

    # --- COMANDOS ---
    def visitar_seq_comandos(self, no):
        if no['primeiro']:
            self.visitar(no['primeiro'])
        if no['resto']:
            self.visitar(no['resto'])

    def visitar_cmd_atrib(self, no):
        nome = no['id']['nome']
        tipo_exp = self.visitar(no['exp']) # Avalia expressão
        
        info = self.tabela.buscar(nome)
        
        # Verifica se é variável declarada
        if info:
            if info['categoria'] not in ['var', 'param']:
                 # Caso especial: Retorno de função 
                 if self.funcao_atual and self.funcao_atual['nome'] == nome:
                     tipo_variavel = self.funcao_atual['tipo']
                 else:
                    self.erro(f"Atribuição inválida para '{nome}'. Não é uma variável.")
                    return
            else:
                tipo_variavel = info['tipo']
                
            # Verifica compatibilidade de tipos
            if tipo_variavel != tipo_exp:
                self.erro(f"Tipos incompatíveis na atribuição para '{nome}'. Esperado {tipo_variavel}, encontrado {tipo_exp}.")
        else:
            # Verifica se é atribuição de retorno de função (nome da função) dentro dela mesma
            if self.funcao_atual and self.funcao_atual['nome'] == nome:
                 if self.funcao_atual['tipo'] != tipo_exp:
                     self.erro(f"Tipo de retorno incorreto para função '{nome}'.")
            else:
                self.erro(f"Identificador '{nome}' não declarado.")

    def visitar_cmd_condicional(self, no):
        tipo_cond = self.visitar(no['condicao'])
        # Condição deve ser booleana
        if tipo_cond != 'boolean':
            self.erro("Condição do 'if' deve ser boolean.")
        self.visitar(no['corpo'])
        if 'senao' in no:
            self.visitar(no['senao'])

    def visitar_cmd_repeticao(self, no):
        tipo_cond = self.visitar(no['condicao'])
        if tipo_cond != 'boolean':
            self.erro("Condição do 'while' deve ser boolean.")
        self.visitar(no['corpo'])

    def visitar_chamada_proc(self, no):
        nome = no['nome']
        args = no['args'] # Lista de expressões
        info = self.tabela.buscar(nome)
        
        # Procedimento deve estar declarado
        if not info or info['categoria'] != 'proc':
            self.erro(f"Procedimento '{nome}' não declarado.")
            return

        params_formais = info['params']
        # Número de argumentos
        if len(args) != len(params_formais):
            self.erro(f"Chamada '{nome}' esperava {len(params_formais)} argumentos, recebeu {len(args)}.")
            return

        # Tipos dos argumentos
        for i, arg_exp in enumerate(args):
            tipo_arg = self.visitar(arg_exp)
            if tipo_arg != params_formais[i]:
                self.erro(f"Argumento {i+1} de '{nome}' incompatível. Esperado {params_formais[i]}, encontrado {tipo_arg}.")

    def visitar_cmd_leitura(self, no):
        # Argumentos devem ser variáveis visíveis
        for var_node in no['vars']:
            nome = var_node['nome']
            info = self.tabela.buscar(nome)
            if not info or info['categoria'] not in ['var', 'param']:
                self.erro(f"Variável '{nome}' não declarada para leitura.")

    def visitar_cmd_escrita(self, no):
        # Argumentos expressões válidas
        for exp in no['expressoes']:
            self.visitar(exp)

    # --- EXPRESSÕES (Retornam o tipo) ---
    def visitar_exp_binaria(self, no):
        esq = self.visitar(no['esq'])
        dir = self.visitar(no['dir'])
        op = no['op']
        
        # Aritmética
        if op in ['+', '-', '*', 'div']:
            if esq == 'integer' and dir == 'integer':
                return 'integer'
            else:
                self.erro(f"Operação '{op}' requer inteiros.")
                return 'integer'
        
        # Relacional
        if op in ['<', '<=', '>', '>=']:
            if esq == 'integer' and dir == 'integer':
                return 'boolean'
            else:
                self.erro(f"Operador relacional '{op}' requer operandos inteiros.")
                return 'boolean'

        # (des)Igualdade
        if op in ['=', '<>']:
            if esq == dir:
                return 'boolean'
            else:
                self.erro(f"Operador '{op}' requer operandos do mesmo tipo.")
                return 'boolean'

        # Lógica
        if op in ['and', 'or']:
            if esq == 'boolean' and dir == 'boolean':
                return 'boolean'
            else:
                self.erro(f"Operação '{op}' requer booleanos.")
                return 'boolean'

    def visitar_exp_num(self, no):
        return 'integer'

    def visitar_logico(self, no):
        return 'boolean'

    def visitar_exp_var(self, no):
        nome = no['id']['nome']
        info = self.tabela.buscar(nome)
        if not info:
            self.erro(f"Variável '{nome}' não declarada.")
            return 'integer' # dummy
        return info['tipo']

    def visitar_chamada_func(self, no):
        # Análise análoga a chamada de procedimento
        nome = no['nome']
        args = no['args']
        info = self.tabela.buscar(nome)
        
        if not info:
            self.erro(f"Função '{nome}' não declarada.")
            return 'integer'

        if info['categoria'] != 'func':
            self.erro(f"Uso inválido do procedimento '{nome}' em uma expressão. Procedimentos não retornam valor.")
            return 'integer'

        if not info or info['categoria'] != 'func':
            self.erro(f"Função '{nome}' não declarada.")
            return 'integer'

        params_formais = info['params']
        if len(args) != len(params_formais):
            self.erro(f"Função '{nome}' esperava {len(params_formais)} argumentos.")
            return info['tipo']

        for i, arg_exp in enumerate(args):
            tipo_arg = self.visitar(arg_exp)
            if tipo_arg != params_formais[i]:
                self.erro(f"Argumento {i+1} de '{nome}' incompatível.")
        
        return info['tipo']

    def visitar_exp_unaria(self, no):
        tipo = self.visitar(no['exp'])
        op = no['op']
        if op == 'not':
            if tipo != 'boolean': self.erro("'not' requer boolean.")
            return 'boolean'
        if op == '-':
            if tipo != 'integer': self.erro("'-' unário requer integer.")
            return 'integer'

# Main
if __name__ == '__main__':
    try:
        with open("ast.json", "r") as f:
            ast = json.load(f)
        
        analisador = AnalisadorSemantico()
        analisador.visitar(ast)
        
        if analisador.erros:
            for e in analisador.erros:
                print(e)
        else:
            print("Análise Semântica concluída com sucesso! Nenhum erro encontrado.")
            
    except FileNotFoundError:
        print("Arquivo ast.json não encontrado. Execute o yacc.py primeiro.")