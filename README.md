# gui-skill

Gerenciador de skills para Claude Code. Instale coleções de slash commands diretamente no seu projeto com um único comando.

As instruções reais das skills ficam em um **repositório privado** e são injetadas em tempo real via hook — o desenvolvedor usa a skill normalmente, mas nunca vê o conteúdo do prompt.

## Como funciona

```
Dev digita /commit
      ↓
Claude Code lê o stub local (apenas um marcador)
      ↓
Hook intercepta → busca prompt real no GitHub privado
      ↓
Claude recebe as instruções e executa
```

O dev vê apenas o marcador no arquivo local (`{{PRIVATE:dev/commit}}`), nunca o prompt real.

---

## Instalação

```bash
pip install git+https://github.com/galvesb/skills
```

---

## Configuração (uma vez por máquina)

Adicione ao seu `~/.bashrc` ou `~/.zshrc`:

```bash
export SKILLS_GITHUB_TOKEN=ghp_seu_token_aqui
export SKILLS_PRIVATE_REPO=sua-org/skills-private
```

O token precisa ter permissão de leitura (`contents: read`) no repositório privado.

---

## Uso

### Listar categorias disponíveis

```bash
gui-skill list
```

```
Categorias disponíveis:
  • dev
  • produtos
```

### Instalar skills de uma categoria

```bash
gui-skill install dev
```

```
Buscando skills de 'dev'...
  ✓ commit.md instalado
  ✓ code-review.md instalado
  ✓ hook configurado

2 skill(s) instalada(s) em .claude/commands/
```

### Atualizar skills já instaladas

```bash
gui-skill install dev
```

```
  ✓ commit.md atualizado
  ✓ code-review.md atualizado
  ✓ hook configurado
```

---

## Skills disponíveis

### `dev`

| Skill | Comando |
|---|---|
| `commit` | `/commit` |
| `code-review` | `/code-review` |

### `produtos`

| Skill | Comando |
|---|---|
| `prd` | `/prd` |

---

## Como usar as skills no Claude Code

Após instalar, abra o Claude Code no projeto e use `/` para ver os comandos:

```
/commit        → cria um commit
/code-review   → revisa o código
/prd           → escreve um PRD
```

---

## Repositório privado (para quem mantém as skills)

As instruções reais ficam em um repositório privado com a mesma estrutura de pastas:

```
skills-private/
├── dev/
│   ├── commit.md        ← instruções reais do /commit
│   └── code-review.md
└── produtos/
    └── prd.md
```

O repositório público (`galvesb/skills`) contém apenas os stubs com marcadores.
O repositório privado (`sua-org/skills-private`) contém os prompts reais.

### Adicionar uma nova skill

**No repo público** — crie o stub:
```
dev/minha-skill.md
```
```
{{PRIVATE:dev/minha-skill}}
```

**No repo privado** — crie o prompt real:
```
dev/minha-skill.md
```
```markdown
Analise o código e sugira melhorias de performance...
```

Faça push nos dois repos — a skill aparece automaticamente no `gui-skill list`.
