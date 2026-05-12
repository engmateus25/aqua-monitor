import pya, math

layout = pya.Layout()
layout.read('docs/microeletronica/sar_dac_layout.gds')
top_cell = layout.top_cell()

MIM_BOT  = layout.layer(6, 0)
MIM_TOP  = layout.layer(7, 0)
MET2     = layout.layer(2, 0)
VIA      = layout.layer(8, 0)

dbu = layout.dbu  # 0.001 um/DBU

total_metal_area = 0
total_via_count  = 0
vtop_bus_len_um  = 0

for shape in top_cell.each_shape(MIM_TOP):
    if shape.is_box():
        area_um2 = shape.box.width() * shape.box.height() * dbu * dbu
        total_metal_area += area_um2

for shape in top_cell.each_shape(VIA):
    if shape.is_box():
        total_via_count += 1

for shape in top_cell.each_shape(MET2):
    if shape.is_box():
        w = shape.box.width() * dbu
        h = shape.box.height() * dbu
        vtop_bus_len_um += max(w, h)

# Parametros tipicos 180nm
# Metal2 -> Substrate: ~0.05 fF/um2 (parallel) + ~0.04 fF/um (fringe)
# Via capacitance: ~0.15 fF/via
CMIM_density  = 1.0   # fF/um2 (MIM capacitor real)
Cmetal_area   = 0.05  # fF/um2 (Metal2 to substrate)
Cmetal_fringe = 0.04  # fF/um (fringe)
Cvia          = 0.15  # fF/via

C_vtop_metal_pF  = (vtop_bus_len_um * Cmetal_area + vtop_bus_len_um * Cmetal_fringe) / 1000
C_vtop_via_pF    = (total_via_count * Cvia) / 1000
C_vtop_total_fF  = (C_vtop_metal_pF + C_vtop_via_pF) * 1000

print(f'=== EXTRACAO SIMPLIFICADA DE PARASITAS ===')
print(f'MIM Top area total:     {total_metal_area:.1f} um2')
print(f'Vtop bus length:        {vtop_bus_len_um:.1f} um')
print(f'Vias no Vtop:           {total_via_count}')
print(f'C_parasita_metal (Vtop):{C_vtop_metal_pF*1000:.2f} fF')
print(f'C_parasita_vias  (Vtop):{C_vtop_via_pF*1000:.2f} fF')
print(f'C_parasita TOTAL (Vtop):{C_vtop_total_fF:.2f} fF')
print(f'C_total_ideal:          1600.00 fF')
print(f'Razao parasita/total:   {(C_vtop_total_fF/1600)*100:.2f} %')
