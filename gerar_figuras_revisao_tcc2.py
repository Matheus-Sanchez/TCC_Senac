# -*- coding: utf-8 -*-
"""Gera figuras limpas (300 DPI) de balanceamento, arquiteturas por etapa, comparativo, circuito 5-qubits e oclusao."""

import json
import pathlib
from collections import defaultdict
from html.parser import HTMLParser
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Arc, Rectangle, Ellipse
from matplotlib.ticker import FuncFormatter

OUT_DIR = pathlib.Path(r"C:\Users\matheus.sduda\repos\TCC\TCC_Senac\figuras")
OUT_DIR.mkdir(parents=True, exist_ok=True)

NB_BALANCE = pathlib.Path(
    r"C:\Users\matheus.sduda\repos\teste-modelos-tcc\teste-modelos-tcc\notebooks\training_complete_analysis.ipynb"
)
JSON_OCL = pathlib.Path(
    r"C:\Users\matheus.sduda\Documents\ChatGPT\projeto-do-tcc\outputs\oclusao-completa-2026-11-07\manifesto_completo.json"
)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.edgecolor": "#94A3B8",
    "axes.linewidth": 0.9,
    "grid.color": "#E2E8F0",
    "grid.linestyle": "-",
    "grid.linewidth": 0.6,
    "figure.facecolor": "#FFFFFF",
    "axes.facecolor": "#FFFFFF",
    "text.color": "#0F172A",
    "axes.labelcolor": "#1E293B",
    "xtick.color": "#334155",
    "ytick.color": "#334155",
})

DS_CANONICAL_ORDER = [
    ("mnist", "MNIST"),
    ("fashion_mnist", "Fashion-MNIST"),
    ("kmnist", "KMNIST"),
    ("emnist_balanced", "EMNIST Bal."),
    ("cifar10", "CIFAR-10"),
    ("cifar100_coarse", "CIFAR-100 C."),
    ("svhn", "SVHN"),
    ("gtsrb", "GTSRB"),
    ("fer2013", "FER2013"),
]

MODE_META = [
    ("all_raw", "Original (all_raw)", "#1D4ED8"),
    ("oversample", "Sobreamostragem", "#0F766E"),
    ("class_weight", "Peso na perda", "#D97706"),
    ("undersample", "Subamostragem", "#DC2626"),
]


class _TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_td = False
        self.in_tr = False
        self.rows = []
        self.cur_row = []
        self.cur_cell = []

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.in_tr = True
            self.cur_row = []
        elif tag in ("td", "th") and self.in_tr:
            self.in_td = True
            self.cur_cell = []

    def handle_data(self, data):
        if self.in_td:
            self.cur_cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.in_td:
            self.cur_row.append("".join(self.cur_cell).strip())
            self.in_td = False
        elif tag == "tr" and self.in_tr:
            if self.cur_row:
                self.rows.append(self.cur_row)
            self.in_tr = False


def parse_notebook_table(cell_index: int) -> pd.DataFrame:
    nb = json.loads(NB_BALANCE.read_text(encoding="utf-8"))
    html_str = ""
    for out in nb["cells"][cell_index].get("outputs", []):
        data = out.get("data", {})
        if "text/html" in data:
            html_str = "".join(data["text/html"])
            break
    if not html_str:
        raise RuntimeError(f"HTML table not found in cell {cell_index}")
    parser = _TableParser()
    parser.feed(html_str)
    headers = parser.rows[0][1:]
    data_rows = [r[1:] for r in parser.rows[1:]]
    df = pd.DataFrame(data_rows, columns=headers)
    for col in df.columns:
        if col not in ("dataset", "balance_mode"):
            df[col] = pd.to_numeric(df[col])
    return df


def fmt_pt(val: float, decimals: int = 2) -> str:
    return f"{val:.{decimals}f}".replace(".", ",")


def draw_box(ax, x, y, w, h, text, fc="#F1F5F9", ec="#64748B", lw=1.3, fs=9.2,
             fw="bold", text_color="#0F172A", ls="-", pad=0.004, rsize=0.012, zorder=3):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad={pad},rounding_size={rsize}",
        facecolor=fc, edgecolor=ec, linewidth=lw, linestyle=ls, zorder=zorder
    )
    ax.add_patch(box)
    if text:
        ax.text(
            x + w / 2.0, y + h / 2.0, text,
            ha="center", va="center", fontsize=fs, fontweight=fw,
            color=text_color, zorder=zorder + 1, linespacing=1.25
        )
    return box


def draw_arrow(ax, x1, y1, x2, y2, color="#475569", lw=1.6, rad=0.0, ls="-", zorder=2):
    arr = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>,head_length=5.5,head_width=3.2",
        color=color, linewidth=lw, linestyle=ls,
        connectionstyle=f"arc3,rad={rad}",
        zorder=zorder
    )
    ax.add_patch(arr)


def gerar_figs_balanceamento():
    df = parse_notebook_table(6)

    # 1) Macro-F1 (%) por base e modo de balanceamento (sem suptitle longo duplicado)
    fig, ax = plt.subplots(figsize=(13.2, 5.2), dpi=300)
    x = np.arange(len(DS_CANONICAL_ORDER))
    w = 0.195
    offsets = [-1.5 * w, -0.5 * w, 0.5 * w, 1.5 * w]
    lookup = df.set_index(["dataset", "balance_mode"])

    for (mode, label, color), off in zip(MODE_META, offsets):
        vals = [float(lookup.loc[(ds, mode), "test_macro_f1"]) * 100.0 for ds, _ in DS_CANONICAL_ORDER]
        bars = ax.bar(x + off, vals, width=w * 0.90, color=color, label=label, alpha=0.93, zorder=3)
        for bar, v, (ds, _) in zip(bars, vals, DS_CANONICAL_ORDER):
            if ds in ("svhn", "gtsrb", "fer2013"):
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    v + 1.4,
                    fmt_pt(v, 1),
                    ha="center", va="bottom", fontsize=8.0, fontweight="bold",
                    color=color, rotation=90
                )

    ax.axvspan(5.55, 8.45, color="#FEF3C7", alpha=0.40, zorder=1)
    ax.text(7.0, 114.5, "Bases desbalanceadas (IR > 3x)",
            ha="center", va="top", fontsize=9.2, fontweight="bold", color="#92400E")

    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, lbl in DS_CANONICAL_ORDER], fontsize=10.0, fontweight="bold")
    ax.set_ylim(0, 118)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_ylabel("Macro-F1 de teste (%)", fontsize=10.5, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(
        loc="lower center", bbox_to_anchor=(0.5, 1.02),
        ncol=4, fontsize=9.6, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1"
    )

    out1 = OUT_DIR / "fig_balanceamento_macro_f1.png"
    fig.savefig(out1, dpi=300, bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)
    print("Gerado:", out1)

    # 2A) Tempo de treinamento por base e modo de balanceamento (Fig. 3.4.2-A)
    fig, ax1 = plt.subplots(figsize=(7.6, 5.2), dpi=300)
    for (mode, label, color), off in zip(MODE_META, offsets):
        hrs = [float(lookup.loc[(ds, mode), "training_hours"]) for ds, _ in DS_CANONICAL_ORDER]
        bars = ax1.bar(x + off, hrs, width=w * 0.90, color=color, label=label, alpha=0.93, zorder=3)
        for bar, h_val in zip(bars, hrs):
            if h_val >= 4.4:
                ax1.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    h_val + 0.22,
                    f"{fmt_pt(h_val, 2)} h",
                    ha="center", va="bottom", fontsize=12.2, fontweight="bold", color=color, rotation=90
                )

    ax1.set_xticks(x)
    ax1.set_xticklabels([lbl for _, lbl in DS_CANONICAL_ORDER], fontsize=12.2, fontweight="bold", rotation=25, ha="right")
    ax1.tick_params(axis="y", labelsize=12.2)
    ax1.set_ylim(0, 12.8)
    ax1.set_ylabel("Tempo total de treino (horas)", fontsize=13.0, fontweight="bold")
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 0)))
    ax1.set_title("Tempo de treino por modo (total: 88,86 h)", fontsize=13.8, fontweight="bold", pad=56)
    ax1.grid(True, axis="y", alpha=0.8)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(
        loc="lower center", bbox_to_anchor=(0.5, 1.02),
        ncol=2, fontsize=12.2, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1"
    )

    out2a = OUT_DIR / "fig_342_balanceamento_tempo_treino.png"
    fig.savefig(out2a, dpi=300, bbox_inches="tight", pad_inches=0.08, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out2a)

    # 2B) Variacao de Macro-F1 frente a all_raw (Fig. 3.4.2-B)
    fig, ax2 = plt.subplots(figsize=(8.0, 5.4), dpi=300)
    deltas_meta = MODE_META[1:]
    w2 = 0.24
    offs2 = [-w2, 0.0, w2]
    for (mode, label, color), off in zip(deltas_meta, offs2):
        deltas = [
            (float(lookup.loc[(ds, mode), "test_macro_f1"]) - float(lookup.loc[(ds, "all_raw"), "test_macro_f1"])) * 100.0
            for ds, _ in DS_CANONICAL_ORDER
        ]
        bars = ax2.bar(x + off, deltas, width=w2 * 0.90, color=color, label=label, alpha=0.93, zorder=3)
        for bar, dv, (ds, _) in zip(bars, deltas, DS_CANONICAL_ORDER):
            if abs(dv) >= 1.1:
                va = "top" if dv < 0 else "bottom"
                dy = -0.55 if dv < 0 else 0.45
                if ds == "fer2013" and mode == "class_weight":
                    ax2.text(
                        bar.get_x() + bar.get_width() * 0.90, dv + dy,
                        f"{fmt_pt(dv, 2)}",
                        ha="right", va=va, fontsize=11.0, fontweight="bold", color=color
                    )
                else:
                    ax2.text(
                        bar.get_x() + bar.get_width() / 2.0, dv + dy,
                        f"{fmt_pt(dv, 2)}",
                        ha="center", va=va, fontsize=11.0, fontweight="bold", color=color
                    )

    ax2.axhline(0.0, color="#0F172A", linewidth=1.2, zorder=4)
    ax2.set_xticks(x)
    ax2.set_xticklabels([lbl for _, lbl in DS_CANONICAL_ORDER], fontsize=12.2, fontweight="bold", rotation=25, ha="right")
    ax2.tick_params(axis="y", labelsize=12.2)
    ax2.set_ylim(-24.0, 4.5)
    ax2.set_ylabel("Δ Macro-F1 vs. all_raw (p.p.)", fontsize=13.0, fontweight="bold")
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 0)))
    ax2.set_title("Variação de Macro-F1 frente a all_raw (p.p.)", fontsize=13.8, fontweight="bold", pad=38)
    ax2.grid(True, axis="y", alpha=0.8)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(
        loc="lower center", bbox_to_anchor=(0.5, 1.02),
        ncol=3, fontsize=12.0, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1",
        columnspacing=0.9, handletextpad=0.4
    )

    out2b = OUT_DIR / "fig_342_balanceamento_delta_f1.png"
    fig.savefig(out2b, dpi=300, bbox_inches="tight", pad_inches=0.08, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out2b)


