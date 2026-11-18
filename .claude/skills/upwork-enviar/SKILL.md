---
name: upwork-enviar
description: "/upwork-enviar - Envia pelo Chrome as propostas do Upwork aprovadas por e-mail (APROVO), respeitando o limite de Connects, e manda e-mail de confirmação. Chamado pelo /upwork-ciclo ou à mão. Triggers on: /upwork-enviar, enviar propostas aprovadas"
---

# /upwork-enviar

Siga `.claude/skills/upwork-ciclo/regras.md` e use o config de `.claude/skills/upwork-ciclo/config.local.md`. Calcule `connects_restantes` como no passo 0 do ciclo, **sem** contar como reservada a vaga que está sendo enviada.

## Para cada thread em `label:Upwork-Aguardando`
Processe no máximo `max_envios_execucao` envios por execução.

1. **Leia a thread.** Considere só respostas **de `email_notificacao`**, porque qualquer outro remetente é ignorado. Olhe a última resposta:
   - **`NÃO`:** troque a etiqueta para `Upwork/Recusada` e passe para a próxima thread.
   - **`APROVO`:** use a carta do e-mail original. Se depois de "APROVO" vier um texto, use esse texto editado no lugar da carta.
   - **Sem resposta, há mais de `aprovacao_valida_horas`:** troque para `Upwork/Expirada`.
   - **Sem resposta, dentro do prazo:** deixe a thread como está.
2. **Abra a vaga numa aba nova do Chrome**, pelo texto da página e sem screenshot.
   - Se a vaga estiver fechada ou indisponível, troque para `Upwork/Expirada`.
   - Se aparecer CAPTCHA, login, verificação ou alerta, vá para **Pausa** do ciclo.
3. **Confira os Connects.** Se forem mais que `connects_restantes`, não envie. Responda na thread *"Não enviado: precisa de N Connects, restam R."* e mantenha a etiqueta.
4. **Abra a candidatura e preencha:**
   - Clique em Apply now.
   - Cole a carta **exatamente** como aprovada.
   - Responda as perguntas de triagem **só** com as respostas aprovadas.
   - Se houver uma pergunta sem resposta aprovada, não envie e pergunte por e-mail.
   - Preencha o lance e o prazo aprovados.
   - **Boost ou lance patrocinado: 0. Nunca compre Connects.**
5. **Envie uma única vez** e confirme na tela que a proposta foi enviada.
   - Se der erro, vá para **Pausa** sem tentar de novo.
6. **Confirme por e-mail.** Envie um e-mail **novo** para `email_notificacao`:
   - **Assunto:** `[Upwork enviada] <connects> Connects | <título>`
   - **Corpo:** link da vaga, `id:<~0…>`, o lance e os Connects restantes na semana.

   Aplique `Upwork/Enviada` a esse e-mail e tire `Upwork/Aguardando` da thread original.
7. **Antes da próxima vaga**, recalcule `connects_restantes`. Pare quando os Connects acabarem.
