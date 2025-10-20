from graphviz import Digraph
import json

class VisualizadorAST:
    def __init__(self, ast_data):
        self.ast = ast_data
        self.dot = Digraph('AST', comment='Árvore Sintática Abstrata')
        self.dot.attr('node', fontname='helvetica')
        self.dot.attr('edge', fontname='helvetica', fontsize='10')
        self.contador_nos = 0

    def gerar_id_no(self):
        self.contador_nos += 1
        return f'node{self.contador_nos}'

    def adicionar_no_e_filhos(self, no_atual):
        if not isinstance(no_atual, dict):
            id_no = self.gerar_id_no()
            self.dot.node(id_no, str(no_atual), shape='box', style='filled', fillcolor='sandybrown')
            return id_no

        # Nó interno
        id_no_atual = self.gerar_id_no()
        tipo_no = no_atual.get('tipo', 'desconhecido')
        self.dot.node(id_no_atual, tipo_no, shape='box', style='rounded,filled', fillcolor='skyblue')

        # Define a ordem desejada para os filhos aparecerem no gráfico
        ordem_chaves = ['esq', 'op', 'dir']
        
        chaves_restantes = [k for k in no_atual.keys() if k not in ordem_chaves and k != 'tipo']
        
        for chave in ordem_chaves + chaves_restantes:
            if chave not in no_atual:
                continue

            valor = no_atual[chave]
            
            if chave == 'op':
                # Desenha o operador como um nó folha terminal
                id_filho_op = self.gerar_id_no()
                self.dot.node(id_filho_op, str(valor), shape='box', style='filled', fillcolor='sandybrown')
                self.dot.edge(id_no_atual, id_filho_op, label=chave)
                continue

            if isinstance(valor, list):
                # Tratamento para listas (ex: lista de expressões)
                id_filho_lista = self.gerar_id_no()
                self.dot.node(id_filho_lista, f"lista_{chave}")
                self.dot.edge(id_no_atual, id_filho_lista, label=chave)
                for item in valor:
                     id_item = self.adicionar_no_e_filhos(item)
                     self.dot.edge(id_filho_lista, id_item)
            elif valor is not None:
                # Tratamento para filhos normais
                id_filho = self.adicionar_no_e_filhos(valor)
                self.dot.edge(id_no_atual, id_filho, label=chave)

        return id_no_atual

    def visualizar(self, nome_arquivo_saida='ast_visualizada'):
        if not self.ast:
            print("AST está vazia. Nada para visualizar.")
            return

        self.adicionar_no_e_filhos(self.ast)
        
        try:
            self.dot.render(nome_arquivo_saida, view=True, cleanup=True, format='png')
            print(f"Visualização da AST salva em '{nome_arquivo_saida}.png'")
        except Exception as e:
            print("\n--- ERRO AO GERAR A IMAGEM ---")
            print("Verifique se o Graphviz está instalado e configurado no PATH do seu sistema.")
            print(f"Detalhes do erro: {e}")

if __name__ == '__main__':

    arquivo_ast_json = "ast.json"

    try:
        with open(arquivo_ast_json, "r", encoding='utf-8') as f:
            dados_ast = json.load(f)
            visualizador = VisualizadorAST(dados_ast)
            visualizador.visualizar()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{arquivo_ast_json}' não encontrado.")
    except json.JSONDecodeError:
        print(f"Erro: O arquivo '{arquivo_ast_json}' não contém um JSON válido.")