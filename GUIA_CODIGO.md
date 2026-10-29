# Guia de leitura do código

Este guia descreve a organização para estudar e explicar o repositório. Os comentários do código destacam regras, contratos, validações e responsabilidade pela memória ou pelos dados.

## Por onde começar

| Caminho | Responsabilidade |
| --- | --- |
| [app.py](app.py) | Rotas e validações do carrinho associado à sessão. |
| [database.py](database.py) | Conexão e inicialização do SQLite. |
| [seed_data.py](seed_data.py) | Cardápio de demonstração. |
| [static/script.js](static/script.js) | Interação, opções, carrinho e resumo como texto. |
| [test_app.py](test_app.py) | Testes HTTP com SQLite temporário. |

## Como estudar uma alteração

1. Identifique a entrada: argumento, formulário ou requisição HTTP.
2. Localize a validação e a função que transforma os dados.
3. Observe a saída e o comportamento quando algo falha.
4. Execute um exemplo pequeno antes de mudar a regra.
5. Consulte o diff do Git para distinguir formatação de mudanças de comportamento.

## Convenções

- `.editorconfig` define codificação, indentação e final de linha.
- Comentários explicam motivos e restrições; não repetem cada comando.
- Arquivos gerados, dependências e credenciais locais ficam fora do versionamento.
- Um `main` pertence ao seu exercício; projetos de aula independentes não formam um único executável.
- Créditos, autoria anterior e licenças são preservados.
- `.prettierrc.json` registra a formatação dos arquivos web.

## Inventário de fontes próprias e didáticas

1 arquivo(s) `.css`, 1 arquivo(s) `.html`, 1 arquivo(s) `.js`, 4 arquivo(s) `.py`.

## Limite desta organização

A formatação e os comentários não comprovam que todos os exercícios estejam completos. Os testes adicionados cobrem os fluxos descritos no README; validar sintaxe não equivale a testar todos os resultados. Veja também as instruções e limitações específicas do projeto.
