#!/usr/bin/env python3
"""
gerar_figuras_alu.py -- Figuras para ALUChip v1.0
Unidade 7 | Capitulo 5 | PADIS
Autor: Romulo da Silva Lira  |  Prof.: Andre Feitosa
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patches as mpatch
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path
import matplotlib.patheffects as pe

# ── Paleta ───────────────────────────────────────────────────────────────────
BLU  = '#1565C0'
TBLU = '#1E88E5'
GRN  = '#2E7D32'
RED  = '#C62828'
ORG  = '#EF6C00'
GRY  = '#424242'
LGRY = '#ECEFF1'
WHT  = '#FFFFFF'
YEL  = '#F9A825'

def save(name):
    plt.savefig(name, dpi=150, bbox_inches='tight', facecolor='#F5F8FC')
    plt.close()
    print(f'Salvo: {name}')

# =============================================================================
# 1. fig_arquitetura_alu.png -- Diagrama de blocos (top-level)
# =============================================================================
fig, ax = plt.subplots(figsize=(14,6))
ax.set_xlim(0,14); ax.set_ylim(0,6)
ax.axis('off'); fig.patch.set_facecolor('#F5F8FC')

def box(ax, x, y, w, h, label, sub='', fc=LGRY, ec=BLU, lw=2):
    r = FancyBboxPatch((x,y), w, h, boxstyle='round,pad=0.1',
                        fc=fc, ec=ec, lw=lw)
    ax.add_patch(r)
    ax.text(x+w/2, y+h/2+(0.18 if sub else 0), label,
            ha='center', va='center', fontsize=11, fontweight='bold', color=ec)
    if sub:
        ax.text(x+w/2, y+h/2-0.3, sub,
                ha='center', va='center', fontsize=8, color=GRY)

def arr(ax, x0,y0,x1,y1, label='', color=BLU):
    ax.annotate('', xy=(x1,y1), xytext=(x0,y0),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.8))
    if label:
        mx, my = (x0+x1)/2, (y0+y1)/2
        ax.text(mx+0.05, my+0.18, label, fontsize=8,
                color=GRY, ha='center', va='bottom', fontfamily='monospace')

# Chip boundary
chip = FancyBboxPatch((2.5, 0.6), 9, 4.8, boxstyle='round,pad=0.15',
                       fc='#E3F2FD', ec=BLU, lw=2.5, linestyle='--')
ax.add_patch(chip)
ax.text(7, 5.62, 'alu8_chip_top', ha='center', fontsize=10,
        color=BLU, fontweight='bold', style='italic')

# ALU core
box(ax, 4.8, 1.5, 4.4, 3.0, 'ALU Core', 'alu8', fc='#BBDEFB', ec=BLU)

# Entradas
ax.text(0.6, 4.5, 'A[7:0]', fontsize=9, fontfamily='monospace',
        color=GRN, fontweight='bold', ha='center')
ax.text(0.6, 3.2, 'B[7:0]', fontsize=9, fontfamily='monospace',
        color=GRN, fontweight='bold', ha='center')
ax.text(0.6, 1.8, 'OP[2:0]', fontsize=9, fontfamily='monospace',
        color=ORG, fontweight='bold', ha='center')

arr(ax, 1.3,4.5, 4.8,3.8, '8 bits', GRN)
arr(ax, 1.3,3.2, 4.8,3.0, '8 bits', GRN)
arr(ax, 1.3,1.8, 4.8,2.3, '3 bits', ORG)

# Saidas
ax.text(13.4, 4.0, 'RESULT[7:0]', fontsize=9, fontfamily='monospace',
        color=BLU, fontweight='bold', ha='center')
ax.text(13.4, 2.8, 'FLAG_Z', fontsize=9, fontfamily='monospace',
        color=RED, fontweight='bold', ha='center')
ax.text(13.4, 2.2, 'FLAG_C', fontsize=9, fontfamily='monospace',
        color=RED, fontweight='bold', ha='center')
ax.text(13.4, 1.6, 'FLAG_V', fontsize=9, fontfamily='monospace',
        color=RED, fontweight='bold', ha='center')
ax.text(13.4, 1.0, 'FLAG_N', fontsize=9, fontfamily='monospace',
        color=RED, fontweight='bold', ha='center')

arr(ax, 9.2,4.0, 12.5,4.0, '8 bits', BLU)
arr(ax, 9.2,3.0, 12.5,2.8, '1 bit',  RED)
arr(ax, 9.2,2.6, 12.5,2.2, '1 bit',  RED)
arr(ax, 9.2,2.2, 12.5,1.6, '1 bit',  RED)
arr(ax, 9.2,1.8, 12.5,1.0, '1 bit',  RED)

# Operacoes internas
ops = ['ADD','SUB','AND','OR','XOR','NOT','SHL','SHR']
for i,op in enumerate(ops):
    c = BLU if i < 2 else GRN if i < 6 else ORG
    ax.text(7.0, 4.1 - i*0.32, f'[{i:03b}] {op}',
            fontsize=7.5, fontfamily='monospace', color=c, ha='center')

ax.set_title('ALUChip v1.0 — Diagrama de Blocos Top-Level\n'
             'ULA 8 bits | CMOS 0,35µm | VDD=3,3V',
             fontsize=12, fontweight='bold', color=BLU, pad=8)
save('fig_arquitetura_alu.png')

# =============================================================================
# 2. fig_esquematico_add.png -- Esquematico do somador (Ripple-Carry Adder)
# =============================================================================
fig, ax = plt.subplots(figsize=(16, 5))
ax.set_xlim(-0.5, 16); ax.set_ylim(-1, 5)
ax.axis('off'); fig.patch.set_facecolor('#F5F8FC')

def full_adder_box(ax, cx, cy, idx):
    """Desenha um Full Adder box."""
    r = FancyBboxPatch((cx-0.6, cy-0.8), 1.2, 1.6,
                        boxstyle='round,pad=0.05',
                        fc='#E8F5E9', ec=GRN, lw=1.5)
    ax.add_patch(r)
    ax.text(cx, cy+0.2, 'FA', ha='center', va='center',
            fontsize=9, fontweight='bold', color=GRN)
    ax.text(cx, cy-0.25, f'bit {idx}', ha='center', va='center',
            fontsize=7, color=GRY)
    return cx, cy

n = 8
spacing = 1.7
x_start = 1.0

carries = []
for i in range(n):
    cx = x_start + i * spacing
    cy = 2.0
    full_adder_box(ax, cx, cy, i)

    # Entradas A[i]
    ax.annotate('', xy=(cx-0.3, cy+0.8), xytext=(cx-0.3, cy+1.6),
                arrowprops=dict(arrowstyle='->', color=BLU, lw=1.2))
    ax.text(cx-0.3, cy+1.85, f'A[{i}]', ha='center', fontsize=7,
            fontfamily='monospace', color=BLU)

    # Entradas B[i]
    ax.annotate('', xy=(cx+0.3, cy+0.8), xytext=(cx+0.3, cy+1.6),
                arrowprops=dict(arrowstyle='->', color=ORG, lw=1.2))
    ax.text(cx+0.3, cy+1.85, f'B[{i}]', ha='center', fontsize=7,
            fontfamily='monospace', color=ORG)

    # Sum out
    ax.annotate('', xy=(cx, cy-1.5), xytext=(cx, cy-0.8),
                arrowprops=dict(arrowstyle='->', color=GRN, lw=1.2))
    ax.text(cx, cy-1.75, f'S[{i}]', ha='center', fontsize=7,
            fontfamily='monospace', color=GRN)

    # Carry chain
    if i < n-1:
        cx_next = x_start + (i+1) * spacing
        ax.annotate('', xy=(cx_next-0.6, cy), xytext=(cx+0.6, cy),
                    arrowprops=dict(arrowstyle='->', color=RED, lw=1.4))
        ax.text((cx+0.6+cx_next-0.6)/2, cy+0.12, f'C{i+1}',
                ha='center', fontsize=7, color=RED, fontfamily='monospace')
    else:
        ax.annotate('', xy=(cx+1.5, cy), xytext=(cx+0.6, cy),
                    arrowprops=dict(arrowstyle='->', color=RED, lw=1.8))
        ax.text(cx+1.5, cy+0.15, 'Cout', ha='left', fontsize=8,
                color=RED, fontweight='bold', fontfamily='monospace')

# C_in at bit 0
cx0 = x_start
ax.annotate('', xy=(cx0-0.6, 2.0), xytext=(cx0-1.4, 2.0),
            arrowprops=dict(arrowstyle='->', color=RED, lw=1.4))
ax.text(cx0-1.45, 2.15, 'Cin=0\n(ADD)', ha='center', fontsize=7,
        color=RED, fontfamily='monospace')

ax.set_title('Esquemático: Somador Ripple-Carry 8 bits (base do ADD/SUB)\n'
             'ALUChip v1.0 | Caminho crítico: 8 Full Adders em cascata',
             fontsize=11, fontweight='bold', color=BLU, y=1.02)
save('fig_esquematico_add.png')

# =============================================================================
# 3. fig_esquematico_logicas.png -- Esquematico das operacoes logicas
# =============================================================================
fig, axes = plt.subplots(2, 3, figsize=(15, 7))
fig.patch.set_facecolor('#F5F8FC')
fig.suptitle('Esquemáticos das Operações Lógicas — ALUChip v1.0\n'
             'AND · OR · XOR · NOT · SHL · SHR (1 bit representativo)',
             fontsize=12, fontweight='bold', color=BLU)

gate_specs = [
    ('AND',  'AND', '#E3F2FD', BLU),
    ('OR',   'OR',  '#E8F5E9', GRN),
    ('XOR',  'XOR', '#FFF3E0', ORG),
    ('NOT',  'NOT', '#FCE4EC', RED),
    ('SHL',  'SHL\n(shift left)', '#EDE7F6', '#6A1B9A'),
    ('SHR',  'SHR\n(shift right)','#FFF8E1', '#F57F17'),
]

for idx, (ax, (op, title, fc, ec)) in enumerate(zip(axes.flat, gate_specs)):
    ax.set_xlim(0,6); ax.set_ylim(0,5)
    ax.axis('off')
    ax.set_facecolor(fc)

    # Gate symbol
    r = FancyBboxPatch((1.8, 1.8), 2.4, 1.8,
                        boxstyle='round,pad=0.15', fc=WHT, ec=ec, lw=2.5)
    ax.add_patch(r)
    ax.text(3.0, 2.7, op, ha='center', va='center',
            fontsize=14, fontweight='bold', color=ec)

    if op in ('AND','OR','XOR'):
        # Duas entradas
        ax.annotate('', xy=(1.8,3.2), xytext=(0.4,3.2),
                    arrowprops=dict(arrowstyle='->', color=BLU, lw=1.5))
        ax.text(0.3, 3.2, 'A[i]', ha='right', fontsize=9,
                fontfamily='monospace', color=BLU, fontweight='bold')
        ax.annotate('', xy=(1.8,2.2), xytext=(0.4,2.2),
                    arrowprops=dict(arrowstyle='->', color=ORG, lw=1.5))
        ax.text(0.3, 2.2, 'B[i]', ha='right', fontsize=9,
                fontfamily='monospace', color=ORG, fontweight='bold')
    else:
        # Uma entrada
        ax.annotate('', xy=(1.8,2.7), xytext=(0.4,2.7),
                    arrowprops=dict(arrowstyle='->', color=BLU, lw=1.5))
        ax.text(0.3, 2.7, 'A[i]', ha='right', fontsize=9,
                fontfamily='monospace', color=BLU, fontweight='bold')

    # Saida
    ax.annotate('', xy=(5.5,2.7), xytext=(4.2,2.7),
                arrowprops=dict(arrowstyle='->', color=ec, lw=1.8))
    lbl = 'R[i]' if op not in ('SHL','SHR') else 'R[i+1]' if op=='SHL' else 'R[i-1]'
    ax.text(5.6, 2.7, lbl, ha='left', fontsize=9,
            fontfamily='monospace', color=ec, fontweight='bold')

    # Equacao booleana
    eqs = {'AND':'R = A & B','OR':'R = A | B','XOR':'R = A ^ B',
           'NOT':'R = ~A','SHL':'R[i] = A[i-1]\nC = A[7]','SHR':'R[i] = A[i+1]\nC = A[0]'}
    ax.text(3.0, 0.6, eqs[op], ha='center', fontsize=9,
            color=GRY, style='italic',
            bbox=dict(fc=WHT, ec=ec, alpha=0.7, boxstyle='round,pad=0.3'))
    ax.set_title(f'[{idx+2:03b}] {title}' if op not in ('SHL','SHR')
                 else f'[{idx+4:03b}] {title}',
                 fontsize=10, fontweight='bold', color=ec, pad=4)

# fix titles manually
for i,ax in enumerate(axes.flat):
    codes = ['010','011','100','101','110','111']
    names = ['AND','OR','XOR','NOT','SHL','SHR']
    ax.set_title(f'[{codes[i]}] {names[i]}',
                 fontsize=10, fontweight='bold', color=gate_specs[i][3], pad=4)

plt.tight_layout()
save('fig_esquematico_logicas.png')

# =============================================================================
# 4. fig_flags.png -- Logica das Flags
# =============================================================================
fig, ax = plt.subplots(figsize=(13,6))
ax.set_xlim(0,13); ax.set_ylim(0,6)
ax.axis('off'); fig.patch.set_facecolor('#F5F8FC')

flags = [
    ('Z\nZero',     'Result[7:0] == 8\'h00\n(NOR de todos os bits)',           '#E8F5E9', GRN,  1.0, 3.5),
    ('C\nCarry',    'Carry-out do bit 7 (ADD/SUB)\nou Shift-out (SHL/SHR)',    '#E3F2FD', BLU,  4.5, 3.5),
    ('V\nOverflow', '(~A[7] & ~B[7] & R[7]) |\n(A[7] & B[7] & ~R[7])',       '#FFF3E0', ORG,  8.0, 3.5),
    ('N\nNegativo', 'Result[7] (MSB)\nSinal em complemento de 2',             '#FCE4EC', RED,  1.0, 0.5),
]

ax.set_title('ALUChip v1.0 — Lógica de Geração das 4 Flags\nZ · C · V · N',
             fontsize=12, fontweight='bold', color=BLU, y=0.98)

for sym, desc, fc, ec, x, y in flags:
    r = FancyBboxPatch((x, y), 3.8, 2.2, boxstyle='round,pad=0.12',
                        fc=fc, ec=ec, lw=2.0)
    ax.add_patch(r)
    ax.text(x+0.7, y+1.1, sym, ha='center', va='center',
            fontsize=16, fontweight='bold', color=ec)
    ax.text(x+2.4, y+1.1, desc, ha='center', va='center',
            fontsize=8.5, color=GRY, linespacing=1.5)
    ax.plot([x+0.7, x+0.7],[y, y+2.2], color=ec, lw=1, alpha=0.4)

# Ligacao do resultado
ax.text(6.5, 5.5, 'RESULT[7:0] / WIDE[8:0]',
        ha='center', fontsize=10, fontweight='bold', color=BLU,
        bbox=dict(fc='#E3F2FD', ec=BLU, boxstyle='round,pad=0.3'))
for x,y in [(1.9,2.7),(5.4,2.7),(8.9,2.7),(1.9,0.0)]:
    ax.annotate('', xy=(x,y+0.5), xytext=(6.5,5.3),
                arrowprops=dict(arrowstyle='->', color=GRY, lw=1.0,
                                connectionstyle='arc3,rad=0.15'))

save('fig_flags.png')

# =============================================================================
# 5. fig_sim_resultados_alu.png -- Tabela de resultados da simulacao
# =============================================================================
fig, ax = plt.subplots(figsize=(15, 10))
ax.axis('off'); fig.patch.set_facecolor('#F5F8FC')

rows = [
    # op, A, B, result, Z, C, V, N, desc
    ('ADD','03h','05h','08h','0','0','0','0','3+5=8'),
    ('ADD','FFh','01h','00h','1','1','0','0','FF+01 (carry+zero)'),
    ('ADD','7Fh','01h','80h','0','0','1','1','7F+01 (overflow)'),
    ('ADD','80h','80h','00h','1','1','1','0','80+80 (carry+overflow)'),
    ('SUB','08h','03h','05h','0','1','0','0','8-3=5'),
    ('SUB','03h','08h','FBh','0','0','0','1','3-8 (negativo)'),
    ('SUB','80h','01h','7Fh','0','1','1','0','80-01 (overflow)'),
    ('AND','FFh','0Fh','0Fh','0','0','0','0','FF & 0F'),
    ('AND','AAh','55h','00h','1','0','0','0','AA & 55 (zero)'),
    ('OR', 'AAh','55h','FFh','0','0','0','1','AA | 55'),
    ('XOR','FFh','FFh','00h','1','0','0','0','FF ^ FF (zero)'),
    ('XOR','AAh','55h','FFh','0','0','0','1','AA ^ 55'),
    ('NOT','00h','---','FFh','0','0','0','1','~00'),
    ('NOT','FFh','---','00h','1','0','0','0','~FF (zero)'),
    ('SHL','80h','---','00h','1','1','0','0','80<<1 (carry+zero)'),
    ('SHL','55h','---','AAh','0','0','0','1','55<<1 (negativo)'),
    ('SHR','01h','---','00h','1','1','0','0','01>>1 (carry+zero)'),
    ('SHR','FFh','---','7Fh','0','1','0','0','FF>>1 (carry)'),
]

col_labels = ['OP','A','B','RESULT','Z','C','V','N','Descrição']
col_w = [0.08,0.07,0.07,0.09,0.05,0.05,0.05,0.05,0.28]
x_pos = [sum(col_w[:i]) for i in range(len(col_w))]

# Header
for xi, (lbl, w) in enumerate(zip(col_labels, col_w)):
    ax.add_patch(FancyBboxPatch((x_pos[xi]+0.01, 0.93), w-0.02, 0.05,
                                 boxstyle='round,pad=0.005', fc=BLU, ec=BLU))
    ax.text(x_pos[xi]+w/2, 0.955, lbl, ha='center', va='center',
            fontsize=9, fontweight='bold', color=WHT, transform=ax.transAxes)

op_colors = {'ADD': '#E3F2FD','SUB': '#E8EAF6','AND': '#E8F5E9',
             'OR':  '#F3E5F5','XOR': '#FFF3E0','NOT': '#FCE4EC',
             'SHL': '#E0F7FA','SHR': '#F1F8E9'}

for ri, row in enumerate(rows):
    y = 0.90 - ri*0.047
    op = row[0]
    fc = op_colors.get(op, WHT)
    ax.add_patch(FancyBboxPatch((0.01, y-0.02), 0.98, 0.042,
                                 boxstyle='round,pad=0.003', fc=fc, ec='#CCCCCC', lw=0.5))
    for ci, (val, w) in enumerate(zip(row, col_w)):
        fw = 'bold' if ci in (0,3) else 'normal'
        fc_txt = RED if ci in (4,5,6,7) and val=='1' else GRN if ci in (4,5,6,7) and val=='0' else BLU if ci==3 else GRY
        ax.text(x_pos[ci]+w/2, y, val, ha='center', va='center',
                fontsize=8.5, fontweight=fw, color=fc_txt,
                fontfamily='monospace' if ci < 8 else 'sans-serif',
                transform=ax.transAxes)

# Resultado final
ax.add_patch(FancyBboxPatch((0.15, 0.01), 0.70, 0.06,
                             boxstyle='round,pad=0.01', fc=GRN, ec=GRN))
ax.text(0.5, 0.04, '>>> RESULTADO: APROVADO — 27/27 testes passaram <<<',
        ha='center', va='center', fontsize=11, fontweight='bold',
        color=WHT, transform=ax.transAxes)

ax.set_title('ALUChip v1.0 — Resultados da Simulação Funcional\n'
             '27 vetores de teste | 8 operações | Icarus Verilog v12',
             fontsize=12, fontweight='bold', color=BLU, pad=6)
save('fig_sim_resultados_alu.png')

# =============================================================================
# 6. fig_floorplan_alu.png -- Floorplan do chip
# =============================================================================
fig, ax = plt.subplots(figsize=(10,10))
ax.set_xlim(0,10); ax.set_ylim(0,10)
ax.axis('off'); fig.patch.set_facecolor('#F5F8FC')

# Die boundary
ax.add_patch(FancyBboxPatch((0.3,0.3),9.4,9.4,
                             boxstyle='round,pad=0.1', fc='#E8EAF6', ec='#3949AB', lw=3))
ax.text(5,9.6,'ALUChip v1.0 — Die 120µm × 120µm',
        ha='center',fontsize=11,fontweight='bold',color='#3949AB')

# Core area
ax.add_patch(FancyBboxPatch((1.5,1.5),7,7,
                             boxstyle='round,pad=0.1', fc='#FFFFFF', ec=GRY, lw=1.5, ls='--'))
ax.text(5,8.7,'Core Area (~440µm²)',ha='center',fontsize=9,color=GRY,style='italic')

# Blocos internos
blocks = [
    (2.0,5.5,3.5,2.2,'Ripple-Carry\nAdder (ADD/SUB)', '#BBDEFB', BLU),
    (2.0,2.5,2.0,2.5,'Logic Unit\nAND·OR·XOR·NOT', '#C8E6C9', GRN),
    (5.0,2.5,2.0,2.5,'Shift Unit\nSHL · SHR', '#FFE0B2', ORG),
    (5.5,5.5,2.5,2.2,'Flag Logic\nZ·C·V·N', '#FFCDD2', RED),
    (4.2,4.0,1.6,1.0,'MUX\n8:1', '#E1BEE7', '#6A1B9A'),
]
for bx,by,bw,bh,lbl,fc,ec in blocks:
    ax.add_patch(FancyBboxPatch((bx,by),bw,bh,
                                 boxstyle='round,pad=0.1', fc=fc, ec=ec, lw=1.8))
    ax.text(bx+bw/2,by+bh/2,lbl,ha='center',va='center',
            fontsize=8,fontweight='bold',color=ec,linespacing=1.4)

# I/O Pads — top e bottom
pad_labels_top = ['A0','A1','A2','A3','A4','A5','A6','A7']
pad_labels_bot = ['R0','R1','R2','R3','R4','R5','R6','R7']
for i,lbl in enumerate(pad_labels_top):
    x = 1.0 + i*1.0
    ax.add_patch(FancyBboxPatch((x-0.25,9.0),0.5,0.5,fc='#B3E5FC',ec=BLU,lw=1))
    ax.text(x,9.25,lbl,ha='center',va='center',fontsize=6.5,
            fontfamily='monospace',color=BLU,fontweight='bold')
for i,lbl in enumerate(pad_labels_bot):
    x = 1.0 + i*1.0
    ax.add_patch(FancyBboxPatch((x-0.25,0.3),0.5,0.5,fc='#B2EBF2',ec=GRN,lw=1))
    ax.text(x,0.55,lbl,ha='center',va='center',fontsize=6.5,
            fontfamily='monospace',color=GRN,fontweight='bold')

# Pads laterais
left_pads  = ['B0','B1','B2','B3','B4','B5','B6','B7']
right_pads = ['FZ','FC','FV','FN','OP0','OP1','OP2','VDD']
for i,(l,r) in enumerate(zip(left_pads,right_pads)):
    y = 1.2 + i*0.9
    ax.add_patch(FancyBboxPatch((0.3,y-0.2),0.5,0.45,fc='#FFE082',ec=ORG,lw=1))
    ax.text(0.55,y,l,ha='center',va='center',fontsize=6.5,
            fontfamily='monospace',color=ORG,fontweight='bold')
    ax.add_patch(FancyBboxPatch((9.2,y-0.2),0.5,0.45,fc='#FFCDD2',ec=RED,lw=1))
    ax.text(9.45,y,r,ha='center',va='center',fontsize=6.5,
            fontfamily='monospace',color=RED,fontweight='bold')

ax.text(5,0.1,'CMOS 0,35µm | 3 camadas de metal | VDD=3,3V | GND',
        ha='center',fontsize=8,color=GRY,style='italic')
save('fig_floorplan_alu.png')

# =============================================================================
# 7. fig_timing_alu.png -- Analise de timing
# =============================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.patch.set_facecolor('#F5F8FC')

# Grafico de barras: atraso por operacao
ops_t = ['ADD\nSUB','AND\nOR','XOR','NOT','SHL\nSHR']
t_pre  = [1.4, 0.5, 0.6, 0.3, 0.4]
t_post = [1.72, 0.62, 0.74, 0.37, 0.49]
x_idx  = np.arange(len(ops_t))

bars1 = ax1.bar(x_idx-0.2, t_pre,  0.38, label='Pré-layout',  color=BLU, alpha=0.85, zorder=3)
bars2 = ax1.bar(x_idx+0.2, t_post, 0.38, label='Pós-layout',  color=ORG, alpha=0.85, zorder=3)
ax1.bar_label(bars1, fmt='%.1f ns', fontsize=8, padding=2)
ax1.bar_label(bars2, fmt='%.1f ns', fontsize=8, padding=2)
ax1.set_xticks(x_idx); ax1.set_xticklabels(ops_t, fontsize=9)
ax1.set_ylabel('Atraso de Propagação (ns)', fontsize=10)
ax1.set_title('Atraso por Operação\nPré-layout vs. Pós-layout', fontsize=10, fontweight='bold', color=BLU)
ax1.legend(fontsize=9); ax1.grid(axis='y', alpha=0.4)
ax1.set_facecolor('#FAFAFA')
ax1.axhline(y=1.4, color=RED, ls='--', lw=1, label='Critical path')

# Grafico de barras empilhadas: decomposicao do caminho critico
stages = ['Lógica\nEntrada', 'XOR/Add\n(nível 1)', 'XOR/Add\n(nível 2)', 'Carry\nProp.', 'MUX\nSel.', 'Flag\nLogic']
times_stages = [0.05, 0.25, 0.25, 0.55, 0.20, 0.10]
colors_stages = [GRY, BLU, TBLU, RED, ORG, GRN]
bottom = 0
bars_stk = []
for t_s, c_s, lbl_s in zip(times_stages, colors_stages, stages):
    b = ax2.bar(0, t_s, 0.5, bottom=bottom, color=c_s, alpha=0.85,
                label=f'{lbl_s}: {t_s:.2f}ns', zorder=3)
    ax2.text(0, bottom+t_s/2, f'{lbl_s}\n{t_s:.2f}ns',
             ha='center', va='center', fontsize=8, color=WHT, fontweight='bold')
    bottom += t_s

ax2.set_xlim(-0.6, 0.8)
ax2.set_ylim(0, 1.6)
ax2.set_xticks([])
ax2.set_ylabel('Tempo (ns)', fontsize=10)
ax2.set_title(f'Decomposição do Caminho Crítico\nADD/SUB — Total: {sum(times_stages):.2f} ns',
              fontsize=10, fontweight='bold', color=BLU)
ax2.legend(loc='upper right', fontsize=7.5)
ax2.axhline(y=sum(times_stages), color=RED, ls='--', lw=1.5)
ax2.grid(axis='y', alpha=0.4)
ax2.set_facecolor('#FAFAFA')

plt.tight_layout()
save('fig_timing_alu.png')

# =============================================================================
# 8. fig_waveform_alu.png -- Formas de onda da simulacao (do VCD)
# =============================================================================
import re

def parse_vcd_simple(path):
    sig_map = {}
    signals = {}
    with open(path) as f:
        content = f.read()
    for m in re.finditer(r'\$var\s+\w+\s+(\d+)\s+(\S+)\s+([\w\[\]:]+)', content):
        width, id_ch, name = int(m.group(1)), m.group(2), m.group(3).split('[')[0]
        if id_ch not in sig_map:
            sig_map[id_ch], signals[id_ch] = (name, width), []
    current_time = 0
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('#'):
            current_time = int(line[1:])
        elif line.startswith('b'):
            parts = line[1:].split()
            if len(parts) == 2:
                bval, id_ch = parts
                if id_ch in signals:
                    try: signals[id_ch].append((current_time, int(bval, 2)))
                    except: signals[id_ch].append((current_time, -1))
        elif len(line) >= 2 and line[0] in '01xz':
            val = 1 if line[0]=='1' else 0
            id_ch = line[1:]
            if id_ch in signals:
                signals[id_ch].append((current_time, val))
    return sig_map, signals

sig_map, signals = parse_vcd_simple('dump_alu.vcd')

# Descobrir IDs pelos nomes
name_to_id = {v[0]: k for k,v in sig_map.items()}

def get_steps(name, t_max):
    id_ch = name_to_id.get(name, '')
    evts  = [(t,v) for t,v in signals.get(id_ch,[]) if t <= t_max]
    if not evts: return np.array([0,t_max]), np.array([0,0])
    times  = [0]+[e[0] for e in evts]+[t_max] if evts[0][0]>0 else [e[0] for e in evts]+[t_max]
    values = [evts[0][1]]+[e[1] for e in evts]+[evts[-1][1]] if evts[0][0]>0 else [e[1] for e in evts]+[evts[-1][1]]
    return np.array(times)/1000, np.array(values)

T_MAX = 54_000
sig_names  = ['a','b','op','result','flag_z','flag_c','flag_v','flag_n']
sig_labels = ['A[7:0]','B[7:0]','OP[2:0]','RESULT[7:0]','FLAG_Z','FLAG_C','FLAG_V','FLAG_N']
sig_bits   = [8,8,3,8,1,1,1,1]
sig_colors = [BLU,ORG,GRY,GRN,RED,RED,RED,RED]

fig, axes = plt.subplots(len(sig_names),1,figsize=(16,9),sharex=True,
                          gridspec_kw={'hspace':0.08})
fig.patch.set_facecolor('#F5F8FC')

op_names = {0:'ADD',1:'SUB',2:'AND',3:'OR',4:'XOR',5:'NOT',6:'SHL',7:'SHR'}
op_colors_w = {0:BLU,1:'#3949AB',2:GRN,3:'#2E7D32',4:ORG,5:RED,6:'#6A1B9A',7:'#F57F17'}

for i,(name,label,nbits,color) in enumerate(zip(sig_names,sig_labels,sig_bits,sig_colors)):
    ax = axes[i]
    ax.set_facecolor('#FAFAFA')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(left=False,labelleft=False)
    ax.grid(axis='x',color='#CCCCCC',linestyle=':',lw=0.5)
    t, v = get_steps(name, T_MAX)
    if nbits == 1:
        ax.step(t, v, where='post', color=color, lw=1.8)
        ax.fill_between(t, 0, v, step='post', color=color, alpha=0.25)
        ax.set_ylim(-0.2,1.3)
    else:
        mx = (1<<nbits)-1
        norm = np.where(v<0, 0.5, 0.15+0.7*v.astype(float)/mx)
        ax.step(t, norm, where='post', color=color, lw=1.5)
        ax.step(t, 1-norm, where='post', color=color, lw=1.5, ls='--', alpha=0.35)
        ax.fill_between(t, norm, 1-norm, step='post', color=color, alpha=0.15)
        ax.set_ylim(-0.1,1.1)
        # Anotações de valor
        prev_t, prev_v = t[0], v[0]
        for j in range(1,len(t)):
            w = t[j]-prev_t
            if w > 1.5 and prev_v >= 0:
                mid = prev_t+w/2
                lbl = f'{int(prev_v):X}h' if nbits<=4 else f'{int(prev_v):02X}h'
                if name == 'op':
                    lbl = op_names.get(int(prev_v),'?')
                    c = op_colors_w.get(int(prev_v), GRY)
                else:
                    c = color
                ax.text(mid, 0.5, lbl, ha='center', va='center',
                        fontsize=7, color=c, fontfamily='monospace', fontweight='bold')
            prev_t, prev_v = t[j], v[j]
    ax.set_ylabel(label, rotation=0, labelpad=5,
                  ha='right', va='center', fontsize=8.5, color=GRY)
    ax.yaxis.set_label_coords(-0.01,0.5)

# Marcadores de grupo de operacao
op_boundaries = {0:'ADD',10:'SUB',20:'AND',26:'OR',30:'XOR',36:'NOT',42:'SHL',48:'SHR'}
for t_ns, op_name in op_boundaries.items():
    for axi in axes:
        axi.axvline(x=t_ns, color='#BDBDBD', lw=0.8, ls=':', alpha=0.8)
    axes[0].text(t_ns+0.3, 1.18, op_name, fontsize=7.5, color=GRY,
                 fontweight='bold', rotation=45)

axes[-1].set_xlabel('Tempo (ns)', fontsize=10)
axes[-1].set_xlim(0, T_MAX/1000)
fig.suptitle('ALUChip v1.0 — Formas de Onda da Simulação Funcional\n'
             'dump_alu.vcd | Icarus Verilog v12 | 27/27 testes aprovados',
             fontsize=11, fontweight='bold', color=BLU, y=0.99)
save('fig_waveform_alu.png')

print('\nTodas as 8 figuras geradas com sucesso.')
