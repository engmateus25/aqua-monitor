"""
Gera graficos das simulacoes pre e pos-layout do SAR ADC DAC
Executa via: klayout_app.exe -b -r gerar_graficos.py
"""
import pya
import math

# ============================================================
# Leitura dos CSVs de simulacao
# ============================================================
def read_csv(path):
    times, values = [], []
    with open(path, 'r') as f:
        for i, line in enumerate(f):
            if i == 0:
                continue  # header
            parts = line.split()
            if len(parts) >= 2:
                try:
                    t = float(parts[0])
                    v = float(parts[1])
                    times.append(t * 1e6)   # converter para microsegundos
                    values.append(v * 1000) # converter para milivolts
                except ValueError:
                    pass
    return times, values

base = "u:/projetos/aqua-monitor/docs/microeletronica/"
t_pre, v_pre = read_csv(base + "pre_layout_data.csv")
t_pos, v_pos = read_csv(base + "pos_layout_data.csv")

print(f"Pre-layout: {len(t_pre)} pontos")
print(f"Pos-layout: {len(t_pos)} pontos")

# ============================================================
# Funcao para mapear valor para coordenada de pixel
# ============================================================
W, H = 900, 560
MARGIN_L, MARGIN_R, MARGIN_T, MARGIN_B = 90, 30, 40, 70

def map_x(t, t_min=0, t_max=7.0):
    plot_w = W - MARGIN_L - MARGIN_R
    return int(MARGIN_L + (t - t_min) / (t_max - t_min) * plot_w)

def map_y(v, v_min=-1400, v_max=800):
    plot_h = H - MARGIN_T - MARGIN_B
    frac = (v - v_min) / (v_max - v_min)
    return int(H - MARGIN_B - frac * plot_h)

# ============================================================
# Gera SVG comparativo (pre vs pos layout)
# ============================================================
def pt(t, v):
    return f"{map_x(t)},{map_y(v)}"

pre_pts  = " ".join(pt(t, v) for t, v in zip(t_pre, v_pre) if 0 <= t <= 7)
post_pts = " ".join(pt(t, v) for t, v in zip(t_pos, v_pos) if 0 <= t <= 7)

# Fases da conversao (linhas verticais)
phases = [
    (1.0,  "HOLD",   "#888"),
    (2.0,  "BIT3",   "#e74c3c"),
    (3.0,  "BIT2",   "#e67e22"),
    (4.0,  "BIT1",   "#27ae60"),
    (5.0,  "BIT0",   "#2980b9"),
    (6.0,  "DONE",   "#8e44ad"),
]

phase_lines = ""
for t_ph, label, color in phases:
    x = map_x(t_ph)
    phase_lines += f'<line x1="{x}" y1="{MARGIN_T}" x2="{x}" y2="{H-MARGIN_B}" stroke="{color}" stroke-width="1.5" stroke-dasharray="6,3" opacity="0.7"/>\n'
    phase_lines += f'<text x="{x+4}" y="{MARGIN_T+14}" font-size="11" fill="{color}" font-family="monospace">{label}</text>\n'

# Grid horizontal
grid_mv = [-1200, -800, -400, 0, 200, 400, 600, 800]
grid_lines = ""
for gv in grid_mv:
    gy = map_y(gv)
    grid_lines += f'<line x1="{MARGIN_L}" y1="{gy}" x2="{W-MARGIN_R}" y2="{gy}" stroke="#ddd" stroke-width="1"/>\n'
    grid_lines += f'<text x="{MARGIN_L-8}" y="{gy+4}" text-anchor="end" font-size="10" fill="#555" font-family="monospace">{gv}</text>\n'

# Grid vertical (tempo)
for t_tick in range(0, 8):
    gx = map_x(float(t_tick))
    grid_lines += f'<line x1="{gx}" y1="{MARGIN_T}" x2="{gx}" y2="{H-MARGIN_B}" stroke="#eee" stroke-width="1"/>\n'
    grid_lines += f'<text x="{gx}" y="{H-MARGIN_B+18}" text-anchor="middle" font-size="10" fill="#555" font-family="monospace">{t_tick}</text>\n'

