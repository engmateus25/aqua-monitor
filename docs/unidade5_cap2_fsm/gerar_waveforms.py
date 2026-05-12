"""Gera fig_waveform_moore.png e fig_waveform_mealy.png para o relatorio FSM."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Sequencia de teste: "11010010111"
# Ciclos: 1..11, cada ciclo = 10 ns (clock 50 MHz)
# t: borda de subida a cada 10 ns, amostramos o estado APOS cada posedge

# Eixo de tempo: transicoes a cada 10 ns
# t = 0, 10, 20, ..., 110 (12 pontos para 11 ciclos)
T = list(range(0, 121, 10))   # [0, 10, 20, ..., 120]

# Entrada x: "11010010111"
X_vals = [1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1]

# Para waveform, cada ciclo ocupa [t_i, t_{i+1}] => preciso duplicar valores
def expand(vals):
    """Expande lista para step plot: cada valor repetido para [t_i, t_{i+1}]."""
    out = []
    for v in vals:
        out.append(v)
        out.append(v)
    return out

# Tempo expandido: [0,10, 10,20, 20,30, ...]
T_step = []
for i in range(len(T)-1):
    T_step.append(T[i])
    T_step.append(T[i+1])

# ---- MOORE FSM ---- #
# Estados apos cada posedge (inicio: IDLE=0, GOT1=1, GOT10=2, GOT101=3)
# Seq: 1  1  0  1  0  0  1  0  1  1  1
# St:  G1 G1 G10 G101 G10 IDLE G1 G10 G101 G1  G1
STATE_MOORE_names = ["IDLE","GOT1","GOT10","GOT101",
                     "GOT10","IDLE","GOT1","GOT10","GOT101","GOT1","GOT1"]
STATE_MOORE_vals  = [1,     1,     2,      3,
                     2,     0,     1,      2,     3,      1,    1]
# Saida Moore: 1 quando estado==GOT101
OUT_MOORE = [1 if s==3 else 0 for s in STATE_MOORE_vals]

# ---- MEALY FSM ---- #
# Estados apos cada posedge (IDLE=0, GOT1=1, GOT10=2)
STATE_MEALY_names = ["GOT1","GOT1","GOT10","GOT1",
                     "GOT10","IDLE","GOT1","GOT10","GOT1","GOT1","GOT1"]
STATE_MEALY_vals  = [1,     1,     2,      1,
                     2,     0,     1,      2,    1,    1,    1]
# Saida Mealy: (estado==GOT10) && (x==1) -- aferida DURANTE o ciclo (antes de posedge)
OUT_MEALY = [1 if (STATE_MEALY_vals[i]==2 and X_vals[i]==1) else 0
             for i in range(11)]

# =========================================================================
# Funcoes de plot
# =========================================================================
CLR_X      = "#4e9af1"
CLR_CLK    = "#888888"
CLR_STATE  = "#f1a44e"
CLR_OUT    = "#e05050"

def plot_clock(ax, T):
    """Desenha forma de onda do clock."""
    t_clk = []
    v_clk = []
    for i, t in enumerate(T):
        t_clk += [t, t, t+5, t+5]
        v_clk += [0, 1, 1, 0]
    ax.plot(t_clk[:-1], v_clk[:-1], color=CLR_CLK, linewidth=1.2)
    ax.set_ylim(-0.3, 1.5)
    ax.set_yticks([])
    ax.spines[:].set_visible(False)
    ax.set_ylabel("clk", rotation=0, labelpad=40, va="center",
                  fontsize=8, fontfamily="monospace", fontweight="bold")

def plot_bit_step(ax, T_pts, vals, color, label, show_detect=False):
    """Plota sinal digital com step plot."""
    ax.set_xlim(-2, 122)
    ax.set_ylim(-0.4, 1.5)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["0","1"], fontsize=7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylabel(label, rotation=0, labelpad=40, va="center",
                  fontsize=8, fontfamily="monospace", fontweight="bold")
    # Step: valor muda na borda de subida do clock
    xs = [0] + T_pts[1:]
    full_x = [0] + T_pts[1:]
    full_v = [vals[0]] + vals
    ax.step(full_x, full_v, where="post", color=color, linewidth=1.5)
    if show_detect:
        for i, (t, v) in enumerate(zip(T_pts[1:], vals)):
            if v == 1:
                ax.axvspan(t, t+10, alpha=0.15, color=color)

def plot_state_bus(ax, T_pts, state_names, color, label):
    """Plota barramento de estado com nome do estado."""
    ax.set_xlim(-2, 122)
    ax.set_ylim(-0.3, 1.3)
    ax.set_yticks([])
    ax.set_ylabel(label, rotation=0, labelpad=40, va="center",
                  fontsize=8, fontfamily="monospace", fontweight="bold")
    ax.spines[:].set_visible(False)

    T_ext = T_pts + [120]
    prev = None
    for i in range(len(state_names)):
        s = state_names[i]
        x0 = T_ext[i]
        x1 = T_ext[i+1]
        if s != prev:
            ax.plot([x0, x0+1], [0, 1], color=color, linewidth=1.2)
            ax.plot([x0, x0+1], [1, 0], color=color, linewidth=1.2)
        ax.plot([x0+1, x1], [1, 1], color=color, linewidth=1.2)
        ax.plot([x0+1, x1], [0, 0], color=color, linewidth=1.2)
        mid = (x0 + x1) / 2
        ax.text(mid, 0.5, s, ha="center", va="center",
                fontsize=7, fontfamily="monospace", color=color,
                bbox=dict(fc="white", ec="none", pad=0.3))
        prev = s

# =========================================================================
# Figura 1: Moore FSM
# =========================================================================
fig1, axes1 = plt.subplots(4, 1, figsize=(12, 5), sharex=True)
fig1.patch.set_facecolor("white")

T_posedge = list(range(10, 120, 10))   # [10,20,...,110] -- momentos de transicao

plot_clock(axes1[0], list(range(0, 120, 10)))
plot_bit_step(axes1[1], [0]+T_posedge, X_vals, CLR_X, "x")
plot_state_bus(axes1[2], [0]+T_posedge, STATE_MOORE_names, CLR_STATE, "estado")
plot_bit_step(axes1[3], [0]+T_posedge, OUT_MOORE, CLR_OUT, "detected", show_detect=True)

axes1[-1].set_xlabel("Tempo de simulacao (ns)", fontsize=9)
axes1[-1].set_xticks(list(range(0, 121, 10)))
axes1[-1].set_xticklabels([f"{x}" for x in range(0, 121, 10)], fontsize=7, rotation=45)

for ax in axes1:
    for xt in range(10, 121, 10):
        ax.axvline(xt, color="lightgray", linewidth=0.5, linestyle="--", zorder=0)

# Marca deteccoes
for ax in axes1[1:]:
    for t_det in [40, 90]:
        ax.axvline(t_det, color=CLR_OUT, linewidth=1.0, linestyle=":", alpha=0.6)

fig1.suptitle("Formas de Onda — Moore FSM: Detector de Sequencia \"101\" (sequencia: 11010010111)",
              fontsize=10, fontweight="bold")
plt.tight_layout(h_pad=0.2)
plt.savefig("fig_waveform_moore.png", dpi=150, bbox_inches="tight")
print("Salvo: fig_waveform_moore.png")
plt.close()

# =========================================================================
# Figura 2: Mealy FSM
# =========================================================================
fig2, axes2 = plt.subplots(4, 1, figsize=(12, 5), sharex=True)
fig2.patch.set_facecolor("white")

CLR_STATE_M = "#4ecb71"

plot_clock(axes2[0], list(range(0, 120, 10)))
plot_bit_step(axes2[1], [0]+T_posedge, X_vals, CLR_X, "x")
plot_state_bus(axes2[2], [0]+T_posedge, STATE_MEALY_names, CLR_STATE_M, "estado")
plot_bit_step(axes2[3], [0]+T_posedge, OUT_MEALY, CLR_OUT, "detected", show_detect=True)

axes2[-1].set_xlabel("Tempo de simulacao (ns)", fontsize=9)
axes2[-1].set_xticks(list(range(0, 121, 10)))
axes2[-1].set_xticklabels([f"{x}" for x in range(0, 121, 10)], fontsize=7, rotation=45)

for ax in axes2:
    for xt in range(10, 121, 10):
        ax.axvline(xt, color="lightgray", linewidth=0.5, linestyle="--", zorder=0)

for ax in axes2[1:]:
    for t_det in [30, 80]:   # Mealy: deteccao DURANTE ciclo (antes do posedge)
        ax.axvline(t_det, color=CLR_OUT, linewidth=1.0, linestyle=":", alpha=0.6)

fig2.suptitle("Formas de Onda — Mealy FSM: Detector de Sequencia \"101\" (sequencia: 11010010111)",
              fontsize=10, fontweight="bold")
plt.tight_layout(h_pad=0.2)
plt.savefig("fig_waveform_mealy.png", dpi=150, bbox_inches="tight")
print("Salvo: fig_waveform_mealy.png")
plt.close()

# =========================================================================
# Figura 3: Comparacao lado a lado Moore vs Mealy
# =========================================================================
fig3, axes3 = plt.subplots(3, 1, figsize=(12, 4), sharex=True)
fig3.patch.set_facecolor("white")

plot_bit_step(axes3[0], [0]+T_posedge, X_vals, CLR_X, "x (entrada)")
plot_bit_step(axes3[1], [0]+T_posedge, OUT_MOORE, CLR_STATE, "Moore\ndetected")
plot_bit_step(axes3[2], [0]+T_posedge, OUT_MEALY, CLR_STATE_M, "Mealy\ndetected")

axes3[-1].set_xlabel("Tempo de simulacao (ns)", fontsize=9)
axes3[-1].set_xticks(list(range(0, 121, 10)))
axes3[-1].set_xticklabels([f"{x}" for x in range(0, 121, 10)], fontsize=7, rotation=45)

for ax in axes3:
    for xt in range(10, 121, 10):
        ax.axvline(xt, color="lightgray", linewidth=0.5, linestyle="--", zorder=0)

patch_moore = mpatches.Patch(color=CLR_STATE, label="Moore (saida pos-posedge)")
patch_mealy = mpatches.Patch(color=CLR_STATE_M, label="Mealy (saida combinacional)")
fig3.legend(handles=[patch_moore, patch_mealy], loc="upper right",
            fontsize=8, framealpha=0.9)

fig3.suptitle("Comparacao Moore vs Mealy -- Saida sequence_detected (sequencia: 11010010111)",
              fontsize=10, fontweight="bold")
plt.tight_layout(h_pad=0.3)
plt.savefig("fig_comparacao_fsm.png", dpi=150, bbox_inches="tight")
print("Salvo: fig_comparacao_fsm.png")
plt.close()
