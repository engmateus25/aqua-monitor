"""Gera fig_waveform_counter.png para o relatorio do Contador Sincrono 4 bits."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Pontos de tempo (em ns) com transicoes chave
# Simplificado: mostra reset, contagem 0->7, disable, overflow, reset mid

# Tempo em ns, cada ciclo = 10ns
# Representamos os estados posedge-a-posedge
T = list(range(0, 291, 10))
N = len(T) - 1  # 29 intervalos

# Sinal clk (para representacao visual)
# rst_n: 0 nos primeiros 2 ciclos, depois 1 (exceto reset mid ~t=259)
# en: 0 inicial, 1 de t=10..75, 0 de t=76..105, 1 de t=106..fim
# count: conforme simulacao

rst_n_vals = [0,0,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,0,1]
en_vals    = [0,0,1,1,1,1,1,1,1,1, 0,0,0,1,1,1,0,1,0,1, 1,1,1,1,1,1,1,1,1]
count_vals = [0,0,0,1,2,3,4,5,6,7, 7,7,7,7,8,9,10,10,11,11, 12,13,14,15,0,1,2,3,0]

# Garantir tamanhos iguais
assert len(rst_n_vals) == N
assert len(en_vals) == N
assert len(count_vals) == N

T_step = [T[i] for i in range(N)] + [T[N]]

CLR_CLK   = "#888888"
CLR_RST   = "#e06cc0"
CLR_EN    = "#4e9af1"
CLR_CNT   = "#f1a44e"

fig, axes = plt.subplots(4, 1, figsize=(14, 6), sharex=True)
fig.patch.set_facecolor("white")

def plot_clk(ax):
    t_c, v_c = [], []
    for t in T[:-1]:
        t_c += [t, t, t+5, t+5]
        v_c += [0, 1, 1, 0]
    ax.plot(t_c, v_c, color=CLR_CLK, linewidth=1.2)
    ax.set_ylim(-0.3, 1.5); ax.set_yticks([])
    ax.spines[:].set_visible(False)
    ax.set_ylabel("clk", rotation=0, labelpad=40, va="center",
                  fontsize=8, fontfamily="monospace", fontweight="bold")

def plot_bit(ax, vals, color, label):
    xs = T_step[:N] + [T_step[N]]
    ys = [vals[0]] + vals
    ax.step(xs, ys, where="post", color=color, linewidth=1.5)
    ax.set_ylim(-0.4, 1.5); ax.set_yticks([0,1])
    ax.set_yticklabels(["0","1"], fontsize=7)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.set_ylabel(label, rotation=0, labelpad=40, va="center",
                  fontsize=8, fontfamily="monospace", fontweight="bold")

def plot_bus(ax, vals, color, label):
    ax.set_xlim(-2, 295); ax.set_ylim(-0.3, 1.3); ax.set_yticks([])
    ax.spines[:].set_visible(False)
    ax.set_ylabel(label, rotation=0, labelpad=40, va="center",
                  fontsize=8, fontfamily="monospace", fontweight="bold")
    prev = None
    for i in range(N):
        v = vals[i]; x0 = T[i]; x1 = T[i+1]
        if v != prev:
            ax.plot([x0, x0+0.5], [0,1], color=color, linewidth=1.2)
            ax.plot([x0, x0+0.5], [1,0], color=color, linewidth=1.2)
        ax.plot([x0+0.5, x1], [1,1], color=color, linewidth=1.2)
        ax.plot([x0+0.5, x1], [0,0], color=color, linewidth=1.2)
        mid = (x0+x1)/2
        if x1-x0 >= 8:
            ax.text(mid, 0.5, str(v), ha="center", va="center",
                    fontsize=7, fontfamily="monospace", color=color,
                    bbox=dict(fc="white", ec="none", pad=0.2))
        prev = v

plot_clk(axes[0])
plot_bit(axes[1], rst_n_vals, CLR_RST, "rst\\_n")
plot_bit(axes[2], en_vals,    CLR_EN,  "en")
plot_bus(axes[3], count_vals, CLR_CNT, "count[3:0]")

axes[-1].set_xlabel("Tempo de simulacao (ns)", fontsize=9)
xticks = list(range(0, 291, 20))
axes[-1].set_xticks(xticks)
axes[-1].set_xticklabels([f"{x}" for x in xticks], fontsize=7, rotation=45)

# Grades verticais
for ax in axes:
    for xt in range(0, 291, 10):
        ax.axvline(xt, color="lightgray", linewidth=0.4, linestyle="--", zorder=0)

# Anotacoes de eventos
eventos = [(10,"reset\noff"), (76,"en=0"), (106,"en=1"), (215,"overflow"), (259,"rst\nmid")]
for t_ev, lbl in eventos:
    for ax in axes:
        ax.axvline(t_ev, color="red", linewidth=0.7, linestyle=":", alpha=0.5)
    axes[0].text(t_ev+1, 1.3, lbl, fontsize=6, color="red", va="top")

fig.suptitle("Formas de Onda — Contador Sincrono 4 bits (clk=50MHz, rst_n ativo baixo, en sincrono)",
             fontsize=10, fontweight="bold")
plt.tight_layout(h_pad=0.2)
plt.savefig("fig_waveform_counter.png", dpi=150, bbox_inches="tight")
print("Salvo: fig_waveform_counter.png")
