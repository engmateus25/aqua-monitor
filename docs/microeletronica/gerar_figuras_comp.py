"""
Geração das figuras do Comparador para o Relatório Final
SAR ADC Aqua Monitor — CI Amazônia U7C5
Saídas: fig_comp_dc.png, fig_comp_transiente.png, fig_comp_pre_vs_pos.png
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "lines.linewidth": 1.8,
})

# ─── Leitura dos dados ──────────────────────────────────────────────────────
def load_csv(fname, col_t, col_vinp, col_vout1, col_vout):
    t, vinp, vout1, vout = [], [], [], []
    with open(fname) as f:
        for line in f:
            v = line.split()
            if len(v) > max(col_t, col_vinp, col_vout1, col_vout):
                try:
                    t.append(float(v[col_t]))
                    vinp.append(float(v[col_vinp]))
                    vout1.append(float(v[col_vout1]))
                    vout.append(float(v[col_vout]))
                except:
                    pass
    return np.array(t), np.array(vinp), np.array(vout1), np.array(vout)

def load_dc(fname, col_inp, col_vout1, col_vout):
    inp, vout1, vout = [], [], []
    with open(fname) as f:
        for line in f:
            v = line.split()
            if len(v) > max(col_inp, col_vout1, col_vout):
                try:
                    inp.append(float(v[col_inp]));
                    vout1.append(float(v[col_vout1]))
                    vout.append(float(v[col_vout]))
                except:
                    pass
    return np.array(inp), np.array(vout1), np.array(vout)

# comp_dc_transfer.csv:  INP Vout1 Vout  (3 cols cada com tempo intercalado)
# wrdata gera: time V1 time V2 time V3 ... (time repetido por coluna)
# Colunas: 0=INP_t 1=INP 2=Vout1_t 3=Vout1 4=Vout_t 5=Vout
dc_inp, dc_vout1, dc_vout = load_dc("comp_dc_transfer.csv", 1, 3, 5)

# comp_transient.csv: time INP INM Vout1 Vout
# Colunas: 0=t 1=t 2=t 3=INP 4=t 5=INM 6=t 7=Vout1 8=t 9=Vout
t_pre, inp_pre, vout1_pre, vout_pre = load_csv("comp_transient.csv", 0, 3, 7, 9)

# comp_poslayout_tran.csv: time INP Vout1 Vout (8 colunas)
# Colunas: 0=t 1=t 2=t 3=INP 4=t 5=Vout1 6=t 7=Vout
t_pos, inp_pos, vout1_pos, vout_pos = load_csv("comp_poslayout_tran.csv", 0, 3, 5, 7)

# ═══════════════════════════════════════════════════════════════════════════
# FIGURA 1 — Curva de Transferência DC
# ═══════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 4.5))

ax.plot(dc_inp, dc_vout,  color="#1f77b4", lw=2.2, label="$V_{out}$ (comp_out)")
ax.plot(dc_inp, dc_vout1, color="#ff7f0e", lw=1.5, ls="--", label="$V_{out1}$ (saída estágio 1)")

ax.axvline(0.9,  color="gray",  lw=1, ls=":", label="$V_{INM}$ = 0.900 V")
ax.axhline(0.9,  color="green", lw=0.8, ls=":")
ax.axhline(1.8,  color="red",   lw=0.8, ls=":", alpha=0.5)
ax.axhline(0.0,  color="red",   lw=0.8, ls=":", alpha=0.5)

# Marcar threshold
ax.annotate("Threshold\n= 0.900 V",
            xy=(0.9002, 0.9), xytext=(1.1, 0.5),
            arrowprops=dict(arrowstyle="->", color="black"),
            fontsize=9, color="black")

ax.set_xlabel("$V_{INP}$ (V)", fontsize=11)
ax.set_ylabel("Tensão de Saída (V)", fontsize=11)
ax.set_title("Comparador 2 Estágios — Curva de Transferência DC\n"
             r"$V_{INM}$ = 0.9 V (ref), $V_{DD}$ = 1.8 V, CMOS 180nm", fontsize=10)
ax.set_xlim(0, 1.8)
ax.set_ylim(-0.1, 1.95)
ax.set_xticks(np.arange(0, 2.0, 0.2))
ax.set_yticks(np.arange(0, 2.0, 0.2))
ax.legend(loc="upper right", fontsize=9)

props = dict(boxstyle="round", facecolor="lightyellow", alpha=0.8)
ax.text(0.02, 0.95,
        "Ganho estágio 1: A₁ = 95 V/V (39.6 dB)\n"
        "Threshold: 0.9002 V (Δ = 0.2 mV vs INM)\n"
        "Swing de saída: 3.9 mV → 1.800 V ✓",
        transform=ax.transAxes, fontsize=8.5,
        verticalalignment="top", bbox=props)

plt.tight_layout()
plt.savefig("fig_comp_dc.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ fig_comp_dc.png gerado")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURA 2 — Resposta Transiente Pré-Layout
# ═══════════════════════════════════════════════════════════════════════════
t_ns = t_pre * 1e9

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5.5), sharex=True)

# Painel superior: entradas
ax1.plot(t_ns, inp_pre,  color="#1f77b4", lw=2, label="$V_{INP}$ (sinal)")
ax1.axhline(0.9, color="gray", lw=1, ls="--", label="$V_{INM}$ = 0.9 V (ref)")
ax1.set_ylabel("Tensão de Entrada (V)")
ax1.set_ylim(0.7, 1.1)
ax1.legend(fontsize=9, loc="upper right")
ax1.set_title("Comparador — Resposta Transiente (overdrive = 56 mV = V$_{LSB}$/2)\n"
              "Pré-Layout | CMOS 180nm", fontsize=10)

# Painel inferior: saídas
ax2.plot(t_ns, vout_pre,  color="#d62728", lw=2.2, label="$V_{out}$ (comp_out)")
ax2.plot(t_ns, vout1_pre, color="#ff7f0e", lw=1.5, ls="--", label="$V_{out1}$ (est. 1)")
ax2.axhline(0.9, color="green", lw=0.8, ls=":")
ax2.axhline(1.8, color="gray",  lw=0.8, ls=":", alpha=0.4)

# Anotar t_pd
ax2.annotate("", xy=(12.9, 0.9), xytext=(5.5, 0.9),
             arrowprops=dict(arrowstyle="<->", color="purple", lw=1.5))
ax2.text(8.5, 1.0, "$t_{pd}$ = 7.4 ns", color="purple", fontsize=9, ha="center")

# Anotar zonas
ax2.axvspan(0, 5, alpha=0.07, color="blue",  label="INP < INM → LOW")
ax2.axvspan(6, 51, alpha=0.07, color="red",  label="INP > INM → HIGH")

ax2.set_ylabel("Tensão de Saída (V)")
ax2.set_xlabel("Tempo (ns)")
ax2.set_ylim(-0.15, 2.0)
ax2.set_xlim(0, 70)
ax2.legend(fontsize=8.5, loc="upper right")

plt.tight_layout()
plt.savefig("fig_comp_transiente.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ fig_comp_transiente.png gerado")

# ═══════════════════════════════════════════════════════════════════════════
# FIGURA 3 — Comparação Pré vs Pós-Layout
# ═══════════════════════════════════════════════════════════════════════════
t_pre_ns = t_pre * 1e9
t_pos_ns = t_pos * 1e9

fig, ax = plt.subplots(figsize=(8, 4.5))

ax.plot(t_pre_ns, vout_pre, color="#1f77b4", lw=2.2, label="$V_{out}$ pré-layout (ideal)")
ax.plot(t_pos_ns, vout_pos, color="#d62728", lw=2.2, ls="--", label="$V_{out}$ pós-layout (com parasitas)")

ax.axhline(0.9, color="green", lw=0.8, ls=":", alpha=0.7)
ax.axhline(1.8, color="gray",  lw=0.8, ls=":", alpha=0.4)

# Marcar cruzamentos
ax.axvline(12.9, color="#1f77b4", lw=1, ls=":", alpha=0.6)
ax.axvline(15.5, color="#d62728", lw=1, ls=":", alpha=0.6)
ax.annotate("", xy=(15.5, 1.35), xytext=(12.9, 1.35),
            arrowprops=dict(arrowstyle="<->", color="black", lw=1.5))
ax.text(14.2, 1.42, "Δt = +2.6 ns\n(parasitas)", fontsize=8.5, ha="center", color="black")

ax.set_xlabel("Tempo (ns)", fontsize=11)
ax.set_ylabel("$V_{out}$ — comp_out (V)", fontsize=11)
ax.set_title("Comparação Pré-Layout vs Pós-Layout\n"
             r"Impacto dos Parasitas RC Extraídos do Layout ($C_{Vout1}$ = 58.5 fF)", fontsize=10)
ax.set_xlim(0, 60)
ax.set_ylim(-0.15, 2.0)
ax.legend(fontsize=10)

props2 = dict(boxstyle="round", facecolor="lightyellow", alpha=0.8)
ax.text(0.98, 0.05,
        "Pré-layout:  $t_{pd}$ = 7.4 ns\n"
        "Pós-layout: $t_{pd}$ = 10.0 ns\n"
        "ΔVth = 0.3 mV (<< $V_{LSB}$/2)\n"
        "$V_{out,max}$ = 1.800 V (ambos)",
        transform=ax.transAxes, fontsize=9,
        verticalalignment="bottom", ha="right", bbox=props2)

plt.tight_layout()
plt.savefig("fig_comp_pre_vs_pos.png", dpi=150, bbox_inches="tight")
plt.close()
print("✓ fig_comp_pre_vs_pos.png gerado")

print("\n=== RESULTADOS FINAIS DAS SIMULAÇÕES ===")
print(f"Threshold DC:         900.2 mV  (Δ = 0.2 mV vs INM=900mV ✓)")
print(f"Swing de saída:       3.9 mV → 1.800 V  (quase trilho a trilho ✓)")
print(f"Ganho estágio 1:      ~95 V/V (39.6 dB) — resolve 56mV com margem ✓")
print(f"t_pd pré-layout:      7.4 ns")
print(f"t_pd pós-layout:      10.0 ns  (Δ = +2.6 ns por parasitas)")
print(f"Impacto em % do SAR:  {10.0/(1670)*100:.2f}% do período de conversão ✓")
print(f"Área do layout:       74.4 µm × 54.1 µm = 4025 µm²")
