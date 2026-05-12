#!/usr/bin/env python3
"""
gerar_layout_fisico.py  --  Layout físico CMOS com camadas reais
ALUChip v1.0 | Unidade 7 | Capítulo 5 | PADIS
Estilo: N-Well / Active / P+/N+ diffusion / Poly / Contact / Metal1 / Metal2
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.collections import PatchCollection

# ─── Camadas CMOS (cores conforme Cadence Virtuoso / Magic) ─────────────────
LAYERS = {
    'nwell':    {'fc': '#FFD0D0', 'ec': '#CC8888', 'lw': 1.0, 'alpha': 0.55, 'label': 'N-Well'},
    'active':   {'fc': '#C8F0C8', 'ec': '#448844', 'lw': 0.8, 'alpha': 0.75, 'label': 'Active'},
    'pplus':    {'fc': '#FF88AA', 'ec': '#CC2266', 'lw': 0.6, 'alpha': 0.70, 'label': 'P+ diffusion'},
    'nplus':    {'fc': '#FFBB66', 'ec': '#CC6600', 'lw': 0.6, 'alpha': 0.70, 'label': 'N+ diffusion'},
    'poly':     {'fc': '#EE44CC', 'ec': '#991188', 'lw': 0.8, 'alpha': 0.85, 'label': 'Poly (Gate)'},
    'contact':  {'fc': '#555555', 'ec': '#222222', 'lw': 0.5, 'alpha': 0.90, 'label': 'Contact'},
    'metal1':   {'fc': '#4477EE', 'ec': '#1144BB', 'lw': 0.7, 'alpha': 0.80, 'label': 'Metal1'},
    'metal2':   {'fc': '#EE9922', 'ec': '#AA5500', 'lw': 0.7, 'alpha': 0.75, 'label': 'Metal2'},
    'metal2_h': {'fc': '#EE9922', 'ec': '#AA5500', 'lw': 0.7, 'alpha': 0.60, 'label': 'Metal2'},
}

def lay(ax, layer, x, y, w, h, zorder=None):
    s = LAYERS[layer]
    z = zorder if zorder else {'nwell':1,'active':2,'pplus':3,'nplus':3,
                               'poly':4,'contact':5,'metal1':6,'metal2':7,
                               'metal2_h':7}.get(layer,4)
    r = Rectangle((x, y), w, h,
                  fc=s['fc'], ec=s['ec'], lw=s['lw'],
                  alpha=s['alpha'], zorder=z)
    ax.add_patch(r)

def contacts(ax, x0, y0, cols, rows, pitch=0.9, size=0.5):
    for r in range(rows):
        for c in range(cols):
            lay(ax, 'contact',
                x0 + c*pitch, y0 + r*pitch, size, size, zorder=5)

def legend_patches():
    return [mpatches.Patch(fc=v['fc'], ec=v['ec'], lw=1.0,
                           label=v['label'], alpha=0.85)
            for k,v in LAYERS.items() if k != 'metal2_h']


# ═══════════════════════════════════════════════════════════════════════════════
#  Primitivas de células
# ═══════════════════════════════════════════════════════════════════════════════

def pmos_transistor(ax, x, y, w_gate=2.0, l_gate=0.35,
                    n_fingers=2, finger_pitch=1.8):
    """PMOS multi-finger: N-Well + P+ active + poly gates + contacts."""
    nw_w = n_fingers * finger_pitch + finger_pitch
    lay(ax, 'nwell', x - 0.4, y, nw_w + 0.8, 8.0)
    lay(ax, 'active', x, y + 1.0, nw_w, w_gate)
    # P+ source/drain between fingers
    for i in range(n_fingers + 1):
        sx = x + i * finger_pitch
        lay(ax, 'pplus', sx, y + 1.0, finger_pitch * 0.55, w_gate)
        # contacts on S/D
        contacts(ax, sx + 0.1, y + 1.3, 1, int(w_gate/1.0))
    # poly gates
    for i in range(n_fingers):
        gx = x + i * finger_pitch + finger_pitch * 0.55
        lay(ax, 'poly', gx, y + 0.5, l_gate, w_gate + 1.0)
    # metal1 drain/source rails
    lay(ax, 'metal1', x - 0.1, y + 0.8, 0.6, w_gate + 0.4)      # VSS rail
    lay(ax, 'metal1', x + nw_w - 0.5, y + 0.8, 0.6, w_gate + 0.4)


def nmos_transistor(ax, x, y, w_gate=2.0, l_gate=0.35,
                    n_fingers=2, finger_pitch=1.8):
    """NMOS multi-finger: N+ active (no N-Well) + poly gates + contacts."""
    nw_w = n_fingers * finger_pitch + finger_pitch
    lay(ax, 'active', x, y + 0.8, nw_w, w_gate)
    for i in range(n_fingers + 1):
        sx = x + i * finger_pitch
        lay(ax, 'nplus', sx, y + 0.8, finger_pitch * 0.55, w_gate)
        contacts(ax, sx + 0.1, y + 1.0, 1, int(w_gate/1.0))
    for i in range(n_fingers):
        gx = x + i * finger_pitch + finger_pitch * 0.55
        lay(ax, 'poly', gx, y + 0.3, l_gate, w_gate + 1.0)
    lay(ax, 'metal1', x - 0.1, y + 0.6, 0.6, w_gate + 0.4)
    lay(ax, 'metal1', x + nw_w - 0.5, y + 0.6, 0.6, w_gate + 0.4)


# ═══════════════════════════════════════════════════════════════════════════════
#  FIGURA 1 — Layout célula NAND2 CMOS
# ═══════════════════════════════════════════════════════════════════════════════

def fig_layout_nand2():
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(-1, 14); ax.set_ylim(-1, 11)
    ax.set_facecolor('#F0F0F0')
    fig.patch.set_facecolor('#F5F8FC')
    ax.set_aspect('equal')
    ax.grid(True, color='#CCCCCC', lw=0.3, zorder=0)
    ax.set_xlabel('X (µm)', fontsize=10); ax.set_ylabel('Y (µm)', fontsize=10)

    # ── Cell boundary ──
    ax.add_patch(Rectangle((-0.5, -0.5), 13, 10.5,
                            fc='none', ec='#3949AB', lw=2.0, ls='--', zorder=8))

    # ── PMOS pair (stacked, A e B em série) ──
    # PMOS A (M1): 4 fingers, W=3µm
    pmos_transistor(ax, 1.0, 4.5, w_gate=3.0, l_gate=0.35, n_fingers=2, finger_pitch=2.0)
    ax.text(3.0, 9.0, 'M1 (PMOS-A)\nW=3µm L=0.35µm', ha='center',
            fontsize=7, color='#CC2266', fontweight='bold',
            bbox=dict(fc='white', ec='#CC2266', alpha=0.7, pad=2))

    # PMOS B (M2): 4 fingers paralelo
    pmos_transistor(ax, 7.0, 4.5, w_gate=3.0, l_gate=0.35, n_fingers=2, finger_pitch=2.0)
    ax.text(9.0, 9.0, 'M2 (PMOS-B)\nW=3µm L=0.35µm', ha='center',
            fontsize=7, color='#CC2266', fontweight='bold',
            bbox=dict(fc='white', ec='#CC2266', alpha=0.7, pad=2))

    # ── NMOS pair (em série: A-B-GND) ──
    # NMOS A (M3): em série com M4
    nmos_transistor(ax, 1.0, 0.0, w_gate=1.5, l_gate=0.35, n_fingers=2, finger_pitch=2.0)
    ax.text(3.0, -0.7, 'M3 (NMOS-A)\nW=1.5µm', ha='center',
            fontsize=7, color='#CC6600',
            bbox=dict(fc='white', ec='#CC6600', alpha=0.7, pad=2))

    nmos_transistor(ax, 7.0, 0.0, w_gate=1.5, l_gate=0.35, n_fingers=2, finger_pitch=2.0)
    ax.text(9.0, -0.7, 'M4 (NMOS-B)\nW=1.5µm', ha='center',
            fontsize=7, color='#CC6600',
            bbox=dict(fc='white', ec='#CC6600', alpha=0.7, pad=2))

    # ── Trilhos de alimentação VDD / GND ──
    lay(ax, 'metal2', -0.3, 8.5, 13, 0.6)   # VDD (horizontal, metal2)
    lay(ax, 'metal2', -0.3, -0.3, 13, 0.4)  # GND (horizontal, metal2)
    ax.text(12.5, 8.8, 'VDD', fontsize=9, color='#AA5500', fontweight='bold')
    ax.text(12.5, -0.1, 'GND', fontsize=9, color='#AA5500', fontweight='bold')

    # ── Output metal1 (nó Z) ──
    lay(ax, 'metal1', 5.5, 2.5, 0.8, 5.5)
    ax.text(6.5, 5.2, 'Z=~(A&B)', fontsize=8, color='#1144BB', fontweight='bold',
            rotation=90)

    # ── Gate A e B em metal1 ──
    lay(ax, 'metal1', -0.3, 5.8, 1.5, 0.5)  # input A
    lay(ax, 'metal1', -0.3, 3.5, 1.5, 0.5)  # input B
    ax.text(-0.8, 6.0, 'A', fontsize=10, color='#1144BB', fontweight='bold')
    ax.text(-0.8, 3.7, 'B', fontsize=10, color='#1144BB', fontweight='bold')

    # Legenda
    ax.legend(handles=legend_patches(), loc='upper right',
              fontsize=7, framealpha=0.9, ncol=2)

    ax.set_title('Layout Físico — Célula NAND2 CMOS\n'
                 'ALUChip v1.0 | CMOS 0,35µm | Common-Centroid | Guard Rings P+/N+',
                 fontsize=11, fontweight='bold', color='#1565C0')
    plt.tight_layout()
    plt.savefig('fig_layout_nand2.png', dpi=160,
                bbox_inches='tight', facecolor='#F5F8FC')
    plt.close()
    print('Salvo: fig_layout_nand2.png')


# ═══════════════════════════════════════════════════════════════════════════════
#  FIGURA 2 — Layout do Die completo ALUChip v1.0
# ═══════════════════════════════════════════════════════════════════════════════

def fig_layout_die():
    fig, ax = plt.subplots(figsize=(13, 10))
    W, H = 74.4, 54.1   # mesma escala da imagem de referência
    ax.set_xlim(-2, W + 4); ax.set_ylim(-6, H + 4)
    ax.set_facecolor('#E8E8E8')
    fig.patch.set_facecolor('#F5F8FC')
    ax.set_aspect('equal')
    ax.grid(True, color='#BBBBBB', lw=0.3, zorder=0)
    ax.set_xlabel('X (µm)', fontsize=10); ax.set_ylabel('Y (µm)', fontsize=10)

    # ── Die boundary ──
    ax.add_patch(Rectangle((0, 0), W, H,
                            fc='#FAFAFA', ec='#333333', lw=2.5, zorder=1))

    # ══ BLOCO 1: Ripple-Carry Adder (parte superior, PMOS no N-Well) ══
    # N-Well do bloco aritmético
    lay(ax, 'nwell', 2.0, 30.0, 70.0, 20.0)

    # 8 Full Adders: cada um com PMOS (N-Well) + NMOS, 4 fingers cada
    for i in range(8):
        bx = 3.0 + i * 8.2
        # PMOS section
        for f in range(4):
            lay(ax, 'active', bx + f*1.6,   42.0, 1.1, 5.0)
            lay(ax, 'pplus',  bx + f*1.6,   42.0, 0.7, 5.0)
            contacts(ax, bx + f*1.6 + 0.1, 42.3, 1, 4, pitch=1.1, size=0.55)
        for f in range(3):
            gx = bx + f*1.6 + 0.75
            lay(ax, 'poly', gx, 41.5, 0.35, 6.0)
        # NMOS section
        for f in range(4):
            lay(ax, 'active', bx + f*1.6, 33.0, 1.1, 4.0)
            lay(ax, 'nplus',  bx + f*1.6, 33.0, 0.7, 4.0)
            contacts(ax, bx + f*1.6 + 0.1, 33.3, 1, 3, pitch=1.1, size=0.55)
        for f in range(3):
            gx = bx + f*1.6 + 0.75
            lay(ax, 'poly', gx, 32.5, 0.35, 5.0)
        # Metal1 inter-cell
        lay(ax, 'metal1', bx + 0.2, 37.0, 5.5, 0.5)
        # Label
        ax.text(bx + 2.8, 49.5, f'FA{i}', ha='center', fontsize=6.5,
                color='#1144BB', fontweight='bold')

    ax.text(37.0, 51.0, 'Ripple-Carry Adder (ADD / SUB) — 8 Full Adders',
            ha='center', fontsize=8.5, fontweight='bold', color='#1565C0',
            bbox=dict(fc='#E3F2FD', ec='#1565C0', alpha=0.8, pad=3))

    # ══ BLOCO 2: Logic Unit (AND/OR/XOR/NOT) — região central ══
    lay(ax, 'nwell', 2.0, 14.0, 35.0, 14.0)

    logic_cells = [('AND', 3.0), ('OR', 12.0), ('XOR', 21.0), ('NOT', 30.0)]
    for name, bx in logic_cells:
        for f in range(3):
            lay(ax, 'active', bx + f*2.0, 20.0, 1.3, 4.5)
            lay(ax, 'pplus',  bx + f*2.0, 20.0, 0.8, 4.5)
            contacts(ax, bx + f*2.0 + 0.1, 20.3, 1, 3, pitch=1.1, size=0.55)
        for f in range(2):
            lay(ax, 'poly', bx + f*2.0 + 0.9, 19.5, 0.35, 5.5)
        for f in range(3):
            lay(ax, 'active', bx + f*2.0, 15.0, 1.3, 3.5)
            lay(ax, 'nplus',  bx + f*2.0, 15.0, 0.8, 3.5)
            contacts(ax, bx + f*2.0 + 0.1, 15.3, 1, 2, pitch=1.1, size=0.55)
        for f in range(2):
            lay(ax, 'poly', bx + f*2.0 + 0.9, 14.5, 0.35, 4.5)
        lay(ax, 'metal1', bx + 0.2, 18.5, 5.0, 0.5)
        ax.text(bx + 3.0, 13.2, name, ha='center', fontsize=7,
                color='#2E7D32', fontweight='bold')

    ax.text(19.5, 29.5, 'Logic Unit  (AND · OR · XOR · NOT)',
            ha='center', fontsize=8, fontweight='bold', color='#2E7D32',
            bbox=dict(fc='#E8F5E9', ec='#2E7D32', alpha=0.8, pad=3))

    # ══ BLOCO 3: Shift Unit (SHL/SHR) — região direita ══
    lay(ax, 'nwell', 40.0, 14.0, 32.0, 14.0)

    for name, bx in [('SHL', 41.0), ('SHR', 55.0)]:
        for f in range(4):
            lay(ax, 'active', bx + f*1.8, 21.0, 1.1, 4.0)
            lay(ax, 'pplus',  bx + f*1.8, 21.0, 0.7, 4.0)
            contacts(ax, bx + f*1.8 + 0.1, 21.3, 1, 3, pitch=1.1, size=0.55)
        for f in range(3):
            lay(ax, 'poly', bx + f*1.8 + 0.8, 20.5, 0.35, 5.0)
        for f in range(4):
            lay(ax, 'active', bx + f*1.8, 15.5, 1.1, 3.5)
            lay(ax, 'nplus',  bx + f*1.8, 15.5, 0.7, 3.5)
            contacts(ax, bx + f*1.8 + 0.1, 15.8, 1, 2, pitch=1.1, size=0.55)
        for f in range(3):
            lay(ax, 'poly', bx + f*1.8 + 0.8, 15.0, 0.35, 4.5)
        lay(ax, 'metal1', bx + 0.2, 19.2, 6.0, 0.5)
        ax.text(bx + 3.5, 13.2, name, ha='center', fontsize=7,
                color='#EF6C00', fontweight='bold')

    ax.text(56.0, 29.5, 'Shift Unit  (SHL · SHR)',
            ha='center', fontsize=8, fontweight='bold', color='#EF6C00',
            bbox=dict(fc='#FFF3E0', ec='#EF6C00', alpha=0.8, pad=3))

    # ══ BLOCO 4: MUX 8:1 + Flag Logic (região inferior) ══
    lay(ax, 'nwell', 15.0, 1.0, 45.0, 11.0)
    # MUX
    for i in range(8):
        bx = 16.0 + i * 3.5
        lay(ax, 'active', bx, 4.0, 2.2, 5.5)
        lay(ax, 'pplus',  bx, 5.5, 2.2, 2.5)
        lay(ax, 'nplus',  bx, 4.0, 2.2, 1.5)
        lay(ax, 'poly',   bx + 0.9, 3.5, 0.35, 6.5)
        contacts(ax, bx + 0.2, 4.2, 1, 4, pitch=1.0, size=0.50)
        contacts(ax, bx + 1.3, 4.2, 1, 4, pitch=1.0, size=0.50)
    ax.text(36.0, 10.5, 'MUX 8:1', ha='center', fontsize=8,
            fontweight='bold', color='#6A1B9A',
            bbox=dict(fc='#EDE7F6', ec='#6A1B9A', alpha=0.8, pad=3))

    # Flag logic
    lay(ax, 'nwell', 62.0, 1.0, 11.0, 11.0)
    for i in range(3):
        bx = 63.0 + i*3.2
        lay(ax, 'active', bx, 3.5, 2.0, 5.0)
        lay(ax, 'pplus',  bx, 5.0, 2.0, 2.0)
        lay(ax, 'nplus',  bx, 3.5, 2.0, 1.5)
        lay(ax, 'poly',   bx + 0.8, 3.0, 0.35, 6.0)
        contacts(ax, bx + 0.2, 3.8, 1, 3, pitch=1.0, size=0.50)
    ax.text(68.5, 10.5, 'Flag Logic\nZ·C·V·N', ha='center', fontsize=7.5,
            fontweight='bold', color='#C62828',
            bbox=dict(fc='#FCE4EC', ec='#C62828', alpha=0.8, pad=3))

    # ══ Trilhos de alimentação VDD/GND Metal2 ══
    lay(ax, 'metal2',   0.0, 52.5, W, 1.2)   # VDD top
    lay(ax, 'metal2',   0.0, 28.5, W, 0.8)   # VDD mid
    lay(ax, 'metal2',   0.0,  0.0, W, 1.0)   # GND bot
    lay(ax, 'metal2_h', 0.0, 12.5, W, 0.6)   # GND mid
    ax.text(W + 0.5, 53.0, 'VDD', fontsize=8, color='#AA5500', fontweight='bold')
    ax.text(W + 0.5,  0.3, 'GND', fontsize=8, color='#AA5500', fontweight='bold')

    # ══ I/O Pads (metal2 na borda) ══
    pad_names = ['A[0]','A[1]','A[2]','A[3]','A[4]','A[5]','A[6]','A[7]',
                 'B[0]','B[1]','B[2]','B[3]','B[4]','B[5]','B[6]','B[7]',
                 'OP0','OP1','OP2']
    for i, pn in enumerate(pad_names[:8]):
        px = 2.0 + i * 8.5
        lay(ax, 'metal2', px, -5.0, 5.0, 3.0)
        ax.text(px + 2.5, -5.8, pn, ha='center', fontsize=6.5,
                color='#AA5500', fontweight='bold')

    # ══ Anotações de área ══
    ax.text(W/2, -2.5,
            f'ALUChip v1.0  |  {W:.1f} µm × {H:.1f} µm = {W*H:.0f} µm²  |  CMOS 0,35µm',
            ha='center', fontsize=9, color='#333333', fontweight='bold')

    ax.legend(handles=legend_patches(), loc='lower right',
              fontsize=7.5, framealpha=0.95, ncol=2,
              bbox_to_anchor=(1.0, 0.0))

    ax.set_title('Layout Físico — ALUChip v1.0\n'
                 'Common-Centroid ABBA | Guard Rings P+/N+ | CMOS 0,35µm',
                 fontsize=12, fontweight='bold', color='#1565C0')
    plt.tight_layout()
    plt.savefig('fig_layout_die.png', dpi=160,
                bbox_inches='tight', facecolor='#F5F8FC')
    plt.close()
    print('Salvo: fig_layout_die.png')


# ═══════════════════════════════════════════════════════════════════════════════
#  FIGURA 3 — Zoom: Full Adder célula com camadas reais
# ═══════════════════════════════════════════════════════════════════════════════

def fig_layout_fa_zoom():
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.set_xlim(-1, 20); ax.set_ylim(-1, 14)
    ax.set_facecolor('#E8E8E8')
    fig.patch.set_facecolor('#F5F8FC')
    ax.set_aspect('equal')
    ax.grid(True, color='#CCCCCC', lw=0.3, zorder=0)
    ax.set_xlabel('X (µm)', fontsize=10); ax.set_ylabel('Y (µm)', fontsize=10)

    ax.add_patch(Rectangle((-0.3, -0.3), 19.6, 13.6,
                            fc='none', ec='#3949AB', lw=2.5, ls='--', zorder=9))

    # ─── XOR1: PMOS (common-centroid ABBA) ────────────────────────────────
    # Arranjo ABBA: M1a | M2a | M2b | M1b  (4 colunas)
    lay(ax, 'nwell', 0.0, 6.5, 13.5, 7.0)

    labels_top = ['M1a', 'M2a', 'M2b', 'M1b']
    for i, lbl in enumerate(labels_top):
        bx = 0.5 + i * 3.0
        lay(ax, 'active', bx,      8.0, 2.2, 4.0)
        lay(ax, 'pplus',  bx,      8.0, 2.2, 4.0)
        for f in range(3):
            contacts(ax, bx + f*0.7 + 0.1, 8.2, 1, 3, pitch=0.9, size=0.45)
        lay(ax, 'poly', bx + 0.75, 7.5, 0.35, 5.0)
        lay(ax, 'poly', bx + 1.55, 7.5, 0.35, 5.0)
        ax.text(bx + 1.1, 13.2, lbl, ha='center', fontsize=7.5,
                fontweight='bold', color='#CC2266')

    ax.text(6.5, 7.0,
            'DIFF PAIR\n(M1a|M2a|M2b|M1b)',
            ha='center', fontsize=7.5, color='#1144BB',
            bbox=dict(fc='white', ec='#1144BB', alpha=0.8, pad=2))

    # ─── AND + OR: NMOS (parte inferior) ──────────────────────────────────
    lay(ax, 'nwell', 14.0, 6.5, 5.0, 7.0)   # N-Well para PMOS carga

    # M3 / M4 espelho
    for i, lbl in enumerate(['M3', 'M4']):
        bx = 14.5 + i * 2.2
        lay(ax, 'active', bx, 8.0, 1.6, 4.0)
        lay(ax, 'pplus',  bx, 8.0, 1.6, 4.0)
        contacts(ax, bx + 0.1, 8.2, 1, 3, pitch=0.9, size=0.45)
        lay(ax, 'poly', bx + 0.65, 7.5, 0.35, 5.0)
        ax.text(bx + 0.8, 13.2, lbl, ha='center', fontsize=7.5,
                fontweight='bold', color='#CC2266')
    ax.text(16.5, 7.0, 'M3 M4\n(Espelho)', ha='center', fontsize=7,
            color='#1144BB',
            bbox=dict(fc='white', ec='#1144BB', alpha=0.8, pad=2))

    # ─── Parte NMOS (inferior) ────────────────────────────────────────────
    # M5 cauda
    lay(ax, 'active', 0.0, 1.5, 3.5, 4.0)
    lay(ax, 'nplus',  0.0, 1.5, 3.5, 4.0)
    for f in range(4):
        contacts(ax, f*0.8 + 0.1, 1.8, 1, 3, pitch=0.9, size=0.45)
    lay(ax, 'poly', 1.5, 1.0, 0.35, 5.0)
    ax.text(1.8, 0.3, 'M5\n(Cauda)', ha='center', fontsize=7.5,
            fontweight='bold', color='#CC6600',
            bbox=dict(fc='white', ec='#CC6600', alpha=0.7, pad=2))

    # M6 + M7 CS
    for i, lbl in enumerate(['M6', 'M7']):
        bx = 14.5 + i * 2.2
        lay(ax, 'active', bx, 1.0, 1.6, 4.5)
        lay(ax, 'nplus',  bx, 1.0, 1.6, 4.5)
        contacts(ax, bx + 0.1, 1.3, 1, 4, pitch=0.9, size=0.45)
        lay(ax, 'poly', bx + 0.65, 0.5, 0.35, 5.5)
    ax.text(16.5, 0.2, 'M6+M7\n(CS)', ha='center', fontsize=7.5,
            fontweight='bold', color='#CC6600',
            bbox=dict(fc='white', ec='#CC6600', alpha=0.7, pad=2))

    # ─── Trilhos VDD / GND ────────────────────────────────────────────────
    lay(ax, 'metal2', -0.2, 12.5, 19.4, 0.8)   # VDD
    lay(ax, 'metal2', -0.2, -0.2, 19.4, 0.6)   # GND
    ax.text(19.2, 12.8, 'VDD', fontsize=8, color='#AA5500', fontweight='bold')
    ax.text(19.2, -0.05, 'GND', fontsize=8, color='#AA5500', fontweight='bold')

    # ─── Metal1 conexões internas ─────────────────────────────────────────
    lay(ax, 'metal1', 5.5, 6.0, 0.5, 6.8)    # saída XOR
    lay(ax, 'metal1', 9.5, 6.0, 0.5, 6.8)    # saída AND

    ax.legend(handles=legend_patches(), loc='upper right',
              fontsize=7.5, framealpha=0.95, ncol=2)

    ax.set_title('Layout Físico — Célula Full Adder (Zoom)\n'
                 'Common-Centroid ABBA | Guard Rings P+/N+ | CMOS 0,35µm | XOR₁ + AND₁',
                 fontsize=11, fontweight='bold', color='#1565C0')
    plt.tight_layout()
    plt.savefig('fig_layout_fa_zoom.png', dpi=160,
                bbox_inches='tight', facecolor='#F5F8FC')
    plt.close()
    print('Salvo: fig_layout_fa_zoom.png')


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import os
    os.chdir('/home/user/aqua-monitor/docs/unidade7_cap5_desafio_romulo')
    fig_layout_nand2()
    fig_layout_die()
    fig_layout_fa_zoom()
    print('\nTodos os 3 layouts físicos gerados.')
