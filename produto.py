import requests
from bs4 import BeautifulSoup
import sqlite3 

def obter_dados_do_produto(link_anuncio):
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    resposta = requests.get(link_anuncio, headers=headers)
    
    if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.content, "html.parser")
        dados_produto = {}
        
        tag_nome = soup.find("h1", class_="ui-pdp-title")
        dados_produto['titulo'] = tag_nome.get_text(strip=True) if tag_nome else "Indisponível"
    
        tag_preco = soup.find("span", class_="andes-money-amount ui-pdp-price__part andes-money-amount--cents-superscript andes-money-amount--compact")
        dados_produto['preco'] = tag_preco.get_text(strip=True) if tag_preco else "Indisponível"
        
        descricao_tag = soup.find("div", class_="ui-pdp-description")
        dados_produto['descricao'] = descricao_tag.get_text(separator='\n', strip=True) if descricao_tag else "Sem descrição"
        
        return dados_produto
    
    return None

def salvar_no_banco_de_dados(dados, banco="produtos.db"):

    conexao = sqlite3.connect(banco)
    cursor = conexao.cursor()
    
    # Cria a tabela 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            preco TEXT NOT NULL,
            descricao TEXT
        )
    ''')
    
    cursor.execute('DELETE FROM produtos')
    
    # novos dados do produto
    cursor.execute('''
        INSERT INTO produtos (titulo, preco, descricao) 
        VALUES (?, ?, ?)
    ''', (dados.get('titulo', 'Indisponível'), dados.get('preco', 'Indisponível'), dados.get('descricao', 'Sem descrição')))
    
    conexao.commit()
    conexao.close()
    
    print(f"Dados do produto salvos com sucesso no banco de dados '{banco}'.")

def main():
    link_anuncio = "https://produto.mercadolivre.com.br/MLB-2223878983-conversores-midia-gigabit-1000-mb-par-a-b-fibra-optica-_JM"

    dados_produto = obter_dados_do_produto(link_anuncio)

    # Dados foram obtidos com sucesso
    if dados_produto:
        salvar_no_banco_de_dados(dados_produto)
    else:
        print("Nenhum dado encontrado.")
