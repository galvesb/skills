# CLAUDE.md

Repositório de skills para Claude Code, distribuído via CLI Python.

## Estrutura

```
skills/
├── gui_skill/        ← CLI Python (pacote publicável via pip)
│   ├── __init__.py
│   └── cli.py
├── dev/              ← Skills de desenvolvimento
├── produtos/         ← Skills de produto
└── pyproject.toml
```

## Como adicionar uma nova skill

1. Crie ou escolha uma pasta de categoria (ex: `design/`, `dados/`)
2. Adicione um arquivo `.md` com as instruções da skill
3. Faça commit e push — a CLI busca direto do GitHub

## Como adicionar uma nova categoria

Basta criar uma nova pasta na raiz do repositório com arquivos `.md` dentro.
A CLI detecta automaticamente via GitHub API.

## Desenvolvimento da CLI

```bash
# Instalar em modo editável
pip install -e .

# Testar localmente
gui-skill list
gui-skill install dev
```

## Publicação

```bash
# Instalar do GitHub
pip install git+https://github.com/galvesb/skills

# Atualizar
pip install --upgrade git+https://github.com/galvesb/skills
```

## Configuração do repositório

O repo está hardcoded em `gui_skill/cli.py`:
```python
GITHUB_REPO = "galvesb/skills"
GITHUB_BRANCH = "main"
```
