#!/usr/bin/env python3
"""
gerar_esquematicos.py  --  Esquemáticos reais em nível de portas lógicas
ALUChip v1.0 | Unidade 7 | Capítulo 5 | PADIS
Autor: Rômulo da Silva Lira  |  Prof.: André Feitosa
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Arc, FancyArrowPatch, FancyBboxPatch
from matplotlib.path import Path
import matplotlib.patheffects as pe

# ─── Paleta ──────────────────────────────────────────────────────────────────
BLU  = '#1565C0'; TBLU = '#1E88E5'; GRN  = '#2E7D32'
RED  = '#C62828'; ORG  = '#EF6C00'; PUR  = '#6A1B9A'
GRY  = '#424242'; LGRY = '#ECEFF1'; WHT  = '#FFFFFF'

LW = 1.8   # espessura padrão das linhas

# ─── Primitivas de gate ──────────────────────────────────────────────────────

def wire(ax, x0, y0, x1, y1, color=GRY, lw=LW):
    ax.plot([x0, x1], [y0, y1], color=color, lw=lw, solid_capstyle='round')

def wire_h(ax, x0, x1, y, **kw):
    wire(ax, x0, y, x1, y, **kw)

def wire_v(ax, x, y0, y1, **kw):
    wire(ax, x, y0, x, y1, **kw)

def dot(ax, x, y, color=GRY, r=0.04):
    ax.add_patch(plt.Circle((x, y), r, color=color, zorder=5))

def label(ax, x, y, txt, ha='center', va='center', color=GRY, size=9, bold=False):
    ax.text(x, y, txt, ha=ha, va=va, color=color,
            fontsize=size, fontweight='bold' if bold else 'normal',
            fontfamily='monospace')

def bubble(ax, x, y, r=0.1, color=GRY):
    """Bolha de inversão (NOT circle)."""
    ax.add_patch(plt.Circle((x, y), r, ec=color, fc=WHT, lw=LW, zorder=4))

# ─── Corpos de gate (símbolo IEEE 91 / ANSI) ────────────────────────────────

def gate_and(ax, cx, cy, w=0.8, h=0.6, color=BLU, lbl='&'):
    """AND gate: retângulo + semicírculo à direita."""
    # corpo retangular
    ax.plot([cx-w/2, cx, cx], [cy-h/2, cy-h/2, cy+h/2],
            color=color, lw=LW, solid_capstyle='round')
    ax.plot([cx-w/2, cx-w/2], [cy-h/2, cy+h/2],
            color=color, lw=LW)
    ax.plot([cx-w/2, cx], [cy+h/2, cy+h/2],
            color=color, lw=LW)
    # semicírculo
    theta = np.linspace(-np.pi/2, np.pi/2, 60)
    ax.plot(cx + h/2*np.sin(theta), cy + h/2*np.cos(theta),
            color=color, lw=LW)
    ax.text(cx-0.05, cy, lbl, ha='center', va='center',
            fontsize=8, color=color, fontweight='bold')
    return cx + h/2, cy   # pino de saída

def gate_or(ax, cx, cy, w=0.8, h=0.6, color=GRN, lbl='≥1'):
    """OR gate: corpo com curvas características."""
    # curva traseira (entrada)
    t = np.linspace(-np.pi/2, np.pi/2, 60)
    back_r = 0.25
    ax.plot(cx - w/2 + back_r*(1-np.cos(t)), cy + (h/2)*np.sin(t),
            color=color, lw=LW)
    # borda superior e inferior
    # curva superior
    ts = np.linspace(0, np.pi/2, 40)
    ax.plot(cx - w/2 + (w + h/2)*np.sin(ts)**1.4,
            cy + h/2*np.cos(ts)**0.5, color=color, lw=LW)
    # curva inferior (espelho)
    ax.plot(cx - w/2 + (w + h/2)*np.sin(ts)**1.4,
            cy - h/2*np.cos(ts)**0.5, color=color, lw=LW)
    ax.text(cx, cy, lbl, ha='center', va='center',
            fontsize=8, color=color, fontweight='bold')
    return cx + w*0.85 + h/2*0.15, cy

def gate_xor(ax, cx, cy, w=0.8, h=0.6, color=ORG, lbl='=1'):
    """XOR gate: OR + curva extra na entrada."""
    x_out, y_out = gate_or(ax, cx, cy, w, h, color=color, lbl=lbl)
    # curva extra
    t = np.linspace(-np.pi/2, np.pi/2, 60)
    back_r = 0.25
    off = -0.18
    ax.plot(cx - w/2 + off + back_r*(1-np.cos(t)),
            cy + (h/2)*np.sin(t), color=color, lw=LW)
    return x_out, y_out

def gate_not(ax, cx, cy, w=0.5, h=0.45, color=RED, lbl='1'):
    """NOT gate: triângulo + bolha."""
    ax.plot([cx - w/2, cx - w/2, cx + w/2 - h/4],
            [cy - h/2,  cy + h/2,  cy],
            color=color, lw=LW, solid_capstyle='round')
    ax.plot([cx - w/2, cx + w/2 - h/4],
            [cy - h/2,  cy],
            color=color, lw=LW, solid_capstyle='round')
    ax.text(cx - 0.05, cy, lbl, ha='center', va='center',
            fontsize=8, color=color, fontweight='bold')
    bubble(ax, cx + w/2 - h/4 + 0.1, cy, r=0.09, color=color)
    return cx + w/2 + 0.1, cy


# ─── Figura 1: Full Adder (nível de portas) ──────────────────────────────────

def fig_full_adder():
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_xlim(-0.5, 13); ax.set_ylim(-0.5, 7)
    ax.axis('off'); fig.patch.set_facecolor('#F5F8FC')

    # ── Gate positions ──
    # XOR1 (A ^ B)
    xor1_cx, xor1_cy = 3.5, 5.0
    # AND1 (A & B)
    and1_cx, and1_cy = 3.5, 3.5
    # XOR2 ((A^B) ^ Cin) → SUM
    xor2_cx, xor2_cy = 6.5, 5.0
    # AND2 ((A^B) & Cin)
    and2_cx, and2_cy = 6.5, 3.5
    # OR (AND1 | AND2) → COUT
    or_cx, or_cy = 9.5, 3.0

    # ── Entradas ──
    # A
    wire_h(ax, 0.5, xor1_cx - 0.4, 5.3, color=BLU)
    wire_h(ax, 0.5, and1_cx - 0.4, 5.3, color=BLU)
    wire_v(ax, 0.5, 5.3, 3.2, color=BLU)
    dot(ax, 0.5, 5.3, color=BLU)
    label(ax, 0.2, 5.3, 'A', color=BLU, bold=True)

    # B
    wire_h(ax, 1.0, xor1_cx - 0.4, 4.7, color=ORG)
    wire_h(ax, 1.0, and1_cx - 0.4, 4.7, color=ORG)
    wire_v(ax, 1.0, 3.2, 4.7, color=ORG)
    dot(ax, 1.0, 4.7, color=ORG)
    label(ax, 0.7, 4.7, 'B', color=ORG, bold=True)

    # Cin
    wire_h(ax, 1.5, xor2_cx - 0.5, 3.8, color=GRN)
    wire_h(ax, 1.5, and2_cx - 0.5, 3.8, color=GRN)
    wire_v(ax, 1.5, 2.0, 3.8, color=GRN)
    label(ax, 1.5, 1.7, 'Cin', color=GRN, bold=True)

    # ── XOR1 ──
    wire_h(ax, xor1_cx-0.4, xor1_cx-0.28, 5.3, color=BLU)
    wire_h(ax, xor1_cx-0.4, xor1_cx-0.28, 4.7, color=ORG)
    xo1_out_x, xo1_out_y = gate_xor(ax, xor1_cx, xor1_cy, color=ORG)
    # pinos entrada XOR1
    wire_h(ax, 0.5, xor1_cx - 0.65, 5.3, color=BLU)
    wire_h(ax, 1.0, xor1_cx - 0.65, 4.7, color=ORG)
    label(ax, xor1_cx, xor1_cy+0.75, 'XOR₁', color=ORG, size=8)

    # ── AND1 ──
    wire_h(ax, 0.5, and1_cx - 0.4, 3.7, color=BLU)
    wire_h(ax, 1.0, and1_cx - 0.4, 3.3, color=ORG)
    and1_out_x, and1_out_y = gate_and(ax, and1_cx, and1_cy, color=BLU)
    label(ax, and1_cx, and1_cy+0.75, 'AND₁', color=BLU, size=8)

    # ── XOR1 output wire → XOR2 ──
    mid_x = 5.2
    wire_h(ax, xo1_out_x, mid_x, xor1_cy, color=ORG)
    wire_v(ax, mid_x, xor1_cy, xor2_cy+0.15, color=ORG)
    wire_h(ax, mid_x, xor2_cx - 0.65, xor2_cy+0.15, color=ORG)
    dot(ax, mid_x, xor1_cy, color=ORG)

    # ── XOR1 output wire → AND2 ──
    wire_v(ax, mid_x, xor2_cy+0.15, and2_cy+0.15, color=ORG)
    wire_h(ax, mid_x, and2_cx - 0.4, and2_cy+0.15, color=ORG)
    dot(ax, mid_x, and2_cy+0.15, color=ORG)

    # ── Cin → XOR2 e AND2 ──
    cin_x = 1.5
    wire_h(ax, cin_x, xor2_cx - 0.65, 3.85, color=GRN)
    wire_h(ax, cin_x, and2_cx - 0.40, 3.85, color=GRN)
    dot(ax, cin_x, 3.85, color=GRN)

    # ── XOR2 ──
    gate_xor(ax, xor2_cx, xor2_cy, color=ORG)
    xo2_out_x = xor2_cx + 0.73
    wire_h(ax, xo2_out_x, 11.5, xor2_cy, color=ORG)
    label(ax, 11.8, xor2_cy, 'SUM', color=ORG, bold=True)
    label(ax, xor2_cx, xor2_cy+0.75, 'XOR₂', color=ORG, size=8)

    # ── AND2 ──
    gate_and(ax, and2_cx, and2_cy, color=BLU)
    and2_out_x = and2_cx + 0.30
    label(ax, and2_cx, and2_cy+0.75, 'AND₂', color=BLU, size=8)

    # ── OR (AND1 | AND2) ──
    # AND1 output → OR
    wire_h(ax, and1_out_x, 8.5, and1_cy, color=BLU)
    wire_v(ax, 8.5, and1_cy, or_cy+0.15, color=BLU)
    wire_h(ax, 8.5, or_cx - 0.65, or_cy+0.15, color=BLU)
    # AND2 output → OR
    wire_h(ax, and2_out_x, 8.8, and2_cy, color=BLU)
    wire_v(ax, 8.8, and2_cy, or_cy-0.15, color=BLU)
    wire_h(ax, 8.8, or_cx - 0.65, or_cy-0.15, color=BLU)

    gate_or(ax, or_cx, or_cy, color=RED)
    or_out_x = or_cx + 0.73
    wire_h(ax, or_out_x, 11.5, or_cy, color=RED)
    label(ax, 11.8, or_cy, 'Cout', color=RED, bold=True)
    label(ax, or_cx, or_cy+0.75, 'OR', color=RED, size=8)

    # ── Legenda ──
    ax.text(0.5, 6.7,
            'FA = Full Adder  |  Sum = A⊕B⊕Cin  |  Cout = AB + Cin(A⊕B)',
            fontsize=9, color=GRY, style='italic')

    ax.set_title('Esquemático: Full Adder — Nível de Portas Lógicas\n'
                 'ALUChip v1.0 | Base do Somador Ripple-Carry de 8 bits',
                 fontsize=12, fontweight='bold', color=BLU)

    plt.savefig('fig_schem_full_adder.png', dpi=160,
                bbox_inches='tight', facecolor='#F5F8FC')
    plt.close()
    print('Salvo: fig_schem_full_adder.png')


# ─── Figura 2: Ripple-Carry Adder 8 bits ─────────────────────────────────────

def fig_rca8():
    fig, ax = plt.subplots(figsize=(18, 5))
    ax.set_xlim(-0.5, 18); ax.set_ylim(-1.0, 4.5)
    ax.axis('off'); fig.patch.set_facecolor('#F5F8FC')

    spacing = 2.0
    fa_w, fa_h = 1.2, 1.4

    for i in range(8):
        cx = 0.8 + i * spacing

        # FA box
        r = FancyBboxPatch((cx - fa_w/2, 0.3), fa_w, fa_h,
                            boxstyle='round,pad=0.08',
                            fc='#E8F5E9', ec=GRN, lw=1.8)
        ax.add_patch(r)
        ax.text(cx, 0.3 + fa_h/2 + 0.1, 'FA', ha='center',
                fontsize=11, fontweight='bold', color=GRN)
        ax.text(cx, 0.3 + fa_h/2 - 0.25, f'bit {i}', ha='center',
                fontsize=7.5, color=GRY)

        # A[i] entrada
        wire_v(ax, cx - 0.25, 0.3 + fa_h, 2.8, color=BLU)
        label(ax, cx - 0.25, 3.0, f'A[{i}]', color=BLU, size=7.5)

        # B[i] entrada
        wire_v(ax, cx + 0.25, 0.3 + fa_h, 2.3, color=ORG)
        label(ax, cx + 0.25, 2.5, f'B[{i}]', color=ORG, size=7.5)

        # S[i] saída
        wire_v(ax, cx, 0.3, -0.4, color=GRN)
        label(ax, cx, -0.65, f'S[{i}]', color=GRN, size=7.5)

        # Carry chain
        if i == 0:
            # Cin = 0
            wire_h(ax, -0.3, cx - fa_w/2, 1.0, color=RED)
            label(ax, -0.4, 1.0, 'Cin\n=0', color=RED, size=7.5)
        else:
            pass  # carry vem do anterior

        if i < 7:
            cx_next = 0.8 + (i + 1) * spacing
            wire_h(ax, cx + fa_w/2, cx_next - fa_w/2, 1.0, color=RED)
            label(ax, (cx + fa_w/2 + cx_next - fa_w/2)/2, 1.18,
                  f'C{i+1}', color=RED, size=7, ha='center')
        else:
            wire_h(ax, cx + fa_w/2, cx + 1.2, 1.0, color=RED)
            label(ax, cx + 1.35, 1.0, 'Cout', color=RED, bold=True, size=8)

    # ── SUB via inversão de B ──
    ax.add_patch(FancyBboxPatch((15.8, -0.3), 1.8, 0.55,
                                 boxstyle='round,pad=0.06',
                                 fc='#FFF3E0', ec=ORG, lw=1.2))
    ax.text(16.7, -0.02, 'SUB: B̄+1\n(~B + Cin=1)',
            ha='center', fontsize=7.5, color=ORG, style='italic')

    ax.set_title('Esquemático: Somador Ripple-Carry de 8 bits (ADD / SUB)\n'
                 'ALUChip v1.0 | Caminho crítico: 8 Full Adders em cascata | $t_{pd} \\approx 1{,}4$\\,ns',
                 fontsize=11, fontweight='bold', color=BLU)

    plt.savefig('fig_schem_rca8.png', dpi=160,
                bbox_inches='tight', facecolor='#F5F8FC')
    plt.close()
    print('Salvo: fig_schem_rca8.png')


# ─── Figura 3: ALU completa — paths paralelos ────────────────────────────────

def fig_alu_gates():
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(-0.5, 16); ax.set_ylim(-0.5, 10.5)
    ax.axis('off'); fig.patch.set_facecolor('#F5F8FC')

    # Entradas A e B verticais
    ax_a, ax_b = 0.8, 1.4

    # ── Linha de A e B ──
    wire_v(ax, ax_a, 0.5, 10.0, color=BLU, lw=1.2)
    wire_v(ax, ax_b, 0.5, 10.0, color=ORG, lw=1.2)
    label(ax, ax_a, 10.2, 'A[i]', color=BLU, bold=True, size=9)
    label(ax, ax_b, 10.2, 'B[i]', color=ORG, bold=True, size=9)

    results = {}  # op -> (out_x, out_y)

    # ── AND ──
    ya = 9.0
    wire_h(ax, ax_a, 2.4, ya+0.15, color=BLU)
    wire_h(ax, ax_b, 2.4, ya-0.15, color=ORG)
    dot(ax, ax_a, ya+0.15, color=BLU); dot(ax, ax_b, ya-0.15, color=ORG)
    ox, oy = gate_and(ax, 3.0, ya, color=BLU)
    wire_h(ax, ox, 5.8, oy, color=BLU)
    label(ax, 3.0, ya-0.7, '[010] AND\nR = A & B', color=BLU, size=8)
    results['AND'] = (5.8, oy)

    # ── OR ──
    yo = 7.4
    wire_h(ax, ax_a, 2.4, yo+0.15, color=GRN)
    wire_h(ax, ax_b, 2.4, yo-0.15, color=GRN)
    dot(ax, ax_a, yo+0.15, color=GRN); dot(ax, ax_b, yo-0.15, color=GRN)
    ox, oy = gate_or(ax, 3.0, yo, color=GRN)
    wire_h(ax, ox, 5.8, oy, color=GRN)
    label(ax, 3.0, yo-0.7, '[011] OR\nR = A | B', color=GRN, size=8)
    results['OR'] = (5.8, oy)

    # ── XOR ──
    yx = 5.8
    wire_h(ax, ax_a, 2.4, yx+0.15, color=ORG)
    wire_h(ax, ax_b, 2.4, yx-0.15, color=ORG)
    dot(ax, ax_a, yx+0.15, color=ORG); dot(ax, ax_b, yx-0.15, color=ORG)
    ox, oy = gate_xor(ax, 3.0, yx, color=ORG)
    wire_h(ax, ox, 5.8, oy, color=ORG)
    label(ax, 3.0, yx-0.7, '[100] XOR\nR = A ⊕ B', color=ORG, size=8)
    results['XOR'] = (5.8, oy)

    # ── NOT ──
    yn = 4.2
    wire_h(ax, ax_a, 2.4, yn, color=RED)
    dot(ax, ax_a, yn, color=RED)
    ox, oy = gate_not(ax, 3.0, yn, color=RED)
    wire_h(ax, ox, 5.8, oy, color=RED)
    label(ax, 3.0, yn-0.65, '[101] NOT\nR = ~A', color=RED, size=8)
    results['NOT'] = (5.8, oy)

    # ── SHL (deslocamento p/ esquerda) ──
    ys = 2.8
    # SHL: R[i] = A[i-1], C = A[7]
    # Representado como reconexão de fios
    wire_h(ax, ax_a, 2.4, ys+0.15, color=PUR)
    dot(ax, ax_a, ys+0.15, color=PUR)
    # buffer / passthrough
    ax.plot([2.4, 2.4, 3.6, 3.6], [ys+0.35, ys+0.15, ys+0.15, ys+0.35],
            color=PUR, lw=LW)
    ax.annotate('', xy=(4.5, ys), xytext=(3.6, ys+0.15),
                arrowprops=dict(arrowstyle='->', color=PUR, lw=LW))
    ax.text(3.0, ys+0.5, 'R[i] = A[i-1]\n(rewire + LSB=0)', ha='center',
            fontsize=7.5, color=PUR, style='italic')
    wire_h(ax, 4.5, 5.8, ys, color=PUR)
    label(ax, 3.0, ys-0.65, '[110] SHL\nC = A[7]', color=PUR, size=8)
    results['SHL'] = (5.8, ys)

    # ── SHR (deslocamento p/ direita) ──
    yr = 1.3
    wire_h(ax, ax_a, 2.4, yr+0.15, color='#F57F17')
    dot(ax, ax_a, yr+0.15, color='#F57F17')
    ax.plot([2.4, 2.4, 3.6, 3.6], [yr+0.35, yr+0.15, yr+0.15, yr+0.35],
            color='#F57F17', lw=LW)
    ax.annotate('', xy=(4.5, yr), xytext=(3.6, yr+0.15),
                arrowprops=dict(arrowstyle='->', color='#F57F17', lw=LW))
    ax.text(3.0, yr+0.5, 'R[i] = A[i+1]\n(rewire + MSB=0)', ha='center',
            fontsize=7.5, color='#F57F17', style='italic')
    wire_h(ax, 4.5, 5.8, yr, color='#F57F17')
    label(ax, 3.0, yr-0.65, '[111] SHR\nC = A[0]', color='#F57F17', size=8)
    results['SHR'] = (5.8, yr)

    # ── ADD/SUB (Full Adder símbolo) ──
    yf = 9.0 + 0.5
    fa_cx, fa_cy = 3.0, 8.5 + 0.5
    # re-draw em posição correta - simplified FA box
    r = FancyBboxPatch((2.2, 9.6), 1.6, 1.2,
                        boxstyle='round,pad=0.1', fc='#E3F2FD', ec=BLU, lw=1.8)
    # This is the adder path - skip redraw, show wire to mux
    # Already drawn ADD above in separate figure - just show output here

    # ── MUX 8:1 ──
    mux_x = 8.5
    mux_h = 9.5
    mux_w = 1.2
    # trapézio MUX
    trap = plt.Polygon(
        [(mux_x, 0.8), (mux_x + mux_w, 1.5),
         (mux_x + mux_w, mux_h - 1.5), (mux_x, mux_h - 0.8)],
        closed=True, fc='#FFF8E1', ec='#F9A825', lw=2.0)
    ax.add_patch(trap)
    ax.text(mux_x + mux_w/2, mux_h/2 - 0.2, 'MUX\n8:1',
            ha='center', va='center', fontsize=10,
            fontweight='bold', color='#F57F17')
    # OP[2:0]
    wire_v(ax, mux_x + mux_w/2, 0.3, 0.8, color=GRY)
    label(ax, mux_x + mux_w/2, 0.1, 'OP[2:0]', color=GRY, size=8, bold=True)

    # Conecta resultados ao MUX
    op_colors2 = {'AND':BLU,'OR':GRN,'XOR':ORG,'NOT':RED,'SHL':PUR,'SHR':'#F57F17'}
    ops_order  = ['AND','OR','XOR','NOT','SHL','SHR']
    for i, op in enumerate(ops_order):
        rx, ry = results[op]
        mux_in_y = 1.5 + i * (mux_h - 3.0) / 5
        wire_h(ax, rx, mux_x, ry, color=op_colors2[op], lw=1.2)
        wire_v(ax, mux_x - 0.02, ry, mux_in_y, color=op_colors2[op], lw=1.2)
        dot(ax, mux_x, mux_in_y, color=op_colors2[op], r=0.06)

    # ADD path (simplified arrow from top)
    ax.annotate('', xy=(mux_x, mux_h - 0.9), xytext=(mux_x - 1.5, mux_h - 0.9),
                arrowprops=dict(arrowstyle='->', color=BLU, lw=1.5))
    ax.text(mux_x - 0.75, mux_h - 0.65, 'ADD/SUB\n(Adder)', ha='center',
            fontsize=7.5, color=BLU, style='italic')

    # MUX saída
    wire_h(ax, mux_x + mux_w, 12.5, mux_h/2 - 0.2, color='#F9A825')
    label(ax, 13.0, mux_h/2 - 0.2, 'RESULT[i]', color='#F9A825', bold=True, size=9)

    # Flags block
    flag_cx = 13.5
    flag_cy = mux_h/2 - 0.2
    r2 = FancyBboxPatch((flag_cx - 0.6, flag_cy - 1.5), 1.8, 3.0,
                         boxstyle='round,pad=0.12', fc='#FCE4EC', ec=RED, lw=1.8)
    ax.add_patch(r2)
    ax.text(flag_cx + 0.3, flag_cy + 0.5, 'FLAG\nLOGIC', ha='center',
            fontsize=9, fontweight='bold', color=RED)
    ax.text(flag_cx + 0.3, flag_cy - 0.6,
            'Z: NOR\nC: carry\nV: ovfl\nN: MSB',
            ha='center', fontsize=7.5, color=RED, linespacing=1.6)
    wire_h(ax, 12.5, flag_cx - 0.6, flag_cy, color='#F9A825', lw=1.2)
    dot(ax, 12.5, flag_cy, color='#F9A825')

    ax.set_title('Esquemático Completo — ALUChip v1.0: Todos os Caminhos de Dados\n'
                 'ADD/SUB · AND · OR · XOR · NOT · SHL · SHR → MUX 8:1 → RESULT + FLAGS',
                 fontsize=11, fontweight='bold', color=BLU)

    plt.savefig('fig_schem_alu_completo.png', dpi=160,
                bbox_inches='tight', facecolor='#F5F8FC')
    plt.close()
    print('Salvo: fig_schem_alu_completo.png')


# ─── Figura 4: Flag Logic em nível de portas ─────────────────────────────────

def fig_flag_gates():
    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    fig.patch.set_facecolor('#F5F8FC')
    fig.suptitle('ALUChip v1.0 — Lógica das Flags em Nível de Portas\nZ · C · V · N',
                 fontsize=12, fontweight='bold', color=BLU, y=1.01)

    # ── FLAG Z (NOR de 8 bits → NOT(OR8)) ──
    ax = axes[0][0]
    ax.set_xlim(0, 8); ax.set_ylim(-0.5, 5); ax.axis('off')
    ax.set_facecolor('#E8F5E9')
    # NOR-8 como OR-8 + NOT
    for i in range(8):
        wire_h(ax, 0.3, 1.8, 0.3 + i*0.55, color=GRN, lw=1.2)
        label(ax, 0.1, 0.3 + i*0.55, f'R[{i}]', color=GRN, size=7.5)
    # OR de 8 entradas (símbolo com texto)
    r = FancyBboxPatch((1.8, 0.0), 1.5, 4.3,
                        boxstyle='round,pad=0.1', fc='#C8E6C9', ec=GRN, lw=1.8)
    ax.add_patch(r)
    ax.text(2.55, 2.15, 'OR\n8-in', ha='center', va='center',
            fontsize=10, fontweight='bold', color=GRN)
    wire_h(ax, 3.3, 4.0, 2.15, color=GRN)
    gate_not(ax, 4.6, 2.15, color=GRN)
    wire_h(ax, 4.6+0.35, 6.5, 2.15, color=GRN)
    label(ax, 6.8, 2.15, 'Z', color=GRN, bold=True, size=11)
    ax.set_title('Flag Z = NOR(R[7:0])\n= ~(R0|R1|...|R7)', fontsize=9,
                 fontweight='bold', color=GRN, pad=4)

    # ── FLAG C (carry-out do somador / shift-out) ──
    ax = axes[0][1]
    ax.set_xlim(0, 8); ax.set_ylim(-0.5, 5); ax.axis('off')
    ax.set_facecolor('#E3F2FD')
    # MUX 3:1: ADD→Cout, SHL→A[7], SHR→A[0]
    wire_h(ax, 0.3, 2.0, 3.8, color=BLU)
    wire_h(ax, 0.3, 2.0, 2.6, color=PUR)
    wire_h(ax, 0.3, 2.0, 1.4, color='#F57F17')
    label(ax, 0.1, 3.8, 'Cout (ADD/SUB)', color=BLU, size=7.5, ha='left')
    label(ax, 0.1, 2.6, 'A[7]  (SHL)',     color=PUR, size=7.5, ha='left')
    label(ax, 0.1, 1.4, 'A[0]  (SHR)',     color='#F57F17', size=7.5, ha='left')
    trap = plt.Polygon(
        [(2.0, 1.0), (3.2, 1.6), (3.2, 3.6), (2.0, 4.2)],
        closed=True, fc='#BBDEFB', ec=BLU, lw=1.8)
    ax.add_patch(trap)
    ax.text(2.6, 2.6, 'MUX\n3:1', ha='center', va='center',
            fontsize=9, fontweight='bold', color=BLU)
    ax.text(2.6, 1.2, 'OP[2:0]', ha='center', fontsize=7.5, color=GRY)
    wire_h(ax, 3.2, 5.5, 2.6, color=RED)
    label(ax, 5.8, 2.6, 'C', color=RED, bold=True, size=11)
    ax.set_title('Flag C = Carry/Borrow/Shift-out\n(MUX 3:1 controlado por OP)',
                 fontsize=9, fontweight='bold', color=BLU, pad=4)

    # ── FLAG V (overflow ADD/SUB) ──
    ax = axes[1][0]
    ax.set_xlim(0, 9); ax.set_ylim(-0.5, 6); ax.axis('off')
    ax.set_facecolor('#FFF3E0')
    # V_ADD = (~A7 & ~B7 & R7) | (A7 & B7 & ~R7)
    # caminho superior: ~A7 AND ~B7 AND R7
    wire_h(ax, 0.3, 1.5, 4.8, color=BLU)
    gate_not(ax, 2.1, 4.8, color=BLU)
    wire_h(ax, 2.55, 3.0, 4.8, color=BLU)
    label(ax, 0.1, 4.8, 'A[7]', color=BLU, size=7.5, ha='left')

    wire_h(ax, 0.3, 1.5, 4.1, color=ORG)
    gate_not(ax, 2.1, 4.1, color=ORG)
    wire_h(ax, 2.55, 3.0, 4.1, color=ORG)
    label(ax, 0.1, 4.1, 'B[7]', color=ORG, size=7.5, ha='left')

    wire_h(ax, 0.3, 3.0, 3.4, color=GRN)
    label(ax, 0.1, 3.4, 'R[7]', color=GRN, size=7.5, ha='left')

    gate_and(ax, 3.7, 4.1, w=0.9, h=1.0, color=BLU)
    wire_h(ax, 4.2, 5.0, 4.1, color=BLU)

    # caminho inferior: A7 AND B7 AND ~R7
    wire_h(ax, 0.3, 2.9, 2.4, color=BLU)
    dot(ax, 0.3, 2.4, color=BLU)
    wire_h(ax, 0.3, 2.9, 1.7, color=ORG)
    dot(ax, 0.3, 1.7, color=ORG)
    gate_not(ax, 1.6, 1.0, color=GRN)
    wire_h(ax, 0.3, 1.2, 1.0, color=GRN)
    dot(ax, 0.3, 1.0, color=GRN)
    wire_h(ax, 2.0, 2.9, 1.0, color=GRN)
    gate_and(ax, 3.6, 1.8, w=0.9, h=1.0, color=ORG)
    wire_h(ax, 4.1, 5.0, 1.8, color=ORG)

    # OR final
    gate_or(ax, 5.8, 3.0, color=RED)
    wire_h(ax, 5.0, 5.15, 4.1, color=BLU)
    wire_h(ax, 5.0, 5.15, 1.8, color=ORG)
    wire_v(ax, 5.15, 4.1, 3.15, color=BLU)
    wire_v(ax, 5.15, 1.8, 2.85, color=ORG)
    wire_h(ax, 5.15, 5.18, 3.15, color=BLU)
    wire_h(ax, 5.15, 5.18, 2.85, color=ORG)
    or_out_x = 5.8 + 0.73
    wire_h(ax, or_out_x, 8.5, 3.0, color=RED)
    label(ax, 8.7, 3.0, 'V', color=RED, bold=True, size=11)
    ax.set_title('Flag V = Overflow (ADD)\n= (~A7&~B7&R7)|(A7&B7&~R7)',
                 fontsize=9, fontweight='bold', color=ORG, pad=4)

    # ── FLAG N (MSB) ──
    ax = axes[1][1]
    ax.set_xlim(0, 8); ax.set_ylim(-0.5, 5); ax.axis('off')
    ax.set_facecolor('#FCE4EC')
    # N = R[7]: simplesmente buffer / passthrough
    wire_h(ax, 0.5, 5.5, 2.5, color=RED, lw=2.5)
    dot(ax, 5.5, 2.5, color=RED, r=0.08)
    label(ax, 0.2, 2.5, 'R[7]\n(MSB)', color=RED, bold=True, size=9, ha='left')
    label(ax, 5.8, 2.5, 'N', color=RED, bold=True, size=11)
    # símbolo de buffer
    ax.plot([2.5, 4.5, 3.5, 2.5], [3.2, 2.5, 1.8, 3.2],
            color=RED, lw=2.0, solid_capstyle='round')
    ax.text(3.5, 2.5, '1', ha='center', va='center',
            fontsize=12, fontweight='bold', color=RED)
    ax.text(3.5, 0.7,
            'N indica número negativo\nem representação C2\n(bit de sinal)',
            ha='center', fontsize=8, color=GRY, style='italic')
    ax.set_title('Flag N = R[7] (bit de sinal)\nN=1 → resultado negativo (C2)',
                 fontsize=9, fontweight='bold', color=RED, pad=4)

    plt.tight_layout()
    plt.savefig('fig_schem_flags.png', dpi=160,
                bbox_inches='tight', facecolor='#F5F8FC')
    plt.close()
    print('Salvo: fig_schem_flags.png')


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import os
    os.chdir('/home/user/aqua-monitor/docs/unidade7_cap5_desafio_romulo')
    fig_full_adder()
    fig_rca8()
    fig_alu_gates()
    fig_flag_gates()
    print('\nTodos os 4 esquemáticos gerados.')
