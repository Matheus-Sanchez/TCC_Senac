"""Gera a apresentacao editavel em PowerPoint (.pptx) revisada e otimizada para leitura.

Diretrizes:
- Fonte minima global de 18 pt nos textos principais (exceto citacoes/fontes em 11 pt,
  rodape discreto em 14 pt, tabelas densas de 9 linhas em 16 pt e subtitulos auxiliares).
- Figuras e GIFs otimizados para apresentacao em figuras/slides/ e figuras/gifs_slides/,
  preservando intactas todas as figuras do TCC escrito (tcc2-adaptado.tex).
- Altura dos cards ajustada automaticamente ao conteudo para eliminar blocos em branco.
"""

from __future__ import annotations

import math
from pathlib import Path
from PIL import Image

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_TICK_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml import parse_xml
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt


BASE_DIR = Path(__file__).resolve().parent
FIG_DIR = BASE_DIR / "figuras"
SLIDE_FIG_DIR = FIG_DIR / "slides"
GIF_DIR = FIG_DIR / "gifs"
GIF_SLIDE_DIR = FIG_DIR / "gifs_slides"
LOGO_PATH = BASE_DIR / "assets" / "logo-senac.png"
OUTPUT_PPTX = BASE_DIR / "apresentacao_tcc2_final.pptx"
OUTPUT_ALT_PPTX = BASE_DIR / "apresentacao_tcc2_final_atualizada.pptx"

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
BAD_RED_LIGHT = RGBColor(253, 236, 236)
TEXT_DARK = RGBColor(24, 30, 38)
TEXT_MUTED = RGBColor(86, 96, 108)
BORDER_GRAY = RGBColor(200, 210, 222)
WHITE = RGBColor(255, 255, 255)


def fpt(size: float, enforce_min: bool = True) -> Pt:
    return Pt(max(MIN_FONT_PT, size) if enforce_min else size)


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
    enforce_min=True,
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
            run.font.size = fpt(font_size, enforce_min=enforce_min)
            run.font.bold = bold
            run.font.italic = italic
            run.font.color.rgb = color
    return tb


def add_rich_paragraphs(
    tf,
    items,
    font_size=18,
    space_after=6,
    bullet=True,
    numbered=False,
    line_spacing=1.08,
    enforce_min=True,
):
    """Popula um text_frame com lista de itens compostos por strings ou tuplas (texto, bold, italic, cor)."""
    tf.word_wrap = True
    sz = max(MIN_FONT_PT, font_size) if enforce_min else font_size
    for idx, entry in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        p.line_spacing = line_spacing
        if bullet:
            r_b = p.add_run()
            r_b.text = "• "
            r_b.font.name = FONT_NAME
            r_b.font.size = fpt(sz, enforce_min=enforce_min)
            r_b.font.bold = True
            r_b.font.color.rgb = SENAC_ORANGE
        elif numbered:
            r_n = p.add_run()
            r_n.text = f"{idx + 1}. "
            r_n.font.name = FONT_NAME
            r_n.font.size = fpt(sz, enforce_min=enforce_min)
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
            r.font.size = fpt(sz, enforce_min=enforce_min)
            r.font.bold = b
            r.font.italic = it
            r.font.color.rgb = col


def _entry_text(entry) -> str:
    if isinstance(entry, str):
        return entry
    return "".join(seg if isinstance(seg, str) else seg[0] for seg in entry)


def estimate_card_height(
    w,
    items=None,
    body_text="",
    font_size=18,
    space_after=6,
    line_spacing=1.08,
    header_h=0.46,
    bullet=True,
    enforce_min=True,
) -> float:
    """Estima altura justa do card em polegadas para evitar blocos vazios."""
    sz = max(MIN_FONT_PT, font_size) if enforce_min else font_size
    tb_w = max(1.0, w - 0.28)
    # Largura media de glifo Calibri (~0.51 * sz / 72 in) com margem conservadora
    cpl = max(12, int(tb_w / (0.51 * sz / 72.0)))
    line_h_in = (sz * line_spacing) / 72.0
    gap_in = space_after / 72.0

    entries = []
    if items is not None:
        entries = list(items)
    elif isinstance(body_text, list):
        entries = list(body_text)
    elif body_text:
        entries = body_text.split("\n")

    total_body_h = 0.0
    for idx, entry in enumerate(entries):
        txt = _entry_text(entry)
        prefix = 2 if (items is not None and bullet) else 0
        sublines = txt.split("\n")
        n_lines = 0
        for s_idx, sub in enumerate(sublines):
            eff_len = len(sub) + (prefix if s_idx == 0 else 0)
            n_lines += max(1, math.ceil(eff_len / cpl))
        total_body_h += n_lines * line_h_in
        if idx < len(entries) - 1:
            total_body_h += gap_in

    return round(header_h + 0.18 + total_body_h + 0.24, 2)


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
    space_after=6,
    line_spacing=1.08,
    auto_height=True,
    center_in=None,
    enforce_min=True,
):
    header_h = 0.46
    final_h = h
    if auto_height:
        needed = estimate_card_height(
            w,
            items=items,
            body_text=body_text,
            font_size=font_size,
            space_after=space_after,
            line_spacing=line_spacing,
            header_h=header_h,
            bullet=(items is not None),
            enforce_min=enforce_min,
        )
        final_h = min(h, max(1.10, needed))

    final_y = y
    if center_in is not None:
        y0, y1 = center_in
        final_y = y0 + max(0.0, (y1 - y0 - final_h) / 2.0)

    header_color = SENAC_ORANGE if alert else SENAC_BLUE
    body_color = SENAC_ORANGE_LIGHT if alert else SENAC_BLUE_LIGHT

    body = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(final_y), Inches(w), Inches(final_h))
    body.adjustments[0] = 0.035
    body.fill.solid()
    body.fill.fore_color.rgb = body_color
    body.line.color.rgb = header_color
    body.line.width = Pt(1.0)

    hdr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(final_y), Inches(w), Inches(header_h))
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
    hr.font.size = fpt(title_size, enforce_min=enforce_min)
    hr.font.bold = True
    hr.font.color.rgb = WHITE

    tb = slide.shapes.add_textbox(
        Inches(x + 0.12),
        Inches(final_y + header_h + 0.06),
        Inches(w - 0.24),
        Inches(max(0.40, final_h - header_h - 0.10)),
    )
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    if items is not None:
        add_rich_paragraphs(
            tf, items, font_size=font_size, space_after=space_after,
            bullet=True, line_spacing=line_spacing, enforce_min=enforce_min,
        )
    elif body_text:
        if isinstance(body_text, list):
            add_rich_paragraphs(
                tf, body_text, font_size=font_size, space_after=space_after,
                bullet=False, line_spacing=line_spacing, enforce_min=enforce_min,
            )
        else:
            p = tf.paragraphs[0]
            p.line_spacing = line_spacing
            r = p.add_run()
            r.text = body_text
            r.font.name = FONT_NAME
            r.font.size = fpt(font_size, enforce_min=enforce_min)
            r.font.color.rgb = TEXT_DARK
    return final_y, final_h


def add_bottom_strip(slide, y, h, cols_items, bg=SENAC_BLUE_LIGHT, border=SENAC_BLUE, font_size=18):
    """Faixa horizontal com colunas lado a lado para substituir blocos altos vazios."""
    strip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.32), Inches(y), Inches(12.69), Inches(h))
    strip.adjustments[0] = 0.06
    strip.fill.solid()
    strip.fill.fore_color.rgb = bg
    strip.line.color.rgb = border
    strip.line.width = Pt(1.0)

    n = len(cols_items)
    gap = 0.18
    col_w = (12.35 - gap * (n - 1)) / n
    for idx, entry in enumerate(cols_items):
        cx = 0.49 + idx * (col_w + gap)
        tb = slide.shapes.add_textbox(Inches(cx), Inches(y + 0.06), Inches(col_w), Inches(h - 0.12))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.02)
        tf.margin_right = Inches(0.02)
        add_rich_paragraphs(tf, [entry], font_size=font_size, space_after=0, bullet=True, line_spacing=1.06)
        if idx < n - 1:
            sep_x = cx + col_w + gap / 2.0
            sep = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(sep_x), Inches(y + 0.14), Inches(0.015), Inches(h - 0.28))
            sep.fill.solid()
            sep.fill.fore_color.rgb = BORDER_GRAY
            sep.line.fill.background()


def add_row_cards(slide, items, y_start=0.96, row_h=1.22, gap=0.16, numbered=False, font_size=18):
    """Renderiza itens estruturados como faixas horizontais equilibradas (estilo Roteiro)."""
    for idx, entry in enumerate(items):
        ry = y_start + idx * (row_h + gap)
        if numbered:
            badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.45), Inches(ry), Inches(0.82), Inches(row_h))
            badge.adjustments[0] = 0.16
            badge.fill.solid()
            badge.fill.fore_color.rgb = SENAC_BLUE
            badge.line.fill.background()
            btf = badge.text_frame
            btf.vertical_anchor = MSO_ANCHOR.MIDDLE
            bp = btf.paragraphs[0]
            bp.alignment = PP_ALIGN.CENTER
            br = bp.add_run()
            br.text = f"{idx + 1}"
            br.font.name = FONT_NAME
            br.font.size = fpt(24)
            br.font.bold = True
            br.font.color.rgb = WHITE
            bx, bw = 1.40, 11.48
        else:
            stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.45), Inches(ry), Inches(0.14), Inches(row_h))
            stripe.fill.solid()
            stripe.fill.fore_color.rgb = SENAC_ORANGE
            stripe.line.fill.background()
            bx, bw = 0.59, 12.29

        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(bx), Inches(ry), Inches(bw), Inches(row_h))
        card.adjustments[0] = 0.05
        card.fill.solid()
        card.fill.fore_color.rgb = SENAC_BLUE_LIGHT
        card.line.color.rgb = BORDER_GRAY
        tf = card.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.16)
        tf.margin_right = Inches(0.14)
        add_rich_paragraphs(tf, [entry], font_size=font_size, space_after=0, bullet=False, line_spacing=1.08)


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
    enforce_min=True,
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
        r.font.size = fpt(header_font_size, enforce_min=enforce_min)
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
            r.font.size = fpt(font_size, enforce_min=enforce_min)
            r.font.bold = (i in bold_rows)
            r.font.color.rgb = SENAC_BLUE if i in bold_rows else TEXT_DARK
    return table


def add_chrome(slide, title_text, slide_label, fonte_text=None):
    # Barra de titulo azul
    hdr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_W, Inches(0.74))
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
    chip = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(12.18), Inches(0.07), Inches(0.93), Inches(0.60))
    chip.adjustments[0] = 0.12
    chip.fill.solid()
    chip.fill.fore_color.rgb = WHITE
    chip.line.fill.background()
    if LOGO_PATH.exists():
        add_picture_fit(slide, LOGO_PATH, 12.24, 0.11, 0.81, 0.52)

    # Rodape discreto (14 pt) para liberar area util
    footer_y = 7.14
    footer_h = 0.36
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
    r1.font.size = fpt(14, enforce_min=False)
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
    r2.font.size = fpt(14, enforce_min=False)
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
    r3.font.size = fpt(14, enforce_min=False)
    r3.font.color.rgb = WHITE

    # Citacao compacta em 11 pt
    if fonte_text:
        add_textbox(
            slide,
            0.35,
            6.83,
            12.63,
            0.27,
            text=f"Fonte: {fonte_text}",
            font_size=11,
            italic=True,
            color=TEXT_MUTED,
            valign=MSO_ANCHOR.BOTTOM,
            line_spacing=1.0,
            enforce_min=False,
        )


