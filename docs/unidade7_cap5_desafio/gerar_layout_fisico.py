#!/usr/bin/env python3
"""
gerar_layout_fisico.py  --  Layout fisico CMOS HammingChip v1.0
Unidade 7 | Capitulo 5 | PADIS
Autor: Matheus Serrao Uchoa  |  Prof.: Thiago Brito
Processo: CMOS 0,35um | VDD=3,3V
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle

# ─── Camadas CMOS (estilo Cadence Virtuoso) ───────────────────────────────────
LAYERS = {
    'nwell':   {'fc': '#FFD0D0', 'ec': '#CC8888', 'lw': 1.2, 'alpha': 0.60, 'zorder': 1},
    'active':  {'fc': '#C8F0C8', 'ec': '#448844', 'lw': 1.0, 'alpha': 0.80, 'zorder': 2},
    'pplus':   {'fc': '#FF88AA', 'ec': '#CC2266', 'lw': 1.0, 'alpha': 0.85, 'zorder': 3},
    'nplus':   {'fc': '#FFBB66', 'ec': '#CC6600', 'lw': 1.0, 'alpha': 0.85, 'zorder': 3},
    'poly':    {'fc': '#EE44CC', 'ec': '#991188', 'lw': 1.2, 'alpha': 0.85, 'zorder': 4},
    'contact': {'fc': '#555555', 'ec': '#222222', 'lw': 0.6, 'alpha': 1.00, 'zorder': 5},
    'metal1':  {'fc': '#4477EE', 'ec': '#1144BB', 'lw': 1.0, 'alpha': 0.80, 'zorder': 6},
    'metal2':  {'fc': '#EE9922', 'ec': '#AA5500', 'lw': 1.2, 'alpha': 0.85, 'zorder': 7},
}

def lay(ax, layer, x, y, w, h):
    s = LAYERS[layer]
    ax.add_patch(Rectangle((x, y), w, h,
                 fc=s['fc'], ec=s['ec'], lw=s['lw'],
                 alpha=s['alpha'], zorder=s['zorder']))

def contacts(ax, x0, y0, cols, rows, pitch=0.35, size=0.22):
    for r in range(rows):
        for c in range(cols):
            cx = x0 + c*pitch
            cy = y0 + r*pitch
            s = LAYERS['contact']
            ax.add_patch(Rectangle((cx-size/2, cy-size/2), size, size,
                         fc=s['fc'], ec=s['ec'], lw=s['lw'],
                         alpha=s['alpha'], zorder=s['zorder']))

def legend(ax, x0=0.62, y0=0.02):
    items = [
        ('N-Well',       LAYERS['nwell']['fc'],   LAYERS['nwell']['ec']),
        ('Active',       LAYERS['active']['fc'],  LAYERS['active']['ec']),
        ('P+ diffusion', LAYERS['pplus']['fc'],   LAYERS['pplus']['ec']),
        ('N+ diffusion', LAYERS['nplus']['fc'],   LAYERS['nplus']['ec']),
        ('Poly (Gate)',  LAYERS['poly']['fc'],    LAYERS['poly']['ec']),
        ('Contact',      LAYERS['contact']['fc'], LAYERS['contact']['ec']),
        ('Metal1',       LAYERS['metal1']['fc'],  LAYERS['metal1']['ec']),
        ('Metal2',       LAYERS['metal2']['fc'],  LAYERS['metal2']['ec']),
    ]
    for i, (name, fc, ec) in enumerate(items):
        col = i // 4; row = i % 4
        xi = x0 + col*0.19; yi = y0 + (3-row)*0.028
        ax.add_patch(Rectangle((xi, yi), 0.025, 0.018, fc=fc, ec=ec, lw=1.0,
                     transform=ax.transAxes, zorder=10, clip_on=False))
        ax.text(xi+0.030, yi+0.009, name, transform=ax.transAxes,
                fontsize=7.5, va='center', color='#333')


# =============================================================================
# Figura 1: Celula XOR2 CMOS
# 4 transistores: 2 PMOS (N-Well) + 2 NMOS (substrato P)
# Configuracao: (A ^ B) = (!A & B) | (A & !B)  -- implementacao CMOS complementar
# =============================================================================
def fig_xor2():
    fig, ax = plt.subplots(figsize=(13, 10))
    ax.set_xlim(-1, 15); ax.set_ylim(-1.5, 11)
    ax.set_xlabel('X (µm)', fontsize=10); ax.set_ylabel('Y (µm)', fontsize=10)
    ax.set_facecolor('#F0F2F5'); fig.patch.set_facecolor('#F0F2F5')
    ax.grid(True, color='white', lw=0.5, alpha=0.6)
    ax.set_title('Layout Físico — Célula XOR2 CMOS\n'
                 'HammingChip v1.0 | CMOS 0,35µm | Common-Centroid ABBA | Guard Rings P+/N+',
                 fontsize=11, fontweight='bold', color='#1A237E', pad=10)

    # ── N-Well (PMOS) ──
    lay(ax, 'nwell',  0.5, 4.8, 13.0, 5.5)

    # ── Guard ring N+ (exterior, lado superior) ──
    lay(ax, 'nplus', 0.8, 9.6, 12.5, 0.45)
    contacts(ax, 1.0, 9.7, 10, 1, pitch=1.1, size=0.28)

    # ── PMOS ativos (4 transistores: M1a M2a M2b M1b — ABBA) ──
    pmos_xs = [1.2, 3.4, 7.2, 9.4]
    pmos_lbl = ['M1\n(PMOS-A)', 'M2\n(PMOS-B)', 'M2\n(PMOS-B)', 'M1\n(PMOS-A)']
    pmos_w = 'W=3µm L=0,35µm'
    for i, px in enumerate(pmos_xs):
        lay(ax, 'active', px, 5.5, 1.8, 3.8)
        lay(ax, 'pplus',  px, 5.5, 1.8, 3.8)
        contacts(ax, px+0.28, 5.85, 1, 3, pitch=0.9, size=0.30)
        contacts(ax, px+1.22, 5.85, 1, 3, pitch=0.9, size=0.30)
        ax.text(px+0.9, 9.25, pmos_lbl[i], ha='center', fontsize=7,
                color='#C62828', fontfamily='monospace',
                bbox=dict(fc='white', ec='#C62828', pad=1.5, lw=0.8))
    ax.text(6.4, 5.2, pmos_w, ha='center', fontsize=7.5, color='#C62828', style='italic')

    # ── Poly gates (PMOS) ──
    poly_pmos_xs = [2.8, 5.0, 8.8, 11.0]
    for px in poly_pmos_xs:
        lay(ax, 'poly', px, 5.2, 0.5, 4.5)
        contacts(ax, px+0.12, 5.4, 1, 2, pitch=1.2, size=0.30)

    # ── VDD rail (Metal2 top) ──
    lay(ax, 'metal2', 0.2, 9.8, 13.3, 0.6)
    ax.text(13.8, 10.1, 'VDD', fontsize=10, fontweight='bold',
            color=LAYERS['metal2']['ec'], va='center')

    # ── NMOS ativos (substrato P, parte inferior) ──
    nmos_xs = [1.2, 3.4, 7.2, 9.4]
    nmos_lbl = ['M3\n(NMOS-A)', 'M4\n(NMOS-B)', 'M4\n(NMOS-B)', 'M3\n(NMOS-A)']
    nmos_w = 'W=1,5µm'
    for i, nx in enumerate(nmos_xs):
        lay(ax, 'active', nx, 0.6, 1.8, 2.8)
        lay(ax, 'nplus',  nx, 0.6, 1.8, 2.8)
        contacts(ax, nx+0.28, 0.9, 1, 2, pitch=0.9, size=0.28)
        contacts(ax, nx+1.22, 0.9, 1, 2, pitch=0.9, size=0.28)
        ax.text(nx+0.9, -0.6, nmos_lbl[i], ha='center', fontsize=7,
                color='#EF6C00', fontfamily='monospace',
                bbox=dict(fc='white', ec='#EF6C00', pad=1.5, lw=0.8))
    ax.text(6.4, 0.3, nmos_w, ha='center', fontsize=7.5, color='#EF6C00', style='italic')

    # ── Poly gates (NMOS) ──
    poly_nmos_xs = [2.8, 5.0, 8.8, 11.0]
    for px in poly_nmos_xs:
        lay(ax, 'poly', px, 0.3, 0.5, 3.3)

    # ── GND rail (Metal2 bottom) ──
    lay(ax, 'metal2', 0.2, -1.0, 13.3, 0.6)
    ax.text(13.8, -0.7, 'GND', fontsize=10, fontweight='bold',
            color=LAYERS['metal2']['ec'], va='center')

    # ── Guard ring P+ (exterior, lado inferior) ──
    lay(ax, 'pplus', 0.8, -0.7, 12.5, 0.45)
    contacts(ax, 1.0, -0.6, 10, 1, pitch=1.1, size=0.28)

    # ── Inputs A, B (Metal1 vertical) ──
    lay(ax, 'metal1', 2.75, 0.2, 0.5, 9.4)
    lay(ax, 'metal1', 4.95, 0.2, 0.5, 9.4)
    ax.annotate('A', xy=(2.75, 5.0), xytext=(1.0, 5.0),
                arrowprops=dict(arrowstyle='->', color=LAYERS['metal1']['ec'], lw=2),
                fontsize=11, fontweight='bold', color=LAYERS['metal1']['ec'])
    ax.annotate('B', xy=(4.95, 3.5), xytext=(0.2, 3.5),
                arrowprops=dict(arrowstyle='->', color=LAYERS['metal1']['ec'], lw=2),
                fontsize=11, fontweight='bold', color=LAYERS['metal1']['ec'])

    # ── Output Z (Metal1 center vertical) ──
    lay(ax, 'metal1', 6.2, 0.5, 0.55, 8.0)
    ax.annotate('Z (A⊕B)', xy=(6.2, 7.5), xytext=(7.2, 7.5),
                arrowprops=dict(arrowstyle='->', color=LAYERS['metal1']['ec'], lw=2),
                fontsize=10, fontweight='bold', color=LAYERS['metal1']['ec'])

    # ── Cell boundary ──
    ax.add_patch(plt.Rectangle((0.2, -1.1), 13.4, 11.5, fill=False,
                 ec='#1565C0', lw=2.0, ls='--', zorder=8))

    legend(ax, x0=0.01, y0=0.01)
    plt.tight_layout()
    plt.savefig('fig_layout_xor2.png', dpi=150, bbox_inches='tight')
    print('Salvo: fig_layout_xor2.png')
    plt.close()


# =============================================================================
# Figura 2: Die completo HammingChip v1.0
# 52 µm x 38 µm (Hamming(7,4): encoder + syndrome gen + corrector + I/O)
# =============================================================================
def fig_hamming_die():
    W, H = 52.0, 38.0
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(-2, W+4); ax.set_ylim(-4, H+4)
    ax.set_xlabel('X (µm)', fontsize=10); ax.set_ylabel('Y (µm)', fontsize=10)
    ax.set_facecolor('#E8EBF0'); fig.patch.set_facecolor('#E8EBF0')
    ax.grid(True, color='white', lw=0.4, alpha=0.5)
    ax.set_title('Layout Físico — HammingChip v1.0\n'
                 'Common-Centroid ABBA | Guard Rings P+/N+ | CMOS 0,35µm',
                 fontsize=12, fontweight='bold', color='#1A237E', pad=10)

    # ── Die outline ──
    ax.add_patch(Rectangle((0, 0), W, H, fc='#F5F5F5', ec='#222', lw=2.5, zorder=0))

    # ── VDD / GND rails (Metal2) ──
    lay(ax, 'metal2', 0, H-1.8, W, 1.8)
    lay(ax, 'metal2', 0, 0,     W, 1.8)
    ax.text(W+0.4, H-0.9, 'VDD', fontsize=9, fontweight='bold',
            color=LAYERS['metal2']['ec'], va='center')
    ax.text(W+0.4, 0.9, 'GND', fontsize=9, fontweight='bold',
            color=LAYERS['metal2']['ec'], va='center')

    # ── N-Well global ──
    lay(ax, 'nwell', 0.5, H/2, W-1, H/2-2.5)

    # helper: cell tile (mini representacao de uma celula logica)
    def cell_tile(ax, x, y, cw=3.0, ch=5.5, col_p='pplus', col_n='nplus'):
        lay(ax, 'active', x, y+2.0, cw, 2.8)
        lay(ax, col_p,    x, y+2.0, cw, 2.8)
        lay(ax, 'poly',   x+cw*0.3, y+1.6, cw*0.12, 3.5)
        lay(ax, 'poly',   x+cw*0.65, y+1.6, cw*0.12, 3.5)
        lay(ax, 'active', x, y,     cw, 1.7)
        lay(ax, col_n,    x, y,     cw, 1.7)
        contacts(ax, x+0.3, y+2.4, 1, 2, pitch=0.8, size=0.22)
        contacts(ax, x+0.3, y+0.3, 1, 1, pitch=0.8, size=0.22)
        lay(ax, 'metal1', x+0.1, y+1.6, cw-0.2, 0.5)

    # ── Bloco ENCODER (top-left) ──
    enc_x, enc_y = 1.0, H-18.0
    ax.add_patch(Rectangle((enc_x, enc_y), 21, 14.5,
                 fc='#E3F2FD', ec='#1565C0', lw=1.8, zorder=1, alpha=0.5))
    ax.text(enc_x+10.5, enc_y+14.8,
            'Encoder Hamming(7,4)  —  3 × XOR2 (p1,p2,p4)',
            ha='center', fontsize=8.5, fontweight='bold', color='#1565C0')
    xor_cells_enc = [(1.5,  enc_y+1),  (5.5,  enc_y+1),  (9.5,  enc_y+1),
                     (1.5,  enc_y+7),  (5.5,  enc_y+7),  (9.5,  enc_y+7)]
    for cx, cy in xor_cells_enc:
        cell_tile(ax, cx, cy, cw=3.2, col_p='pplus', col_n='nplus')
    for i, (cx, cy) in enumerate(xor_cells_enc):
        ax.text(cx+1.6, cy+6.2, f'XOR{i+1}', ha='center', fontsize=7,
                color='#1565C0', fontfamily='monospace')

    # ── Bloco SYNDROME GENERATOR (top-right) ──
    syn_x, syn_y = 24.0, H-18.0
    ax.add_patch(Rectangle((syn_x, syn_y), 26, 14.5,
                 fc='#FFF3E0', ec='#EF6C00', lw=1.8, zorder=1, alpha=0.5))
    ax.text(syn_x+13.0, syn_y+14.8,
            'Gerador de Síndrome  —  9 × XOR2 (s1,s2,s4)',
            ha='center', fontsize=8.5, fontweight='bold', color='#EF6C00')
    xor_cells_syn = [(24.5, syn_y+1),  (28.5, syn_y+1),  (32.5, syn_y+1),
                     (24.5, syn_y+7),  (28.5, syn_y+7),  (32.5, syn_y+7),
                     (36.5, syn_y+1),  (40.5, syn_y+1),  (44.5, syn_y+1)]
    for cx, cy in xor_cells_syn:
        cell_tile(ax, cx, cy, cw=3.2, col_p='pplus', col_n='nplus')
    for i, (cx, cy) in enumerate(xor_cells_syn):
        ax.text(cx+1.6, cy+6.2, f'XOR{i+1}', ha='center', fontsize=7,
                color='#EF6C00', fontfamily='monospace')

    # ── Bloco CORRECTOR (bottom-left) ──
    cor_x, cor_y = 1.0, 2.0
    ax.add_patch(Rectangle((cor_x, cor_y), 30, 13.5,
                 fc='#E8F5E9', ec='#2E7D32', lw=1.8, zorder=1, alpha=0.5))
    ax.text(cor_x+15.0, cor_y+13.8,
            'Corretor de Erro  —  7×AND3 + 7×XOR2  (NOT+AND decoder)',
            ha='center', fontsize=8.5, fontweight='bold', color='#2E7D32')
    cor_cells = [(1.5, cor_y+1), (5.5, cor_y+1), (9.5, cor_y+1),
                 (13.5, cor_y+1), (17.5, cor_y+1), (21.5, cor_y+1), (25.5, cor_y+1),
                 (1.5, cor_y+7), (5.5, cor_y+7), (9.5, cor_y+7),
                 (13.5, cor_y+7), (17.5, cor_y+7), (21.5, cor_y+7), (25.5, cor_y+7)]
    for cx, cy in cor_cells:
        cell_tile(ax, cx, cy, cw=3.0, col_p='pplus', col_n='nplus')

    # ── Bloco I/O PADS (bottom-right) ──
    io_x, io_y = 33.0, 2.0
    ax.add_patch(Rectangle((io_x, io_y), 17, 13.5,
                 fc='#F3E5F5', ec='#6A1B9A', lw=1.8, zorder=1, alpha=0.5))
    ax.text(io_x+8.5, io_y+13.8, 'I/O Pads  —  d[3:0] | dout[3:0] | syndrome[2:0]',
            ha='center', fontsize=8.5, fontweight='bold', color='#6A1B9A')
    io_pads = [(33.5, io_y+1), (36.5, io_y+1), (39.5, io_y+1), (42.5, io_y+1),
               (33.5, io_y+7), (36.5, io_y+7), (39.5, io_y+7), (42.5, io_y+7),
               (45.5, io_y+7), (45.5, io_y+1)]
    pad_lbl = ['d0','d1','d2','d3','o0','o1','o2','o3','ef','—']
    for j, (px, py) in enumerate(io_pads):
        lay(ax, 'metal2', px, py, 2.2, 4.5)
        lay(ax, 'metal1', px+0.4, py+0.5, 1.4, 3.5)
        contacts(ax, px+0.6, py+0.8, 1, 3, pitch=0.8, size=0.25)
        ax.text(px+1.1, py-0.6, pad_lbl[j], ha='center', fontsize=7.5,
                color='#6A1B9A', fontweight='bold', fontfamily='monospace')

    # ── Roteamento Metal1 entre blocos ──
    for ry in [H-11.0, H-14.0]:
        lay(ax, 'metal1', 22.0, ry, 2.5, 0.5)   # ENC → SYN
    for ry in [H-12.0, H-15.0]:
        lay(ax, 'metal1', 22.0, ry, 1.5, 0.5)

    # ── Labels posicoes ──
    ax.text(W/2, -2.5,
            f'HammingChip v1.0  |  {W:.1f} µm × {H:.1f} µm = {W*H:.0f} µm²  |  CMOS 0,35µm',
            ha='center', fontsize=9, color='#555', style='italic')

    legend(ax, x0=0.55, y0=0.01)
    plt.tight_layout()
    plt.savefig('fig_layout_hamming_die.png', dpi=150, bbox_inches='tight')
    print('Salvo: fig_layout_hamming_die.png')
    plt.close()


# =============================================================================
# Figura 3: Zoom do bloco Encoder — Common-Centroid ABBA
# XOR2 implementado com 4 transistores CMOS (NAND-NAND ou transmission gate)
# =============================================================================
def fig_encoder_zoom():
    fig, ax = plt.subplots(figsize=(14, 11))
    ax.set_xlim(-1, 20); ax.set_ylim(-1.5, 14.5)
    ax.set_xlabel('X (µm)', fontsize=10); ax.set_ylabel('Y (µm)', fontsize=10)
    ax.set_facecolor('#F0F2F5'); fig.patch.set_facecolor('#F0F2F5')
    ax.grid(True, color='white', lw=0.5, alpha=0.6)
    ax.set_title('Layout Físico — Bloco Encoder (Zoom)\n'
                 'Common-Centroid ABBA | Guard Rings P+/N+ | CMOS 0,35µm | p1+p2+p4 XOR2',
                 fontsize=11, fontweight='bold', color='#1A237E', pad=10)

    # ── N-Well superior (PMOS) ──
    lay(ax, 'nwell', 0.3, 7.5, 18.8, 6.0)

    # ── VDD (Metal2) ──
    lay(ax, 'metal2', 0.0, 12.8, 19.2, 0.8)
    ax.text(19.5, 13.2, 'VDD', fontsize=9, fontweight='bold',
            color=LAYERS['metal2']['ec'], va='center')

    # ── GND (Metal2) ──
    lay(ax, 'metal2', 0.0, -1.0, 19.2, 0.8)
    ax.text(19.5, -0.6, 'GND', fontsize=9, fontweight='bold',
            color=LAYERS['metal2']['ec'], va='center')

    # ── Guard ring N+ (top) ──
    lay(ax, 'nplus', 0.4, 12.2, 18.4, 0.5)
    contacts(ax, 0.7, 12.3, 14, 1, pitch=1.2, size=0.28)

    # ── Guard ring P+ (bottom) ──
    lay(ax, 'pplus', 0.4, -0.7, 18.4, 0.5)
    contacts(ax, 0.7, -0.6, 14, 1, pitch=1.2, size=0.28)

    # ── PMOS em arranjo ABBA: M1a | M2a | M2b | M1b ──
    # cada transistor: active(pplus) + poly
    pmos_data = [
        (0.6,  'M1a', 'p1', '#1565C0'),
        (4.5,  'M2a', 'p2', '#2E7D32'),
        (9.2,  'M2b', 'p2', '#2E7D32'),
        (13.2, 'M1b', 'p1', '#1565C0'),
    ]
    for px, mn, pn, col in pmos_data:
        lay(ax, 'active', px, 8.0, 3.4, 3.8)
        lay(ax, 'pplus',  px, 8.0, 3.4, 3.8)
        contacts(ax, px+0.3, 8.3, 2, 3, pitch=1.0, size=0.28)
        lay(ax, 'poly', px+1.5, 7.6, 0.5, 4.8)
        ax.text(px+1.7, 7.2, mn, ha='center', fontsize=7.5,
                color=col, fontfamily='monospace',
                bbox=dict(fc='white', ec=col, pad=1.5, lw=0.8))
        ax.text(px+1.7, 6.7, f'({pn})', ha='center', fontsize=7,
                color=col, style='italic')

    # anotacao DIFF PAIR
    ax.annotate('DIFF PAIR\nM1a|M2a|M2b|M1b', xy=(9.0, 10.0), xytext=(5.5, 11.8),
                arrowprops=dict(arrowstyle='->', color=LAYERS['metal1']['ec'], lw=1.5),
                fontsize=8.5, color=LAYERS['metal1']['ec'], ha='center',
                bbox=dict(fc='#E3F2FD', ec=LAYERS['metal1']['ec'], pad=2))

    # ── Metal1 conexoes PMOS ──
    lay(ax, 'metal1', 4.9, 10.2, 0.6, 1.6)   # M1a-M2a
    lay(ax, 'metal1', 9.6, 10.2, 0.6, 1.6)   # M2b-M1b

    # ── NMOS 2 transistores (espelho) ──
    nmos_data = [
        (14.8, 'M3', '#C62828'),
        (17.0, 'M4', '#EF6C00'),
    ]
    for nx, mn, col in nmos_data:
        lay(ax, 'active', nx, 1.5, 1.8, 4.0)
        lay(ax, 'nplus',  nx, 1.5, 1.8, 4.0)
        contacts(ax, nx+0.28, 1.8, 1, 3, pitch=1.0, size=0.26)
        lay(ax, 'poly', nx+0.8, 1.2, 0.5, 4.8)
        ax.text(nx+0.9, 0.9, mn, ha='center', fontsize=8,
                color=col, fontfamily='monospace')
    ax.text(15.9, 7.0, 'M3 M4\n(Espelho)', ha='center', fontsize=8,
            color='#C62828', bbox=dict(fc='white', ec='#C62828', pad=2, lw=0.8))

    # ── Transistores de cauda NMOS ──
    lay(ax, 'active', 0.8, 1.2, 3.0, 4.2)
    lay(ax, 'nplus',  0.8, 1.2, 3.0, 4.2)
    contacts(ax, 1.0, 1.5, 2, 3, pitch=0.9, size=0.26)
    lay(ax, 'poly', 1.7, 0.9, 0.5, 4.8)
    ax.text(2.3, 0.5, 'M5\n(Cauda)', ha='center', fontsize=7.5,
            color=LAYERS['nplus']['ec'],
            bbox=dict(fc='white', ec=LAYERS['nplus']['ec'], pad=1.5, lw=0.8))

    lay(ax, 'active', 10.2, 1.2, 3.5, 4.2)
    lay(ax, 'nplus',  10.2, 1.2, 3.5, 4.2)
    contacts(ax, 10.5, 1.5, 2, 3, pitch=0.9, size=0.26)
    lay(ax, 'poly', 11.2, 0.9, 0.5, 4.8)
    lay(ax, 'poly', 12.8, 0.9, 0.5, 4.8)
    ax.text(11.9, 0.5, 'M6+M7\n(CS)', ha='center', fontsize=7.5,
            color=LAYERS['nplus']['ec'],
            bbox=dict(fc='white', ec=LAYERS['nplus']['ec'], pad=1.5, lw=0.8))

    # ── Cell boundary ──
    ax.add_patch(plt.Rectangle((0.0, -1.1), 19.2, 14.3, fill=False,
                 ec='#1565C0', lw=2.2, ls='--', zorder=9))

    legend(ax, x0=0.55, y0=0.01)
    plt.tight_layout()
    plt.savefig('fig_layout_encoder_zoom.png', dpi=150, bbox_inches='tight')
    print('Salvo: fig_layout_encoder_zoom.png')
    plt.close()


# =============================================================================
if __name__ == '__main__':
    fig_xor2()
    fig_hamming_die()
    fig_encoder_zoom()
    print('\nTodos os 3 layouts fisicos gerados.')