def gerar_fig_oclusao_trocas_globais():
    with open(JSON_OCL, encoding="utf-8") as f:
        m = json.load(f)

    flips_by_ds = defaultdict(lambda: {"desfoque": 0, "media": 0})
    for s in m["summaries"]:
        flips_by_ds[s["dataset"]][s["method"]] += int(s["flips"])

    ds_items = DS_CANONICAL_ORDER

    fig, ax = plt.subplots(figsize=(13.2, 4.9), dpi=300)
    x = np.arange(len(ds_items))
    w = 0.35
    gap = 0.02
    vals_desf = [flips_by_ds[d]["desfoque"] for d, _ in ds_items]
    vals_med = [flips_by_ds[d]["media"] for d, _ in ds_items]

    b1 = ax.bar(x - w / 2 - gap, vals_desf, width=w, color="#0284C7",
                label="Borramento gaussiano", zorder=3)
    b2 = ax.bar(x + w / 2 + gap, vals_med, width=w, color="#DC2626",
                label="Média da imagem", zorder=3)

    for bar, v in zip(b1, vals_desf):
        pct = 100.0 * v / 4096.0
        ax.text(bar.get_x() + bar.get_width() / 2, v + 18, f"{v}\n({fmt_pt(pct, 1)}%)",
                ha="center", va="bottom", fontsize=7.8, fontweight="bold", color="#0369A1")
    for bar, v in zip(b2, vals_med):
        pct = 100.0 * v / 4096.0
        ax.text(bar.get_x() + bar.get_width() / 2, v + 18, f"{v}\n({fmt_pt(pct, 1)}%)",
                ha="center", va="bottom", fontsize=7.8, fontweight="bold", color="#991B1B")

    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, lbl in ds_items], fontsize=10.0, fontweight="bold")
    ax.set_ylim(0, 1180)
    ax.set_ylabel("Trocas de classe\n(em 4.096 oclusões/base)", fontsize=10.0, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.8)
    ax.legend(loc="upper left", fontsize=9.8, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1", ncol=2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    out_path = OUT_DIR / "fig_oclusao_trocas_globais.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_diagrama_etapa1_cnn():
    fig, ax = plt.subplots(figsize=(14.8, 5.2), dpi=300)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    # Container do fluxo global
    top_bg = FancyBboxPatch((0.010, 0.50), 0.980, 0.46,
                            boxstyle="round,pad=0.004,rounding_size=0.012",
                            facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.1, zorder=1)
    ax.add_patch(top_bg)
    ax.text(0.025, 0.935, "Fluxo completo da CNN de origem (treinamento ponta a ponta em FP32)",
            ha="left", va="top", fontsize=10.5, fontweight="bold", color="#1E3A5F", zorder=4)

    # Entrada
    draw_box(ax, 0.022, 0.615, 0.095, 0.210,
             "Entrada\n64×64×C\n(128×128×3)", fc="#E2E8F0", ec="#475569", fs=8.8)

    # Extrator container
    ext_bg = FancyBboxPatch((0.132, 0.565), 0.398, 0.305,
                            boxstyle="round,pad=0.004,rounding_size=0.012",
                            facecolor="#EFF6FF", edgecolor="#3B82F6", linewidth=1.2, linestyle="--", zorder=2)
    ax.add_patch(ext_bg)
    ax.text(0.331, 0.855, "Extrator Convolucional (5 Blocos)",
            ha="center", va="top", fontsize=9.2, fontweight="bold", color="#1D4ED8", zorder=4)
    ax.text(0.331, 0.580, "66.905 pesos (C=1)  |  67.019 pesos (C=3)",
            ha="center", va="bottom", fontsize=8.0, color="#1E40AF", zorder=4)

    draw_arrow(ax, 0.119, 0.720, 0.142, 0.720, color="#334155")

    blocks = [("B1", "32 ch"), ("B2", "48 ch"), ("B3", "64 ch"), ("B4", "96 ch"), ("B5", "128 ch")]
    bx0 = 0.145
    bw = 0.062
    gap = 0.016
    for i, (bname, bch) in enumerate(blocks):
        bx = bx0 + i * (bw + gap)
        draw_box(ax, bx, 0.635, bw, 0.175, f"{bname}\n{bch}", fc="#DBEAFE", ec="#2563EB", fs=8.6)
        if i < len(blocks) - 1:
            draw_arrow(ax, bx + bw + 0.001, 0.722, bx + bw + gap - 0.001, 0.722, color="#2563EB", lw=1.3)

    # Cabeca da CNN original
    head_bg = FancyBboxPatch((0.545, 0.565), 0.432, 0.305,
                             boxstyle="round,pad=0.004,rounding_size=0.012",
                             facecolor="#F0F9FF", edgecolor="#0284C7", linewidth=1.2, linestyle="--", zorder=2)
    ax.add_patch(head_bg)
    ax.text(0.761, 0.855, "Cabeça Original (131.584 + 257K pesos)",
            ha="center", va="top", fontsize=9.2, fontweight="bold", color="#0369A1", zorder=4)

    draw_box(ax, 0.558, 0.735, 0.078, 0.088, "GAP\n(128D)", fc="#E0F2FE", ec="#0284C7", fs=8.4)
    draw_box(ax, 0.558, 0.620, 0.078, 0.088, "GMP\n(128D)", fc="#E0F2FE", ec="#0284C7", fs=8.4)
    draw_arrow(ax, 0.530, 0.730, 0.555, 0.779, color="#0284C7")
    draw_arrow(ax, 0.530, 0.710, 0.555, 0.664, color="#0284C7")

    draw_box(ax, 0.654, 0.640, 0.072, 0.165, "Concat\n(256D)", fc="#BAE6FD", ec="#0369A1", fs=8.4)
    draw_arrow(ax, 0.638, 0.779, 0.652, 0.742, color="#0369A1")
    draw_arrow(ax, 0.638, 0.664, 0.652, 0.702, color="#0369A1")

    draw_box(ax, 0.742, 0.640, 0.128, 0.165, "2× [Drop(0,4) →\nDense(256, SiLU)]", fc="#DBEAFE", ec="#1D4ED8", fs=8.2)
    draw_arrow(ax, 0.728, 0.722, 0.740, 0.722, color="#1D4ED8")

    draw_box(ax, 0.886, 0.640, 0.080, 0.165, "Drop(0,4)\nDense(K)", fc="#1D4ED8", ec="#1E3A8A", fs=8.5, text_color="#FFFFFF")
    draw_arrow(ax, 0.872, 0.722, 0.884, 0.722, color="#1D4ED8")

    # Zoom da estrutura interna do bloco
    bot_bg = FancyBboxPatch((0.080, 0.045), 0.840, 0.375,
                            boxstyle="round,pad=0.004,rounding_size=0.012",
                            facecolor="#F8FAFC", edgecolor="#64748B", linewidth=1.1, zorder=1)
    ax.add_patch(bot_bg)
    ax.text(0.500, 0.395, "Estrutura interna de cada Bloco Convolucional (B1 a B5)",
            ha="center", va="top", fontsize=9.8, fontweight="bold", color="#334155", zorder=4)

    # Linhas de zoom tracejadas saindo da borda inferior do extrator para o bloco inferior
    ax.plot([0.280, 0.085], [0.562, 0.420], color="#94A3B8", linestyle=":", linewidth=1.3, zorder=1)
    ax.plot([0.380, 0.915], [0.562, 0.420], color="#94A3B8", linestyle=":", linewidth=1.3, zorder=1)

    substeps = [
        ("Entrada\ndo bloco", "#E2E8F0", "#475569"),
        ("SepConv2D\n5×5", "#DBEAFE", "#2563EB"),
        ("GroupNorm(16)\n+ SiLU", "#E0F2FE", "#0284C7"),
        ("SepConv2D\n3×3", "#DBEAFE", "#2563EB"),
        ("GroupNorm(16)\n+ SiLU", "#E0F2FE", "#0284C7"),
        ("MaxPool2D\n2×2", "#FEF3C7", "#D97706"),
    ]
    sx0 = 0.105
    sw = 0.114
    sgap = 0.022
    for i, (stxt, sfc, sec) in enumerate(substeps):
        sx = sx0 + i * (sw + sgap)
        draw_box(ax, sx, 0.105, sw, 0.205, stxt, fc=sfc, ec=sec, fs=8.8)
        if i < len(substeps) - 1:
            draw_arrow(ax, sx + sw + 0.002, 0.207, sx + sw + sgap - 0.002, 0.207, color="#475569")

    ax.text(0.298, 0.068, "(passo s=2 no Bloco 1; s=1 nos Blocos 2 a 5)",
            ha="center", va="bottom", fontsize=7.9, color="#475569", style="italic")

    out_path = OUT_DIR / "fig_arq_etapa1_cnn_original.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_diagrama_etapa2_dense20():
    fig, ax = plt.subplots(figsize=(14.8, 5.2), dpi=300)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    # Faixa superior: Etapa 2A (Dense20 sobre imagens)
    bg_a = FancyBboxPatch((0.010, 0.525), 0.980, 0.445,
                          boxstyle="round,pad=0.004,rounding_size=0.012",
                          facecolor="#FFF7ED", edgecolor="#FDBA74", linewidth=1.2, zorder=1)
    ax.add_patch(bg_a)
    ax.text(0.025, 0.945, "Etapa 2A: Dense20 sobre imagens (aumento de dados 50% ativo · Linux)",
            ha="left", va="top", fontsize=10.5, fontweight="bold", color="#9A3412", zorder=4)

    steps_a = [
        (0.025, 0.118, "Imagem +\nAumento", "#E2E8F0", "#475569", "#0F172A"),
        (0.168, 0.165, "Blocos 1–5\n(Congelados)", "#FEF3C7", "#D97706", "#0F172A"),
        (0.358, 0.108, "GAP\n(128D)", "#FEF3C7", "#D97706", "#0F172A"),
        (0.491, 0.125, "Dense(20)\nlinear", "#FFEDD5", "#EA580C", "#0F172A"),
        (0.641, 0.145, "LayerNorm\n+ ReLU", "#FFEDD5", "#EA580C", "#0F172A"),
        (0.811, 0.155, "Dense(K)\nLogits", "#EA580C", "#9A3412", "#FFFFFF"),
    ]
    for i, (bx, bw, txt, fc, ec, tc) in enumerate(steps_a):
        draw_box(ax, bx, 0.625, bw, 0.235, txt, fc=fc, ec=ec, fs=9.2, text_color=tc)
        if i < len(steps_a) - 1:
            nx = steps_a[i + 1][0]
            draw_arrow(ax, bx + bw + 0.003, 0.742, nx - 0.003, 0.742, color="#C2410C")

    ax.text(0.725, 0.550, "Cabeça treinável: 2.620 + 21K pesos",
            ha="center", va="bottom", fontsize=8.4, color="#9A3412", fontweight="bold")

    # Faixa inferior: Etapa 2B (Dense20 vetorial sobre features128)
    bg_b = FancyBboxPatch((0.010, 0.030), 0.980, 0.445,
                          boxstyle="round,pad=0.004,rounding_size=0.012",
                          facecolor="#F0FDF4", edgecolor="#86EFAC", linewidth=1.2, zorder=1)
    ax.add_patch(bg_b)
    ax.text(0.025, 0.450, "Etapa 2B: Extração de features128 e cabeça Dense20 vetorial (Linux e iMac M4)",
            ha="left", va="top", fontsize=10.5, fontweight="bold", color="#166534", zorder=4)

    steps_b = [
        (0.025, 0.165, "Blocos 1–5 + GAP\n(Congelados)", "#FEF3C7", "#D97706", "#0F172A"),
        (0.215, 0.130, "features128\n(.npy · 128D)", "#FEF9C3", "#CA8A04", "#0F172A"),
        (0.370, 0.132, "Dense(128)\n+ ReLU", "#DCFCE7", "#15803D", "#0F172A"),
        (0.527, 0.125, "Dense(20)\nlinear", "#DCFCE7", "#15803D", "#0F172A"),
        (0.677, 0.118, "Ativação\ntanh", "#BBF7D0", "#166534", "#0F172A"),
        (0.820, 0.146, "Dense(K)\nLogits", "#15803D", "#14532D", "#FFFFFF"),
    ]
    for i, (bx, bw, txt, fc, ec, tc) in enumerate(steps_b):
        draw_box(ax, bx, 0.130, bw, 0.235, txt, fc=fc, ec=ec, fs=9.2, text_color=tc)
        if i < len(steps_b) - 1:
            nx = steps_b[i + 1][0]
            draw_arrow(ax, bx + bw + 0.003, 0.247, nx - 0.003, 0.247, color="#15803D")

    ax.text(0.665, 0.055, "Cabeça treinável: 19.092 + 21K pesos (sem aumento de dados)",
            ha="center", va="bottom", fontsize=8.4, color="#166534", fontweight="bold")

    out_path = OUT_DIR / "fig_arq_etapa2_dense20_classicas.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_diagrama_etapa3_hibrida():
    fig, ax = plt.subplots(figsize=(14.8, 5.4), dpi=300)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    bg = FancyBboxPatch((0.010, 0.030), 0.980, 0.940,
                        boxstyle="round,pad=0.004,rounding_size=0.012",
                        facecolor="#FAF5FF", edgecolor="#C4B5FD", linewidth=1.2, zorder=1)
    ax.add_patch(bg)
    ax.text(0.025, 0.945, "Etapa 3: Cabeça Híbrida Quântico-Clássica Paralela (4 × 5 Qubits · Senokosov et al., 2024)",
            ha="left", va="top", fontsize=10.5, fontweight="bold", color="#4C1D95", zorder=4)

    draw_box(ax, 0.028, 0.340, 0.118, 0.280,
             "features128\n(.npy · 128D)\nCongeladas", fc="#FEF9C3", ec="#CA8A04", fs=9.2)
    draw_box(ax, 0.172, 0.340, 0.112, 0.280,
             "Dense(128)\n+ ReLU\n16.512 pesos", fc="#DCFCE7", ec="#15803D", fs=9.0)
    draw_box(ax, 0.308, 0.340, 0.112, 0.280,
             "Dense(20)\nlinear (u)\n2.580 pesos", fc="#DCFCE7", ec="#15803D", fs=9.0)

    draw_arrow(ax, 0.149, 0.480, 0.169, 0.480, color="#15803D")
    draw_arrow(ax, 0.287, 0.480, 0.305, 0.480, color="#15803D")

    # Bloco quantico 4x5
    q_bg = FancyBboxPatch((0.448, 0.095), 0.345, 0.775,
                          boxstyle="round,pad=0.004,rounding_size=0.012",
                          facecolor="#F5F3FF", edgecolor="#7C3AED", linewidth=1.2, linestyle="--", zorder=2)
    ax.add_patch(q_bg)
    ax.text(0.620, 0.852, "Camada Quântica Paralela (4 × 45 = 180 pesos)",
            ha="center", va="top", fontsize=8.8, fontweight="bold", color="#5B21B6", zorder=4)

    branch_ys = [0.680, 0.495, 0.310, 0.125]
    for idx, by in enumerate(branch_ys, start=1):
        sl = f"u[{5*(idx-1)}:{5*idx}]"
        draw_box(ax, 0.464, by, 0.185, 0.125,
                 f"Ramo {idx} · 5 qubits\nEntradas {sl}", fc="#EDE9FE", ec="#6D28D9", fs=8.8)
        draw_arrow(ax, 0.423, 0.480, 0.461, by + 0.062, color="#6D28D9")

        draw_box(ax, 0.674, by, 0.105, 0.125,
                 "5 × ⟨Y⟩\n∈ [-1, 1]", fc="#FCE7F3", ec="#BE185D", fs=8.8)
        draw_arrow(ax, 0.652, by + 0.062, 0.671, by + 0.062, color="#BE185D")

    draw_box(ax, 0.822, 0.340, 0.145, 0.280,
             "Concat(20)\n↓\nDense(K)\nLogits", fc="#0369A1", ec="#0C4A6E", fs=9.4, text_color="#FFFFFF")
    for by in branch_ys:
        draw_arrow(ax, 0.782, by + 0.062, 0.819, 0.480, color="#0369A1")

    ax.text(0.620, 0.052, "Total treinável na cabeça: 19.272 + 21K pesos (sem emaranhamento cruzado entre os 4 ramos)",
            ha="center", va="bottom", fontsize=8.4, color="#4C1D95", fontweight="bold")

    out_path = OUT_DIR / "fig_arq_etapa3_hibrida_4x5.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_diagrama_comparativo_mudancas():
    fig, ax = plt.subplots(figsize=(15.2, 6.2), dpi=300)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    cols = [
        (0.015, 0.135, "Etapa / Modelo"),
        (0.165, 0.125, "Entrada"),
        (0.305, 0.140, "Extrator CNN"),
        (0.460, 0.130, "Pooling / 128D"),
        (0.605, 0.125, "Camada Oculta"),
        (0.745, 0.145, "Gargalo 20D"),
        (0.905, 0.080, "Saída"),
    ]
    for cx, cw, cname in cols:
        draw_box(ax, cx, 0.880, cw, 0.085, cname, fc="#1E293B", ec="#0F172A",
                 fs=9.0, text_color="#FFFFFF", rsize=0.008)

    rows = [
        ("Etapa 1\nCNN Original", "#EFF6FF", "#2563EB", [
            ("Imagem +\nAumento 50%", "#E2E8F0", "#475569", "#0F172A"),
            ("Blocos 1–5\n(Treináveis)", "#DBEAFE", "#2563EB", "#0F172A"),
            ("GAP + GMP\n(256D)", "#DBEAFE", "#2563EB", "#0F172A"),
            ("2× Dense(256)\nSiLU + Drop", "#DBEAFE", "#2563EB", "#0F172A"),
            ("Sem gargalo\n20D", "#F1F5F9", "#94A3B8", "#64748B"),
            ("Dense(K)", "#1D4ED8", "#1E3A8A", "#FFFFFF"),
        ]),
        ("Etapa 2A\nDense20 Imagem", "#FFF7ED", "#EA580C", [
            ("Imagem +\nAumento 50%", "#E2E8F0", "#475569", "#0F172A"),
            ("Blocos 1–5\n(Congelados)", "#FEF3C7", "#D97706", "#0F172A"),
            ("Só GAP (128D)\n[remove GMP]", "#FFEDD5", "#EA580C", "#9A3412"),
            ("Removida\n[sem Dense256]", "#F1F5F9", "#94A3B8", "#64748B"),
            ("Dense(20) +\nLN + ReLU", "#FFEDD5", "#EA580C", "#0F172A"),
            ("Dense(K)", "#EA580C", "#9A3412", "#FFFFFF"),
        ]),
        ("Etapa 2B\nDense20 Vetorial", "#F0FDF4", "#15803D", [
            ("features128\n(.npy fixo)", "#FEF9C3", "#CA8A04", "#0F172A"),
            ("Pré-extraído\n(Congelado)", "#FEF3C7", "#D97706", "#0F172A"),
            ("Vetor 128D\ndeterminístico", "#FEF3C7", "#D97706", "#0F172A"),
            ("Dense(128)\n+ ReLU", "#DCFCE7", "#15803D", "#0F172A"),
            ("Dense(20) +\ntanh clássica", "#BBF7D0", "#15803D", "#14532D"),
            ("Dense(K)", "#15803D", "#14532D", "#FFFFFF"),
        ]),
        ("Etapa 3\nHíbrido 4×5", "#FAF5FF", "#6D28D9", [
            ("features128\n(.npy fixo)", "#FEF9C3", "#CA8A04", "#0F172A"),
            ("Pré-extraído\n(Congelado)", "#FEF3C7", "#D97706", "#0F172A"),
            ("Vetor 128D\ndeterminístico", "#FEF3C7", "#D97706", "#0F172A"),
            ("Dense(128)\n+ ReLU", "#DCFCE7", "#15803D", "#0F172A"),
            ("Dense(20) +\n4× PQC (5q)", "#EDE9FE", "#6D28D9", "#4C1D95"),
            ("Dense(K)", "#0369A1", "#0C4A6E", "#FFFFFF"),
        ]),
    ]

    row_ys = [0.680, 0.490, 0.300, 0.110]
    row_h = 0.145
    for (rlabel, rfc, rec, cells), ry in zip(rows, row_ys):
        row_bg = FancyBboxPatch((0.010, ry - 0.012), 0.980, row_h + 0.024,
                                boxstyle="round,pad=0.002,rounding_size=0.010",
                                facecolor=rfc, edgecolor=rec, linewidth=1.0, zorder=1)
        ax.add_patch(row_bg)
        draw_box(ax, cols[0][0], ry, cols[0][1], row_h, rlabel, fc=rec, ec=rec,
                 fs=8.8, text_color="#FFFFFF", rsize=0.008)
        for j, (ctxt, cfc, cec, ctc) in enumerate(cells):
            cx, cw, _ = cols[j + 1]
            draw_box(ax, cx, ry, cw, row_h, ctxt, fc=cfc, ec=cec,
                     fs=8.2, text_color=ctc, rsize=0.008)
            if j < len(cells) - 1:
                nx = cols[j + 2][0]
                draw_arrow(ax, cx + cw + 0.001, ry + row_h / 2.0, nx - 0.001, ry + row_h / 2.0,
                           color="#475569", lw=1.2)

    # Destaque da diferenca exata entre Etapa 2B e Etapa 3 (apenas tanh -> 4x PQC)
    diff_box = FancyBboxPatch((0.737, 0.090), 0.161, 0.375,
                              boxstyle="round,pad=0.002,rounding_size=0.012",
                              facecolor="none", edgecolor="#DC2626", linewidth=2.0, linestyle="--", zorder=5)
    ax.add_patch(diff_box)
    ax.text(0.817, 0.045, "Única alteração 2B → 3: tanh ↔ 4× PQC (5 qubits)",
            ha="center", va="center", fontsize=8.8, fontweight="bold", color="#991B1B",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#FEF2F2", edgecolor="#DC2626", lw=1.1))

    ax.text(0.375, 0.045, "Pesos do extrator congelados e compartilhados nas Etapas 2A, 2B e 3",
            ha="center", va="center", fontsize=8.6, fontweight="bold", color="#92400E",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="#FEF3C7", edgecolor="#D97706", lw=1.0))

    out_path = OUT_DIR / "fig_arq_comparativo_mudancas.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print("Gerado:", out_path)


def _draw_cnot(ax, x, y_ctrl, y_targ, color="#1D4ED8", r_targ=0.19):
    ax.plot([x, x], [y_ctrl, y_targ], color=color, linewidth=1.5, zorder=3)
    ax.scatter([x], [y_ctrl], s=42, color=color, zorder=4)
    circ = Circle((x, y_targ), radius=r_targ, facecolor="#FFFFFF", edgecolor=color, linewidth=1.6, zorder=4)
    ax.add_patch(circ)
    ax.plot([x - r_targ * 0.72, x + r_targ * 0.72], [y_targ, y_targ], color=color, linewidth=1.4, zorder=5)
    ax.plot([x, x], [y_targ - r_targ * 0.72, y_targ + r_targ * 0.72], color=color, linewidth=1.4, zorder=5)


def _draw_gate(ax, x, y, w, h, label, fc, ec, text_color="#0F172A", fs=8.5):
    box = FancyBboxPatch(
        (x - w / 2.0, y - h / 2.0), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        facecolor=fc, edgecolor=ec, linewidth=1.3, zorder=4
    )
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=fs, fontweight="bold",
            color=text_color, zorder=5)


