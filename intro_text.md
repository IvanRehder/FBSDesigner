### O que você vai fazer

Você vai ajudar a definir elementos de uma interface humano-máquina (HMI) multimodal, num sistema de operações **MUM-T** (Manned-Unmanned Teaming) de **ISR** (Intelligence, Surveillance, Reconnaissance). Cada requisito já vem com contexto suficiente (intenção e modalidades fixas) — você não precisa conhecer os detalhes operacionais completos.

O trabalho é organizado em três camadas, sempre nessa ordem, pra cada requisito:

Nas definições abaixo, "artefato" é a interface (HMI) — :

- **Artefato** — é uma parte da interface (HMI) (pode ser um compoenten, ou um comjunto de componentes que juntor realizam uma ou mais coisas) que aquele requisito pede pra você definir. Não é o sistema inteiro (aeronave, VANT etc.), só a peça de interação em questão.
- **Function (F)** — pra que o artefato serve. Conecta o objetivo de quem projeta ao efeito mensurável do artefato. Function **não** descreve sequência, ordem, lógica de condução ou passos de confirmação — isso é Behaviour.
- **Behaviour (Be)** — o que o artefato **faz**: o fluxo de interação que realiza a função, usando só as modalidades fixas daquele requisito.
- **Structure (S)** — do que o artefato **é feito**: os componentes concretos de HMI e como eles se relacionam.

Uma Function pode dar origem a mais de um Behaviour, e um Behaviour pode reaproveitar Structure já definida em outro lugar — não é uma relação 1:1:1.

### Modalidades fixas

Cada requisito já vem com uma ou mais modalidades definidas. Use só essas — não introduza outras:

- **Touch** — entrada direta numa tela sensível ao toque (tocar, selecionar, arrastar).
- **Keyboard** — teclado físico ou virtual e botões; entrada de texto e valores.
- **Screen** — saída visual; informação renderizada numa tela.
- **Voice-in** — entrada por comando de voz reconhecido (fala transformada em comando).
- **Audio-out** — saída sonora do sistema (alerta acústico ou fala sintetizada).
- **Wearable/HMD** — dispositivo de cabeça (VR/AR/XR). Como entrada: rastreamento de cabeça/olhar, gestos. Como saída: exibição dentro do visor.
- **Haptic** — retorno tátil / força.

### Como isso vai ser avaliado

Isso faz parte de uma pesquisa de doutorado que compara diferentes formas de derivar decisões de projeto de interface a partir de requisitos. Não existe resposta certa ou errada — o que importa é o processo que você segue. Ao final, tem um questionário curto sobre a experiência de usar a ferramenta.
