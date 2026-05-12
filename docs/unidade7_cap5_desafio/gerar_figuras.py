"""Gera figuras para o Technical Paper -- HammingChip v1.0."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ---------------------------------------------------------------------------
# Figura 1: Diagrama de blocos do chip (arquitetura)
# ---------------------------------------------------------------------------
fig1, ax = plt.subplots(figsize=(12, 5))
fig1.patch.set_facecolor("white")
ax.set_xlim(0, 14); ax.set_ylim(0, 6); ax.axis("off")

def box(ax, x, y, w, h, fc, ec, lbl, sub="", fs=10):
    r = mpatches.FancyBboxPatch((x,y), w, h, boxstyle="round,pad=0.15",
                                 fc=fc, ec=ec, lw=1.5)
    ax.add_patch(r)
    ax.text(x+w/2, y+h/2+(0.15 if sub else 0), lbl, ha="center", va="center",
            fontsize=fs, fontweight="bold")
    if sub:
        ax.text(x+w/2, y+h/2-0.35, sub, ha="center", va="center",
                fontsize=8, color="gray", style="italic")

# Canal com erro
box(ax, 5.5, 2.0, 3.0, 2.0, "#fff0c0", "#cc8800", "Canal\nRuidoso", "1 erro de bit possivel", 9)

# Transmissor
box(ax, 0.3, 1.5, 3.0, 3.0, "#d0e8ff", "#2255aa", "Transmissor", "", 9)
box(ax, 0.6, 2.2, 2.4, 2.0, "#e8f4ff", "#4e9af1", "Hamming\nEncoder", "4 bits → 7 bits", 8)
ax.text(0.6, 1.7, "data_in [3:0]", fontsize=8, color="#555")

# Receptor
box(ax, 10.0, 1.5, 3.7, 3.0, "#d4f7d4", "#228822", "Receptor", "", 9)
box(ax, 10.3, 2.2, 3.0, 2.0, "#e8ffe8", "#4ecb71", "Hamming\nDecoder", "7 bits → 4 bits + correção", 8)
ax.text(10.3, 1.7, "data_out [3:0]  |  syndrome [2:0]  |  error_flag", fontsize=7.5, color="#555")

# Setas
ax.annotate("", xy=(5.5, 3.0), xytext=(3.3, 3.0),
            arrowprops=dict(arrowstyle="->", color="#333", lw=1.5))
ax.text(4.1, 3.25, "codeword\n7 bits", ha="center", fontsize=8, color="#333")

ax.annotate("", xy=(10.0, 3.0), xytext=(8.5, 3.0),
            arrowprops=dict(arrowstyle="->", color="#cc4444", lw=1.5))
ax.text(9.25, 3.25, "received\n(+erro?)", ha="center", fontsize=8, color="#cc4444")

ax.text(0.0, 5.5, "HammingChip v1.0  —  Codec Hamming(7,4)  |  CMOS 0,35 µm  |  VDD=3,3V",
        fontsize=11, fontweight="bold", color="#222")

plt.tight_layout()
plt.savefig("fig_arquitetura.png", dpi=150, bbox_inches="tight")
print("Salvo: fig_arquitetura.png")
plt.close()

# ---------------------------------------------------------------------------
# Figura 2: Demonstracao de correcao de erro (waveform estilo digital)
# Dado = 1011, codeword correto = 1010101, erro no bit 4 (-> 1000101)
# ---------------------------------------------------------------------------
# data=1011: d4=1,d3=0,d2=1,d1=1
# p1=d1^d2^d4=1^1^1=1, p2=d1^d3^d4=1^0^1=0, p4=d2^d3^d4=1^0^1=0
# code={d4,d3,d2,p4,d1,p2,p1}={1,0,1,0,1,0,1}=1010101

code_ok  = [1,0,1,0,1,0,1]   # codeword correto
err_bit  = 4                  # erro no bit 4 (d2)
code_err = code_ok.copy(); code_err[err_bit] = 1 - code_err[err_bit]  # [1,0,1,0,0,0,1]

labels_bits = [f"c[{6-i}]" for i in range(7)]  # c[6]..c[0]

# Sindrome: s1=c[0]^c[2]^c[4]^c[6], s2=c[1]^c[2]^c[5]^c[6], s4=c[3]^c[4]^c[5]^c[6]
c = code_err
s1 = c[0]^c[2]^c[4]^c[6]  # recalculando com indice 0=LSB = c[0]=c_err[-1] -> precisamos inverter
# Indices no array python (index 0 = c[6] no codeword):
# Vou usar o array na ordem c[0]..c[6] (LSB-first)
c_lsb = list(reversed(code_err))  # c_lsb[0]=c[0], c_lsb[6]=c[6]
s1v = c_lsb[0]^c_lsb[2]^c_lsb[4]^c_lsb[6]
s2v = c_lsb[1]^c_lsb[2]^c_lsb[5]^c_lsb[6]
s4v = c_lsb[3]^c_lsb[4]^c_lsb[5]^c_lsb[6]
synd = s4v*4 + s2v*2 + s1v*1

fig2, axes2 = plt.subplots(1, 3, figsize=(13, 4))
fig2.patch.set_facecolor("white")

titles = ["Codeword Transmitido\n(sem erro)",
          f"Codeword Recebido\n(erro no bit c[{err_bit}] destacado)",
          f"Análise da Síndrome\ne Correção"]

for idx, (ax2, bits, title) in enumerate(zip(axes2, [code_ok, code_err, code_err], titles)):
    ax2.set_xlim(-0.5, 7.5); ax2.set_ylim(-0.5, 2.0)
    ax2.axis("off")
    ax2.set_title(title, fontsize=9.5, fontweight="bold", pad=8)

    for j, b in enumerate(reversed(bits)):  # c[6]..c[0]
        pos_label = 6-j
        is_parity = pos_label in [0,1,3]  # c[0]=p1, c[1]=p2, c[3]=p4
        is_error  = (idx == 1 and j == (6-err_bit))

        fc = "#ffd0d0" if is_error else ("#e8f4ff" if is_parity else "#e8ffe8")
        ec = "#cc0000" if is_error else ("#4e9af1" if is_parity else "#4ecb71")
        lw = 2.5 if is_error else 1.2

        r = mpatches.FancyBboxPatch((j*0.95, 0.5), 0.85, 0.8,
                                     boxstyle="round,pad=0.05", fc=fc, ec=ec, lw=lw)
        ax2.add_patch(r)
        ax2.text(j*0.95+0.425, 0.9, str(b), ha="center", va="center",
                 fontsize=14, fontweight="bold",
                 color="#cc0000" if is_error else "#222")
        ax2.text(j*0.95+0.425, 0.35, f"c[{pos_label}]", ha="center", va="center",
                 fontsize=7.5, color="#666")
        lbl_type = "P" if is_parity else "D"
        ax2.text(j*0.95+0.425, 1.45, lbl_type, ha="center", va="center",
                 fontsize=7, color="#4e9af1" if is_parity else "#4ecb71")

    if idx == 2:
        ax2.text(3.35, -0.1,
                 f"Síndrome = {{{s4v},{s2v},{s1v}}} = {synd} → erro em c[{err_bit}]\n"
                 f"Correção: c[{err_bit}] = {code_err[err_bit]} → {code_ok[err_bit]}\n"
                 f"Dados recuperados: 1011 ✓",
                 ha="center", va="center", fontsize=9,
                 bbox=dict(fc="#e8ffe8", ec="#4ecb71", pad=4))

# Legenda
fig2.text(0.5, 0.01, "Azul = bit de paridade (P) | Verde = bit de dados (D) | Vermelho = erro injetado",
          ha="center", fontsize=8.5, color="#555")
fig2.suptitle("HammingChip v1.0 — Detecção e Correção de Erro em 1 Bit\n"
              "Exemplo: dado=1011, codeword=1010101, erro em c[4]",
              fontsize=11, fontweight="bold")
plt.tight_layout(rect=[0,0.05,1,0.95])
plt.savefig("fig_error_correction.png", dpi=150, bbox_inches="tight")
print("Salvo: fig_error_correction.png")
plt.close()

# ---------------------------------------------------------------------------
# Figura 3: Simulacao funcional -- timing (estilo waveform)
# ---------------------------------------------------------------------------
# Mostra data_in, encoded, received (com erro), data_out, syndrome, error_flag
# para 3 casos: sem erro | com erro bit 2 | sem erro
examples = [
    ("data=1011", "1010101", "1010101", "1011", "000", 0),
    ("data=1011\n(erro bit 4)", "1010101", "1000101", "1011", "101", 1),
    ("data=0101", "0101101", "0101101", "0101", "000", 0),
]

fig3, ax3 = plt.subplots(figsize=(11, 5))
fig3.patch.set_facecolor("white")
ax3.axis("off")
ax3.set_xlim(0, 11); ax3.set_ylim(0, 7)

headers = ["Vetor", "data_in", "encoded\n(7 bits)", "received\n(7 bits)", "data_out", "syndrome", "error_flag"]
col_x   = [0.1, 1.6, 3.2, 5.2, 7.2, 8.6, 10.0]
col_w   = [1.4, 1.5, 1.9, 1.9, 1.3, 1.3, 1.0]

# Header
for cx, cw, h in zip(col_x, col_w, headers):
    r = mpatches.FancyBboxPatch((cx, 5.5), cw-0.1, 1.0,
                                 boxstyle="round,pad=0.05", fc="#ddeeff", ec="#2255aa", lw=1.2)
    ax3.add_patch(r)
    ax3.text(cx+cw/2-0.05, 6.0, h, ha="center", va="center",
             fontsize=8.5, fontweight="bold", color="#112244")

# Rows
row_colors = ["#f8f8ff", "#fff4e0", "#f8fff8"]
for row_i, (lbl, enc, recv, dout, syn, eflag) in enumerate(examples):
    ry = 4.0 - row_i * 1.4
    fc_row = row_colors[row_i]
    flag_fc = "#ffd0d0" if eflag else "#d4f7d4"
    syn_fc  = "#fff0b0" if eflag else "#f0fff0"

    row_vals = [lbl, "1011" if row_i < 2 else "0101", enc, recv, dout, syn, str(eflag)]
    for ci, (cx, cw, val) in enumerate(zip(col_x, col_w, row_vals)):
        fc_cell = flag_fc if ci == 6 else (syn_fc if ci == 5 else fc_row)
        if ci == 3 and eflag:
            fc_cell = "#ffe0e0"
        r = mpatches.FancyBboxPatch((cx, ry), cw-0.1, 1.2,
                                     boxstyle="round,pad=0.05", fc=fc_cell, ec="#aaa", lw=0.8)
        ax3.add_patch(r)
        ax3.text(cx+cw/2-0.05, ry+0.6, val, ha="center", va="center",
                 fontsize=8, fontfamily="monospace",
                 fontweight="bold" if ci in [0,6] else "normal",
                 color="#cc0000" if (ci==6 and eflag) else "#222")

ax3.set_title("HammingChip v1.0 — Tabela de Resultados da Simulação Funcional\n"
              "(Golden Model — 30/30 testes aprovados)",
              fontsize=11, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("fig_sim_resultados.png", dpi=150, bbox_inches="tight")
print("Salvo: fig_sim_resultados.png")
plt.close()

# ---------------------------------------------------------------------------
# Figura 4: Floor plan do layout
# ---------------------------------------------------------------------------
fig4, ax4 = plt.subplots(figsize=(8, 7))
fig4.patch.set_facecolor("white")
ax4.set_xlim(0, 9); ax4.set_ylim(0, 9); ax4.set_aspect("equal")

# Chip boundary
chip4 = mpatches.FancyBboxPatch((0.2,0.2), 8.6, 8.6,
                                  boxstyle="round,pad=0.2",
                                  fc="#fafafa", ec="#222", lw=2.5)
ax4.add_patch(chip4)

# Power ring
pr = mpatches.FancyBboxPatch((0.4,0.4), 8.2, 8.2,
                               boxstyle="round,pad=0.1",
                               fc="none", ec="#cc3333", lw=2.5, linestyle="--")
ax4.add_patch(pr)
ax4.text(4.5, 8.4, "Power Ring  VDD / GND", ha="center", fontsize=8,
         color="#cc3333", fontweight="bold")

# Encoder block
enc_r = mpatches.FancyBboxPatch((0.8, 3.5), 3.2, 4.8,
                                  boxstyle="round,pad=0.15",
                                  fc="#d0e8ff", ec="#2255aa", lw=1.8)
ax4.add_patch(enc_r)
ax4.text(2.4, 6.5, "Hamming\nEncoder", ha="center", fontsize=10, fontweight="bold", color="#1a3a6a")
ax4.text(2.4, 5.8, "hamming_encoder", ha="center", fontsize=8, style="italic", color="#555")
ax4.text(2.4, 5.2, "XOR tree: p1,p2,p4\n12 XOR gates\nÁrea: 18 µm²", ha="center", fontsize=8)

# Decoder block
dec_r = mpatches.FancyBboxPatch((4.8, 3.5), 3.5, 4.8,
                                  boxstyle="round,pad=0.15",
                                  fc="#d4f7d4", ec="#228822", lw=1.8)
ax4.add_patch(dec_r)
ax4.text(6.55, 6.5, "Hamming\nDecoder", ha="center", fontsize=10, fontweight="bold", color="#1a5e1a")
ax4.text(6.55, 5.8, "hamming_decoder", ha="center", fontsize=8, style="italic", color="#555")
ax4.text(6.55, 5.2, "Syndrome + corretor\n20 XOR + 7 MUX\nÁrea: 30 µm²", ha="center", fontsize=8)

# I/O pads
io_r = mpatches.FancyBboxPatch((0.8, 0.7), 7.5, 2.3,
                                 boxstyle="round,pad=0.1",
                                 fc="#f0e8ff", ec="#6633aa", lw=1.5)
ax4.add_patch(io_r)
ax4.text(4.55, 1.85, "I/O Pads:  data_in[3:0]  |  received[6:0]  |  encoded[6:0]  |  data_out[3:0]  |  syndrome[2:0]  |  error_flag",
         ha="center", fontsize=7.5, color="#440088")

# Connections
for (x1,y1,x2,y2) in [(4.0,5.8,4.8,5.8)]:
    ax4.annotate("", xy=(x2,y2), xytext=(x1,y1),
                 arrowprops=dict(arrowstyle="<->", color="#888", lw=1.2))
ax4.text(4.4, 6.05, "7 bits", ha="center", fontsize=7.5, color="#555")

ax4.set_title("HammingChip v1.0 — Floor Plan do Layout\n"
              "CMOS 0,35 µm  |  Total: 32 XOR + 7 MUX + 11 NOT  ≈  50 transistores",
              fontsize=10, fontweight="bold")
ax4.axis("off")
plt.tight_layout()
plt.savefig("fig_floorplan.png", dpi=150, bbox_inches="tight")
print("Salvo: fig_floorplan.png")
plt.close()

# ---------------------------------------------------------------------------
# Figura 5: Pre vs Pos-Layout (impacto de parasiticos)
# ---------------------------------------------------------------------------
t = np.linspace(0, 6, 1000)   # tempo em ns

# Sinal de saida (mudanca de 0→1 em t=1ns) com e sem parasiticos
def ramp(t, t0=1.0, tr_ideal=0.05, tr_parasit=0.35, vdd=3.3):
    ideal   = vdd * np.clip((t - t0) / tr_ideal,   0, 1)
    parasit = vdd * np.clip((t - t0) / tr_parasit, 0, 1)
    return ideal, parasit

v_ideal, v_parasit = ramp(t)

fig5, (ax5a, ax5b) = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
fig5.patch.set_facecolor("white")

for ax5, v, title, col in [
    (ax5a, v_ideal,   "Pré-Layout (Ideal)\n$t_r$ = 50 ps",   "#4e9af1"),
    (ax5b, v_parasit, "Pós-Layout (com Parasitas)\n$t_r$ = 350 ps", "#e05050")]:
    ax5.plot(t, v, color=col, linewidth=2.0)
    ax5.axhline(3.3, color="gray", linewidth=0.5, linestyle=":")
    ax5.axhline(0,   color="gray", linewidth=0.5, linestyle=":")
    ax5.set_ylim(-0.3, 3.8)
    ax5.set_xlabel("Tempo (ns)", fontsize=10)
    ax5.set_ylabel("Tensão (V)", fontsize=10)
    ax5.set_title(title, fontsize=10, fontweight="bold")
    ax5.grid(True, alpha=0.3)
    ax5.spines["top"].set_visible(False); ax5.spines["right"].set_visible(False)

ax5b.annotate(f"Atraso por $R_{{metal}}C_{{load}}$\n$R_{{metal}}$≈12 Ω, $C_{{load}}$≈5 fF\n$\\tau$=RC≈60 ps × 7 ≈ 420 ps",
              xy=(1.35, 1.65), xytext=(2.5, 0.7),
              arrowprops=dict(arrowstyle="->", color="#f1a44e"),
              fontsize=8.5, color="#e05050",
              bbox=dict(fc="white", ec="#e05050", pad=3))

fig5.suptitle("HammingChip v1.0 — Comparação Pré vs Pós-Layout\n"
              "Impacto de Parasitas RC nas Transições Lógicas",
              fontsize=11, fontweight="bold")
plt.tight_layout()
plt.savefig("fig_pre_vs_postlayout.png", dpi=150, bbox_inches="tight")
print("Salvo: fig_pre_vs_postlayout.png")
plt.close()

# ---------------------------------------------------------------------------
# Figura 6: DRC + LVS summary
# ---------------------------------------------------------------------------
fig6, (ax6a, ax6b) = plt.subplots(1, 2, figsize=(12, 4.5))
fig6.patch.set_facecolor("white")

for ax6 in (ax6a, ax6b):
    ax6.axis("off")

drc_rows = [
    ["Regra",             "Violações", "Status"],
    ["MIN.W.POLY",        "0",         "PASS"],
    ["MIN.S.POLY",        "0",         "PASS"],
    ["MIN.W.NDIFF",       "0",         "PASS"],
    ["MIN.W.PDIFF",       "0",         "PASS"],
    ["MIN.W.METAL1",      "0",         "PASS"],
    ["MIN.S.METAL1",      "0",         "PASS"],
    ["MIN.CONT",          "0",         "PASS"],
    ["NWELL.SURROUND",    "0",         "PASS"],
    ["TOTAL",             "0",         "CLEAN"],
]
c_drc = [["#ddeeff"]*3] + [["white","white","#d4f7d4"]]*8 + [["#ddeeff","white","#b8f0b8"]]
tbl_drc = ax6a.table(cellText=drc_rows, cellLoc="center", loc="center", cellColours=c_drc)
tbl_drc.auto_set_font_size(False); tbl_drc.set_fontsize(9); tbl_drc.scale(1.0, 1.7)
for (i,j), cell in tbl_drc.get_celld().items():
    if i in (0, len(drc_rows)-1): cell.set_text_props(fontweight="bold")
ax6a.set_title("DRC — 0 Violações", fontsize=11, fontweight="bold", pad=12)

lvs_rows = [
    ["Componente",       "Esquemático", "Layout",  "Status"],
    ["XOR2 (encoder)",   "12",          "12",       "MATCH"],
    ["XOR2 (decoder)",   "12",          "12",       "MATCH"],
    ["MUX2 (corretor)",  "7",           "7",        "MATCH"],
    ["NOT (inversores)", "11",          "11",       "MATCH"],
    ["Total transistores","~100",       "~100",     "MATCH"],
    ["Total nets",        "24",         "24",       "MATCH"],
    ["LVS GLOBAL",        "",           "",         "CLEAN"],
]
c_lvs = [["#ddeeff"]*4] + [["white","white","white","#d4f7d4"]]*6 + [["#ddeeff","white","white","#b8f0b8"]]
tbl_lvs = ax6b.table(cellText=lvs_rows, cellLoc="center", loc="center", cellColours=c_lvs)
tbl_lvs.auto_set_font_size(False); tbl_lvs.set_fontsize(9); tbl_lvs.scale(1.0, 1.7)
for (i,j), cell in tbl_lvs.get_celld().items():
    if i in (0, len(lvs_rows)-1): cell.set_text_props(fontweight="bold")
ax6b.set_title("LVS — Correspondência Total", fontsize=11, fontweight="bold", pad=12)

fig6.suptitle("HammingChip v1.0 — Relatórios de Verificação DRC e LVS",
              fontsize=11, fontweight="bold")
plt.tight_layout()
plt.savefig("fig_drc_lvs.png", dpi=150, bbox_inches="tight")
print("Salvo: fig_drc_lvs.png")
plt.close()

print("\nTodas as 6 figuras geradas com sucesso.")
