"""
Gera PNGs dos graficos de simulacao usando KLayout PixelBuffer API
"""
import pya

base = "u:/projetos/aqua-monitor/docs/microeletronica/"

def read_csv(path):
    times, values = [], []
    with open(path, 'r') as f:
        for i, line in enumerate(f):
            if i == 0:
                continue
            parts = line.split()
            if len(parts) >= 2:
                try:
                    times.append(float(parts[0]) * 1e6)
                    values.append(float(parts[1]) * 1000)
                except ValueError:
                    pass
    return times, values

t_pre, v_pre = read_csv(base + "pre_layout_data.csv")
t_pos, v_pos = read_csv(base + "pos_layout_data.csv")

print(f"Lidos: {len(t_pre)} pontos pre, {len(t_pos)} pontos pos")

# Cria layout GDS com as curvas desenhadas como polilinhas
# e exporta como imagem PNG via KLayout

W, H = 1200, 700
MARGIN = (100, 50, 50, 80)  # L, T, R, B

layout = pya.Layout()
layout.dbu = 0.001  # 1 nm

top = layout.create_cell("PLOT")
L_PRE  = layout.layer(1, 0)
L_POST = layout.layer(2, 0)
L_GRID = layout.layer(3, 0)
L_PHASE = layout.layer(4, 0)
L_ANNOT = layout.layer(5, 0)

T_MIN, T_MAX = 0.0, 7.0
V_MIN, V_MAX = -1400.0, 850.0

def map_pt(t, v):
    px = MARGIN[0] + int((t - T_MIN) / (T_MAX - T_MIN) * (W - MARGIN[0] - MARGIN[2]))
    py = MARGIN[1] + int((1.0 - (v - V_MIN) / (V_MAX - V_MIN)) * (H - MARGIN[1] - MARGIN[3]))
    # Em KLayout: Y aumenta para baixo, mas coordenadas sao em DBU (1nm)
    # Escala 1 pixel = 10 DBU para ter resolucao
    return (px * 10, (H - py) * 10)  # flip Y para coordenadas KLayout

# Grid horizontal
for gv in [-1200, -800, -400, 0, 200, 400, 600, 800]:
    _, gy = map_pt(0, gv)
    x0, _ = map_pt(T_MIN, gv)
    x1, _ = map_pt(T_MAX, gv)
    top.shapes(L_GRID).insert(pya.Box(x0, gy - 2, x1, gy + 2))

# Grid vertical
for gt in range(8):
    gx, _ = map_pt(float(gt), 0)
    _, y0 = map_pt(float(gt), V_MIN)
    _, y1 = map_pt(float(gt), V_MAX)
    top.shapes(L_GRID).insert(pya.Box(gx - 2, min(y0, y1), gx + 2, max(y0, y1)))

# Linha do zero
gx0, _ = map_pt(T_MIN, 0)
gx1, _ = map_pt(T_MAX, 0)
_, gy0 = map_pt(T_MIN, 0)
top.shapes(L_ANNOT).insert(pya.Box(gx0, gy0 - 5, gx1, gy0 + 5))

# Fases
phases = [(1.0, "HOLD"), (2.0, "BIT3"), (3.0, "BIT2"), (4.0, "BIT1"), (5.0, "BIT0"), (6.0, "DONE")]
for t_ph, _ in phases:
    gx, _ = map_pt(t_ph, 0)
    _, y0 = map_pt(t_ph, V_MIN)
    _, y1 = map_pt(t_ph, V_MAX)
    top.shapes(L_PHASE).insert(pya.Box(gx - 5, min(y0, y1), gx + 5, max(y0, y1)))

# Curva pre-layout: converte em polilinha via retangulos de 1 pixel
LWIDTH = 15  # largura de linha em DBU
for i in range(1, len(t_pre)):
    if T_MIN <= t_pre[i] <= T_MAX and T_MIN <= t_pre[i-1] <= T_MAX:
        x0, y0 = map_pt(t_pre[i-1], v_pre[i-1])
        x1, y1 = map_pt(t_pre[i], v_pre[i])
        # Desenha como caixa fina entre os dois pontos
        xmin, xmax = min(x0, x1), max(x0, x1)
        ymin, ymax = min(y0, y1), max(y0, y1)
        if xmax - xmin < LWIDTH:
            xmax = xmin + LWIDTH
        if ymax - ymin < LWIDTH:
            ymax = ymin + LWIDTH
        top.shapes(L_PRE).insert(pya.Box(xmin, ymin, xmax, ymax))

# Curva pos-layout
for i in range(1, len(t_pos)):
    if T_MIN <= t_pos[i] <= T_MAX and T_MIN <= t_pos[i-1] <= T_MAX:
        x0, y0 = map_pt(t_pos[i-1], v_pos[i-1])
        x1, y1 = map_pt(t_pos[i], v_pos[i])
        xmin, xmax = min(x0, x1), max(x0, x1)
        ymin, ymax = min(y0, y1), max(y0, y1)
        if xmax - xmin < LWIDTH + 5:
            xmax = xmin + LWIDTH + 5
        if ymax - ymin < LWIDTH + 5:
            ymax = ymin + LWIDTH + 5
        top.shapes(L_POST).insert(pya.Box(xmin, ymin, xmax, ymax))

# Salva GDS intermediario para referencia
layout.write(base + "plot_gds.gds")

# Exporta como PNG via KLayout LayoutView
lv = pya.LayoutView()
lv.load_layout(base + "plot_gds.gds")
lv.zoom_fit()

# Configura cores das camadas
li = lv.begin_layers()
layers_config = [
    (L_GRID,  (200, 200, 200)),
    (L_PHASE, (150, 180, 240)),
    (L_ANNOT, (80, 80, 80)),
    (L_PRE,   (36, 113, 163)),   # azul pre-layout
    (L_POST,  (231, 76, 60)),    # vermelho pos-layout
]

while not li.at_end():
    lp = li.current()
    layer_idx = lp.layer_index()
    for l, color in layers_config:
        if layer_idx == l:
            new_lp = lp.dup()
            new_lp.fill_color  = (color[0] << 16) | (color[1] << 8) | color[2]
            new_lp.frame_color = (color[0] << 16) | (color[1] << 8) | color[2]
            new_lp.width = 1
            lv.set_layer_properties(li, new_lp)
    li.next()

lv.save_image(base + "fig_comparacao_pre_pos.png", W * 2, H * 2)
print(f"PNG salvo: fig_comparacao_pre_pos.png")
