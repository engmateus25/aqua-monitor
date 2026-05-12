#!/usr/bin/env python3
"""
gerar_waveform.py -- Gera fig_waveform.png a partir de dump_hamming.vcd
HammingChip v1.0 | Unidade 7 | Capitulo 5 | PADIS
"""
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

# ── VCD parser minimo ────────────────────────────────────────────────────────

def parse_vcd(path):
    """Retorna dict: id -> (name, width) e dict: id -> [(time, value_int)]"""
    sig_map = {}   # id_char -> (name, width)
    signals = {}   # id_char -> [(time, int_value)]

    with open(path) as f:
        content = f.read()

    # Extrai declaracoes de variaveis
    for m in re.finditer(r'\$var\s+\w+\s+(\d+)\s+(\S+)\s+([\w\[\]:]+)', content):
        width  = int(m.group(1))
        id_ch  = m.group(2)
        name   = m.group(3).split('[')[0]   # remove [n:m]
        if id_ch not in sig_map:
            sig_map[id_ch] = (name, width)
            signals[id_ch] = []

    # Percorre eventos
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
                    try:
                        signals[id_ch].append((current_time, int(bval, 2)))
                    except ValueError:
                        signals[id_ch].append((current_time, -1))
        elif len(line) >= 2 and line[0] in '01xz':
            val  = 1 if line[0] == '1' else 0
            id_ch = line[1:]
            if id_ch in signals:
                signals[id_ch].append((current_time, val))

    return sig_map, signals


def to_steps(events, t_max):
    """Converte lista de (time, val) em arrays x, y para plot tipo degrau."""
    if not events:
        return np.array([0, t_max]), np.array([0, 0])
    times  = [e[0] for e in events]
    values = [e[1] for e in events]
    # Adiciona ponto inicial se necessario
    if times[0] > 0:
        times  = [0] + times
        values = [values[0]] + values
    # Adiciona ponto final
    times.append(t_max)
    values.append(values[-1])
    return np.array(times), np.array(values)


# ── Parsing ──────────────────────────────────────────────────────────────────
sig_map, signals = parse_vcd('dump_hamming.vcd')

# IDs relevantes (do VCD inspecionado)
# % = data_in, # = encoded, & = received, $ = data_out, ! = syndrome, " = error_flag
ID = {'data_in': '%', 'encoded': '#', 'received': '&',
      'data_out': '$', 'syndrome': '!', 'error_flag': '"'}

T_MAX = 240_000   # primeiros 120 ns (60 ciclos * 2ns) -- fase round-trip + inicio fase 2

# ── Figura ───────────────────────────────────────────────────────────────────
COLORS = {
    'data_in':   '#2196F3',   # azul
    'encoded':   '#4CAF50',   # verde
    'received':  '#FF9800',   # laranja
    'data_out':  '#9C27B0',   # roxo
    'syndrome':  '#F44336',   # vermelho
    'error_flag':'#795548',   # marrom
}

LABELS = {
    'data_in':   r'$\mathtt{data\_in}$  [3:0]',
    'encoded':   r'$\mathtt{encoded}$  [6:0]',
    'received':  r'$\mathtt{received}$  [6:0]',
    'data_out':  r'$\mathtt{data\_out}$  [3:0]',
    'syndrome':  r'$\mathtt{syndrome}$  [2:0]',
    'error_flag':r'$\mathtt{error\_flag}$',
}

WIDTHS = {'data_in': 4, 'encoded': 7, 'received': 7,
          'data_out': 4, 'syndrome': 3, 'error_flag': 1}

row_order = ['data_in', 'encoded', 'received', 'data_out', 'syndrome', 'error_flag']
n_rows = len(row_order)
row_h  = 1.0   # altura de cada trilha em unidades do eixo y

fig, axes = plt.subplots(n_rows, 1, figsize=(16, 8),
                          sharex=True,
                          gridspec_kw={'hspace': 0.05})
fig.patch.set_facecolor('#F5F8FC')

for ax in axes:
    ax.set_facecolor('#FAFAFA')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.tick_params(left=False, labelleft=False)

