Você vai avaliar as decisões de design que um designer tomou usando o método FBS (Function-Behaviour-Structure), aplicado ao projeto de uma HMI multimodal para operações MUM-T (Manned-Unmanned Teaming) de ISR. Você não participou do processo de design — só vai julgar o resultado final, com base no que está escrito.

Você não sabe, e não deve tentar adivinhar, se esse designer teve ajuda de IA ou trabalhou sozinho. Não comente sobre isso, não infira a partir do estilo de escrita, e não deixe isso influenciar a nota. Avalie só o conteúdo final.

=== DEFINIÇÕES DO PROJETO ===
- Function (F): para que o artefato serve. Conecta o objetivo de quem projeta ao efeito mensurável do artefato. Function NÃO descreve sequência, ordem, lógica de condução ou passos de confirmação — isso é Behaviour.
- Behaviour (Be): o que o artefato FAZ — o fluxo de interação que realiza a Function, usando só as modalidades fixas daquele requisito.
- Structure (S): do que o artefato É FEITO — os componentes concretos de HMI e como eles se relacionam.
Uma Function pode dar origem a mais de um Behaviour, e um Behaviour pode reaproveitar Structure já definida em outro lugar — não é uma relação 1:1:1.

=== VOCABULÁRIO DE MODALIDADES (use só isso pra checar conformidade) ===
- Touch: entrada direta numa tela sensível ao toque.
- Keyboard: teclado físico ou virtual e botões; entrada de texto e valores.
- Screen: saída visual; informação renderizada numa tela.
- Voice-in: entrada por comando de voz reconhecido.
- Audio-out: saída sonora do sistema (alerta acústico ou fala sintetizada).
- Wearable/HMD: dispositivo de cabeça (VR/AR/XR). Entrada: rastreamento de cabeça/olhar, gestos. Saída: exibição no visor.
- Haptic: retorno tátil / força.
Cada requisito já vem com uma ou mais modalidades fixas — o designer não escolhe livremente, só usa as que foram dadas.

=== O QUE AVALIAR, POR REQUISITO ===
1. Conformidade às modalidades fixas — Behaviour e Structure usam só as modalidades listadas pra aquele requisito? (Sim / Parcial / Não + por quê)
2. Separação correta entre camadas — Function evita descrever fluxo? Behaviour evita listar componentes físicos? Structure é concreta, não uma repetição vaga da Behaviour? (Sim / Parcial / Não + por quê)
3. Completude e substância — as três camadas têm conteúdo específico o suficiente pra alguém desenhar a tela a partir disso, ou ficou vago/genérico? (Sim / Parcial / Não + por quê)
4. Nota geral do requisito, de 1 a 5 (3 = aceitável/usável, 5 = modelo do que se espera, 1 = precisa refazer).

=== O QUE AVALIAR NO CONJUNTO ===
- Cobertura: quantos requisitos do projeto foram de fato fechados, e quais faltaram.
- Consistência entre requisitos parecidos: requisitos com função semelhante foram resolvidos de forma semelhante, ou há contradição de critério entre eles?
- Padrões recorrentes: algo que se repete em vários requisitos, bom ou problemático.
- Nota geral do conjunto, de 1 a 5.

=== FORMATO DA RESPOSTA ===
## <código> — <nome>
Conformidade: ...
Separação de camadas: ...
Completude: ...
Nota: X/5
Observações: ...

(repita pra cada requisito fechado)

## Resumo geral
Cobertura: X/Y requisitos fechados (faltando: ...)
Consistência: ...
Padrões recorrentes: ...
Nota geral do conjunto: X/5

Seja direto e específico — cite o texto real da Function/Behaviour/Structure quando for apontar um problema, não fale em abstrato. Não elogie por elogiar; se um requisito está mediano, diga que está mediano.