def add_delayed_appear_animation(slide, shape_id: int, delay_ms: int = 1900) -> None:
    """Insere animacao OOXML nativa 'Aparecer (Com o Anterior)' com atraso para congelar GIF 1-shot no quadro final."""
    timing_xml = f"""
    <p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
      <p:tnLst>
        <p:par>
          <p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">
            <p:childTnLst>
              <p:seq concurrent="1" nextAc="seek">
                <p:cTn id="2" dur="indefinite" nodeType="mainSeq">
                  <p:childTnLst>
                    <p:par>
                      <p:cTn id="3" fill="hold">
                        <p:stCondLst>
                          <p:cond delay="indefinite"/>
                          <p:cond evt="onBegin" delay="0">
                            <p:tn val="2"/>
                          </p:cond>
                        </p:stCondLst>
                        <p:childTnLst>
                          <p:par>
                            <p:cTn id="4" fill="hold">
                              <p:stCondLst>
                                <p:cond delay="0"/>
                              </p:stCondLst>
                              <p:childTnLst>
                                <p:par>
                                  <p:cTn id="5" presetID="1" presetClass="entr" presetSubtype="0" fill="hold" grpId="0" nodeType="withEffect">
                                    <p:stCondLst>
                                      <p:cond delay="{int(delay_ms)}"/>
                                    </p:stCondLst>
                                    <p:childTnLst>
                                      <p:set>
                                        <p:cBhvr>
                                          <p:cTn id="6" dur="1" fill="hold">
                                            <p:stCondLst>
                                              <p:cond delay="0"/>
                                            </p:stCondLst>
                                          </p:cTn>
                                          <p:tgtEl>
                                            <p:spTgt spid="{int(shape_id)}"/>
                                          </p:tgtEl>
                                          <p:attrNameLst>
                                            <p:attrName>style.visibility</p:attrName>
                                          </p:attrNameLst>
                                        </p:cBhvr>
                                        <p:to>
                                          <p:strVal val="visible"/>
                                        </p:to>
                                      </p:set>
                                    </p:childTnLst>
                                  </p:cTn>
                                </p:par>
                              </p:childTnLst>
                            </p:cTn>
                          </p:par>
                        </p:childTnLst>
                      </p:cTn>
                    </p:par>
                  </p:childTnLst>
                </p:cTn>
                <p:prevCondLst>
                  <p:cond evt="onPrev" delay="0">
                    <p:tgtEl>
                      <p:sldTgt/>
                    </p:tgtEl>
                  </p:cond>
                </p:prevCondLst>
                <p:nextCondLst>
                  <p:cond evt="onNext" delay="0">
                    <p:tgtEl>
                      <p:sldTgt/>
                    </p:tgtEl>
                  </p:cond>
                </p:nextCondLst>
              </p:seq>
            </p:childTnLst>
          </p:cTn>
        </p:par>
      </p:tnLst>
      <p:bldLst>
        <p:bldP spid="{int(shape_id)}" grpId="0"/>
      </p:bldLst>
    </p:timing>
    """
    timing_el = parse_xml(timing_xml.strip())
    sld = slide.element
    ext_lst = sld.find("{http://schemas.openxmlformats.org/presentationml/2006/main}extLst")
    if ext_lst is not None:
        ext_lst.addprevious(timing_el)
    else:
        sld.append(timing_el)


