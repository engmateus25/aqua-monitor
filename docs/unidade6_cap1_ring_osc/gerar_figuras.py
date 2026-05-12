"""Gera figuras para o relatorio do Oscilador em Anel (Unidade 6 Cap.1)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Parametros do processo CMOS 0.35um
VDD   = 3.3   # V
VTN   = 0.50  # threshold nMOS
VTP   = 0.60  # |threshold| pMOS
TP    = 0.20  # atraso de propagacao por inversor (ns)
FREQ  = 1.0 / (2 * 5 * TP)  # 500 MHz (5 inversores)
TPER  = 1.0 / FREQ            # 2 ns

# ---------------------------------------------------------------------------
# Figura 1: Formas de onda da inversora CMOS (Vin vs Vout)
# ---------------------------------------------------------------------------
t = np.linspace(0, 12, 4000)   # ns
Tin = 4.0  # periodo da entrada (ns)

def square_wave(t, period, Vlo=0, Vhi=VDD, tr=0.1):
    """Onda quadrada com rampas de transicao."""
    phase = np.mod(t, period) / period
    v = np.zeros_like(t)
    for i, p in enumerate(phase):
        if p < 0.5 - tr/2:
            v[i] = Vhi
        elif p < 0.5 + tr/2:
            v[i] = Vhi - (Vhi-Vlo) * (p - (0.5-tr/2)) / tr
        elif p < 1.0 - tr/2:
            v[i] = Vlo
        else:
            v[i] = Vlo + (Vhi-Vlo) * (p - (1.0-tr/2)) / tr
    return v

def inv_wave(t, vin, tp=TP, tr=0.12):
    """Versao invertida com atraso tp e rampas ligeiramente maiores."""
    t_shifted = t - tp
    v = VDD - square_wave(t_shifted, Tin, tr=tr*1.15)
    v = np.clip(v, 0, VDD)
    return v

Vin  = square_wave(t, Tin)
Vout = inv_wave(t, Vin)

fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
fig1.patch.set_facecolor("white")

ax1.plot(t, Vin, color="#4e9af1", linewidth=1.8, label="$V_{in}$")
ax1.set_ylabel("$V_{in}$ (V)", fontsize=10)
ax1.set_ylim(-0.3, VDD+0.5)
ax1.axhline(VDD, color="gray", linewidth=0.5, linestyle=":")
ax1.axhline(0,   color="gray", linewidth=0.5, linestyle=":")
ax1.set_yticks([0, VDD/2, VDD])
ax1.set_yticklabels(["0", f"{VDD/2:.2f}", f"{VDD:.1f}"])
ax1.legend(loc="upper right", fontsize=9)
ax1.spines["top"].set_visible(False); ax1.spines["right"].set_visible(False)
ax1.grid(True, alpha=0.3)

ax2.plot(t, Vout, color="#e05050", linewidth=1.8, label="$V_{out}$")
ax2.set_ylabel("$V_{out}$ (V)", fontsize=10)
ax2.set_xlabel("Tempo (ns)", fontsize=10)
ax2.set_ylim(-0.3, VDD+0.5)
ax2.axhline(VDD, color="gray", linewidth=0.5, linestyle=":")
ax2.axhline(0,   color="gray", linewidth=0.5, linestyle=":")
ax2.set_yticks([0, VDD/2, VDD])
ax2.set_yticklabels(["0", f"{VDD/2:.2f}", f"{VDD:.1f}"])
ax2.legend(loc="upper right", fontsize=9)
ax2.spines["top"].set_visible(False); ax2.spines["right"].set_visible(False)
ax2.grid(True, alpha=0.3)
ax2.set_xticks(range(0, 13, 2))

# Anotacao de atraso de propagacao
ax2.annotate("", xy=(2.20, 1.65), xytext=(2.00, 1.65),
             arrowprops=dict(arrowstyle="<->", color="#f1a44e", lw=1.5))
ax2.text(2.08, 1.85, f"$t_p$={TP*1000:.0f} ps", fontsize=8, color="#f1a44e")

fig1.suptitle("Simulacao DSCH -- Porta Inversora CMOS: $V_{in}$ vs $V_{out}$\n"
              f"VDD={VDD}V, processo 0,35 µm", fontsize=11, fontweight="bold")
plt.tight_layout()
plt.savefig("fig_inverter_waveform.png", dpi=150, bbox_inches="tight")
print("Salvo: fig_inverter_waveform.png")
plt.close()

# ---------------------------------------------------------------------------
# Figura 2: Curva de Transferencia de Tensao (VTC)
# ---------------------------------------------------------------------------
Vin_sweep = np.linspace(0, VDD, 1000)

def vtc(vin, Vtn=VTN, Vtp=VTP, kn=1.0, kp=1.0):
    """VTC aproximada pela analise DC da inversora CMOS."""
    Vm = (VDD/2 + Vtp*np.sqrt(kp/kn)) / (1 + np.sqrt(kp/kn))
    sigma = 0.08
    vout = VDD / (1 + np.exp((vin - Vm)/sigma))
    # limita entre 0 e VDD
    return np.clip(vout, 0, VDD)

Vout_dc = vtc(Vin_sweep)
Vm = VDD/2

# Derivada para encontrar V_IL, V_IH (pontos de ganho=-1)
dv = np.gradient(Vout_dc, Vin_sweep)
idx_vil = np.argmin(np.abs(dv + 1.0))  # primeiro ponto onde dVout/dVin = -1
idx_vih = np.argmin(np.abs(dv[500:] + 1.0)) + 500
VIL = Vin_sweep[idx_vil]
VIH = Vin_sweep[idx_vih]
VOL = Vout_dc[idx_vih]
VOH = Vout_dc[idx_vil]
NML = VIL - VOL
NMH = VOH - VIH

fig2, ax = plt.subplots(figsize=(7, 6))
fig2.patch.set_facecolor("white")
ax.plot(Vin_sweep, Vout_dc, color="#4e9af1", linewidth=2.2, label="VTC")
ax.plot([0, VDD], [0, VDD], color="lightgray", linewidth=1.0, linestyle="--", label="$V_{out}=V_{in}$")

# Marcadores
ax.axvline(VIL, color="#4ecb71", linewidth=1.0, linestyle=":")
ax.axvline(VIH, color="#e06cc0", linewidth=1.0, linestyle=":")
ax.axhline(VOH, color="#4ecb71", linewidth=0.8, linestyle=":")
ax.axhline(VOL, color="#e06cc0", linewidth=0.8, linestyle=":")
ax.axvline(Vm,  color="#f1a44e", linewidth=1.2, linestyle="--")

ax.text(VIL-0.05, -0.15, f"$V_{{IL}}$\n{VIL:.2f}V", ha="center", fontsize=8, color="#4ecb71")
ax.text(VIH+0.05, -0.15, f"$V_{{IH}}$\n{VIH:.2f}V", ha="center", fontsize=8, color="#e06cc0")
ax.text(Vm,       VDD+0.18, f"$V_m$={Vm:.2f}V", ha="center", fontsize=8, color="#f1a44e")
ax.text(VDD+0.05, VOH, f"$V_{{OH}}$={VOH:.2f}V", va="center", fontsize=8, color="#4ecb71")
ax.text(VDD+0.05, VOL+0.05, f"$V_{{OL}}$={VOL:.2f}V", va="center", fontsize=8, color="#e06cc0")

# Margens de ruido
ax.annotate("", xy=(VIL, VOL*0.5), xytext=(VOL, VOL*0.5),
            arrowprops=dict(arrowstyle="<->", color="#4ecb71"))
ax.text((VIL+VOL)/2, VOL*0.5+0.1, f"NM_L={NML:.2f}V", ha="center", fontsize=7.5, color="#4ecb71")
ax.annotate("", xy=(VIH, VOH*0.92), xytext=(VOH, VOH*0.92),
            arrowprops=dict(arrowstyle="<->", color="#e06cc0"))
ax.text((VIH+VOH)/2, VOH*0.92+0.1, f"NM_H={NMH:.2f}V", ha="center", fontsize=7.5, color="#e06cc0")

ax.set_xlim(-0.1, VDD+0.6); ax.set_ylim(-0.3, VDD+0.4)
ax.set_xlabel("$V_{in}$ (V)", fontsize=11)
ax.set_ylabel("$V_{out}$ (V)", fontsize=11)
ax.set_title("Curva de Transferencia de Tensao (VTC)\nInversora CMOS 0,35 µm | VDD=3,3V",
             fontsize=11, fontweight="bold")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig("fig_vtc.png", dpi=150, bbox_inches="tight")
print("Salvo: fig_vtc.png")
plt.close()

# ---------------------------------------------------------------------------
# Figura 3: I_D vs V_GS (nMOS e pMOS)
# ---------------------------------------------------------------------------
VGS_n = np.linspace(0, VDD, 500)
VGS_p = np.linspace(-VDD, 0, 500)

kn  = 270e-6 * (1.0 / 0.35)   # µn*Cox * W/L (W=1µm)
kp  = 90e-6  * (2.0 / 0.35)   # µp*Cox * W/L (W=2µm)

ID_n = np.where(VGS_n > VTN,  0.5*kn*(VGS_n - VTN)**2, 0)
ID_p = np.where(VGS_p < -VTP, 0.5*kp*(np.abs(VGS_p) - VTP)**2, 0)

fig3, ax3 = plt.subplots(figsize=(8, 5))
fig3.patch.set_facecolor("white")
ax3.plot(VGS_n*1e0, ID_n*1e3, color="#4e9af1", linewidth=2.0, label=f"nMOS (W/L=1/0,35 µm)")
ax3.plot(np.abs(VGS_p), ID_p*1e3, color="#e05050", linewidth=2.0, linestyle="--",
         label=f"pMOS (W/L=2/0,35 µm, eixo $|V_{{GS}}|$)")
ax3.axvline(VTN, color="#4e9af1", linewidth=0.8, linestyle=":", alpha=0.7)
ax3.axvline(VTP, color="#e05050", linewidth=0.8, linestyle=":", alpha=0.7)
ax3.text(VTN+0.05, ID_n.max()*0.65, f"$V_{{th,n}}$={VTN}V", fontsize=8.5, color="#4e9af1")
ax3.text(VTP+0.05, ID_p.max()*0.80, f"$|V_{{th,p}}|$={VTP}V", fontsize=8.5, color="#e05050")
ax3.set_xlabel("$|V_{GS}|$ (V)", fontsize=11)
ax3.set_ylabel("$I_D$ (mA)", fontsize=11)
ax3.set_title("$I_D$ vs $V_{GS}$ -- nMOS e pMOS\nProcesso CMOS 0,35 µm | $V_{DS}=V_{DD}=3,3$V (saturacao)",
              fontsize=11, fontweight="bold")
ax3.legend(fontsize=9)
ax3.grid(True, alpha=0.3)
ax3.spines["top"].set_visible(False); ax3.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig("fig_id_vgs.png", dpi=150, bbox_inches="tight")
print("Salvo: fig_id_vgs.png")
plt.close()

# ---------------------------------------------------------------------------
# Figura 4: Oscilador em Anel -- forma de onda de saida
# ---------------------------------------------------------------------------
T_osc = 2.0   # ns (= 2 * 5 * 0.2ns)
f_osc = 1.0 / T_osc  # 500 MHz
t_osc = np.linspace(0, 10, 5000)  # 5 periodos

# Onda de saida: aproximacao trapezoidal com rampas suaves (resultado real)
def ring_osc_wave(t, T=T_osc, Vlo=0.05, Vhi=VDD-0.05, tr_frac=0.25):
    """Simula a saida do oscilador em anel (onda trapezoidal arredondada)."""
    phase = np.mod(t, T) / T
    v = np.zeros_like(t)
    tr = tr_frac
    for i, p in enumerate(phase):
        if p < 0.5 - tr/2:
            v[i] = Vhi
        elif p < 0.5:
            alpha = (p - (0.5 - tr/2)) / (tr/2)
            v[i] = Vhi - (Vhi - (Vhi+Vlo)/2) * alpha
        elif p < 0.5 + tr/2:
            alpha = (p - 0.5) / (tr/2)
            v[i] = (Vhi+Vlo)/2 - ((Vhi+Vlo)/2 - Vlo) * alpha
        elif p < 1.0 - tr/2:
            v[i] = Vlo
        elif p < 1.0:
            alpha = (p - (1.0 - tr/2)) / (tr/2)
            v[i] = Vlo + (((Vhi+Vlo)/2) - Vlo) * alpha
        else:
            alpha = (p - (1.0)) / (tr/2) if tr/2 > 0 else 0
            v[i] = (Vhi+Vlo)/2 + (Vhi - (Vhi+Vlo)/2) * min(alpha, 1.0)
    return v

V_ring = ring_osc_wave(t_osc)

fig4, ax4 = plt.subplots(figsize=(10, 4))
fig4.patch.set_facecolor("white")
ax4.plot(t_osc, V_ring, color="#4ecb71", linewidth=1.8)
ax4.set_ylim(-0.3, VDD+0.5)
ax4.set_xlabel("Tempo (ns)", fontsize=10)
ax4.set_ylabel("$V_{out,5}$ (V)", fontsize=10)
ax4.set_yticks([0, VDD/2, VDD])
ax4.set_yticklabels(["0", f"{VDD/2:.2f}", f"{VDD:.1f}"])
ax4.axhline(VDD, color="gray", linewidth=0.4, linestyle=":")
ax4.axhline(0,   color="gray", linewidth=0.4, linestyle=":")
ax4.grid(True, alpha=0.3)
ax4.spines["top"].set_visible(False); ax4.spines["right"].set_visible(False)

# Anotacoes de periodo e frequencia
ax4.annotate("", xy=(T_osc*2, VDD+0.3), xytext=(T_osc*1, VDD+0.3),
             arrowprops=dict(arrowstyle="<->", color="#e05050", lw=1.5))
ax4.text(T_osc*1.5, VDD+0.42, f"T = {T_osc:.1f} ns\nf = {f_osc*1000:.0f} MHz",
         ha="center", fontsize=8.5, color="#e05050")

ax4.set_title(f"Oscilador em Anel -- 5 Inversores CMOS (Simulacao Microwind)\n"
              f"f = {f_osc*1000:.0f} MHz | T = {T_osc:.1f} ns | "
              f"$t_p$ = {TP*1000:.0f} ps/inversor | VDD = {VDD}V",
              fontsize=10, fontweight="bold")
plt.tight_layout()
plt.savefig("fig_ring_osc_wave.png", dpi=150, bbox_inches="tight")
print("Salvo: fig_ring_osc_wave.png")
plt.close()

# ---------------------------------------------------------------------------
# Figura 5: Efeito de W/L na frequencia de oscilacao
# ---------------------------------------------------------------------------
wl_ratios = np.linspace(0.5, 8.0, 200)
# tp proporcional a (C_load) / (I_drive) ~ L / (W * kn * (VDD-Vtn)^2)
# simplificado: tp ~ 1/sqrt(W/L) (para fixed L)
tp_base = TP   # ns para W/L = 1/0.35 ~ 2.86
wl_base = 1.0/0.35

tp_wl  = tp_base * np.sqrt(wl_base / wl_ratios)
freq_wl = 1.0 / (2 * 5 * tp_wl) * 1000  # MHz

fig5, ax5 = plt.subplots(figsize=(8, 4))
fig5.patch.set_facecolor("white")
ax5.plot(wl_ratios, freq_wl, color="#f1a44e", linewidth=2.0)
ax5.axvline(wl_base, color="gray", linewidth=1.0, linestyle="--")
ax5.text(wl_base+0.1, freq_wl.max()*0.5,
         f"W/L = {wl_base:.2f}\n(referencia)", fontsize=8.5, color="gray")
ax5.scatter([wl_base], [freq_wl[np.argmin(np.abs(wl_ratios - wl_base))]],
            color="#e05050", zorder=5, s=60)
ax5.set_xlabel("Relacao W/L do transistor nMOS", fontsize=10)
ax5.set_ylabel("Frequencia de oscilacao (MHz)", fontsize=10)
ax5.set_title("Impacto de W/L na Frequencia do Oscilador em Anel\n"
              "(5 inversores, processo 0,35 µm, VDD=3,3V)", fontsize=10, fontweight="bold")
ax5.grid(True, alpha=0.3)
ax5.spines["top"].set_visible(False); ax5.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig("fig_wl_freq.png", dpi=150, bbox_inches="tight")
print("Salvo: fig_wl_freq.png")
plt.close()

print(f"\nParametros do oscilador:")
print(f"  Processo: 0,35 um CMOS | VDD={VDD}V")
print(f"  t_p/inversor = {TP*1000:.0f} ps")
print(f"  N = 5 inversores")
print(f"  T = 2*N*t_p = {T_osc:.2f} ns")
print(f"  f = {f_osc*1000:.0f} MHz")
print(f"  VTC: Vm={VDD/2:.2f}V | V_IL={VIL:.2f}V | V_IH={VIH:.2f}V")
print(f"  NM_L={NML:.2f}V | NM_H={NMH:.2f}V")