for idx, name in enumerate(row_order):
    ax   = axes[idx]
    id_ch = ID[name]
    evts  = signals.get(id_ch, [])
    # filtra ate T_MAX
    evts  = [(t, v) for t, v in evts if t <= T_MAX]
    times, values = to_steps(evts, T_MAX)

    # ns
    times_ns = times / 1000.0
    color = COLORS[name]

    if WIDTHS[name] == 1:
        # sinal binario: desenha como forma de onda digital
        ax.step(times_ns, values, where='post', color=color, lw=1.8)
        ax.fill_between(times_ns, 0, values, step='post',
                        color=color, alpha=0.25)
        ax.set_ylim(-0.15, 1.25)
    else:
        # sinal de bus: desenha linhas duplas com valor hexadecimal anotado
        bits = WIDTHS[name]
        max_val = (1 << bits) - 1

        # Normaliza entre 0.15 e 0.85
        norm = np.where(values < 0, 0.5,
                        0.15 + 0.7 * values.astype(float) / max_val)
        ax.step(times_ns, norm, where='post', color=color, lw=1.6)
        ax.step(times_ns, 1 - norm, where='post', color=color, lw=1.6, linestyle='--', alpha=0.4)
        ax.fill_between(times_ns, norm, 1 - norm,
                        step='post', color=color, alpha=0.18)
        ax.set_ylim(-0.05, 1.1)

        # Anota valor em hex nos segmentos
        prev_t = times_ns[0]
        prev_v = values[0]
        for i in range(1, len(times_ns)):
            seg_w = times_ns[i] - prev_t
            if seg_w > 2 and prev_v >= 0:
                mid_t = prev_t + seg_w / 2
                if WIDTHS[name] <= 4:
                    label = f'{int(prev_v):X}h'
                else:
                    label = f'{int(prev_v):02X}h'
                ax.text(mid_t, 0.5, label,
                        ha='center', va='center',
                        fontsize=7, color=color,
                        fontfamily='monospace',
                        fontweight='bold')
            prev_t = times_ns[i]
            prev_v = values[i]

    # Rotulo do sinal
    ax.set_ylabel(LABELS[name], rotation=0, labelpad=5,
                  ha='right', va='center', fontsize=9, color='#333')
    ax.yaxis.set_label_coords(-0.01, 0.5)
    ax.grid(axis='x', color='#CCCCCC', linestyle=':', linewidth=0.6)

# ── Marcadores de fase ───────────────────────────────────────────────────────
ax_top = axes[0]
phase1_end = 32 * 2   # 16 round-trips * 2ns cada = 64ns... ajusta conforme simulacao
# Marca inicio da Fase 2 (estimado em t=64ns = 64_000ps)
phase2_t = 64.0  # ns
for ax in axes:
    ax.axvline(x=phase2_t, color='#E91E63', lw=1.2, linestyle='--', alpha=0.7)

axes[0].text(phase2_t / 2, 1.15, 'Fase 1: Round-trip (sem erro)',
             ha='center', fontsize=8, color='#1565C0', fontweight='bold',
             transform=axes[0].transData)
axes[0].text((phase2_t + T_MAX/1000) / 2, 1.15, 'Fase 2: Injeção de erro',
             ha='center', fontsize=8, color='#C62828', fontweight='bold',
             transform=axes[0].transData)

# ── Eixo x ───────────────────────────────────────────────────────────────────
axes[-1].set_xlabel('Tempo (ns)', fontsize=10)
axes[-1].set_xlim(0, T_MAX / 1000)

# ── Titulo ───────────────────────────────────────────────────────────────────
fig.suptitle('HammingChip v1.0 — Formas de Onda da Simulação Funcional\n'
             'Codec Hamming(7,4) | Icarus Verilog v12 | Timescale: 1ps',
             fontsize=11, fontweight='bold', color='#0A3D7A', y=0.98)

# Legenda global
legend_patches = [
    mpatches.Patch(color=COLORS[n], label=n.replace('_', r'\_'), alpha=0.8)
    for n in row_order
]
fig.legend(handles=legend_patches, loc='lower center', ncol=6,
           fontsize=8, framealpha=0.8,
           bbox_to_anchor=(0.5, 0.01))

plt.savefig('fig_waveform.png', dpi=160, bbox_inches='tight',
            facecolor=fig.get_facecolor())
plt.close()
print('Salvo: fig_waveform.png')
