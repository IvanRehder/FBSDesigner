### O que é MUM-T

MUM-T (Manned-Unmanned Teaming) é o paradigma operacional em que uma tripulação humana coordena, em tempo real, um ou mais sistemas não tripulados (VANTs) durante uma missão — dividindo tarefas e, em certos momentos, assumindo o controle direto deles.

Neste projeto, o cenário é: um piloto de aeronave tripulada da Força Aérea Brasileira, em missão de ISR, que pode assumir o controle de um VANT operado por um outro operador dedicado (o "UAV Pilot"), dirigir os sensores do VANT pra pontos ou áreas de interesse, rastrear alvos, ajustar parâmetros de voo, e depois devolver o controle de volta pra esse operador quando a tarefa termina. A vantagem operacional é estender o alcance de vigilância e reconhecimento sem precisar de outra aeronave tripulada dedicada só pra isso.

Os requisitos que você vai trabalhar cobrem esse tipo de interação — pedir e devolver controle do VANT, ajustar parâmetros de voo dele, direcionar sensores, reportar dados de inteligência — além das ações do piloto na própria aeronave.

### O que é uma interface multimodal

"Multimodal" significa que a interação não depende de um canal só. Em vez de só toque, ou só voz, a HMI combina diferentes modalidades de entrada e saída (as mesmas que você viu na página anterior — Touch, Keyboard, Voice-in, Audio-out, etc.). Cada requisito já vem com as modalidades fixas que fazem sentido pra aquela tarefa específica, considerando coisas como a carga de trabalho do piloto naquele momento e o que as mãos e os olhos dele já estão ocupados fazendo.

### O que é ISR

ISR é a sigla de Intelligence, Surveillance and Reconnaissance — o conjunto de atividades de coletar, processar e entregar informação sobre o ambiente operacional (posições, terreno, pontos de interesse) pra apoiar decisões de comando. Dentro da missão, na prática:

- **Vigilância (Surveillance)** — observação contínua de uma área.
- **Reconhecimento (Reconnaissance)** — busca ativa por uma informação específica.
- **Inteligência (Intelligence)** — processamento e relato dessas informações pra quem decide.