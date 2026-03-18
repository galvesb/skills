Faça um code review detalhado do código fornecido ou dos arquivos modificados (`git diff`).

**Avalie:**
1. **Bugs** — erros lógicos, edge cases não tratados, race conditions
2. **Segurança** — injeção, exposição de dados, validação de inputs
3. **Performance** — queries N+1, loops desnecessários, memória
4. **Legibilidade** — nomes claros, funções pequenas, comentários onde necessário
5. **Padrões** — consistência com o restante do projeto

**Formato da resposta:**
- Liste os problemas por prioridade (🔴 crítico, 🟡 melhoria, 🟢 sugestão)
- Para cada item: o que está errado, por quê é problema e como corrigir
- Ao final, um resumo geral com nota de 1 a 10
