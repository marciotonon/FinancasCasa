# FinancasCasa

Sistema web simples para controle financeiro domestico, feito com Flask e persistencia em arquivo JSON.

## Visao geral

O FinancasCasa permite registrar entradas e saidas, controlar contas a pagar, baixar contas pendentes e acompanhar relatorios mensais. Os dados sao gravados localmente no arquivo `data.json`, sem banco de dados.

## Funcionalidades

- Dashboard com resumo de entradas, saidas, saldo atual e contas pendentes
- Cadastro de transacoes de entrada e saida
- Filtros de transacoes por tipo, mes e categoria
- Agrupamento de transacoes por mes com totais de entrada, saida e saldo mensal
- Cadastro de contas a pagar
- Filtros de contas por status e mes
- Agrupamento de contas por mes de vencimento
- Baixa de conta com geracao automatica de transacao de saida
- Relatorios por mes e por categoria

## Tecnologias

- Python
- Flask
- HTML com templates Jinja2
- CSS e JavaScript puros
- JSON para armazenamento local

## Requisitos

- Python 3 instalado
- `pip` habilitado

## Instalacao

No diretorio do projeto, execute:

```bash
pip install -r requirements.txt
```

## Como executar

### Opcao 1: pelo terminal

```bash
python app.py
```

Depois acesse:

```text
http://127.0.0.1:5000
```

### Opcao 2: pelo arquivo BAT

No Windows, tambem e possivel iniciar pelo arquivo:

```text
Iniciar_FinancasCasa.bat
```

## Git e sincronizacao

O projeto agora esta conectado ao repositorio remoto abaixo:

```text
https://github.com/marciotonon/FinancasCasa.git
```

Arquivos auxiliares criados no projeto:

- `Git_Pull.bat`: faz `pull --rebase --autostash` da branch `main`
- `Git_Push.bat`: faz `add`, `commit`, `pull --rebase --autostash` e `push` para a `main`

Exemplos de uso:

```text
Git_Pull.bat
```

```text
Git_Push.bat "ajusta filtros de contas"
```

Observacao: o GitHub pode pedir autenticacao na primeira operacao de push ou pull, dependendo da sua sessao local.

## Estrutura do projeto

```text
.
|-- app.py
|-- data.json
|-- requirements.txt
|-- Iniciar_FinancasCasa.bat
|-- static/
|   |-- app.js
|   `-- style.css
`-- templates/
    |-- base.html
    |-- index.html
    |-- transacoes.html
    |-- contas.html
    |-- relatorios.html
    |-- form_transacao.html
    `-- form_conta.html
```

## Como os dados sao armazenados

O sistema utiliza o arquivo `data.json` com tres blocos principais:

- `transacoes`: lista de entradas e saidas
- `contas`: lista de contas a pagar
- `categorias`: categorias disponiveis para uso no sistema

Exemplos de campos:

- Transacao: `id`, `descricao`, `valor`, `tipo`, `categoria`, `data`, `observacao`
- Conta: `id`, `descricao`, `valor`, `vencimento`, `categoria`, `status`, `observacao`, `recorrente`

## Fluxo principal

1. Cadastre uma transacao de entrada, como salario.
2. Cadastre contas a pagar com vencimento e categoria.
3. Quando uma conta for paga, use a acao de baixa.
4. O sistema cria automaticamente uma transacao de saida correspondente.
5. Consulte a tela de transacoes e a tela de relatorios para acompanhar os totais por mes.

## Observacoes

- O sistema usa o servidor de desenvolvimento do Flask.
- Os dados ficam locais no arquivo `data.json`.
- Se o arquivo `data.json` nao existir, o sistema cria a estrutura inicial em memoria ao iniciar.

## Melhorias futuras

- Edicao de transacoes e contas
- Autenticacao de usuario
- Backup automatico do arquivo de dados
- Exportacao para Excel ou CSV
- Uso de banco de dados em vez de JSON
