# Agente Upwork: instalação (uma vez só)

**Fluxo:** captador (Haiku) → juiz (Sonnet) → redator (Opus high, um contexto novo por proposta) → e-mail pedindo aprovação → sua resposta `APROVO` → envio pelo Chrome → e-mail de confirmação.

1. **Atualize o repositório no seu computador:**
   ```bash
   git fetch origin claude/wizardly-mendel-a5bcpm && git checkout claude/wizardly-mendel-a5bcpm
   ```
2. **Crie a configuração local.** Copie `config.exemplo.md` para `config.local.md`, nesta mesma pasta, e preencha. Esse arquivo nunca vai para o git.
3. **Conecte as ferramentas no Claude desktop:** o Gmail (conector do claude.ai) e o Claude in Chrome, com o Chrome logado no Upwork.
4. **Publique o portfólio no perfil do Upwork:** imagens + título + descrição. Faça isso uma vez, à mão ou pedindo ao Claude no desktop.
5. **Primeiro teste:** abra o Claude desktop na pasta do repositório e rode `/upwork-ciclo`. Confira o e-mail `[Upwork aprovar]` que chegar.
6. **Deixe automático:** no Claude desktop, crie uma tarefa agendada nesta pasta com o prompt `/upwork-ciclo`, 2 vezes ao dia. Use Sonnet como modelo da tarefa, porque os subagentes já escolhem o modelo deles. O computador precisa estar ligado, com o Chrome aberto.

**Controles:**
- **Aprovar:** responda `APROVO` ao e-mail. Para mudar o texto, escreva `APROVO` e cole a versão editada logo abaixo.
- **Descartar:** responda `NÃO`.
- **Pausa:** chega um e-mail `[Upwork pausado]` e a automação para. Para retomar, responda `RETOMAR`.
- **Limites:** ficam no config, em `limite_connects_semana`, `max_propostas_dia` e `max_envios_execucao`.