def _draw_meter(ax, x, y, w=0.66, h=0.58):
    box = FancyBboxPatch(
        (x - w / 2.0, y - h / 2.0), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        facecolor="#FCE7F3", edgecolor="#BE185D", linewidth=1.4, zorder=4
    )
    ax.add_patch(box)
    arc = Arc((x, y - 0.11), width=0.42, height=0.34, theta1=15, theta2=165,
              color="#9D174D", linewidth=1.4, zorder=5)
    ax.add_patch(arc)
    ax.plot([x, x + 0.17], [y - 0.11, y + 0.15], color="#9D174D", linewidth=1.5, zorder=5)


def gerar_diagrama_circuito_quantico_5qubits():
    fig, ax = plt.subplots(figsize=(16.6, 5.2), dpi=300)
    ax.set_xlim(-0.5, 24.8)
    ax.set_ylim(-0.75, 5.25)
    ax.axis("off")

    wires_y = [4.0, 3.0, 2.0, 1.0, 0.0]

    # Fios quanticos e kets iniciais
    for w_idx, y in enumerate(wires_y):
        ax.plot([0.85, 22.8], [y, y], color="#334155", linewidth=1.35, zorder=1)
        ax.text(0.70, y, f"$q_{w_idx}:\\ |0\\rangle$", ha="right", va="center",
                fontsize=10.2, fontweight="bold", color="#0F172A")

    # 1) Bloco de codificacao RX(u_w)
    enc_rect = FancyBboxPatch((1.10, -0.42), 1.30, 4.86,
                              boxstyle="round,pad=0.04,rounding_size=0.14",
                              facecolor="#EFF6FF", edgecolor="#3B82F6", linewidth=1.1, linestyle="--", zorder=0)
    ax.add_patch(enc_rect)
    ax.text(1.75, 4.72, "Codificação\n$R_X(u_w)$", ha="center", va="bottom",
            fontsize=9.0, fontweight="bold", color="#1D4ED8")
    for w_idx, y in enumerate(wires_y):
        _draw_gate(ax, 1.75, y, 0.88, 0.56, f"$R_X(u_{w_idx})$", fc="#DBEAFE", ec="#2563EB", fs=8.3)

    # 2) Tres camadas variacionais StronglyEntanglingLayers (r = 1, 2, 3)
    layer_starts = [2.85, 9.20, 15.55]
    ranges = [1, 2, 3]
    for layer_idx, (x0, dist) in enumerate(zip(layer_starts, ranges), start=1):
        lw_box = FancyBboxPatch((x0, -0.42), 5.95, 4.86,
                                boxstyle="round,pad=0.04,rounding_size=0.14",
                                facecolor="#FAF5FF", edgecolor="#7C3AED", linewidth=1.1, linestyle="--", zorder=0)
        ax.add_patch(lw_box)
        ax.text(x0 + 2.975, 4.72, f"Camada {layer_idx} · CNOT circular (alcance r = {dist})",
                ha="center", va="bottom", fontsize=9.2, fontweight="bold", color="#5B21B6")

        # Sub-rotacoes R_Z -> R_Y -> R_Z em cada qubit
        rx_xs = [x0 + 0.58, x0 + 1.38, x0 + 2.18]
        rot_names = [("$R_Z$", "#EDE9FE", "#6D28D9"), ("$R_Y$", "#E0E7FF", "#4338CA"), ("$R_Z$", "#EDE9FE", "#6D28D9")]
        for w_idx, y in enumerate(wires_y):
            for gx, (gname, gfc, gec) in zip(rx_xs, rot_names):
                _draw_gate(ax, gx, y, 0.62, 0.54, gname, fc=gfc, ec=gec, fs=8.5)

        ax.text(x0 + 1.38, -0.60, "$R_Z(\\theta_0) \\cdot R_Y(\\theta_1) \\cdot R_Z(\\theta_2)$",
                ha="center", va="top", fontsize=8.0, color="#4C1D95")

        # 5 CNOTs circulares: controle w, alvo (w + r) mod 5
        cx_xs = [x0 + 3.05, x0 + 3.68, x0 + 4.31, x0 + 4.94, x0 + 5.57]
        for w_idx, cx in enumerate(cx_xs):
            target = (w_idx + dist) % 5
            _draw_cnot(ax, cx, wires_y[w_idx], wires_y[target], color="#1D4ED8")

        ax.text(x0 + 4.31, -0.60, "5 CNOTs: $w \\rightarrow (w+" + str(dist) + ")\\ \\mathrm{mod}\\ 5$",
                ha="center", va="top", fontsize=8.0, color="#1E40AF")

    # 3) Medicao Pauli-Y nos 5 fios
    meas_rect = FancyBboxPatch((21.95, -0.42), 2.55, 4.86,
                               boxstyle="round,pad=0.04,rounding_size=0.14",
                               facecolor="#FFF1F2", edgecolor="#BE185D", linewidth=1.1, linestyle="--", zorder=0)
    ax.add_patch(meas_rect)
    ax.text(23.22, 4.72, "Medição\nPauli-$Y$", ha="center", va="bottom",
            fontsize=9.0, fontweight="bold", color="#9D174D")
    for w_idx, y in enumerate(wires_y):
        _draw_meter(ax, 22.55, y)
        ax.text(23.22, y, f"$\\langle Y_{w_idx}\\rangle$", ha="left", va="center",
                fontsize=9.6, fontweight="bold", color="#831843")

    out_path = OUT_DIR / "fig_circuito_quantico_5qubits.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print("Gerado:", out_path)


# ==============================================================================
# FIGURAS TEORICAS DA REVISAO QUANTICA E MODELOS HIBRIDOS (SECOES 2.6 e 2.7)
# ==============================================================================

def _draw_wire_gate(ax, x, y, w, h, label, fc="#EFF6FF", ec="#1D4ED8", tc="#0F172A", fs=8.5, zorder=4):
    rect = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.03,rounding_size=0.08",
        facecolor=fc, edgecolor=ec, linewidth=1.35, zorder=zorder
    )
    ax.add_patch(rect)
    ax.text(x, y, label, ha="center", va="center", fontsize=fs, fontweight="bold", color=tc, zorder=zorder + 1)


