"""
Converte SVGs de simulacao para PNG usando cairosvg via KLayout Python
Se nao disponivel, usa abordagem alternativa de render via Qt
"""
import pya, os

base = "u:/projetos/aqua-monitor/docs/microeletronica/"

svgs = [
    "fig_comparacao_pre_pos.svg",
    "fig_zoom_decisao.svg",
]

for svg_name in svgs:
    svg_path = base + svg_name
    png_path = base + svg_name.replace(".svg", ".png")

    # Usa QSvgRenderer + QImage via Qt (disponivel no KLayout)
    from PyQt5.QtSvg import QSvgRenderer
    from PyQt5.QtGui import QImage, QPainter
    from PyQt5.QtCore import Qt, QSize

    renderer = QSvgRenderer(svg_path)
    sz = renderer.defaultSize()
    img = QImage(sz.width() * 2, sz.height() * 2, QImage.Format_ARGB32)  # 2x para qualidade
    img.fill(Qt.white)
    painter = QPainter(img)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.TextAntialiasing, True)
    renderer.render(painter)
    painter.end()
    img.save(png_path)
    print(f"PNG salvo: {png_path} ({sz.width()}x{sz.height()} -> {sz.width()*2}x{sz.height()*2}px)")

print("Conversao concluida.")
