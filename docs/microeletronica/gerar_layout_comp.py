"""
Layout do Comparador Diferencial de 2 Estágios - SAR ADC Aqua Monitor
Tecnologia: CMOS 180nm (camadas educacionais)
Ferramenta: KLayout v0.30.8 via Python API

Floorplan:
  ┌─────────────────────────────────────────────────────────┐
  │  PMOS (N-WELL)                                          │
  │  ┌─────────────────────────────────┐  ┌──────────────┐ │
  │  │ M5 (tail, W10/L2)              │  │ M7 (W20/L0.5)│ │
  │  └─────────────────────────────────┘  └──────────────┘ │
  │  ┌─────────────────────────────────────────────────────┐│
  │  │  M1 | M2 | M2 | M1  (ABBA Common-Centroid)         ││
  │  │  W=20/L=1, 2 fingers each, finger=10um             ││
  │  └─────────────────────────────────────────────────────┘│
  ├─────────────────────────────────────────────────────────┤
  │  NMOS (substrato P)                                     │
  │  ┌────────────────────┐  ┌──────────────────────────┐  │
  │  │ M3 (W10/L1) diodo  │  │ M4 (W10/L1) espelho      │  │
  │  └────────────────────┘  └──────────────────────────┘  │
  │  ┌──────────────┐                                       │
  │  │ M6 (W10/L0.5)│  ← Estágio 2 NMOS CS               │
  │  └──────────────┘                                       │
  └─────────────────────────────────────────────────────────┘

Camadas utilizadas:
  11 - N-Well
  12 - Active (difusão ativa, NMOS e PMOS)
  13 - P+ Select (implante PMOS)
  14 - N+ Select (implante NMOS)
  15 - Poly (gate)
  16 - Contact cut
   1 - Metal1 (horizontal)
   8 - Via1
   2 - Metal2 (vertical, roteamento principal)
  17 - Guard ring (anel de guarda)
"""

import klayout.db as db

# ─── Configuração do Layout ────────────────────────────────────────────────
layout = db.Layout()
layout.dbu = 0.001          # Resolução: 1 nm
TOP = layout.create_cell("COMPARATOR_2STAGE_SAR")

# ─── Definição de Camadas ──────────────────────────────────────────────────
LY = {
    "nwell":   layout.layer(11, 0),
    "active":  layout.layer(12, 0),
    "pplus":   layout.layer(13, 0),
    "nplus":   layout.layer(14, 0),
    "poly":    layout.layer(15, 0),
    "contact": layout.layer(16, 0),
    "metal1":  layout.layer(1,  0),
    "via1":    layout.layer(8,  0),
    "metal2":  layout.layer(2,  0),
    "guard":   layout.layer(17, 0),
}

# ─── Funções Auxiliares ───────────────────────────────────────────────────
def um(val):
    """Converte µm para unidades do layout (DBU=0.001)"""
    return int(round(val * 1000))

def box(x0, y0, x1, y1):
    return db.Box(um(x0), um(y0), um(x1), um(y1))

def insert(cell, layer, x0, y0, x1, y1):
    cell.shapes(layer).insert(box(x0, y0, x1, y1))

def label(cell, layer, x, y, text):
    cell.shapes(layer).insert(db.Text(text, um(x), um(y)))

def contacts_column(cell, x_center, y_bot, height, pitch=0.4):
    """Coluna de contacts (0.22x0.22µm) com pitch vertical."""
    n = max(1, int(height / pitch))
    y_start = y_bot + (height - (n - 1) * pitch) / 2
    for i in range(n):
        yc = y_start + i * pitch
        insert(cell, LY["contact"],
               x_center - 0.11, yc - 0.11,
               x_center + 0.11, yc + 0.11)

def metal1_bar(cell, x0, y0, x1, y1):
    insert(cell, LY["metal1"], x0, y0, x1, y1)

def metal2_bar(cell, x0, y0, x1, y1):
    insert(cell, LY["metal2"], x0, y0, x1, y1)