def new_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def build_deck() -> None:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    MAIN_TOTAL = 57
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
        ("2. Fundamentação", "Funil bibliográfico, Macro-F1, SepConv, qubits, VQAs e HQNN-Parallel"),
        ("3. Trabalhos correlatos", "Estudos clássicos e híbridos nas 9 bases e lacuna de pesquisa"),
        ("4. Desenvolvimento", "Pipeline, 9 bases, all_raw, 7 diagramas arquiteturais e 2 ambientes"),
        ("5. Resultados", "72 modelos, controle Dense20, oclusão 8×8, tempos e telemetria M4"),
        ("6. Conclusão e apoio", "Síntese integrada, contribuições, limitações e slides de apoio"),
    ]
    for i, (t, d) in enumerate(agenda):
        row_y = 0.98 + i * 0.98
        badge = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.55), Inches(row_y), Inches(3.85), Inches(0.78))
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

        desc_box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.58), Inches(row_y), Inches(8.20), Inches(0.78))
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
    ctx_cards = [
        ("Visão computacional", "Classificação de imagens sustenta leitura de documentos, inspeção industrial, sinalização viária e reconhecimento facial."),
        ("CNNs clássicas", "Extraem atributos espaciais hierárquicos direto dos pixels, mas desempenho e custo dependem de arquitetura, lote e hardware."),
        ("QML na era NISQ", "Circuitos quânticos parametrizados (PQCs) acoplados a CNNs prometem expressividade, mas enfrentam custos de simulação e escala."),
    ]
    ctx_h = max(estimate_card_height(3.98, body_text=b, font_size=20, line_spacing=1.15) for _, b in ctx_cards)
    ctx_h = min(4.20, max(3.15, ctx_h))
    ctx_y = 1.05
    for idx, (ct, cb) in enumerate(ctx_cards):
        add_card(
            s, 0.45 + idx * 4.23, ctx_y, 3.98, ctx_h, ct,
            body_text=cb, font_size=20, title_size=21, line_spacing=1.15, auto_height=False,
        )
    q_box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.45), Inches(ctx_y + ctx_h + 0.45), Inches(12.43), Inches(1.10))
    q_box.adjustments[0] = 0.08
    q_box.fill.solid()
    q_box.fill.fore_color.rgb = SENAC_ORANGE_LIGHT
    q_box.line.color.rgb = SENAC_ORANGE
    q_box.line.width = Pt(1.2)
    qtf = q_box.text_frame
    qtf.word_wrap = True
    qtf.vertical_anchor = MSO_ANCHOR.MIDDLE
    qp = qtf.paragraphs[0]
    qp.alignment = PP_ALIGN.CENTER
    qr = qp.add_run()
    qr.text = "Como CNNs clássicas e cabeças híbridas se comparam em nove domínios visuais?"
    qr.font.name = FONT_NAME
    qr.font.size = fpt(22)
    qr.font.bold = True
    qr.font.color.rgb = SENAC_BLUE

    # ===============================================================
    # 4. PROBLEMA E JUSTIFICATIVA
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Problema e justificativa", next_lbl())
    p_items = [
        "Experimentos em recortes simples: MNIST binário (3 vs. 5), 4 classes ou grades sintéticas",
        "Avaliação quase restrita à acurácia global (omissão do Macro-F1)",
        "Variáveis de confusão: lotes assimétricos e falta de controle clássico de gargalo",
        "Baixa reprodutibilidade de sementes, partições e custos reais",
    ]
    j_items = [
        [("Tecnológica: ", True, False, SENAC_ORANGE), ("equilíbrio real entre Macro-F1, tempo, hardware e energia", False, False, TEXT_DARK)],
        [("Acadêmica: ", True, False, SENAC_ORANGE), ("validar o circuito paralelo de Senokosov et al. (2024) sob condições idênticas", False, False, TEXT_DARK)],
        [("Metodológica: ", True, False, SENAC_ORANGE), ("campanha auditável de 72 modelos com controle Dense20 e telemetria", False, False, TEXT_DARK)],
    ]
    h_pj = max(
        estimate_card_height(6.05, items=p_items, font_size=19, space_after=12, line_spacing=1.12),
        estimate_card_height(6.05, items=j_items, font_size=19, space_after=14, line_spacing=1.12),
    )
    h_pj = min(5.70, max(4.30, h_pj))
    y_pj = 0.92 + (5.90 - h_pj) / 2.0
    add_card(s, 0.45, y_pj, 6.05, h_pj, "O problema na literatura de QML", items=p_items, font_size=19, title_size=20, space_after=12, line_spacing=1.12, auto_height=False)
    add_card(s, 6.83, y_pj, 6.05, h_pj, "Por que este estudo importa", items=j_items, font_size=19, title_size=20, space_after=14, line_spacing=1.12, auto_height=False)

    # ===============================================================
    # 5. OBJETIVOS
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Objetivos", next_lbl())
    obj_ger_txt = [
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
    ]
    _, h_obj_top = add_card(
        s, 0.45, 0.96, 12.43, 1.85, "Objetivo geral",
        body_text=obj_ger_txt, font_size=20, title_size=20, line_spacing=1.14,
    )
    obj_cols = [
        ("Bases e pipeline", [
            "Inventariar 9 bases públicas (7 a 47 classes)",
            "Avaliar 4 modos de balanceamento (36 treinos)",
            "Fluxo reprodutível auditado por SHA-256",
        ]),
        ("Arquiteturas", [
            "CNN separável FP32 e features128 congeladas",
            "Controles Dense20 (imagem e vetorial)",
            "Cabeça híbrida 4×5 qubits (Senokosov et al., 2024)",
        ]),
        ("Auditoria completa", [
            "Macro-F1, matrizes, Bayes e calibração (ECE)",
            "Oclusão 8×8, gradientes e ruído/shots",
            "Telemetria em Linux, Windows e iMac M4",
        ]),
    ]
    y_sub = 0.96 + h_obj_top + 0.30
    h_sub = max(estimate_card_height(3.98, items=it, font_size=19, space_after=10) for _, it in obj_cols)
    h_sub = min(6.75 - y_sub, max(3.25, h_sub))
    for idx, (ot, oit) in enumerate(obj_cols):
        add_card(
            s, 0.45 + idx * 4.23, y_sub, 3.98, h_sub, ot,
            items=oit, font_size=19, title_size=20, space_after=10, auto_height=False,
        )

    # ===============================================================
    # 6. HIPÓTESE E DELIMITAÇÕES
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Hipótese e delimitações", next_lbl())
    hip_body = [
        [
            ("Uma cabeça híbrida com PQCs simulados alcança ", False, False, TEXT_DARK),
            ("convergência estável e desempenho competitivo", True, False, SENAC_BLUE),
            (", próximo ao controle clássico, sob protocolo padronizado.", False, False, TEXT_DARK),
        ],
        [
            ("Não ", True, True, SENAC_ORANGE),
            ("se pressupõe superioridade quântica irrestrita: o custo de simulação e a complexidade visual condicionam a viabilidade prática.", False, False, TEXT_DARK),
        ],
    ]
    del_items = [
        "Classificação supervisionada de imagens estáticas 2D em 9 bases públicas",
        [("Circuitos quânticos ", False, False, TEXT_DARK), ("apenas simulados em CPU local", True, False, TEXT_DARK), (" (PennyLane e Qiskit Aer, sem QPU física)", False, False, TEXT_DARK)],
        "Campanha principal de 72 checkpoints em seed=42 (sem inferência inter-sementes)",
    ]
    _, h_hip = add_card(
        s, 0.45, 1.00, 12.43, 2.90, "Hipótese científica",
        body_text=hip_body, font_size=20, title_size=20, space_after=10, line_spacing=1.12,
    )
    add_card(
        s, 0.45, 1.00 + h_hip + 0.34, 12.43, 3.10, "Delimitações do estudo",
        items=del_items, alert=True, font_size=19, title_size=20, space_after=8, line_spacing=1.10,
    )

    # ===============================================================
    # 7. REVISÃO DA LITERATURA (MOVIDO DE ANTIGO 18 PARA CA)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Como foi a revisão da literatura", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "fig_funil_pesquisa.png", 0.30, 0.88, 7.05, 5.82)
    add_card(
        s, 7.50, 0.96, 5.48, 5.65,
        "Diretrizes da auditoria bibliográfica",
        items=[
            [("Frente 1: ", True, False, SENAC_BLUE), ("fundamentação teórica e artigos originais das 9 bases", False, False, TEXT_DARK)],
            [("Frente 2: ", True, False, SENAC_BLUE), ("estudos empíricos por base (recorte 2021–2026)", False, False, TEXT_DARK)],
            "Conferência manual na fonte primária: variante, nº de classes, partição e métrica",
            "28 registros verificados (19 clássicos + 9 quânticos/híbridos) em mapeamento preliminar",
        ],
        font_size=18, title_size=19, space_after=10, center_in=(0.90, 6.72),
    )

    # ===============================================================
    # 8. MÉTRICAS: POR QUE O MACRO-F1?
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Métricas: por que o Macro-F1?", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, SLIDE_FIG_DIR / "metricas_classificacao_exemplos_slide.png", 0.20, 0.82, 8.95, 5.92)
    add_card(
        s, 9.28, 0.90, 3.80, 5.75,
        "Avaliação multiclasse",
        items=[
            "Matriz de confusão, decomposição um-contra-todos (TP, FP, FN, TN) e curvas ROC/AUC",
            [("Macro-F1: ", True, False, SENAC_BLUE), ("média não ponderada do F1 entre classes — dá peso igual às minoritárias (SVHN, GTSRB, FER2013)", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=10, center_in=(0.86, 6.72),
    )

    # ===============================================================
    # 9. CONVOLUÇÃO SEPARÁVEL (ANTIGO 10 — ANIMACAO + TITULO MAIORES, SEM CALCULOS)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Convolução separável: Depthwise 3×3 + Pointwise 1×1", next_lbl(), "Elaborado pelo autor (2026).")
    # Titulo nativo grande acima da animacao
    sub_hdr = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.28), Inches(0.82), Inches(12.77), Inches(0.46))
    sub_hdr.adjustments[0] = 0.08
    sub_hdr.fill.solid()
    sub_hdr.fill.fore_color.rgb = SENAC_BLUE_LIGHT
    sub_hdr.line.color.rgb = BORDER_GRAY
    stf = sub_hdr.text_frame
    stf.vertical_anchor = MSO_ANCHOR.MIDDLE
    sp = stf.paragraphs[0]
    sp.alignment = PP_ALIGN.CENTER
    sr = sp.add_run()
    sr.text = "Entrada 4×4×2 → Intermediário Z (2×2×2) → Saída 2×2×3  |  24 vs. 54 pesos (2,25× menos)"
    sr.font.name = FONT_NAME
    sr.font.size = fpt(19)
    sr.font.bold = True
    sr.font.color.rgb = SENAC_BLUE

    add_picture_fit(s, GIF_SLIDE_DIR / "07_sepconv_numerico_clean.gif", 0.28, 1.32, 12.77, 4.18)
    add_bottom_strip(
        s, 5.56, 1.18,
        [
            [("DW 3×3: ", True, False, SENAC_BLUE), ("filtro espacial por canal → Z (2×2×2; 18 pesos)", False, False, TEXT_DARK)],
            [("PW 1×1: ", True, False, SENAC_BLUE), ("3 filtros combinam canais → saída 2×2×3 (6 pesos)", False, False, TEXT_DARK)],
            [("Economia: ", True, False, OK_GREEN), ("24 pesos totais vs. 54 na Conv2D padrão", False, False, TEXT_DARK)],
        ],
        font_size=18,
    )

    # ===============================================================
    # 10. MAPAS DE CARACTERÍSTICAS (ANTIGO 11 — MAIS ESPACO P/ IMAGENS)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Mapas de características em entradas 64×64×1", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "fmap_03a_piramide_blocos_fashion_mnist.png", 0.20, 0.80, 4.55, 5.96)
    add_picture_fit(s, FIG_DIR / "fmap_03b_piramide_blocos_fer2013.png", 4.82, 0.80, 4.55, 5.96)
    add_card(
        s, 9.48, 0.90, 3.62, 5.80,
        "Hierarquia de ativações",
        items=[
            [("B1–B2: ", True, False, SENAC_BLUE), ("bordas e contornos locais (bota; olhos e sorriso)", False, False, TEXT_DARK)],
            [("B3–B5: ", True, False, SENAC_BLUE), ("foco crescente na região do objeto", False, False, TEXT_DARK)],
            [("GAP → features128: ", True, False, SENAC_BLUE), ("62/128 ativos (Fashion) e 63/128 (FER2013)", False, False, TEXT_DARK)],
            "Mínimo em −0,2785 (curva SiLU)",
        ],
        font_size=18, title_size=19, space_after=8, center_in=(0.82, 6.74),
    )

    # ===============================================================
    # 11. PIPELINE COMPOSTO DE AUMENTO DE DADOS (ANTIGO 12 — MAIS ESPACO P/ IMAGENS)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Aumento de dados: pipeline composto em 6 etapas", next_lbl(), "Elaborado pelo autor (2026).")
    add_textbox(s, 0.25, 0.78, 12.83, 0.32, "(a) GTSRB (128×128×3 — placa PARE)  |  RMS composto = 0,2967", font_size=18, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER)
    add_picture_fit(s, SLIDE_FIG_DIR / "aug_01_pipeline_etapas_gtsrb_slide.png", 0.20, 1.10, 12.93, 2.72)
    add_textbox(s, 0.25, 3.84, 12.83, 0.32, "(b) CIFAR-10 (64×64×3 — navio)  |  RMS composto = 0,1084", font_size=18, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER)
    add_picture_fit(s, SLIDE_FIG_DIR / "aug_02_pipeline_etapas_cifar10_slide.png", 0.20, 4.16, 12.93, 2.66)

    # ===============================================================
    # 12. PRESERVAÇÃO SEMÂNTICA E flip_lr=False (ANTIGO 13)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Preservação semântica e flip_lr=False", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, SLIDE_FIG_DIR / "aug_03_comparacao_flip_lr_semantico_slide.png", 0.30, 0.80, 12.73, 4.72)
    add_bottom_strip(
        s, 5.58, 1.18,
        [
            [("Inversão de classe: ", True, False, BAD_RED), ("espelhar altera GTSRB, MNIST ('3'), EMNIST ('R') e SVHN ('5')", False, False, TEXT_DARK)],
            [("Invariância restrita: ", True, False, OK_GREEN), ("válido só em objetos naturais (ex.: cavalo CIFAR-10)", False, False, TEXT_DARK)],
            [("Correção: ", True, False, SENAC_BLUE), ("fixado flip_lr=False em src/data_prep/data.py", False, False, TEXT_DARK)],
        ],
        font_size=18,
    )

    # ===============================================================
    # 13. QUBITS, SUPERPOSIÇÃO E EMARANHAMENTO (ESFERA DE BLOCH PASSO A PASSO)
    # ===============================================================
    bloch_lbl = next_lbl()
    bloch_steps = [
        (
            None,
            GIF_DIR / "09a_bloch_passo0_init.png",
            [("Esfera de Bloch (início): ", True, False, SENAC_BLUE), ("qubit em |0⟩ (+Z) antes das rotações unitárias", False, False, TEXT_DARK)],
        ),
        (
            GIF_DIR / "09b_bloch_passo1_rx.gif",
            GIF_DIR / "09b_bloch_passo1_rx_final.png",
            [("Rotação R_X(−π/4): ", True, False, RGBColor(220, 38, 38)), ("gira −45° em torno de X para frente (+Y), em superposição", False, False, TEXT_DARK)],
        ),
        (
            GIF_DIR / "09c_bloch_passo2_ry.gif",
            GIF_DIR / "09c_bloch_passo2_ry_final.png",
            [("Rotação R_Y(2π/3): ", True, False, RGBColor(5, 150, 105)), ("gira 120° em torno de Y na face frontal (y fixo; altera x e z)", False, False, TEXT_DARK)],
        ),
        (
            GIF_DIR / "09d_bloch_passo3_rz.gif",
            GIF_DIR / "09d_bloch_passo3_rz_final.png",
            [("Rotação R_Z(π/3): ", True, False, RGBColor(124, 58, 237)), ("gira 60° em torno de Z, ajustando a fase relativa φ", False, False, TEXT_DARK)],
        ),
        (
            GIF_DIR / "09e_bloch_passo4_pauli_y.gif",
            GIF_DIR / "09e_bloch_passo4_pauli_y_final.png",
            [("Medição Pauli-Y: ", True, False, RGBColor(15, 118, 110)), ("projeta |ψ⟩ no eixo Y → ⟨Y⟩ = +0,88 ∈ [−1, +1]", False, False, TEXT_DARK)],
        ),
    ]
    for gif_path, cover_png, step_bullet in bloch_steps:
        s = new_slide(prs)
        add_chrome(
            s,
            "Qubits, superposição, emaranhamento e medição",
            bloch_lbl,
            "Elaborado pelo autor (2026), com base em Nielsen e Chuang (2010) e IBM Quantum (2026).",
        )
        if gif_path is not None:
            add_picture_fit(s, gif_path, 0.45, 0.82, 6.12, 4.65)
            cover_shape = add_picture_fit(s, cover_png, 0.45, 0.82, 6.12, 4.65)
            add_delayed_appear_animation(s, cover_shape.shape_id, delay_ms=1900)
        else:
            add_picture_fit(s, cover_png, 0.45, 0.82, 6.12, 4.65)
        add_picture_fit(s, FIG_DIR / "fig_261_circuito_bell.png", 6.78, 0.82, 6.07, 4.65)
        add_bottom_strip(
            s, 5.58, 1.18,
            [
                step_bullet,
                "Portas H e CNOT geram emaranhamento (estado de Bell); medição extrai valores esperados reais",
            ],
            font_size=18,
        )

    # ===============================================================
    # 14. CODIFICAÇÃO DE DADOS E LAÇO VQA
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Codificação de dados e laço variacional (VQA)",
        next_lbl(),
        "Elaborado pelo autor (2026), com base em Schuld, Sweke e Meyer (2021), Pérez-Salinas et al. (2020), Cerezo et al. (2021) e IBM Quantum (2026).",
    )
    add_picture_fit(s, FIG_DIR / "fig_263_codificacoes_vetoriais.png", 0.40, 0.82, 6.10, 4.65)
    add_picture_fit(s, FIG_DIR / "fig_264_laco_vqa.png", 6.65, 0.82, 6.28, 4.65)
    add_bottom_strip(
        s, 5.58, 1.18,
        [
            [("Codificação angular: ", True, False, SENAC_BLUE), ("vetor clássico vira ângulos de rotação R_X em profundidade O(1)", False, False, TEXT_DARK)],
            [("Laço VQA: ", True, False, SENAC_BLUE), ("ansatz atualizado por parameter-shift acoplado ao otimizador clássico", False, False, TEXT_DARK)],
        ],
        font_size=18,
    )

    # ===============================================================
    # 15. SIMULAÇÃO, BARREN PLATEAUS E ESCALABILIDADE
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Simulação, barren plateaus e escalabilidade",
        next_lbl(),
        "Elaborado pelo autor (2026), com base em McClean et al. (2018), Cerezo et al. (2021), Faj et al. (2023) e Bayraktar et al. (2023).",
    )
    add_picture_fit(s, FIG_DIR / "fig_265_variancia_gradiente.png", 0.40, 0.82, 6.05, 4.65)
    add_picture_fit(s, FIG_DIR / "fig_266_fluxo_backends_simulacao.png", 6.60, 0.82, 6.33, 4.65)
    add_bottom_strip(
        s, 5.58, 1.18,
        [
            "Simular 20 qubits em statevector exige 2²⁰ (1.048.576) amplitudes e sofre barren plateaus",
            [("Decisão arquitetural: ", True, False, SENAC_BLUE), ("4 circuitos paralelos de 5 qubits (2⁵ = 32 estados cada)", False, False, TEXT_DARK)],
        ],
        font_size=18,
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
    add_picture_fit(s, FIG_DIR / "fig_arxiv2304_hqnn_parallel_arquitetura.jpg", 0.40, 0.82, 12.53, 3.05)
    s16_c1 = [
        "Codificação R_X + 3 camadas R_Z–R_Y–R_Z com CNOT cíclico",
        "Medição Pauli-Y: 45 pesos/ramo = 180 pesos quânticos",
        "MNIST original: 99,21% (45k pesos) vs. 98,71% CNN (372k)",
    ]
    s16_c2 = [
        "Extrator padronizado de 5 blocos congelado (features128)",
        "Projeção clássica 128 → 20 comum ao controle Dense20",
        "Execução cruzada: 9 bases, Macro-F1, PennyLane e Qiskit",
    ]
    h_s16 = max(
        estimate_card_height(6.05, items=s16_c1, font_size=18, space_after=6),
        estimate_card_height(6.05, items=s16_c2, font_size=18, space_after=6),
    )
    h_s16 = min(2.75, h_s16)
    add_card(s, 0.45, 3.98, 6.05, h_s16, "Circuito preservado (4 × 5 qubits)", items=s16_c1, font_size=18, title_size=19, space_after=6, auto_height=False)
    add_card(s, 6.80, 3.98, 6.08, h_s16, "Adaptações metodológicas neste TCC", items=s16_c2, font_size=18, title_size=19, space_after=6, auto_height=False)

    # ===============================================================
    # 17. CORRELATOS CLÁSSICOS (ANTIGO 19)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Estudos clássicos nas nove bases",
        next_lbl(),
        "Elaborado pelo autor (2026), a partir da auditoria das publicações originais.",
    )
    add_styled_table(
        s, 0.42, 0.84, 12.49, 5.20,
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
        s, 0.42, 6.18, 12.49, 0.52,
        "Acurácias dos artigos originais: não equivalem diretamente ao Macro-F1 deste TCC (protocolos distintos).",
        font_size=18, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER,
    )

    # ===============================================================
    # 18. CORRELATOS QUÂNTICOS E HÍBRIDOS (ANTIGO 20 — TABELA IGUAL A ANTERIOR, 3 COLUNAS, 9 BASES)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Estudos quânticos e híbridos na literatura",
        next_lbl(),
        "Elaborado pelo autor (2026), a partir da auditoria das publicações originais.",
    )
    add_styled_table(
        s, 0.42, 0.84, 12.49, 5.20,
        ["Base", "Estudo, arquitetura e recorte", "Resultado"],
        [
            ["MNIST", "Riaz (2023) NNQE (10 cl.) · Long (2025) QCQ-CNN (bin. 3 vs. 5)", "93,8% · 98,85%"],
            ["Fashion-MNIST", "Bokhan (2022) QCNN (4 cl.) · Song (2024) QAOA (10 cl.)", "85,9–93,6% · 92,6%"],
            ["KMNIST", "Dong (2025) — CNN híbrida (apenas binário confirmado)", "Binário (s/ 10 cl.)"],
            ["EMNIST Balanced", "Riaz (2026) — filtro quântico fixo de 4 qubits (47 cl.)", "75,9%"],
            ["CIFAR-10", "Riaz (2023) NNQE cinza · Senokosov (2024) HQNN", "36,0% · 82,78%"],
            ["CIFAR-100 Coarse", "Nenhum estudo quântico/híbrido nas 20 superclasses", "Lacuna aberta"],
            ["SVHN", "Kong (2026) CQNAS — resumo confirma uso (sem valor)", "Não detalhado"],
            ["GTSRB", "Riaz (2023) NNQE cinza (vs. 82,2% na densa clássica)", "73,4% (−8,8 p.p.)"],
            ["FER2013", "Alsubai (2024) ResNet-18 híbrida (protocolo c/ ressalva*)", "98,19%*"],
        ],
        col_widths=[2.50, 7.64, 2.35],
        alignments=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT],
        font_size=16, header_font_size=17, bold_rows={5}, enforce_min=False,
    )
    add_textbox(
        s, 0.42, 6.18, 12.49, 0.52,
        "Predominam recortes binários/4 classes e filtros fixos; *FER2013 tem divergência amostral no artigo.",
        font_size=18, bold=True, color=SENAC_ORANGE, align=PP_ALIGN.CENTER,
    )

    # ===============================================================
    # 19. LACUNA DE PESQUISA
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Lacuna de pesquisa", next_lbl())
    add_row_cards(
        s,
        [
            [("Protocolos fragmentados: ", True, False, SENAC_BLUE), ("poucas classes ou domínios; lacuna aberta nas 20 superclasses do CIFAR-100 Coarse", False, False, TEXT_DARK)],
            [("Omissão do Macro-F1: ", True, False, SENAC_BLUE), ("literatura reporta quase só acurácia global, mascarando minoritárias (GTSRB, FER2013, SVHN)", False, False, TEXT_DARK)],
            [("Variáveis de confusão: ", True, False, SENAC_BLUE), ("lotes assimétricos (ex.: 1 vs. 4) e falta de controle clássico com gargalo de mesma dimensão", False, False, TEXT_DARK)],
        ],
        y_start=0.92, row_h=1.08, gap=0.14, numbered=True, font_size=19,
    )
    add_card(
        s, 0.45, 4.62, 12.43, 2.05,
        "Contribuição proposta",
        body_text="Campanha padronizada nas 9 bases completas (72 modelos), avaliada por Macro-F1 com controle vetorial Dense20, calibração, oclusão 8×8 e telemetria multiplataforma.",
        font_size=20, title_size=20, line_spacing=1.14,
    )

    # ===============================================================
    # 20. TIPO DE PESQUISA E PERGUNTA
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Tipo de pesquisa e pergunta norteadora", next_lbl())
    _, h_tp = add_card(
        s, 0.45, 1.05, 12.43, 2.75,
        "Enquadramento metodológico",
        items=[
            [("Natureza aplicada", True, False, SENAC_BLUE), (", abordagem ", False, False, TEXT_DARK), ("quantitativa", True, False, SENAC_BLUE), (" e protocolo estritamente auditável", False, False, TEXT_DARK)],
            [("Objetivos ", False, False, TEXT_DARK), ("exploratórios", True, False, TEXT_DARK), (" (CIFAR-100 Coarse e EMNIST), ", False, False, TEXT_DARK), ("descritivos", True, False, TEXT_DARK), (" (72 modelos + 36 balanceamento + 27 telemetria M4) e ", False, False, TEXT_DARK), ("comparativos", True, False, TEXT_DARK)],
        ],
        font_size=20, title_size=20, space_after=10, line_spacing=1.14,
    )
    add_card(
        s, 0.45, 1.05 + h_tp + 0.38, 12.43, 3.00,
        "Pergunta de pesquisa",
        body_text="Em que medida uma representação convolucional congelada (features128) sustenta cabeças reduzidas nas nove bases, e como a cabeça híbrida (4 × 5 qubits) se compara em Macro-F1, calibração, explicabilidade e custo frente à CNN original e ao controle Dense20?",
        font_size=20, title_size=20, line_spacing=1.18,
    )

    # ===============================================================
    # 21. PIPELINE EXPERIMENTAL EM SEIS ETAPAS
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
    ys = [1.14, 3.98]
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
    # 22. AS NOVE BASES DE DADOS
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "As nove bases de dados", next_lbl(), "Elaborado pelo autor (2026).")
    add_styled_table(
        s, 0.42, 0.84, 12.49, 5.20,
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
        s, 0.42, 6.18, 12.49, 0.52,
        "Partições estratificadas fixas (70/15/15) compartilhadas pelos 8 modelos em cada base.",
        font_size=18, color=TEXT_MUTED, align=PP_ALIGN.CENTER,
    )

    # ===============================================================
    # 23. EQUILÍBRIO DE CLASSES (ANTIGO 25 — IMAGEM HORIZONTAL EM TELA INTEIRA)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Equilíbrio de classes: três regimes", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, SLIDE_FIG_DIR / "equilibrio_classes_9_datasets_horiz.png", 0.16, 0.78, 13.01, 6.02)

    # ===============================================================
    # 24. MODOS DE BALANCEAMENTO (ANTIGO 26 — LEGENDA MAIOR NO 1º GRAFICO)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Modos de balanceamento: Macro-F1 e tempo (36 execuções)", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, SLIDE_FIG_DIR / "fig_balanceamento_macro_f1_slide.png", 0.22, 0.82, 7.15, 5.42)
    add_picture_fit(s, SLIDE_FIG_DIR / "fig_342_balanceamento_tempo_treino_slide.png", 7.45, 0.82, 5.66, 5.42)
    add_textbox(
        s, 0.35, 6.28, 12.63, 0.48,
        "Triagem preliminar na CNN original (mixed_float16, lote 512, 2.486 épocas, 88,86 h acumuladas).",
        font_size=18, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER,
    )

    # ===============================================================
    # 25. JUSTIFICATIVA OBJETIVA DE all_raw
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Por que adotar a distribuição natural (all_raw)?", next_lbl(), "Elaborado pelo autor (2026).")
    add_styled_table(
        s, 0.45, 0.88, 12.43, 2.25,
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
        s, 0.45, 3.38, 12.43, 3.30,
        "Conclusão da triagem de 36 execuções",
        items=[
            [("all_raw: ", True, False, OK_GREEN), ("maior média e maior mediana sem distorcer frequências empíricas nem custos quânticos", False, False, TEXT_DARK)],
            [("undersample: ", True, False, BAD_RED), ("colapso severo em FER2013 (−19,28 p.p.) e GTSRB (−13,69 p.p.)", False, False, TEXT_DARK)],
            [("class_weight: ", True, False, BAD_RED), ("−6,12 p.p. no FER2013; idêntico a all_raw nas 5 bases equilibradas", False, False, TEXT_DARK)],
            [("oversample: ", True, False, SENAC_ORANGE), ("+15,1% de tempo (GTSRB 9,90 h vs. 5,20 h) e −1,26 p.p. no CIFAR-10", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=6,
    )

    # ===============================================================
    # 26. PRÉ-PROCESSAMENTO E AUDITORIA DE INTEGRIDADE
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Pré-processamento e auditoria de integridade", next_lbl())
    pp_items = [
        "Tensores em ponto flutuante, normalização por canal e política all_raw",
        "Redimensionamento proporcional (resize_with_pad) para 64×64 (128×128 no GTSRB)",
        "Partição estratificada fixa (70/15/15) compartilhada pelos 8 modelos de cada base",
        "Rastreabilidade por hashes SHA-256 e impressões digitais das partições",
    ]
    lim_items = [
        [("GTSRB: ", True, False, BAD_RED), ("3.990 de 5.876 imagens de teste (67,9%) compartilham tracks físicos com o treino", False, False, TEXT_DARK)],
        [("FER2013: ", True, False, BAD_RED), ("378 duplicatas exatas no teste (7,02%), 403 na validação e 57 conflitos de rótulo", False, False, TEXT_DARK)],
        "EMNIST (1) e CIFAR-100 Coarse (7): cópias pontuais; 5 bases restantes livres de duplicatas",
    ]
    h_pp = max(
        estimate_card_height(6.05, items=pp_items, font_size=19, space_after=10, line_spacing=1.12),
        estimate_card_height(6.05, items=lim_items, font_size=19, space_after=12, line_spacing=1.12),
    )
    h_pp = min(5.70, max(4.30, h_pp))
    y_pp = 0.90 + (5.90 - h_pp) / 2.0
    add_card(s, 0.45, y_pp, 6.05, h_pp, "Padronização idêntica", items=pp_items, font_size=19, title_size=20, space_after=10, line_spacing=1.12, auto_height=False)
    add_card(s, 6.83, y_pp, 6.05, h_pp, "Limitações auditadas nos dados", items=lim_items, alert=True, font_size=19, title_size=20, space_after=12, line_spacing=1.12, auto_height=False)

    # ===============================================================
    # 27. TRÊS FAMÍLIAS DE MODELOS
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Três famílias de modelos comparadas", next_lbl())
    fam_specs = [
        ("CNN original (FP32)", [
            "5 blocos SeparableConv2D (32→48→64→96→128), GroupNorm(16), SiLU e MaxPool.",
            "Cabeça GAP+GMP → 256 → 256 → K.",
            [("Extrator: ", True, False, SENAC_BLUE), ("66.905 (C=1) ou 67.019 (C=3) pesos.", False, False, TEXT_DARK)],
        ]),
        ("Dense20 (controle)", [
            "Extrator congelado (features128): D20 imagem (LayerNorm + ReLU) e Dense20 vetorial (128→20 tanh→K).",
            [("Função: ", True, False, SENAC_BLUE), ("isolar o efeito da compressão para o gargalo de 20 dimensões.", False, False, TEXT_DARK)],
        ]),
        ("Híbrido 4×5 qubits", [
            "Mesma projeção 128 → 20 sobre features128; troca apenas tanh por 4 PQCs de 5 qubits.",
            "Simulação exata em CPU: PennyLane e Qiskit Aer (Windows e Mac).",
        ]),
    ]
    h_fam = max(estimate_card_height(3.98, body_text=b, font_size=19, space_after=10, line_spacing=1.12, bullet=False) for _, b in fam_specs)
    h_fam = min(4.60, max(3.60, h_fam))
    for idx, (ft, fb) in enumerate(fam_specs):
        add_card(
            s, 0.45 + idx * 4.23, 1.05, 3.98, h_fam, ft,
            body_text=fb, font_size=19, title_size=20, space_after=10, line_spacing=1.12, auto_height=False,
        )
    chk_box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.45), Inches(1.05 + h_fam + 0.35), Inches(12.43), Inches(0.90))
    chk_box.adjustments[0] = 0.08
    chk_box.fill.solid()
    chk_box.fill.fore_color.rgb = SENAC_BLUE_LIGHT
    chk_box.line.color.rgb = SENAC_BLUE
    ctf = chk_box.text_frame
    ctf.vertical_anchor = MSO_ANCHOR.MIDDLE
    cp = ctf.paragraphs[0]
    cp.alignment = PP_ALIGN.CENTER
    cr = cp.add_run()
    cr.text = "Campanha principal auditada: 72 checkpoints = 9 bases × 8 configurações"
    cr.font.name = FONT_NAME
    cr.font.size = fpt(21)
    cr.font.bold = True
    cr.font.color.rgb = SENAC_BLUE

    # ===============================================================
    # 28. ETAPA 1: CNN CLÁSSICA DE ORIGEM (ANTIGO 30)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Etapa 1: CNN clássica de origem (FP32)", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, SLIDE_FIG_DIR / "fig_arq_etapa1_cnn_original_slide.png", 0.25, 0.82, 12.83, 4.70)
    add_bottom_strip(
        s, 5.58, 1.18,
        [
            "Treinada do zero em Linux (FP32, aumento de 50%, label smoothing 0,05); 201.059 pesos (C=1, K=10)",
            "Congelada em block5_pool + GAP para exportar features128 determinísticas (.npy) em ~3 min nas 9 bases",
        ],
        font_size=18,
    )

    # ===============================================================
    # 29..34. ANIMACOES CORTADAS NA PARTE DAS FORMULAS + DISPOSICAO EM LARGURA TOTAL
    # ===============================================================

    # 29. ANATOMIA INTERNA DE UM BLOCO CNN (BLOCO B3)
    s = new_slide(prs)
    add_chrome(s, "Anatomia interna de um bloco CNN (Bloco B3)", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, GIF_SLIDE_DIR / "05_zoom_bloco_cnn_clean.gif", 0.25, 0.80, 12.83, 4.78)
    add_bottom_strip(
        s, 5.64, 1.12,
        [
            [("Ordem: ", True, False, SENAC_BLUE), ("SepConv 5×5 + GroupNorm(16) + SiLU + SepConv 3×3 + MaxPool 2×2", False, False, TEXT_DARK)],
            [("Bloco B3: ", True, False, SENAC_BLUE), ("8×8×48 → 4×4×64 com 9.200 pesos e 572.416 MACs", False, False, TEXT_DARK)],
            "GroupNorm independe do tamanho de lote (estável em lote 128 e 512)",
        ],
        font_size=18,
    )

    # 30. ETAPA 2A: CABEÇA Dense20 SOBRE IMAGENS
    s = new_slide(prs)
    add_chrome(s, "Etapa 2A: cabeça Dense20 sobre imagens", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, GIF_SLIDE_DIR / "02_fluxo_dense20_imagem_clean.gif", 0.25, 0.80, 12.83, 4.78)
    add_bottom_strip(
        s, 5.64, 1.12,
        [
            "5 blocos convolucionais congelados + aumento de 50% (Linux)",
            [("Gargalo: ", True, False, SENAC_BLUE), ("GAP(128) → Dense(20) + LayerNorm + ReLU → Dense(K)", False, False, TEXT_DARK)],
            [("Treináveis: ", True, False, OK_GREEN), ("2.830 pesos (K=10) sobre imagens diretas", False, False, TEXT_DARK)],
        ],
        font_size=18,
    )

    # 31. ETAPA 2B: CABEÇA CLÁSSICA VETORIAL (Dense20)
    s = new_slide(prs)
    add_chrome(s, "Etapa 2B: cabeça clássica vetorial (Dense20)", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, GIF_SLIDE_DIR / "03_fluxo_classico_tanh_clean.gif", 0.25, 0.80, 12.83, 4.78)
    add_bottom_strip(
        s, 5.64, 1.12,
        [
            [("Entrada: ", True, False, SENAC_BLUE), ("features128 congelados em .npy (Linux e Mac)", False, False, TEXT_DARK)],
            [("Cabeça: ", True, False, SENAC_BLUE), ("Dense(128, ReLU) → Dense(20) → tanh → Dense(K)", False, False, TEXT_DARK)],
            [("Treináveis: ", True, False, OK_GREEN), ("19.302 pesos (K=10); par direto da etapa quântica", False, False, TEXT_DARK)],
        ],
        font_size=18,
    )

    # 32. ETAPA 3: CABEÇA HÍBRIDA 4×5 QUBITS
    s = new_slide(prs)
    add_chrome(
        s,
        "Etapa 3: cabeça híbrida paralela (4 × 5 qubits)",
        next_lbl(),
        "Elaborado pelo autor (2026), com base em Senokosov et al. (2024).",
    )
    add_picture_fit(s, GIF_SLIDE_DIR / "04_fluxo_hibrido_4xpqc_clean.gif", 0.25, 0.80, 12.83, 4.78)
    add_bottom_strip(
        s, 5.64, 1.12,
        [
            "Mesmas features128 e projeção 128 → 20 da Etapa 2B",
            [("Divisão: ", True, False, SENAC_BLUE), ("vetor u ∈ ℝ²⁰ em 4 ramos disjuntos de 5 qubits", False, False, TEXT_DARK)],
            [("Treináveis: ", True, False, OK_GREEN), ("19.482 pesos (K=10; +180 ângulos) no lugar de tanh", False, False, TEXT_DARK)],
        ],
        font_size=18,
    )

    # 33. CIRCUITO QUÂNTICO DE 5 QUBITS
    s = new_slide(prs)
    add_chrome(
        s,
        "Circuito variacional de 5 qubits por ramo",
        next_lbl(),
        "Elaborado pelo autor (2026), reproduzindo Senokosov et al. (2024).",
    )
    add_picture_fit(s, GIF_SLIDE_DIR / "06_zoom_pqc_5qubits_clean.gif", 0.25, 0.80, 12.83, 4.78)
    add_bottom_strip(
        s, 5.64, 1.12,
        [
            "RX(u) + 3×(RZ·RY·RZ + CNOT circular r = 1, 2, 3)",
            [("Medição: ", True, False, SENAC_BLUE), ("Pauli-Y ⟨Y⟩ ∈ [−1, 1] nos 5 qubits (45 ângulos/ramo)", False, False, TEXT_DARK)],
            [("Parameter-shift: ", True, False, BAD_RED), ("404 aval./amostra no treino e 4 na inferência", False, False, TEXT_DARK)],
        ],
        font_size=18,
    )

    # 34. COMPARATIVO ESTRUTURAL ENTRE AS ETAPAS
    s = new_slide(prs)
    add_chrome(s, "Comparativo estrutural: o que mudou entre as etapas", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, GIF_SLIDE_DIR / "08_comparativo_4_etapas_clean.gif", 0.25, 0.80, 12.83, 4.78)
    add_bottom_strip(
        s, 5.64, 1.12,
        [
            "Backbone de 67.019 pesos (3ch) congelado após Etapa 1",
            [("2B → 3: ", True, False, SENAC_BLUE), ("19.302 para 19.482 pesos (muda só a camada 20D)", False, False, TEXT_DARK)],
            [("Troca 1:1: ", True, False, OK_GREEN), ("tanh(u) ↔ 4×5 qubits (+180 ângulos quânticos)", False, False, TEXT_DARK)],
        ],
        font_size=18,
    )

    # ===============================================================
    # 35. PROTOCOLO EXPERIMENTAL
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Protocolo experimental e critérios de avaliação", next_lbl())
    prot_l = [
        "72 checkpoints (9 bases × 8 configurações), 100 épocas completas",
        "Otimizador Adam (η = 3×10⁻⁴, cosseno + aquecimento)",
        "Seleção pelo melhor Macro-F1 de validação; teste final em all_raw",
        "Imagens: label smoothing 0,05; features128: entropia cruzada padrão, lote 128",
    ]
    prot_r2 = [
        "Convergência estável acima do acaso (1/K)",
        "1.336 posteriores bayesianas (Jeffreys) e calibração (ECE, NLL, Brier)",
        "576 Grad-CAM, 73.728 oclusões 8×8, gradientes, ruído/shots e telemetria",
    ]
    _, h_pr1 = add_card(
        s, 6.80, 1.00, 6.08, 1.95, "Métrica primária",
        body_text="Macro-F1 de teste (%) e Δ pareado em pontos percentuais (p.p.).",
        font_size=19, title_size=20,
    )
    _, h_pr2 = add_card(
        s, 6.80, 1.00 + h_pr1 + 0.28, 6.08, 3.80, "Critérios de auditoria",
        items=prot_r2, font_size=18, title_size=20, space_after=8,
    )
    total_r_h = h_pr1 + 0.28 + h_pr2
    add_card(
        s, 0.45, 1.00, 6.08, total_r_h, "Regime de treinamento (seed=42)",
        items=prot_l, font_size=19, title_size=20, space_after=12, line_spacing=1.12, auto_height=False,
    )

    # ===============================================================
    # 36. DOIS AMBIENTES COMPUTACIONAIS
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Dois ambientes computacionais e versões auditadas", next_lbl(), "Elaborado pelo autor (2026).")
    add_styled_table(
        s, 0.42, 0.90, 12.49, 5.55,
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
    # 37. HEATMAP MACRO-F1 (ANTIGO 39 — SUBSTITUIDO PELO HEATMAP COMPLETO 9x8)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Macro-F1 de teste (%) nas nove bases — todos os 72 modelos", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, SLIDE_FIG_DIR / "figura_26_comparacao_matriz_slide.png", 0.20, 0.78, 12.93, 5.48)
    add_textbox(
        s, 0.35, 6.32, 12.63, 0.46,
        "Empate entre os 8 modelos em cada base (médias 81,9%–82,2%; PL vs. QK < 0,05 p.p.; *tracks).",
        font_size=18, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER,
    )

    # ===============================================================
    # 38. GRÁFICO DOS DELTAS (ANTIGO 40 — CLARO E AUTOEXPLICATIVO)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Diferença de Macro-F1: Híbrido vs. CNN e vs. Dense20", next_lbl(), "Elaborado pelo autor (2026).")
    add_textbox(
        s, 0.35, 0.78, 12.63, 0.42,
        "Δ em p.p. no Macro-F1 de teste — acima de 0: Híbrido vence; abaixo de 0: Híbrido perde",
        font_size=18, color=TEXT_DARK, align=PP_ALIGN.CENTER,
    )
    chart_data = CategoryChartData()
    chart_data.categories = ["MNIST", "F-MN", "KMN", "EMNIST", "CIF10", "C100C", "SVHN", "GTSRB", "FER13"]
    chart_data.add_series("Híbrido (Mac PL) − CNN original", (0.321, -0.021, -0.001, 0.755, 0.203, -0.341, 0.546, 0.225, 0.361))
    chart_data.add_series("Híbrido (Mac PL) − Dense20 vetorial", (0.080, -0.156, 0.000, -0.168, -0.069, -0.442, 0.067, -0.043, 0.620))

    ch_shape = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.42), Inches(1.18), Inches(12.49), Inches(4.78), chart_data)
    chart = ch_shape.chart
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.TOP
    chart.legend.include_in_layout = False
    chart.legend.font.name = FONT_NAME
    chart.legend.font.size = fpt(18)
    plot = chart.plots[0]
    plot.gap_width = 85
    plot.overlap = -20
    plot.has_data_labels = True
    plot.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    plot.data_labels.number_format = "+0.00;-0.00;0.00"
    plot.data_labels.font.name = FONT_NAME
    plot.data_labels.font.size = fpt(12, enforce_min=False)
    plot.data_labels.font.bold = True

    plot.series[0].invert_if_negative = False
    plot.series[0].format.fill.solid()
    plot.series[0].format.fill.fore_color.rgb = SENAC_BLUE
    plot.series[1].invert_if_negative = False
    plot.series[1].format.fill.solid()
    plot.series[1].format.fill.fore_color.rgb = SENAC_ORANGE

    va = chart.value_axis
    va.has_title = True
    va.axis_title.text_frame.text = "Δ Macro-F1 (p.p.)"
    va.axis_title.text_frame.paragraphs[0].font.name = FONT_NAME
    va.axis_title.text_frame.paragraphs[0].font.size = fpt(16, enforce_min=False)
    va.axis_title.text_frame.paragraphs[0].font.bold = True
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

    add_bottom_strip(
        s, 6.02, 0.74,
        [
            [("Empate prático: ", True, False, SENAC_BLUE), ("toda diferença fica abaixo de 0,8 p.p. (média +0,23 p.p. vs. CNN e −0,01 p.p. vs. Dense20; 16/36 positivos)", False, False, TEXT_DARK)],
        ],
        font_size=18,
    )

    # ===============================================================
    # 39. PAPEL DO CONTROLE Dense20 (ANTIGO 41 — CLARO E DIDATICO)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Por que o controle clássico (Dense20) foi decisivo?", next_lbl())
    s39_l = [
        "Comparando só Híbrido vs. CNN, o Híbrido parece vencer em 6 de 9 bases:",
        "EMNIST +0,76 p.p. · SVHN +0,55 p.p. · FER2013 +0,36 p.p. · MNIST +0,32 p.p.",
    ]
    s39_r = [
        "Trocando os qubits por tanh(20) clássica, o Dense20 obtém os mesmos ganhos:",
        "EMNIST 88,64% (vs. 88,47%) · GTSRB 99,63% (vs. 99,59%) · CIFAR-10 73,39% (vs. 73,32%).",
    ]
    h_s39 = max(
        estimate_card_height(5.88, body_text=s39_l, font_size=18, space_after=8, bullet=False),
        estimate_card_height(5.88, body_text=s39_r, font_size=18, space_after=8, bullet=False),
    )
    h_s39 = min(2.90, max(2.40, h_s39))
    add_card(s, 0.42, 0.96, 5.88, h_s39, "1. Sem o controle: falso 'ganho quântico'", body_text=s39_l, alert=True, font_size=18, title_size=19, space_after=8, auto_height=False)
    arr39 = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(6.40), Inches(0.96 + h_s39 / 2.0 - 0.18), Inches(0.53), Inches(0.36))
    arr39.fill.solid()
    arr39.fill.fore_color.rgb = SENAC_ORANGE
    arr39.line.fill.background()
    add_card(s, 7.03, 0.96, 5.88, h_s39, "2. Com o Dense20 (clássico): o ganho some", body_text=s39_r, font_size=18, title_size=19, space_after=8, auto_height=False)

    add_card(
        s, 0.42, 0.96 + h_s39 + 0.30, 12.49, 2.75,
        "Conclusão: o mérito é do gargalo de 20 neurônios, não dos qubits",
        items=[
            [("Causa real: ", True, False, SENAC_BLUE), ("comprimir features128 → 20 regulariza a cabeça e explica a melhora sobre a CNN original.", False, False, TEXT_DARK)],
            [("Parâmetros (C=1, K=10): ", True, False, SENAC_BLUE), ("CNN usa 201,1k; Dense20 vetorial (86,2k) e Híbrido (86,4k) reduzem 57% igualmente (mantendo 66,9k do extrator congelado).", False, False, TEXT_DARK)],
        ],
        font_size=19, title_size=20, space_after=10,
    )

    # ===============================================================
    # 40. COMPLEXIDADE DO DOMÍNIO (ANTIGO 42 — CLARO E OBVIO)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "O que define o Macro-F1 é a base, não o modelo", next_lbl(), "Elaborado pelo autor (2026).")
    add_textbox(
        s, 0.35, 0.78, 12.63, 0.42,
        "Macro-F1 do Híbrido por base — variação entre bases (>52 p.p.) supera 50× a entre modelos (≤1,1 p.p.)",
        font_size=17, color=TEXT_DARK, align=PP_ALIGN.CENTER, enforce_min=False,
    )
    cd39 = CategoryChartData()
    cd39.categories = ["CIFAR-100C", "FER2013", "CIFAR-10", "EMNIST", "F-MNIST", "SVHN", "KMNIST", "MNIST"]
    vals40 = (47.1, 48.5, 73.3, 88.5, 91.9, 92.6, 98.6, 99.3)
    cd39.add_series("Macro-F1 do híbrido (%)", vals40)
    ch39 = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.45), Inches(1.22), Inches(12.43), Inches(3.82), cd39).chart
    ch39.has_legend = False
    p39 = ch39.plots[0]
    p39.has_data_labels = True
    p39.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    p39.data_labels.number_format = '0.0"%"'
    p39.data_labels.font.name = FONT_NAME
    p39.data_labels.font.size = fpt(18)
    p39.data_labels.font.bold = True
    bar_colors_40 = [BAD_RED, BAD_RED, SENAC_BLUE_MID, SENAC_BLUE_MID, SENAC_BLUE_MID, SENAC_BLUE_MID, SENAC_BLUE, SENAC_BLUE]
    for pt_idx, pt_col in enumerate(bar_colors_40):
        pt = p39.series[0].points[pt_idx]
        pt.format.fill.solid()
        pt.format.fill.fore_color.rgb = pt_col

    ch39.value_axis.has_title = True
    ch39.value_axis.axis_title.text_frame.text = "Macro-F1 de teste (%)"
    ch39.value_axis.axis_title.text_frame.paragraphs[0].font.name = FONT_NAME
    ch39.value_axis.axis_title.text_frame.paragraphs[0].font.size = fpt(16, enforce_min=False)
    ch39.value_axis.axis_title.text_frame.paragraphs[0].font.bold = True
    ch39.value_axis.minimum_scale = 0
    ch39.value_axis.maximum_scale = 114
    ch39.value_axis.major_gridlines.format.line.color.rgb = RGBColor(218, 224, 232)
    ch39.value_axis.tick_labels.font.name = FONT_NAME
    ch39.value_axis.tick_labels.font.size = fpt(18)
    ch39.category_axis.tick_labels.font.name = FONT_NAME
    ch39.category_axis.tick_labels.font.size = fpt(18)

    add_card(
        s, 0.45, 5.10, 12.43, 1.68,
        "Leitura prática",
        items=[
            [("Na mesma base: ", True, False, SENAC_BLUE), ("os 8 modelos variam só 0,09 p.p. (KMNIST) a 1,12 p.p. (EMNIST) — o teto vem das features128", False, False, TEXT_DARK)],
            [("Bases difíceis (vermelho): ", True, False, BAD_RED), ("CIFAR-100 Coarse (5 classes finas/superclasse) e FER2013 (82 amostras de desgosto). GTSRB (99,6%) vem a seguir.", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=4, line_spacing=1.05, auto_height=False,
    )

    # ===============================================================
    # 41. GTSRB: INTERPRETAÇÃO CAUTELOSA
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "GTSRB: números altos, interpretação cautelosa", next_lbl())
    s41_c1 = "3.990 de 5.876 imagens de teste (67,9%) pertencem a tracks físicos já presentes no treino (quadros correlacionados da mesma placa)."
    s41_c2 = "Mesmo com F1 observado de 100%, o IC 95% de Jeffreys vai de 94,15% a 99,96% (P(F1 > 99%) = 46,74%)."
    _, h41_1 = add_card(s, 5.75, 1.15, 7.05, 2.55, "Por que exigir cautela?", body_text=s41_c1, alert=True, font_size=19, title_size=20)
    _, h41_2 = add_card(s, 5.75, 1.15 + h41_1 + 0.28, 7.05, 2.35, "Incerteza bayesiana (classe 0, N = 31)", body_text=s41_c2, font_size=19, title_size=20)
    tot_h41 = h41_1 + 0.28 + h41_2

    left_box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.55), Inches(1.15), Inches(4.85), Inches(tot_h41))
    left_box.adjustments[0] = 0.06
    left_box.fill.solid()
    left_box.fill.fore_color.rgb = SENAC_BLUE_LIGHT
    left_box.line.color.rgb = SENAC_BLUE
    ltf = left_box.text_frame
    ltf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for idx, line in enumerate(["99,365%   CNN", "99,633%   Dense20", "99,590%   Híbrido"]):
        p = ltf.paragraphs[0] if idx == 0 else ltf.add_paragraph()
        p.alignment = PP_ALIGN.CENTER
        p.space_after = Pt(18 if idx < 2 else 0)
        r = p.add_run()
        r.text = line
        r.font.name = FONT_NAME
        r.font.size = fpt(26)
        r.font.bold = True
        r.font.color.rgb = SENAC_BLUE

    # ===============================================================
    # 42. EXPLICABILIDADE POR OCLUSÃO 8×8 (ANTIGO 44 — SEM GRAD-CAM, GUIA DE LEITURA)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Explicabilidade por oclusão 8×8: como ler os próximos slides",
        next_lbl(),
        "Elaborado pelo autor (2026), com base em Zeiler e Fergus (2014).",
    )
    oc_left = [
        "Ocultamos um bloco por vez em uma grade 8×8 (64 posições) sobre imagens curadas (sem duplicatas ou tracks conhecidos).",
        "Aplicamos duas perturbações: preenchimento pela média da imagem ou desfoque gaussiano.",
        "Medimos nos 8 modelos quanto a margem cai e quantos blocos fazem o modelo trocar a previsão.",
    ]
    oc_right = [
        "Canto superior esquerdo: entrada original e classe verdadeira.",
        "8 mapas seguintes: resposta de CNN, Dense20 e Híbridos (Win/Mac × PL/Qiskit) na mesma imagem.",
        "Título de cada mapa: classe prevista, 'X/64 trocas' (blocos que mudam a decisão) e maior queda de margem.",
    ]
    h_oc = max(
        estimate_card_height(6.05, items=oc_left, font_size=18, space_after=10, line_spacing=1.10),
        estimate_card_height(6.05, items=oc_right, font_size=18, space_after=10, line_spacing=1.10),
    )
    h_oc = min(4.05, max(3.35, h_oc))
    add_card(s, 0.45, 0.92, 6.05, h_oc, "O que vamos mostrar nos painéis", items=oc_left, font_size=18, title_size=19, space_after=10, line_spacing=1.10, auto_height=False)
    add_card(s, 6.83, 0.92, 6.05, h_oc, "Como ler cada painel 3×3", items=oc_right, font_size=18, title_size=19, space_after=10, line_spacing=1.10, auto_height=False)

    # Legenda de cores vermelho vs azul
    leg_y = 0.92 + h_oc + 0.28
    leg_h = max(1.25, 6.68 - leg_y)
    badge_r = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.45), Inches(leg_y), Inches(6.05), Inches(leg_h))
    badge_r.adjustments[0] = 0.08
    badge_r.fill.solid()
    badge_r.fill.fore_color.rgb = BAD_RED_LIGHT
    badge_r.line.color.rgb = BAD_RED
    badge_r.line.width = Pt(1.5)
    rtf = badge_r.text_frame
    rtf.word_wrap = True
    rtf.vertical_anchor = MSO_ANCHOR.MIDDLE
    rtf.margin_left = Inches(0.16)
    rtf.margin_right = Inches(0.14)
    add_rich_paragraphs(
        rtf,
        [[("VERMELHO: ", True, False, BAD_RED), ("ocultar este bloco REDUZ a confiança — região decisiva que sustenta a previsão do modelo.", False, False, TEXT_DARK)]],
        font_size=18, space_after=0, bullet=False, line_spacing=1.12,
    )

    badge_b = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.83), Inches(leg_y), Inches(6.05), Inches(leg_h))
    badge_b.adjustments[0] = 0.08
    badge_b.fill.solid()
    badge_b.fill.fore_color.rgb = SENAC_BLUE_LIGHT
    badge_b.line.color.rgb = SENAC_BLUE
    badge_b.line.width = Pt(1.5)
    btf = badge_b.text_frame
    btf.word_wrap = True
    btf.vertical_anchor = MSO_ANCHOR.MIDDLE
    btf.margin_left = Inches(0.16)
    btf.margin_right = Inches(0.14)
    add_rich_paragraphs(
        btf,
        [[("AZUL: ", True, False, SENAC_BLUE), ("ocultar este bloco AUMENTA a confiança — região que competia contra a classe prevista.", False, False, TEXT_DARK)]],
        font_size=18, space_after=0, bullet=False, line_spacing=1.12,
    )

    # ===============================================================
    # 43. PAINÉIS CAUSAIS DE OCLUSÃO — RGB
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Painéis causais de oclusão: domínios RGB", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, SLIDE_FIG_DIR / "painel_oclusao_gtsrb_07_media_slide.png", 0.35, 0.80, 6.10, 4.95)
    add_textbox(
        s, 0.35, 5.80, 6.10, 0.96,
        "gtsrb_07 (real cl. 3): CNN/Vet acertam (3–6/64); D20 img. prevê cl. 25; Híbridos cl. 10 (10–15/64, até +9,02).",
        font_size=18, color=TEXT_DARK, align=PP_ALIGN.CENTER, line_spacing=1.04,
    )
    add_picture_fit(s, SLIDE_FIG_DIR / "painel_oclusao_cifar100_coarse_01_desfoque_slide.png", 6.88, 0.80, 6.10, 4.95)
    add_textbox(
        s, 6.88, 5.80, 6.10, 0.96,
        "cifar100_01 (insects): 8 acertam; CNN/Vet 0/64 trocas; D20 2/64; Híbridos 3/64 p/ flowers (+1,51).",
        font_size=18, color=TEXT_DARK, align=PP_ALIGN.CENTER, line_spacing=1.04,
    )

    # ===============================================================
    # 44. PAINÉIS CAUSAIS DE OCLUSÃO — MONOCROMÁTICOS
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Painéis causais de oclusão: monocromáticos", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, SLIDE_FIG_DIR / "painel_oclusao_fashion_mnist_06_media_slide.png", 0.35, 0.80, 6.10, 4.95)
    add_textbox(
        s, 0.35, 5.80, 6.10, 0.96,
        "fashion_06 (pulôver): CNN/Vet acertam cl. 2 (23–26/64); D20 e Híbridos partem da cl. 6 (16 e 31/64).",
        font_size=18, color=TEXT_DARK, align=PP_ALIGN.CENTER, line_spacing=1.04,
    )
    add_picture_fit(s, SLIDE_FIG_DIR / "painel_oclusao_mnist_06_desfoque_slide.png", 6.88, 0.80, 6.10, 4.95)
    add_textbox(
        s, 6.88, 5.80, 6.10, 0.96,
        "mnist_06 (dígito '2'): só D20 img. acerta (17/64); CNN, Vet e Híbridos preveem '7' (até +10,46).",
        font_size=18, color=TEXT_DARK, align=PP_ALIGN.CENTER, line_spacing=1.04,
    )

    # ===============================================================
    # 45. CUSTO COMPUTACIONAL POR ETAPA (ANTIGO 47 — SEM CNN b128 fp16 / aug2*, FONTES GRANDES)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Custo computacional por etapa (100 épocas, lote 128)", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, SLIDE_FIG_DIR / "fig_48_tempos_etapas_slide.png", 0.20, 0.82, 8.65, 5.92)
    add_card(
        s, 8.98, 0.90, 4.10, 5.75,
        "Gargalo da simulação",
        items=[
            [("36 híbridos: ", True, False, BAD_RED), ("503,66 h (21 dias) vs. 18 vetoriais: 558,88 s (9,3 min) — 778× a 2.854×", False, False, TEXT_DARK)],
            [("Mais rápido: ", True, False, OK_GREEN), ("Dense20 vet. Mac (194,86 s; 1.019× vs. Mac PL)", False, False, TEXT_DARK)],
            [("Melhor híbrido: ", True, False, SENAC_BLUE), ("PQC Mac PL (55,17 h) vs. Win QK (200,30 h)", False, False, TEXT_DARK)],
            "CNN FP32: 25,81 h | D20 imagem: 3,32 h",
        ],
        font_size=18, title_size=19, space_after=8, center_in=(0.86, 6.72),
    )

    # ===============================================================
    # 46. FATORES DE ACELERAÇÃO (ANTIGO 48)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Aceleração entre ambientes e simuladores", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, SLIDE_FIG_DIR / "fig_fatores_aceleracao_slide.png", 0.20, 0.82, 8.65, 5.92)
    add_card(
        s, 8.98, 0.90, 4.10, 5.75,
        "Razões exatas (18/18 pares)",
        items=[
            [("iMac M4 vs. Windows: ", True, False, OK_GREEN), ("1,82× no PennyLane e 1,36× no Qiskit (1,87× vs. Linux no vetorial)", False, False, TEXT_DARK)],
            [("PennyLane vs. Qiskit: ", True, False, OK_GREEN), ("2,68× no Mac e 2,00× no Windows", False, False, TEXT_DARK)],
            [("PQC Mac PennyLane: ", True, False, SENAC_BLUE), ("3,63× mais rápido que Win Qiskit com mesmo Macro-F1 (82,17%; Δ < 0,05 p.p.)", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=10, center_in=(0.86, 6.72),
    )

    # ===============================================================
    # 47. TELEMETRIA DE HARDWARE E I/O (ANTIGO 49)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Telemetria de hardware e I/O (campanha 100 épocas)", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, SLIDE_FIG_DIR / "fig_48_telemetria_hardware_io_slide.png", 0.20, 0.82, 8.65, 5.92)
    add_card(
        s, 8.98, 0.90, 4.10, 5.75,
        "Assinaturas de hardware",
        items=[
            [("Mac (M4): ", True, False, SENAC_BLUE), ("384–389% CPU (≈4 núcleos), 2,56–2,94 GiB RSS; GPU AGX 0,00–0,51%* e I/O proj. 3,2–8,5* GiB", False, False, TEXT_DARK)],
            [("Windows (PQC): ", True, False, BAD_RED), ("316–347% CPU, GPU ociosa (3,7–4,0%) e 456 GiB leitura / 165 GiB escrita", False, False, TEXT_DARK)],
            [("Linux/WSL2: ", True, False, OK_GREEN), ("GPU RTX A2000 ativa (24–43%, 3,0–3,6 GiB VRAM) e baixo I/O", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=8, center_in=(0.86, 6.72),
    )

    # ===============================================================
    # 48. SENSORES MACMON NO iMac M4 (ANTIGO 50)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Sensores macmon e energia no iMac M4", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, SLIDE_FIG_DIR / "fig_48_mac_hardware_sensores_macmon_slide.png", 0.20, 0.80, 7.75, 5.96)
    add_card(
        s, 8.08, 0.90, 5.00, 5.75,
        "Perfil eletrotérmico (M4)",
        items=[
            [("Potência CPU: ", True, False, SENAC_BLUE), ("15,22 W (PL) vs. 15,15 W (QK); GPU ≈ 0,00 W", False, False, TEXT_DARK)],
            [("Térmica / clock: ", True, False, SENAC_BLUE), ("89,0 °C / 87,6 °C; P-cores em 3,39 GHz (vs. 4,45 GHz clássico)", False, False, TEXT_DARK)],
            [("Energia (100 ép.*): ", True, False, OK_GREEN), ("946,7 Wh (PL) vs. 2.332,7 Wh (QK) — economia proj. 2,46×", False, False, TEXT_DARK)],
            [("Escopo: ", True, False, TEXT_MUTED), ("potência/temp. de CPU via macmon existem só no Apple M4 (Windows tem CPU/GPU/disco no slide 47)", False, False, TEXT_MUTED)],
        ],
        font_size=18, title_size=19, space_after=8, center_in=(0.84, 6.74),
    )

    # ===============================================================
    # 49. TELEMETRIA COMPLEMENTAR NO iMac M4 (ANTIGO 51)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Telemetria complementar no iMac M4 (27 sessões, 1 ép.)", next_lbl(), "Elaborado pelo autor (2026).")
    add_picture_fit(s, SLIDE_FIG_DIR / "fig_48_mac_hardware_io_complementar_slide.png", 0.20, 0.82, 8.65, 5.92)
    add_card(
        s, 8.98, 0.90, 4.10, 5.75,
        "Confirmado no Apple M4",
        items=[
            [("100% em CPU: ", True, False, SENAC_BLUE), ("GPU Apple AGX em 0,00%–0,51% (potência ≤ 0,03 W)", False, False, TEXT_DARK)],
            [("Regime macmon: ", True, False, SENAC_BLUE), ("~15,2 W CPU, 87,6–89,0 °C, P-cores em 3,39 GHz", False, False, TEXT_DARK)],
            [("I/O baixo: ", True, False, OK_GREEN), ("32×–71× menos leitura projetada que Windows", False, False, TEXT_DARK)],
            [("Energia (100 ép.*): ", True, False, OK_GREEN), ("PL 0,95 kWh vs. QK 2,33 kWh (2,46× economia)", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=8, center_in=(0.86, 6.72),
    )

    # ===============================================================
    # 49a. TEMPO ATÉ best.keras VS. 100 ÉPOCAS E MELHOR ÉPOCA (72 MODELOS)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Tempo até best.keras vs. 100 épocas e melhor época",
        next_lbl(),
        "Elaborado pelo autor (2026).",
    )
    add_picture_fit(s, SLIDE_FIG_DIR / "fig_48_tempo_100ep_vs_melhor_epoca_slide.png", 0.25, 0.80, 12.83, 5.05)
    add_bottom_strip(
        s, 5.92, 0.84,
        [
            [("72 modelos: ", True, False, SENAC_BLUE), ("532,9 → 177,0 h até best.keras (−66,8%; med. e* = 30)", False, False, TEXT_DARK)],
            [("36 híbridos: ", True, False, SENAC_BLUE), ("503,7 → 150,0 h (−70,2%; med. 26,5) vs. CNN 24,2/25,8 h (−6%)", False, False, TEXT_DARK)],
        ],
        font_size=18,
    )

    # ===============================================================
    # 49b. TRAJETÓRIAS TEMPORAIS DE MACRO-F1 (CNN FP32 VS. PQCs - ZOOM)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Trajetórias temporais de Macro-F1: CNN FP32 vs. PQCs",
        next_lbl(),
        "Elaborado pelo autor (2026). Recorte ampliado no platô superior de convergência.",
    )
    add_picture_fit(s, FIG_DIR / "fig_48_metricas_por_tempo_cnn_pqc.png", 0.25, 0.80, 12.83, 5.95)

    # ===============================================================
    # 49c. CUSTO ATÉ best.keras E PARADA ANTECIPADA (CNN FP32 VS. PQCs - ZOOM)
    # ===============================================================
    s = new_slide(prs)
    add_chrome(
        s,
        "Custo até best.keras e parada antecipada: CNN FP32 vs. PQCs",
        next_lbl(),
        "Elaborado pelo autor (2026).",
    )
    add_picture_fit(s, FIG_DIR / "fig_48_eficiencia_melhor_epoca_patience15_cnn_pqc.png", 0.25, 0.80, 12.83, 5.05)
    add_bottom_strip(
        s, 5.92, 0.84,
        [
            [("Até best.keras: ", True, False, SENAC_BLUE), ("PQCs caem ~70% (16,4–58,8 h) vs. CNN 24,2 h (−6%)", False, False, TEXT_DARK)],
            [("patience=15: ", True, False, SENAC_BLUE), ("28/36 PQCs sem perda (máx. 0,15 p.p. FER2013) vs. 8/9 CNN (até 1,16 p.p.)", False, False, TEXT_DARK)],
        ],
        font_size=18,
    )

    # ===============================================================
    # 50. SÍNTESE: HIPÓTESE, DADOS E COMPROMISSOS
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Síntese: o que a hipótese e os dados dizem", next_lbl())
    synth_rows = [
        ("✓", OK_GREEN, "Estabilidade nas 9 bases (7 a 47 classes): médias globais entre 81,94% e 82,23%"),
        ("✓", OK_GREEN, "Paridade preditiva: Δ Híb. − Dense20 de −0,449 a +0,620 p.p.; PL vs. QK < 0,05 p.p."),
        ("✓", OK_GREEN, "Sem vantagem quântica: ganho sobre a CNN vem do gargalo Dense20"),
        ("✗", BAD_RED, "Trade-offs críticos: custo 778×–2.854× maior, ECE 36,62% no FER2013 e oclusão expõe divergências"),
    ]
    for idx, (sym, scol, stxt) in enumerate(synth_rows):
        ry = 0.92 + idx * 0.88
        row_bg = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.45), Inches(ry), Inches(12.43), Inches(0.74))
        row_bg.adjustments[0] = 0.08
        row_bg.fill.solid()
        row_bg.fill.fore_color.rgb = BAD_RED_LIGHT if sym == "✗" else SENAC_BLUE_ALT
        row_bg.line.color.rgb = BAD_RED if sym == "✗" else BORDER_GRAY
        tf = row_bg.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = Inches(0.18)
        p = tf.paragraphs[0]
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
        s, 0.45, 4.55, 12.43, 2.10,
        "Comparação operacional e literatura",
        body_text="Com features128, o híbrido mantém alta separabilidade onde NNQE (filtro fixo) caiu para 36,0% (CIFAR-10) e 73,4% (GTSRB). Entre híbridos, PQC Mac PennyLane (55,17 h) lidera; no geral, Dense20 vetorial Mac entrega paridade em 194,86 s.",
        font_size=19, title_size=20, line_spacing=1.14,
    )

    # ===============================================================
    # 51. RETOMADA DO PROBLEMA E OBJETIVOS
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Conclusão: retomada do problema e objetivos", next_lbl())
    add_row_cards(
        s,
        [
            [("Campanha integralmente auditada: ", True, False, SENAC_BLUE), ("9 bases, 72 checkpoints (mais 36 de balanceamento e 27 de telemetria no iMac M4), avaliados por Macro-F1", False, False, TEXT_DARK)],
            [("Circuito de Senokosov et al. (2024): ", True, False, SENAC_BLUE), ("convergência estável e paridade com CNN e Dense20, com gradientes ativos nos 4 ramos de 5 qubits", False, False, TEXT_DARK)],
            [("Sem superioridade quântica irrestrita: ", True, False, SENAC_BLUE), ("sem o controle Dense20, ganhos sobre a CNN seriam falsos positivos", False, False, TEXT_DARK)],
            [("Eficiência operacional: ", True, False, SENAC_BLUE), ("iMac M4 + PennyLane é 3,63× mais rápido e 2,46× mais econômico em energia que Win/Mac Qiskit, mas 1.019× mais lento que Dense20 vetorial Mac", False, False, TEXT_DARK)],
        ],
        y_start=0.98, row_h=1.28, gap=0.18, numbered=False, font_size=19,
    )

    # ===============================================================
    # 52. CONTRIBUIÇÕES PARA A COMPUTAÇÃO
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Contribuições para a Computação", next_lbl())
    add_row_cards(
        s,
        [
            [("Benchmark padronizado em 9 bases (72 modelos): ", True, False, SENAC_BLUE), ("supera recortes binários e cobre as 20 superclasses do CIFAR-100 Coarse em Macro-F1", False, False, TEXT_DARK)],
            [("Controle Dense20 e contabilidade paramétrica: ", True, False, SENAC_BLUE), ("evita falsos positivos arquiteturais e separa pesos da cabeça vs. inferência completa", False, False, TEXT_DARK)],
            [("Auditoria de calibração, Bayes e explicabilidade: ", True, False, SENAC_BLUE), ("ECE/NLL/Brier, 1.336 posteriores, 576 Grad-CAM e 73.728 oclusões (ρ = 0,002)", False, False, TEXT_DARK)],
            [("Telemetria multiplataforma de hardware e energia: ", True, False, SENAC_BLUE), ("speedups exatos, CPU, RSS, GPU RTX/AGX, I/O e sensores macmon no Apple M4", False, False, TEXT_DARK)],
            [("Auditoria crítica de dados e literatura: ", True, False, SENAC_BLUE), ("tracks no GTSRB (67,9%), duplicatas/conflitos no FER2013 e divergências em artigos", False, False, TEXT_DARK)],
        ],
        y_start=0.92, row_h=1.04, gap=0.14, numbered=True, font_size=18,
    )

    # ===============================================================
    # 53. LIMITAÇÕES E TRABALHOS FUTUROS
    # ===============================================================
    s = new_slide(prs)
    add_chrome(s, "Limitações e trabalhos futuros", next_lbl())
    add_styled_table(
        s, 0.42, 0.94, 12.49, 5.75,
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
    # 54. OBRIGADO
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
    add_picture_fit(s, FIG_DIR / "balanceamento_oversampling_silva2025.png", 0.50, 0.88, 5.95, 3.70)
    add_textbox(s, 0.50, 4.62, 5.95, 0.42, "Sobreamostragem (oversampling)", font_size=18, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER)
    add_picture_fit(s, FIG_DIR / "balanceamento_undersampling_silva2025.png", 6.85, 0.88, 5.95, 3.70)
    add_textbox(s, 6.85, 4.62, 5.95, 0.42, "Subamostragem (undersampling)", font_size=18, bold=True, color=SENAC_BLUE, align=PP_ALIGN.CENTER)
    add_bottom_strip(
        s, 5.20, 1.24,
        [
            "Estratégias de dados e de algoritmo (class_weight) testadas em 36 execuções preliminares",
            "Validação e teste mantêm sempre a distribuição original; avaliação primária em Macro-F1",
        ],
        font_size=18,
    )

    # A2: Calibração probabilística (FER2013)
    s = new_slide(prs)
    add_chrome(s, "Apoio A2: calibração probabilística no FER2013", "A2", "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "figura_28_calibracao_fer.png", 0.30, 0.84, 7.35, 5.90)
    add_card(
        s, 7.80, 0.90, 5.10, 5.75,
        "Confiança excessiva nos erros",
        items=[
            [("CNN FP32 (LS 0,05): ", True, False, OK_GREEN), ("ECE = 2,08%, NLL = 1,281, conf. nos erros = 42,76%", False, False, TEXT_DARK)],
            [("D20 imagem: ", True, False, SENAC_BLUE), ("ECE = 18,38%, erros = 60,47%", False, False, TEXT_DARK)],
            [("Vetorial Mac: ", True, False, SENAC_BLUE), ("ECE = 31,43%, erros = 75,45%", False, False, TEXT_DARK)],
            [("PQC Mac PL: ", True, False, BAD_RED), ("ECE = 36,62%, NLL = 2,497, conf. nos erros = 82,82% (requer temperature scaling)", False, False, TEXT_DARK)],
        ],
        font_size=18, title_size=19, space_after=8, center_in=(0.86, 6.72),
    )

    # A3: Diagnósticos quânticos (gradientes e ruído/shots)
    s = new_slide(prs)
    add_chrome(s, "Apoio A3: gradientes por ramo e ruído/shots", "A3", "Elaborado pelo autor (2026).")
    add_picture_fit(s, FIG_DIR / "figura_19_gradientes.png", 0.35, 0.84, 6.20, 4.35)
    add_picture_fit(s, FIG_DIR / "figura_22_ruido_shots.png", 6.78, 0.84, 6.20, 4.35)
    add_bottom_strip(
        s, 5.34, 1.32,
        [
            [("Gradientes (Ramos 1–4): ", True, False, SENAC_BLUE), ("MNIST decai (0,13 → 10⁻⁷); FER2013 segue ativo (4,3×10⁻² a 1,1×10⁻¹) até a época 100.", False, False, TEXT_DARK)],
            [("Ruído e shots (Mac/PL): ", True, False, SENAC_BLUE), ("fidelidade cai a 0,51 (ruído 2,0), mas Δ Macro-F1 típico < 0,10 p.p. (máx. −0,38 p.p. CIFAR-10).", False, False, TEXT_DARK)],
        ],
        font_size=18,
    )

    # A4: Resultados originais de Senokosov et al. (2024)
    s = new_slide(prs)
    add_chrome(
        s,
        "Apoio A4: resultados originais de Senokosov et al. (2024)",
        "A4",
        "Extraído de Senokosov et al. (2024) (arXiv:2304.09224, Figura 5).",
    )
    add_picture_fit(s, FIG_DIR / "fig_arxiv2304_mnist_loss_acc.png", 0.40, 0.90, 12.53, 4.10)
    add_bottom_strip(
        s, 5.18, 1.45,
        [
            "MNIST (10 épocas, lote 16, SGD): HQNN-Parallel atingiu 99,21% (45.194 pesos) vs. CNN 98,71% (372.234 pesos)",
            "No artigo original: Medical MNIST 99,97% (vs. 99,96%) e CIFAR-10 82,78% (vs. 82,64%) com 6×5 qubits",
        ],
        font_size=18,
    )

    # A5: Riscos e limitações metodológicas
    s = new_slide(prs)
    add_chrome(s, "Apoio A5: riscos e limitações metodológicas", "A5")
    add_row_cards(
        s,
        [
            "Sem emaranhamento cruzado entre os quatro subcircuitos independentes de 5 qubits",
            "Uma semente por configuração (seed=42): sem estimativa de variância inter-sementes",
            "Dense20 imagem, vetorial e híbrido diferem em camadas e aumento: sem fator causal único",
            "Dependências auditadas: 67,9% de tracks no GTSRB e 7,02% de duplicatas + 57 conflitos no FER2013",
            "Restrição integral à simulação clássica local em CPU, sem execução em QPU física",
        ],
        y_start=0.94, row_h=1.02, gap=0.14, numbered=True, font_size=19,
    )

    # A6: Siglas principais
    s = new_slide(prs)
    add_chrome(s, "Apoio A6: siglas principais", "A6")
    add_styled_table(
        s, 0.42, 0.98, 6.08, 5.60,
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
        s, 6.83, 0.98, 6.08, 5.60,
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

    if len(sys.argv) > 1:
        out_path = Path(sys.argv[1])
        prs.save(out_path)
        print(f"PPTX salvo em: {out_path} ({len(prs.slides)} slides)")
        return

    saved_paths = []
    for target_p in (OUTPUT_ALT_PPTX, OUTPUT_PPTX):
        try:
            prs.save(target_p)
            saved_paths.append(target_p)
            print(f"PPTX salvo em: {target_p} ({len(prs.slides)} slides)")
        except PermissionError:
            print(f"AVISO: {target_p.name} está bloqueado (aberto no PowerPoint).")

    if not saved_paths:
        fallback_p = BASE_DIR / "apresentacao_tcc2_final_revisada.pptx"
        prs.save(fallback_p)
        print(f"PPTX revisado salvo em: {fallback_p} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    build_deck()