def _draw_wire_cnot(ax, x, y_ctrl, y_targ, color="#1D4ED8", r=0.16, zorder=4):
    ax.plot([x, x], [y_ctrl, y_targ], color=color, lw=1.6, zorder=zorder - 1)
    ax.add_patch(Circle((x, y_ctrl), 0.065, facecolor=color, edgecolor=color, zorder=zorder))
    ax.add_patch(Circle((x, y_targ), r, facecolor="#FFFFFF", edgecolor=color, lw=1.5, zorder=zorder))
    ax.plot([x - r * 0.72, x + r * 0.72], [y_targ, y_targ], color=color, lw=1.4, zorder=zorder + 1)
    ax.plot([x, x], [y_targ - r * 0.72, y_targ + r * 0.72], color=color, lw=1.4, zorder=zorder + 1)


def _draw_wire_meter(ax, x, y, w=0.58, h=0.46, fc="#F8FAFC", ec="#334155", zorder=4):
    rect = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.07",
        facecolor=fc, edgecolor=ec, linewidth=1.3, zorder=zorder
    )
    ax.add_patch(rect)
    arc = Arc((x, y - 0.08), w * 0.65, h * 0.68, angle=0, theta1=15, theta2=165, color=ec, lw=1.25, zorder=zorder + 1)
    ax.add_patch(arc)
    ax.plot([x, x + w * 0.22], [y - 0.09, y + h * 0.24], color="#B91C1C", lw=1.35, zorder=zorder + 2)


def _panel_card(ax, title, subtitle=None, accent="#1D4ED8"):
    ax.set_axis_off()
    bg = FancyBboxPatch(
        (0.01, 0.01), 0.98, 0.98,
        boxstyle="round,pad=0.01,rounding_size=0.025",
        facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.15,
        transform=ax.transAxes, zorder=0
    )
    ax.add_patch(bg)
    header = FancyBboxPatch(
        (0.03, 0.875), 0.94, 0.095,
        boxstyle="round,pad=0.005,rounding_size=0.015",
        facecolor="#FFFFFF", edgecolor=accent, linewidth=1.1,
        transform=ax.transAxes, zorder=1
    )
    ax.add_patch(header)
    if subtitle:
        ax.text(0.50, 0.935, title, ha="center", va="center", fontsize=9.8, fontweight="bold", color="#0F172A", transform=ax.transAxes, zorder=2)
        ax.text(0.50, 0.895, subtitle, ha="center", va="center", fontsize=8.0, color="#475569", transform=ax.transAxes, zorder=2)
    else:
        ax.text(0.50, 0.922, title, ha="center", va="center", fontsize=9.8, fontweight="bold", color="#0F172A", transform=ax.transAxes, zorder=2)


def _single_card(ax, title, subtitle=None, accent="#1D4ED8", title_fs=14.5, sub_fs=12.0):
    ax.set_axis_off()
    bg = FancyBboxPatch(
        (0.01, 0.01), 0.98, 0.98,
        boxstyle="round,pad=0.008,rounding_size=0.022",
        facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.2,
        transform=ax.transAxes, zorder=0
    )
    ax.add_patch(bg)
    header = FancyBboxPatch(
        (0.03, 0.875), 0.94, 0.095,
        boxstyle="round,pad=0.005,rounding_size=0.015",
        facecolor="#FFFFFF", edgecolor=accent, linewidth=1.2,
        transform=ax.transAxes, zorder=1
    )
    ax.add_patch(header)
    if subtitle:
        ax.text(0.50, 0.938, title, ha="center", va="center", fontsize=title_fs, fontweight="bold", color="#0F172A", transform=ax.transAxes, zorder=2)
        ax.text(0.50, 0.896, subtitle, ha="center", va="center", fontsize=sub_fs, color="#475569", transform=ax.transAxes, zorder=2)
    else:
        ax.text(0.50, 0.922, title, ha="center", va="center", fontsize=title_fs, fontweight="bold", color="#0F172A", transform=ax.transAxes, zorder=2)


def _save_fig_and_aliases(fig, filenames, pad_inches=0.08):
    for name in filenames:
        out_path = OUT_DIR / name
        fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=pad_inches, facecolor="#FFFFFF")
        print(f"Salvo: {out_path}")
    plt.close(fig)


def gerar_fig_funcoes_ativacao_praticas():
    """Secao 2.5.1: Funcoes de ativacao usadas na pratica (ReLU, Tanh, Swish/SiLU e Softmax)."""
    fig = plt.figure(figsize=(13.6, 5.4), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 0.95], wspace=0.24)

    # --- Painel A: Ativacoes escalares (ReLU, Tanh, Swish/SiLU) ---
    ax_a = fig.add_subplot(gs[0, 0])
    z = np.linspace(-4.0, 4.0, 800)
    y_relu = np.maximum(0.0, z)
    y_tanh = np.tanh(z)
    y_swish = z / (1.0 + np.exp(-z))

    ax_a.axhline(0.0, color="#94A3B8", lw=0.9, zorder=1)
    ax_a.axvline(0.0, color="#94A3B8", lw=0.9, zorder=1)
    ax_a.axhline(1.0, color="#0F766E", ls=":", lw=1.1, alpha=0.65, zorder=1)
    ax_a.axhline(-1.0, color="#0F766E", ls=":", lw=1.1, alpha=0.65, zorder=1)

    ax_a.plot(z, y_relu, color="#1D4ED8", lw=2.4, label=r"$\mathrm{ReLU}(z) = \max(0, z)$", zorder=4)
    ax_a.plot(z, y_swish, color="#D97706", lw=2.4, label=r"$\mathrm{Swish\ (SiLU)}(z) = z\,\sigma(z)$", zorder=4)
    ax_a.plot(z, y_tanh, color="#0F766E", lw=2.4, label=r"$\tanh(z) = (e^z - e^{-z})/(e^z + e^{-z})$", zorder=4)

    ax_a.text(3.92, 1.12, "Saturação tanh (+1)", ha="right", va="bottom", fontsize=8.4, fontweight="bold", color="#0F766E")
    ax_a.text(3.92, -1.14, "Saturação tanh (−1)", ha="right", va="top", fontsize=8.4, fontweight="bold", color="#0F766E")

    z_min = -1.27846454
    y_min = z_min / (1.0 + np.exp(-z_min))
    ax_a.scatter([z_min], [y_min], color="#B45309", s=46, zorder=6)
    ax_a.annotate(
        "Mínimo SiLU:\n(−1,28; −0,28)",
        xy=(z_min, y_min), xytext=(-2.75, -0.78),
        ha="center", va="center", fontsize=8.6, fontweight="bold", color="#92400E",
        arrowprops=dict(arrowstyle="-|>", color="#B45309", lw=1.2),
        bbox=dict(boxstyle="round,pad=0.22", facecolor="#FFFBEB", edgecolor="#F59E0B", lw=0.9),
        zorder=6
    )

    ax_a.annotate(
        "ReLU = 0 para z ≤ 0\n(gradiente nulo)",
        xy=(-2.35, 0.03), xytext=(-2.45, 0.56),
        ha="center", va="center", fontsize=8.5, fontweight="bold", color="#1E40AF",
        arrowprops=dict(arrowstyle="-|>", color="#1D4ED8", lw=1.2),
        bbox=dict(boxstyle="round,pad=0.22", facecolor="#EFF6FF", edgecolor="#93C5FD", lw=0.9),
        zorder=6
    )

    ax_a.set_xlim(-4.05, 4.05)
    ax_a.set_ylim(-1.42, 4.25)
    ax_a.set_xlabel("Pré-ativação z", fontsize=10.2, fontweight="bold")
    ax_a.set_ylabel("Saída φ(z)", fontsize=10.2, fontweight="bold")
    ax_a.set_title("A. Ativações escalares usadas no projeto: ReLU, Tanh e Swish (SiLU)", fontsize=11.0, fontweight="bold", pad=10)
    ax_a.xaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 0)))
    ax_a.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 1) if abs(v - round(v)) > 1e-6 else fmt_pt(v, 0)))
    ax_a.tick_params(labelsize=9.4)
    ax_a.grid(True, alpha=0.7)
    ax_a.spines["top"].set_visible(False)
    ax_a.spines["right"].set_visible(False)
    ax_a.legend(loc="upper left", fontsize=8.9, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1")

    # --- Painel B: Normalizacao vetorial por Softmax (logits s_k -> p_k) ---
    gs_b = gs[0, 1].subgridspec(2, 1, hspace=0.52)
    ax_log = fig.add_subplot(gs_b[0, 0])
    ax_prob = fig.add_subplot(gs_b[1, 0])

    classes = ["Classe 0", "Classe 1", "Classe 2", "Classe 3"]
    s = np.array([-1.20, 0.30, 2.10, -0.10])
    p = np.exp(s) / np.sum(np.exp(s))
    x_cls = np.arange(len(classes))

    cols_log = ["#64748B", "#64748B", "#1D4ED8", "#64748B"]
    bars_l = ax_log.bar(x_cls, s, width=0.52, color=cols_log, edgecolor="#1E293B", lw=0.8, zorder=3)
    ax_log.axhline(0.0, color="#334155", lw=0.95, zorder=2)
    for bar, val in zip(bars_l, s):
        txt = f"+{fmt_pt(val, 2)}" if val > 0 else fmt_pt(val, 2).replace("-", "−")
        va = "bottom" if val >= 0 else "top"
        dy = 0.12 if val >= 0 else -0.14
        ax_log.text(bar.get_x() + bar.get_width() / 2.0, val + dy, txt,
                    ha="center", va=va, fontsize=9.0, fontweight="bold",
                    color="#1E40AF" if val > 2.0 else "#334155")
    ax_log.set_xticks(x_cls)
    ax_log.set_xticklabels(classes, fontsize=9.2, fontweight="bold")
    ax_log.set_ylim(-1.95, 2.95)
    ax_log.set_ylabel("Logit bruto s_k", fontsize=9.6, fontweight="bold")
    ax_log.set_title("B. Normalização vetorial por Softmax (logits s_k → p_k)\n1. Escores lineares não normalizados (logits)", fontsize=10.2, fontweight="bold", pad=8)
    ax_log.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 0)))
    ax_log.tick_params(axis="y", labelsize=8.8)
    ax_log.grid(True, axis="y", alpha=0.7)
    ax_log.spines["top"].set_visible(False)
    ax_log.spines["right"].set_visible(False)

    cols_prob = ["#94A3B8", "#94A3B8", "#0F766E", "#94A3B8"]
    bars_p = ax_prob.bar(x_cls, p, width=0.52, color=cols_prob, edgecolor="#0F172A", lw=0.8, zorder=3)
    for bar, pv in zip(bars_p, p):
        lbl = f"{fmt_pt(pv, 2)} ({fmt_pt(pv * 100.0, 1)}%)"
        ax_prob.text(bar.get_x() + bar.get_width() / 2.0, pv + 0.03, lbl,
                     ha="center", va="bottom", fontsize=8.6, fontweight="bold",
                     color="#0F766E" if pv > 0.5 else "#334155")
    ax_prob.text(
        0.02, 0.94,
        "Classe prevista:\nŷ = arg max p_k = Classe 2",
        transform=ax_prob.transAxes, ha="left", va="top",
        fontsize=8.6, fontweight="bold", color="#0F766E",
        bbox=dict(boxstyle="round,pad=0.26", facecolor="#ECFDF5", edgecolor="#0F766E", lw=1.0),
        zorder=5
    )
    ax_prob.set_xticks(x_cls)
    ax_prob.set_xticklabels(classes, fontsize=9.2, fontweight="bold")
    ax_prob.set_ylim(0.0, 1.10)
    ax_prob.set_ylabel("Probabilidade p_k", fontsize=9.6, fontweight="bold")
    ax_prob.set_title("2. Distribuição Softmax: p_k = exp(s_k) / Σ_j exp(s_j)  (Σ p_k = 1,00)", fontsize=9.8, fontweight="bold", pad=8)
    ax_prob.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 1)))
    ax_prob.tick_params(axis="y", labelsize=8.8)
    ax_prob.grid(True, axis="y", alpha=0.7)
    ax_prob.spines["top"].set_visible(False)
    ax_prob.spines["right"].set_visible(False)

    _save_fig_and_aliases(fig, ["fig_funcoes_ativacao_praticas.png"], pad_inches=0.10)


