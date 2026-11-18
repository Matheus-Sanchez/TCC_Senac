# -*- coding: utf-8 -*-
"""Gera as figuras revisadas de alta resolucao (300 DPI) para R4, R5 e R7 da monografia TCC2."""

import json
import pathlib
from collections import defaultdict
from html.parser import HTMLParser
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

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
    "text.color": "#1E293B",
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
    ("oversample", "Sobreamostragem (oversample)", "#0F766E"),
    ("class_weight", "Peso na perda (class_weight)", "#D97706"),
    ("undersample", "Subamostragem (undersample)", "#DC2626"),
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


def draw_box(ax, x, y, w, h, text, fc="#F1F5F9", ec="#64748B", lw=1.2, fs=8.2, fw="normal", text_color="#0F172A", ls="-"):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.004,rounding_size=0.012",
        facecolor=fc, edgecolor=ec, linewidth=lw, linestyle=ls, zorder=3
    )
    ax.add_patch(box)
    ax.text(
        x + w / 2.0, y + h / 2.0, text,
        ha="center", va="center", fontsize=fs, fontweight=fw,
        color=text_color, zorder=4, linespacing=1.28
    )


def draw_arrow(ax, x1, y1, x2, y2, color="#475569", lw=1.5, rad=0.0, ls="-"):
    arr = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>,head_length=5.5,head_width=3.2",
        color=color, linewidth=lw, linestyle=ls,
        connectionstyle=f"arc3,rad={rad}",
        zorder=2
    )
    ax.add_patch(arr)


