"""Gera fig_waveform_mux.png a partir dos dados da simulacao do MUX 4:1."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Dados da simulacao (tempo em ns, timescale 1ns/1ps)
# t=0..10: S=00, Y=AA ; t=10..20: S=01, Y=BB ; t=20..30: S=10, Y=CC ; t=30..40: S=11, Y=DD

T  = [0, 10, 10, 20, 20, 30, 30, 40]
S1 = [0,  0,  0,  0,  1,  1,  1,  1]  # bit [1] de S
S0 = [0,  0,  1,  1,  0,  0,  1,  1]  # bit [0] de S

# Dados de entrada (constantes)
D0 = [0xAA]*8
D1 = [0xBB]*8
D2 = [0xCC]*8
D3 = [0xDD]*8

# Saida Y: muda conforme selecao
Y  = [0xAA, 0xAA, 0xBB, 0xBB, 0xCC, 0xCC, 0xDD, 0xDD]

fig, axes = plt.subplots(7, 1, figsize=(10, 7), sharex=True)
fig.patch.set_facecolor("white")

colors = {
    "d0": "#4e9af1", "d1": "#4ecb71", "d2": "#f1a44e", "d3": "#e06cc0",
    "s1": "#888", "s0": "#888", "y": "#e05050"
}

def plot_bus(ax, t, vals, color, label, fmt="hex"):
    xs = np.array(t)
    ax.set_xlim(-1, 42)
    ax.set_ylim(-0.3, 1.3)
    ax.set_yticks([])
    ax.set_ylabel(label, rotation=0, labelpad=38, va="center", fontsize=9,
                  fontfamily="monospace", fontweight="bold")
    ax.spines[:].set_visible(False)
    ax.axhline(0.5, color="lightgray", linewidth=0.4, zorder=0)

    prev = None
    for i in range(len(vals)-1):
        v = vals[i]
        x0, x1 = xs[i], xs[i+1]
        if v != prev:
            # transition marks
            ax.plot([x0, x0+0.4], [0, 1], color=color, linewidth=1.2)
            ax.plot([x0, x0+0.4], [1, 0], color=color, linewidth=1.2)
        ax.plot([x0+0.4, x1], [1, 1], color=color, linewidth=1.2)
        ax.plot([x0+0.4, x1], [0, 0], color=color, linewidth=1.2)
        if fmt == "hex":
            lbl = f"0x{v:02X}"
        else:
            lbl = str(v)
        mid = (x0 + x1) / 2
        if x1 - x0 >= 3:
            ax.text(mid, 0.5, lbl, ha="center", va="center",
                    fontsize=8, fontfamily="monospace", color=color,
                    bbox=dict(fc="white", ec="none", pad=0.5))
        prev = v

def plot_bit(ax, t, vals, color, label):
    xs = np.array(t, dtype=float)
    ax.set_xlim(-1, 42)
    ax.set_ylim(-0.3, 1.3)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["0","1"], fontsize=7)
    ax.set_ylabel(label, rotation=0, labelpad=38, va="center", fontsize=9,
                  fontfamily="monospace", fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.step(xs, vals, where="post", color=color, linewidth=1.5)

signals = [
    ("d0[7:0]", D0, "bus", colors["d0"]),
    ("d1[7:0]", D1, "bus", colors["d1"]),
    ("d2[7:0]", D2, "bus", colors["d2"]),
    ("d3[7:0]", D3, "bus", colors["d3"]),
    ("s[1]",    S1, "bit", colors["s1"]),
    ("s[0]",    S0, "bit", colors["s0"]),
    ("y[7:0]",  Y,  "bus", colors["y"]),
]

for ax, (lbl, data, kind, col) in zip(axes, signals):
    if kind == "bus":
        plot_bus(ax, T, data, col, lbl)
    else:
        plot_bit(ax, T, data, col, lbl)

# Eixo X (tempo)
axes[-1].set_xlabel("Tempo de simulacao (ns)", fontsize=9)
xticks = [0, 10, 20, 30, 40]
axes[-1].set_xticks(xticks)
axes[-1].set_xticklabels([f"{x} ns" for x in xticks], fontsize=8)

# Linhas de grade verticais em cada transicao
for ax in axes:
    for xt in [10, 20, 30]:
        ax.axvline(xt, color="lightgray", linewidth=0.6, linestyle="--", zorder=0)

fig.suptitle("Formas de Onda — MUX 4:1 (DATA_WIDTH=8)", fontsize=11, fontweight="bold", y=1.01)
plt.tight_layout(h_pad=0.3)
plt.savefig("fig_waveform_mux.png", dpi=150, bbox_inches="tight")
print("Salvo: fig_waveform_mux.png")
