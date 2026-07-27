# WAD — Screens & Panels — Component Inventory

Organizado por tela/painel. Cada seção lista os componentes de UI
que a compõem, extraídos do Structure de cada requisito.

---

## Telas-base

### Map View
*Origem: R05*
- Superfície de mapa (tappable)
- Input bindings: Touch (press-hold + tap) / Keyboard (bezel rotary + OSS)

### UAV List / Roster
*Origem: R09*
- Lista de UAVs (linhas selecionáveis)
- Seleção via Touch (tap) / Keyboard (bezel rotary + OSS) / UCP (UAV-ID)

### Sensor / ISR Feed View
*Origem: R14 + R16*
- Janela de feed de vídeo/sensor (chassi reusado do UAV Detail/Status Panel: header, close X, toggle persistente)
- Botão "ISR FEED" (invocação, no UAV screen)
- Controle de summon/dismiss no header do painel
- Toggle via bezel OSS / UCP soft-key
- Tab strip / lista de fontes de sensor (seleção entre sensores)
- Stepping de fonte via bezel rotary / UCP up-down
- Superfície tappable (recebe aimpoint)

---

## Overlays sobre o Map View

### Marker glyph layer
*Origem: R05/R07*
- Glifos de marcadores committed (intel/surveillance) na posição do mapa

### UAV glyph layer
*Origem: R09*
- Glifo por UAV na posição do mapa
- Estado clicável/selecionável

### Search-area geometry overlay
*Origem: R15*
- Handles de vértice/rotação arrastáveis (Touch)
- Geometry Field strip (UCP alphanumeric + bezel rotary) — vinculado bidirecionalmente ao overlay
- Botão de commit (on-panel + OSS)

---

## Overlay sobre o Sensor / ISR Feed View

### Sensor-aimpoint glyph + footprint
*Origem: R14*
- Glifo de aimpoint
- Footprint do sensor (área coberta)
- Indicador de direção/vetor de slew (para rate-slew contínuo)

---

## Painéis persistentes

### Autopilot Setpoint Panel
*Origem: R01*
- Campos Altitude / Heading / Speed (valor atual + pendente)
- Keypad numérico on-screen (Touch)
- Controles de step ± (Touch)
- Lista de presets (Touch)
- Bezel rotary + OSS (Keyboard — step/seleção/pick)
- UCP alfanumérico (Keyboard — entrada direta)

### Autopilot Mode Panel
*Origem: R03/R04*
- Botões de modo (um por modo de piloto automático, tap direto)
- Botão dedicado MANUAL (Touch)
- Bezel mode OSS/rotary (Keyboard, um por modo + dedicado MANUAL)
- Suporte a re-tap-to-deselect no controle do modo ativo

### UAV Parameter Panel
*Origem: R11*
- 3 linhas de parâmetro (speed / altitude / heading)
- Campo numérico + keypad por linha (Touch)
- Steppers ± por linha (Touch)
- Linha seletora de preset (Touch)
- Bezel rotary (Keyboard — step na linha selecionada)
- UCP alfanumérico (Keyboard — entrada direta)
- Botão Commit/Send (Touch OSS + bezel OSS)

### UAV Detail/Status Panel
*Origem: R12/R13*
- Tab/OSS persistente de toggle (show/hide)
- Botão de fechar (X)
- Campos de status ao vivo: link, modo, saúde, combustível, posição/atitude
- Destaque/flag no campo em transição (highlight de severidade)
- Linha de ação in-panel (reusada por R09/R10/R17/R19/R20 — ex: TAKEOVER, TRACK, HANDOVER)

### Tracking Panel
*Origem: R17/R18*
- Linha de status/detail do TOI ativo
- Affordance inline TRACK
- Linha editável de distância de rastreamento (co-localizada, quick-access)

---

## Mensagens e notificações

### Messages tab/screen
*Origem: R08*
- Lista persistente de mensagens
- Marcadores de não lida + timestamp
- Preview (primeiras palavras) por entrada
- Abertura do conteúdo completo sob demanda

### Notification pop-ups
*Origem: R08*
- Modo transient (auto-decai ~5s, sem dismiss)
- Modo preview (mostra início da mensagem)
- Modo on-demand (abre detalhe a partir de marker)

### Notification markers
*Origem: R08*
- Modo badge genérico (contagem/não lida)
- Modo âncora direcionada (aponta pro painel/campo alterado)
- Seleção via Touch (WAD) ou bezel OSS (Keyboard)

---

## Camadas modais / de entrada

### Option Ring
*Origem: R05, reusado em R06/R07/R09/R10/R14/R17/R19/R20*
- Menu radial, spawnado no ponto de press-hold
- Segmentos configuráveis por contexto (preset marker / Takeover / Track / Handover / Move Sensor)
- Seleção via Touch (tap no segmento) ou Keyboard (bezel rotary + OSS confirm)

### Virtual Keypad
*Origem: R01 Be1 (Touch)*
- Teclado numérico on-screen
- Ativado ao tocar um campo do painel ativo

---

## Fora do WAD (dispositivo separado)

### HUD flag/strip
*Origem: R02/R06/R13/R14*
- Flag booleano "condição atingida" (R02)
- Indicador "nova ordem" apontando pro painel WAD (R06)
- Strip resumido always-on: link/modo/saúde (R13)
- Escalonamento de flags de severidade máxima (R13)
- Reticle de designação (HMD, entrada) (R14)