# ─── Função: Desenhar Transistor MOSFET Multi-Finger ─────────────────────
def draw_mosfet(cell, x0, y0, W, L, nfingers, is_pmos,
                label_src="S", label_gate="G", label_drn="D"):
    """
    Desenha um transistor MOSFET com nfingers fingers lado a lado.
    Corrente flui na direção X (canal); W é na direção Y.

    Geometria de cada finger (dimensões em µm):
      - Active: sd_ext | gate_L | sd_ext  (X)  ×  W  (Y)
      - Poly: estende gate_ext além do active em Y
      - Contacts: no centro de cada região S/D

    Fingers são interdigitados: S|G|D|G|S|G|D|G|S ...
    (regiões de difusão compartilhadas)
    """
    sd_ext   = 0.6    # extensão S/D além do gate em X
    gate_ext = 0.4    # extensão do poly além do active em Y
    contact_x_off = 0.3  # offset X do contact a partir da borda da active/gate

    # Largura da região S/D (= sd_ext para um lado simples)
    sd_w = sd_ext

    # pitch de cada finger (em X): um S/D + um gate
    fp = sd_w + L

    # largura total da célula (X)
    # nfingers fingers: (nfingers+1) regiões S/D + nfingers gates
    total_x = (nfingers + 1) * sd_w + nfingers * L

    # altura total (Y) = W + 2*gate_ext
    total_y = W + 2 * gate_ext

    # ── Active (difusão) ──────────────────────────────────────────────────
    insert(cell, LY["active"],
           x0, y0 + gate_ext,
           x0 + total_x, y0 + gate_ext + W)

    # ── Select (implante P+ ou N+) ────────────────────────────────────────
    sel_layer = LY["pplus"] if is_pmos else LY["nplus"]
    insert(cell, sel_layer,
           x0 - 0.2, y0 + gate_ext - 0.2,
           x0 + total_x + 0.2, y0 + gate_ext + W + 0.2)

    # ── Poly Gates ────────────────────────────────────────────────────────
    for f in range(nfingers):
        gx0 = x0 + (f + 1) * sd_w + f * L
        gx1 = gx0 + L
        insert(cell, LY["poly"],
               gx0, y0,
               gx1, y0 + total_y)
        label(cell, LY["poly"], gx0 + L / 2, y0 - 0.5, label_gate + str(f))

    # ── Contacts e Metal1 para cada região S/D ───────────────────────────
    metal_w = 0.5
    for sd in range(nfingers + 1):
        cx = x0 + sd * (sd_w + L) + sd_w / 2
        cy_bot = y0 + gate_ext + 0.1
        cy_top = y0 + gate_ext + W - 0.1
        # coluna de contacts
        contacts_column(cell, cx, cy_bot, W - 0.2)
        # barra de metal1 cobrindo a coluna
        metal1_bar(cell,
                   cx - metal_w / 2, cy_bot - 0.1,
                   cx + metal_w / 2, cy_top + 0.1)
        # labels alternados S/D
        if sd % 2 == 0:
            label(cell, LY["metal1"], cx, cy_bot - 0.8, label_src)
        else:
            label(cell, LY["metal1"], cx, cy_bot - 0.8, label_drn)

    return total_x, total_y

# ─── Função: Anel de Guarda ───────────────────────────────────────────────
def draw_guard_ring(cell, x0, y0, x1, y1, w=0.5, is_nwell=False):
    """Anel de guarda ao redor de uma região."""
    layer = LY["pplus"] if not is_nwell else LY["nplus"]
    # top/bottom bars
    insert(cell, LY["active"],  x0 - w, y0 - w, x1 + w, y0)
    insert(cell, LY["active"],  x0 - w, y1,     x1 + w, y1 + w)
    # left/right bars
    insert(cell, LY["active"],  x0 - w, y0, x0, y1)
    insert(cell, LY["active"],  x1,     y0, x1 + w, y1)
    # implante no anel
    insert(cell, layer,         x0 - w - 0.1, y0 - w - 0.1, x1 + w + 0.1, y1 + w + 0.1)
    # metal1 no anel
    metal1_bar(cell, x0 - w, y0 - w, x1 + w, y0)
    metal1_bar(cell, x0 - w, y1,     x1 + w, y1 + w)
    metal1_bar(cell, x0 - w, y0,     x0,     y1)
    metal1_bar(cell, x1,     y0,     x1 + w, y1)

# ═══════════════════════════════════════════════════════════════════════════
# BLOCO 1: N-WELL (cobre toda a seção PMOS)
# ═══════════════════════════════════════════════════════════════════════════
NWELL_X0, NWELL_Y0 = 1.0, 1.0
NWELL_W,  NWELL_H  = 74.0, 28.0
insert(TOP, LY["nwell"],
       NWELL_X0, NWELL_Y0,
       NWELL_X0 + NWELL_W, NWELL_Y0 + NWELL_H)