# Linha do zero
y0 = map_y(0)
grid_lines += f'<line x1="{MARGIN_L}" y1="{y0}" x2="{W-MARGIN_R}" y2="{y0}" stroke="#999" stroke-width="1.5"/>\n'

svg1 = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" style="background:#fff;font-family:sans-serif;">
  <!-- Titulo -->
  <text x="{W//2}" y="22" text-anchor="middle" font-size="14" font-weight="bold" fill="#222">
    V(Vtop) - Comparacao Pre-Layout vs Pos-Layout | Vin=1.25V, Vref=1.8V
  </text>

  <!-- Eixos -->
  <rect x="{MARGIN_L}" y="{MARGIN_T}" width="{W-MARGIN_L-MARGIN_R}" height="{H-MARGIN_T-MARGIN_B}" fill="#fafafa" stroke="#ccc"/>

  <!-- Grid -->
  {grid_lines}

  <!-- Fases -->
  {phase_lines}

  <!-- Curva Pre-Layout -->
  <polyline points="{pre_pts}" fill="none" stroke="#2471a3" stroke-width="2.2" stroke-linejoin="round"/>

  <!-- Curva Pos-Layout -->
  <polyline points="{post_pts}" fill="none" stroke="#e74c3c" stroke-width="2.0" stroke-dasharray="8,4" stroke-linejoin="round"/>

  <!-- Legenda -->
  <rect x="{MARGIN_L+10}" y="{MARGIN_T+10}" width="200" height="48" fill="white" stroke="#ccc" rx="4"/>
  <line x1="{MARGIN_L+20}" y1="{MARGIN_T+26}" x2="{MARGIN_L+50}" y2="{MARGIN_T+26}" stroke="#2471a3" stroke-width="2.2"/>
  <text x="{MARGIN_L+56}" y="{MARGIN_T+30}" font-size="11" fill="#222">Pre-Layout (sem parasitas)</text>
  <line x1="{MARGIN_L+20}" y1="{MARGIN_T+44}" x2="{MARGIN_L+50}" y2="{MARGIN_T+44}" stroke="#e74c3c" stroke-width="2.0" stroke-dasharray="8,4"/>
  <text x="{MARGIN_L+56}" y="{MARGIN_T+48}" font-size="11" fill="#222">Pos-Layout (+6.72fF, +3.36O)</text>

  <!-- Eixo Y label -->
  <text x="16" y="{H//2}" text-anchor="middle" font-size="12" fill="#333" transform="rotate(-90,16,{H//2})">V(Vtop) [mV]</text>

  <!-- Eixo X label -->
  <text x="{W//2}" y="{H-8}" text-anchor="middle" font-size="12" fill="#333">Tempo [us]</text>
