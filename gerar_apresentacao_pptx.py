"""Gera a apresentacao editavel em PowerPoint (.pptx) alinhada a apresentacao_tcc2_final.tex e tcc2-adaptado.tex."""

from __future__ import annotations

from pathlib import Path
from PIL import Image

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt


BASE_DIR = Path(__file__).resolve().parent
FIG_DIR = BASE_DIR / "figuras"
LOGO_PATH = BASE_DIR / "assets" / "logo-senac.png"
OUTPUT_PPTX = BASE_DIR / "apresentacao_tcc2_final.pptx"

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

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
TEXT_MUTED = RGBColor(96, 106, 118)
BORDER_GRAY = RGBColor(200, 210, 222)
WHITE = RGBColor(255, 255, 255)


def set_cell_margins(cell, left=0.06, right=0.06, top=0.03, bottom=0.03):
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
    font_size=14,
    bold=False,
    italic=False,
    color=TEXT_DARK,
    align=PP_ALIGN.LEFT,
    valign=MSO_ANCHOR.TOP,
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
        p = tf.paragraphs[0]
        p.alignment = align
        run = p.add_run()
        run.text = text
        run.font.name = FONT_NAME
        run.font.size = Pt(font_size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = color
    return tb


def add_rich_paragraphs(tf, items, font_size=13.5, space_after=5, bullet=True, numbered=False):
    """Popula um text_frame com lista de itens compostos por tuplas (texto, bold, italic, cor)."""
    tf.word_wrap = True
    for idx, entry in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        p.line_spacing = 1.12
        if bullet:
            r_b = p.add_run()
            r_b.text = "● "
            r_b.font.name = FONT_NAME
            r_b.font.size = Pt(max(10, font_size - 2))
            r_b.font.bold = True
            r_b.font.color.rgb = SENAC_ORANGE
        elif numbered:
            r_n = p.add_run()
            r_n.text = f"{idx + 1}. "
            r_n.font.name = FONT_NAME
            r_n.font.size = Pt(font_size)
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
            r.font.size = Pt(font_size)
            r.font.bold = b
            r.font.italic = it
            r.font.color.rgb = col


def add_picture_fit(slide, img_path: Path, x, y, max_w, max_h, center_v=True):
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


def add_card(slide, x, y, w, h, title, items=None, body_text="", alert=False, font_size=13, title_size=14):
    header_color = SENAC_ORANGE if alert else SENAC_BLUE
    body_color = SENAC_ORANGE_LIGHT if alert else SENAC_BLUE_LIGHT
    header_h = 0.42

    body = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    body.adjustments[0] = 0.04
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
    hp = htf.paragraphs[0]
    hr = hp.add_run()
    hr.text = title
    hr.font.name = FONT_NAME
    hr.font.size = Pt(title_size)
    hr.font.bold = True
    hr.font.color.rgb = WHITE

    tb = slide.shapes.add_textbox(Inches(x + 0.12), Inches(y + header_h + 0.08), Inches(w - 0.24), Inches(h - header_h - 0.14))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.02)
    if items is not None:
        add_rich_paragraphs(tf, items, font_size=font_size, space_after=4, bullet=True)
    elif body_text:
        if isinstance(body_text, list):
            add_rich_paragraphs(tf, body_text, font_size=font_size, space_after=5, bullet=False)
        else:
            p = tf.paragraphs[0]
            p.line_spacing = 1.15
            r = p.add_run()
            r.text = body_text
            r.font.name = FONT_NAME
            r.font.size = Pt(font_size)
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
    font_size=10.5,
    header_font_size=11,
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
        set_cell_margins(cell, 0.06, 0.06, 0.04, 0.04)
        set_cell_border(cell, "003366", 0.5)
        p = cell.text_frame.paragraphs[0]
        p.alignment = alignments[j] if alignments else PP_ALIGN.LEFT
        r = p.add_run()
        r.text = head
        r.font.name = FONT_NAME
        r.font.size = Pt(header_font_size)
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
            set_cell_margins(cell, 0.06, 0.06, 0.03, 0.03)
            set_cell_border(cell, "CFD9E6", 0.5)
            p = cell.text_frame.paragraphs[0]
            p.alignment = alignments[j] if alignments else PP_ALIGN.LEFT
            r = p.add_run()
            r.text = str(val)
            r.font.name = FONT_NAME
            r.font.size = Pt(font_size)
            r.font.bold = (i in bold_rows) or (j == 0 and len(headers) <= 6 and i in bold_rows)
            r.font.color.rgb = SENAC_BLUE if i in bold_rows else TEXT_DARK
    return table


def add_chrome(slide, title_text, slide_label, fonte_text=None):
    # Barra de título azul
    hdr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_W, Inches(0.78))
    hdr.fill.solid()
    hdr.fill.fore_color.rgb = SENAC_BLUE
    hdr.line.fill.background()
    tf = hdr.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.45)
    tf.margin_right = Inches(1.45)
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = title_text
    r.font.name = FONT_NAME
    r.font.size = Pt(21)
    r.font.bold = True
    r.font.color.rgb = WHITE

    # Chip branco com logo SENAC
    chip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(12.16), Inches(0.08), Inches(0.95), Inches(0.62))
    chip.adjustments[0] = 0.12
    chip.fill.solid()
    chip.fill.fore_color.rgb = WHITE
    chip.line.fill.background()
    if LOGO_PATH.exists():
        add_picture_fit(slide, LOGO_PATH, 12.22, 0.12, 0.83, 0.54)

    # Rodapé
    f1 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.18), Inches(4.53), Inches(0.32))
    f1.fill.solid()
    f1.fill.fore_color.rgb = SENAC_BLUE
    f1.line.fill.background()
    p1 = f1.text_frame.paragraphs[0]
    f1.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    f1.text_frame.margin_left = Inches(0.25)
    r1 = p1.add_run()
    r1.text = "M. S. Duda"
    r1.font.name = FONT_NAME
    r1.font.size = Pt(10)
    r1.font.color.rgb = WHITE

    f2 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.53), Inches(7.18), Inches(6.67), Inches(0.32))
    f2.fill.solid()
    f2.fill.fore_color.rgb = SENAC_BLUE_MID
    f2.line.fill.background()
    p2 = f2.text_frame.paragraphs[0]
    p2.alignment = PP_ALIGN.CENTER
    f2.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    r2 = p2.add_run()
    r2.text = "CNNs clássicas vs. híbridas quântico-clássicas"
    r2.font.name = FONT_NAME
    r2.font.size = Pt(10)
    r2.font.color.rgb = WHITE

    f3 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(11.20), Inches(7.18), Inches(2.133), Inches(0.32))
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
    r3.font.size = Pt(10)
    r3.font.color.rgb = WHITE

    if fonte_text:
        add_textbox(
            slide,
            0.45,
            6.88,
            12.43,
            0.26,
            text=f"Fonte: {fonte_text}",
            font_size=9.5,
            color=TEXT_MUTED,
            valign=MSO_ANCHOR.BOTTOM,
        )


