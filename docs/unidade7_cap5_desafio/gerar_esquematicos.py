#!/usr/bin/env python3
"""
gerar_esquematicos.py  --  Esquematicos gate-level HammingChip v1.0
Unidade 7 | Capitulo 5 | PADIS
Autor: Matheus Serrao Uchoa  |  Prof.: Thiago Brito
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

# ─── Paleta ──────────────────────────────────────────────────────────────────
BLU  = '#1565C0'; TBLU = '#1E88E5'; GRN  = '#2E7D32'; TGRN = '#43A047'
RED  = '#C62828'; ORG  = '#EF6C00'; PUR  = '#6A1B9A'; TPUR = '#8E24AA'
GRY  = '#424242'; LGRY = '#ECEFF1'; WHT  = '#FFFFFF'; DRK  = '#212121'

LW = 1.8

# ─── Primitivas ──────────────────────────────────────────────────────────────
def wire(ax, x0, y0, x1, y1, color=GRY, lw=LW):
    ax.plot([x0, x1], [y0, y1], color=color, lw=lw, solid_capstyle='round')

def dot(ax, x, y, color=GRY, r=0.05):
    ax.add_patch(plt.Circle((x, y), r, color=color, zorder=6))

def lbl(ax, x, y, txt, ha='center', va='center', color=GRY, size=8.5, bold=False, mono=True):
    ax.text(x, y, txt, ha=ha, va=va, color=color, fontsize=size,
            fontweight='bold' if bold else 'normal',
            fontfamily='monospace' if mono else 'sans-serif')

def input_pin(ax, x, y, name, color=BLU):
    ax.annotate('', xy=(x, y), xytext=(x-0.7, y),
                arrowprops=dict(arrowstyle='->', color=color, lw=LW))
    lbl(ax, x-1.0, y, name, ha='right', color=color, size=9, bold=True)

def output_pin(ax, x, y, name, color=GRN):
    ax.annotate('', xy=(x+0.7, y), xytext=(x, y),
                arrowprops=dict(arrowstyle='->', color=color, lw=LW))
    lbl(ax, x+1.1, y, name, ha='left', color=color, size=9, bold=True)

# ─── Corpo XOR IEEE ──────────────────────────────────────────────────────────
def gate_xor(ax, cx, cy, w=0.9, h=0.7, color=ORG):
    t = np.linspace(-np.pi/2, np.pi/2, 80)
    back_r = 0.28
    # corpo OR
    ax.plot(cx - w/2 + back_r*(1-np.cos(t)), cy + (h/2)*np.sin(t),
            color=color, lw=LW)
    ts = np.linspace(0, np.pi/2, 60)
    ax.plot(cx - w/2 + (w + h/2)*np.sin(ts)**1.35, cy + h/2*np.cos(ts)**0.5,
            color=color, lw=LW)
    ax.plot(cx - w/2 + (w + h/2)*np.sin(ts)**1.35, cy - h/2*np.cos(ts)**0.5,
            color=color, lw=LW)
    # curva extra XOR
    off = -0.20
    ax.plot(cx - w/2 + off + back_r*(1-np.cos(t)), cy + (h/2)*np.sin(t),
            color=color, lw=LW)
    ax.text(cx, cy, '=1', ha='center', va='center', fontsize=8,
            color=color, fontweight='bold', fontfamily='monospace')
    x_out = cx + w*0.82 + h/2*0.18
    x_in  = cx - w/2 + off - back_r*0.02
    return x_in, x_out, cy

def gate_and(ax, cx, cy, w=0.8, h=0.65, color=BLU):
    ax.plot([cx-w/2, cx, cx], [cy-h/2, cy-h/2, cy+h/2],
            color=color, lw=LW, solid_capstyle='round')
    ax.plot([cx-w/2, cx-w/2], [cy-h/2, cy+h/2], color=color, lw=LW)
    ax.plot([cx-w/2, cx], [cy+h/2, cy+h/2], color=color, lw=LW)
    theta = np.linspace(-np.pi/2, np.pi/2, 60)
    ax.plot(cx + h/2*np.sin(theta), cy + h/2*np.cos(theta), color=color, lw=LW)
    ax.text(cx-0.05, cy, '&', ha='center', va='center',
            fontsize=8, color=color, fontweight='bold', fontfamily='monospace')
    return cx - w/2, cx + h/2, cy

def gate_not(ax, cx, cy, w=0.55, h=0.48, color=RED):
    ax.plot([cx-w/2, cx-w/2, cx+w/2-h/4], [cy-h/2, cy+h/2, cy],
            color=color, lw=LW, solid_capstyle='round')
    ax.plot([cx-w/2, cx+w/2-h/4], [cy-h/2, cy],
            color=color, lw=LW, solid_capstyle='round')
    ax.text(cx-0.05, cy, '1', ha='center', va='center',
            fontsize=8, color=color, fontweight='bold')
    ax.add_patch(plt.Circle((cx+w/2-h/4+0.11, cy), 0.09,
                 ec=color, fc=WHT, lw=LW, zorder=4))
    return cx - w/2, cx+w/2+0.02, cy

# ─── Bloco retangular generico ───────────────────────────────────────────────
def block(ax, x, y, w, h, fc, ec, title, sub='', fs=9):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.12',
                 fc=fc, ec=ec, lw=1.8, zorder=2))
    ax.text(x+w/2, y+h/2+(0.18 if sub else 0), title,
            ha='center', va='center', fontsize=fs, fontweight='bold', color=ec)
    if sub:
        ax.text(x+w/2, y+h/2-0.28, sub, ha='center', va='center',
                fontsize=7.5, color='#555', style='italic')

def title_bar(ax, title, subtitle=''):
    ax.text(0.5, 0.98, title, transform=ax.transAxes,
            ha='center', va='top', fontsize=12, fontweight='bold', color=DRK)
    if subtitle:
        ax.text(0.5, 0.94, subtitle, transform=ax.transAxes,
                ha='center', va='top', fontsize=9, color='#555',
                style='italic')

# =============================================================================
# Figura 1: Codificador Hamming(7,4) — portas XOR
# p1 = d1 ^ d2 ^ d4
# p2 = d1 ^ d3 ^ d4
# p4 = d2 ^ d3 ^ d4
# Saida: codeword[6:0] = {p1,p2,d1,p4,d2,d3,d4}
# =============================================================================
def fig_encoder():
    fig, ax = plt.subplots(figsize=(14, 11))
    ax.set_xlim(-1, 14); ax.set_ylim(0, 11)
    ax.axis('off'); fig.patch.set_facecolor('#F5F8FC')
    title_bar(ax,
        'HammingChip v1.0 — Codificador Hamming(7,4)',
        'Geração de paridade: p1 = d1⊕d2⊕d4 | p2 = d1⊕d3⊕d4 | p4 = d2⊕d3⊕d4')

    # ── posições fixas dos 3 pares de XOR (cada row bem separada) ──
    # Row 0 (p1=d1^d2^d4): y_gate1=9.0, y_gate2=8.2
    # Row 1 (p2=d1^d3^d4): y_gate1=6.0, y_gate2=5.2
    # Row 2 (p4=d2^d3^d4): y_gate1=3.0, y_gate2=2.2
    rows = [
        # (pname, g1_y, g2_y, in1_d, in2_d, in3_d, color)
        #   in_d = index in d_y list (d1=0, d2=1, d3=2, d4=3)
        ('p1', 9.0, 8.2, 0, 1, 3, BLU),
        ('p2', 6.0, 5.2, 0, 2, 3, TGRN),
        ('p4', 3.0, 2.2, 1, 2, 3, PUR),
    ]

    # ── faixas de entrada (guias horizontais) ──
    d_y   = [9.5, 7.2, 4.8, 2.5]   # d1, d2, d3, d4  (evenly spread)
    d_lbl = ['d1', 'd2', 'd3', 'd4']
    d_x0  = 0.3

    for i, (y, n) in enumerate(zip(d_y, d_lbl)):
        ax.annotate('', xy=(d_x0+0.5, y), xytext=(d_x0, y),
                    arrowprops=dict(arrowstyle='->', color=BLU, lw=LW))
        lbl(ax, d_x0-0.1, y, n, ha='right', color=BLU, size=10, bold=True)
        wire(ax, d_x0+0.5, y, 11.0, y, color='#CCCCCC', lw=0.6)

    xor1_x = 4.5
    xor2_x = 7.5

    for pname, g1y, g2y, ia, ib, ic, col in rows:
        ya, yb, yc = d_y[ia], d_y[ib], d_y[ic]

        # ── XOR gate 1: input_a ^ input_b ──
        x_in1, x_out1, _ = gate_xor(ax, xor1_x, g1y, color=col)
        # input A: down from wire ya to gate upper pin
        wire(ax, d_x0+0.5, ya, x_in1-0.05, ya, color=col, lw=1.1)
        wire(ax, x_in1-0.05, ya, x_in1-0.05, g1y+0.26, color=col, lw=1.1)
        wire(ax, x_in1-0.05, g1y+0.26, x_in1, g1y+0.26, color=col, lw=1.1)
        dot(ax, x_in1-0.05, ya, color=col, r=0.04)
        # input B: up from wire yb to gate lower pin
        wire(ax, d_x0+0.5, yb, x_in1-0.20, yb, color=col, lw=1.1)
        wire(ax, x_in1-0.20, yb, x_in1-0.20, g1y-0.26, color=col, lw=1.1)
        wire(ax, x_in1-0.20, g1y-0.26, x_in1, g1y-0.26, color=col, lw=1.1)
        dot(ax, x_in1-0.20, yb, color=col, r=0.04)

        # ── XOR gate 2: (A^B) ^ input_c ──
        x_in2, x_out2, _ = gate_xor(ax, xor2_x, g2y, color=col)
        # output of XOR1 → upper pin of XOR2
        wire(ax, x_out1, g1y, xor2_x-0.60, g1y, color=col, lw=1.2)
        wire(ax, xor2_x-0.60, g1y, xor2_x-0.60, g2y+0.26, color=col, lw=1.2)
        wire(ax, xor2_x-0.60, g2y+0.26, x_in2, g2y+0.26, color=col, lw=1.2)
        # input C → lower pin of XOR2
        wire(ax, d_x0+0.5, yc, xor2_x-0.76, yc, color=col, lw=1.1)
        wire(ax, xor2_x-0.76, yc, xor2_x-0.76, g2y-0.26, color=col, lw=1.1)
        wire(ax, xor2_x-0.76, g2y-0.26, x_in2, g2y-0.26, color=col, lw=1.1)
        dot(ax, xor2_x-0.76, yc, color=col, r=0.04)

        # output wire
        wire(ax, x_out2, g2y, 11.0, g2y, color=col, lw=1.5)
        lbl(ax, x_out2+0.55, g2y+0.28, pname, color=col, size=9.5, bold=True)

    # ── Codeword assembly ──────────────────────────────────────────────────────
    cw_bits   = ['p1', 'p2', 'd1', 'p4', 'd2', 'd3', 'd4']
    cw_colors = [BLU, TGRN, BLU, PUR, TGRN, TGRN, BLU]
    # fonte de y para cada bit (onde está o fio horizontal)
    cw_src_y  = [rows[0][2], rows[1][2],   # p1=g2y row0, p2=g2y row1
                 d_y[0],                   # d1
                 rows[2][2],               # p4=g2y row2
                 d_y[1], d_y[2], d_y[3]]  # d2,d3,d4

    xc = 12.4
    cw_ys = np.linspace(10.0, 1.8, 7)
    block(ax, xc-0.55, 1.3, 1.1, 9.2, '#EEF4FF', BLU, 'codeword\n[6:0]', fs=8)

    for i, (bit, col, cy, src_y) in enumerate(zip(cw_bits, cw_colors, cw_ys, cw_src_y)):
        ax.add_patch(FancyBboxPatch((xc-0.42, cy-0.24), 0.84, 0.48,
                     boxstyle='square,pad=0.02', fc='#DDEEFF', ec=col, lw=1.2))
        lbl(ax, xc, cy, bit, color=col, size=8.5, bold=True)
        lbl(ax, xc, cy-0.42, f'[{i}]', color='#999', size=7)
        # horizontal line from source y to codeword bit y
        wire(ax, 11.0, src_y, 11.0, cy, color='#BBBBBB', lw=0.7)
        wire(ax, 11.0, cy, xc-0.42, cy, color=col, lw=1.1)

    ax.text(0.01, 0.01,
            'Hamming(7,4): d[3:0]→7 bits  |  p1=d1⊕d2⊕d4  |  p2=d1⊕d3⊕d4  |  p4=d2⊕d3⊕d4',
            transform=ax.transAxes, fontsize=8, color='#666', style='italic')

    plt.tight_layout()
    plt.savefig('fig_schem_encoder.png', dpi=150, bbox_inches='tight')
    print('Salvo: fig_schem_encoder.png')
    plt.close()


# =============================================================================
# Figura 2: Gerador de Sindrome (Decoder parte 1)
# s1 = r1^r3^r5^r7  (posicoes 1,3,5,7)
# s2 = r2^r3^r6^r7  (posicoes 2,3,6,7)
# s4 = r4^r5^r6^r7  (posicoes 4,5,6,7)
# =============================================================================
def fig_syndrome():
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(-1, 14); ax.set_ylim(-0.5, 10.5)
    ax.axis('off'); fig.patch.set_facecolor('#F5F8FC')
    title_bar(ax,
        'HammingChip v1.0 — Gerador de Síndrome',
        's1=r1⊕r3⊕r5⊕r7  |  s2=r2⊕r3⊕r6⊕r7  |  s4=r4⊕r5⊕r6⊕r7')

    # ── Entradas (bits recebidos r1..r7) ──
    r_y = [9.3, 8.2, 7.1, 6.0, 4.9, 3.8, 2.7]
    r_lbl = ['r1 (p1)', 'r2 (p2)', 'r3 (d1)', 'r4 (p4)',
             'r5 (d2)', 'r6 (d3)', 'r7 (d4)']
    r_col = [BLU, TGRN, GRY, PUR, GRY, GRY, GRY]
    x0 = 0.5
    for ry, rl, rc in zip(r_y, r_lbl, r_col):
        ax.annotate('', xy=(x0+0.5, ry), xytext=(x0, ry),
                    arrowprops=dict(arrowstyle='->', color=rc, lw=LW))
        lbl(ax, x0-0.1, ry, rl, ha='right', color=rc, size=9, bold=True)
        wire(ax, x0+0.5, ry, 11.5, ry, color='#CCCCCC', lw=0.7)

    # ── XOR chains (3 XOR gates each) ──
    chains = [
        ('s1', [0, 2, 4, 6], ORG),   # r1,r3,r5,r7 (index 0-based)
        ('s2', [1, 2, 5, 6], TGRN),  # r2,r3,r6,r7
        ('s4', [3, 4, 5, 6], PUR),   # r4,r5,r6,r7
    ]
    x_stages = [3.5, 6.0, 8.5]
    sy_out   = [9.0, 7.0, 5.0]

    for ci, (sname, ridx, col) in enumerate(chains):
        src_ys = [r_y[i] for i in ridx]  # 4 input y-positions
        cy1 = (src_ys[0] + src_ys[1]) / 2
        cy2 = (cy1 + src_ys[2]) / 2
        cy3 = (cy2 + src_ys[3]) / 2

        # XOR stage 1: ridx[0] ^ ridx[1]
        x_in1a, x_out1, _ = gate_xor(ax, x_stages[0], cy1, color=col)
        wire(ax, x0+0.5, src_ys[0], x_in1a, src_ys[0], color=col, lw=1.1)
        wire(ax, x_in1a, src_ys[0], x_in1a, cy1+0.25, color=col, lw=1.1)
        wire(ax, x0+0.5, src_ys[1], x_in1a-0.12, src_ys[1], color=col, lw=1.1)
        wire(ax, x_in1a-0.12, src_ys[1], x_in1a-0.12, cy1-0.25, color=col, lw=1.1)
        wire(ax, x_in1a-0.12, cy1-0.25, x_in1a, cy1-0.25, color=col, lw=1.1)

        # XOR stage 2: prev ^ ridx[2]
        x_in2, x_out2, _ = gate_xor(ax, x_stages[1], cy2, color=col)
        wire(ax, x_out1, cy1, x_stages[1]-0.65, cy1, color=col, lw=1.1)
        wire(ax, x_stages[1]-0.65, cy1, x_stages[1]-0.65, cy2+0.25, color=col, lw=1.1)
        wire(ax, x0+0.5, src_ys[2], x_in2-0.14, src_ys[2], color=col, lw=1.1)
        wire(ax, x_in2-0.14, src_ys[2], x_in2-0.14, cy2-0.25, color=col, lw=1.1)
        wire(ax, x_in2-0.14, cy2-0.25, x_in2, cy2-0.25, color=col, lw=1.1)

        # XOR stage 3: prev ^ ridx[3]
        x_in3, x_out3, _ = gate_xor(ax, x_stages[2], cy3, color=col)
        wire(ax, x_out2, cy2, x_stages[2]-0.65, cy2, color=col, lw=1.1)
        wire(ax, x_stages[2]-0.65, cy2, x_stages[2]-0.65, cy3+0.25, color=col, lw=1.1)
        wire(ax, x0+0.5, src_ys[3], x_in3-0.14, src_ys[3], color=col, lw=1.1)
        wire(ax, x_in3-0.14, src_ys[3], x_in3-0.14, cy3-0.25, color=col, lw=1.1)
        wire(ax, x_in3-0.14, cy3-0.25, x_in3, cy3-0.25, color=col, lw=1.1)

        # output
        wire(ax, x_out3, cy3, 11.6, cy3, color=col, lw=1.5)
        dot(ax, 11.6, cy3, color=col)
        lbl(ax, x_out3+0.5, cy3+0.28, sname, color=col, size=10, bold=True)

    # ── Syndrome bus ──
    sb_ys = [y for _, ridx, _ in chains
             for y in [( r_y[ridx[0]]+r_y[ridx[1]])/2]]
    sb_ys2 = []
    for ci, (sname, ridx, col) in enumerate(chains):
        src_ys = [r_y[i] for i in ridx]
        cy3 = ((src_ys[0]+src_ys[1])/2 + src_ys[2])/2
        cy3 = (cy3 + src_ys[3])/2
        sb_ys2.append(cy3)

    block(ax, 12.0, min(sb_ys2)-0.4, 1.5, max(sb_ys2)-min(sb_ys2)+0.8,
          '#FFF8E1', ORG, 'síndrome\n[2:0]', fs=8)

    for i, (sn, col, sy) in enumerate(zip(['s4','s2','s1'],
                                          [PUR, TGRN, ORG],
                                          sb_ys2[::-1])):
        ax.add_patch(FancyBboxPatch((12.1, sy-0.22), 1.3, 0.44,
                     boxstyle='square,pad=0.02', fc='#FFF3CD', ec=col, lw=1.2))
        lbl(ax, 12.75, sy, sn, color=col, size=9, bold=True)

    ax.text(0.01, 0.02,
            'Sindrome != 0 → posicao do erro  |  sindrome == 0 → sem erro',
            transform=ax.transAxes, fontsize=8, color='#666', style='italic')

    plt.tight_layout()
    plt.savefig('fig_schem_syndrome.png', dpi=150, bbox_inches='tight')
    print('Salvo: fig_schem_syndrome.png')
    plt.close()


# =============================================================================
# Figura 3: Corretor de Erro
# sindrome[2:0] = {s4,s2,s1} → posicao 1-7 → inverte bit errado via XOR
# =============================================================================
def fig_corrector():
    fig, ax = plt.subplots(figsize=(14, 11))
    ax.set_xlim(-0.5, 14); ax.set_ylim(-0.5, 11.5)
    ax.axis('off'); fig.patch.set_facecolor('#F5F8FC')
    title_bar(ax,
        'HammingChip v1.0 — Corretor de Erro',
        'Decodificador 3→7 (AND-NOT) + XOR para inversão do bit errado')

    # ── Entradas: sindrome e bits recebidos ──
    s_y = [10.2, 9.5, 8.8]
    s_lbl = ['s4', 's2', 's1']
    s_col = [PUR, TGRN, ORG]
    x0 = 0.4

    for sy, sl, sc in zip(s_y, s_lbl, s_col):
        ax.annotate('', xy=(x0+0.4, sy), xytext=(x0, sy),
                    arrowprops=dict(arrowstyle='->', color=sc, lw=LW))
        lbl(ax, x0-0.1, sy, sl, ha='right', color=sc, size=10, bold=True)
        wire(ax, x0+0.4, sy, 5.5, sy, color='#CCCCCC', lw=0.7)

    r_y = np.linspace(8.2, 1.2, 7)
    for i, ry in enumerate(r_y):
        ax.annotate('', xy=(x0+0.4, ry), xytext=(x0, ry),
                    arrowprops=dict(arrowstyle='->', color=GRY, lw=1.2))
        lbl(ax, x0-0.1, ry, f'r{i+1}', ha='right', color=GRY, size=8.5)
        wire(ax, x0+0.4, ry, 10.5, ry, color='#DDDDDD', lw=0.7)

    # ── NOT gates (inversoes do sindrome) ──
    not_x = 2.0
    not_ys  = [sy - 1.2 for sy in s_y]
    ns_y_inv = []
    for j, (sy, sc) in enumerate(zip(s_y, s_col)):
        x_in_n, x_out_n, _ = gate_not(ax, not_x, sy-1.2, color=sc)
        wire(ax, x0+0.4, sy, not_x-0.28, sy, color=sc, lw=1.1)
        wire(ax, not_x-0.28, sy, not_x-0.28, sy-1.2, color=sc, lw=1.1)
        dot(ax, not_x-0.28, sy, color=sc)
        ns_y_inv.append((sy, sy-1.2, x_out_n, sc))
        lbl(ax, x_out_n+0.3, sy-1.2+0.25, f'!{s_lbl[j]}', color=sc, size=8)

    # ── AND3 gates para cada posicao 1-7 ──
    # pos: (s4, s2, s1) que devem ser 1 ou 0
    # pos1 = !s4 & !s2 &  s1
    # pos2 = !s4 &  s2 & !s1
    # pos3 = !s4 &  s2 &  s1
    # pos4 =  s4 & !s2 & !s1
    # pos5 =  s4 & !s2 &  s1
    # pos6 =  s4 &  s2 & !s1
    # pos7 =  s4 &  s2 &  s1
    pos_cfg = [
        (0, 0, 1), (0, 1, 0), (0, 1, 1),
        (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1),
    ]
    and_x = 5.2
    and_ys = np.linspace(9.8, 1.6, 7)
    sel_x_out = 7.0

    for i, (cfg, ay) in enumerate(zip(pos_cfg, and_ys)):
        x_in_a, x_out_a, _ = gate_and(ax, and_x, ay, h=0.55, color=BLU)
        # draw 3 input lines
        terms = [(cfg[0], s_y[0], s_lbl[0]),
                 (cfg[1], s_y[1], s_lbl[1]),
                 (cfg[2], s_y[2], s_lbl[2])]
        offs = [-0.22, 0.0, 0.22]
        for j, (use_pos, syin, sln) in enumerate(terms):
            col = s_col[j] if use_pos else s_col[j]
            src_y = syin if use_pos else (syin - 1.2)
            wire(ax, 5.5, src_y, x_in_a-0.05, src_y, color=col, lw=0.9)
            wire(ax, x_in_a-0.05, src_y, x_in_a-0.05, ay+offs[j], color=col, lw=0.9)
            wire(ax, x_in_a-0.05, ay+offs[j], x_in_a, ay+offs[j], color=col, lw=0.9)
            if not use_pos:
                ax.add_patch(plt.Circle((x_in_a-0.05, ay+offs[j]), 0.07,
                             ec=RED, fc=WHT, lw=1.0, zorder=5))

        wire(ax, x_out_a, ay, sel_x_out, ay, color=BLU, lw=1.1)
        lbl(ax, sel_x_out+0.2, ay+0.2, f'sel{i+1}', color=BLU, size=7.5)

    # ── XOR de correcao ──
    xor_x = 9.0
    for i, (ry, ay) in enumerate(zip(r_y, and_ys)):
        x_in_x, x_out_x, _ = gate_xor(ax, xor_x, (ry+ay)/2, h=0.55, color=ORG)
        # bit recebido
        wire(ax, x0+0.4, ry, x_in_x-0.08, ry, color=GRY, lw=1.0)
        wire(ax, x_in_x-0.08, ry, x_in_x-0.08, (ry+ay)/2+0.22, color=GRY, lw=1.0)
        wire(ax, x_in_x-0.08, (ry+ay)/2+0.22, x_in_x, (ry+ay)/2+0.22, color=GRY, lw=1.0)
        # sel
        wire(ax, sel_x_out, ay, xor_x-0.55, ay, color=BLU, lw=1.0)
        wire(ax, xor_x-0.55, ay, xor_x-0.55, (ry+ay)/2-0.22, color=BLU, lw=1.0)
        wire(ax, xor_x-0.55, (ry+ay)/2-0.22, x_in_x, (ry+ay)/2-0.22, color=BLU, lw=1.0)
        # output
        wire(ax, x_out_x, (ry+ay)/2, 12.5, (ry+ay)/2, color=TGRN, lw=1.3)
        dot(ax, 12.5, (ry+ay)/2, color=TGRN)

    # ── Output block ──
    out_ys = [(r_y[i]+and_ys[i])/2 for i in range(7)]
    block(ax, 12.6, min(out_ys)-0.5, 1.2, max(out_ys)-min(out_ys)+1.0,
          '#E8F5E9', GRN, 'c[6:0]\ncorrig.', fs=7.5)
    for i, cy in enumerate(out_ys):
        ax.add_patch(FancyBboxPatch((12.7, cy-0.2), 1.0, 0.4,
                     boxstyle='square,pad=0.02', fc='#C8E6C9', ec=GRN, lw=1.0))
        lbl(ax, 13.2, cy, f'c{i+1}', color=GRN, size=8)

    ax.text(0.01, 0.02,
            'sel_i = AND(!s4^cfg4, !s2^cfg2, !s1^cfg1)  |  c_i = r_i XOR sel_i',
            transform=ax.transAxes, fontsize=7.5, color='#666', style='italic')

    plt.tight_layout()
    plt.savefig('fig_schem_corrector.png', dpi=150, bbox_inches='tight')
    print('Salvo: fig_schem_corrector.png')
    plt.close()


# =============================================================================
# Figura 4: Visao completa do chip (blocos)
# =============================================================================
def fig_chip_full():
    fig, ax = plt.subplots(figsize=(16, 7))
    ax.set_xlim(0, 16); ax.set_ylim(0, 7.5)
    ax.axis('off'); fig.patch.set_facecolor('#F5F8FC')
    ax.text(8, 7.2, 'HammingChip v1.0 — Esquemático Completo (Visão de Blocos)',
            ha='center', va='center', fontsize=13, fontweight='bold', color=DRK)
    ax.text(8, 6.8, 'Codec Hamming(7,4) | Encoder + Canal + Síndrome + Corrector | CMOS 0,35 µm | VDD=3,3V',
            ha='center', va='center', fontsize=9, color='#555', style='italic')

    # ── Blocos ──
    # Encoder
    block(ax, 0.3, 1.2, 2.5, 4.0, '#D0E8FF', BLU, 'ENCODER', 'Hamming(7,4)\nd[3:0]→cw[6:0]', fs=10)
    # Canal
    block(ax, 4.5, 2.0, 2.5, 2.5, '#FFF9C4', '#AA8800', 'CANAL\nRUIDOSO', '0/1 erro de bit', fs=9)
    # Syndrome
    block(ax, 8.5, 1.2, 2.5, 4.0, '#FFF3E0', ORG, 'GERADOR DE\nSÍNDROME', 'rx[6:0]→s[2:0]', fs=9)
    # Corrector
    block(ax, 12.2, 1.2, 3.3, 4.0, '#E8F5E9', GRN, 'CORRETOR\nDE ERRO', 's[2:0]+rx→c[6:0]', fs=9)

    # ── Fios ──
    # d[3:0] → Encoder
    for i, y in enumerate([4.6, 3.9, 3.2, 2.5]):
        ax.annotate('', xy=(0.3, y), xytext=(-0.4, y),
                    arrowprops=dict(arrowstyle='->', color=BLU, lw=1.5))
        lbl(ax, -0.6, y, f'd{i+1}', ha='right', color=BLU, size=9)

    # Encoder → Canal
    ax.annotate('', xy=(4.5, 3.2), xytext=(2.8, 3.2),
                arrowprops=dict(arrowstyle='->', color=BLU, lw=2.0))
    ax.text(3.65, 3.55, 'codeword[6:0]', ha='center', fontsize=8.5,
            color=BLU, fontweight='bold')

    # Canal → Syndrome
    ax.annotate('', xy=(8.5, 3.2), xytext=(7.0, 3.2),
                arrowprops=dict(arrowstyle='->', color=RED, lw=2.0))
    ax.text(7.75, 3.55, 'received[6:0]', ha='center', fontsize=8.5,
            color=RED, fontweight='bold')
    ax.text(7.75, 2.85, '(possível erro)', ha='center', fontsize=7.5,
            color='#AA4444', style='italic')

    # Syndrome → Corrector (sindrome)
    ax.annotate('', xy=(12.2, 4.0), xytext=(11.0, 4.0),
                arrowprops=dict(arrowstyle='->', color=ORG, lw=2.0))
    ax.text(11.6, 4.3, 'syndrome[2:0]', ha='center', fontsize=8.5,
            color=ORG, fontweight='bold')

    # Canal → Corrector (recebido direto)
    ax.annotate('', xy=(12.2, 2.5), xytext=(11.0, 2.5),
                arrowprops=dict(arrowstyle='->', color=GRY, lw=1.5))
    wire(ax, 9.75, 3.2, 9.75, 2.5, color=GRY, lw=1.4)
    wire(ax, 9.75, 2.5, 11.0, 2.5, color=GRY, lw=1.4)
    ax.text(11.6, 2.75, 'rx[6:0]', ha='center', fontsize=8.5, color=GRY)

    # Corrector → output
    for i, y in enumerate([4.6, 3.9, 3.2, 2.5]):
        ax.annotate('', xy=(16.0, y), xytext=(15.5, y),
                    arrowprops=dict(arrowstyle='->', color=GRN, lw=1.5))
        lbl(ax, 16.1, y, f'd{i+1}', ha='left', color=GRN, size=9)
    ax.annotate('', xy=(16.0, 1.8), xytext=(15.5, 1.8),
                arrowprops=dict(arrowstyle='->', color=ORG, lw=1.5))
    lbl(ax, 16.1, 1.8, 'err_flag', ha='left', color=ORG, size=8.5)

    # ── Detalhe das flags ──
    block(ax, 0.3, 0.1, 15.5, 0.8, '#FAFAFA', '#BBBBBB',
          'Flags: Z (zero_flag) | err_flag | syndrome[2:0]=posição do erro (0=sem erro)', fs=8.5)

    plt.tight_layout()
    plt.savefig('fig_schem_chip_full.png', dpi=150, bbox_inches='tight')
    print('Salvo: fig_schem_chip_full.png')
    plt.close()


# =============================================================================
if __name__ == '__main__':
    fig_encoder()
    fig_syndrome()
    fig_corrector()
    fig_chip_full()
    print('\nTodos os 4 esquematicos gerados.')
