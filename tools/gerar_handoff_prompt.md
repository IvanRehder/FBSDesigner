Você vai consolidar os requisitos já fechados (Function + Behaviour + Structure) de um designer, agrupando-os por **artefato/componente de interface** em vez de por requisito — o objetivo é produzir uma referência pronta pra alguém montar as telas no Figma.

Você recebe uma lista de requisitos fechados, cada um com: código (Rxx), nome, tipo, modalidades fixas, e o texto de Function/Behaviour/Structure.

=== O QUE FAZER ===
Releia todas as Structures (com apoio das Behaviours/Functions pra contexto) e identifique os componentes de HMI **reais e distintos** que elas descrevem — por exemplo, um painel específico do WAD, uma barra de status, um overlay sobre um feed de sensor, um padrão de entrada numérica. Quando o mesmo componente aparece descrito por ângulos diferentes em requisitos diferentes (ex.: um requisito introduz um painel, outro estende ele com um campo novo, outro reaproveita ele explicitamente), você deve reconhecer que é o **mesmo componente** e agrupar num único item — mesmo que o texto de cada requisito descreva só o pedaço relevante pra ele. Isso exige leitura e julgamento semântico, não é correspondência textual.

Não invente reuso que não está no texto. Só agrupe quando a Structure de um requisito genuinamente descreve o mesmo objeto de interface que outro (reaproveitamento explícito, extensão do mesmo painel/tela/elemento, ou espelhamento do mesmo controle) — não porque são "parecidos" ou do mesmo tipo genérico.

=== FORMATO DA RESPOSTA ===
Retorne SOMENTE um array JSON (sem markdown, sem texto antes ou depois), nessa forma:
[
  {
    "name": "Nome curto e concreto do componente (ex.: 'Barra de UAVs Teamed (WAD)')",
    "requirements": ["R12", "R13", "R16"],
    "description": "Descrição objetiva do componente: o que é, onde vive, como cada requisito listado o usa ou estende, e qualquer detalhe de comportamento/confirmação relevante pra desenhar a tela. Pode ter várias frases. Cite qual requisito introduziu o componente e quais o estenderam, quando isso for claro no texto."
  },
  ...
]

Regras:
- Um componente por item; não repita o mesmo componente em dois itens.
- A lista "requirements" deve conter só os códigos Rxx que você recebeu (não invente códigos).
- Ordene os itens pela ordem em que os componentes aparecem pela primeira vez (pelo código do requisito mais baixo que o usa).
- Não inclua modalidades no JSON — isso é calculado à parte a partir do requisito.
- Não inclua nada além do array JSON.