def new_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def build_deck() -> None:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    # Contagem principal: slides 1..44 (apêndice A1..A7 fica fora do contador principal, igual ao appendixnumberbeamer)
    MAIN_TOTAL = 44

    def lbl(n):
        return f"{n}/{MAIN_TOTAL}"

    # ---------------------------------------------------------------
    # 1. CAPA
    # ---------------------------------------------------------------
    s = new_slide(prs)
    top_bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_W, Inches(0.14))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = SENAC_BLUE
    top_bar.line.fill.background()

    if LOGO_PATH.exists():
        add_picture_fit(s, LOGO_PATH, 5.4, 0.45, 2.5, 1.75)

    add_textbox(
        s,
        0.9,
        2.45,
        11.53,
        1.15,
        "Classificação de imagens em múltiplos conjuntos de referência de visão computacional:\nCNNs clássicas vs. arquiteturas híbridas quântico-clássicas",
        font_size=24,
        bold=True,
        color=SENAC_BLUE,
        align=PP_ALIGN.CENTER,
    )
    add_textbox(
        s,
        1.5,
        3.75,
        10.33,
        0.45,
        "Apresentação final — TCC2",
        font_size=17,
        color=SENAC_ORANGE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_textbox(
        s,
        1.5,
        4.45,
        10.33,
        0.45,
        "Matheus Sanchez Duda",
        font_size=17,
        bold=True,
        color=TEXT_DARK,
        align=PP_ALIGN.CENTER,
    )
    add_textbox(
        s,
        1.2,
        5.00,
        10.93,
        1.1,
        "SENAC — Unidade Santo Amaro\nBacharelado em Ciência da Computação\nOrientador: Prof. Samuel Mendes Sanches Junior   |   Coorientador: Prof. Thyago Conchado Quintas",
        font_size=13.5,
        color=TEXT_MUTED,
        align=PP_ALIGN.CENTER,
    )
    add_textbox(s, 1.5, 6.65, 10.33, 0.35, "São Paulo, 2026", font_size=12.5, color=TEXT_MUTED, align=PP_ALIGN.CENTER)

    # ---------------------------------------------------------------
    # 2. ROTEIRO
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Roteiro da apresentação", lbl(2))
    agenda = [
        ("1. Introdução e problema", "Contexto, lacuna na literatura de QML, objetivos e delimitações"),
        ("2. Fundamentação", "Imagens, Macro-F1, CNNs (FMAP3), aumento de dados (aug_01–03), circuitos quânticos e simulação"),
        ("3. Trabalhos correlatos e lacuna", "Funil bibliográfico, estudos clássicos e quânticos nas 9 bases e lacuna"),
        ("4. Desenvolvimento", "Pipeline experimental, 9 bases, balanceamento (all_raw), arquiteturas separadas e 2 ambientes"),
        ("5. Resultados e discussão", "72 modelos em Macro-F1, controle Dense20, GTSRB, oclusão 8×8 e custo computacional"),
        ("6. Conclusão e apêndice", "Síntese crítica, contribuições, limitações e slides de apoio para arguição"),
    ]
    for i, (t, d) in enumerate(agenda):
        row_y = 1.15 + i * 0.90
        badge = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), Inches(row_y), Inches(3.85), Inches(0.70))
        badge.adjustments[0] = 0.14
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
        br.font.size = Pt(14.5)
        br.font.bold = True
        br.font.color.rgb = WHITE

        desc_box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.88), Inches(row_y), Inches(7.55), Inches(0.70))
        desc_box.adjustments[0] = 0.14
        desc_box.fill.solid()
        desc_box.fill.fore_color.rgb = SENAC_BLUE_LIGHT
        desc_box.line.color.rgb = BORDER_GRAY
        dtf = desc_box.text_frame
        dtf.word_wrap = True
        dtf.vertical_anchor = MSO_ANCHOR.MIDDLE
        dtf.margin_left = Inches(0.20)
        dp = dtf.paragraphs[0]
        dr = dp.add_run()
        dr.text = d
        dr.font.name = FONT_NAME
        dr.font.size = Pt(13.5)
        dr.font.color.rgb = TEXT_DARK

    # ---------------------------------------------------------------
    # 3. CONTEXTO
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Contexto", lbl(3))
    add_card(
        s, 0.50, 1.15, 3.92, 3.90,
        "Visão computacional",
        body_text="Classificar imagens é base de leitura de documentos, inspeção industrial, trânsito e interação humano-computador.",
        font_size=15, title_size=15.5,
    )
    add_card(
        s, 4.70, 1.15, 3.92, 3.90,
        "CNNs",
        body_text="Extraem representações hierárquicas direto dos pixels, mas seu desempenho e custo dependem de ativação, lote, quantização e hardware.",
        font_size=15, title_size=15.5,
    )
    add_card(
        s, 8.90, 1.15, 3.92, 3.90,
        "QML e era NISQ",
        body_text="Circuitos quânticos parametrizados (PQCs) acoplados a extratores clássicos: promessa de espaços de Hilbert grandes, mas com gargalos de simulação, gradientes e escala.",
        font_size=15, title_size=15.5,
    )
    add_textbox(
        s, 0.7, 5.45, 11.9, 0.75,
        "Como esses dois mundos se comparam em vários domínios visuais?",
        font_size=22, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER,
    )

    # ---------------------------------------------------------------
    # 4. PROBLEMA E JUSTIFICATIVA
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Problema e justificativa", lbl(4))
    add_card(
        s, 0.50, 1.15, 5.95, 5.30,
        "O problema na literatura de QML",
        items=[
            "Experimentos em recortes simples: MNIST binário (3 vs. 5), 4 classes, conjuntos sintéticos",
            "Métrica quase sempre restrita à acurácia global",
            "Comparações com variáveis de confusão (lote 1 vs. 4, ausência de controle de gargalo)",
            "Pouca reprodutibilidade (sementes, hiperparâmetros e partições)",
        ],
        font_size=14.5, title_size=15.5,
    )
    add_card(
        s, 6.85, 1.15, 5.95, 5.30,
        "Por que importa",
        items=[
            [("Tecnológica: ", True, False, SENAC_ORANGE), ("qualidade preditiva vs. custo computacional", False, False, TEXT_DARK)],
            [("Acadêmica: ", True, False, SENAC_ORANGE), ("validar cabeças quânticas sob condições idênticas na era NISQ", False, False, TEXT_DARK)],
            [("Metodológica: ", True, False, SENAC_ORANGE), ("base empírica auditável, transparente e reprodutível", False, False, TEXT_DARK)],
        ],
        font_size=14.5, title_size=15.5,
    )

    # ---------------------------------------------------------------
    # 5. OBJETIVOS
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Objetivos", lbl(5))
    add_card(
        s, 0.50, 1.05, 12.33, 1.55,
        "Objetivo geral",
        body_text=[
            [
                ("Comparar desempenho preditivo, estabilidade e custo computacional de ", False, False, TEXT_DARK),
                ("CNNs clássicas", True, False, SENAC_BLUE),
                (" e ", False, False, TEXT_DARK),
                ("arquiteturas híbridas quântico-clássicas", True, False, SENAC_BLUE),
                (" na classificação de imagens em ", False, False, TEXT_DARK),
                ("nove conjuntos de dados", True, False, SENAC_BLUE),
                (".", False, False, TEXT_DARK),
            ]
        ],
        font_size=15, title_size=15,
    )
    add_card(
        s, 0.50, 2.85, 3.92, 3.65,
        "Bases e pipeline",
        items=[
            "Inventariar as 9 bases de referência",
            "Fluxo reprodutível: pré-processamento, partição estratificada, treino, validação e teste",
        ],
        font_size=14, title_size=14.5,
    )
    add_card(
        s, 4.70, 2.85, 3.92, 3.65,
        "Modelos",
        items=[
            "CNN clássica de referência",
            "Controle clássico Dense20 (imagem e vetorial)",
            "Cabeça híbrida 4×5 qubits compatível com simulação de PQCs",
        ],
        font_size=14, title_size=14.5,
    )
    add_card(
        s, 8.90, 2.85, 3.92, 3.65,
        "Avaliação",
        items=[
            "Macro-F1, acurácia, precisão, revocação e matrizes de confusão",
            "Calibração, oclusão 8×8 e telemetria de execução",
            "Discussão crítica de viabilidade",
        ],
        font_size=14, title_size=14.5,
    )

    # ---------------------------------------------------------------
    # 6. HIPÓTESE E DELIMITAÇÕES
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Hipótese e delimitações", lbl(6))
    add_card(
        s, 0.50, 1.15, 12.33, 2.45,
        "Hipótese",
        body_text=[
            [
                ("Uma cabeça híbrida com PQCs simulados alcança ", False, False, TEXT_DARK),
                ("convergência estável e desempenho competitivo", True, False, SENAC_BLUE),
                (", próximo ao ", False, False, TEXT_DARK),
                ("baseline", False, True, TEXT_DARK),
                (" clássico, sob um protocolo controlado.", False, False, TEXT_DARK),
            ],
            [
                ("Não", True, True, SENAC_ORANGE),
                (" se pressupõe superioridade quântica irrestrita.", False, False, TEXT_DARK),
            ],
        ],
        font_size=16, title_size=15.5,
    )
    add_card(
        s, 0.50, 3.90, 12.33, 2.50,
        "Delimitações",
        items=[
            "Somente classificação supervisionada de imagens estáticas 2D",
            [("Circuitos quânticos ", False, False, TEXT_DARK), ("apenas simulados", True, False, TEXT_DARK), (" em CPU local (sem QPU física)", False, False, TEXT_DARK)],
        ],
        alert=True, font_size=15.5, title_size=15.5,
    )

    # ---------------------------------------------------------------
    # 7. IMAGEM DIGITAL
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Imagem digital como matriz de intensidades", lbl(7), "TCC, Seção 2.4.1 (Representação computacional de imagens digitais).")
    add_picture_fit(s, FIG_DIR / "imagem_matriz_5x5.png", 1.3, 1.00, 10.7, 3.95)
    tb = add_textbox(s, 0.75, 5.15, 11.8, 1.55)
    add_rich_paragraphs(
        tb.text_frame,
        [
            "Imagem em cinza: matriz 2D de pixels; imagem RGB: tensor com 3 canais",
            "As 9 bases variam em resolução original (28×28 a 48×48; variável no GTSRB) e canais (1 ou 3)",
        ],
        font_size=15, space_after=8,
    )

    # ---------------------------------------------------------------
    # 8. MÉTRICAS
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Métricas: por que o Macro-F1?", lbl(8), "TCC, Seção 2.4.4 (Métricas de avaliação).")
    add_picture_fit(s, FIG_DIR / "metricas_classificacao_exemplos.png", 1.8, 0.98, 9.7, 4.10)
    tb = add_textbox(s, 0.75, 5.20, 11.8, 1.50)
    add_rich_paragraphs(
        tb.text_frame,
        [
            "Matriz de confusão, TP/FP/FN/TN por classe (um contra todos), ROC/AUC",
            [("Macro-F1", True, False, SENAC_BLUE), (" = média não ponderada do F1 de todas as classes: dá o mesmo peso às minoritárias (SVHN, GTSRB, FER2013)", False, False, TEXT_DARK)],
        ],
        font_size=14.5, space_after=8,
    )

    # ---------------------------------------------------------------
    # 9. CONVOLUÇÃO E POOLING
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "CNN: convolução e pooling", lbl(9), "TCC, Seção 2.5.2 (Redes neurais convolucionais).")
    add_picture_fit(s, FIG_DIR / "convolutional-pooling.png", 2.1, 0.98, 9.1, 4.25)
    tb = add_textbox(s, 0.75, 5.35, 11.8, 1.35)
    add_rich_paragraphs(
        tb.text_frame,
        [
            "Filtros treináveis percorrem a imagem e detectam padrões espaciais locais",
            "Pooling reduz a resolução espacial progressivamente, preservando informações discriminativas",
        ],
        font_size=15, space_after=8,
    )

    # ---------------------------------------------------------------
    # 10. MAPAS DE CARACTERÍSTICAS (FMAP3)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Mapas de características em entradas monocromáticas (64×64×1)",
        lbl(10),
        "TCC, Seção 2.5.2 (Figura 6: FMAP3 em entradas 64×64×1).",
    )
    add_picture_fit(s, FIG_DIR / "fmap_03_piramide_blocos_grayscale.png", 0.45, 0.98, 7.85, 5.65)
    add_card(
        s, 8.50, 1.15, 4.35, 5.20,
        "Hierarquia de ativações (FMAP3)",
        items=[
            [("B1–B2: ", True, False, SENAC_BLUE), ("bordas e contornos locais (bota no Fashion-MNIST; sorriso/olhos no FER2013)", False, False, TEXT_DARK)],
            [("B3–B5 pré: ", True, False, SENAC_BLUE), ("concentração progressiva na região semântica do objeto", False, False, TEXT_DARK)],
            [("GAP → features128: ", True, False, SENAC_BLUE), ("62/128 canais ativos (>0) no Fashion-MNIST (100,00%) e 63/128 no FER2013 (97,40%)", False, False, TEXT_DARK)],
            "Valores negativos leves limitados em −0,2785 (mínimo teórico da SiLU)",
        ],
        font_size=13.5, title_size=14.5,
    )

    # ---------------------------------------------------------------
    # 11. PIPELINE COMPOSTO DE AUMENTO DE DADOS (aug_01 + aug_02)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Aumento de dados: pipeline composto em 6 etapas (data.py)",
        lbl(11),
        "TCC, Seção 2.5.4 (Figura 8: decomposição composta GTSRB e CIFAR-10).",
    )
    add_textbox(s, 0.50, 0.88, 12.33, 0.30, "(a) GTSRB (128×128×3, classe 14 — placa PARE)", font_size=12, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER)
    add_picture_fit(s, FIG_DIR / "aug_01_pipeline_etapas_gtsrb.png", 0.55, 1.16, 12.23, 2.35)
    add_textbox(s, 0.50, 3.58, 12.33, 0.30, "(b) CIFAR-10 (64×64×3, classe navio)", font_size=12, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER)
    add_picture_fit(s, FIG_DIR / "aug_02_pipeline_etapas_cifar10.png", 0.55, 3.86, 12.23, 2.35)
    add_textbox(
        s, 0.50, 6.26, 12.33, 0.55,
        "Seis etapas determinísticas (REFLECT ±5%, zoom [0,96; 1,04], brilho ±0,03, contraste [0,92; 1,08], ruído σ=0,005 e cutout ~8%) com mapas |Δ| e RMS total de 0,2967 (GTSRB) e 0,1084 (CIFAR-10).",
        font_size=12.5, color=TEXT_DARK, align=PP_ALIGN.CENTER,
    )

    # ---------------------------------------------------------------
    # 12. PRESERVAÇÃO SEMÂNTICA E flip_lr=False (aug_03)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Aumento de dados, preservação semântica e flip_lr=False",
        lbl(12),
        "TCC, Seção 2.5.4 (Figura 7: comparação semântica aug_03).",
    )
    add_picture_fit(s, FIG_DIR / "aug_03_comparacao_flip_lr_semantico.png", 0.45, 0.98, 7.75, 5.65)
    add_card(
        s, 8.40, 1.15, 4.45, 5.20,
        "Por que retirar o flip horizontal?",
        items=[
            [("Inversão semântica: ", True, False, BAD_RED), ("espelhar altera a classe de GTSRB (cl. 34 'Vire à esquerda'), MNIST ('3'), EMNIST ('R') e SVHN ('5')", False, False, TEXT_DARK)],
            [("Invariância restrita: ", True, False, OK_GREEN), ("válido apenas em objetos naturais como o cavalo do CIFAR-10", False, False, TEXT_DARK)],
            [("Transparência metodológica: ", True, False, SENAC_BLUE), ("checkpoints FP32 legados usaram flip_lr=True; corrigido definitivamente para flip_lr=False em src/data_prep/data.py", False, False, TEXT_DARK)],
        ],
        font_size=13.5, title_size=14.5,
    )

    # ---------------------------------------------------------------
    # 13. QUBITS E CIRCUITOS
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Qubits, portas e circuitos quânticos",
        lbl(13),
        "TCC, Seção 2.6.1–2.6.2. Figura ilustrativa da documentação IBM Quantum/Qiskit.",
    )
    add_picture_fit(s, FIG_DIR / "ibm_visualize_circuits_latex.png", 2.0, 1.15, 9.3, 3.6)
    tb = add_textbox(s, 0.85, 5.05, 11.6, 1.65)
    add_rich_paragraphs(
        tb.text_frame,
        [
            "Qubit: superposição de |0⟩ e |1⟩; portas H, X e CNOT transformam amplitudes e geram emaranhamento",
            "A medição colapsa o estado quântico e retorna valores esperados clássicos para a rede",
        ],
        font_size=15, space_after=10,
    )

    # ---------------------------------------------------------------
    # 14. CODIFICAÇÃO + ANSATZ
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Codificação de dados e ansatz parametrizado",
        lbl(14),
        "TCC, Seções 2.6.3–2.6.4. Figuras ilustrativas da documentação Qiskit; experimento implementado com PennyLane e Qiskit Aer.",
    )
    add_picture_fit(s, FIG_DIR / "qiskit_ml_torch_connector_qnn_circuit.png", 0.65, 1.05, 12.0, 1.75)
    add_picture_fit(s, FIG_DIR / "ibm_real_amplitudes_1.png", 0.65, 3.20, 5.2, 3.0)
    add_card(
        s, 6.15, 3.15, 6.65, 3.20,
        "Mapeamento e otimização",
        items=[
            [("Feature map: ", True, False, SENAC_BLUE), ("dado clássico codificado como ângulos de rotação dos qubits", False, False, TEXT_DARK)],
            [("Ansatz: ", True, False, SENAC_BLUE), ("camadas rotacionais treináveis + portas CNOT de emaranhamento", False, False, TEXT_DARK)],
            "Parâmetros otimizados por gradiente (parameter-shift / diferenciação automática) acoplados à rede neural",
        ],
        font_size=14, title_size=14.5,
    )

    # ---------------------------------------------------------------
    # 15. SIMULAÇÃO E LIMITES
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Simulação, barren plateaus e escalabilidade",
        lbl(15),
        "TCC, Seções 2.6.5–2.6.6. Fluxo de simulação do Qiskit Aer (Faj et al., 2023).",
    )
    add_picture_fit(s, FIG_DIR / "qiskit_aer_cuquantum_workflow_faj2023.png", 0.75, 1.05, 11.8, 3.15)
    tb = add_textbox(s, 0.75, 4.45, 11.8, 2.25)
    add_rich_paragraphs(
        tb.text_frame,
        [
            "Simular n qubits exige 2ⁿ amplitudes: 20 qubits ⇒ 2²⁰ (1.048.576) estados por amostra do lote",
            "Barren plateaus dificultam o treinamento de circuitos largos e profundos",
            [("Consequência de projeto: ", True, False, SENAC_BLUE), ("decompor a cabeça em 4 circuitos independentes de 5 qubits (2⁵ = 32 estados cada)", False, False, TEXT_DARK)],
        ],
        font_size=15, space_after=10,
    )

    # ---------------------------------------------------------------
    # 16. REVISÃO DA LITERATURA (FUNIL NATIVO)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Como foi a revisão da literatura", lbl(16), "TCC, Seção 2.1 (fluxo de busca, triagem e extração).")
    funnel_steps = [
        ("5.925 ocorrências brutas (2021–2026)", 6.4, SENAC_BLUE, WHITE),
        ("3.297 grupos após desduplicação", 5.4, RGBColor(38, 86, 134), WHITE),
        ("1.025 candidatos (triagem automática)", 4.4, RGBColor(72, 120, 168), WHITE),
        ("28 registros verificados (19 clássicos + 9 quânticos)", 3.7, SENAC_ORANGE, WHITE),
    ]
    for idx, (ftext, fw, bgc, fgc) in enumerate(funnel_steps):
        fx = 0.55 + (6.4 - fw) / 2.0
        fy = 1.25 + idx * 1.25
        box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(fx), Inches(fy), Inches(fw), Inches(0.95))
        box.adjustments[0] = 0.14
        box.fill.solid()
        box.fill.fore_color.rgb = bgc
        box.line.fill.background()
        btf = box.text_frame
        btf.word_wrap = True
        btf.vertical_anchor = MSO_ANCHOR.MIDDLE
        bp = btf.paragraphs[0]
        bp.alignment = PP_ALIGN.CENTER
        br = bp.add_run()
        br.text = ftext
        br.font.name = FONT_NAME
        br.font.size = Pt(14)
        br.font.bold = True
        br.font.color.rgb = fgc

    add_card(
        s, 7.35, 1.25, 5.45, 4.95,
        "Diretrizes da auditoria bibliográfica",
        items=[
            "Frente 1: fundamentação teórica e artigos originais das 9 bases",
            "Frente 2: estudos empíricos por base de dados",
            "Conferência manual da fonte primária: variante, nº de classes, partição e métrica",
            "Contagens representam mapeamento preliminar, não total exaustivo de elegíveis",
        ],
        font_size=14, title_size=15,
    )

    # ---------------------------------------------------------------
    # 17. CORRELATOS CLÁSSICOS (TABELA NATIVA)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Estudos clássicos nas 9 bases", lbl(17), "TCC, Tabela 2 (Seção 2.8.1).")
    add_styled_table(
        s, 0.50, 1.00, 12.33, 5.15,
        ["Base", "Estudo e arquitetura", "Resultado"],
        [
            ["MNIST", "Kabir et al. (2023), VGG-5 + Spinal FC", "99,69%"],
            ["Fashion-MNIST", "Khanday et al. (2021), CNN rasa", "92,68%"],
            ["KMNIST", "Kabir et al. (2023), VGG-5 + Spinal FC", "99,05%"],
            ["EMNIST Balanced", "Kabir et al. (2023), VGG-5 + Spinal FC (47 classes)", "90,73%"],
            ["CIFAR-10", "Khanday et al. (2021), CNN 3×3", "73,04%"],
            ["CIFAR-100 Coarse", "Guo et al. (2018), CNN-RNN, tarefa conjunta", "88,23%"],
            ["SVHN", "Huang et al. (2017), DenseNet (usa conjunto extra)", "98,41%"],
            ["GTSRB", "An et al. (2024), LeNet-5 modificada (Tab. 8 do artigo: val_accuracy)", "97,53%"],
            ["FER2013", "Li et al. (2021), Auto-FERNet", "73,78%"],
        ],
        col_widths=[2.50, 7.83, 2.00],
        alignments=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT],
        font_size=11.5, header_font_size=12,
    )
    add_textbox(
        s, 0.50, 6.26, 12.33, 0.45,
        "Acurácia de teste reportada pelos autores: não equivale ao Macro-F1 deste trabalho; protocolos e partições diferem.",
        font_size=12, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER,
    )

    # ---------------------------------------------------------------
    # 18. CORRELATOS QUÂNTICOS (TABELA NATIVA + CARD)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Estudos quânticos e híbridos", lbl(18), "TCC, Tabela 3 (Seção 2.8.2).")
    add_styled_table(
        s, 0.45, 1.05, 8.05, 5.40,
        ["Base", "Recorte e resultado"],
        [
            ["MNIST", "3 vs. 5 binário: 98,85% (Long, 2025); NNQE 10 classes: 93,8% (Riaz, 2023)"],
            ["Fashion-MNIST", "4 classes: 85,93–93,63% vs. 89,69–97,42% clás. (Bokhan, 2022)"],
            ["KMNIST", "Apenas experimento binário identificado (Dong, 2025)"],
            ["EMNIST", "75,9% com filtro quântico fixo de 4 qubits (Riaz, 2026)"],
            ["CIFAR-10", "NNQE em tons de cinza: 36,0% em teste (Riaz, 2023)"],
            ["CIFAR-100 Coarse", "Nenhum estudo quântico/híbrido confirmado nas 20 superclasses"],
            ["GTSRB", "NNQE: 73,4% vs. 82,2% na rede densa clássica (Riaz, 2023)"],
        ],
        col_widths=[2.25, 5.80],
        alignments=[PP_ALIGN.LEFT, PP_ALIGN.LEFT],
        font_size=11, header_font_size=11.5, bold_rows={5},
    )
    add_card(
        s, 8.70, 1.05, 4.18, 5.40,
        "Padrões críticos observados",
        items=[
            "Predomínio de recortes binários, 4 classes ou conjuntos sintéticos",
            "Filtros quânticos fixos (não treináveis) seguidos de camadas densas",
            "O NNQE no GTSRB demonstra que a inserção quântica não melhora todas as tarefas",
            "CIFAR-100 Coarse (20 superclasses) permanece lacuna aberta na literatura QML",
        ],
        font_size=13, title_size=14,
    )

    # ---------------------------------------------------------------
    # 19. LACUNA DE PESQUISA
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Lacuna de pesquisa", lbl(19), "TCC, Seção 2.9 (Síntese da lacuna de pesquisa).")
    tb = add_textbox(s, 0.55, 1.15, 12.23, 3.15)
    add_rich_paragraphs(
        tb.text_frame,
        [
            [("Protocolos fragmentados: ", True, False, SENAC_BLUE), ("poucas classes e poucos domínios; nenhum resultado quântico confirmado para as 20 superclasses do CIFAR-100 Coarse", False, False, TEXT_DARK)],
            [("Só acurácia global: ", True, False, SENAC_BLUE), ("Macro-F1 raramente reportado justamente nas bases severamente desbalanceadas (GTSRB, FER2013, SVHN)", False, False, TEXT_DARK)],
            [("Variáveis de confusão: ", True, False, SENAC_BLUE), ("tamanhos de lote assimétricos (ex.: 1 vs. 4) e ausência de controle clássico com gargalo equivalente", False, False, TEXT_DARK)],
        ],
        font_size=15.5, space_after=12, bullet=False, numbered=True,
    )
    add_card(
        s, 0.55, 4.45, 12.23, 2.00,
        "Contribuição proposta",
        body_text="Campanha padronizada nas 9 bases completas, avaliada prioritariamente por Macro-F1 e acompanhada de controle vetorial de gargalo (Dense20), calibração, oclusão 8×8 e telemetria.",
        font_size=15, title_size=15.5,
    )

    # ---------------------------------------------------------------
    # 20. TIPO DE PESQUISA E PERGUNTA
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Tipo de pesquisa e pergunta de pesquisa", lbl(20), "TCC, Seções 3.1–3.2.")
    tb = add_textbox(s, 0.60, 1.15, 12.13, 2.40)
    add_rich_paragraphs(
        tb.text_frame,
        [
            [("Aplicada", True, False, SENAC_BLUE), (", com abordagem ", False, False, TEXT_DARK), ("quantitativa", True, False, SENAC_BLUE)],
            [("Objetivos ", False, False, TEXT_DARK), ("exploratórios", True, False, TEXT_DARK), (" (CIFAR-100 Coarse e EMNIST pouco explorados em QML), ", False, False, TEXT_DARK), ("descritivos", True, False, TEXT_DARK), (" (72 checkpoints documentados) e ", False, False, TEXT_DARK), ("comparativos", True, False, TEXT_DARK)],
        ],
        font_size=16, space_after=14,
    )
    add_card(
        s, 0.60, 3.75, 12.13, 2.55,
        "Pergunta de pesquisa",
        body_text="Nas nove bases, em que medida a representação congelada features128 sustenta cabeças reduzidas e como o híbrido (4 circuitos de 5 qubits) se compara em Macro-F1, calibração, explicabilidade e custo frente à CNN original e ao controle Dense20?",
        font_size=16, title_size=15.5,
    )

    # ---------------------------------------------------------------
    # 21. PIPELINE EXPERIMENTAL EM SEIS ETAPAS (NATIVO COM SETAS)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Pipeline experimental em seis etapas", lbl(21), "TCC, Seção 3.3 (Visão geral da solução proposta).")
    stages = [
        ("1. Inventário e partições", "9 bases padronizadas (SHA-256)"),
        ("2. Extrator e features128", "CNN FP32, 64×64 (128×128 GTSRB) → .npy"),
        ("3. Cabeças clássicas", "CNN original e controle Dense20"),
        ("4. Híbrido 4×5 qubits", "36 treinos CPU (Win/Mac × PL/QK)"),
        ("5. Auditoria e explicabilidade", "Macro-F1, ECE, Grad-CAM e oclusão 8×8"),
        ("6. Telemetria operacional", "Tempos em lote 128, CPU% e RSS"),
    ]
    box_w, box_h = 3.55, 1.55
    xs = [0.65, 4.88, 9.11]
    ys = [1.45, 4.05]
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
        r0.font.size = Pt(14)
        r0.font.bold = True
        r0.font.color.rgb = SENAC_BLUE
        p1 = btf.add_paragraph()
        p1.alignment = PP_ALIGN.CENTER
        r1 = p1.add_run()
        r1.text = st_d
        r1.font.name = FONT_NAME
        r1.font.size = Pt(12.5)
        r1.font.color.rgb = TEXT_DARK

    # Setas conectoras nativas (1->2->3 e retorno Z de 3->4->5->6)
    for row_y in [ys[0] + box_h / 2, ys[1] + box_h / 2]:
        for c in range(2):
            arr = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(xs[c] + box_w + 0.10), Inches(row_y - 0.14), Inches(0.48), Inches(0.28))
            arr.fill.solid()
            arr.fill.fore_color.rgb = SENAC_ORANGE
            arr.line.fill.background()
    # Conector em degrau: saída inferior do bloco 3 -> horizontal -> entrada superior do bloco 4
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

    # ---------------------------------------------------------------
    # 22. AS NOVE BASES DE DADOS (TABELA NATIVA)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "As nove bases de dados", lbl(22), "TCC, Tabela 1 (Seções 2.3.2 e 3.4).")
    add_styled_table(
        s, 0.55, 1.05, 12.23, 5.05,
        ["Base", "Domínio", "Entrada original", "Classes", "Treino / Val. / Teste"],
        [
            ["MNIST", "dígitos manuscritos", "28×28, cinza", "10", "48.999 / 10.503 / 10.498"],
            ["Fashion-MNIST", "vestuário", "28×28, cinza", "10", "49.000 / 10.500 / 10.500"],
            ["KMNIST", "caracteres Kuzushiji", "28×28, cinza", "10", "49.000 / 10.500 / 10.500"],
            ["EMNIST Balanced", "alfanumérico", "28×28, cinza", "47", "92.120 / 19.740 / 19.740"],
            ["CIFAR-10", "objetos e animais", "32×32, RGB", "10", "42.000 / 9.000 / 9.000"],
            ["CIFAR-100 Coarse", "superclasses", "32×32, RGB", "20", "42.000 / 9.000 / 9.000"],
            ["SVHN", "dígitos de fachadas", "32×32, RGB", "10", "69.502 / 14.894 / 14.893"],
            ["GTSRB", "placas de trânsito", "variável, RGB", "43", "27.489 / 5.905 / 5.876"],
            ["FER2013", "expressões faciais", "48×48, cinza", "7", "25.121 / 5.384 / 5.382"],
        ],
        col_widths=[2.55, 3.00, 2.25, 1.25, 3.18],
        alignments=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT],
        font_size=12, header_font_size=12.5,
    )
    add_textbox(
        s, 0.55, 6.22, 12.23, 0.45,
        "Partições estratificadas fixas (70/15/15) da campanha auditada (30/10/2026), distintas das divisões oficiais originais.",
        font_size=12, color=TEXT_MUTED, align=PP_ALIGN.CENTER,
    )

    # ---------------------------------------------------------------
    # 23. EQUILÍBRIO DE CLASSES (FIGURA 14 MOVIDA PARA SEÇÃO 3.4)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Equilíbrio de classes: três regimes",
        lbl(23),
        "TCC, Seção 3.4.1 (Figura 14: distribuição de amostras por classe e razão de desbalanceamento).",
    )
    add_picture_fit(s, FIG_DIR / "equilibrio_classes_9_datasets.png", 0.45, 0.94, 8.20, 5.82)
    add_card(
        s, 8.85, 1.20, 4.00, 5.10,
        "Regimes amostrais (IR = n_max / n_min)",
        items=[
            [("IR = 1,00× (CV = 0%): ", True, False, SENAC_BLUE), ("Fashion-MNIST, KMNIST, EMNIST, CIFAR-10 e CIFAR-100 Coarse", False, False, TEXT_DARK)],
            [("IR = 1,25×: ", True, False, SENAC_BLUE), ("MNIST (assimetria branda)", False, False, TEXT_DARK)],
            [("IR = 3,03× a 16,43×: ", True, False, BAD_RED), ("SVHN (3,03×), GTSRB (10,71×) e FER2013 (16,43×; só 547 imagens em desgosto)", False, False, TEXT_DARK)],
            "Validação e teste preservam integralmente a distribuição original",
        ],
        font_size=13, title_size=14,
    )

    # ---------------------------------------------------------------
    # 24. MODOS DE BALANCEAMENTO E ESCOLHA DE all_raw
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Modos de balanceamento e escolha de all_raw (36 execuções)",
        lbl(24),
        "TCC, Seção 3.4.2 (Tabelas 4–5 e Figuras 16–17).",
    )
    add_picture_fit(s, FIG_DIR / "fig_balanceamento_macro_f1.png", 0.42, 0.94, 7.15, 2.85)
    add_picture_fit(s, FIG_DIR / "fig_balanceamento_tempo_treino.png", 0.42, 3.88, 7.15, 2.85)

    add_styled_table(
        s, 7.72, 0.96, 5.15, 1.75,
        ["Modo", "Média", "Mediana", "Tempo"],
        [
            ["all_raw", "82,464%", "92,010%", "22,46 h"],
            ["oversample", "82,455%", "91,851%", "25,85 h"],
            ["class_weight", "81,646%", "91,467%", "24,64 h"],
            ["undersample", "78,469%", "88,057%", "15,90 h"],
        ],
        col_widths=[1.75, 1.15, 1.20, 1.05],
        alignments=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT],
        font_size=10.5, header_font_size=11, bold_rows={0},
    )
    add_card(
        s, 7.72, 3.36, 5.15, 3.34,
        "Triagem (CNN orig., mixed_fp16, lote 512)",
        items=[
            [("all_raw: ", True, False, OK_GREEN), ("maior média e mediana sem sobrecarga artificial (2.486 épocas, 88,86 h totais)", False, False, TEXT_DARK)],
            [("undersample: ", True, False, BAD_RED), ("colapso em FER2013 (−19,28 p.p.) e GTSRB (−13,69 p.p.)", False, False, TEXT_DARK)],
            [("class_weight: ", True, False, BAD_RED), ("−6,12 p.p. no FER2013; idêntico ao all_raw nas 5 bases equilibradas", False, False, TEXT_DARK)],
            [("oversample: ", True, False, SENAC_ORANGE), ("+15,1% de tempo (GTSRB 9,90 h vs. 5,20 h) e −1,26 p.p. no CIFAR-10", False, False, TEXT_DARK)],
        ],
        font_size=11.5, title_size=13,
    )

    # ---------------------------------------------------------------
    # 25. PRÉ-PROCESSAMENTO E AUDITORIA DE INTEGRIDADE
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Pré-processamento e auditoria de integridade das partições",
        lbl(25),
        "TCC, Seção 3.4.3 (Auditoria de integridade entre partições).",
    )
    add_card(
        s, 0.50, 1.15, 5.95, 5.20,
        "Padronização idêntica entre modelos",
        items=[
            "Tensores em ponto flutuante, normalização por canal e política all_raw",
            "Redimensionamento proporcional (resize_with_pad) para 64×64 (128×128 no GTSRB)",
            "Partição estratificada fixa (70/15/15) compartilhada pelos 8 modelos de cada base",
            "Rastreamento por hashes SHA-256 e impressões digitais das partições",
        ],
        font_size=14, title_size=15,
    )
    add_card(
        s, 6.85, 1.15, 5.95, 5.20,
        "Limitações auditadas: GTSRB e FER2013",
        items=[
            [("GTSRB: ", True, False, BAD_RED), ("3.990 das 5.876 imagens de teste (67,9%) compartilham a mesma sequência física (track) com o treino; exige divisão track-aware futura", False, False, TEXT_DARK)],
            [("FER2013: ", True, False, BAD_RED), ("378 duplicatas exatas no teste (7,02%), 403 na validação e 57 grupos com conflito de rótulo", False, False, TEXT_DARK)],
            "EMNIST Balanced (1) e CIFAR-100 Coarse (7) têm sobreposições pontuais; 5 bases restantes estão livres de cópias exatas",
        ],
        alert=True, font_size=14, title_size=15,
    )

    # ---------------------------------------------------------------
    # 26. TRÊS FAMÍLIAS DE MODELOS
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Três famílias de modelos comparadas", lbl(26), "TCC, Seção 3.5.")
    add_card(
        s, 0.50, 1.15, 3.92, 4.55,
        "CNN original",
        body_text=[
            "5 blocos SeparableConv2D (32→48→64→96→128), GroupNormalization(16), SiLU e MaxPooling2D(2×2).",
            "Cabeça GAP+GMP → 256 → 256 → K.",
            [("Extrator: ", True, False, SENAC_BLUE), ("66.905 (C=1) ou 67.019 (C=3) pesos.", False, False, TEXT_DARK)],
        ],
        font_size=13.5, title_size=15,
    )
    add_card(
        s, 4.70, 1.15, 3.92, 4.55,
        "Dense20 (img. e vet.)",
        body_text=[
            "Extrator congelado (features128): D20 imagem (LayerNorm+ReLU) e Dense20 vetorial (128 → 20 tanh → K).",
            [("Controle: ", True, False, SENAC_BLUE), ("isola o efeito da compressão para o gargalo clássico de 20 dimensões.", False, False, TEXT_DARK)],
        ],
        font_size=13.5, title_size=15,
    )
    add_card(
        s, 8.90, 1.15, 3.92, 4.55,
        "Híbrido 4×5 qubits",
        body_text=[
            "Mesma projeção Dense(128, ReLU) → Dense(20, linear) sobre features128, processada por 4 PQCs de 5 qubits e camada linear final.",
            "Simulação local em PennyLane e Qiskit Aer (Windows e macOS).",
        ],
        font_size=13.5, title_size=15,
    )
    add_textbox(
        s, 0.50, 6.00, 12.33, 0.45,
        "Total auditado: 72 checkpoints = 9 bases × 8 configurações",
        font_size=16, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER,
    )

    # ---------------------------------------------------------------
    # 27. ARQUITETURA CLÁSSICA (FIGURA SEPARADA 1)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Arquitetura clássica: origem comum e três fluxos",
        lbl(27),
        "TCC, Seção 3.5 (Figura 18; especificações de model_summary.txt).",
    )
    add_picture_fit(s, FIG_DIR / "fig_arquitetura_classica_fluxos.png", 0.55, 0.98, 12.23, 5.72)

    # ---------------------------------------------------------------
    # 28. CABEÇA HÍBRIDA (FIGURA SEPARADA 2)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Cabeça híbrida: 4 circuitos independentes de 5 qubits (Pauli-Y)",
        lbl(28),
        "TCC, Seção 3.5 (Figura 22; especificações de model_summary.txt e circuit.txt).",
    )
    add_picture_fit(s, FIG_DIR / "fig_arquitetura_hibrida_4x5_qubits.png", 0.70, 0.95, 11.93, 4.15)
    tb = add_textbox(s, 0.65, 5.22, 12.03, 1.48)
    add_rich_paragraphs(
        tb.text_frame,
        [
            [("Sem emaranhamento cruzado: ", True, False, SENAC_BLUE), ("4×5 qubits (2⁵ = 32 estados/ramo); codificação R_X(u) + 3 blocos R_Z–R_Y–R_Z e CNOT circular + medição Pauli-Y (⟨Y⟩ ∈ [−1, 1]²⁰)", False, False, TEXT_DARK)],
            [("Parâmetros e custo: ", True, False, SENAC_BLUE), ("45 pesos/ramo = 180 quânticos (19.272 + 21K treináveis; 19.482 para K=10); 404 avaliações lógicas/amostra no treino e 4 na validação", False, False, TEXT_DARK)],
        ],
        font_size=13, space_after=6,
    )

    # ---------------------------------------------------------------
    # 29. PROTOCOLO EXPERIMENTAL
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Protocolo experimental e critérios de avaliação", lbl(29), "TCC, Seção 3.6.")
    add_card(
        s, 0.50, 1.15, 6.05, 5.25,
        "Regime de treinamento (seed=42)",
        items=[
            "72 checkpoints (9 bases × 8 configurações), 100 épocas completas",
            "Otimizador Adam (η = 3×10⁻⁴, escalonamento cosseno + aquecimento)",
            "Seleção pelo melhor Macro-F1 de validação; avaliação final no teste interno (all_raw)",
            "Imagens: label smoothing 0,05 (lote 32/64/128); features128: entropia cruzada padrão (lote 128)",
        ],
        font_size=13.5, title_size=15,
    )
    add_card(
        s, 6.80, 1.15, 6.00, 1.75,
        "Métrica primária",
        body_text="Macro-F1 de teste (%) e Δ pareado em pontos percentuais (p.p.).",
        font_size=14.5, title_size=14.5,
    )
    add_card(
        s, 6.80, 3.15, 6.00, 3.25,
        "Critérios de auditoria",
        items=[
            "Convergência estável acima do acaso (1/K)",
            "Magnitude das diferenças frente ao controle Dense20",
            "Calibração (ECE/NLL/Brier), incerteza bayesiana, oclusão 8×8, gradientes/ruído e telemetria",
        ],
        font_size=13.5, title_size=14.5,
    )

    # ---------------------------------------------------------------
    # 30. AMBIENTES COMPUTACIONAIS E VERSÕES AUDITADAS (TABELAS NATIVAS)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Dois ambientes computacionais e versões auditadas",
        lbl(30),
        "TCC, Seção 3.7 (Tabelas 6 e 7: especificações completas das duas máquinas físicas).",
    )
    add_textbox(s, 0.45, 0.92, 6.10, 0.32, "Ambiente 1 — Estação Windows / WSL2 (Ubuntu 22.04.5 LTS)", font_size=12.5, bold=True, color=SENAC_BLUE)
    add_styled_table(
        s, 0.45, 1.24, 6.10, 5.42,
        ["Componente", "Configuração / Versão"],
        [
            ["SO / Kernel", "Ubuntu 22.04.5 LTS (WSL2), Kernel 6.18.33.2-microsoft-standard-WSL2 (x86-64); PQC em Windows nativo"],
            ["CPU", "Intel Core i7-14700K (28 lógicos; 14 núcleos por soquete no WSL)"],
            ["Memória", "≈ 15 GiB disponíveis ao WSL + 4 GiB de swap"],
            ["GPU / CUDA", "NVIDIA RTX A2000 12GB; Driver 596.51; nvidia-smi 595.76 (CUDA 13.2)"],
            ["DL e dados", "TensorFlow 2.21.0, Keras 3.12.4, NumPy 2.2.6, SciPy 1.15.3, scikit-learn 1.7.2, pandas 2.3.3"],
            ["Visualização / Tel.", "Matplotlib 3.10.9, Pillow 11.3.0, PyYAML 6.0.3, psutil 7.2.2, nvidia-ml-py 12.575.51"],
        ],
        col_widths=[1.75, 4.35],
        font_size=10.5, header_font_size=11,
    )

    add_textbox(s, 6.78, 0.92, 6.10, 0.32, "Ambiente 2 — iMac Mac16,3 (Apple Silicon M4)", font_size=12.5, bold=True, color=SENAC_BLUE)
    add_styled_table(
        s, 6.78, 1.24, 6.10, 5.42,
        ["Item", "Estado / Versão observada"],
        [
            ["Máquina / SO", "iMac Mac16,3, macOS 15.5 (ARM64; Metal suportado pelo hardware)"],
            ["Chip / Memória", "Apple M4 (10 núcleos de GPU integrados), 16 GB de memória unificada"],
            ["Python / .venv", "Sistema 3.9.6 (incompatível); .venv/ com CPython 3.12.3 (.python-version), 76 pacotes via uv pip check"],
            ["Ferramentas", "Xcode/clang ARM64 disponível; ≈ 230 GiB livres em disco"],
            ["DL", "TensorFlow 2.18.1, tensorflow-metal 1.2.0, PyTorch 2.8.0"],
            ["Quântico / Tel.", "PennyLane 0.44.1, Qiskit 2.3.0, Qiskit Aer 0.17.2 (telemetria CPU/RSS)"],
        ],
        col_widths=[1.75, 4.35],
        font_size=10.5, header_font_size=11,
    )

    # ---------------------------------------------------------------
    # 31. TABELA MACRO-F1 (NATIVA)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Macro-F1 de teste (%) nas nove bases", lbl(31), "TCC, Tabela 8 (Seção 4.1), campanha de 30/10/2026.")
    add_styled_table(
        s, 0.55, 1.05, 12.23, 5.00,
        ["Base", "CNN orig.", "Dense20", "Híbrido", "Δ Híb.−CNN", "Δ Híb.−Dense20"],
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
        col_widths=[2.73, 1.75, 1.75, 1.75, 2.00, 2.25],
        alignments=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT],
        font_size=12, header_font_size=12.5,
    )
    add_textbox(
        s, 0.55, 6.20, 12.23, 0.45,
        "*GTSRB: teste com sobreposição de tracks (3.990 de 5.876); não é o teste oficial. Dense20 e Híbrido referem-se à execução Mac.",
        font_size=11, color=TEXT_MUTED, align=PP_ALIGN.CENTER,
    )

    # ---------------------------------------------------------------
    # 32. GRÁFICO DOS DELTAS (GRÁFICO NATIVO DE POWERPOINT)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Quanto o híbrido difere? (Δ em pontos percentuais)",
        lbl(32),
        "Elaborado pelo autor a partir da Tabela 8 do TCC (Seção 4.1); médias calculadas sobre os nove Δ.",
    )
    chart_data = CategoryChartData()
    chart_data.categories = ["MNIST", "F-MNIST", "KMNIST", "EMNIST", "CIFAR-10", "CIFAR-100C", "SVHN", "GTSRB", "FER2013"]
    chart_data.add_series("Híbrido − CNN original", (0.321, -0.021, -0.001, 0.755, 0.203, -0.341, 0.546, 0.225, 0.361))
    chart_data.add_series("Híbrido − Dense20", (0.080, -0.156, 0.000, -0.168, -0.069, -0.442, 0.067, -0.043, 0.620))

    ch_shape = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.65), Inches(0.95), Inches(12.0), Inches(5.15), chart_data)
    chart = ch_shape.chart
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.TOP
    chart.legend.include_in_layout = False
    chart.legend.font.name = FONT_NAME
    chart.legend.font.size = Pt(12)
    plot = chart.plots[0]
    plot.gap_width = 120
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
    va.tick_labels.font.size = Pt(11)
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RGBColor(218, 224, 232)
    ca = chart.category_axis
    ca.tick_label_position = XL_TICK_LABEL_POSITION.LOW
    ca.tick_labels.font.name = FONT_NAME
    ca.tick_labels.font.size = Pt(11)

    add_textbox(
        s, 0.65, 6.20, 12.0, 0.45,
        "Frente à CNN: média +0,23 p.p.; frente ao Dense20: média −0,01 p.p. (híbrido melhor em apenas 3 de 9; KMNIST empata).",
        font_size=14, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER,
    )

    # ---------------------------------------------------------------
    # 33. PAPEL DO CONTROLE Dense20
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "O papel do controle Dense20", lbl(33), "TCC, Seção 4.2–4.3.")
    add_card(
        s, 0.55, 1.15, 5.95, 3.30,
        "Sem o controle, haveria 'ganhos'",
        body_text="Híbrido − CNN: EMNIST +0,755 p.p., SVHN +0,546 p.p., MNIST +0,321 p.p., GTSRB +0,225 p.p., CIFAR-10 +0,203 p.p.",
        alert=True, font_size=15, title_size=15,
    )
    add_card(
        s, 6.82, 1.15, 5.95, 3.30,
        "Com o controle, o ganho some",
        body_text="O Dense20 já explica a maior parte: EMNIST 88,642 (vs. 88,474), CIFAR-10 73,389 (vs. 73,320), GTSRB 99,633 (vs. 99,590). KMNIST: idêntico (98,648).",
        font_size=15, title_size=15,
    )
    tb = add_textbox(s, 0.55, 4.75, 12.23, 1.75)
    add_rich_paragraphs(
        tb.text_frame,
        [
            [("O efeito vem da ", False, False, TEXT_DARK), ("projeção vetorial de 20 dimensões", True, False, SENAC_BLUE), (", não do circuito quântico", False, False, TEXT_DARK)],
            [("Limite: parametrização e não linearidades distintas e ", False, False, TEXT_DARK), ("uma semente", True, False, TEXT_DARK), (" ⇒ diferenças de décimos de p.p. não provam vantagem nem desvantagem quântica", False, False, TEXT_DARK)],
        ],
        font_size=15, space_after=10,
    )

    # ---------------------------------------------------------------
    # 34. COMPLEXIDADE SEMÂNTICA (GRÁFICO NATIVO HORIZONTAL)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Complexidade do domínio governa o desempenho",
        lbl(34),
        "Elaborado pelo autor a partir da Tabela 8 do TCC (Seção 4.1); análise em Seção 4.2.",
    )
    cd34 = CategoryChartData()
    cd34.categories = ["FER2013", "CIFAR-100 Coarse", "CIFAR-10", "Fashion-MNIST", "SVHN", "KMNIST", "MNIST"]
    cd34.add_series("Macro-F1 do híbrido (%)", (48.5, 47.1, 73.3, 91.9, 92.6, 98.6, 99.3))
    ch34 = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.85), Inches(1.00), Inches(11.6), Inches(4.25), cd34).chart
    ch34.has_legend = False
    p34 = ch34.plots[0]
    p34.has_data_labels = True
    p34.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    p34.data_labels.font.name = FONT_NAME
    p34.data_labels.font.size = Pt(11)
    p34.series[0].format.fill.solid()
    p34.series[0].format.fill.fore_color.rgb = SENAC_BLUE
    ch34.value_axis.minimum_scale = 0
    ch34.value_axis.maximum_scale = 115
    ch34.value_axis.major_gridlines.format.line.color.rgb = RGBColor(218, 224, 232)
    ch34.value_axis.tick_labels.font.name = FONT_NAME
    ch34.value_axis.tick_labels.font.size = Pt(10.5)
    ch34.category_axis.tick_labels.font.name = FONT_NAME
    ch34.category_axis.tick_labels.font.size = Pt(11.5)

    tb = add_textbox(s, 0.85, 5.38, 11.6, 1.35)
    add_rich_paragraphs(
        tb.text_frame,
        [
            [("CIFAR-100 Coarse: ", True, False, SENAC_BLUE), ("20 superclasses, cada uma com 5 classes finas visualmente distintas; CNN compacta capta só parte", False, False, TEXT_DARK)],
            [("FER2013: ", True, False, SENAC_BLUE), ("forte desbalanceamento ('desgosto') penaliza o Macro-F1, mais ainda frente à acurácia da literatura (ex.: 73,78%)", False, False, TEXT_DARK)],
        ],
        font_size=13.5, space_after=6,
    )

    # ---------------------------------------------------------------
    # 35. GTSRB: INTERPRETAÇÃO CAUTELOSA
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "GTSRB: números altos, interpretação cautelosa", lbl(35), "TCC, Seções 3.4.3 e 4.1.")
    left_box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.65), Inches(1.55), Inches(5.15), Inches(4.25))
    left_box.adjustments[0] = 0.06
    left_box.fill.solid()
    left_box.fill.fore_color.rgb = SENAC_BLUE_LIGHT
    left_box.line.color.rgb = SENAC_BLUE
    ltf = left_box.text_frame
    ltf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for idx, line in enumerate(["99,365%   CNN", "99,633%   Dense20", "99,590%   Híbrido"]):
        p = ltf.paragraphs[0] if idx == 0 else ltf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.space_after = Pt(18)
        r = p.add_run()
        r.text = line
        r.font.name = FONT_NAME
        r.font.size = Pt(24)
        r.font.bold = True
        r.font.color.rgb = SENAC_BLUE

    add_card(
        s, 6.25, 1.55, 6.45, 2.50,
        "Por quê?",
        body_text="3.990 de 5.876 imagens de teste (67,9%) vêm de tracks já vistos no treino: quadros correlacionados facilitam o acerto.",
        alert=True, font_size=15, title_size=15.5,
    )
    add_textbox(
        s, 6.25, 4.35, 6.45, 1.35,
        "Os números demonstram consistência interna das três arquiteturas, não generalização para placas inéditas.",
        font_size=15.5, bold=True, color=TEXT_DARK,
    )

    # ---------------------------------------------------------------
    # 36. EXPLICABILIDADE GLOBAL (73.728 OCLUSÕES)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Explicabilidade espacial: Grad-CAM vs. oclusão 8×8", lbl(36), "TCC, Seção 4.7 (Figura 32).")
    add_picture_fit(s, FIG_DIR / "fig_oclusao_trocas_globais.png", 0.90, 0.96, 11.53, 4.20)
    tb = add_textbox(s, 0.70, 5.26, 11.93, 1.48)
    add_rich_paragraphs(
        tb.text_frame,
        [
            [("73.728 oclusões ", True, False, SENAC_BLUE), ("(9 bases × 8 imagens × 8 modelos × 64 blocos × 2 métodos): média constante provoca mais trocas que borramento (pico de 23,4% no CIFAR-100 Coarse)", False, False, TEXT_DARK)],
            [("Mediana Spearman Grad-CAM vs. oclusão: ", True, False, SENAC_BLUE), ("ρ = 0,002 — mapas em camadas profundas não equivalem à sensibilidade causal da entrada", False, False, TEXT_DARK)],
        ],
        font_size=13.5, space_after=6,
    )

    # ---------------------------------------------------------------
    # 37. PAINÉIS CAUSAIS DE OCLUSÃO — RGB
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Painéis causais de oclusão: RGB (gtsrb_07 e cifar100_coarse_01)",
        lbl(37),
        "TCC, Seção 4.7 (Figuras 33 e 36; suíte completa em dist/paineis).",
    )
    add_picture_fit(s, FIG_DIR / "painel_oclusao_gtsrb_07_media.png", 0.50, 0.94, 5.95, 4.85)
    add_textbox(
        s, 0.50, 5.84, 5.95, 0.95,
        "gtsrb_07_media (cl. 3): CNN e Vet. acertam cl. 3 (3–6/64 trocas); D20 img. prevê cl. 25 (13/64); Híbridos preveem cl. 10 (10–15/64, queda até +9,02).",
        font_size=11.5, color=TEXT_DARK, align=PP_ALIGN.CENTER,
    )
    add_picture_fit(s, FIG_DIR / "painel_oclusao_cifar100_coarse_01_desfoque.png", 6.85, 0.94, 5.95, 4.85)
    add_textbox(
        s, 6.85, 5.84, 5.95, 0.95,
        "cifar100_coarse_01_desfoque (insects): 8 modelos acertam; CNN/Vet. 0/64 trocas; D20 img. 2/64; Híbridos 3/64 para flowers (+1,51).",
        font_size=11.5, color=TEXT_DARK, align=PP_ALIGN.CENTER,
    )

    # ---------------------------------------------------------------
    # 38. PAINÉIS CAUSAIS DE OCLUSÃO — MONOCROMÁTICOS
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Painéis causais de oclusão: monocromáticos (fashion_mnist_06 e mnist_06)",
        lbl(38),
        "TCC, Seção 4.7 (Figuras 34 e 35; suíte completa em dist/paineis).",
    )
    add_picture_fit(s, FIG_DIR / "painel_oclusao_fashion_mnist_06_media.png", 0.50, 0.94, 5.95, 4.85)
    add_textbox(
        s, 0.50, 5.84, 5.95, 0.95,
        "fashion_mnist_06_media (cl. 2, pulôver): CNN e Vet. acertam cl. 2 (23–26/64 trocas); D20 img. e híbridos preveem cl. 6 (16 e 31/64 trocas).",
        font_size=11.5, color=TEXT_DARK, align=PP_ALIGN.CENTER,
    )
    add_picture_fit(s, FIG_DIR / "painel_oclusao_mnist_06_desfoque.png", 6.85, 0.94, 5.95, 4.85)
    add_textbox(
        s, 6.85, 5.84, 5.95, 0.95,
        "mnist_06_desfoque (dígito '2'): só D20 img. acerta cl. 2 (17/64, +1,83); CNN, Vet. e híbridos preveem '7' (5–8/64, até +10,46).",
        font_size=11.5, color=TEXT_DARK, align=PP_ALIGN.CENTER,
    )

    # ---------------------------------------------------------------
    # 39. CUSTO COMPUTACIONAL E TELEMETRIA
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(
        s,
        "Custo computacional: simulação quântica vs. controle vetorial",
        lbl(39),
        "TCC, Seção 4.8 (telemetria das 100 épocas em lote 128).",
    )
    add_picture_fit(s, FIG_DIR / "fig_tempos_100_epocas_comparativo.png", 0.45, 0.96, 8.15, 5.75)
    add_card(
        s, 8.75, 1.15, 4.10, 5.20,
        "Gargalo operacional (100 épocas)",
        items=[
            [("36 híbridos: ", True, False, BAD_RED), ("503,66 h (20,99 dias) vs. 18 vetoriais: 558,88 s (9,31 min) — 778× a 2.854× mais caro", False, False, TEXT_DARK)],
            [("Pico absoluto: ", True, False, SENAC_BLUE), ("EMNIST no Win/Qiskit = 54,93 h (>30× a CNN completa em lote 128, 1,65 h)", False, False, TEXT_DARK)],
            [("iMac M4 vs. Windows: ", True, False, OK_GREEN), ("1,43×–3,18× mais rápido no PennyLane (55,17 vs. 100,39 h)", False, False, TEXT_DARK)],
            [("PennyLane vs. Qiskit: ", True, False, OK_GREEN), ("2,64×–2,74× mais rápido no Mac", False, False, TEXT_DARK)],
        ],
        font_size=12.5, title_size=14,
    )

    # ---------------------------------------------------------------
    # 40. SÍNTESE
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Síntese: o que a hipótese e os dados dizem", lbl(40), "TCC, Seções 4.1–4.3 e 2.8.2.")
    synth_rows = [
        ("✓", OK_GREEN, "Híbrido converge de forma estável nas 9 bases, inclusive com 20, 43 e 47 classes"),
        ("✓", OK_GREEN, "Macro-F1 competitivo: Híb. − Dense20 entre −0,442 e +0,620 p.p."),
        ("✓", OK_GREEN, "Sem superioridade quântica: o ganho sobre a CNN vem do gargalo clássico"),
        ("✗", BAD_RED, "Sem atribuição causal: semente única e cabeças com parametrização distinta"),
    ]
    for idx, (sym, scol, stxt) in enumerate(synth_rows):
        ry = 1.15 + idx * 0.85
        tb = add_textbox(s, 0.70, ry, 11.9, 0.65)
        p = tb.text_frame.paragraphs[0]
        r_s = p.add_run()
        r_s.text = f"{sym}   "
        r_s.font.name = FONT_NAME
        r_s.font.size = Pt(18)
        r_s.font.bold = True
        r_s.font.color.rgb = scol
        r_t = p.add_run()
        r_t.text = stxt
        r_t.font.name = FONT_NAME
        r_t.font.size = Pt(16)
        r_t.font.color.rgb = TEXT_DARK

    add_card(
        s, 0.70, 4.75, 11.9, 1.70,
        "Comparação com a literatura",
        body_text="Com extrator convolucional, o híbrido preserva a capacidade discriminativa onde o NNQE (filtro fixo + camada densa) obteve 36,0% no CIFAR-10 e 73,4% no GTSRB.",
        font_size=15, title_size=15,
    )

    # ---------------------------------------------------------------
    # 41. RETOMADA DO PROBLEMA E OBJETIVOS
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Retomada do problema e dos objetivos", lbl(41), "TCC, Seção 5.1.")
    tb = add_textbox(s, 0.70, 1.35, 11.9, 4.90)
    add_rich_paragraphs(
        tb.text_frame,
        [
            [("Estudo comparativo em ", False, False, TEXT_DARK), ("9 bases", True, False, SENAC_BLUE), (", ", False, False, TEXT_DARK), ("72 checkpoints", True, False, SENAC_BLUE), (", avaliado por Macro-F1", False, False, TEXT_DARK)],
            "Revisão orientada por base: 19 registros clássicos e 9 quânticos/híbridos, além de candidatos adicionais",
            [("Resposta à pergunta de pesquisa: ", True, False, SENAC_BLUE), ("o híbrido (4×5 qubits, simulado) é estável e apresenta paridade aproximada com CNN e Dense20", False, False, TEXT_DARK)],
            [("Sem vantagem quântica irrestrita: ", True, False, SENAC_BLUE), ("sem o controle Dense20, ganhos aparentes seriam falsos positivos", False, False, TEXT_DARK)],
        ],
        font_size=16.5, space_after=16,
    )

    # ---------------------------------------------------------------
    # 42. CONTRIBUIÇÕES PARA A COMPUTAÇÃO
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Contribuições para a Computação", lbl(42), "TCC, Seção 5.2.")
    tb = add_textbox(s, 0.70, 1.25, 11.9, 5.10)
    add_rich_paragraphs(
        tb.text_frame,
        [
            [("Protocolo e revisão multi-dataset ", True, False, SENAC_BLUE), ("em 9 bases completas (7 a 47 classes), com cobertura empírica do CIFAR-100 Coarse, sem estudo quântico prévio identificado", False, False, TEXT_DARK)],
            [("Controle Dense20: ", True, False, SENAC_BLUE), ("evita falsos ganhos arquiteturais (ex.: +0,755 p.p. no EMNIST)", False, False, TEXT_DARK)],
            [("Viabilização por decomposição ", True, False, SENAC_BLUE), ("em 4 subcircuitos de 5 qubits: simulação tratável em PennyLane/PyTorch e Qiskit Aer", False, False, TEXT_DARK)],
            [("Auditoria crítica ", True, False, SENAC_BLUE), ("de artefatos e da literatura (resultados em validação, lotes assimétricos, partição do GTSRB e duplicatas no FER2013)", False, False, TEXT_DARK)],
        ],
        font_size=16, space_after=16, bullet=False, numbered=True,
    )

    # ---------------------------------------------------------------
    # 43. LIMITAÇÕES E TRABALHOS FUTUROS (TABELA NATIVA)
    # ---------------------------------------------------------------
    s = new_slide(prs)
    add_chrome(s, "Limitações e trabalhos futuros", lbl(43), "TCC, Seção 5.3.")
    add_styled_table(
        s, 0.55, 1.25, 12.23, 4.95,
        ["Limitação", "Trabalho futuro"],
        [
            ["Uma semente por configuração", "5 a 10 sementes: intervalos de confiança e testes de significância"],
            ["GTSRB com sobreposição de tracks", "Divisão agrupada track-aware no pré-processamento"],
            ["Sem emaranhamento entre subcircuitos", "Emaranhar os blocos; aceleração GPU (Qiskit Aer/cuQuantum); data re-uploading"],
            ["Dense20 sem paridade de parâmetros", "Parear exatamente parâmetros, ativação e temperatura com a cabeça quântica"],
            ["Apenas simulação ideal", "Modelos de ruído NISQ no treinamento e validação em QPUs reais"],
        ],
        col_widths=[5.40, 6.83],
        alignments=[PP_ALIGN.LEFT, PP_ALIGN.LEFT],
        font_size=14, header_font_size=14.5,
    )

    # ---------------------------------------------------------------
    # 44. OBRIGADO
    # ---------------------------------------------------------------
    s = new_slide(prs)
    top_bar2 = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_W, Inches(0.14))
    top_bar2.fill.solid()
    top_bar2.fill.fore_color.rgb = SENAC_BLUE
    top_bar2.line.fill.background()

    if LOGO_PATH.exists():
        add_picture_fit(s, LOGO_PATH, 5.4, 0.95, 2.5, 1.85)
    add_textbox(s, 1.5, 3.25, 10.33, 0.70, "Obrigado!", font_size=34, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER)
    add_textbox(s, 1.5, 4.05, 10.33, 0.50, "Perguntas?", font_size=20, color=SENAC_ORANGE, bold=True, align=PP_ALIGN.CENTER)
    add_textbox(s, 1.5, 5.05, 10.33, 0.45, "Matheus Sanchez Duda", font_size=16, bold=True, color=TEXT_DARK, align=PP_ALIGN.CENTER)
    add_textbox(
        s, 1.2, 5.55, 10.93, 0.45,
        "Orientador: Prof. Samuel Mendes Sanches Junior   |   Coorientador: Prof. Thyago Conchado Quintas",
        font_size=12.5, color=TEXT_MUTED, align=PP_ALIGN.CENTER,
    )

    # ---------------------------------------------------------------
    # APÊNDICE (A1..A7)
    # ---------------------------------------------------------------
    # A1
    s = new_slide(prs)
    add_chrome(s, "Apoio A1: sobreamostragem e subamostragem", "A1", "TCC, Seção 3.4.1; adaptado de Silva (2025).")
    add_picture_fit(s, FIG_DIR / "balanceamento_oversampling_silva2025.png", 0.55, 1.10, 5.95, 3.40)
    add_textbox(s, 0.55, 4.55, 5.95, 0.35, "Sobreamostragem (oversampling)", font_size=13.5, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER)
    add_picture_fit(s, FIG_DIR / "balanceamento_undersampling_silva2025.png", 6.80, 1.10, 5.95, 3.40)
    add_textbox(s, 6.80, 4.55, 5.95, 0.35, "Subamostragem (undersampling)", font_size=13.5, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER)
    tb = add_textbox(s, 0.70, 5.10, 11.9, 1.40)
    add_rich_paragraphs(
        tb.text_frame,
        [
            "Estratégias de nível de dados e de algoritmo (perda ponderada class_weight) avaliadas na Seção 3.4",
            "Validação e teste mantêm sempre a distribuição original; avaliação primária por Macro-F1",
        ],
        font_size=14, space_after=8,
    )

    # A2
    s = new_slide(prs)
    add_chrome(s, "Apoio A2: calibração probabilística e confiança nos erros (FER2013)", "A2", "TCC, Seção 4.5 (Figura 29).")
    add_picture_fit(s, FIG_DIR / "figura_28_calibracao_fer.png", 0.50, 1.00, 7.25, 5.65)
    add_card(
        s, 7.95, 1.15, 4.88, 5.20,
        "Trade-off de calibração no FER2013",
        items=[
            [("CNN FP32 (label smoothing 0,05): ", True, False, OK_GREEN), ("melhor calibração (ECE=2,08%, NLL=1,281, conf. erros 42,76%)", False, False, TEXT_DARK)],
            [("D20 imagem: ", True, False, SENAC_BLUE), ("ECE=18,38%, conf. nos erros 60,47%", False, False, TEXT_DARK)],
            [("Vet. Mac: ", True, False, SENAC_BLUE), ("ECE=31,43%, conf. nos erros 75,45%", False, False, TEXT_DARK)],
            [("PQC Mac PL: ", True, False, BAD_RED), ("maior Macro-F1 (48,519%), porém ECE=36,62%, NLL=2,497 e 82,82% de confiança nos erros (requer temperature scaling)", False, False, TEXT_DARK)],
        ],
        font_size=13, title_size=14,
    )

    # A3
    s = new_slide(prs)
    add_chrome(s, "Apoio A3: diagnósticos quânticos (gradientes por ramo e ruído/shots)", "A3", "TCC, Seção 4.6 (Figuras 30 e 31).")
    add_picture_fit(s, FIG_DIR / "figura_19_gradientes.png", 0.50, 1.00, 6.00, 4.30)
    add_textbox(
        s, 0.50, 5.42, 6.00, 1.10,
        "Normas de gradiente (Ramos 1–4): MNIST decai naturalmente (0,13 → 10⁻⁷); FER2013 segue ativo (4,3×10⁻² a 1,1×10⁻¹) até a época 100.",
        font_size=12.5, color=TEXT_DARK, align=PP_ALIGN.CENTER,
    )
    add_picture_fit(s, FIG_DIR / "figura_22_ruido_shots.png", 6.80, 1.00, 6.00, 4.30)
    add_textbox(
        s, 6.80, 5.42, 6.00, 1.10,
        "Ruído e shots (Mac/PL): fidelidade cai a 0,51 (ruído 2,0), mas Δ Macro-F1 típico <0,10 p.p. (máx. −0,38 p.p. no CIFAR-10).",
        font_size=12.5, color=TEXT_DARK, align=PP_ALIGN.CENTER,
    )

    # A4
    s = new_slide(prs)
    add_chrome(s, "Apoio A4: aceleração Windows vs. Mac e telemetria", "A4", "TCC, Seção 4.8.")
    add_picture_fit(s, FIG_DIR / "fig_fatores_aceleracao_ambientes_simuladores.png", 0.45, 0.98, 8.15, 5.65)
    add_card(
        s, 8.75, 1.15, 4.10, 5.20,
        "Speedups e telemetria Mac/PL",
        items=[
            [("Aceleração iMac M4: ", True, False, OK_GREEN), ("1,43×–3,18× mais rápido que Windows no PennyLane e 1,07×–1,79× no Qiskit", False, False, TEXT_DARK)],
            [("Aceleração PennyLane: ", True, False, OK_GREEN), ("2,64×–2,74× mais rápido que Qiskit no Mac", False, False, TEXT_DARK)],
            [("Telemetria Mac/PL: ", True, False, SENAC_BLUE), ("uso estável de 383,9%–385,0% de CPU (≈4 núcleos) e pico de RAM residente (RSS) entre 2,40 e 3,28 GiB", False, False, TEXT_DARK)],
        ],
        font_size=13.5, title_size=14,
    )

    # A5
    s = new_slide(prs)
    add_chrome(s, "Apoio A5: generalidade do operador convolucional", "A5", "TCC, Seção 2.5.2.")
    add_picture_fit(s, FIG_DIR / "2plus1CNN-converted.png", 2.3, 1.05, 8.7, 4.35)
    add_textbox(
        s, 0.90, 5.65, 11.53, 0.85,
        "Convolução (2+1)D separa dimensões espacial e temporal; as nove bases deste trabalho são imagens estáticas 2D.",
        font_size=15, color=TEXT_DARK, align=PP_ALIGN.CENTER,
    )

    # A6
    s = new_slide(prs)
    add_chrome(s, "Apoio A6: riscos e limitações metodológicas", "A6", "TCC, Seção 3.8.")
    tb = add_textbox(s, 0.70, 1.25, 11.9, 5.10)
    add_rich_paragraphs(
        tb.text_frame,
        [
            "Sem emaranhamento entre os quatro subcircuitos independentes de 5 qubits",
            "Uma semente por configuração (seed=42): sem testes de significância entre inicializações",
            "Dense20 vs. híbrido: parametrizações e não linearidades distintas, sem isolar efeito puramente quântico",
            "Sobreposição de tracks no GTSRB (3.990 de 5.876 imagens de teste) e duplicatas no FER2013 (378 no teste)",
            "Restrição integral à simulação clássica em CPU local, sem execução em QPU física",
        ],
        font_size=15.5, space_after=14, bullet=False, numbered=True,
    )

    # A7
    s = new_slide(prs)
    add_chrome(s, "Apoio A7: siglas principais", "A7")
    add_styled_table(
        s, 0.55, 1.15, 5.95, 5.10,
        ["Sigla", "Significado"],
        [
            ["CNN", "Rede Neural Convolucional"],
            ["PQC", "Circuito Quântico Parametrizado"],
            ["QML", "Aprendizado de Máquina Quântico"],
            ["NISQ", "Computação Quântica Ruidosa de Escala Intermediária"],
            ["QPU", "Unidade de Processamento Quântico"],
        ],
        col_widths=[1.65, 4.30],
        font_size=13.5, header_font_size=14,
    )
    add_styled_table(
        s, 6.80, 1.15, 5.95, 5.10,
        ["Sigla", "Significado"],
        [
            ["IR", "Razão de Desbalanceamento (n_max / n_min)"],
            ["CV", "Coeficiente de Variação"],
            ["TP/FP/FN/TN", "Verdadeiro/Falso Positivo/Negativo"],
            ["ROC/AUC", "Curva ROC e Área sob a Curva"],
            ["Grad-CAM", "Mapeamento de Ativação de Classe por Gradiente"],
        ],
        col_widths=[1.75, 4.20],
        font_size=13.5, header_font_size=14,
    )

    prs.save(OUTPUT_PPTX)
    print(f"PPTX salvo em: {OUTPUT_PPTX} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    build_deck()