# ═══════════════════════════════════════════════════════════════════════════
# BLOCO 2: M5 — Fonte de Corrente de Cauda (PMOS W=10/L=2)
# Posição: canto superior esquerdo do N-Well
# ═══════════════════════════════════════════════════════════════════════════
M5_X0, M5_Y0 = 2.0, 16.0
M5_W, M5_H = draw_mosfet(TOP, M5_X0, M5_Y0,
                          W=10, L=2, nfingers=2, is_pmos=True,
                          label_src="VDD", label_gate="Vbias", label_drn="Vtail")
label(TOP, LY["metal2"], M5_X0, M5_Y0 + M5_H + 0.5, "M5 PMOS W10/L2")
metal2_bar(TOP, M5_X0 + 1.0, M5_Y0 + 1.0, M5_X0 + 2.5, M5_Y0 + M5_H - 1.0)

# ═══════════════════════════════════════════════════════════════════════════
# BLOCO 3: M1 + M2 — Par Diferencial PMOS (ABBA Common-Centroid)
# Arranjo: M1a | M2a | M2b | M1b  (2 fingers cada, W_finger=10µm)
# W=20µm, L=1µm por transistor
# ═══════════════════════════════════════════════════════════════════════════
# Dimensões de cada finger individual (W=10, L=1, nfingers=1)
# Usamos draw_mosfet 4 vezes para ter controle total do ABBA

DIFFPAIR_Y0 = 3.0
sd_ext = 0.6

# Coordenadas X dos 4 fingers (ABBA): M1a | M2a | M2b | M1b
# Cada "finger cell" tem active_w = sd_ext + L + sd_ext = 0.6+1+0.6=2.2µm
# Poly do gate: L=1µm
# Spacing entre fingers: compartilhamos a região S/D → pitch = sd_ext + L = 1.6µm
# 4 fingers: x_starts = [2.0, 3.6, 5.2, 6.8] com shared S/D

# Vamos desenhar a região ativa comum e os 4 gates separados
DP_X0 = 18.0   # início do bloco do par diferencial
DP_Y0 = DIFFPAIR_Y0
W_finger = 10.0
L_diff = 1.0
gate_ext = 0.4
sd_w = 0.8     # largura das regiões S/D
fp_pitch = sd_w + L_diff  # pitch de cada finger = 1.8µm
n_fingers_total = 4
total_dp_x = (n_fingers_total + 1) * sd_w + n_fingers_total * L_diff  # 4*0.8 + 4*1 + 0.8 = 8µm

# Active region comum
insert(TOP, LY["active"],
       DP_X0, DP_Y0 + gate_ext,
       DP_X0 + total_dp_x, DP_Y0 + gate_ext + W_finger)
insert(TOP, LY["pplus"],
       DP_X0 - 0.2, DP_Y0 + gate_ext - 0.2,
       DP_X0 + total_dp_x + 0.2, DP_Y0 + gate_ext + W_finger + 0.2)

# 4 Gates em ordem ABBA: M1a(gate=INM), M2a(gate=INP), M2b(gate=INP), M1b(gate=INM)
gate_labels = ["INM(M1a)", "INP(M2a)", "INP(M2b)", "INM(M1b)"]
gate_nodes  = ["INM",       "INP",      "INP",       "INM"]
drain_nodes = ["Vd1",       "Vout1",    "Vout1",     "Vd1"]

for f in range(4):
    gx0 = DP_X0 + (f + 1) * sd_w + f * L_diff
    gx1 = gx0 + L_diff
    insert(TOP, LY["poly"],
           gx0, DP_Y0,
           gx1, DP_Y0 + W_finger + 2 * gate_ext)
    label(TOP, LY["poly"], gx0 + 0.1, DP_Y0 - 0.6, gate_labels[f])

