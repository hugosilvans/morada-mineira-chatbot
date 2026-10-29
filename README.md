# Morada Mineira — Chatbot de Atendimento

Chatbot web desenvolvido em equipe pelo Squad 20 para apoiar o atendimento de uma confeitaria. O cliente pode consultar o cardápio, escolher produtos, montar um carrinho e abrir o WhatsApp com o pedido preenchido.

## Identidade visual

<img src="static/images/MimoBot.png" alt="Personagem MimoBot utilizado na interface" width="120">

[![Imagem de identidade da Morada Mineira utilizada no fundo da aplicação](static/images/MoradaMineira.png)](static/images/MoradaMineira.png)

As imagens acima são recursos visuais do projeto, não capturas de tela da aplicação.

## Problema e solução

O projeto busca agilizar a consulta de produtos e a montagem de pedidos. A interface de chat oferece opções guiadas e respostas pré-programadas, enquanto o backend organiza os dados em SQLite.

## Funcionalidades

- Consulta do cardápio por categoria
- Exibição de produtos mais vendidos
- Sugestões a partir de informações do evento
- Seleção de opções e quantidade dos produtos
- Inclusão e edição de itens no carrinho
- Finalização por link do WhatsApp com mensagem preenchida

A conversa utiliza regras e opções predefinidas. A finalização gera um link para o WhatsApp; não representa envio automático por uma API de mensagens.

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| Interface | HTML, CSS e JavaScript |
| Backend | Python e Flask |
| Dados | SQLite |
| Servidor WSGI | Gunicorn |

## Executar localmente

Clone o projeto:

```bash
git clone https://github.com/hugosilvans/SQUAD20-Morada-Mineira.git
cd SQUAD20-Morada-Mineira
python -m venv .venv
```

Ative o ambiente virtual no PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

No Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as versões declaradas em [requirements.txt](requirements.txt) e inicie:

```bash
python -m pip install -r requirements.txt
python app.py
```

Acesse [http://localhost:5000](http://localhost:5000). A execução direta de `app.py` chama `init_db()` antes de iniciar o servidor.

## Usar a interface

1. Abra **Menu** e selecione uma categoria.
2. Escolha um produto, suas opções e quantidade.
3. Confira os itens em **Carrinho**.
4. Finalize para abrir o link do WhatsApp e revisar a mensagem antes de enviar.

**Favoritos** apresenta categorias de mais vendidos; **Sugestões** solicita informações para orientar a escolha. O número de destino está configurado em `COMPANY_WHATSAPP_NUMBER`, no [app.py](app.py). Para testar, não envie pedidos reais.

## Estrutura

| Caminho | Responsabilidade |
| --- | --- |
| [app.py](app.py) | Rotas, regras do chatbot e acesso ao banco |
| [templates/index.html](templates/index.html) | Interface |
| [static/script.js](static/script.js) | Interações, menu e carrinho |
| [static/style.css](static/style.css) | Estilos |
| [static/images](static/images/) | Identidade visual e fotos dos produtos |
| [requirements.txt](requirements.txt) | Dependências utilizadas |
| [Procfile](Procfile) | Comando do servidor para hospedagem |

## Hospedagem

O comando WSGI é `gunicorn app:app`. A importação pelo Gunicorn não executa o bloco principal de `app.py`; em um ambiente novo, inicialize o banco antes de iniciar o servidor:

```bash
python -c "from app import init_db; init_db()"
gunicorn app:app
```

A hospedagem precisa oferecer armazenamento persistente para o SQLite. Antes de uso real, revise a chave de sessão, as configurações e as validações da aplicação.

## Equipe e créditos

Projeto coletivo do Squad 20. Hugo da Silva Nunes integra a equipe abaixo. Os créditos são mantidos em conjunto, sem atribuir funcionalidades individuais que não estejam documentadas.

### Integrantes
- Elise Akie Sugiyama;
- Felippe Cotrim da Silva;
- Heitor Alves Rebouças;
- Henrique Souto de Almeida;
- Hugo da Silva Nunes;
- João Gabriel Lucas Ferreira;
- Júlia Barros Ferraz;
- Marcio Antônio Freitas de Pinho;
- Marcus Vinícius Lima Cardoso Fagundes;

### Mentor

- Igor Santos

## Licença

[MIT](LICENSE).