def gerar_figs_balanceamento():
    df = parse_notebook_table(6)
    summary = parse_notebook_table(9)

    # 1) Macro-F1 (%) by dataset and balancing mode
    fig, ax = plt.subplots(figsize=(13.6, 5.9), dpi=300)
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
                    v + 1.2,
                    fmt_pt(v, 1),
                    ha="center", va="bottom", fontsize=7.5, fontweight="bold",
                    color=color, rotation=90
                )

    ax.axvspan(5.55, 8.45, color="#FEF3C7", alpha=0.38, zorder=1)
    ax.text(7.0, 117.5, "Bases fortemente desbalanceadas (IR = 3,03x a 16,43x)",
            ha="center", va="top", fontsize=8.8, fontweight="bold", color="#92400E")

    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, lbl in DS_CANONICAL_ORDER], fontsize=10.0, fontweight="bold")
    ax.set_ylim(0, 121)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_ylabel("Macro-F1 de teste (%)", fontsize=10.5, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(
        loc="lower center", bbox_to_anchor=(0.5, 1.01),
        ncol=4, fontsize=9.2, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1"
    )
    fig.suptitle(
        "Macro-F1 de Teste por Conjunto de Dados e Modo de Balanceamento (CNN Original, 36 Execuções)",
        fontsize=12.6, fontweight="bold", y=1.06
    )

    out1 = OUT_DIR / "fig_balanceamento_macro_f1.png"
    fig.savefig(out1, dpi=300, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print("Gerado:", out1)

    # 2) Two-panel figure: (A) Training hours + (B) Delta Macro-F1 (p.p.) vs all_raw
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.4, 6.1), dpi=300,
                                   gridspec_kw={"width_ratios": [1.05, 1.0], "wspace": 0.24})

    for (mode, label, color), off in zip(MODE_META, offsets):
        hrs = [float(lookup.loc[(ds, mode), "training_hours"]) for ds, _ in DS_CANONICAL_ORDER]
        bars = ax1.bar(x + off, hrs, width=w * 0.90, color=color, label=label, alpha=0.93, zorder=3)
        for bar, h_val in zip(bars, hrs):
            if h_val >= 4.4:
                ax1.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    h_val + 0.18,
                    f"{fmt_pt(h_val, 2)}h",
                    ha="center", va="bottom", fontsize=7.3, fontweight="bold", color=color, rotation=90
                )

    ax1.set_xticks(x)
    ax1.set_xticklabels([lbl for _, lbl in DS_CANONICAL_ORDER], fontsize=8.8, fontweight="bold", rotation=25, ha="right")
    ax1.set_ylim(0, 11.7)
    ax1.set_ylabel("Tempo total de treino (horas, soma das épocas)", fontsize=9.6, fontweight="bold")
    ax1.set_title("A. Tempo de treinamento por execução (total: 88,86 h)", fontsize=10.6, fontweight="bold", pad=10)
    ax1.grid(True, axis="y", alpha=0.8)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    deltas_meta = MODE_META[1:]
    w2 = 0.25
    offs2 = [-w2, 0.0, w2]
    for (mode, label, color), off in zip(deltas_meta, offs2):
        deltas = [
            (float(lookup.loc[(ds, mode), "test_macro_f1"]) - float(lookup.loc[(ds, "all_raw"), "test_macro_f1"])) * 100.0
            for ds, _ in DS_CANONICAL_ORDER
        ]
        bars = ax2.bar(x + off, deltas, width=w2 * 0.90, color=color, label=label, alpha=0.93, zorder=3)
        for bar, dv, (ds, _) in zip(bars, deltas, DS_CANONICAL_ORDER):
            if abs(dv) >= 1.2:
                va = "top" if dv < 0 else "bottom"
                dy = -0.45 if dv < 0 else 0.35
                ha = "right" if (ds == "fer2013" and mode == "class_weight") else "center"
                dx = bar.get_width() * 0.45 if ha == "right" else bar.get_width() / 2.0
                ax2.text(
                    bar.get_x() + dx, dv + dy,
                    f"{fmt_pt(dv, 2)}",
                    ha=ha, va=va, fontsize=7.3, fontweight="bold", color=color
                )

    ax2.axhline(0.0, color="#0F172A", linewidth=1.1, zorder=4)
    ax2.set_xticks(x)
    ax2.set_xticklabels([lbl for _, lbl in DS_CANONICAL_ORDER], fontsize=8.8, fontweight="bold", rotation=25, ha="right")
    ax2.set_ylim(-22.5, 4.0)
    ax2.set_ylabel("Δ Macro-F1 vs. all_raw (pontos percentuais)", fontsize=9.6, fontweight="bold")
    ax2.set_title("B. Ganho ou perda frente à distribuição original (all_raw)", fontsize=10.6, fontweight="bold", pad=10)
    ax2.grid(True, axis="y", alpha=0.8)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    fig.subplots_adjust(top=0.80)
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(
        handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.925),
        ncol=4, fontsize=9.0, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1"
    )
    fig.suptitle(
        "Custo Temporal e Impacto Relativo dos Modos de Balanceamento (Justificativa Empírica de all_raw)",
        fontsize=12.4, fontweight="bold", y=0.985
    )

    out2 = OUT_DIR / "fig_balanceamento_tempo_treino.png"
    fig.savefig(out2, dpi=300, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print("Gerado:", out2)
    print(summary.to_string(index=False))


def gerar_figs_arquitetura_separadas():
    # Diagram 1: Classical Architecture & Flows (matching 4d5b7c4b.png + model_summary.txt)
    fig, ax = plt.subplots(figsize=(14.6, 7.2), dpi=300)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    ax.text(
        0.50, 0.978,
        "Arquitetura Clássica: Extrator CNN Compartilhado e Três Fluxos de Cabeças",
        ha="center", va="top", fontsize=14.0, fontweight="bold", color="#0F172A"
    )
    ax.text(
        0.50, 0.938,
        "Uma origem convolucional comum em FP32 por base; cabeças e regimes de treinamento distintos (36 modelos clássicos)",
        ha="center", va="top", fontsize=9.8, color="#475569"
    )

    bg = FancyBboxPatch((0.010, 0.025), 0.980, 0.875, boxstyle="round,pad=0.004,rounding_size=0.012",
                        facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.1, zorder=1)
    ax.add_patch(bg)

    # Top row
    draw_box(ax, 0.022, 0.690, 0.130, 0.175,
             "Imagem de Entrada\n\n64×64×C (8 bases)\n128×128×3 (GTSRB)\nFP32 em [0, 1]",
             fc="#E2E8F0", ec="#475569", fs=8.3, fw="bold")

    draw_box(ax, 0.176, 0.690, 0.228, 0.175,
             "Extrator CNN (5 Blocos)\n32 → 48 → 64 → 96 → 128 canais\n\n66.905 pesos (C=1)\n67.019 pesos (C=3)",
             fc="#DBEAFE", ec="#2563EB", fs=8.5, fw="bold")

    draw_box(ax, 0.428, 0.690, 0.170, 0.175,
             "Saída block5_pool\n\n1×1×128 (64×64 px)\n2×2×128 (GTSRB 128)",
             fc="#DBEAFE", ec="#2563EB", fs=8.3)

    draw_box(ax, 0.625, 0.675, 0.350, 0.195,
             "Fluxo 1: Cabeça CNN Original\n(9 treinos Linux · aumento 50% · LS = 0,05)\nGAP(128)+GMP(128) → Concat(256)\n→ [Drop(0,4) → Dense(256, SiLU)]×2 → K\nCabeça: 131.584+257K | Total: 201.059 (C=1, K=10)",
             fc="#EFF6FF", ec="#1D4ED8", fs=7.8, fw="bold")

    ax.text(0.320, 0.630,
            "Cada bloco: SepConv2D(5×5, s=2 no B1) → GN(16) → SiLU → SepConv2D(3×3) → GN(16) → SiLU → MaxPool(2×2)",
            ha="center", va="center", fontsize=8.0, color="#334155", style="italic", zorder=5,
            bbox=dict(boxstyle="round,pad=0.22", facecolor="#FFFFFF", edgecolor="#CBD5E1"))

    draw_arrow(ax, 0.156, 0.777, 0.172, 0.777)
    draw_arrow(ax, 0.408, 0.777, 0.424, 0.777)
    draw_arrow(ax, 0.602, 0.777, 0.621, 0.777, color="#1D4ED8")

    # Middle-left freeze box -> GAP -> features128
    draw_box(ax, 0.025, 0.230, 0.220, 0.295,
             "Extrator Congelado\n(melhor checkpoint de val.)\n↓\nGAP(128) → features128\n\n128 valores aprendidos\ncompartilhados por base",
             fc="#FEF3C7", ec="#D97706", fs=8.5, fw="bold")

    # Clean routed connection from block5_pool down to Extrator Congelado without crossing Fluxo 2
    ax.plot([0.513, 0.513, 0.135], [0.686, 0.585, 0.585], color="#B45309", linewidth=1.6, zorder=2)
    draw_arrow(ax, 0.135, 0.585, 0.135, 0.531, color="#B45309")

    # Lower-left: Fluxo 2 (Dense20 imagem)
    draw_box(ax, 0.285, 0.370, 0.395, 0.185,
             "Fluxo 2: Dense20 sobre Imagens (D20 img.)\n(9 treinos Linux · aumento 50% ativo · LS = 0,05)\nGAP(128) → Dense(20, linear) [2.580] → LayerNorm(10⁻³) [40]\n→ ReLU → logits Dense(K) [21K]\nTreinável: 2.620+21K (2.830 p/ K=10) | Cadeia: 69.735 (C=1)",
             fc="#FFEDD5", ec="#EA580C", fs=7.8, fw="bold")

    draw_arrow(ax, 0.249, 0.430, 0.281, 0.460, color="#EA580C")

    # Lower-right: Fluxo 3 (Dense20 vetorial)
    draw_box(ax, 0.285, 0.130, 0.395, 0.195,
             "Fluxo 3: Dense20 Vetorial (Vet. Linux / Vet. Mac)\n(18 treinos: 9 Linux + 9 Mac sobre .npy salvos, sem aumento)\nfeatures128 → Dense(128, ReLU) [16.512] → Dense(20, linear) [2.580]\n→ tanh → logits Dense(K) [21K]\nTreinável: 19.092+21K (19.302 p/ K=10) | Cadeia: 86.207 (C=1)",
             fc="#DCFCE7", ec="#15803D", fs=7.7, fw="bold")

    draw_arrow(ax, 0.249, 0.310, 0.281, 0.225, color="#15803D")

    # Right methodological control & link to Fluxo 4
    draw_box(ax, 0.715, 0.345, 0.260, 0.215,
             "Controle Dimensional (n = 20)\n• D20 img.: LayerNorm + ReLU\n  direto com imagens aumentadas\n• Dense20 vetorial: controle direto\n  sobre features128 congeladas\n• Paridade Linux vs. Mac confirma\n  consistência numérica do .npy",
             fc="#F1F5F9", ec="#64748B", fs=7.8)
    draw_arrow(ax, 0.684, 0.462, 0.711, 0.455, color="#64748B")
    draw_arrow(ax, 0.684, 0.255, 0.711, 0.380, color="#64748B")

    draw_box(ax, 0.715, 0.130, 0.260, 0.175,
             "Ponte para o Fluxo 4 (PQC 4×5)\nMesma entrada features128 e\nprojeção Dense(128) → Dense(20),\nsubstituindo tanh por 4 circuitos\nde 5 qubits (Figura seguinte)",
             fc="#EDE9FE", ec="#6D28D9", fs=7.8, fw="bold", ls="--")
    draw_arrow(ax, 0.684, 0.195, 0.711, 0.205, color="#6D28D9", ls="--")

    ax.text(0.50, 0.058,
            "Nota: Nas 8 bases de 64×64 px, block5_pool possui resolução 1×1×128 (GAP ≡ GMP); no GTSRB (128×128 px), block5_pool é 2×2×128.",
            ha="center", va="center", fontsize=8.4, color="#475569")

    out1 = OUT_DIR / "fig_arquitetura_classica_fluxos.png"
    fig.savefig(out1, dpi=300, bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)
    print("Gerado:", out1)

    # Diagram 2: Hybrid 4x5 Qubit Head (matching 45e083f9.jpg + model_summary.txt + circuit.txt)
    fig, ax = plt.subplots(figsize=(14.6, 7.0), dpi=300)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    ax.text(
        0.50, 0.978,
        "Fluxo 4: Cabeça Híbrida Quântico-Clássica (4 Circuitos Independentes de 5 Qubits)",
        ha="center", va="top", fontsize=14.0, fontweight="bold", color="#0F172A"
    )
    ax.text(
        0.50, 0.938,
        "36 execuções (Windows/iMac M4 × PennyLane/Qiskit Aer) sobre vetores features128 congelados (model_summary.txt e circuit.txt)",
        ha="center", va="top", fontsize=9.8, color="#475569"
    )

    bg = FancyBboxPatch((0.010, 0.025), 0.980, 0.875, boxstyle="round,pad=0.004,rounding_size=0.012",
                        facecolor="#FAF5FF", edgecolor="#C4B5FD", linewidth=1.2, zorder=1)
    ax.add_patch(bg)

    draw_box(ax, 0.024, 0.245, 0.195, 0.580,
             "Entrada & Projeção\n\nfeatures128 (salvas)\n(None, 128) [0 pesos]\n↓\ndense_128_128\nDense(128, ReLU)\n[16.512 pesos]\n↓\ndense_128_20\nDense(20, linear)\n[2.580 pesos]\n↓\nu ∈ ℝ²⁰ (4 × 5 rad)",
             fc="#DCFCE7", ec="#15803D", fs=8.3, fw="bold")

    branch_ys = [0.705, 0.552, 0.399, 0.246]
    for idx, by in enumerate(branch_ys, start=1):
        u_slice = f"u[{5*(idx-1)}:{5*idx}]"
        draw_box(ax, 0.252, by, 0.405, 0.118,
                 f"Ramo {idx} — 5 qubits ({u_slice})  |  45 pesos quânticos\n|0⟩⊗⁵ → RX(u) → 3×[RZ–RY–RZ + 5 CNOT circ. (alcances 1, 2, 3)]",
                 fc="#EDE9FE", ec="#6D28D9", fs=7.7, fw="bold")
        draw_arrow(ax, 0.223, 0.535, 0.248, by + 0.059, color="#6D28D9")

        draw_box(ax, 0.678, by, 0.145, 0.118,
                 "5 expectativas\nPauli-Y ∈ [-1, 1]\n(⟨Y₀⟩ ... ⟨Y₄⟩)",
                 fc="#FCE7F3", ec="#BE185D", fs=8.0, fw="bold")
        draw_arrow(ax, 0.661, by + 0.059, 0.674, by + 0.059, color="#BE185D")

    draw_box(ax, 0.844, 0.245, 0.132, 0.580,
             "Classificação\n\nConcat(20)\n(parallel_pqc20)\n↓\nlogits\nDense(K, linear)\n[21K pesos]\n\nTreinável:\n19.272 + 21K\n(19.482 p/ K=10)\n\nCadeia (C=1):\n86.387 pesos",
             fc="#E0F2FE", ec="#0369A1", fs=8.0, fw="bold")

    for by in branch_ys:
        draw_arrow(ax, 0.827, by + 0.059, 0.840, 0.535, color="#0369A1")

    draw_box(ax, 0.024, 0.052, 0.952, 0.152,
             "Detalhe de cada subcircuito (5 fios, 2⁵ = 32 amplitudes, sem emaranhamento cruzado entre os 4 ramos):\n"
             "RX(u_j) em j=0..4 → Bloco 1 [RZ–RY–RZ + CNOT_circ(1)] → Bloco 2 [RZ–RY–RZ + CNOT_circ(2)] → Bloco 3 [RZ–RY–RZ + CNOT_circ(3)] → ⟨Y_j⟩\n"
             "45 pesos por circuito = 180 pesos quânticos  |  404 avaliações lógicas por exemplo no treino (parameter-shift ±π/2); 4 na validação/teste  |  Simulação CPU ideal",
             fc="#FFFFFF", ec="#7C3AED", fs=7.7, fw="bold", text_color="#4C1D95")

    out2 = OUT_DIR / "fig_arquitetura_hibrida_4x5_qubits.png"
    fig.savefig(out2, dpi=300, bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)
    print("Gerado:", out2)


def gerar_fig_oclusao_trocas_globais():
    with open(JSON_OCL, encoding="utf-8") as f:
        m = json.load(f)

    flips_by_ds = defaultdict(lambda: {"desfoque": 0, "media": 0})
    for s in m["summaries"]:
        flips_by_ds[s["dataset"]][s["method"]] += int(s["flips"])

    ds_items = [
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

    fig, ax = plt.subplots(figsize=(13.4, 5.4), dpi=300)
    x = np.arange(len(ds_items))
    w = 0.34
    gap = 0.02
    vals_desf = [flips_by_ds[d]["desfoque"] for d, _ in ds_items]
    vals_med = [flips_by_ds[d]["media"] for d, _ in ds_items]

    b1 = ax.bar(x - w / 2 - gap, vals_desf, width=w, color="#0284C7",
                label="Borramento gaussiano (4.096 oclusões/base)", zorder=3)
    b2 = ax.bar(x + w / 2 + gap, vals_med, width=w, color="#DC2626",
                label="Preenchimento pela média da imagem (4.096 oclusões/base)", zorder=3)

    for bar, v in zip(b1, vals_desf):
        pct = 100.0 * v / 4096.0
        ax.text(bar.get_x() + bar.get_width() / 2, v + 18, f"{v}\n({fmt_pt(pct, 1)}%)",
                ha="center", va="bottom", fontsize=7.5, fontweight="bold", color="#0369A1")
    for bar, v in zip(b2, vals_med):
        pct = 100.0 * v / 4096.0
        ax.text(bar.get_x() + bar.get_width() / 2, v + 18, f"{v}\n({fmt_pt(pct, 1)}%)",
                ha="center", va="bottom", fontsize=7.5, fontweight="bold", color="#991B1B")

    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, lbl in ds_items], fontsize=10.0, fontweight="bold")
    ax.set_ylim(0, 1200)
    ax.set_ylabel("Trocas de classe predita\n(em 4.096 blocos por método)", fontsize=10.0, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.8)
    ax.legend(loc="upper left", fontsize=9.4, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.set_title(
        "Sensibilidade Global nas 73.728 Oclusões (8 amostras × 8 modelos × 64 blocos × 2 métodos)\n"
        "Mediana de correlação Spearman (Grad-CAM block4_activation2 vs. queda de logit por oclusão): ρ = 0,002",
        fontsize=11.0, fontweight="bold", pad=12
    )

    out_path = OUT_DIR / "fig_oclusao_trocas_globais.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print("Gerado:", out_path)


if __name__ == "__main__":
    gerar_figs_balanceamento()
    gerar_figs_arquitetura_separadas()
    gerar_fig_oclusao_trocas_globais()
    print("Todas as figuras revisadas de R4, R5 e R7 foram geradas com sucesso!")