# Contacts e Metal1 para as 5 regiões S/D
sd_net = ["Vtail", "Vd1", "Vout1", "Vout1", "Vtail"]
# 0:Vtail, 1:Vd1, 2:Vout1 (shared center), 3:Vtail (right)
sd_actual = ["Vtail", "Vd1", "Vout1", "Vd1", "Vtail"]
for sd in range(5):
    cx = DP_X0 + sd * (sd_w + L_diff) + sd_w / 2
    cy_bot = DP_Y0 + gate_ext + 0.1
    cy_top = DP_Y0 + gate_ext + W_finger - 0.1
    contacts_column(TOP, cx, cy_bot, W_finger - 0.2)
    metal1_bar(TOP, cx - 0.25, cy_bot, cx + 0.25, cy_top)
    label(TOP, LY["metal1"], cx, cy_top + 0.2, sd_actual[sd])

label(TOP, LY["metal2"], DP_X0, DP_Y0 + W_finger + 2 * gate_ext + 0.8,
      "M1/M2 PMOS W20/L1 ABBA Common-Centroid")

# ═══════════════════════════════════════════════════════════════════════════
# BLOCO 4: M7 — Carga PMOS Estágio 2 (W=20/L=0.5)
# ═══════════════════════════════════════════════════════════════════════════
M7_X0, M7_Y0 = 48.0, 4.0
M7_W, M7_H = draw_mosfet(TOP, M7_X0, M7_Y0,
                          W=10, L=0.5, nfingers=2, is_pmos=True,
                          label_src="VDD", label_gate="Vbias2", label_drn="Vout")
label(TOP, LY["metal2"], M7_X0, M7_Y0 + M7_H + 0.5, "M7 PMOS W20/L0.5")

# ═══════════════════════════════════════════════════════════════════════════
# BLOCO 5 (NMOS): M3 + M4 — Espelho de Corrente (W=10/L=1 cada)
# Abaixo do N-Well, lado a lado
# ═══════════════════════════════════════════════════════════════════════════
NMOS_Y0 = NWELL_Y0 + NWELL_H + 3.0   # abaixo do N-Well

M3_X0 = 18.0
M3_W, M3_H = draw_mosfet(TOP, M3_X0, NMOS_Y0,
                          W=10, L=1, nfingers=2, is_pmos=False,
                          label_src="GND", label_gate="Vd1", label_drn="Vd1")
label(TOP, LY["metal2"], M3_X0, NMOS_Y0 + M3_H + 0.5, "M3 NMOS W10/L1 (diodo)")

# Curto-circuito gate-drain de M3 (diodo conectado)
diode_x = M3_X0 + 0.5
metal1_bar(TOP, diode_x, NMOS_Y0 + 0.5, diode_x + 1.5, NMOS_Y0 + 1.5)
label(TOP, LY["metal1"], diode_x, NMOS_Y0 - 0.5, "G=D")

M4_X0 = M3_X0 + M3_W + 4.0
M4_W, M4_H = draw_mosfet(TOP, M4_X0, NMOS_Y0,
                          W=10, L=1, nfingers=2, is_pmos=False,
                          label_src="GND", label_gate="Vd1", label_drn="Vout1")
label(TOP, LY["metal2"], M4_X0, NMOS_Y0 + M4_H + 0.5, "M4 NMOS W10/L1 (espelho)")

# Metal2 de Vd1: conecta dreno/gate de M3 ao gate de M4 (roteamento vertical)
metal2_bar(TOP, M3_X0 + 1.0, NMOS_Y0 - 2.0, M4_X0 + 1.0, NMOS_Y0 - 1.5)

# ═══════════════════════════════════════════════════════════════════════════
# BLOCO 6 (NMOS): M6 — Amplificador CS Estágio 2 (W=10/L=0.5)
# ═══════════════════════════════════════════════════════════════════════════
M6_X0 = 48.0
M6_W, M6_H = draw_mosfet(TOP, M6_X0, NMOS_Y0,
                          W=10, L=0.5, nfingers=2, is_pmos=False,
                          label_src="GND", label_gate="Vout1", label_drn="Vout")
label(TOP, LY["metal2"], M6_X0, NMOS_Y0 + M6_H + 0.5, "M6 NMOS W10/L0.5")

# ═══════════════════════════════════════════════════════════════════════════
# ROTEAMENTO PRINCIPAL (Metal2)
# ═══════════════════════════════════════════════════════════════════════════

# Vout: conecta dreno de M7 (PMOS) ao dreno de M6 (NMOS)
metal2_bar(TOP, M7_X0 + 1.0, NMOS_Y0 + 2.0,
               M7_X0 + 2.5, NWELL_Y0 + NWELL_H + 2.0)