</svg>"""

out1 = base + "fig_comparacao_pre_pos.svg"
with open(out1, 'w') as f:
    f.write(svg1)
print(f"Grafico 1 salvo: {out1}")

# ============================================================
# Gera SVG: Zoom na regiao de decisao dos bits (1us a 7us)
# ============================================================
W2, H2 = 900, 480
ML2, MR2, MT2, MB2 = 90, 30, 40, 70

def map_x2(t, t_min=0.8, t_max=7.0):
    pw = W2 - ML2 - MR2
    return int(ML2 + (t - t_min) / (t_max - t_min) * pw)

def map_y2(v, v_min=-200, v_max=800):
    ph = H2 - MT2 - MB2
    return int(H2 - MB2 - (v - v_min) / (v_max - v_min) * ph)

pre_pts2  = " ".join(f"{map_x2(t)},{map_y2(v)}" for t, v in zip(t_pre, v_pre) if 0.8 <= t <= 7)
post_pts2 = " ".join(f"{map_x2(t)},{map_y2(v)}" for t, v in zip(t_pos, v_pos) if 0.8 <= t <= 7)

# Niveis teoricos de Vtop para cada fase
teorico = [
    (2.0, 3.0,  281, "#e74c3c", "BIT3: +281mV"),
    (3.0, 4.0,  506, "#e67e22", "BIT2: +506mV"),
    (4.0, 5.0,  619, "#27ae60", "BIT1: +619mV"),
    (5.0, 6.0,  506, "#2980b9", "BIT0: +506mV"),
]

teorico_lines = ""
for t_start, t_end, v_ref, color, label in teorico:
    x1, x2 = map_x2(t_start), map_x2(t_end)
    y_ref = map_y2(v_ref)
    teorico_lines += f'<line x1="{x1}" y1="{y_ref}" x2="{x2}" y2="{y_ref}" stroke="{color}" stroke-width="1.5" stroke-dasharray="5,3" opacity="0.6"/>\n'
    teorico_lines += f'<text x="{x2+3}" y="{y_ref-4}" font-size="10" fill="{color}">{label}</text>\n'

# Fases zoom
phase_lines2 = ""
for t_ph, label, color in phases:
    if 0.8 <= t_ph <= 7.0:
        x = map_x2(t_ph)
        phase_lines2 += f'<line x1="{x}" y1="{MT2}" x2="{x}" y2="{H2-MB2}" stroke="{color}" stroke-width="1.5" stroke-dasharray="6,3" opacity="0.5"/>\n'
        phase_lines2 += f'<text x="{x+4}" y="{MT2+14}" font-size="10" fill="{color}">{label}</text>\n'

# Grid horizontal zoom
grid2 = ""
for gv in [0, 100, 200, 300, 400, 500, 600, 700]:
    gy = map_y2(gv)
    grid2 += f'<line x1="{ML2}" y1="{gy}" x2="{W2-MR2}" y2="{gy}" stroke="#eee" stroke-width="1"/>\n'
    grid2 += f'<text x="{ML2-8}" y="{gy+4}" text-anchor="end" font-size="10" fill="#555" font-family="monospace">{gv}</text>\n'

y02 = map_y2(0)
grid2 += f'<line x1="{ML2}" y1="{y02}" x2="{W2-MR2}" y2="{y02}" stroke="#aaa" stroke-width="1.5"/>\n'

svg2 = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W2}" height="{H2}" style="background:#fff;">
  <text x="{W2//2}" y="22" text-anchor="middle" font-size="14" font-weight="bold" fill="#222">
    Zoom: Fases de Decisao SAR | Comparativo com Nivel Teorico
  </text>
  <rect x="{ML2}" y="{MT2}" width="{W2-ML2-MR2}" height="{H2-MT2-MB2}" fill="#fafafa" stroke="#ccc"/>
  {grid2}
  {phase_lines2}
  {teorico_lines}
  <polyline points="{pre_pts2}" fill="none" stroke="#2471a3" stroke-width="2.2" stroke-linejoin="round"/>
  <polyline points="{post_pts2}" fill="none" stroke="#e74c3c" stroke-width="2.0" stroke-dasharray="8,4" stroke-linejoin="round"/>
  <!-- Legenda -->
  <rect x="{ML2+10}" y="{MT2+10}" width="200" height="66" fill="white" stroke="#ccc" rx="4"/>
  <line x1="{ML2+20}" y1="{MT2+26}" x2="{ML2+50}" y2="{MT2+26}" stroke="#2471a3" stroke-width="2.2"/>
  <text x="{ML2+56}" y="{MT2+30}" font-size="11" fill="#222">Pre-Layout</text>
  <line x1="{ML2+20}" y1="{MT2+44}" x2="{ML2+50}" y2="{MT2+44}" stroke="#e74c3c" stroke-width="2.0" stroke-dasharray="8,4"/>
  <text x="{ML2+56}" y="{MT2+48}" font-size="11" fill="#222">Pos-Layout</text>
  <line x1="{ML2+20}" y1="{MT2+62}" x2="{ML2+50}" y2="{MT2+62}" stroke="#888" stroke-width="1.5" stroke-dasharray="5,3"/>
  <text x="{ML2+56}" y="{MT2+66}" font-size="11" fill="#888">Nivel Teorico</text>
  <text x="16" y="{H2//2}" text-anchor="middle" font-size="12" fill="#333" transform="rotate(-90,16,{H2//2})">V(Vtop) [mV]</text>
  <text x="{W2//2}" y="{H2-8}" text-anchor="middle" font-size="12" fill="#333">Tempo [us]</text>
</svg>"""

out2 = base + "fig_zoom_decisao.svg"
with open(out2, 'w') as f:
    f.write(svg2)
print(f"Grafico 2 salvo: {out2}")

print("=== Graficos gerados com sucesso ===")
