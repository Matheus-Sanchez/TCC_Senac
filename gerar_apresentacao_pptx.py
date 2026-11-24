"""Gera a apresentacao editavel em PowerPoint (.pptx) alinhada a versao mais recente de tcc2-adaptado.tex.

Diretrizes:
- Fonte minima global de 18 pt em todos os textos, tabelas, graficos, fontes e rodapes.
- Conteudo e figuras atualizados conforme tcc2-adaptado.tex (20/11/2026), incluindo
  Senokosov et al. (2024), as 5 figuras arquiteturais e a telemetria completa da Secao 4.8
  (incluindo coleta complementar no iMac M4 com macmon).
- Referencias nas imagens e tabelas identicas as citacoes de autor do TCC escrito
  (sem referencias genericas a 'TCC, Secao X.Y').
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt


BASE_DIR = Path(__file__).resolve().parent
FIG_DIR = BASE_DIR / "figuras"
GIF_DIR = FIG_DIR / "gifs"
LOGO_PATH = BASE_DIR / "assets" / "logo-senac.png"
OUTPUT_PPTX = BASE_DIR / "apresentacao_tcc2_final.pptx"

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
MIN_FONT_PT = 18

FONT_NAME = "Calibri"
SENAC_BLUE = RGBColor(0, 51, 102)
SENAC_BLUE_MID = RGBColor(28, 72, 118)
SENAC_BLUE_LIGHT = RGBColor(235, 241, 248)
SENAC_BLUE_ALT = RGBColor(246, 249, 253)
SENAC_ORANGE = RGBColor(243, 146, 0)
SENAC_ORANGE_LIGHT = RGBColor(254, 243, 224)
OK_GREEN = RGBColor(30, 130, 76)
BAD_RED = RGBColor(176, 48, 48)
TEXT_DARK = RGBColor(24, 30, 38)
TEXT_MUTED = RGBColor(86, 96, 108)
BORDER_GRAY = RGBColor(200, 210, 222)
WHITE = RGBColor(255, 255, 255)


def fpt(size: float) -> Pt:
    return Pt(max(MIN_FONT_PT, size))


def set_cell_margins(cell, left=0.06, right=0.06, top=0.02, bottom=0.02):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.set("marL", str(int(Inches(left))))
    tcPr.set("marR", str(int(Inches(right))))
    tcPr.set("marT", str(int(Inches(top))))
    tcPr.set("marB", str(int(Inches(bottom))))


def set_cell_border(cell, color_hex="D0D9E4", width_pt=0.5):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        for old in tcPr.findall(f"{{{tcPr.nsmap['a']}}}{tag.split(':')[1]}"):
            tcPr.remove(old)
        ln = OxmlElement(tag)
        ln.set("w", str(int(width_pt * 12700)))
        ln.set("cap", "flat")
        ln.set("cmpd", "sng")
        ln.set("algn", "ctr")
        solid = OxmlElement("a:solidFill")
        srgb = OxmlElement("a:srgbClr")
        srgb.set("val", color_hex)
        solid.append(srgb)
        ln.append(solid)
        tcPr.append(ln)


def add_textbox(
    slide,
    x,
    y,
    w,
    h,
    text="",
    font_size=18,
    bold=False,
    italic=False,
    color=TEXT_DARK,
    align=PP_ALIGN.LEFT,
    valign=MSO_ANCHOR.TOP,
    line_spacing=1.10,
):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = valign
    tf.margin_left = Inches(0.04)
    tf.margin_right = Inches(0.04)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    if text:
        lines = text.split("\n")
        for idx, ln_txt in enumerate(lines):
            p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
            p.alignment = align
            p.line_spacing = line_spacing
            run = p.add_run()
            run.text = ln_txt
            run.font.name = FONT_NAME
            run.font.size = fpt(font_size)
            run.font.bold = bold
            run.font.italic = italic
            run.font.color.rgb = color
    return tb


def add_rich_paragraphs(tf, items, font_size=18, space_after=6, bullet=True, numbered=False, line_spacing=1.08):
    """Popula um text_frame com lista de itens compostos por tuplas (texto, bold, italic, cor)."""
    tf.word_wrap = True
    sz = max(MIN_FONT_PT, font_size)
    for idx, entry in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        p.line_spacing = line_spacing
        if bullet:
            r_b = p.add_run()
            r_b.text = "• "
            r_b.font.name = FONT_NAME
            r_b.font.size = fpt(sz)
            r_b.font.bold = True
            r_b.font.color.rgb = SENAC_ORANGE
        elif numbered:
            r_n = p.add_run()
            r_n.text = f"{idx + 1}. "
            r_n.font.name = FONT_NAME
            r_n.font.size = fpt(sz)
            r_n.font.bold = True
            r_n.font.color.rgb = SENAC_ORANGE

        segments = entry if isinstance(entry, list) else [(entry, False, False, TEXT_DARK)]
        for seg in segments:
            if isinstance(seg, str):
                txt, b, it, col = seg, False, False, TEXT_DARK
            else:
                txt = seg[0]
                b = seg[1] if len(seg) > 1 else False
                it = seg[2] if len(seg) > 2 else False
                col = seg[3] if len(seg) > 3 else TEXT_DARK
            r = p.add_run()
            r.text = txt
            r.font.name = FONT_NAME
            r.font.size = fpt(sz)
            r.font.bold = b
            r.font.italic = it
            r.font.color.rgb = col


def add_picture_fit(slide, img_path: Path, x, y, max_w, max_h, center_v=True):
    if not img_path.exists():
        raise FileNotFoundError(f"Imagem nao encontrada: {img_path}")
    with Image.open(img_path) as im:
        iw, ih = im.size
    ratio = iw / ih
    box_ratio = max_w / max_h
    if ratio >= box_ratio:
        w = max_w
        h = max_w / ratio
    else:
        h = max_h
        w = max_h * ratio
    px = x + (max_w - w) / 2.0
    py = y + ((max_h - h) / 2.0 if center_v else 0.0)
    return slide.shapes.add_picture(str(img_path), Inches(px), Inches(py), Inches(w), Inches(h))


def add_picture_crop_fit(
    slide,
    img_path: Path,
    x,
    y,
    max_w,
    max_h,
    crop_left=0.0,
    crop_right=0.0,
    crop_top=0.0,
    crop_bottom=0.0,
    center_v=True,
):
    """Insere recorte proporcional da imagem sem distorcer a regiao visivel."""
    if not img_path.exists():
        raise FileNotFoundError(f"Imagem nao encontrada: {img_path}")
    with Image.open(img_path) as im:
        iw, ih = im.size
    vis_w = iw * max(1e-6, 1.0 - crop_left - crop_right)
    vis_h = ih * max(1e-6, 1.0 - crop_top - crop_bottom)
    vis_ratio = vis_w / vis_h
    box_ratio = max_w / max_h
    if vis_ratio >= box_ratio:
        w = max_w
        h = max_w / vis_ratio
    else:
        h = max_h
        w = max_h * vis_ratio
    px = x + (max_w - w) / 2.0
    py = y + ((max_h - h) / 2.0 if center_v else 0.0)
    pic = slide.shapes.add_picture(str(img_path), Inches(px), Inches(py), Inches(w), Inches(h))
    if crop_left:
        pic.crop_left = crop_left
    if crop_right:
        pic.crop_right = crop_right
    if crop_top:
        pic.crop_top = crop_top
    if crop_bottom:
        pic.crop_bottom = crop_bottom
    return pic


def add_card(
    slide,
    x,
    y,
    w,
    h,
    title,
    items=None,
    body_text="",
    alert=False,
    font_size=18,
    title_size=19,
    space_after=5,
    line_spacing=1.08,
):
    header_color = SENAC_ORANGE if alert else SENAC_BLUE
    body_color = SENAC_ORANGE_LIGHT if alert else SENAC_BLUE_LIGHT
    header_h = 0.48

    body = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    body.adjustments[0] = 0.035
    body.fill.solid()
    body.fill.fore_color.rgb = body_color
    body.line.color.rgb = header_color
    body.line.width = Pt(1.0)

    hdr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(header_h))
    hdr.fill.solid()
    hdr.fill.fore_color.rgb = header_color
    hdr.line.fill.background()
    htf = hdr.text_frame
    htf.word_wrap = True
    htf.vertical_anchor = MSO_ANCHOR.MIDDLE
    htf.margin_left = Inches(0.12)
    htf.margin_right = Inches(0.10)
    hp = htf.paragraphs[0]
    hr = hp.add_run()
    hr.text = title
    hr.font.name = FONT_NAME
    hr.font.size = fpt(title_size)
    hr.font.bold = True
    hr.font.color.rgb = WHITE

    tb = slide.shapes.add_textbox(
        Inches(x + 0.12),
        Inches(y + header_h + 0.06),
        Inches(w - 0.24),
        Inches(h - header_h - 0.10),
    )
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    if items is not None:
        add_rich_paragraphs(tf, items, font_size=font_size, space_after=space_after, bullet=True, line_spacing=line_spacing)
    elif body_text:
        if isinstance(body_text, list):
            add_rich_paragraphs(tf, body_text, font_size=font_size, space_after=space_after, bullet=False, line_spacing=line_spacing)
        else:
            p = tf.paragraphs[0]
            p.line_spacing = line_spacing
            r = p.add_run()
            r.text = body_text
            r.font.name = FONT_NAME
            r.font.size = fpt(font_size)
            r.font.color.rgb = TEXT_DARK
    return tb


def add_styled_table(
    slide,
    x,
    y,
    w,
    h,
    headers,
    rows,
    col_widths=None,
    alignments=None,
    font_size=18,
    header_font_size=18,
    bold_rows=None,
):
    bold_rows = bold_rows or set()
    n_rows = len(rows) + 1
    n_cols = len(headers)
    shape = slide.shapes.add_table(n_rows, n_cols, Inches(x), Inches(y), Inches(w), Inches(h))
    table = shape.table

    if col_widths:
        for j, cw in enumerate(col_widths):
            table.columns[j].width = Inches(cw)

    for j, head in enumerate(headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = SENAC_BLUE
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        set_cell_margins(cell, 0.06, 0.06, 0.02, 0.02)
        set_cell_border(cell, "003366", 0.5)
        p = cell.text_frame.paragraphs[0]
        p.alignment = alignments[j] if alignments else PP_ALIGN.LEFT
        r = p.add_run()
        r.text = head
        r.font.name = FONT_NAME
        r.font.size = fpt(header_font_size)
        r.font.bold = True
        r.font.color.rgb = WHITE

    for i, row in enumerate(rows):
        bg = SENAC_BLUE_ALT if i % 2 == 1 else WHITE
        if i in bold_rows:
            bg = SENAC_BLUE_LIGHT
        for j, val in enumerate(row):
            cell = table.cell(i + 1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            set_cell_margins(cell, 0.06, 0.06, 0.02, 0.02)
            set_cell_border(cell, "CFD9E6", 0.5)
            p = cell.text_frame.paragraphs[0]
            p.alignment = alignments[j] if alignments else PP_ALIGN.LEFT
            r = p.add_run()
            r.text = str(val)
            r.font.name = FONT_NAME
            r.font.size = fpt(font_size)
            r.font.bold = (i in bold_rows) or (j == 0 and i in bold_rows)
            r.font.color.rgb = SENAC_BLUE if i in bold_rows else TEXT_DARK
    return table


def add_chrome(slide, title_text, slide_label, fonte_text=None, fonte_two_lines=False):
    # Barra de título azul
    hdr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_W, Inches(0.76))
    hdr.fill.solid()
    hdr.fill.fore_color.rgb = SENAC_BLUE
    hdr.line.fill.background()
    tf = hdr.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.42)
    tf.margin_right = Inches(1.40)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = title_text
    r.font.name = FONT_NAME
    r.font.size = fpt(22 if len(title_text) > 54 else 24)
    r.font.bold = True
    r.font.color.rgb = WHITE

    # Chip branco com logo SENAC
    chip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(12.16), Inches(0.08), Inches(0.95), Inches(0.60))
    chip.adjustments[0] = 0.12
    chip.fill.solid()
    chip.fill.fore_color.rgb = WHITE
    chip.line.fill.background()
    if LOGO_PATH.exists():
        add_picture_fit(slide, LOGO_PATH, 12.22, 0.12, 0.83, 0.52)

    # Rodapé (>= 18 pt em todos os campos)
    footer_y = 7.12
    footer_h = 0.38
    f1 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(footer_y), Inches(2.90), Inches(footer_h))
    f1.fill.solid()
    f1.fill.fore_color.rgb = SENAC_BLUE
    f1.line.fill.background()
    p1 = f1.text_frame.paragraphs[0]
    f1.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    f1.text_frame.margin_left = Inches(0.25)
    r1 = p1.add_run()
    r1.text = "M. S. Duda"
    r1.font.name = FONT_NAME
    r1.font.size = fpt(18)
    r1.font.color.rgb = WHITE

    f2 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(2.90), Inches(footer_y), Inches(8.30), Inches(footer_h))
    f2.fill.solid()
    f2.fill.fore_color.rgb = SENAC_BLUE_MID
    f2.line.fill.background()
    p2 = f2.text_frame.paragraphs[0]
    p2.alignment = PP_ALIGN.CENTER
    f2.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    r2 = p2.add_run()
    r2.text = "CNNs clássicas vs. híbridas quântico-clássicas"
    r2.font.name = FONT_NAME
    r2.font.size = fpt(18)
    r2.font.color.rgb = WHITE

    f3 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(11.20), Inches(footer_y), Inches(2.133), Inches(footer_h))
    f3.fill.solid()
    f3.fill.fore_color.rgb = SENAC_BLUE_MID
    f3.line.fill.background()
    p3 = f3.text_frame.paragraphs[0]
    p3.alignment = PP_ALIGN.RIGHT
    f3.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    f3.text_frame.margin_right = Inches(0.25)
    r3 = p3.add_run()
    r3.text = slide_label
    r3.font.name = FONT_NAME
    r3.font.size = fpt(18)
    r3.font.color.rgb = WHITE

    if fonte_text:
        full_src = f"Fonte: {fonte_text}"
        is_two = fonte_two_lines or len(full_src) > 96
        fy = 6.46 if is_two else 6.72
        fh = 0.62 if is_two else 0.36
        add_textbox(
            slide,
            0.42,
            fy,
            12.49,
            fh,
            text=full_src,
            font_size=18,
            color=TEXT_MUTED,
            valign=MSO_ANCHOR.BOTTOM,
            line_spacing=1.02,
        )


def new_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def build_deck() -> None:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    MAIN_TOTAL = 56
    main_idx = 1

    def next_lbl() -> str:
        nonlocal main_idx
        main_idx += 1
        return f"{main_idx}/{MAIN_TOTAL}"

    # ===============================================================
    # 1. CAPA
    # ===============================================================
    s = new_slide(prs)
    top_bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_W, Inches(0.14))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = SENAC_BLUE
    top_bar.line.fill.background()

    if LOGO_PATH.exists():
        add_picture_fit(s, LOGO_PATH, 5.4, 0.38, 2.5, 1.60)

    add_textbox(
        s,
        0.75,
        2.15,
        11.83,
        1.55,
        "Classificação de imagens em múltiplos conjuntos de referência\nde visão computacional: CNNs clássicas vs.\narquiteturas híbridas quântico-clássicas",
        font_size=28,
        bold=True,
        color=SENAC_BLUE,
        align=PP_ALIGN.CENTER,
        line_spacing=1.12,
    )
    add_textbox(
        s,
        1.5,
        3.92,
        10.33,
        0.50,
        "Apresentação final — TCC2",
        font_size=22,
        color=SENAC_ORANGE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_textbox(
        s,
        1.5,
        4.55,
        10.33,
        0.50,
        "Matheus Sanchez Duda",
        font_size=22,
        bold=True,
        color=TEXT_DARK,
        align=PP_ALIGN.CENTER,
    )
    add_textbox(
        s,
        0.65,
        5.12,
        12.03,
        1.35,
        "SENAC — Unidade Santo Amaro | Bacharelado em Ciência da Computação\nOrientador: Prof. Samuel Mendes Sanches Junior\nCoorientador: Prof. Thyago Conchado Quintas",
        font_size=18,
        color=TEXT_MUTED,
        align=PP_ALIGN.CENTER,
        line_spacing=1.15,
    )
    add_textbox(s, 1.5, 6.68, 10.33, 0.42, "São Paulo, 2026", font_size=18, color=TEXT_MUTED, align=PP_ALIGN.CENTER)

    # ===============================================================
    # 2. ROTEIRO
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Roteiro da apresentação", next_lbl())
    agenda = [
        ("1. Introdução", "Contexto, problema na literatura de QML, objetivos e hipótese"),
        ("2. Fundamentação", "Imagens, Macro-F1, CNNs, qubits, VQAs e HQNN-Parallel (Senokosov et al.)"),
        ("3. Trabalhos correlatos", "Funil bibliográfico, estudos clássicos e híbridos nas 9 bases e lacuna"),
        ("4. Desenvolvimento", "Pipeline, 9 bases, all_raw, 7 diagramas arquiteturais e 2 ambientes"),
        ("5. Resultados", "72 modelos, controle Dense20, oclusão 8×8, tempos e telemetria M4"),
        ("6. Conclusão e apoio", "Síntese integrada, contribuições, limitações e slides de apoio"),
    ]
    for i, (t, d) in enumerate(agenda):
        row_y = 1.00 + i * 0.96
        badge = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.55), Inches(row_y), Inches(3.85), Inches(0.76))
        badge.adjustments[0] = 0.12
        badge.fill.solid()
        badge.fill.fore_color.rgb = SENAC_BLUE
        badge.line.fill.background()
        btf = badge.text_frame
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        btf.margin_left = Inches(0.18)
        bp = btf.paragraphs[0]
        br = bp.add_run()
        br.text = t
        br.font.name = FONT_NAME
        br.font.size = fpt(19)
        br.font.bold = True
        br.font.color.rgb = WHITE

        desc_box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.58), Inches(row_y), Inches(8.20), Inches(0.76))
        desc_box.adjustments[0] = 0.12
        desc_box.fill.solid()
        desc_box.fill.fore_color.rgb = SENAC_BLUE_LIGHT
        desc_box.line.color.rgb = BORDER_GRAY
        dtf = desc_box.text_frame
        dtf.word_wrap = True
        dtf.vertical_anchor = MSO_ANCHOR.MIDDLE
        dtf.margin_left = Inches(0.18)
        dtf.margin_right = Inches(0.14)
        dp = dtf.paragraphs[0]
        dr = dp.add_run()
        dr.text = d
        dr.font.name = FONT_NAME
        dr.font.size = fpt(18)
        dr.font.color.rgb = TEXT_DARK

    # ===============================================================
    # 3. CONTEXTO
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Contexto", next_lbl())
    add_card(
        s, 0.45, 1.05, 3.98, 4.45,
        "Visão computacional",
        body_text="Classificação de imagens sustenta leitura de documentos, inspeção industrial, sinalização viária e reconhecimento facial.",
        font_size=19, title_size=20, line_spacing=1.14,
    )
    add_card(
        s, 4.68, 1.05, 3.98, 4.45,
        "CNNs clássicas",
        body_text="Extraem atributos espaciais hierárquicos direto dos pixels, mas desempenho e custo dependem de arquitetura, lote e hardware.",
        font_size=19, title_size=20, line_spacing=1.14,
    )
    add_card(
        s, 8.91, 1.05, 3.98, 4.45,
        "QML na era NISQ",
        body_text="Circuitos quânticos parametrizados (PQCs) acoplados a CNNs prometem expressividade, mas enfrentam custos de simulação e escala.",
        font_size=19, title_size=20, line_spacing=1.14,
    )
    add_textbox(
        s, 0.60, 5.85, 12.13, 0.85,
        "Como CNNs clássicas e cabeças híbridas se comparam em nove domínios visuais?",
        font_size=22, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER,
    )

    # ===============================================================
    # 4. PROBLEMA E JUSTIFICATIVA
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Problema e justificativa", next_lbl())
    add_card(
        s, 0.45, 1.02, 6.05, 5.75,
        "O problema na literatura de QML",
        items=[
            "Experimentos em recortes simples: MNIST binário (3 vs. 5), 4 classes ou grades sintéticas",
            "Avaliação quase restrita à acurácia global (omissão do Macro-F1)",
            "Variáveis de confusão: lotes assimétricos e falta de controle clássico de gargalo",
            "Baixa reprodutibilidade de sementes, partições e custos reais",
        ],
        font_size=18, title_size=20, space_after=10,
    )
    add_card(
        s, 6.83, 1.02, 6.05, 5.75,
        "Por que este estudo importa",
        items=[
            [("Tecnológica: ", True, False, SENAC_ORANGE), ("equilíbrio real entre Macro-F1, tempo, hardware e energia", False, False, TEXT_DARK)],
            [("Acadêmica: ", True, False, SENAC_ORANGE), ("validar o circuito paralelo de Senokosov et al. (2024) sob condições idênticas", False, False, TEXT_DARK)],
            [("Metodológica: ", True, False, SENAC_ORANGE), ("campanha auditável de 72 modelos com controle Dense20 e telemetria", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=20, space_after=14,
    )

    # ===============================================================
    # 5. OBJETIVOS
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Objetivos", next_lbl())
    add_card(
        s, 0.45, 0.96, 12.43, 1.85,
        "Objetivo geral",
        body_text=[
            [
                ("Comparar desempenho preditivo, estabilidade, calibração, explicabilidade e custo de ", False, False, TEXT_DARK),
                ("CNNs clássicas", True, False, SENAC_BLUE),
                (", controles ", False, False, TEXT_DARK),
                ("Dense20", True, False, SENAC_BLUE),
                (" e cabeças híbridas ", False, False, TEXT_DARK),
                ("4×5 qubits", True, False, SENAC_BLUE),
                (" em ", False, False, TEXT_DARK),
                ("nove conjuntos de dados", True, False, SENAC_BLUE),
                (" de visão computacional.", False, False, TEXT_DARK),
            ]
        ],
        font_size=19, title_size=20,
    )
    add_card(
        s, 0.45, 3.00, 3.98, 3.85,
        "Bases e pipeline",
        items=[
            "Inventariar 9 bases públicas (7 a 47 classes)",
            "Avaliar 4 modos de balanceamento (36 treinos)",
            "Fluxo reprodutível auditado por SHA-256",
        ],
        font_size=18, title_size=19, space_after=8,
    )
    add_card(
        s, 4.68, 3.00, 3.98, 3.85,
        "Arquiteturas",
        items=[
            "CNN separável FP32 e features128 congeladas",
            "Controles Dense20 (imagem e vetorial)",
            "Cabeça híbrida 4×5 qubits (Senokosov et al., 2024)",
        ],
        font_size=18, title_size=19, space_after=8,
    )
    add_card(
        s, 8.91, 3.00, 3.98, 3.85,
        "Auditoria completa",
        items=[
            "Macro-F1, matrizes, Bayes e calibração (ECE)",
            "Grad-CAM vs. oclusão 8×8 e ruído/shots",
            "Telemetria em Linux, Windows e iMac M4",
        ],
        font_size=18, title_size=19, space_after=8,
    )

    # ===============================================================
    # 6. HIPÓTESE E DELIMITAÇÕES
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Hipótese e delimitações", next_lbl())
    add_card(
        s, 0.45, 1.02, 12.43, 2.75,
        "Hipótese científica",
        body_text=[
            [
                ("Uma cabeça híbrida com PQCs simulados alcança ", False, False, TEXT_DARK),
                ("convergência estável e desempenho competitivo", True, False, SENAC_BLUE),
                (", próximo ao controle clássico, sob protocolo padronizado.", False, False, TEXT_DARK),
            ],
            [
                ("Não ", True, True, SENAC_ORANGE),
                ("se pressupõe superioridade quântica irrestrita: o custo de simulação e a complexidade visual condicionam a viabilidade prática.", False, False, TEXT_DARK),
            ],
        ],
        font_size=19, title_size=20, space_after=10,
    )
    add_card(
        s, 0.45, 4.02, 12.43, 2.75,
        "Delimitações do estudo",
        items=[
            "Classificação supervisionada de imagens estáticas 2D em 9 bases públicas",
            [("Circuitos quânticos ", False, False, TEXT_DARK), ("apenas simulados em CPU local", True, False, TEXT_DARK), (" (PennyLane e Qiskit Aer, sem QPU física)", False, False, TEXT_DARK)],
            "Campanha principal de 72 checkpoints em seed=42 (sem inferência inter-sementes)",
        ],
        alert=True, font_size=19, title_size=20, space_after=8,
    )

    # ===============================================================
    # 7. IMAGEM DIGITAL
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Imagem digital como matriz de intensidades", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "imagem_matriz_5x5.png", 1.10, 0.90, 11.13, 3.85)
    tb = add_textbox(s, 0.65, 4.92, 12.03, 1.70)
    add_rich_paragraphs(
        tb.text_frame,
        [
            "Escala de cinza: matriz 2D de intensidades; imagem RGB: tensor com 3 canais de cor",
            "As 9 bases variam de 28×28 a 48×48 pixels (variável no GTSRB), com 1 ou 3 canais",
        ],
        font_size=19, space_after=10,
    )

    # ===============================================================
    # 8. MÉTRICAS
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Métricas: por que o Macro-F1?", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "metricas_classificacao_exemplos.png", 0.30, 0.94, 8.20, 5.55)
    add_card(
        s, 8.65, 0.96, 4.33, 5.50,
        "Avaliação multiclasse",
        items=[
            "Matriz de confusão, decomposição um-contra-todos (TP, FP, FN, TN) e curvas ROC/AUC",
            [("Macro-F1: ", True, False, SENAC_BLUE), ("média não ponderada do F1 entre classes — dá peso igual às minoritárias (SVHN, GTSRB, FER2013)", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=10,
    )

    # ===============================================================
    # 9. CONVOLUÇÃO E POOLING
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "CNN: convolução e pooling", next_lbl(), "adaptado de Zhao e Zhang (2024).")
    add_picture_fit(s, FIG_DIR / "convolutional-pooling.png", 0.30, 0.94, 8.20, 5.55)
    add_card(
        s, 8.65, 0.96, 4.33, 5.50,
        "Extração hierárquica",
        items=[
            "Filtros treináveis percorrem a imagem e detectam padrões espaciais locais",
            "Pooling reduz a resolução espacial progressivamente e preserva atributos discriminativos",
        ],
        font_size=18, title_size=19, space_after=10,
    )

    # ===============================================================
    # 9b. SEPARABLECONV2D UNIFICADA (DEPTHWISE 3×3 + POINTWISE 1×1)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Convolução separável: Depthwise 3×3 + Pointwise 1×1", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, GIF_DIR / "07_sepconv_numerico.gif", 0.25, 0.94, 8.95, 5.45)
    add_card(
        s, 9.32, 0.94, 3.68, 5.55,
        "24 vs. 54 pesos",
        items=[
            [("DW 3×3: ", True, False, SENAC_BLUE), ("filtro espacial por canal em 4×4×2 → Z (2×2×2; 18 pesos)", False, False, TEXT_DARK)],
            [("PW 1×1: ", True, False, SENAC_BLUE), ("3 filtros combinam [Z₀, Z₁] → saída 2×2×3 (6 pesos)", False, False, TEXT_DARK)],
            [("Economia: ", True, False, OK_GREEN), ("24 pesos totais frente a 54 na Conv2D padrão (2,25× menos)", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=8,
    )

    # ===============================================================
    # 10. MAPAS DE CARACTERÍSTICAS (FMAP3)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Mapas de características em entradas 64×64×1", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "fmap_03a_piramide_blocos_fashion_mnist.png", 0.35, 0.88, 4.10, 5.65)
    add_picture_fit(s, FIG_DIR / "fmap_03b_piramide_blocos_fer2013.png", 4.55, 0.88, 4.10, 5.65)
    add_card(
        s, 8.78, 0.96, 4.18, 5.60,
        "Hierarquia de ativações",
        items=[
            [("B1–B2: ", True, False, SENAC_BLUE), ("bordas e contornos locais (bota; olhos e sorriso)", False, False, TEXT_DARK)],
            [("B3–B5: ", True, False, SENAC_BLUE), ("foco crescente na região semântica do objeto", False, False, TEXT_DARK)],
            [("GAP → features128: ", True, False, SENAC_BLUE), ("62/128 canais positivos (Fashion) e 63/128 (FER2013)", False, False, TEXT_DARK)],
            "Mínimo negativo em −0,2785 (curva SiLU)",
        ],
        font_size=18, title_size=19, space_after=6,
    )

    # ===============================================================
    # 11. PIPELINE COMPOSTO DE AUMENTO DE DADOS (aug_01 + aug_02)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Aumento de dados: pipeline composto em 6 etapas", next_lbl(), "Elaborado pelo autor (2026).")
    add_textbox(s, 0.45, 0.84, 12.43, 0.36, "(a) GTSRB (128×128×3 — placa PARE) | RMS = 0,2967", font_size=18, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER)
    add_picture_fit(s, FIG_DIR / "aug_01_pipeline_etapas_gtsrb.png", 0.45, 1.20, 12.43, 2.15)
    add_textbox(s, 0.45, 3.42, 12.43, 0.36, "(b) CIFAR-10 (64×64×3 — navio) | RMS = 0,1084", font_size=18, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER)
    add_picture_fit(s, FIG_DIR / "aug_02_pipeline_etapas_cifar10.png", 0.45, 3.78, 12.43, 2.15)
    add_textbox(
        s, 0.45, 6.00, 12.43, 0.65,
        "Etapas: translação ±5%, zoom [0,96; 1,04], brilho ±0,03, contraste [0,92; 1,08], ruído σ=0,005 e cutout ~8%.",
        font_size=18, color=TEXT_DARK, align=PP_ALIGN.CENTER,
    )

    # ===============================================================
    # 12. PRESERVAÇÃO SEMÂNTICA E flip_lr=False (aug_03)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Preservação semântica e flip_lr=False", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "aug_03_comparacao_flip_lr_semantico.png", 0.42, 0.90, 7.65, 5.65)
    add_card(
        s, 8.25, 0.96, 4.63, 5.60,
        "Por que remover o flip?",
        items=[
            [("Inversão de classe: ", True, False, BAD_RED), ("espelhar altera GTSRB ('vire à esquerda'), MNIST ('3'), EMNIST ('R') e SVHN ('5')", False, False, TEXT_DARK)],
            [("Invariância restrita: ", True, False, OK_GREEN), ("válido só em objetos naturais (ex.: cavalo no CIFAR-10)", False, False, TEXT_DARK)],
            [("Correção: ", True, False, SENAC_BLUE), ("fixado flip_lr=False em src/data_prep/data.py", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=10,
    )

    # ===============================================================
    # 13. QUBITS, SUPERPOSIÇÃO E EMARANHAMENTO (FIGURAS ATUALIZADAS)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Qubits, superposição, emaranhamento e medição",
        next_lbl(),
        "Elaborado pelo autor (2026), com base em Nielsen e Chuang (2010) e IBM Quantum (2026).",
    )
    add_picture_fit(s, FIG_DIR / "fig_261_esfera_bloch.png", 0.55, 0.88, 5.80, 4.10)
    add_picture_fit(s, FIG_DIR / "fig_261_circuito_bell.png", 6.70, 0.88, 6.08, 4.10)
    tb = add_textbox(s, 0.55, 5.08, 12.23, 1.55)
    add_rich_paragraphs(
        tb.text_frame,
        [
            "Qubit na esfera de Bloch: superposição de |0⟩ e |1⟩ manipulada por rotações unitárias",
            "Portas H e CNOT geram emaranhamento (estado de Bell); medição extrai valores esperados reais",
        ],
        font_size=18, space_after=8,
    )

    # ===============================================================
    # 14. CODIFICAÇÃO DE DADOS E LAÇO VQA (FIGURAS ATUALIZADAS)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Codificação de dados e laço variacional (VQA)",
        next_lbl(),
        "Elaborado pelo autor (2026), com base em Schuld, Sweke e Meyer (2021), Pérez-Salinas et al. (2020), Cerezo et al. (2021) e IBM Quantum (2026).",
        fonte_two_lines=True,
    )
    add_picture_fit(s, FIG_DIR / "fig_263_codificacoes_vetoriais.png", 0.50, 0.88, 5.95, 4.00)
    add_picture_fit(s, FIG_DIR / "fig_264_laco_vqa.png", 6.75, 0.88, 6.08, 4.00)
    tb = add_textbox(s, 0.55, 4.98, 12.23, 1.42)
    add_rich_paragraphs(
        tb.text_frame,
        [
            [("Codificação angular: ", True, False, SENAC_BLUE), ("vetor clássico vira ângulos de rotação R_X nos qubits em profundidade O(1)", False, False, TEXT_DARK)],
            [("Laço VQA: ", True, False, SENAC_BLUE), ("ansatz parametrizado atualizado por gradientes (parameter-shift) acoplado ao otimizador clássico", False, False, TEXT_DARK)],
        ],
        font_size=18, space_after=6,
    )

    # ===============================================================
    # 15. SIMULAÇÃO, BARREN PLATEAUS E ESCALABILIDADE (FIGURAS ATUALIZADAS)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Simulação, barren plateaus e escalabilidade",
        next_lbl(),
        "Elaborado pelo autor (2026), com base em McClean et al. (2018), Cerezo et al. (2021), Faj et al. (2023) e Bayraktar et al. (2023).",
        fonte_two_lines=True,
    )
    add_picture_fit(s, FIG_DIR / "fig_265_variancia_gradiente.png", 0.50, 0.88, 5.90, 4.00)
    add_picture_fit(s, FIG_DIR / "fig_266_fluxo_backends_simulacao.png", 6.65, 0.88, 6.18, 4.00)
    tb = add_textbox(s, 0.55, 4.98, 12.23, 1.42)
    add_rich_paragraphs(
        tb.text_frame,
        [
            "Simular 20 qubits em vetor de estado exige 2²⁰ (1.048.576) amplitudes e sofre com barren plateaus",
            [("Decisão arquitetural: ", True, False, SENAC_BLUE), ("decompor em 4 circuitos paralelos de 5 qubits (2⁵ = 32 estados cada)", False, False, TEXT_DARK)],
        ],
        font_size=18, space_after=6,
    )

    # ===============================================================
    # 16. MODELO HÍBRIDO PARALELO DE REFERÊNCIA (SENOKOSOV ET AL., 2024)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Modelo de referência: HQNN-Parallel (Senokosov et al., 2024)",
        next_lbl(),
        "Extraído de Senokosov et al. (2024) (arXiv:2304.09224, Figura 4).",
    )
    add_picture_fit(s, FIG_DIR / "fig_arxiv2304_hqnn_parallel_arquitetura.jpg", 0.50, 0.84, 12.33, 2.55)
    add_card(
        s, 0.50, 3.52, 6.00, 3.12,
        "Circuito preservado (4 × 5 qubits)",
        items=[
            "Codificação R_X + 3 camadas R_Z–R_Y–R_Z com CNOT cíclico",
            "Medição Pauli-Y: 45 pesos/ramo = 180 pesos quânticos",
            "MNIST original: 99,21% (45k pesos) vs. 98,71% CNN (372k)",
        ],
        font_size=18, title_size=19, space_after=6,
    )
    add_card(
        s, 6.75, 3.52, 6.08, 3.12,
        "Adaptações metodológicas neste TCC",
        items=[
            "Extrator padronizado de 5 blocos congelado (features128)",
            "Projeção clássica 128 → 20 comum ao controle Dense20",
            "Execução cruzada: 9 bases, Macro-F1, PennyLane e Qiskit",
        ],
        font_size=18, title_size=19, space_after=6,
    )

    # ===============================================================
    # 17. REVISÃO DA LITERATURA (FUNIL)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Como foi a revisão da literatura", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "fig_funil_pesquisa.png", 0.45, 0.92, 6.75, 5.55)
    add_card(
        s, 7.40, 1.00, 5.48, 5.45,
        "Diretrizes da auditoria bibliográfica",
        items=[
            [("Frente 1: ", True, False, SENAC_BLUE), ("fundamentação teórica e artigos originais das 9 bases", False, False, TEXT_DARK)],
            [("Frente 2: ", True, False, SENAC_BLUE), ("estudos empíricos por base (recorte 2021–2026)", False, False, TEXT_DARK)],
            "Conferência manual na fonte primária: variante, nº de classes, partição e métrica",
            "28 registros verificados (19 clássicos + 9 quânticos/híbridos) em mapeamento preliminar",
        ],
        font_size=18, title_size=19, space_after=10,
    )

    # ===============================================================
    # 18. CORRELATOS CLÁSSICOS (TABELA NATIVA >= 18pt)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Estudos clássicos nas nove bases",
        next_lbl(),
        "Elaborado pelo autor (2026), a partir da auditoria das publicações originais.",
    )
    add_styled_table(
        s, 0.42, 0.88, 12.49, 5.05,
        ["Base", "Estudo e arquitetura", "Acurácia"],
        [
            ["MNIST", "Kabir et al. (2023) — VGG-5 + Spinal FC", "99,69%"],
            ["Fashion-MNIST", "Khanday et al. (2021) — CNN rasa (filtro 3×3)", "92,68%"],
            ["KMNIST", "Kabir et al. (2023) — VGG-5 + Spinal FC", "99,05%"],
            ["EMNIST Balanced", "Kabir et al. (2023) — VGG-5 + Spinal FC (47 cl.)", "90,73%"],
            ["CIFAR-10", "Khanday et al. (2021) — CNN 3×3 (50 épocas)", "73,04%"],
            ["CIFAR-100 Coarse", "Guo et al. (2018) — CNN-RNN (tarefa conjunta)", "88,23%"],
            ["SVHN", "Huang et al. (2017) — DenseNet (c/ conj. extra)", "98,41%"],
            ["GTSRB", "An et al. (2024) — LeNet-5 mod. (Tab. 8: val_acc)", "97,53%"],
            ["FER2013", "Li et al. (2021) — Auto-FERNet (re-rotulagem)", "73,78%"],
        ],
        col_widths=[2.75, 7.99, 1.75],
        alignments=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT],
        font_size=18, header_font_size=18,
    )
    add_textbox(
        s, 0.42, 6.08, 12.49, 0.55,
        "Acurácias dos artigos originais: não equivalem diretamente ao Macro-F1 deste TCC (protocolos distintos).",
        font_size=18, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER,
    )

    # ===============================================================
    # 19. CORRELATOS QUÂNTICOS E HÍBRIDOS (TABELA NATIVA >= 18pt)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Estudos quânticos e híbridos na literatura",
        next_lbl(),
        "Elaborado pelo autor (2026), a partir da auditoria das publicações originais.",
    )
    add_styled_table(
        s, 0.42, 0.90, 12.49, 4.75,
        ["Base", "Recorte e resultado reportado na literatura"],
        [
            ["MNIST", "Binário 3 vs. 5: 98,85% (Long, 2025); 10 cl. NNQE: 93,8% (Riaz, 2023)"],
            ["Fashion-MNIST", "4 classes: 85,9–93,6% vs. 89,7–97,4% CNN (Bokhan, 2022)"],
            ["KMNIST", "Apenas experimento binário confirmado (Dong, 2025)"],
            ["EMNIST", "75,9% com filtro quântico fixo de 4 qubits (Riaz, 2026)"],
            ["CIFAR-10", "NNQE em cinza: 36,0% teste (Riaz, 2023); HQNN: 82,78% (Senokosov, 2024)"],
            ["CIFAR-100 Coarse", "Nenhum estudo quântico/híbrido confirmado nas 20 superclasses"],
            ["GTSRB", "NNQE: 73,4% vs. 82,2% na rede densa clássica (Riaz, 2023)"],
        ],
        col_widths=[2.75, 9.74],
        alignments=[PP_ALIGN.LEFT, PP_ALIGN.LEFT],
        font_size=18, header_font_size=18, bold_rows={5},
    )
    add_textbox(
        s, 0.42, 5.88, 12.49, 0.72,
        "Predominam recortes binários/4 classes e filtros fixos; no GTSRB, NNQE perde em 8,8 p.p. para a rede clássica.",
        font_size=18, bold=True, color=SENAC_ORANGE, align=PP_ALIGN.CENTER,
    )

    # ===============================================================
    # 20. LACUNA DE PESQUISA
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Lacuna de pesquisa", next_lbl())
    tb = add_textbox(s, 0.50, 0.98, 12.33, 3.45)
    add_rich_paragraphs(
        tb.text_frame,
        [
            [("Protocolos fragmentados: ", True, False, SENAC_BLUE), ("poucas classes ou domínios; lacuna aberta nas 20 superclasses do CIFAR-100 Coarse", False, False, TEXT_DARK)],
            [("Omissão do Macro-F1: ", True, False, SENAC_BLUE), ("literatura reporta quase só acurácia global, mascarando minoritárias (GTSRB, FER2013, SVHN)", False, False, TEXT_DARK)],
            [("Variáveis de confusão: ", True, False, SENAC_BLUE), ("lotes assimétricos (ex.: 1 vs. 4) e falta de controle clássico com gargalo de mesma dimensão", False, False, TEXT_DARK)],
        ],
        font_size=19, space_after=12, bullet=False, numbered=True,
    )
    add_card(
        s, 0.50, 4.55, 12.33, 2.25,
        "Contribuição proposta",
        body_text="Campanha padronizada nas 9 bases completas (72 modelos), avaliada por Macro-F1 com controle vetorial Dense20, calibração, oclusão 8×8 e telemetria multiplataforma.",
        font_size=19, title_size=20,
    )

    # ===============================================================
    # 21. TIPO DE PESQUISA E PERGUNTA
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Tipo de pesquisa e pergunta norteadora", next_lbl())
    tb = add_textbox(s, 0.55, 1.05, 12.23, 2.45)
    add_rich_paragraphs(
        tb.text_frame,
        [
            [("Natureza aplicada", True, False, SENAC_BLUE), (", abordagem ", False, False, TEXT_DARK), ("quantitativa", True, False, SENAC_BLUE), (" e protocolo estritamente auditável", False, False, TEXT_DARK)],
            [("Objetivos ", False, False, TEXT_DARK), ("exploratórios", True, False, TEXT_DARK), (" (CIFAR-100 Coarse e EMNIST), ", False, False, TEXT_DARK), ("descritivos", True, False, TEXT_DARK), (" (72 modelos + 36 balanceamento + 27 telemetria M4) e ", False, False, TEXT_DARK), ("comparativos", True, False, TEXT_DARK)],
        ],
        font_size=19, space_after=14,
    )
    add_card(
        s, 0.55, 3.70, 12.23, 2.95,
        "Pergunta de pesquisa",
        body_text="Em que medida uma representação convolucional congelada (features128) sustenta cabeças reduzidas nas nove bases, e como a cabeça híbrida (4 × 5 qubits) se compara em Macro-F1, calibração, explicabilidade e custo frente à CNN original e ao controle Dense20?",
        font_size=19, title_size=20, line_spacing=1.18,
    )

    # ===============================================================
    # 22. PIPELINE EXPERIMENTAL EM SEIS ETAPAS
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Pipeline experimental em seis etapas", next_lbl(), "Elaborado pelo autor (2026).")
    stages = [
        ("1. Inventário e dados", "9 bases 70/15/15\nHashes SHA-256"),
        ("2. Extrator FP32", "CNN 64×64 (128×128)\nExporta features128"),
        ("3. Cabeças Dense20", "D20 imagem e vetorial\n(Linux e macOS)"),
        ("4. Híbrido 4×5 qubits", "36 treinos em CPU\nWin/Mac × PL/Qiskit"),
        ("5. Auditoria completa", "Macro-F1, Bayes, ECE\nGrad-CAM e oclusão"),
        ("6. Telemetria", "Tempos lote 128, CPU\nRSS, GPU, I/O e macmon"),
    ]
    box_w, box_h = 3.70, 1.95
    xs = [0.50, 4.82, 9.14]
    ys = [1.18, 4.02]
    for idx, (st_t, st_d) in enumerate(stages):
        r_idx, c_idx = divmod(idx, 3)
        bx, by = xs[c_idx], ys[r_idx]
        box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(bx), Inches(by), Inches(box_w), Inches(box_h))
        box.adjustments[0] = 0.08
        box.fill.solid()
        box.fill.fore_color.rgb = SENAC_BLUE_LIGHT
        box.line.color.rgb = SENAC_BLUE
        box.line.width = Pt(1.5)
        btf = box.text_frame
        btf.word_wrap = True
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p0 = btf.paragraphs[0]
        p0.alignment = PP_ALIGN.CENTER
        p0.space_after = Pt(6)
        r0 = p0.add_run()
        r0.text = st_t
        r0.font.name = FONT_NAME
        r0.font.size = fpt(19)
        r0.font.bold = True
        r0.font.color.rgb = SENAC_BLUE
        for ln_d in st_d.split("\n"):
            p1 = btf.add_paragraph()
            p1.alignment = PP_ALIGN.CENTER
            r1 = p1.add_run()
            r1.text = ln_d
            r1.font.name = FONT_NAME
            r1.font.size = fpt(18)
            r1.font.color.rgb = TEXT_DARK

    for row_y in [ys[0] + box_h / 2, ys[1] + box_h / 2]:
        for c in range(2):
            arr = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(xs[c] + box_w + 0.08), Inches(row_y - 0.14), Inches(0.46), Inches(0.28))
            arr.fill.solid()
            arr.fill.fore_color.rgb = SENAC_ORANGE
            arr.line.fill.background()

    c3_x = xs[2] + box_w / 2.0
    c4_x = xs[0] + box_w / 2.0
    mid_y = (ys[0] + box_h + ys[1]) / 2.0
    stem1 = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(c3_x - 0.03), Inches(ys[0] + box_h + 0.04), Inches(0.06), Inches(mid_y - (ys[0] + box_h + 0.04)))
    hbar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(c4_x - 0.03), Inches(mid_y - 0.03), Inches(c3_x - c4_x + 0.06), Inches(0.06))
    for seg in (stem1, hbar):
        seg.fill.solid()
        seg.fill.fore_color.rgb = SENAC_ORANGE
        seg.line.fill.background()
    down_arr = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(c4_x - 0.14), Inches(mid_y), Inches(0.28), Inches(ys[1] - mid_y - 0.06))
    down_arr.fill.solid()
    down_arr.fill.fore_color.rgb = SENAC_ORANGE
    down_arr.line.fill.background()

    # ===============================================================
    # 23. AS NOVE BASES DE DADOS (TABELA NATIVA >= 18pt)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "As nove bases de dados", next_lbl(), "Elaborado pelo autor (2026).")
    add_styled_table(
        s, 0.42, 0.88, 12.49, 5.05,
        ["Base", "Domínio", "Entrada", "K", "Treino / Val. / Teste"],
        [
            ["MNIST", "Dígitos manuscritos", "28×28, cinza", "10", "48.999 / 10.503 / 10.498"],
            ["Fashion-MNIST", "Vestuário", "28×28, cinza", "10", "49.000 / 10.500 / 10.500"],
            ["KMNIST", "Caracteres Kuzushiji", "28×28, cinza", "10", "49.000 / 10.500 / 10.500"],
            ["EMNIST Balanced", "Alfanumérico", "28×28, cinza", "47", "92.120 / 19.740 / 19.740"],
            ["CIFAR-10", "Objetos e animais", "32×32, RGB", "10", "42.000 / 9.000 / 9.000"],
            ["CIFAR-100 Coarse", "Superclasses", "32×32, RGB", "20", "42.000 / 9.000 / 9.000"],
            ["SVHN", "Dígitos de fachadas", "32×32, RGB", "10", "69.502 / 14.894 / 14.893"],
            ["GTSRB", "Placas de trânsito", "Variável, RGB", "43", "27.489 / 5.905 / 5.876"],
            ["FER2013", "Expressões faciais", "48×48, cinza", "7", "25.121 / 5.384 / 5.382"],
        ],
        col_widths=[2.65, 2.85, 2.15, 0.80, 4.04],
        alignments=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT],
        font_size=18, header_font_size=18,
    )
    add_textbox(
        s, 0.42, 6.08, 12.49, 0.55,
        "Partições estratificadas fixas (70/15/15) compartilhadas pelos 8 modelos em cada base.",
        font_size=18, color=TEXT_MUTED, align=PP_ALIGN.CENTER,
    )

    # ===============================================================
    # 24. EQUILÍBRIO DE CLASSES
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Equilíbrio de classes: três regimes", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_crop_fit(
        s, FIG_DIR / "equilibrio_classes_9_datasets.png",
        0.30, 0.90, 6.28, 5.68, crop_bottom=0.401, center_v=True,
    )
    add_picture_crop_fit(
        s, FIG_DIR / "equilibrio_classes_9_datasets.png",
        6.72, 0.88, 6.26, 3.12, crop_top=0.599, center_v=False,
    )
    add_card(
        s, 6.72, 4.04, 6.26, 2.60,
        "Regimes (IR = n_max / n_min)",
        items=[
            [("IR = 1,00× (CV = 0%): ", True, False, SENAC_BLUE), ("Fashion, KMNIST, EMNIST, CIFAR-10 e CIFAR-100 Coarse", False, False, TEXT_DARK)],
            [("IR = 1,25×: ", True, False, SENAC_BLUE), ("MNIST (assimetria branda)", False, False, TEXT_DARK)],
            [("IR = 3,03× a 16,43×: ", True, False, BAD_RED), ("SVHN (3,03×), GTSRB (10,71×) e FER2013 (16,43×; 547 desgosto)", False, False, TEXT_DARK)],
            "Validação e teste mantêm distribuição natural",
        ],
        font_size=18, title_size=19, space_after=2, line_spacing=1.02,
    )

    # ===============================================================
    # 25. MODOS DE BALANCEAMENTO: GRÁFICOS (ATUALIZADO)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Modos de balanceamento: Macro-F1 e tempo (36 execuções)", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "fig_balanceamento_macro_f1.png", 0.42, 0.96, 6.75, 4.95)
    add_picture_fit(s, FIG_DIR / "fig_342_balanceamento_tempo_treino.png", 7.35, 0.96, 5.55, 4.95)
    add_textbox(
        s, 0.42, 6.02, 12.49, 0.62,
        "Triagem preliminar na CNN original (mixed_float16, lote 512, 2.486 épocas, 88,86 h acumuladas).",
        font_size=18, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER,
    )

    # ===============================================================
    # 26. JUSTIFICATIVA OBJETIVA DE all_raw
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Por que adotar a distribuição natural (all_raw)?", next_lbl(), "Elaborado pelo autor (2026).")
    add_styled_table(
        s, 0.45, 0.92, 12.43, 2.25,
        ["Modo", "Média Macro-F1", "Mediana", "Δ vs. all_raw", "Tempo total"],
        [
            ["all_raw", "82,464%", "92,010%", "0,000 p.p.", "22,46 h"],
            ["oversample", "82,455%", "91,851%", "−0,009 p.p.", "25,85 h"],
            ["class_weight", "81,646%", "91,467%", "−0,819 p.p.", "24,64 h"],
            ["undersample", "78,469%", "88,057%", "−3,995 p.p.", "15,90 h"],
        ],
        col_widths=[2.50, 2.75, 2.30, 2.58, 2.30],
        alignments=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT],
        font_size=18, header_font_size=18, bold_rows={0},
    )
    add_card(
        s, 0.45, 3.40, 12.43, 3.22,
        "Conclusão da triagem de 36 execuções",
        items=[
            [("all_raw: ", True, False, OK_GREEN), ("maior média e maior mediana sem distorcer frequências empíricas nem custos quânticos", False, False, TEXT_DARK)],
            [("undersample: ", True, False, BAD_RED), ("colapso severo em FER2013 (−19,28 p.p.) e GTSRB (−13,69 p.p.)", False, False, TEXT_DARK)],
            [("class_weight: ", True, False, BAD_RED), ("−6,12 p.p. no FER2013; idêntico a all_raw nas 5 bases equilibradas", False, False, TEXT_DARK)],
            [("oversample: ", True, False, SENAC_ORANGE), ("+15,1% de tempo (GTSRB 9,90 h vs. 5,20 h) e −1,26 p.p. no CIFAR-10", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=5,
    )

    # ===============================================================
    # 27. PRÉ-PROCESSAMENTO E AUDITORIA DE INTEGRIDADE
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Pré-processamento e auditoria de integridade", next_lbl())
    add_card(
        s, 0.45, 1.02, 6.05, 5.75,
        "Padronização idêntica",
        items=[
            "Tensores em ponto flutuante, normalização por canal e política all_raw",
            "Redimensionamento proporcional (resize_with_pad) para 64×64 (128×128 no GTSRB)",
            "Partição estratificada fixa (70/15/15) compartilhada pelos 8 modelos de cada base",
            "Rastreabilidade por hashes SHA-256 e impressões digitais das partições",
        ],
        font_size=18, title_size=20, space_after=10,
    )
    add_card(
        s, 6.83, 1.02, 6.05, 5.75,
        "Limitações auditadas nos dados",
        items=[
            [("GTSRB: ", True, False, BAD_RED), ("3.990 de 5.876 imagens de teste (67,9%) compartilham tracks físicos com o treino", False, False, TEXT_DARK)],
            [("FER2013: ", True, False, BAD_RED), ("378 duplicatas exatas no teste (7,02%), 403 na validação e 57 conflitos de rótulo", False, False, TEXT_DARK)],
            "EMNIST (1) e CIFAR-100 Coarse (7): cópias pontuais; 5 bases restantes livres de duplicatas",
        ],
        alert=True, font_size=18, title_size=20, space_after=12,
    )

    # ===============================================================
    # 28. TRÊS FAMÍLIAS DE MODELOS
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Três famílias de modelos comparadas", next_lbl())
    add_card(
        s, 0.45, 1.00, 3.98, 4.95,
        "CNN original (FP32)",
        body_text=[
            "5 blocos SeparableConv2D (32→48→64→96→128), GroupNorm(16), SiLU e MaxPool.",
            "Cabeça GAP+GMP → 256 → 256 → K.",
            [("Extrator: ", True, False, SENAC_BLUE), ("66.905 (C=1) ou 67.019 (C=3) pesos.", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=8,
    )
    add_card(
        s, 4.68, 1.00, 3.98, 4.95,
        "Dense20 (controle)",
        body_text=[
            "Extrator congelado (features128): D20 imagem (LayerNorm + ReLU) e Dense20 vetorial (128→20 tanh→K).",
            [("Função: ", True, False, SENAC_BLUE), ("isolar o efeito da compressão para o gargalo de 20 dimensões.", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=8,
    )
    add_card(
        s, 8.91, 1.00, 3.98, 4.95,
        "Híbrido 4×5 qubits",
        body_text=[
            "Mesma projeção 128 → 20 sobre features128; troca apenas tanh por 4 PQCs de 5 qubits.",
            "Simulação exata em CPU: PennyLane e Qiskit Aer (Windows e Mac).",
        ],
        font_size=18, title_size=19, space_after=8,
    )
    add_textbox(
        s, 0.45, 6.20, 12.43, 0.55,
        "Campanha principal auditada: 72 checkpoints = 9 bases × 8 configurações",
        font_size=20, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER,
    )

    # ===============================================================
    # 29. ETAPA 1: CNN CLÁSSICA DE ORIGEM (FIGURA NOVA DO TCC)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Etapa 1: CNN clássica de origem (FP32)", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "fig_arq_etapa1_cnn_original.png", 0.42, 0.92, 12.49, 4.35)
    tb = add_textbox(s, 0.55, 5.38, 12.23, 1.25)
    add_rich_paragraphs(
        tb.text_frame,
        [
            "Treinada do zero em Linux (FP32, aumento de 50%, label smoothing 0,05); 201.059 pesos (C=1, K=10)",
            "Congelada em block5_pool + GAP para exportar features128 determinísticas (.npy) em ~3 min nas 9 bases",
        ],
        font_size=18, space_after=6,
    )

    # ===============================================================
    # 29b. ANATOMIA INTERNA DE UM BLOCO CNN (BLOCO B3)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Anatomia interna de um bloco CNN (Bloco B3)", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, GIF_DIR / "05_zoom_bloco_cnn.gif", 0.25, 0.94, 8.95, 5.45)
    add_card(
        s, 9.32, 0.94, 3.68, 5.55,
        "Estrutura do bloco",
        items=[
            [("Ordem: ", True, False, SENAC_BLUE), ("SepConv 5×5 + GroupNorm(16) + SiLU + SepConv 3×3 + MaxPool 2×2", False, False, TEXT_DARK)],
            [("Bloco B3: ", True, False, SENAC_BLUE), ("8×8×48 → 4×4×64 com 9.200 pesos e 572.416 MACs", False, False, TEXT_DARK)],
            "GroupNorm independe do tamanho de lote (estável em lote 128 e 512)",
        ],
        font_size=18, title_size=19, space_after=8,
    )

    # ===============================================================
    # 30a. ETAPA 2A: CABEÇA Dense20 SOBRE IMAGENS
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Etapa 2A: cabeça Dense20 sobre imagens", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, GIF_DIR / "02_fluxo_dense20_imagem.gif", 0.25, 0.94, 8.95, 5.45)
    add_card(
        s, 9.32, 0.94, 3.68, 5.55,
        "Backbone congelado",
        items=[
            "5 blocos convolucionais congelados + aumento de 50% (Linux)",
            [("Gargalo: ", True, False, SENAC_BLUE), ("GAP(128) → Dense(20) + LayerNorm + ReLU → Dense(K)", False, False, TEXT_DARK)],
            [("Treináveis: ", True, False, OK_GREEN), ("2.830 pesos (K=10) sobre imagens diretas", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=8,
    )

    # ===============================================================
    # 30b. ETAPA 2B: CABEÇA CLÁSSICA VETORIAL (Dense20)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Etapa 2B: cabeça clássica vetorial (Dense20)", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, GIF_DIR / "03_fluxo_classico_tanh.gif", 0.25, 0.94, 8.95, 5.45)
    add_card(
        s, 9.32, 0.94, 3.68, 5.55,
        "Controle clássico 1:1",
        items=[
            [("Entrada: ", True, False, SENAC_BLUE), ("features128 congelados em .npy (Linux e Mac)", False, False, TEXT_DARK)],
            [("Cabeça: ", True, False, SENAC_BLUE), ("Dense(128, ReLU) → Dense(20) → tanh → Dense(K)", False, False, TEXT_DARK)],
            [("Treináveis: ", True, False, OK_GREEN), ("19.302 pesos (K=10); par direto da etapa quântica", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=8,
    )

    # ===============================================================
    # 31. ETAPA 3: CABEÇA HÍBRIDA 4×5 QUBITS (FIGURA NOVA + CITAÇÃO)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Etapa 3: cabeça híbrida paralela (4 × 5 qubits)",
        next_lbl(),
        "Elaborado pelo autor (2026), com base em Senokosov et al. (2024).",
    )
    add_picture_fit(s, GIF_DIR / "04_fluxo_hibrido_4xpqc.gif", 0.25, 0.94, 8.95, 5.45)
    add_card(
        s, 9.32, 0.94, 3.68, 5.55,
        "Camada ParallelPQC20",
        items=[
            "Mesmas features128 e projeção 128 → 20 da Etapa 2B",
            [("Divisão: ", True, False, SENAC_BLUE), ("vetor u ∈ ℝ²⁰ em 4 ramos disjuntos de 5 qubits", False, False, TEXT_DARK)],
            [("Treináveis: ", True, False, OK_GREEN), ("19.482 pesos (K=10; +180 ângulos) no lugar de tanh", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=8,
    )

    # ===============================================================
    # 32. CIRCUITO QUÂNTICO DE 5 QUBITS (FIGURA NOVA + CITAÇÃO)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Circuito variacional de 5 qubits por ramo",
        next_lbl(),
        "Elaborado pelo autor (2026), reproduzindo Senokosov et al. (2024).",
    )
    add_picture_fit(s, GIF_DIR / "06_zoom_pqc_5qubits.gif", 0.25, 0.94, 8.95, 5.45)
    add_card(
        s, 9.32, 0.94, 3.68, 5.55,
        "Ansatz e gradientes",
        items=[
            "RX(u) + 3×(RZ·RY·RZ + CNOT circular r = 1, 2, 3)",
            [("Medição: ", True, False, SENAC_BLUE), ("Pauli-Y ⟨Y⟩ ∈ [−1, 1] nos 5 qubits (45 ângulos/ramo)", False, False, TEXT_DARK)],
            [("Parameter-shift: ", True, False, BAD_RED), ("404 aval./amostra no treino e 4 na inferência", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=8,
    )

    # ===============================================================
    # 33. COMPARATIVO ESTRUTURAL ENTRE AS ETAPAS (FIGURA NOVA)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Comparativo estrutural: o que mudou entre as etapas", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, GIF_DIR / "08_comparativo_4_etapas.gif", 0.25, 0.94, 8.95, 5.45)
    add_card(
        s, 9.32, 0.94, 3.68, 5.55,
        "Isolamento causal",
        items=[
            "Backbone de 67.019 pesos (3ch) congelado após Etapa 1",
            [("2B → 3: ", True, False, SENAC_BLUE), ("19.302 para 19.482 pesos (muda só a camada 20D)", False, False, TEXT_DARK)],
            [("Troca 1:1: ", True, False, OK_GREEN), ("tanh(u) ↔ 4×5 qubits (+180 ângulos quânticos)", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=8,
    )

    # ===============================================================
    # 34. PROTOCOLO EXPERIMENTAL
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Protocolo experimental e critérios de avaliação", next_lbl())
    add_card(
        s, 0.45, 1.00, 6.08, 5.75,
        "Regime de treinamento (seed=42)",
        items=[
            "72 checkpoints (9 bases × 8 configurações), 100 épocas completas",
            "Otimizador Adam (η = 3×10⁻⁴, cosseno + aquecimento)",
            "Seleção pelo melhor Macro-F1 de validação; teste final em all_raw",
            "Imagens: label smoothing 0,05; features128: entropia cruzada padrão, lote 128",
        ],
        font_size=18, title_size=20, space_after=10,
    )
    add_card(
        s, 6.80, 1.00, 6.08, 1.95,
        "Métrica primária",
        body_text="Macro-F1 de teste (%) e Δ pareado em pontos percentuais (p.p.).",
        font_size=19, title_size=20,
    )
    add_card(
        s, 6.80, 3.18, 6.08, 3.57,
        "Critérios de auditoria",
        items=[
            "Convergência estável acima do acaso (1/K)",
            "1.336 posteriores bayesianas (Jeffreys) e calibração (ECE, NLL, Brier)",
            "576 Grad-CAM, 73.728 oclusões 8×8, gradientes, ruído/shots e telemetria",
        ],
        font_size=18, title_size=20, space_after=8,
    )

    # ===============================================================
    # 35. DOIS AMBIENTES COMPUTACIONAIS (TABELA COMPARATIVA >= 18pt)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Dois ambientes computacionais e versões auditadas", next_lbl(), "Elaborado pelo autor (2026).")
    add_styled_table(
        s, 0.42, 0.92, 12.49, 5.55,
        ["Componente", "Ambiente 1: Win / WSL2", "Ambiente 2: iMac M4"],
        [
            ["SO / Arq.", "Ubuntu 22.04.5 (WSL2) + Win nativo (x86-64)", "macOS 15.5 (ARM64, Metal)"],
            ["CPU", "Intel Core i7-14700K (28 lógicos)", "Apple Silicon M4 (P/E-cores)"],
            ["Memória", "≈ 15 GiB (WSL) + 4 GiB swap", "16 GB de memória unificada"],
            ["GPU", "NVIDIA RTX A2000 12GB (CUDA 13.2)", "GPU Apple M4 10 núcleos (AGX)"],
            ["Deep Learning", "TensorFlow 2.21.0; Keras 3.12.4", "TF 2.18.1; Metal 1.2; PyTorch 2.8.0"],
            ["Simulação / Tel.", "PennyLane & Qiskit Aer (Win); psutil, NVML", "PennyLane 0.44.1; Qiskit 2.3.0; Aer 0.17.2; macmon"],
        ],
        col_widths=[2.35, 5.07, 5.07],
        alignments=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.LEFT],
        font_size=18, header_font_size=18,
    )

    # ===============================================================
    # 36. TABELA MACRO-F1 (NATIVA >= 18pt)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Macro-F1 de teste (%) nas nove bases", next_lbl(), "Elaborado pelo autor (2026).")
    add_styled_table(
        s, 0.42, 0.88, 12.49, 5.05,
        ["Base", "CNN orig.", "Dense20", "Híbrido", "Δ Híb−CNN", "Δ Híb−D20"],
        [
            ["MNIST", "98,984", "99,225", "99,305", "+0,321", "+0,080"],
            ["Fashion-MNIST", "91,915", "92,050", "91,894", "−0,021", "−0,156"],
            ["KMNIST", "98,649", "98,648", "98,648", "−0,001", "0,000"],
            ["EMNIST Balanced", "87,719", "88,642", "88,474", "+0,755", "−0,168"],
            ["CIFAR-10", "73,117", "73,389", "73,320", "+0,203", "−0,069"],
            ["CIFAR-100 Coarse", "47,458", "47,559", "47,117", "−0,341", "−0,442"],
            ["SVHN", "92,088", "92,567", "92,634", "+0,546", "+0,067"],
            ["GTSRB*", "99,365", "99,633", "99,590", "+0,225", "−0,043"],
            ["FER2013", "48,158", "47,899", "48,519", "+0,361", "+0,620"],
        ],
        col_widths=[2.95, 1.80, 1.80, 1.80, 2.07, 2.07],
        alignments=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT],
        font_size=18, header_font_size=18,
    )
    add_textbox(
        s, 0.42, 6.08, 12.49, 0.55,
        "*GTSRB: 67,9% do teste em tracks do treino. Dense20 e Híbrido: Mac/PennyLane (desvio PL vs. QK < 0,05 p.p.).",
        font_size=18, color=TEXT_MUTED, align=PP_ALIGN.CENTER,
    )

    # ===============================================================
    # 37. GRÁFICO DOS DELTAS (GRÁFICO NATIVO >= 18pt)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Quanto o híbrido difere? (Δ em pontos percentuais)", next_lbl(), "Elaborado pelo autor (2026).")
    chart_data = CategoryChartData()
    chart_data.categories = ["MNIST", "F-MN", "KMN", "EMNIST", "CIF10", "C100C", "SVHN", "GTSRB", "FER13"]
    chart_data.add_series("Híbrido − CNN original", (0.321, -0.021, -0.001, 0.755, 0.203, -0.341, 0.546, 0.225, 0.361))
    chart_data.add_series("Híbrido − Dense20", (0.080, -0.156, 0.000, -0.168, -0.069, -0.442, 0.067, -0.043, 0.620))

    ch_shape = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.45), Inches(0.90), Inches(12.43), Inches(5.00), chart_data)
    chart = ch_shape.chart
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.TOP
    chart.legend.include_in_layout = False
    chart.legend.font.name = FONT_NAME
    chart.legend.font.size = fpt(18)
    plot = chart.plots[0]
    plot.gap_width = 110
    plot.overlap = -15
    plot.series[0].invert_if_negative = False
    plot.series[0].format.fill.solid()
    plot.series[0].format.fill.fore_color.rgb = SENAC_BLUE
    plot.series[1].invert_if_negative = False
    plot.series[1].format.fill.solid()
    plot.series[1].format.fill.fore_color.rgb = SENAC_ORANGE
    va = chart.value_axis
    va.minimum_scale = -0.6
    va.maximum_scale = 0.9
    va.major_unit = 0.3
    va.tick_labels.font.name = FONT_NAME
    va.tick_labels.font.size = fpt(18)
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RGBColor(218, 224, 232)
    ca = chart.category_axis
    ca.tick_label_position = XL_TICK_LABEL_POSITION.LOW
    ca.tick_labels.font.name = FONT_NAME
    ca.tick_labels.font.size = fpt(18)

    add_textbox(
        s, 0.45, 6.02, 12.43, 0.60,
        "Frente à CNN: média +0,23 p.p. | Frente ao Dense20: média −0,01 p.p. (16/36 positivos e 20/36 negativos nos pares).",
        font_size=18, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER,
    )

    # ===============================================================
    # 38. PAPEL DO CONTROLE Dense20 E EFICIÊNCIA PARAMÉTRICA
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "O papel do controle Dense20 e eficiência paramétrica", next_lbl())
    add_card(
        s, 0.45, 1.00, 6.05, 3.25,
        "Sem o controle, haveria 'ganhos'",
        body_text="Híbrido − CNN: EMNIST +0,755 p.p., SVHN +0,546 p.p., FER2013 +0,361 p.p., MNIST +0,321 p.p., GTSRB +0,225 p.p.",
        alert=True, font_size=18, title_size=19,
    )
    add_card(
        s, 6.83, 1.00, 6.05, 3.25,
        "Com o controle, o ganho some",
        body_text="Dense20 já explica a maior parte: EMNIST 88,642 (vs. 88,474), CIFAR-10 73,389 (vs. 73,320), GTSRB 99,633 (vs. 99,590), KMNIST 98,648.",
        font_size=18, title_size=19,
    )
    tb = add_textbox(s, 0.50, 4.48, 12.33, 2.35)
    add_rich_paragraphs(
        tb.text_frame,
        [
            [("Gargalo clássico: ", True, False, SENAC_BLUE), ("o ganho frente à CNN vem da regularização em 20 dimensões, não de vantagem quântica", False, False, TEXT_DARK)],
            [("Parâmetros (C=1, K=10): ", True, False, SENAC_BLUE), ("CNN 201,1k → inferência completa usa 69,7k (D20 img), 86,2k (Vet) e 86,4k (Híb) — redução real de 57%–65%, mantendo os 66,9k pesos do extrator", False, False, TEXT_DARK)],
        ],
        font_size=18, space_after=10,
    )

    # ===============================================================
    # 39. COMPLEXIDADE DO DOMÍNIO (GRÁFICO NATIVO >= 18pt)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Complexidade do domínio governa o desempenho", next_lbl(), "Elaborado pelo autor (2026).")
    cd39 = CategoryChartData()
    cd39.categories = ["CIFAR-100C", "FER2013", "CIFAR-10", "EMNIST", "F-MNIST", "SVHN", "KMNIST", "MNIST"]
    cd39.add_series("Macro-F1 do híbrido (%)", (47.1, 48.5, 73.3, 88.5, 91.9, 92.6, 98.6, 99.3))
    ch39 = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.45), Inches(0.88), Inches(12.43), Inches(4.35), cd39).chart
    ch39.has_legend = False
    p39 = ch39.plots[0]
    p39.has_data_labels = True
    p39.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    p39.data_labels.font.name = FONT_NAME
    p39.data_labels.font.size = fpt(18)
    p39.series[0].format.fill.solid()
    p39.series[0].format.fill.fore_color.rgb = SENAC_BLUE
    ch39.value_axis.minimum_scale = 0
    ch39.value_axis.maximum_scale = 115
    ch39.value_axis.major_gridlines.format.line.color.rgb = RGBColor(218, 224, 232)
    ch39.value_axis.tick_labels.font.name = FONT_NAME
    ch39.value_axis.tick_labels.font.size = fpt(18)
    ch39.category_axis.tick_labels.font.name = FONT_NAME
    ch39.category_axis.tick_labels.font.size = fpt(18)

    tb = add_textbox(s, 0.55, 5.32, 12.23, 1.32)
    add_rich_paragraphs(
        tb.text_frame,
        [
            [("Amplitude estreita por base: ", True, False, SENAC_BLUE), ("0,085 p.p. (KMNIST) a 1,124 p.p. (EMNIST) — features128 governam o teto preditivo", False, False, TEXT_DARK)],
            [("Domínios difíceis: ", True, False, SENAC_BLUE), ("CIFAR-100 Coarse (5 classes finas/superclasse) e FER2013 (desgosto com 82 amostras no teste)", False, False, TEXT_DARK)],
        ],
        font_size=18, space_after=5,
    )

    # ===============================================================
    # 40. GTSRB: INTERPRETAÇÃO CAUTELOSA
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "GTSRB: números altos, interpretação cautelosa", next_lbl())
    left_box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.55), Inches(1.25), Inches(4.85), Inches(4.95))
    left_box.adjustments[0] = 0.06
    left_box.fill.solid()
    left_box.fill.fore_color.rgb = SENAC_BLUE_LIGHT
    left_box.line.color.rgb = SENAC_BLUE
    ltf = left_box.text_frame
    ltf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for idx, line in enumerate(["99,365%   CNN", "99,633%   Dense20", "99,590%   Híbrido"]):
        p = ltf.paragraphs[0] if idx == 0 else ltf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.space_after = Pt(22)
        r = p.add_run()
        r.text = line
        r.font.name = FONT_NAME
        r.font.size = fpt(26)
        r.font.bold = True
        r.font.color.rgb = SENAC_BLUE

    add_card(
        s, 5.75, 1.25, 7.05, 2.55,
        "Por que exigir cautela?",
        body_text="3.990 de 5.876 imagens de teste (67,9%) pertencem a tracks físicos já presentes no treino (quadros correlacionados da mesma placa).",
        alert=True, font_size=19, title_size=20,
    )
    add_card(
        s, 5.75, 4.05, 7.05, 2.15,
        "Incerteza bayesiana (classe 0, N = 31)",
        body_text="Mesmo com F1 observado de 100%, o IC 95% de Jeffreys vai de 94,15% a 99,96% (P(F1 > 99%) = 46,74%).",
        font_size=18, title_size=19,
    )

    # ===============================================================
    # 41. EXPLICABILIDADE ESPACIAL (SEM FIGURA REMOVIDA DO TCC)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Explicabilidade espacial: Grad-CAM vs. oclusão 8×8",
        next_lbl(),
        "Elaborado pelo autor (2026), com base em Selvaraju et al. (2020), Zeiler e Fergus (2014) e Adebayo et al. (2018).",
        fonte_two_lines=True,
    )
    add_card(
        s, 0.45, 0.98, 6.05, 5.30,
        "Escala da auditoria espacial",
        items=[
            [("72 imagens curadas: ", True, False, SENAC_BLUE), ("8 por base (4 consensos e 4 divergências, sem duplicatas ou tracks conhecidos)", False, False, TEXT_DARK)],
            [("576 mapas Grad-CAM: ", True, False, SENAC_BLUE), ("validados em block4_activation2 dentro de 10⁻⁴ e testes de sanidade", False, False, TEXT_DARK)],
            [("73.728 oclusões 8×8: ", True, False, SENAC_BLUE), ("borramento gaussiano e preenchimento constante pela média", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=10,
    )
    add_card(
        s, 6.83, 0.98, 6.05, 5.30,
        "Achado central: Spearman ρ = 0,002",
        items=[
            [("1.152 pares auditados: ", True, False, BAD_RED), ("mediana global ρ = 0,002 (−0,002 borramento; +0,008 média)", False, False, TEXT_DARK)],
            "Mapas Grad-CAM em baixa resolução (4×4 ou 8×8) não equivalem à sensibilidade causal da entrada",
            "Painéis causais 8×8 revelam divergências de fronteira entre CNN, Dense20 e cabeças 4×5 qubits",
        ],
        alert=True, font_size=18, title_size=19, space_after=12,
    )

    # ===============================================================
    # 42. PAINÉIS CAUSAIS DE OCLUSÃO — RGB
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Painéis causais de oclusão: domínios RGB", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "painel_oclusao_gtsrb_07_media.png", 0.45, 0.88, 5.95, 4.45)
    add_textbox(
        s, 0.45, 5.38, 5.95, 1.25,
        "gtsrb_07 (cl. 3, média): CNN/Vet acertam (3–6/64); D20 img. prevê cl. 25; Híbridos cl. 10 (10–15/64, até +9,02).",
        font_size=18, color=TEXT_DARK, align=PP_ALIGN.CENTER, line_spacing=1.05,
    )
    add_picture_fit(s, FIG_DIR / "painel_oclusao_cifar100_coarse_01_desfoque.png", 6.90, 0.88, 5.95, 4.45)
    add_textbox(
        s, 6.90, 5.38, 5.95, 1.25,
        "cifar100_01 (insects, desfoque): 8 acertam; CNN/Vet 0/64 trocas; D20 2/64; Híbridos 3/64 p/ flowers (+1,51).",
        font_size=18, color=TEXT_DARK, align=PP_ALIGN.CENTER, line_spacing=1.05,
    )

    # ===============================================================
    # 43. PAINÉIS CAUSAIS DE OCLUSÃO — MONOCROMÁTICOS
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Painéis causais de oclusão: monocromáticos", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "painel_oclusao_fashion_mnist_06_media.png", 0.45, 0.88, 5.95, 4.45)
    add_textbox(
        s, 0.45, 5.38, 5.95, 1.25,
        "fashion_06 (pulôver, média): CNN/Vet acertam cl. 2 (23–26/64); D20 e Híbridos partem da cl. 6 (16 e 31/64).",
        font_size=18, color=TEXT_DARK, align=PP_ALIGN.CENTER, line_spacing=1.05,
    )
    add_picture_fit(s, FIG_DIR / "painel_oclusao_mnist_06_desfoque.png", 6.90, 0.88, 5.95, 4.45)
    add_textbox(
        s, 6.90, 5.38, 5.95, 1.25,
        "mnist_06 (dígito '2', desfoque): só D20 img. acerta (17/64); CNN, Vet e Híbridos preveem '7' (até +10,46).",
        font_size=18, color=TEXT_DARK, align=PP_ALIGN.CENTER, line_spacing=1.05,
    )

    # ===============================================================
    # 44. CUSTO COMPUTACIONAL POR ETAPA (SEÇÃO 4.8 ATUALIZADA)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Custo computacional por etapa (100 épocas, lote 128)", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "fig_48_tempos_etapas_consolidado.png", 0.30, 0.90, 8.35, 5.65)
    add_card(
        s, 8.78, 0.92, 4.20, 5.65,
        "Gargalo da simulação",
        items=[
            [("36 híbridos: ", True, False, BAD_RED), ("503,66 h (21 dias) vs. 18 vetoriais: 558,88 s (9,3 min) — 778× a 2.854×", False, False, TEXT_DARK)],
            [("Mais rápido: ", True, False, OK_GREEN), ("Dense20 vet. Mac (194,86 s; 1.019× vs. Mac PL)", False, False, TEXT_DARK)],
            [("Melhor híbrido: ", True, False, SENAC_BLUE), ("PQC Mac PL (55,17 h) vs. Win QK (200,30 h)", False, False, TEXT_DARK)],
            "CNN FP32: 25,81 h | b128: 18,77 h | D20 img: 3,32 h",
        ],
        font_size=18, title_size=19, space_after=6,
    )

    # ===============================================================
    # 45. FATORES DE ACELERAÇÃO E CUSTO × MACRO-F1 (SEÇÃO 4.8)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Aceleração entre ambientes e simuladores", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "fig_fatores_aceleracao_ambientes_simuladores.png", 0.30, 0.90, 8.35, 5.65)
    add_card(
        s, 8.78, 0.92, 4.20, 5.65,
        "Razões exatas (18/18 pares)",
        items=[
            [("iMac M4 vs. Windows: ", True, False, OK_GREEN), ("1,82× no PennyLane e 1,36× no Qiskit (1,87× vs. Linux no vetorial)", False, False, TEXT_DARK)],
            [("PennyLane vs. Qiskit: ", True, False, OK_GREEN), ("2,68× no Mac e 2,00× no Windows", False, False, TEXT_DARK)],
            [("PQC Mac PennyLane: ", True, False, SENAC_BLUE), ("3,63× mais rápido que Win Qiskit com mesmo Macro-F1 (82,17%; Δ < 0,05 p.p.)", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=8,
    )

    # ===============================================================
    # 46. TELEMETRIA DE HARDWARE E I/O (100 ÉPOCAS - SEÇÃO 4.8)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Telemetria de hardware e I/O (campanha 100 épocas)", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "fig_48_telemetria_hardware_io.png", 0.30, 0.90, 8.35, 5.65)
    add_card(
        s, 8.78, 0.92, 4.20, 5.65,
        "Assinaturas de hardware",
        items=[
            [("Mac (M4): ", True, False, SENAC_BLUE), ("384–389% CPU (≈4 núcleos), 2,56–2,94 GiB RSS; GPU AGX 0,00–0,51%* e I/O proj. 3,2–8,5* GiB", False, False, TEXT_DARK)],
            [("Windows (PQC): ", True, False, BAD_RED), ("316–347% CPU, GPU ociosa (3,7–4,0%) e 456 GiB leitura / 165 GiB escrita", False, False, TEXT_DARK)],
            [("Linux/WSL2: ", True, False, OK_GREEN), ("GPU RTX A2000 ativa (24–43%, 3,0–3,6 GiB VRAM) e baixo I/O", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=8,
    )

    # ===============================================================
    # 46b. SENSORES MACMON E PROJEÇÃO ENERGÉTICA NO iMac M4 (PROMOVIDO AO PRINCIPAL)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Sensores macmon e energia no iMac M4", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "fig_48_mac_hardware_sensores_macmon.png", 0.35, 0.88, 7.40, 5.72)
    add_card(
        s, 7.92, 0.92, 5.05, 5.65,
        "Perfil eletrotérmico (M4)",
        items=[
            [("Potência CPU: ", True, False, SENAC_BLUE), ("15,22 W (PL) vs. 15,15 W (QK); GPU ≈ 0,00 W", False, False, TEXT_DARK)],
            [("Térmica / clock: ", True, False, SENAC_BLUE), ("89,0 °C / 87,6 °C; P-cores estáveis em 3,39 GHz (vs. 4,45 GHz clássico)", False, False, TEXT_DARK)],
            [("Energia (100 ép.*): ", True, False, OK_GREEN), ("946,7 Wh (PL) vs. 2.332,7 Wh (QK) — economia projetada de 2,46×", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=8,
    )

    # ===============================================================
    # 47. TELEMETRIA COMPLEMENTAR NO iMac M4 (20/11 - SEÇÃO 4.8.1)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Telemetria complementar no iMac M4 (27 sessões, 1 ép.)", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "fig_48_mac_hardware_io_complementar.png", 0.30, 0.90, 8.35, 5.65)
    add_card(
        s, 8.78, 0.92, 4.20, 5.65,
        "Confirmado no Apple M4",
        items=[
            [("100% em CPU: ", True, False, SENAC_BLUE), ("GPU Apple AGX em 0,00%–0,51% (potência ≤ 0,03 W)", False, False, TEXT_DARK)],
            [("Regime macmon: ", True, False, SENAC_BLUE), ("~15,2 W CPU, 87,6–89,0 °C, P-cores em 3,39 GHz", False, False, TEXT_DARK)],
            [("I/O baixo: ", True, False, OK_GREEN), ("32×–71× menos leitura projetada que Windows", False, False, TEXT_DARK)],
            [("Energia (100 ép.*): ", True, False, OK_GREEN), ("PL 0,95 kWh vs. QK 2,33 kWh (2,46× economia)", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=6,
    )

    # ===============================================================
    # 48. SÍNTESE: HIPÓTESE, DADOS E COMPROMISSOS
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Síntese: o que a hipótese e os dados dizem", next_lbl())
    synth_rows = [
        ("✓", OK_GREEN, "Estabilidade nas 9 bases (7 a 47 classes): médias globais entre 81,94% e 82,23%"),
        ("✓", OK_GREEN, "Paridade preditiva: Δ Híb. − Dense20 de −0,449 a +0,620 p.p.; PL vs. QK < 0,05 p.p."),
        ("✓", OK_GREEN, "Sem vantagem quântica: ganho sobre a CNN vem do gargalo Dense20"),
        ("✗", BAD_RED, "Trade-offs críticos: custo 778×–2.854× maior, ECE 36,62% no FER2013 e ρ = 0,002"),
    ]
    for idx, (sym, scol, stxt) in enumerate(synth_rows):
        ry = 0.98 + idx * 0.92
        tb = add_textbox(s, 0.55, ry, 12.23, 0.82)
        p = tb.text_frame.paragraphs[0]
        p.line_spacing = 1.08
        r_s = p.add_run()
        r_s.text = f"{sym}  "
        r_s.font.name = FONT_NAME
        r_s.font.size = fpt(20)
        r_s.font.bold = True
        r_s.font.color.rgb = scol
        r_t = p.add_run()
        r_t.text = stxt
        r_t.font.name = FONT_NAME
        r_t.font.size = fpt(18)
        r_t.font.color.rgb = TEXT_DARK

    add_card(
        s, 0.55, 4.78, 12.23, 2.02,
        "Comparação operacional e literatura",
        body_text="Com features128, o híbrido mantém alta separabilidade onde NNQE (filtro fixo) caiu para 36,0% (CIFAR-10) e 73,4% (GTSRB). Entre híbridos, PQC Mac PennyLane (55,17 h) lidera; no geral, Dense20 vetorial Mac entrega paridade em 194,86 s.",
        font_size=18, title_size=19,
    )

    # ===============================================================
    # 49. RETOMADA DO PROBLEMA E OBJETIVOS
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Conclusão: retomada do problema e objetivos", next_lbl())
    tb = add_textbox(s, 0.55, 1.05, 12.23, 5.75)
    add_rich_paragraphs(
        tb.text_frame,
        [
            [("Campanha integralmente auditada: ", True, False, SENAC_BLUE), ("9 bases, 72 checkpoints (mais 36 de balanceamento e 27 de telemetria no iMac M4), avaliados por Macro-F1", False, False, TEXT_DARK)],
            [("Circuito de Senokosov et al. (2024): ", True, False, SENAC_BLUE), ("convergência estável e paridade com CNN e Dense20, com gradientes ativos nos 4 ramos de 5 qubits", False, False, TEXT_DARK)],
            [("Sem superioridade quântica irrestrita: ", True, False, SENAC_BLUE), ("sem o controle Dense20, ganhos sobre a CNN seriam falsos positivos", False, False, TEXT_DARK)],
            [("Eficiência operacional: ", True, False, SENAC_BLUE), ("iMac M4 + PennyLane é 3,63× mais rápido e 2,46× mais econômico em energia que Win/Mac Qiskit, mas 1.019× mais lento que Dense20 vetorial Mac", False, False, TEXT_DARK)],
        ],
        font_size=19, space_after=16,
    )

    # ===============================================================
    # 50. CONTRIBUIÇÕES PARA A COMPUTAÇÃO (5 FRENTES - SEÇÃO 5.3)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Contribuições para a Computação", next_lbl())
    tb = add_textbox(s, 0.55, 0.96, 12.23, 5.95)
    add_rich_paragraphs(
        tb.text_frame,
        [
            [("Benchmark padronizado em 9 bases (72 modelos): ", True, False, SENAC_BLUE), ("supera recortes binários e cobre as 20 superclasses do CIFAR-100 Coarse em Macro-F1", False, False, TEXT_DARK)],
            [("Controle Dense20 e contabilidade paramétrica: ", True, False, SENAC_BLUE), ("evita falsos positivos arquiteturais e separa pesos da cabeça vs. inferência completa", False, False, TEXT_DARK)],
            [("Auditoria de calibração, Bayes e explicabilidade: ", True, False, SENAC_BLUE), ("ECE/NLL/Brier, 1.336 posteriores, 576 Grad-CAM e 73.728 oclusões (ρ = 0,002)", False, False, TEXT_DARK)],
            [("Telemetria multiplataforma de hardware e energia: ", True, False, SENAC_BLUE), ("speedups exatos, CPU, RSS, GPU RTX/AGX, I/O e sensores macmon no Apple M4", False, False, TEXT_DARK)],
            [("Auditoria crítica de dados e literatura: ", True, False, SENAC_BLUE), ("tracks no GTSRB (67,9%), duplicatas/conflitos no FER2013 e divergências em artigos", False, False, TEXT_DARK)],
        ],
        font_size=18, space_after=12, bullet=False, numbered=True,
    )

    # ===============================================================
    # 51. LIMITAÇÕES E TRABALHOS FUTUROS (SEÇÃO 5.4 ATUALIZADA)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Limitações e trabalhos futuros", next_lbl())
    add_styled_table(
        s, 0.42, 0.96, 12.49, 5.80,
        ["Limitação auditada", "Trabalho futuro prioritário"],
        [
            ["Semente única; tracks (GTSRB) e duplicatas (FER2013)", "Split track-aware, deduplicação e múltiplas sementes com IC"],
            ["Descalibração sobre features congeladas (ECE 36,6%)", "Recalibração pós-treino (temperature scaling) e label smoothing"],
            ["4 ramos sem emaranhamento; parameter-shift em CPU", "Emaranhamento cruzado, data re-uploading, adjunto e GPU/cuQuantum"],
            ["Capacidade distinta entre Dense20 e cabeça híbrida", "Ablação de largura do gargalo e pareamento estrito de parâmetros"],
            ["Apenas simulação ideal local (sem QPU física)", "Execução com mitigação de erros em processadores quânticos reais"],
        ],
        col_widths=[5.75, 6.74],
        alignments=[PP_ALIGN.LEFT, PP_ALIGN.LEFT],
        font_size=18, header_font_size=18,
    )

    # ===============================================================
    # 52. OBRIGADO
    # ===============================================================
    main_idx += 1
    assert main_idx == MAIN_TOTAL, f"Esperado {MAIN_TOTAL} slides principais, obtido {main_idx}"
    s = new_slide(prs)
    top_bar2 = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_W, Inches(0.14))
    top_bar2.fill.solid()
    top_bar2.fill.fore_color.rgb = SENAC_BLUE
    top_bar2.line.fill.background()

    if LOGO_PATH.exists():
        add_picture_fit(s, LOGO_PATH, 5.4, 0.78, 2.5, 1.75)
    add_textbox(s, 1.5, 2.95, 10.33, 0.85, "Obrigado!", font_size=38, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER)
    add_textbox(s, 1.5, 3.88, 10.33, 0.55, "Perguntas?", font_size=24, color=SENAC_ORANGE, bold=True, align=PP_ALIGN.CENTER)
    add_textbox(s, 1.5, 4.82, 10.33, 0.50, "Matheus Sanchez Duda", font_size=21, bold=True, color=TEXT_DARK, align=PP_ALIGN.CENTER)
    add_textbox(
        s, 0.65, 5.45, 12.03, 1.05,
        "Orientador: Prof. Samuel Mendes Sanches Junior\nCoorientador: Prof. Thyago Conchado Quintas",
        font_size=18, color=TEXT_MUTED, align=PP_ALIGN.CENTER, line_spacing=1.20,
    )

    # ===============================================================
    # APÊNDICE (A1..A6) — SLIDES DE APOIO PARA ARGUIÇÃO
    # ===============================================================

    # A1: Sobreamostragem e subamostragem
    s = new_slide(prs)
    add_chrome(s, "Apoio A1: sobreamostragem e subamostragem", "A1", "adaptado de Silva (2025).")
    add_picture_fit(s, FIG_DIR / "balanceamento_oversampling_silva2025.png", 0.50, 0.96, 5.95, 3.40)
    add_textbox(s, 0.50, 4.42, 5.95, 0.42, "Sobreamostragem (oversampling)", font_size=18, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER)
    add_picture_fit(s, FIG_DIR / "balanceamento_undersampling_silva2025.png", 6.85, 0.96, 5.95, 3.40)
    add_textbox(s, 6.85, 4.42, 5.95, 0.42, "Subamostragem (undersampling)", font_size=18, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER)
    tb = add_textbox(s, 0.60, 5.05, 12.13, 1.50)
    add_rich_paragraphs(
        tb.text_frame,
        [
            "Estratégias de dados e de algoritmo (class_weight) testadas em 36 execuções preliminares",
            "Validação e teste mantêm sempre a distribuição original; avaliação primária em Macro-F1",
        ],
        font_size=18, space_after=8,
    )

    # A2: Calibração probabilística (FER2013)
    s = new_slide(prs)
    add_chrome(s, "Apoio A2: calibração probabilística no FER2013", "A2", "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "figura_28_calibracao_fer.png", 0.42, 0.90, 7.15, 5.65)
    add_card(
        s, 7.78, 0.94, 5.10, 5.60,
        "Confiança excessiva nos erros",
        items=[
            [("CNN FP32 (LS 0,05): ", True, False, OK_GREEN), ("ECE = 2,08%, NLL = 1,281, conf. nos erros = 42,76%", False, False, TEXT_DARK)],
            [("D20 imagem: ", True, False, SENAC_BLUE), ("ECE = 18,38%, erros = 60,47%", False, False, TEXT_DARK)],
            [("Vetorial Mac: ", True, False, SENAC_BLUE), ("ECE = 31,43%, erros = 75,45%", False, False, TEXT_DARK)],
            [("PQC Mac PL: ", True, False, BAD_RED), ("ECE = 36,62%, NLL = 2,497, conf. nos erros = 82,82% (requer temperature scaling)", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=6,
    )

    # A3: Diagnósticos quânticos (gradientes e ruído/shots)
    s = new_slide(prs)
    add_chrome(s, "Apoio A3: gradientes por ramo e ruído/shots", "A3", "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "figura_19_gradientes.png", 0.45, 0.92, 6.00, 3.85)
    add_textbox(
        s, 0.45, 4.92, 6.00, 1.65,
        "Gradientes (Ramos 1–4): MNIST decai (0,13 → 10⁻⁷); FER2013 segue ativo (4,3×10⁻² a 1,1×10⁻¹) até a época 100.",
        font_size=18, color=TEXT_DARK, align=PP_ALIGN.CENTER, line_spacing=1.08,
    )
    add_picture_fit(s, FIG_DIR / "figura_22_ruido_shots.png", 6.85, 0.92, 6.00, 3.85)
    add_textbox(
        s, 6.85, 4.92, 6.00, 1.65,
        "Ruído e shots (Mac/PL): fidelidade cai a 0,51 (ruído 2,0), mas Δ Macro-F1 típico < 0,10 p.p. (máx. −0,38 p.p. CIFAR-10).",
        font_size=18, color=TEXT_DARK, align=PP_ALIGN.CENTER, line_spacing=1.08,
    )

    # A4: Resultados originais de Senokosov et al. (2024)
    s = new_slide(prs)
    add_chrome(
        s,
        "Apoio A4: resultados originais de Senokosov et al. (2024)",
        "A4",
        "Extraído de Senokosov et al. (2024) (arXiv:2304.09224, Figura 5).",
    )
    add_picture_fit(s, FIG_DIR / "fig_arxiv2304_mnist_loss_acc.png", 0.45, 0.98, 12.43, 3.65)
    tb = add_textbox(s, 0.55, 4.82, 12.23, 1.75)
    add_rich_paragraphs(
        tb.text_frame,
        [
            "MNIST (10 épocas, lote 16, SGD): HQNN-Parallel atingiu 99,21% (45.194 pesos) vs. CNN 98,71% (372.234 pesos)",
            "No artigo original: Medical MNIST 99,97% (vs. 99,96%) e CIFAR-10 82,78% (vs. 82,64%) com 6×5 qubits",
        ],
        font_size=18, space_after=8,
    )

    # A5: Riscos e limitações metodológicas
    s = new_slide(prs)
    add_chrome(s, "Apoio A5: riscos e limitações metodológicas", "A5")
    tb = add_textbox(s, 0.55, 1.02, 12.23, 5.75)
    add_rich_paragraphs(
        tb.text_frame,
        [
            "Sem emaranhamento cruzado entre os quatro subcircuitos independentes de 5 qubits",
            "Uma semente por configuração (seed=42): sem estimativa de variância inter-sementes",
            "Dense20 imagem, vetorial e híbrido diferem em camadas e aumento: sem fator causal único",
            "Dependências auditadas: 67,9% de tracks no GTSRB e 7,02% de duplicatas + 57 conflitos no FER2013",
            "Restrição integral à simulação clássica local em CPU, sem execução em QPU física",
        ],
        font_size=19, space_after=14, bullet=False, numbered=True,
    )

    # A6: Siglas principais
    s = new_slide(prs)
    add_chrome(s, "Apoio A6: siglas principais", "A6")
    add_styled_table(
        s, 0.42, 1.02, 6.08, 5.60,
        ["Sigla", "Significado"],
        [
            ["CNN", "Rede Neural Convolucional"],
            ["PQC", "Circuito Quântico Parametrizado"],
            ["QML", "Aprendizado de Máquina Quântico"],
            ["NISQ", "Era Quântica Ruidosa Intermediária"],
            ["QPU", "Unidade de Processamento Quântico"],
        ],
        col_widths=[1.75, 4.33],
        font_size=18, header_font_size=18,
    )
    add_styled_table(
        s, 6.83, 1.02, 6.08, 5.60,
        ["Sigla", "Significado"],
        [
            ["IR / CV", "Razão de Desbal. / Coef. Variação"],
            ["ECE / NLL", "Erro Calibração / Log-Veross. Neg."],
            ["RSS", "Memória Residente (RAM)"],
            ["VQA", "Algoritmo Quântico Variacional"],
            ["Grad-CAM", "Ativação de Classe por Gradiente"],
        ],
        col_widths=[1.95, 4.13],
        font_size=18, header_font_size=18,
    )

    import sys

    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else OUTPUT_PPTX
    try:
        prs.save(out_path)
    except PermissionError:
        alt_path = out_path.with_name(f"{out_path.stem}_atualizada{out_path.suffix}")
        prs.save(alt_path)
        print(f"AVISO: {out_path} bloqueado (aberto no PowerPoint). Salvo em: {alt_path} ({len(prs.slides)} slides)")
        return
    print(f"PPTX salvo em: {out_path} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    build_deck()
