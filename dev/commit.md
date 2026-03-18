Analise as mudanças staged com `git diff --staged` e crie um commit seguindo **Conventional Commits**:

**Formato:** `<tipo>(<escopo opcional>): <descrição curta>`

**Tipos:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Regras:**
- Descrição em português, imperativo, sem ponto final
- Se houver breaking change, adicione `!` após o tipo
- Rode `git status` antes para confirmar o que está staged

Após criar o commit, exiba o hash e a mensagem para confirmação.