def gerar_fig_261_esfera_bloch():
    """Secao 2.6.1 (a): Estado de 1 Qubit na Esfera de Bloch."""
    fig = plt.figure(figsize=(7.2, 6.2), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    _single_card(ax, "Estado de 1 Qubit na Esfera de Bloch", "Superposição e fase relativa em S²", accent="#1D4ED8")

    ax_in = fig.add_axes([0.10, 0.20, 0.80, 0.64])
    ax_in.set_xlim(-1.72, 1.72)
    ax_in.set_ylim(-1.48, 1.48)
    ax_in.set_aspect("equal")
    ax_in.axis("off")

    az = np.deg2rad(32)
    el = np.deg2rad(20)
    def proj(x, y, z):
        u = -x * np.sin(az) + y * np.cos(az)
        v = (-x * np.cos(az) - y * np.sin(az)) * np.sin(el) + z * np.cos(el)
        depth = (x * np.cos(az) + y * np.sin(az)) * np.cos(el) + z * np.sin(el)
        return u, v, depth

    t_ext = np.linspace(0, 2 * np.pi, 240)
    ax_in.plot(np.cos(t_ext), np.sin(t_ext), color="#94A3B8", lw=1.5, zorder=1)
    ax_in.fill(np.cos(t_ext), np.sin(t_ext), color="#EFF6FF", alpha=0.38, zorder=0)

    ts = np.linspace(0, 2 * np.pi, 300)
    eu, ev, ed = proj(np.cos(ts), np.sin(ts), np.zeros_like(ts))
    front = ed >= 0
    ax_in.plot(eu[~front], ev[~front], color="#CBD5E1", lw=1.2, ls="--", zorder=1)
    ax_in.plot(np.where(front, eu, np.nan), np.where(front, ev, np.nan), color="#64748B", lw=1.5, zorder=2)

    axes_spec = [
        ((-1.15, 0, 0), (1.18, 0, 0), r"$+X\;(|+\rangle)$", "#475569"),
        ((0, -1.15, 0), (0, 1.20, 0), r"$+Y\;(|+i\rangle)$", "#475569"),
        ((0, 0, -1.15), (0, 0, 1.20), "", "#334155"),
    ]
    for p0, p1, lbl, col in axes_spec:
        u0, v0, _ = proj(*p0)
        u1, v1, _ = proj(*p1)
        ax_in.annotate("", xy=(u1, v1), xytext=(u0, v0),
                       arrowprops=dict(arrowstyle="-|>", color=col, lw=1.3, mutation_scale=12), zorder=2)
        if lbl:
            if "+X" in lbl:
                ax_in.text(u1 * 1.45, v1 * 1.45 - 0.04, lbl, fontsize=12.2, color="#334155", ha="center", va="center", fontweight="bold")
            else:
                ax_in.text(u1 * 1.38, v1 * 1.38 - 0.03, lbl, fontsize=12.2, color="#334155", ha="center", va="center", fontweight="bold")

    u_n, v_n, _ = proj(0, 0, 1.0)
    u_s, v_s, _ = proj(0, 0, -1.0)
    ax_in.scatter([u_n, u_s], [v_n, v_s], s=40, color="#0F172A", zorder=5)
    ax_in.text(u_n + 0.07, v_n + 0.19, r"$|0\rangle$ (+Z)", fontsize=12.6, fontweight="bold", color="#0F172A", ha="left")
    ax_in.text(u_s + 0.07, v_s - 0.22, r"$|1\rangle$ (-Z)", fontsize=12.6, fontweight="bold", color="#0F172A", ha="left")

    th = np.deg2rad(52)
    ph = np.deg2rad(42)
    px, py, pz = np.sin(th) * np.cos(ph), np.sin(th) * np.sin(ph), np.cos(th)
    pu, pv, _ = proj(px, py, pz)
    p0u, p0v, _ = proj(px, py, 0)
    ax_in.plot([0, p0u], [0, p0v], color="#64748B", lw=1.3, ls=":", zorder=3)
    ax_in.plot([p0u, pu], [p0v, pv], color="#64748B", lw=1.3, ls=":", zorder=3)
    ax_in.annotate("", xy=(pu, pv), xytext=(0, 0),
                   arrowprops=dict(arrowstyle="-|>", color="#1D4ED8", lw=2.6, mutation_scale=16), zorder=6)
    ax_in.text(pu + 0.11, pv + 0.10, r"$|\psi\rangle$", fontsize=15.5, fontweight="bold", color="#1D4ED8", zorder=7)

    th_arc = np.linspace(0, th, 40)
    au, av, _ = proj(0.45 * np.sin(th_arc) * np.cos(ph), 0.45 * np.sin(th_arc) * np.sin(ph), 0.45 * np.cos(th_arc))
    ax_in.plot(au, av, color="#B45309", lw=1.8, zorder=5)
    ax_in.text(au[20] + 0.11, av[20] + 0.03, r"$\theta$", fontsize=13.5, fontweight="bold", color="#B45309")

    ph_arc = np.linspace(0, ph, 40)
    fu, fv, _ = proj(0.45 * np.cos(ph_arc), 0.45 * np.sin(ph_arc), np.zeros_like(ph_arc))
    ax_in.plot(fu, fv, color="#047857", lw=1.8, zorder=5)
    ax_in.text(fu[15] - 0.12, fv[15] - 0.14, r"$\phi$", fontsize=13.5, fontweight="bold", color="#047857")

    eq_box = FancyBboxPatch(
        (0.05, 0.035), 0.90, 0.145,
        boxstyle="round,pad=0.008,rounding_size=0.015",
        facecolor="#FFFFFF", edgecolor="#BFDBFE", linewidth=1.2,
        transform=ax.transAxes, zorder=2
    )
    ax.add_patch(eq_box)
    ax.text(
        0.50, 0.132,
        r"$|\psi\rangle = \cos(\theta/2)|0\rangle + e^{i\phi}\sin(\theta/2)|1\rangle$",
        ha="center", va="center", fontsize=12.6, fontweight="bold", color="#0F172A", transform=ax.transAxes, zorder=3
    )
    ax.text(
        0.50, 0.070,
        r"Normalização: $|\alpha|^2 + |\beta|^2 = 1$   (probabilidades na base $Z$)",
        ha="center", va="center", fontsize=11.6, color="#475569", transform=ax.transAxes, zorder=3
    )

    _save_fig_and_aliases(fig, ["fig_261_esfera_bloch.png"])


def gerar_fig_261_circuito_bell():
    """Secao 2.6.1 (b): Circuito de Bell e Leitura por Base."""
    fig = plt.figure(figsize=(7.6, 5.4), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    _single_card(ax, "Circuito de Bell e Leitura por Base", "Portas unitárias, emaranhamento e medição", accent="#047857")

    ax_in = fig.add_axes([0.05, 0.22, 0.90, 0.59])
    ax_in.set_xlim(-0.95, 6.45)
    ax_in.set_ylim(-0.35, 3.28)
    ax_in.axis("off")

    yq0, yq1, yc = 2.22, 1.22, 0.22
    ax_in.text(-0.90, yq0, r"$q_0:|0\rangle$", fontsize=13.5, fontweight="bold", va="center", color="#0F172A")
    ax_in.text(-0.90, yq1, r"$q_1:|0\rangle$", fontsize=13.5, fontweight="bold", va="center", color="#0F172A")
    ax_in.text(-0.90, yc, r"$c_{0,1}:00$", fontsize=12.8, fontweight="bold", va="center", color="#475569")

    ax_in.plot([0.10, 5.75], [yq0, yq0], color="#334155", lw=1.6, zorder=1)
    ax_in.plot([0.10, 5.75], [yq1, yq1], color="#334155", lw=1.6, zorder=1)
    ax_in.plot([0.10, 6.05], [yc + 0.03, yc + 0.03], color="#64748B", lw=1.1, zorder=1)
    ax_in.plot([0.10, 6.05], [yc - 0.03, yc - 0.03], color="#64748B", lw=1.1, zorder=1)

    ax_in.plot([3.22, 3.22], [0.70, 2.66], color="#94A3B8", lw=1.3, ls="--", zorder=2)

    _draw_wire_gate(ax_in, 0.65, yq0, 0.72, 0.56, r"$H$", fc="#ECFDF5", ec="#047857", fs=15.0)
    _draw_wire_cnot(ax_in, 2.42, yq0, yq1, color="#1D4ED8", r=0.20)

    _draw_wire_gate(ax_in, 4.05, yq0, 0.90, 0.54, r"$R_{\text{base}}$", fc="#F5F3FF", ec="#7C3AED", fs=12.5)
    _draw_wire_gate(ax_in, 4.05, yq1, 0.90, 0.54, r"$R_{\text{base}}$", fc="#F5F3FF", ec="#7C3AED", fs=12.5)
    _draw_wire_meter(ax_in, 5.45, yq0, w=0.62, h=0.50)
    _draw_wire_meter(ax_in, 5.45, yq1, w=0.62, h=0.50)

    ax_in.annotate("", xy=(5.28, yc + 0.06), xytext=(5.28, yq0 - 0.25),
                   arrowprops=dict(arrowstyle="-|>", color="#64748B", lw=1.2, mutation_scale=11), zorder=3)
    ax_in.annotate("", xy=(5.62, yc + 0.06), xytext=(5.62, yq1 - 0.25),
                   arrowprops=dict(arrowstyle="-|>", color="#64748B", lw=1.2, mutation_scale=11), zorder=3)

    ax_in.text(0.65, 2.95, "1. Superposição", ha="center", va="center", fontsize=11.6, fontweight="bold", color="#047857")
    ax_in.text(2.42, 2.95, "2. Emaranhamento", ha="center", va="center", fontsize=11.6, fontweight="bold", color="#1D4ED8")
    ax_in.text(4.75, 2.95, "3. Base (X/Y/Z)\n+ Medição", ha="center", va="center", fontsize=11.6, fontweight="bold", color="#7C3AED")

    eq_box1 = FancyBboxPatch(
        (0.05, 0.035), 0.90, 0.145,
        boxstyle="round,pad=0.008,rounding_size=0.015",
        facecolor="#FFFFFF", edgecolor="#A7F3D0", linewidth=1.2,
        transform=ax.transAxes, zorder=2
    )
    ax.add_patch(eq_box1)
    ax.text(
        0.50, 0.132,
        r"Estado de Bell: $|\Phi^+\rangle = \frac{1}{\sqrt{2}}(|00\rangle + |11\rangle)$",
        ha="center", va="center", fontsize=13.0, fontweight="bold", color="#0F172A", transform=ax.transAxes, zorder=3
    )
    ax.text(
        0.50, 0.070,
        r"Correlação máxima: $\langle Z_0 Z_1 \rangle = +1$; sem estado separável",
        ha="center", va="center", fontsize=12.0, color="#475569", transform=ax.transAxes, zorder=3
    )

    _save_fig_and_aliases(fig, ["fig_261_circuito_bell.png"])


def gerar_fig_261_shots_bell():
    """Secao 2.6.1 (c): Valor Exato vs. Amostragem por Shots."""
    fig = plt.figure(figsize=(7.4, 5.8), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    _single_card(ax, "Valor Exato vs. Amostragem por Shots", "Estimativa binomial em hardware NISQ / QASM", accent="#7C3AED")

    ax_in = fig.add_axes([0.13, 0.28, 0.81, 0.54])
    estados = [r"$|00\rangle$", r"$|01\rangle$", r"$|10\rangle$", r"$|11\rangle$"]
    p_exato = np.array([0.50, 0.00, 0.00, 0.50])
    rng = np.random.default_rng(7)
    s64 = rng.multinomial(64, p_exato) / 64.0
    s1024 = rng.multinomial(1024, p_exato) / 1024.0

    x_idx = np.arange(len(estados)) * 1.15
    bw = 0.31
    b1 = ax_in.bar(x_idx - bw, p_exato, width=bw * 0.80, color="#1D4ED8", edgecolor="#1E3A8A", lw=0.9, label="Exato (Statevector)")
    b2 = ax_in.bar(x_idx, s1024, width=bw * 0.80, color="#7C3AED", edgecolor="#5B21B6", lw=0.9, label="S = 1.024 shots")
    b3 = ax_in.bar(x_idx + bw, s64, width=bw * 0.80, color="#F59E0B", edgecolor="#B45309", lw=0.9, label="S = 64 shots")

    for bars in (b1, b2, b3):
        for bar in bars:
            h = bar.get_height()
            if h > 0.01:
                ax_in.text(
                    bar.get_x() + bar.get_width() / 2, h + 0.015,
                    fmt_pt(h, 2), ha="center", va="bottom", fontsize=11.0, fontweight="bold", color="#0F172A"
                )

    ax_in.axhline(0.50, color="#94A3B8", lw=1.0, ls="--", zorder=0)
    ax_in.set_xticks(x_idx)
    ax_in.set_xticklabels(estados, fontsize=12.6, fontweight="bold")
    ax_in.set_ylim(0.0, 0.72)
    ax_in.set_ylabel("Probabilidade observada", fontsize=12.2, fontweight="bold", color="#334155")
    ax_in.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 1)))
    ax_in.tick_params(axis="y", labelsize=12.0)
    ax_in.grid(axis="y", alpha=0.55)
    ax_in.spines["top"].set_visible(False)
    ax_in.spines["right"].set_visible(False)
    ax_in.legend(loc="upper center", frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1", fontsize=11.8, ncol=1)

    eq_box2 = FancyBboxPatch(
        (0.05, 0.035), 0.90, 0.145,
        boxstyle="round,pad=0.008,rounding_size=0.015",
        facecolor="#FFFFFF", edgecolor="#DDD6FE", linewidth=1.2,
        transform=ax.transAxes, zorder=2
    )
    ax.add_patch(eq_box2)
    ax.text(
        0.50, 0.132,
        r"Incerteza estatística: $\sigma_{\langle O\rangle} \propto \mathcal{O}(1/\sqrt{S})$",
        ha="center", va="center", fontsize=12.5, fontweight="bold", color="#0F172A", transform=ax.transAxes, zorder=3
    )
    ax.text(
        0.50, 0.070,
        "Statevector evita erro amostral; QPUs exigem S elevado",
        ha="center", va="center", fontsize=11.8, color="#475569", transform=ax.transAxes, zorder=3
    )

    _save_fig_and_aliases(fig, ["fig_261_shots_bell.png"])


def gerar_fig_263_codificacoes_vetoriais():
    """Secao 2.6.3 (a): Codificacao de Vetores em Circuitos (Amplitude, Angular e Data Re-uploading)."""
    fig = plt.figure(figsize=(7.6, 6.0), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    _single_card(ax, "Codificação de Vetores em Circuitos", "Amplitude, Angular e Data Re-uploading", accent="#1D4ED8")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    rows = [
        (
            0.62, 0.23, "#EFF6FF", "#1D4ED8",
            "1. Amplitude Embedding  [n = log₂(d) qubits]",
            r"$|x\rangle = \frac{1}{\|x\|_2}\sum_{i=0}^{d-1} x_i |i\rangle$",
            "Compactação exponencial; preparação profunda / QRAM"
        ),
        (
            0.34, 0.24, "#ECFDF5", "#047857",
            "2. Angle Embedding  [n = d qubits — Adotado no TCC]",
            r"$|\psi(x)\rangle = \bigotimes_{j=0}^{n-1} R_X(x_j)|0\rangle$",
            "Profundidade O(1); compatível com NISQ e gradiente direto"
        ),
        (
            0.06, 0.24, "#F5F3FF", "#7C3AED",
            "3. Reenvio de Dados (Data Re-uploading)",
            r"$U(x,\theta) = \prod_{\ell=1}^{L} W_\ell(\theta_\ell)\,S(x)$",
            "Contorna não clonagem; amplia espectro em série de Fourier"
        ),
    ]
    for y0, h, fc, ec, title_r, eq_r, note_r in rows:
        card = FancyBboxPatch(
            (0.045, y0), 0.91, h,
            boxstyle="round,pad=0.006,rounding_size=0.018",
            facecolor="#FFFFFF", edgecolor=ec, linewidth=1.3,
            transform=ax.transAxes, zorder=2
        )
        ax.add_patch(card)
        pill = FancyBboxPatch(
            (0.06, y0 + h - 0.065), 0.88, 0.054,
            boxstyle="round,pad=0.003,rounding_size=0.012",
            facecolor=fc, edgecolor="none",
            transform=ax.transAxes, zorder=3
        )
        ax.add_patch(pill)
        ax.text(0.08, y0 + h - 0.038, title_r, ha="left", va="center", fontsize=12.8, fontweight="bold", color=ec, transform=ax.transAxes, zorder=4)
        ax.text(0.50, y0 + h * 0.44, eq_r, ha="center", va="center", fontsize=14.2, color="#0F172A", transform=ax.transAxes, zorder=4)
        ax.text(0.50, y0 + 0.036, note_r, ha="center", va="center", fontsize=12.0, color="#475569", transform=ax.transAxes, zorder=4)

    _save_fig_and_aliases(fig, ["fig_263_codificacoes_vetoriais.png"])


def gerar_fig_263_qkm_gcq():
    """Secao 2.6.3 (b): Nucleos Quanticos (QKM) e Diferenca Geometrica."""
    fig = plt.figure(figsize=(7.6, 6.0), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    _single_card(ax, "Núcleos Quânticos e Diferença Geométrica", "Mapa de características e critério de Egginger et al. (2024)", accent="#047857")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    draw_box(ax, 0.05, 0.72, 0.35, 0.12, r"Entradas clássicas" + "\n" + r"$x, z \in \mathbb{R}^d$", fc="#F1F5F9", ec="#475569", fs=12.6)
    draw_box(ax, 0.55, 0.72, 0.40, 0.12, r"Espaço de Hilbert $\mathcal{H}$" + "\n" + r"$|\Phi(x)\rangle = U_\Phi(x)|0\rangle^{\otimes n}$", fc="#ECFDF5", ec="#047857", fs=12.4)
    draw_arrow(ax, 0.405, 0.78, 0.545, 0.78, color="#047857", lw=1.8)
    ax.text(0.475, 0.812, r"$U_\Phi(x)$", ha="center", va="bottom", fontsize=13.0, fontweight="bold", color="#047857")

    draw_box(ax, 0.05, 0.52, 0.90, 0.145,
             "Núcleo Quântico (Fidelidade) vs. Núcleo RDM Projetado\n" +
             r"$K_Q(x, z) = |\langle\Phi(x) | \Phi(z)\rangle|^2$   e   $K_{\mathrm{RDM}}$ via $\mathrm{Tr}(\rho_k(x)\rho_k(z))$",
             fc="#EFF6FF", ec="#1D4ED8", fs=12.2)
    draw_arrow(ax, 0.75, 0.715, 0.75, 0.670, color="#1D4ED8", lw=1.7)

    draw_box(ax, 0.05, 0.30, 0.90, 0.165,
             r"Diferença Geométrica (GD): separação $K_Q$ vs. $K_C$" + "\n" +
             r"$g_{CQ} = \sqrt{\|\sqrt{K_Q}\, K_C^{-1}\, \sqrt{K_Q}\|_\infty}$",
             fc="#FFFBEB", ec="#B45309", fs=12.4)
    draw_arrow(ax, 0.50, 0.515, 0.50, 0.470, color="#B45309", lw=1.7)

    note_b = FancyBboxPatch(
        (0.05, 0.04), 0.90, 0.22,
        boxstyle="round,pad=0.006,rounding_size=0.015",
        facecolor="#FFFFFF", edgecolor="#CBD5E1", linewidth=1.1,
        transform=ax.transAxes, zorder=2
    )
    ax.add_patch(note_b)
    ax.text(
        0.50, 0.15,
        "Achado empírico (Egginger et al., 2024):\n"
        "• Tempo evolutivo t, base do núcleo e γ dominam o desempenho.\n"
        "• Regiões que maximizam g_CQ (distância geométrica)\n"
        "  nem sempre coincidem com a maior acurácia em classificação.",
        ha="center", va="center", fontsize=12.0, color="#334155", linespacing=1.34, transform=ax.transAxes, zorder=3
    )

    _save_fig_and_aliases(fig, ["fig_263_qkm_gcq.png"])


def gerar_fig_263_qir_psnr():
    """Secao 2.6.3 (c): Imagens Quanticas (QIR) e Limite de Leitura."""
    fig = plt.figure(figsize=(7.6, 6.6), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    _single_card(ax, "Imagens Quânticas (QIR) e Limite de Leitura", "QL, FRQI e NEQR (Okada et al., 2025)", accent="#7C3AED")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    qir_cards = [
        (0.735, 0.115, "#F1F5F9", "#475569",
         "Qubit Lattice (QL) — 2²ⁿ qubits (N×N)",
         "Sem superposição espacial; leitura isolada por pixel."),
        (0.600, 0.115, "#F5F3FF", "#7C3AED",
         "FRQI — (2n + 1) qubits: intensidade na amplitude",
         r"Leitura probabilística → $\mathrm{PSNR}_m \approx 10\log_{10}(m) + 9{,}94\ \mathrm{dB}$"),
        (0.465, 0.115, "#EFF6FF", "#1D4ED8",
         "NEQR — (2n + d) qubits: intensidade digital d bits",
         r"Determinística/pixel; requer $E_N = N\cdot H_N$ amostras (cupons)"),
    ]
    for y0, h, fc, ec, t1, t2 in qir_cards:
        box = FancyBboxPatch(
            (0.05, y0), 0.90, h,
            boxstyle="round,pad=0.005,rounding_size=0.014",
            facecolor=fc, edgecolor=ec, linewidth=1.2,
            transform=ax.transAxes, zorder=2
        )
        ax.add_patch(box)
        ax.text(0.075, y0 + h * 0.68, t1, ha="left", va="center", fontsize=12.6, fontweight="bold", color=ec, transform=ax.transAxes, zorder=3)
        ax.text(0.075, y0 + h * 0.28, t2, ha="left", va="center", fontsize=12.0, color="#1E293B", transform=ax.transAxes, zorder=3)

    ax_in = fig.add_axes([0.14, 0.095, 0.79, 0.305])
    m_vals = np.logspace(0, 4, 200)
    psnr_bound = 10.0 * np.log10(m_vals * (np.pi ** 2))
    ax_in.semilogx(m_vals, psnr_bound, color="#7C3AED", lw=2.4, label="Limite teórico FRQI")
    pts_m = np.array([10, 100, 1000, 10000])
    pts_p = 10.0 * np.log10(pts_m * (np.pi ** 2))
    ax_in.scatter(pts_m, pts_p, color="#B91C1C", s=42, zorder=5)
    for xm, yp in zip(pts_m, pts_p):
        ax_in.text(xm * 0.78, yp + 4.8, f"{fmt_pt(yp, 1)} dB", fontsize=12.0, ha="center", fontweight="bold", color="#7C3AED")

    ax_in.set_title("FRQI: PSNR teórico vs. shots por pixel (m)", fontsize=12.6, fontweight="bold", color="#334155", pad=6)
    ax_in.set_xlabel("Amostras por pixel (m)", fontsize=12.2, fontweight="bold", color="#475569")
    ax_in.set_ylabel("PSNR (dB)", fontsize=12.2, fontweight="bold", color="#475569")
    ax_in.set_xlim(0.7, 2.5e4)
    ax_in.set_ylim(6, 63)
    ax_in.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 0)))
    ax_in.tick_params(labelsize=11.8)
    ax_in.grid(True, which="major", alpha=0.55)
    ax_in.spines["top"].set_visible(False)
    ax_in.spines["right"].set_visible(False)

    _save_fig_and_aliases(fig, ["fig_263_qir_psnr.png"])


def gerar_fig_264_laco_vqa():
    """Secao 2.6.4 (a): Arquitetura do Laco Hibrido VQA."""
    fig = plt.figure(figsize=(8.2, 5.8), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    _single_card(ax, "Arquitetura do Laço Híbrido VQA",
                 "Ansatz RealAmplitudes / N-Local + Otimizador Clássico", accent="#1D4ED8", title_fs=14.2, sub_fs=12.6)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    z_q = FancyBboxPatch((0.04, 0.455), 0.92, 0.395, boxstyle="round,pad=0.006,rounding_size=0.02",
                         facecolor="#EFF6FF", edgecolor="#3B82F6", ls="--", lw=1.3, transform=ax.transAxes, zorder=1)
    ax.add_patch(z_q)
    ax.text(0.06, 0.822, "DOMÍNIO QUÂNTICO (QPU Real ou Simulador Statevector)", fontsize=12.6, fontweight="bold", color="#1D4ED8", transform=ax.transAxes, zorder=2)

    z_c = FancyBboxPatch((0.04, 0.04), 0.92, 0.35, boxstyle="round,pad=0.006,rounding_size=0.02",
                         facecolor="#ECFDF5", edgecolor="#10B981", ls="--", lw=1.3, transform=ax.transAxes, zorder=1)
    ax.add_patch(z_c)
    ax.text(0.50, 0.068, "DOMÍNIO CLÁSSICO (PyTorch Autograd / CPU ou GPU)", ha="center", va="center", fontsize=12.6, fontweight="bold", color="#047857", transform=ax.transAxes, zorder=2)

    draw_box(ax, 0.055, 0.565, 0.215, 0.17, "Codificação\nS(x)", fc="#DBEAFE", ec="#1D4ED8", fs=13.0, zorder=3)
    ans_bg = FancyBboxPatch((0.295, 0.495), 0.44, 0.29, boxstyle="round,pad=0.005,rounding_size=0.015",
                            facecolor="#FFFFFF", edgecolor="#1D4ED8", lw=1.4, transform=ax.transAxes, zorder=3)
    ax.add_patch(ans_bg)
    ax.text(0.515, 0.760, "Ansatz N-local / RealAmplitudes U(θ)", ha="center", va="center", fontsize=12.2, fontweight="bold", color="#1E3A8A", transform=ax.transAxes, zorder=4)

    ys = [0.695, 0.615, 0.535]
    for yq in ys:
        ax.plot([0.315, 0.715], [yq, yq], color="#334155", lw=1.3, transform=ax.transAxes, zorder=4)
        for xg, lbl in [(0.375, r"$R_Y$"), (0.645, r"$R_Y$")]:
            gb = FancyBboxPatch((xg - 0.032, yq - 0.026), 0.064, 0.052,
                                boxstyle="round,pad=0.002,rounding_size=0.006",
                                facecolor="#EFF6FF", edgecolor="#2563EB", lw=1.1, transform=ax.transAxes, zorder=5)
            ax.add_patch(gb)
            ax.text(xg, yq, lbl, ha="center", va="center", fontsize=12.6, fontweight="bold", color="#0F172A", transform=ax.transAxes, zorder=6)
    for xc, yc_c, yc_t in [(0.47, ys[0], ys[1]), (0.535, ys[1], ys[2])]:
        ax.plot([xc, xc], [yc_c, yc_t], color="#1D4ED8", lw=1.4, transform=ax.transAxes, zorder=5)
        ax.scatter([xc], [yc_c], s=28, color="#1D4ED8", transform=ax.transAxes, zorder=6)
        ax.add_patch(Circle((xc, yc_t), 0.015, facecolor="#FFFFFF", edgecolor="#1D4ED8", lw=1.3, transform=ax.transAxes, zorder=6))
        ax.plot([xc - 0.011, xc + 0.011], [yc_t, yc_t], color="#1D4ED8", lw=1.2, transform=ax.transAxes, zorder=7)

    draw_box(ax, 0.76, 0.565, 0.185, 0.17, "Medição\n⟨Oⱼ⟩(x, θ)", fc="#F5F3FF", ec="#7C3AED", fs=13.0, zorder=3)

    draw_arrow(ax, 0.273, 0.65, 0.295, 0.65, color="#1D4ED8", lw=1.7, zorder=4)
    draw_arrow(ax, 0.738, 0.65, 0.76, 0.65, color="#7C3AED", lw=1.7, zorder=4)

    draw_box(ax, 0.535, 0.115, 0.405, 0.205, "Função de Custo C(θ) + Gradiente\nC = f(⟨O⟩, y)\n∇_θ C via Adjoint / Parameter-Shift",
             fc="#FFFFFF", ec="#047857", fs=11.8, zorder=3)
    draw_box(ax, 0.06, 0.115, 0.405, 0.205, "Otimizador Clássico\nAdam / QNG / COBYLA / L-BFGS-B\nθ ← θ − η ∇_θ C(θ)",
             fc="#FFFFFF", ec="#047857", fs=11.8, zorder=3)

    draw_arrow(ax, 0.85, 0.560, 0.85, 0.325, color="#7C3AED", lw=1.9, zorder=4)
    ax.text(0.832, 0.422, "Vetor ⟨Z⟩/⟨Y⟩", ha="right", va="center", fontsize=12.4, fontweight="bold", color="#7C3AED", transform=ax.transAxes)
    draw_arrow(ax, 0.530, 0.218, 0.470, 0.218, color="#047857", lw=1.9, zorder=4)
    draw_arrow(ax, 0.26, 0.325, 0.44, 0.490, color="#1D4ED8", lw=1.9, zorder=4)
    ax.text(0.295, 0.422, "Atualiza θ", ha="right", va="center", fontsize=12.4, fontweight="bold", color="#1D4ED8", transform=ax.transAxes)

    _save_fig_and_aliases(fig, ["fig_264_laco_vqa.png"])


def gerar_fig_264_parameter_shift():
    """Secao 2.6.4 (b): Regra Parameter-Shift e Diferenciacao."""
    fig = plt.figure(figsize=(7.6, 6.4), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    _single_card(ax, "Regra Parameter-Shift e Diferenciação",
                 "Gradiente analítico exato vs. métodos em simulador", accent="#7C3AED")

    ax_in = fig.add_axes([0.13, 0.41, 0.81, 0.40])
    th_grid = np.linspace(0.0, 2 * np.pi, 300)
    f_val = 0.85 * np.sin(th_grid + 0.25)
    ax_in.plot(th_grid, f_val, color="#1D4ED8", lw=2.4, label=r"$\langle O \rangle(\theta_p)$")

    th0 = 1.55
    shift = np.pi / 2.0
    ym = 0.85 * np.sin(th0 - shift + 0.25)
    yp = 0.85 * np.sin(th0 + shift + 0.25)
    y0 = 0.85 * np.sin(th0 + 0.25)
    slope = 0.5 * (yp - ym)

    ax_in.plot([th0 - shift, th0 + shift], [ym, yp], color="#B91C1C", lw=1.9, ls="--", label=r"Pontos deslocados ($\pm\pi/2$)")
    t_tan = np.linspace(th0 - 0.85, th0 + 0.85, 50)
    ax_in.plot(t_tan, y0 + slope * (t_tan - th0), color="#047857", lw=2.2, label="Inclinação exata = Δ⟨O⟩/2")
    ax_in.scatter([th0 - shift, th0, th0 + shift], [ym, y0, yp], color=["#B91C1C", "#047857", "#B91C1C"], s=48, zorder=6)

    ax_in.annotate(r"$\theta_p - \frac{\pi}{2}$", xy=(th0 - shift, ym), xytext=(0.12, ym - 0.38),
                   fontsize=12.4, fontweight="bold", color="#B91C1C")
    ax_in.annotate(r"$\theta_p$", xy=(th0, y0), xytext=(th0 - 0.08, y0 + 0.22),
                   fontsize=13.0, fontweight="bold", color="#047857")
    ax_in.annotate(r"$\theta_p + \frac{\pi}{2}$", xy=(th0 + shift, yp), xytext=(th0 + shift + 0.14, yp + 0.12),
                   fontsize=12.4, fontweight="bold", color="#B91C1C")

    ax_in.set_xlim(-0.15, 2 * np.pi + 0.15)
    ax_in.set_ylim(-1.18, 1.28)
    ax_in.set_xticks([0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi])
    ax_in.set_xticklabels(["0", "π/2", "π", "3π/2", "2π"], fontsize=12.0, fontweight="bold")
    ax_in.set_ylabel("⟨O⟩(θ)", fontsize=12.4, fontweight="bold", color="#334155")
    ax_in.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 1)))
    ax_in.tick_params(axis="y", labelsize=12.0)
    ax_in.grid(True, alpha=0.45)
    ax_in.spines["top"].set_visible(False)
    ax_in.spines["right"].set_visible(False)
    ax_in.legend(loc="lower left", fontsize=11.6, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1")

    box_ps = FancyBboxPatch((0.04, 0.035), 0.92, 0.315, boxstyle="round,pad=0.006,rounding_size=0.015",
                            facecolor="#FFFFFF", edgecolor="#DDD6FE", lw=1.2, transform=ax.transAxes, zorder=2)
    ax.add_patch(box_ps)
    ax.text(
        0.50, 0.295,
        r"$\frac{\partial \langle O \rangle}{\partial \theta_p} = \frac{1}{2}\left[\langle O \rangle(\theta_p + \frac{\pi}{2}) - \langle O \rangle(\theta_p - \frac{\pi}{2})\right]$",
        ha="center", va="center", fontsize=14.2, fontweight="bold", color="#5B21B6", transform=ax.transAxes, zorder=3
    )
    ax.text(
        0.06, 0.135,
        "• Parameter-Shift: gradiente exato em QPU real; custo 2P execuções/passo.\n"
        "• Adjunto (Adjoint): O(1) passagens em simulador clássico statevector.\n"
        "• Diferenças finitas: δ pequeno amplifica erro estatístico de shots (1/√S).",
        ha="left", va="center", fontsize=12.0, color="#334155", linespacing=1.38, transform=ax.transAxes, zorder=3
    )

    _save_fig_and_aliases(fig, ["fig_264_parameter_shift.png"])


def gerar_fig_265_paisagem_barren_plateau():
    """Secao 2.6.5 (a): Paisagem de Custo C(theta) — Vale Treinavel vs Plato Esteril."""
    fig = plt.figure(figsize=(7.4, 6.4), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    _single_card(ax, "Paisagem de Custo C(θ)", "Vale treinável vs. concentração em platô estéril", accent="#1D4ED8")

    th = np.linspace(-3.0, 3.0, 300)
    c_train = 0.72 - 0.52 * np.exp(-1.1 * th ** 2) + 0.04 * np.cos(2.5 * th)
    c_bp = 0.50 + 0.012 * np.sin(5.0 * th) - 0.06 * np.exp(-12.0 * (th - 1.9) ** 2)

    ax_t = fig.add_axes([0.12, 0.52, 0.81, 0.27])
    ax_t.plot(th, c_train, color="#047857", lw=2.4)
    ax_t.scatter([0.0], [c_train[150]], color="#047857", s=46, zorder=5)
    ax_t.annotate(r"Vale amplo ($\nabla C \neq 0$)", xy=(0.0, c_train[150]), xytext=(0.72, 0.22),
                  arrowprops=dict(arrowstyle="->", color="#047857", lw=1.4), fontsize=12.5, fontweight="bold", color="#047857")
    ax_t.set_title("Ansatz raso / estruturado", fontsize=13.0, fontweight="bold", color="#047857", pad=5)
    ax_t.set_xticks([])
    ax_t.set_yticks([0.2, 0.5, 0.8])
    ax_t.set_yticklabels(["0,2", "0,5", "0,8"], fontsize=12.0)
    ax_t.set_ylim(0.12, 0.90)
    ax_t.grid(True, alpha=0.45)
    ax_t.spines["top"].set_visible(False)
    ax_t.spines["right"].set_visible(False)

    ax_b = fig.add_axes([0.12, 0.145, 0.81, 0.27])
    ax_b.plot(th, c_bp, color="#B91C1C", lw=2.4)
    ax_b.axhspan(0.46, 0.54, color="#FEE2E2", alpha=0.65)
    ax_b.text(-0.2, 0.63, "Platô estéril: ∂C/∂θ ≈ 0", ha="center", fontsize=12.5, fontweight="bold", color="#B91C1C")
    ax_b.set_title("Circuito profundo / 2-design global", fontsize=13.0, fontweight="bold", color="#B91C1C", pad=5)
    ax_b.set_xlabel("Parâmetro θₖ", fontsize=12.2, fontweight="bold", color="#334155")
    ax_b.set_xticks([])
    ax_b.set_yticks([0.2, 0.5, 0.8])
    ax_b.set_yticklabels(["0,2", "0,5", "0,8"], fontsize=12.0)
    ax_b.set_ylim(0.12, 0.90)
    ax_b.grid(True, alpha=0.45)
    ax_b.spines["top"].set_visible(False)
    ax_b.spines["right"].set_visible(False)

    ax.text(0.50, 0.052, r"Lema de Lévy em $\mathbb{S}^{2^n}$: concentração em torno da média",
            ha="center", va="center", fontsize=12.0, color="#475569", transform=ax.transAxes)

    _save_fig_and_aliases(fig, ["fig_265_paisagem_barren_plateau.png"])


def gerar_fig_265_variancia_gradiente():
    """Secao 2.6.5 (b): Escalonamento da Variancia do Gradiente."""
    fig = plt.figure(figsize=(7.4, 6.0), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    _single_card(ax, "Escalonamento da Variância do Gradiente", "Decaimento com o número de qubits n (curvas teóricas)", accent="#B91C1C")

    ax_in = fig.add_axes([0.15, 0.20, 0.79, 0.61])
    nq = np.arange(2, 21)
    var_2design = 0.35 * (2.0 ** (-nq))
    var_noise = 0.22 * (2.6 ** (-nq))
    var_local = 0.18 / (nq ** 1.4)

    ax_in.semilogy(nq, var_local, color="#047857", lw=2.4, ls="-", label=r"Custo local / raso: $\mathcal{O}(1/\mathrm{poly}(n))$")
    ax_in.semilogy(nq, var_2design, color="#B91C1C", lw=2.4, ls="-", label=r"Global 2-design: $\mathcal{O}(2^{-n})$")
    ax_in.semilogy(nq, var_noise, color="#B45309", lw=2.1, ls="--", label="Ruído profundo (induzido)")

    ax_in.axvline(5, color="#1D4ED8", lw=1.6, ls=":")
    ax_in.text(5.4, 0.14, "Subcircuitos\nn = 5 qubits\n(TCC)", fontsize=12.2, fontweight="bold", color="#1D4ED8", va="bottom")

    ax_in.set_xlabel("Número de qubits (n)", fontsize=12.6, fontweight="bold", color="#334155")
    ax_in.set_ylabel("Var[∂C/∂θₖ] (escala log)", fontsize=12.6, fontweight="bold", color="#334155")
    ax_in.set_xlim(2, 20)
    ax_in.set_ylim(1e-9, 1e0)
    ax_in.set_xticks([2, 5, 10, 15, 20])
    ax_in.tick_params(labelsize=12.2)
    ax_in.grid(True, which="major", alpha=0.5)
    ax_in.spines["top"].set_visible(False)
    ax_in.spines["right"].set_visible(False)
    ax_in.legend(loc="lower left", fontsize=11.8, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1")

    ax.text(0.50, 0.052, "Escalonamento assintótico segundo McClean et al. (2018) e Cerezo et al. (2021)",
            ha="center", va="center", fontsize=11.8, color="#475569", transform=ax.transAxes)

    _save_fig_and_aliases(fig, ["fig_265_variancia_gradiente.png"])


def gerar_fig_265_canais_kraus():
    """Secao 2.6.5 (c): Canais de Ruido NISQ (Operadores de Kraus)."""
    fig = plt.figure(figsize=(7.4, 6.2), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    _single_card(ax, "Canais de Ruído NISQ (Operadores de Kraus)", "Evolução não unitária:  ℰ(ρ) = ∑ₖ Eₖ · ρ · Eₖ†", accent="#B45309")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    noise_cards = [
        (0.605, 0.22, "#FFFBEB", "#B45309",
         "1. Amortecimento de Amplitude (T₁)",
         "Perda energética |1⟩ → |0⟩;\nEsfera de Bloch contrai em direção ao polo norte.",
         "amp"),
        (0.340, 0.22, "#F5F3FF", "#7C3AED",
         "2. Amortecimento de Fase / Dephasing (T₂)",
         "Perda de coerência quântica sem troca de população;\nContração radial no plano equatorial X–Y.",
         "phase"),
        (0.075, 0.22, "#FEF2F2", "#B91C1C",
         "3. Canal Despolarizante",
         "Contração isotrópica rumo ao estado misto máximo I/2:\nρ ↦ (1 − p)ρ + p·I/2.",
         "depol"),
    ]
    r_w = 0.062
    r_h = r_w * (7.4 / 6.2)

    for y0, h, fc, ec, title_c, desc_c, kind in noise_cards:
        card = FancyBboxPatch(
            (0.045, y0), 0.91, h,
            boxstyle="round,pad=0.006,rounding_size=0.016",
            facecolor="#FFFFFF", edgecolor=ec, lw=1.3,
            transform=ax.transAxes, zorder=2
        )
        ax.add_patch(card)
        cx, cy = 0.14, y0 + h / 2.0
        ax.add_patch(Ellipse((cx, cy), 2 * r_w, 2 * r_h, facecolor="none", edgecolor="#CBD5E1", lw=1.2, ls="--", transform=ax.transAxes, zorder=3))
        if kind == "amp":
            ax.add_patch(Ellipse((cx, cy + 0.024), 2 * r_w * 0.62, 2 * r_h * 0.62, facecolor=fc, edgecolor=ec, lw=1.5, transform=ax.transAxes, zorder=4))
            ax.annotate("", xy=(cx, cy + r_h * 0.85), xytext=(cx, cy - r_h * 0.45), arrowprops=dict(arrowstyle="-|>", color=ec, lw=1.4), transform=ax.transAxes, zorder=5)
        elif kind == "phase":
            ax.add_patch(Ellipse((cx, cy), 2 * r_w * 0.42, 2 * r_h * 0.98, facecolor=fc, edgecolor=ec, lw=1.5, transform=ax.transAxes, zorder=4))
            ax.annotate("", xy=(cx, cy), xytext=(cx + r_w * 0.92, cy), arrowprops=dict(arrowstyle="-|>", color=ec, lw=1.3), transform=ax.transAxes, zorder=5)
        else:
            ax.add_patch(Ellipse((cx, cy), 2 * r_w * 0.56, 2 * r_h * 0.56, facecolor=fc, edgecolor=ec, lw=1.5, transform=ax.transAxes, zorder=4))
            ax.scatter([cx], [cy], s=22, color=ec, transform=ax.transAxes, zorder=5)

        ax.text(0.235, y0 + h * 0.72, title_c, ha="left", va="center", fontsize=13.2, fontweight="bold", color=ec, transform=ax.transAxes, zorder=4)
        ax.text(0.235, y0 + h * 0.30, desc_c, ha="left", va="center", fontsize=12.2, color="#334155", linespacing=1.28, transform=ax.transAxes, zorder=4)

    _save_fig_and_aliases(fig, ["fig_265_canais_kraus.png"])


def gerar_fig_266_fluxo_backends_simulacao():
    """Secao 2.6.6 (a): Fluxo de Compilacao e Backends de Simulacao."""
    fig = plt.figure(figsize=(8.4, 6.2), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    _single_card(ax, "Fluxo de Compilação e Backends de Simulação",
                 "PennyLane QNode + PyTorch e Qiskit SDK / Aer sobre CPU, GPU e QPU", accent="#1D4ED8", title_fs=14.0, sub_fs=12.0)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    draw_box(ax, 0.035, 0.675, 0.450, 0.165,
             "PennyLane (QNode + TorchLayer)\nAdjoint / Backprop / Shift\nPrecisão float64 com PyTorch",
             fc="#EFF6FF", ec="#1D4ED8", fs=11.6)
    draw_box(ax, 0.515, 0.675, 0.450, 0.165,
             "Qiskit SDK e Primitivas V2\nSampler e Estimator ⟨O⟩\nTranspilação e Circuit Library",
             fc="#F5F3FF", ec="#7C3AED", fs=11.6)

    draw_box(ax, 0.045, 0.465, 0.910, 0.155,
             "Otimização (Faj et al., 2023; Bayraktar et al., 2023)\n"
             "• Gate Fusion: agrega portas em matrizes densas\n"
             "• Cache Blocking: blocos em cache L1/L2 ou GPU",
             fc="#ECFDF5", ec="#047857", fs=11.6)

    draw_arrow(ax, 0.255, 0.670, 0.35, 0.625, color="#1D4ED8", lw=1.8)
    draw_arrow(ax, 0.745, 0.670, 0.65, 0.625, color="#7C3AED", lw=1.8)

    draw_box(ax, 0.035, 0.125, 0.295, 0.285,
             "CPU Multi-Thread\nOpenMP · default.qubit\n\n"
             "• Vetor de estado exato\n"
             "• Baixa latência para\n  circuitos rasos (n ≤ 12)",
             fc="#F1F5F9", ec="#475569", fs=11.0)

    draw_box(ax, 0.352, 0.125, 0.296, 0.285,
             "GPU CUDA (cuQuantum)\ncuStateVec + cuTensorNet\n\n"
             "• Paralelismo em GPU\n"
             "• Redes Tensoriais\n  (MPS/PEPS) p/ grande n",
             fc="#DBEAFE", ec="#1D4ED8", fs=11.0)

    draw_box(ax, 0.670, 0.125, 0.295, 0.285,
             "QPU / Simulador NISQ\nDensityMatrix + Kraus\n\n"
             "• Ruído realista T₁/T₂\n"
             "• Shots finitos e\n  mitigação de erros",
             fc="#FFFBEB", ec="#B45309", fs=11.0)

    draw_arrow(ax, 0.28, 0.460, 0.185, 0.415, color="#475569", lw=1.8)
    draw_arrow(ax, 0.50, 0.460, 0.500, 0.415, color="#1D4ED8", lw=1.8)
    draw_arrow(ax, 0.72, 0.460, 0.818, 0.415, color="#B45309", lw=1.8)

    ax.text(0.50, 0.055, "Retorno de ⟨O⟩ e gradientes ∇_θ C ao otimizador clássico PyTorch",
            ha="center", va="center", fontsize=12.0, fontweight="bold", color="#0F172A", transform=ax.transAxes)

    _save_fig_and_aliases(fig, ["fig_266_fluxo_backends_simulacao.png"])


def gerar_fig_266_memoria_statevector():
    """Secao 2.6.6 (b): Memoria do Vetor de Estado (complex128)."""
    fig = plt.figure(figsize=(7.6, 5.8), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    _single_card(ax, "Memória do Vetor de Estado (complex128)",
                 "Crescimento exponencial 16 bytes × 2ⁿ em simulação exata", accent="#047857")

    ax_in = fig.add_axes([0.16, 0.24, 0.78, 0.56])
    qubits = np.array([5, 10, 20, 30, 34, 40])
    mem_bytes = 16.0 * (2.0 ** qubits)
    mem_labels = ["512 B (1 ramo)", "16 KB", "16 MB", "16 GB", "256 GB", "16 TB"]
    colors_bar = ["#047857", "#10B981", "#1D4ED8", "#F59E0B", "#EA580C", "#B91C1C"]

    y_pos = np.arange(len(qubits))
    bars = ax_in.barh(y_pos, mem_bytes, color=colors_bar, edgecolor="#1E293B", lw=0.9, height=0.58)
    ax_in.set_xscale("log")
    ax_in.set_yticks(y_pos)
    ax_in.set_yticklabels([f"n = {q}" for q in qubits], fontsize=13.0, fontweight="bold")
    ax_in.set_xlim(1e2, 3e16)
    ax_in.set_xlabel("Memória RAM / VRAM necessária (bytes, escala log)", fontsize=12.2, fontweight="bold", color="#334155")
    ax_in.tick_params(axis="x", labelsize=12.0)
    ax_in.grid(axis="x", which="major", alpha=0.5)
    ax_in.spines["top"].set_visible(False)
    ax_in.spines["right"].set_visible(False)

    for bar, lbl in zip(bars, mem_labels):
        w = bar.get_width()
        ax_in.text(w * 1.45, bar.get_y() + bar.get_height() / 2, lbl,
                   va="center", ha="left", fontsize=12.4, fontweight="bold", color="#0F172A")

    ax.text(
        0.50, 0.068,
        "Particionar 20 atributos em 4 × 5 qubits evita 2²⁰ amplitudes acopladas\n"
        "(512 B/ramo vs. 16 MB contínuos) e reduz o emaranhamento parasita.",
        ha="center", va="center", fontsize=12.1, color="#334155", linespacing=1.32, transform=ax.transAxes
    )

    _save_fig_and_aliases(fig, ["fig_266_memoria_statevector.png"])


def gerar_fig_taxonomia_modelos_hibridos_visao():
    """Figura 2.13 (Secao 2.7): Taxonomia das Quatro Familias de Modelos Hibridos para Visao."""
    fig = plt.figure(figsize=(8.8, 11.2), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")

    ax = fig.add_axes([0.01, 0.01, 0.98, 0.98])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    cards = [
        (
            0.755,
            "1. Camadas Quanvolucionais\n(Quanvolutional Neural Networks)",
            "Processamento\nespacial local",
            "#047857", "#ECFDF5",
            [("Imagem\nH × W", "#F1F5F9", "#475569"),
             ("Janelas Locais\nk × k (patches)", "#ECFDF5", "#047857"),
             ("PQC Local\ne → U → d", "#DBEAFE", "#1D4ED8"),
             ("Mapas Latentes\n+ CNN / MLP", "#F1F5F9", "#334155")],
            "Refs.: Henderson et al. (2020); Riaz et al. (2023, 2026) —\nfiltros quânticos locais substituem ou complementam convoluções."
        ),
        (
            0.505,
            "2. QCNN Variacional Pura e Redes de\nAutoatenção Quântica (QKSAN / QSAN)",
            "Hierarquia no\nespaço de Hilbert",
            "#7C3AED", "#F5F3FF",
            [("Entrada / QIR\n(FRQI / Amp.)", "#F5F3FF", "#7C3AED"),
             ("Conv. Unitárias\n+ Pooling", "#EDE9FE", "#6D28D9"),
             ("Autoatenção\n(QKSAN / QSAN)", "#F5F3FF", "#7C3AED"),
             ("Medição Final\n→ Classes K", "#F1F5F9", "#334155")],
            "Refs.: Bokhan et al. (2022); Song et al. (2024);\nDaka et al. (2026); Zhao et al. (2024); Shi et al. (2025)."
        ),
        (
            0.255,
            "3. Extrator CNN Clássico + Cabeça\nVariacional Única (Transfer Learning)",
            "Gargalo único\ncomprimido",
            "#B45309", "#FFFBEB",
            [("Imagem Geral /\nBiomédica", "#F1F5F9", "#475569"),
             ("Backbone CNN\n(ResNet / Conv)", "#FFFBEB", "#B45309"),
             ("Gargalo Linear\nDense(n)", "#FEF3C7", "#B45309"),
             ("1 PQC (n qubits)\n+ Dense(K)", "#DBEAFE", "#1D4ED8")],
            "Refs.: Schetakis et al. (2022); Long et al. (2025) —\nacopla um único registrador quântico estreito após extrator clássico."
        ),
        (
            0.005,
            "4. Extrator CNN + PQCs Paralelos Disjuntos\n(HQNN-Parallel — Adotada neste TCC)",
            "Escalável em NISQ\n(4 × 5 qubits)",
            "#1D4ED8", "#DBEAFE",
            [("Imagem 224²\n→ features128", "#F1F5F9", "#475569"),
             ("Dense(128, ReLU)\n+ Dense(20)", "#EFF6FF", "#1D4ED8"),
             ("4 PQCs (5q)\nRX + 3×SEL + ⟨Y⟩", "#DBEAFE", "#1E40AF"),
             ("Vetor ∈ ℝ²⁰\n→ Dense(K)", "#ECFDF5", "#047857")],
            "Ref.: Senokosov et al. (2024) — divide 20 atributos em 4 circuitos\nindependentes de 5 qubits sem emaranhamento cruzado."
        ),
    ]

    for y0, title, badge, ec, hfc, steps, ref_txt in cards:
        h = 0.235
        outer = FancyBboxPatch(
            (0.015, y0), 0.97, h,
            boxstyle="round,pad=0.004,rounding_size=0.014",
            facecolor="#FFFFFF", edgecolor=ec, lw=2.0 if "Adotada" in title else 1.3,
            zorder=1
        )
        ax.add_patch(outer)
        hdr = FancyBboxPatch(
            (0.025, y0 + h - 0.068), 0.95, 0.058,
            boxstyle="round,pad=0.003,rounding_size=0.010",
            facecolor=hfc, edgecolor="none", zorder=2
        )
        ax.add_patch(hdr)
        ax.text(0.036, y0 + h - 0.039, title, ha="left", va="center", fontsize=14.2, fontweight="bold",
                color="#0F172A", linespacing=1.15, zorder=3)
        badge_box = FancyBboxPatch(
            (0.720, y0 + h - 0.062), 0.245, 0.046,
            boxstyle="round,pad=0.002,rounding_size=0.010",
            facecolor=ec, edgecolor="none", zorder=3
        )
        ax.add_patch(badge_box)
        ax.text(0.8425, y0 + h - 0.039, badge, ha="center", va="center", fontsize=13.8, fontweight="bold",
                color="#FFFFFF", linespacing=1.10, zorder=4)

        xs = [0.032, 0.273, 0.514, 0.755]
        bw = 0.213
        bh = 0.088
        yb = y0 + 0.066
        for idx_s, (x_s, (txt_s, fc_s, ec_s)) in enumerate(zip(xs, steps)):
            draw_box(ax, x_s, yb, bw, bh, txt_s, fc=fc_s, ec=ec_s, fs=12.8, lw=1.3, zorder=3)
            if idx_s < len(xs) - 1:
                draw_arrow(ax, x_s + bw + 0.004, yb + bh / 2, xs[idx_s + 1] - 0.004, yb + bh / 2, color=ec, lw=1.8, zorder=4)

        ax.text(0.035, y0 + 0.032, ref_txt, ha="left", va="center", fontsize=13.8,
                color="#475569", linespacing=1.18, zorder=3)

    _save_fig_and_aliases(fig, ["fig_taxonomia_modelos_hibridos_visao.png"])


def gerar_todas_figuras_teoricas():
    gerar_fig_funcoes_ativacao_praticas()
    gerar_fig_261_esfera_bloch()
    gerar_fig_261_circuito_bell()
    gerar_fig_261_shots_bell()
    gerar_fig_263_codificacoes_vetoriais()
    gerar_fig_263_qkm_gcq()
    gerar_fig_263_qir_psnr()
    gerar_fig_264_laco_vqa()
    gerar_fig_264_parameter_shift()
    gerar_fig_265_paisagem_barren_plateau()
    gerar_fig_265_variancia_gradiente()
    gerar_fig_265_canais_kraus()
    gerar_fig_266_fluxo_backends_simulacao()
    gerar_fig_266_memoria_statevector()
    gerar_fig_taxonomia_modelos_hibridos_visao()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--teoria", action="store_true", help="Gera as figuras teóricas das Seções 2.5, 2.6 e 2.7")
    parser.add_argument("--ativacoes", action="store_true", help="Gera apenas a figura das funções de ativação da Seção 2.5.1")
    parser.add_argument("--balanceamento", action="store_true", help="Gera as figuras de balanceamento da Seção 3.4.2")
    parser.add_argument("--all", action="store_true", help="Gera todas as figuras do script (padrão)")
    args = parser.parse_args()

    run_all = args.all or (not args.teoria and not args.balanceamento and not args.ativacoes)
    if run_all:
        gerar_figs_balanceamento()
        gerar_fig_oclusao_trocas_globais()
        gerar_diagrama_etapa1_cnn()
        gerar_diagrama_etapa2_dense20()
        gerar_diagrama_etapa3_hibrida()
        gerar_diagrama_comparativo_mudancas()
        gerar_diagrama_circuito_quantico_5qubits()
        gerar_todas_figuras_teoricas()
        print("Todas as figuras limpas de revisao/arquitetura/circuito/teoria foram geradas!")
    else:
        if args.balanceamento:
            gerar_figs_balanceamento()
        if args.teoria:
            gerar_todas_figuras_teoricas()
        elif args.ativacoes:
            gerar_fig_funcoes_ativacao_praticas()
