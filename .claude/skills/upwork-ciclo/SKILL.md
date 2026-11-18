---
name: upwork-ciclo
description: "/upwork-ciclo - Ciclo automático do Upwork: envia as propostas já aprovadas, capta vagas (Haiku), julga (Sonnet), redige cada proposta num contexto novo (Opus high) e pede aprovação por e-mail. Roda no Claude desktop com o Claude in Chrome logado. Triggers on: /upwork-ciclo, ciclo upwork, propostas upwork"
---

# /upwork-ciclo

Rode no Claude desktop, na pasta deste repositório, com o Chrome aberto e logado no Upwork e o Gmail conectado. Pode ser à mão ou por tarefa agendada, 2 vezes ao dia. **Leia `regras.md` antes de tudo.** Seja breve: este ciclo existe para gastar pouco.

## 0. Preparação (barata, sem navegador)
1. **Config:** leia `.claude/skills/upwork-ciclo/config.local.md`. Se ele não existir, pare e diga ao usuário para copiar `config.exemplo.md`.
2. **Etiquetas:** garanta que existem no Gmail `Upwork/Aguardando`, `Upwork/Enviada`, `Upwork/Recusada`, `Upwork/Expirada` e `Upwork/Pausado`. Crie só as que faltarem.
3. **Pausa:** se existir uma thread em `label:Upwork-Pausado` cuja última mensagem do usuário não diga `RETOMAR`, **pare** sem fazer nada.
4. **Connects:**
   - `enviados_7d`: some o número N dos assuntos `[Upwork enviada] N Connects | …` em `label:Upwork-Enviada newer_than:7d`.
   - `reservados`: some os Connects das threads em `label:Upwork-Aguardando`.
   - `connects_restantes = limite_connects_semana − enviados_7d − reservados`
5. **Vagas do dia:** `vagas_permitidas = max_propostas_dia − (pedidos [Upwork aprovar] enviados hoje)`.

## 1. Envios aprovados
Execute `.claude/skills/upwork-enviar/SKILL.md`. Depois disso, recalcule `connects_restantes`.

## 2. Perfil base (só se `## perfil_base` estiver vazio)
Despache `upwork-juiz` no modo `"perfil"` e grave o JSON retornado em `## perfil_base` do config.local.md. Se `## portfolio` estiver vazio, preencha com os títulos de portfólio que o juiz leu.

## 3. Captação
Se `vagas_permitidas ≤ 0` ou `connects_restantes < 4`, encerre aqui com uma linha de resumo.

Junte os IDs já vistos: os `id:~0…` que aparecem nos e-mails `label:Upwork-* newer_than:30d`. Despache `upwork-captador` com `palavras_chave`, `excluir`, `buscas_salvas` e os IDs vistos.

Se o retorno tiver `pausar`, vá para **Pausa**. Se vier vazio, encerre.

## 4. Julgamento
Despache `upwork-juiz` no modo `"vagas"`, com os candidatos, o `perfil_base`, o `score_minimo`, os `connects_restantes` e as `vagas_permitidas`.

Se nada passar, encerre com uma linha de resumo. Não mande e-mail quando não houver vaga.

## 5. Redação: um `upwork-redator` por vaga, cada um num Agent novo
Para cada vaga aprovada, despache **um** `upwork-redator` separado, passando só aquela vaga, o `perfil_base` e o `portfolio`. Não reaproveite contexto entre vagas.

## 6. Pedido de aprovação, um e-mail por vaga
Envie para `email_notificacao`:
- **Assunto:** `[Upwork aprovar] <título> | <connects> Connects | score <s>`
- **Corpo em texto puro:**
  - link da vaga e `id:<~0…>`
  - motivo
  - orçamento e lance
  - prazo
  - a carta inteira
  - as respostas de triagem
  - a linha: *"Responda APROVO para enviar exatamente este texto, ou APROVO seguido do texto editado, ou NÃO para descartar. Vale por <aprovacao_valida_horas>h."*

Aplique a etiqueta `Upwork/Aguardando`. Some os Connects da vaga em `reservados`.

## Pausa
Envie um e-mail para `email_notificacao`:
- **Assunto:** `[Upwork pausado] <motivo>`
- **Corpo:** o que aconteceu, e que a automação só volta quando o usuário responder `RETOMAR`.

Aplique a etiqueta `Upwork/Pausado` e encerre.

## Fim
Responda com uma linha: `enviadas X | aprovar Y | descartadas Z | connects restantes R`.
