import requests  # Para fazer requisições HTTP
from bs4 import BeautifulSoup  # Para extrair dados de páginas HTML
import sqlite3  # Para interagir com o banco de dados SQLite

def obter_dados_do_produto(link_anuncio):
    """
    Obtém dados de um produto específico a partir do link do anúncio no Mercado Livre.
    
    Args:
        link_anuncio (str): Link direto do anúncio.
    
    Returns:
        dict: Dicionário contendo os dados do produto (nome, preço e descrição).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    resposta = requests.get(link_anuncio, headers=headers)
    
    if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.content, "html.parser")
        dados_produto = {}
        
        # Obtendo o nome do produto
        tag_nome = soup.find("h1", class_="ui-pdp-title")
        dados_produto['nome'] = tag_nome.get_text(strip=True) if tag_nome else "Indisponível"
        
        # Obtendo o preço do produto
        tag_preco = soup.find("span", class_="andes-money-amount ui-pdp-price__part andes-money-amount--cents-superscript andes-money-amount--compact")
        dados_produto['preco'] = tag_preco.get_text(strip=True) if tag_preco else "Indisponível"
        
        # Obtendo a descrição do produto
        descricao_tag = soup.find("div", class_="ui-pdp-description")
        dados_produto['descricao'] = descricao_tag.get_text(separator='\n', strip=True) if descricao_tag else "Sem descrição"
        
        return dados_produto
    
    return None

def salvar_no_banco_de_dados(dados, nome_banco="produtos.db"):
    """
    Salva os dados do produto em um banco de dados SQLite.
    
    Args:
        dados (dict): Dicionário contendo os dados do produto.
        nome_banco (str): Nome do arquivo do banco de dados SQLite.
    """
    # Conecta ao banco de dados SQLite (cria o banco se ele não existir)
    conexao = sqlite3.connect(nome_banco)
    
    # Cria um cursor para executar comandos SQL
    cursor = conexao.cursor()
    
    # Cria a tabela 'produtos' se ela ainda não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco TEXT NOT NULL,
            descricao TEXT
        )
    ''')
    
    # Limpa a tabela (deleta todos os dados anteriores)
    cursor.execute('DELETE FROM produtos')
    
    # Insere os novos dados do produto
    cursor.execute('''
        INSERT INTO produtos (nome, preco, descricao) 
        VALUES (?, ?, ?)
    ''', (dados.get('nome', 'Indisponível'), dados.get('preco', 'Indisponível'), dados.get('descricao', 'Sem descrição')))
    
    # Confirma a transação no banco de dados (salva as alterações)
    conexao.commit()
    
    # Fecha a conexão com o banco de dados
    conexao.close()
    
    print(f"Dados do produto salvos com sucesso no banco de dados '{nome_banco}'.")

# Link do anúncio do produto no Mercado Livre
link_anuncio = "https://www.mercadolivre.com.br/pedra-para-afiar-faca-de-cozinha-gastronomia-15cm-churrasco/p/MLB26601783?pdp_filters=item_id:MLB3556220077#reco_item_pos=2&reco_backend=pads-retrieval-model-odin&reco_backend_type=low_level&reco_client=pdp-pads-right&reco_id=6af7caca-f378-4eee-8e7b-c53d5c2443ea&is_advertising=true&ad_domain=PDPDESKTOP_RIGHT&ad_position=3&ad_click_id=NGYzNmI1MDMtMTM3Yi00NDkzLTkxYjYtN2Y2YTU2YjhkZDg3"

# Obtém os dados do produto a partir do link
dados_produto = obter_dados_do_produto(link_anuncio)

# Verifica se os dados foram obtidos com sucesso
if dados_produto:
    # Salva os dados do produto no banco de dados
    salvar_no_banco_de_dados(dados_produto)
else:
    print("Nenhum dado encontrado.")
