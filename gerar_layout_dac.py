"""
Script KLayout Python: Layout da Matriz de Capacitores Common-Centroid
SAR ADC de 4-Bits -- Aqua Monitor IC Design Project

Gera automaticamente o layout GDS da rede de capacitores MIM do DAC.
Execute via: strmrun.exe -r gerar_layout_dac.py

Tecnica: Common-Centroid para casamento de capacitores (matching).
Disposicao: Os 16 capacitores unitarios sao distribuidos em arranjo
simetrico 4x4 para mitigar gradientes de processo litografico.

Mapa de disposicao (C3=MSB=8 unidades, C2=4, C1=2, C0=1, Ct=term):
  C3 C2 C2 C3     <- linha 0 (simetria horizontal e vertical)
  C1 C0 Ct C1     <- linha 1
  C1 Ct C0 C1     <- linha 2 (espelho da linha 1)
  C3 C2 C2 C3     <- linha 3 (espelho da linha 0)

Autor: Matheus Serrão Uchoa | Projeto Aqua Monitor
"""

import pya

# ============================================================
# PARAMETROS DO PROCESSO (estilo 180nm generico educacional)
# ============================================================
DBU          = 0.001          # Database Unit = 1nm (1um = 1000 DBU)
C0_W         = 10_000         # Largura do cap unitario: 10um (em DBU)
C0_H         = 10_000         # Altura do cap unitario: 10um (em DBU)
SPACING      = 2_000          # Espacamento entre caps: 2um
GUARD_RING_W = 1_000          # Largura do anel de guarda: 1um
METAL_W      = 1_000          # Largura da trilha de metal de conexao: 1um

# Mapa de identidade de cada capacitor na grade 4x4
# C3=MSB (8u), C2(4u), C1(2u), C0(1u=LSB), Ct(terminacao)
GRID = [
    ["C3", "C2", "C2", "C3"],
    ["C1", "C0", "Ct", "C1"],
    ["C1", "Ct", "C0", "C1"],
    ["C3", "C2", "C2", "C3"],
]

# Mapeamento nome -> bit do barramento
BIT_MAP = {
    "C3": 3,  # MSB - dac_in[3]
    "C2": 2,
    "C1": 1,
    "C0": 0,  # LSB - dac_in[0]
    "Ct": -1, # Terminacao (sempre GND)
}

# Cores/camadas (simplificadas para layout educacional)
LAYER_MIM_BOT  = pya.LayerInfo(6, 0)   # Metal base do capacitor MIM
LAYER_MIM_TOP  = pya.LayerInfo(7, 0)   # Metal topo do capacitor MIM
LAYER_VIA      = pya.LayerInfo(8, 0)   # Via de conexao
LAYER_MET1     = pya.LayerInfo(1, 0)   # Metal 1 (roteamento horizontal)
LAYER_MET2     = pya.LayerInfo(2, 0)   # Metal 2 (roteamento vertical)
LAYER_GUARD    = pya.LayerInfo(9, 0)   # Anel de guarda (substrato)
LAYER_LABEL    = pya.LayerInfo(10, 0)  # Texto/Labels

def create_rect(cell, layer, x, y, w, h):
    """Insere um retangulo na celula."""
    cell.shapes(layer).insert(pya.Box(x, y, x + w, y + h))

def create_label(cell, layer, text, x, y):
    """Insere um label de texto."""
    cell.shapes(layer).insert(pya.Text(text, pya.Trans(pya.Point(x, y))))

def build_layout():
    layout = pya.Layout()
    layout.dbu = DBU

    top = layout.create_cell("SAR_DAC_4BIT_CC")

    step = C0_W + SPACING

    print("=== Gerando layout Common-Centroid do DAC ===")
    print(f"Grid: 4x4 capacitores unitarios de {C0_W/1000:.0f}um x {C0_H/1000:.0f}um")
    print(f"Pitch: {step/1000:.0f}um")

    cap_positions = {}  # nome -> lista de (x,y) dos centros

    # ---- CAPACITORES ----
    for row_idx, row in enumerate(GRID):
        for col_idx, cap_name in enumerate(row):
            x = col_idx * step
            y = row_idx * step

            # Placa inferior MIM (Metal 1)
            create_rect(top, LAYER_MIM_BOT, x, y, C0_W, C0_H)

            # Placa superior MIM (Metal 2) com recuo de 500nm
            inset = 500
            create_rect(top, LAYER_MIM_TOP, x+inset, y+inset, C0_W-2*inset, C0_H-2*inset)

            # Via central
            via_x = x + C0_W//2 - 500
            via_y = y + C0_H//2 - 500
            create_rect(top, LAYER_VIA, via_x, via_y, 1000, 1000)

            # Label com nome e posicao
            create_label(top, LAYER_LABEL, cap_name, x + 1000, y + 4000)

            # Acumula posicoes por nome
            cx, cy = x + C0_W//2, y + C0_H//2
            if cap_name not in cap_positions:
                cap_positions[cap_name] = []
            cap_positions[cap_name].append((cx, cy))

            print(f"  [{row_idx},{col_idx}] {cap_name:3s} -> ({x/1000:.0f}um, {y/1000:.0f}um)")

    total_w = 4 * step - SPACING
    total_h = 4 * step - SPACING

    # ---- ANEL DE GUARDA (Guard Ring) ----
    g = GUARD_RING_W
    # Bordas: top, bottom, left, right
    create_rect(top, LAYER_GUARD, -g-SPACING, -g-SPACING, total_w + 2*(g+SPACING), g)  # bottom
    create_rect(top, LAYER_GUARD, -g-SPACING, total_h+SPACING, total_w + 2*(g+SPACING), g)  # top
    create_rect(top, LAYER_GUARD, -g-SPACING, -g-SPACING, g, total_h + 2*(g+SPACING))  # left
    create_rect(top, LAYER_GUARD, total_w+SPACING, -g-SPACING, g, total_h + 2*(g+SPACING))  # right

    # ---- BARRAMENTO DE SAIDA (Vtop = placa superior comum) ----
    # Trilha horizontal no topo conectando todas as placas superiores
    bus_y = total_h + SPACING + 2000
    create_rect(top, LAYER_MET2, -g, bus_y, total_w + 2*g, METAL_W)
    create_label(top, LAYER_LABEL, "Vtop (-> Comparator)", 0, bus_y + 2000)

    # Labels das entradas do DAC
    for cap_name, positions in cap_positions.items():
        bit = BIT_MAP[cap_name]
        if bit >= 0:
            label = f"dac_in[{bit}]"
        else:
            label = "GND"
        # Label na base da primeira coluna de cada capacitor
        x0, y0 = positions[0]
        create_label(top, LAYER_LABEL, label, x0-2000, y0-6000)

    # ---- ESTATISTICAS ----
    print("\n=== Resumo do Layout ===")
    for name, pos in cap_positions.items():
        print(f"  {name}: {len(pos)} instancias @ {[(p[0]//1000, p[1]//1000) for p in pos]} um")
    print(f"\nArea total estimada: {total_w/1000:.0f}um x {total_h/1000:.0f}um = {(total_w*total_h)/1e12:.0f} um2")
    print(f"Capacitancia total: {16 * 100}fF = {16 * 100 / 1000:.1f}pF")

    # ---- SALVA O GDS ----
    out_path = "docs/microeletronica/sar_dac_layout.gds"
    layout.write(out_path)
    print(f"\n=== Layout salvo em: {out_path} ===")
    print("Abra com: klayout_app.exe docs/microeletronica/sar_dac_layout.gds")

    return layout

if __name__ == "__main__":
    build_layout()