# Vout1: saída do estágio 1 → gate de M6 (e drain de M2/M4)
metal2_bar(TOP, M6_X0 - 0.5, NMOS_Y0 - 1.5,
               M6_X0 + 0.5, NMOS_Y0 + 2.0)

# Vtail: liga dreno de M5 ao source de M1/M2
metal2_bar(TOP, M5_X0 + 1.5, DP_Y0 + 8.0,
               M5_X0 + 1.5, NWELL_Y0 + NWELL_H - 2.0)

# Vd1: liga dreno de M3 ao gate de M4
metal2_bar(TOP, M3_X0 + 2.0, NMOS_Y0 + 5.0,
               M4_X0 + 0.5, NMOS_Y0 + 5.0)

# ═══════════════════════════════════════════════════════════════════════════
# ANÉIS DE GUARDA
# ═══════════════════════════════════════════════════════════════════════════
# Anel externo: P+ guard ring ao redor de todo o bloco NMOS
draw_guard_ring(TOP,
                15.0, NMOS_Y0 - 1.0,
                62.0, NMOS_Y0 + 15.0,
                w=0.5, is_nwell=False)

# Anel N-Well: N+ guard ring interno ao N-Well para PMOS
draw_guard_ring(TOP,
                NWELL_X0 + 0.3, NWELL_Y0 + 0.3,
                NWELL_X0 + NWELL_W - 0.3, NWELL_Y0 + NWELL_H - 0.3,
                w=0.4, is_nwell=True)

# ═══════════════════════════════════════════════════════════════════════════
# PADS DE ENTRADA/SAÍDA
# ═══════════════════════════════════════════════════════════════════════════
pad_ports = [
    ("INP",    2.0,  -3.0),
    ("INM",    8.0,  -3.0),
    ("Vbias",  14.0, -3.0),
    ("Vbias2", 20.0, -3.0),
    ("VDD",    26.0, -3.0),
    ("GND",    32.0, -3.0),
    ("comp_out", 38.0, -3.0),
]
for pname, px, py in pad_ports:
    insert(TOP, LY["metal2"], px, py, px + 3.0, py + 2.0)
    label(TOP, LY["metal2"], px + 0.5, py + 0.5, pname)

# ═══════════════════════════════════════════════════════════════════════════
# LABEL GERAL
# ═══════════════════════════════════════════════════════════════════════════
label(TOP, LY["metal2"], 1.0, -5.0,
      "COMPARATOR 2-STAGE | SAR ADC | CMOS 180nm | Aqua Monitor")
label(TOP, LY["metal2"], 1.0, -6.5,
      "W_M1=W_M2=20um L=1um | W_M5=10um L=2um | Common-Centroid ABBA")

# ─── Salvar GDS ──────────────────────────────────────────────────────────
output_file = "comp_layout.gds"
layout.write(output_file)
print(f"Layout salvo: {output_file}")

# ─── Relatório de área ───────────────────────────────────────────────────
bbox = TOP.bbox()
w_um = bbox.width()  / 1000
h_um = bbox.height() / 1000
print(f"Bounding box: {w_um:.1f} µm x {h_um:.1f} µm")
print(f"Área total:   {w_um * h_um:.0f} µm²")
print()
print("Transistores incluídos:")
print("  M1  PMOS W=20/L=1  — Par diferencial INM (layout: 2 fingers ABBA)")
print("  M2  PMOS W=20/L=1  — Par diferencial INP (layout: 2 fingers ABBA)")
print("  M3  NMOS W=10/L=1  — Espelho de corrente (diodo conectado)")
print("  M4  NMOS W=10/L=1  — Espelho de corrente (cópia)")
print("  M5  PMOS W=10/L=2  — Fonte de corrente de cauda")
print("  M6  NMOS W=10/L=0.5— Amplificador CS (estágio 2)")
print("  M7  PMOS W=20/L=0.5— Carga ativa (estágio 2)")
print()
print("Técnicas de layout aplicadas:")
print("  ✓ Common-Centroid ABBA para M1/M2 (simetria de processo)")
print("  ✓ Guard rings P+ (NMOS) e N+ (PMOS/N-Well)")
print("  ✓ Metal2 para roteamento de sinais críticos")
print("  ✓ Fingers interdigitados para melhor casamento")
