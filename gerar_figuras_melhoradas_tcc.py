# -*- coding: utf-8 -*-
"""Gera as 5 figuras melhoradas e integradas de alta resolucao (300 DPI) para o TCC."""

import json
import pathlib
from collections import defaultdict
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from PIL import Image

OUT_DIR = pathlib.Path(r"C:\Users\matheus.sduda\repos\TCC\TCC_Senac\figuras")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ROOT_OUT = pathlib.Path(r"C:\Users\matheus.sduda\Documents\ChatGPT\projeto-do-tcc\outputs")
CSV_FIG26 = ROOT_OUT / "analise-ilustrada-2026-10-27" / "dados_dos_graficos" / "figura_26_comparacao_matriz.csv"
CSV_TEMPOS = ROOT_OUT / "graficos-cnn-completa-batch128-vs-quantico-2026-11-16" / "01_tempos_por_execucao.csv"
CSV_COMP_QC = ROOT_OUT / "graficos-tempos-batch128-2026-11-16" / "comparacoes_classico_quantico.csv"
CSV_AMB_Q = ROOT_OUT / "graficos-cnn-completa-batch128-vs-quantico-2026-11-16" / "05_ambientes_quanticos.csv"
CSV_SIM_Q = ROOT_OUT / "graficos-cnn-completa-batch128-vs-quantico-2026-11-16" / "06_simuladores_quanticos.csv"
DIR_HW_IO = ROOT_OUT / "graficos-hardware-io-batch128-2026-11-18"
CSV_EPOCAS = DIR_HW_IO / "dados_por_epoca.csv"
CSV_SESSOES = DIR_HW_IO / "sessoes_e_fontes.csv"
JSON_OCL = ROOT_OUT / "oclusao-completa-2026-11-07" / "manifesto_completo.json"
IMG_GRADCAM = ROOT_OUT / "explicabilidade-gradcam-2026-11-05" / "paineis_comparativos" / "gtsrb" / "gtsrb_01.png"
IMG_OCLUSAO = ROOT_OUT / "oclusao-completa-2026-11-07" / "relatorio_interativo" / "dist" / "paineis" / "gtsrb_01_media.png"

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

DATASET_ORDER = [
    "MNIST",
    "Fashion-MNIST",
    "KMNIST",
    "EMNIST Balanced",
    "CIFAR-10",
    "CIFAR-100 Coarse",
    "SVHN",
    "GTSRB",
    "FER2013",
]

SHORT_NAMES = {
    "MNIST": "MNIST",
    "Fashion-MNIST": "Fashion-MNIST",
    "KMNIST": "KMNIST",
    "EMNIST Balanced": "EMNIST Bal.",
    "CIFAR-10": "CIFAR-10",
    "CIFAR-100 Coarse": "CIFAR-100 C.",
    "SVHN": "SVHN",
    "GTSRB": "GTSRB",
    "FER2013": "FER2013",
}


def fmt_pt(val: float, decimals: int = 2) -> str:
    return f"{val:.{decimals}f}".replace(".", ",")


def draw_box(ax, x, y, w, h, text, fc="#F1F5F9", ec="#64748B", lw=1.2, fs=8.8, fw="normal", text_color="#0F172A"):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.004,rounding_size=0.012",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3
    )
    ax.add_patch(box)
    ax.text(
        x + w / 2.0, y + h / 2.0, text,
        ha="center", va="center", fontsize=fs, fontweight=fw,
        color=text_color, zorder=4, linespacing=1.28
    )


def draw_arrow(ax, x1, y1, x2, y2, color="#475569", lw=1.4, rad=0.0):
    arr = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>,head_length=5.5,head_width=3.2",
        color=color, linewidth=lw,
        connectionstyle=f"arc3,rad={rad}",
        zorder=2
    )
    ax.add_patch(arr)


def gerar_fig_arquitetura():
    fig, ax = plt.subplots(figsize=(15.0, 10.2), dpi=300)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    ax.text(
        0.5, 0.980,
        "Arquitetura Completa da Campanha (72 Modelos): Extrator CNN Compartilhado e Quatro Fluxos de Cabeças",
        ha="center", va="top", fontsize=13.5, fontweight="bold", color="#0F172A"
    )
    ax.text(
        0.5, 0.952,
        "9 bases × 8 configurações (seed 42): 9 CNNs base, 9 Dense20 imagem, 18 Dense20 vetoriais (Linux/Mac) e 36 híbridas 4×5 qubits (Win/Mac × PennyLane/Qiskit)",
        ha="center", va="top", fontsize=9.6, color="#475569"
    )

    # Painel A
    panel_a = FancyBboxPatch((0.012, 0.445), 0.976, 0.488, boxstyle="round,pad=0.004,rounding_size=0.012",
                             facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.1, zorder=1)
    ax.add_patch(panel_a)
    ax.text(0.025, 0.913, "A. Extrator CNN (FP32) e bifurcação nos fluxos clássicos (Linux e Mac)",
            ha="left", va="center", fontsize=11.0, fontweight="bold", color="#1E3A5F", zorder=4)

    draw_box(ax, 0.025, 0.775, 0.135, 0.100,
             "Entrada\n64×64×C (8 bases)\n128×128×3 (GTSRB)", fc="#E2E8F0", ec="#475569", fs=8.5, fw="bold")
    draw_box(ax, 0.185, 0.775, 0.255, 0.100,
             "Extrator Convolucional (5 Blocos)\n32 → 48 → 64 → 96 → 128 canais\n66.905 pesos (C=1) | 67.019 (C=3)",
             fc="#DBEAFE", ec="#2563EB", fs=8.5, fw="bold")
    draw_box(ax, 0.465, 0.775, 0.185, 0.100,
             "block5_pool\n1×1×128 (64×64 px)\n2×2×128 (GTSRB 128 px)",
             fc="#DBEAFE", ec="#2563EB", fs=8.5)
    draw_box(ax, 0.675, 0.760, 0.300, 0.125,
             "1. Cabeça CNN Original (9 treinos Linux)\nGAP(128)+GMP(128) → Concat(256)+Drop(0,4)\n→ Dense(256, SiLU) → Drop → Dense(256, SiLU) → K\n131.584+257K cabeça (201.059 tot. C=1, K=10)",
             fc="#EFF6FF", ec="#1D4ED8", fs=8.1, fw="bold")

    ax.text(0.34, 0.742,
            "Bloco i: SeparableConv2D(5×5, s=2 no Bloco 1) → GroupNorm(16) → SiLU → SeparableConv2D(3×3) → GroupNorm(16) → SiLU → MaxPool(2×2)",
            ha="center", va="center", fontsize=8.0, color="#334155", style="italic", zorder=5,
            bbox=dict(boxstyle="round,pad=0.18", facecolor="#F8FAFC", edgecolor="none", alpha=0.95))

    draw_arrow(ax, 0.164, 0.825, 0.181, 0.825)
    draw_arrow(ax, 0.444, 0.825, 0.461, 0.825)
    draw_arrow(ax, 0.654, 0.825, 0.671, 0.825, color="#1D4ED8")

    # Linha inferior do Painel A
    draw_box(ax, 0.025, 0.480, 0.255, 0.205,
             "Extrator Congelado + GAP(128)\n\n• Fluxo 2 (9 treinos Linux):\n  Aumento 50% ativo na imagem\n• Fluxos vetorial e quântico:\n  Exportação única para .npz (features128)\n  em inferência determinística (sem aumento)",
             fc="#FEF3C7", ec="#D97706", fs=8.1)
    draw_arrow(ax, 0.557, 0.771, 0.284, 0.630, color="#B45309", rad=-0.04)

    draw_box(ax, 0.315, 0.595, 0.345, 0.105,
             "2. Dense20 sobre Imagens (9 treinos Linux)\nGAP(128) → Dense(20) → LayerNorm → ReLU → K\n2.620+21K treináveis (69.735 cadeia, C=1, K=10)",
             fc="#FFEDD5", ec="#EA580C", fs=8.0, fw="bold")
    draw_arrow(ax, 0.284, 0.615, 0.311, 0.648, color="#EA580C")

    draw_box(ax, 0.315, 0.468, 0.345, 0.105,
             "3. Dense20 Vetorial (18 treinos: 9 Linux + 9 Mac)\nfeatures128 → Dense(128, ReLU) → Dense(20) → tanh → K\n19.092+21K treináveis (86.207 cadeia, C=1, K=10)",
             fc="#DCFCE7", ec="#15803D", fs=8.0, fw="bold")
    draw_arrow(ax, 0.284, 0.545, 0.311, 0.520, color="#15803D")

    draw_box(ax, 0.690, 0.485, 0.285, 0.195,
             "Controle Metodológico do Gargalo (n=20)\n• Fluxos 2 e 3 não são arquiteturalmente\n  idênticos: LayerNorm+ReLU (com imagem)\n  vs. Dense128+tanh (sobre features128)\n• Campanhas Linux e Mac do Fluxo 3 confirmam\n  consistência numérica sobre o mesmo .npz",
             fc="#F1F5F9", ec="#64748B", fs=7.9)
    draw_arrow(ax, 0.664, 0.648, 0.686, 0.600, color="#64748B")
    draw_arrow(ax, 0.664, 0.520, 0.686, 0.560, color="#64748B")

    # Painel B
    panel_b = FancyBboxPatch((0.012, 0.020), 0.976, 0.405, boxstyle="round,pad=0.004,rounding_size=0.012",
                             facecolor="#FAF5FF", edgecolor="#C4B5FD", linewidth=1.2, zorder=1)
    ax.add_patch(panel_b)
    ax.text(0.025, 0.403,
            "B. Fluxo 4: Cabeça Híbrida Quântico-Clássica 4×5 Qubits (36 treinos: Windows/Mac × PennyLane/Qiskit)",
            ha="left", va="center", fontsize=11.0, fontweight="bold", color="#4C1D95", zorder=4)

    draw_box(ax, 0.025, 0.125, 0.175, 0.220,
             "Entrada & Projeção\nfeatures128 (salvas)\n↓\nDense(128, ReLU)\n[16.512 pesos]\n↓\nDense(20, linear)\n[2.580 pesos]",
             fc="#DCFCE7", ec="#15803D", fs=8.3, fw="bold")

    branch_ys = [0.305, 0.230, 0.155, 0.080]
    for idx, by in enumerate(branch_ys, start=1):
        draw_box(ax, 0.240, by, 0.380, 0.060,
                 f"Ramo {idx} (5 qubits, u[{5*(idx-1)}:{5*idx}])  |  45 pesos quânticos\nCodif. RX → 3×[RZ–RY–RZ + 5 CNOT circ. (1, 2, 3)]",
                 fc="#EDE9FE", ec="#6D28D9", fs=7.7, fw="bold")
        draw_arrow(ax, 0.204, 0.235, 0.236, by + 0.030, color="#6D28D9")

        draw_box(ax, 0.648, by, 0.160, 0.060,
                 "5 Pauli-Y ∈ [-1, 1]\n(sem emaranh. cruzado)",
                 fc="#FCE7F3", ec="#BE185D", fs=7.6)
        draw_arrow(ax, 0.624, by + 0.030, 0.644, by + 0.030, color="#BE185D")

    draw_box(ax, 0.835, 0.125, 0.140, 0.220,
             "Classificação\nConcat(20)\n↓\nDense(K logits)\n[21K pesos]\n\nTreinável: 19.272+21K\n(86.387 cadeia)",
             fc="#E0F2FE", ec="#0369A1", fs=8.1, fw="bold")

    for by in branch_ys:
        draw_arrow(ax, 0.812, by + 0.030, 0.831, 0.235, color="#0369A1")

    ax.text(0.50, 0.042,
            "180 pesos quânticos no total (4×45); simulação local ideal em CPU (sem QPU real); 404 avaliações lógicas por exemplo no treino (parameter-shift ±π/2) e 4 na inferência.",
            ha="center", va="center", fontsize=8.3, color="#4C1D95", fontweight="bold", zorder=4)

    out_path = OUT_DIR / "fig_arquitetura_fluxos_e_cabecas.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_fig_tempos_100_epocas():
    df_t = pd.read_csv(CSV_TEMPOS, sep=";", decimal=",")
    df_c = pd.read_csv(CSV_COMP_QC, sep=";", decimal=".")

    vet_linux = df_c[df_c["comparacao"].str.contains("Windows · PennyLane")].set_index("dataset")["classico_segundos"]
    vet_mac = df_c[df_c["comparacao"].str.contains("Mac · PennyLane")].set_index("dataset")["classico_segundos"]

    cnn_b128 = df_t[df_t["tipo"] == "CNN campanha batch"].set_index("dataset")["soma_100_epocas_segundos"]
    q_w_pl = df_t[df_t["configuracao"] == "PQC Windows PennyLane"].set_index("dataset")["soma_100_epocas_segundos"]
    q_w_qk = df_t[df_t["configuracao"] == "PQC Windows Qiskit"].set_index("dataset")["soma_100_epocas_segundos"]
    q_m_pl = df_t[df_t["configuracao"] == "PQC Mac PennyLane"].set_index("dataset")["soma_100_epocas_segundos"]
    q_m_qk = df_t[df_t["configuracao"] == "PQC Mac Qiskit"].set_index("dataset")["soma_100_epocas_segundos"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.2, 8.2), dpi=300, sharey=True,
                                   gridspec_kw={"width_ratios": [1.15, 1.0], "wspace": 0.08})

    y = np.arange(len(DATASET_ORDER))[::-1].astype(float)
    ds_labels = [SHORT_NAMES[d] for d in DATASET_ORDER]

    # Pequenos deslocamentos verticais entre as series quanticas para evitar sobreposicao dos triangulos
    series_a = [
        ("Vetorial Mac (128-20)", [vet_mac[d] for d in DATASET_ORDER], "o", "#0F766E", 8.0, 0.0),
        ("Vetorial Linux (128-20)", [vet_linux[d] for d in DATASET_ORDER], "s", "#65A30D", 7.2, 0.0),
        ("CNN batch-128 (Linux, mixed_fp16)", [cnn_b128[d] for d in DATASET_ORDER], "D", "#334155", 7.2, 0.0),
        ("PQC Mac · PennyLane", [q_m_pl[d] for d in DATASET_ORDER], "^", "#7C3AED", 8.2, +0.16),
        ("PQC Windows · PennyLane", [q_w_pl[d] for d in DATASET_ORDER], "^", "#2563EB", 8.2, -0.16),
        ("PQC Mac · Qiskit", [q_m_qk[d] for d in DATASET_ORDER], "v", "#D97706", 8.2, +0.16),
        ("PQC Windows · Qiskit", [q_w_qk[d] for d in DATASET_ORDER], "v", "#B91C1C", 8.2, -0.16),
    ]

    for i, ds in enumerate(DATASET_ORDER):
        vals = [s[1][i] for s in series_a]
        ax1.hlines(y[i], min(vals), max(vals), color="#CBD5E1", linewidth=1.6, zorder=1)
        ax1.text(vet_mac[ds] * 0.78, y[i], f"{fmt_pt(vet_mac[ds], 1)} s",
                 ha="right", va="center", fontsize=8.4, color="#0F766E", fontweight="bold")
        ax1.text(q_w_qk[ds] * 1.24, y[i], f"{fmt_pt(q_w_qk[ds]/3600.0, 1)} h",
                 ha="left", va="center", fontsize=8.4, color="#991B1B", fontweight="bold")

    for label, vals, marker, color, ms, dy in series_a:
        ax1.scatter(vals, y + dy, label=label, marker=marker, s=ms**2, color=color, edgecolors="#FFFFFF", linewidths=0.8, zorder=4)

    ax1.set_xscale("log")
    ax1.set_xlim(2.5, 9e5)
    ax1.set_yticks(y)
    ax1.set_yticklabels(ds_labels, fontsize=10.5, fontweight="bold")
    ax1.set_xlabel("Soma das 100 épocas em segundos (escala log)", fontsize=10.0)
    ax1.set_title("A. Tempo total de 100 épocas (lote 128)", fontsize=11.3, fontweight="bold", pad=10)
    ax1.grid(True, axis="x", which="major", alpha=0.8)
    ax1.legend(loc="upper center", bbox_to_anchor=(0.48, -0.10), fontsize=8.5, frameon=True,
               facecolor="#FFFFFF", edgecolor="#CBD5E1", ncol=2)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    h = 0.19
    configs_b = [
        ("Mac · PennyLane − Vet. Mac", "Mac · PennyLane − Clássico · Mac", "#7C3AED", +1.5 * h),
        ("Windows · PennyLane − Vet. Linux", "Windows · PennyLane − Clássico · Linux", "#2563EB", +0.5 * h),
        ("Mac · Qiskit − Vet. Mac", "Mac · Qiskit − Clássico · Mac", "#D97706", -0.5 * h),
        ("Windows · Qiskit − Vet. Linux", "Windows · Qiskit − Clássico · Linux", "#B91C1C", -1.5 * h),
    ]

    for lbl, cmp_key, color, offset in configs_b:
        sub = df_c[df_c["comparacao"] == cmp_key].set_index("dataset")
        vals_h = [float(sub.loc[d, "diferenca_horas"]) for d in DATASET_ORDER]
        bars = ax2.barh(y + offset, vals_h, height=h * 0.92, label=lbl, color=color, alpha=0.92, zorder=3)
        for bar, val in zip(bars, vals_h):
            ax2.text(val + 0.65, bar.get_y() + bar.get_height() / 2.0,
                     f"{fmt_pt(val, 2)} h", va="center", ha="left", fontsize=8.1, color="#1E293B")

    ax2.set_xlim(0, 64)
    ax2.set_xlabel("Tempo extra: quântico − clássico vetorial (h)", fontsize=10.0)
    ax2.set_title("B. Sobrecarga da simulação quântica", fontsize=11.3, fontweight="bold", pad=10)
    ax2.grid(True, axis="x", alpha=0.8)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.50, -0.10), fontsize=8.5, frameon=True,
               facecolor="#FFFFFF", edgecolor="#CBD5E1", ncol=2)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    out_path = OUT_DIR / "fig_tempos_100_epocas_comparativo.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_fig_aceleracao():
    df_ep = pd.read_csv(CSV_EPOCAS, sep=";", decimal=",", encoding="utf-8-sig")
    df_ses = pd.read_csv(CSV_SESSOES, sep=";", decimal=",", encoding="utf-8-sig")
    meta_runs = df_ses[["codigo", "dataset", "modelo"]].drop_duplicates(subset=["codigo"])
    ep_sums = df_ep.groupby("codigo", as_index=False)["epoch_seconds"].sum()
    df_runs = ep_sums.merge(meta_runs, on="codigo", how="left")

    def _series_s(modelo_nome):
        sub = df_runs[df_runs["modelo"] == modelo_nome].set_index("dataset")["epoch_seconds"]
        return np.array([float(sub.loc[d]) for d in DATASET_ORDER], dtype=float)

    t_w_pl = _series_s("PQC Windows PennyLane")
    t_m_pl = _series_s("PQC Mac PennyLane")
    t_w_qk = _series_s("PQC Windows Qiskit")
    t_m_qk = _series_s("PQC Mac Qiskit")
    t_v_lin = _series_s("Dense20 vetorial Linux")
    t_v_mac = _series_s("Dense20 vetorial Mac")

    vals_pl_wm = list(t_w_pl / t_m_pl) + [float(t_w_pl.sum() / t_m_pl.sum())]
    vals_qk_wm = list(t_w_qk / t_m_qk) + [float(t_w_qk.sum() / t_m_qk.sum())]
    vals_win_qp = list(t_w_qk / t_w_pl) + [float(t_w_qk.sum() / t_w_pl.sum())]
    vals_mac_qp = list(t_m_qk / t_m_pl) + [float(t_m_qk.sum() / t_m_pl.sum())]

    # Verificacao cruzada contra CSV_AMB_Q e CSV_SIM_Q
    df_amb = pd.read_csv(CSV_AMB_Q, sep=";", decimal=",")
    df_sim = pd.read_csv(CSV_SIM_Q, sep=";", decimal=",")
    pl_wm_ref = df_amb[df_amb["backend"] == "pennylane"].set_index("dataset")
    qk_wm_ref = df_amb[df_amb["backend"] == "qiskit"].set_index("dataset")
    win_qp_ref = df_sim[df_sim["ambiente"] == "Windows"].set_index("dataset")
    mac_qp_ref = df_sim[df_sim["ambiente"] == "Mac"].set_index("dataset")
    max_diff = max(
        float(np.max(np.abs(np.array(vals_pl_wm[:-1]) - np.array([float(pl_wm_ref.loc[d, "razao_windows_dividido_mac"]) for d in DATASET_ORDER])))),
        float(np.max(np.abs(np.array(vals_qk_wm[:-1]) - np.array([float(qk_wm_ref.loc[d, "razao_windows_dividido_mac"]) for d in DATASET_ORDER])))),
        float(np.max(np.abs(np.array(vals_win_qp[:-1]) - np.array([float(win_qp_ref.loc[d, "razao_qiskit_dividido_pennylane"]) for d in DATASET_ORDER])))),
        float(np.max(np.abs(np.array(vals_mac_qp[:-1]) - np.array([float(mac_qp_ref.loc[d, "razao_qiskit_dividido_pennylane"]) for d in DATASET_ORDER])))),
    )
    assert max_diff < 1e-6, f"Divergencia nas razoes de aceleracao: {max_diff}"

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 7.6), dpi=300, sharey=True,
                                   gridspec_kw={"wspace": 0.14})
    fig.subplots_adjust(top=0.81, bottom=0.13)

    y = np.arange(10)[::-1]
    ds_labels = [SHORT_NAMES[d] for d in DATASET_ORDER] + ["Total (9 bases)"]
    h = 0.35

    for ax in (ax1, ax2):
        ax.axhline(0.5, color="#94A3B8", lw=1.1, zorder=1)
        ax.axhspan(-0.5, 0.5, color="#F1F5F9", zorder=0)
        ax.axvline(1.0, color="#0F172A", linestyle="--", linewidth=1.2, zorder=4)
        ax.grid(True, axis="x", alpha=0.75, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # Painel A: Ambientes
    b1 = ax1.barh(y + h / 2, vals_pl_wm, height=h * 0.88, color="#2563EB", label="PennyLane (R_Win/Mac)", zorder=3)
    b2 = ax1.barh(y - h / 2, vals_qk_wm, height=h * 0.88, color="#D97706", label="Qiskit (R_Win/Mac)", zorder=3)
    for bar, v in zip(b1, vals_pl_wm):
        ax1.text(v + 0.05, bar.get_y() + bar.get_height() / 2, f"{fmt_pt(v, 2)}×",
                 va="center", ha="left", fontsize=9.8, fontweight="bold", color="#1E40AF")
    for bar, v in zip(b2, vals_qk_wm):
        ax1.text(v + 0.05, bar.get_y() + bar.get_height() / 2, f"{fmt_pt(v, 2)}×",
                 va="center", ha="left", fontsize=9.8, fontweight="bold", color="#92400E")

    ax1.set_xlim(0, 4.70)
    ax1.set_yticks(y)
    ax1.set_yticklabels(ds_labels, fontsize=11.0, fontweight="bold")
    ax1.get_yticklabels()[-1].set_color("#0F172A")
    ax1.set_xlabel(r"Razão de duração ($R_{\mathrm{Win/Mac}} = T_{\mathrm{Win}} / T_{\mathrm{Mac}}$)", fontsize=10.8, fontweight="bold")
    ax1.set_title(r"A. Ambientes: $R_{\mathrm{Win/Mac}} = T_{\mathrm{Win}} / T_{\mathrm{Mac}}$", fontsize=12.0, fontweight="bold", pad=22)
    ax1.text(0.5, 1.015, "Valores > 1,0× indicam iMac M4 mais rápido (18/18 pares)",
             transform=ax1.transAxes, ha="center", va="bottom", fontsize=9.8, color="#1E40AF", fontweight="bold")

    r_vec_tot = float(t_v_lin.sum() / t_v_mac.sum())
    r_vec_min = float(np.min(t_v_lin / t_v_mac))
    r_vec_max = float(np.max(t_v_lin / t_v_mac))
    ax1.text(
        0.98, 0.34,
        f"Ref. clássica (Dense20 vetorial):\n"
        f"R_Lin/Mac = {fmt_pt(r_vec_tot, 2)}×\n"
        f"({fmt_pt(t_v_lin.sum(), 2)} s / {fmt_pt(t_v_mac.sum(), 2)} s)\n"
        f"Faixa: {fmt_pt(r_vec_min, 2)}× a {fmt_pt(r_vec_max, 2)}×",
        transform=ax1.transAxes, ha="right", va="center", fontsize=8.8, fontweight="bold", color="#0F766E",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#ECFDF5", edgecolor="#0F766E", lw=1.0),
        zorder=5
    )
    ax1.tick_params(axis="x", labelsize=10.0)
    ax1.legend(loc="upper center", bbox_to_anchor=(0.50, -0.11), fontsize=9.8, frameon=True, ncol=2, edgecolor="#CBD5E1")

    # Painel B: Simuladores
    b3 = ax2.barh(y + h / 2, vals_win_qp, height=h * 0.88, color="#0F766E", label="Windows (R_QK/PL)", zorder=3)
    b4 = ax2.barh(y - h / 2, vals_mac_qp, height=h * 0.88, color="#7C3AED", label="iMac M4 (R_QK/PL)", zorder=3)
    for bar, v in zip(b3, vals_win_qp):
        ax2.text(v + 0.05, bar.get_y() + bar.get_height() / 2, f"{fmt_pt(v, 2)}×",
                 va="center", ha="left", fontsize=9.8, fontweight="bold", color="#115E59")
    for bar, v in zip(b4, vals_mac_qp):
        ax2.text(v + 0.05, bar.get_y() + bar.get_height() / 2, f"{fmt_pt(v, 2)}×",
                 va="center", ha="left", fontsize=9.8, fontweight="bold", color="#5B21B6")

    ax2.set_xlim(0, 3.45)
    ax2.set_xlabel(r"Razão de duração ($R_{\mathrm{QK/PL}} = T_{\mathrm{QK}} / T_{\mathrm{PL}}$)", fontsize=10.8, fontweight="bold")
    ax2.set_title(r"B. Simuladores: $R_{\mathrm{QK/PL}} = T_{\mathrm{QK}} / T_{\mathrm{PL}}$", fontsize=12.0, fontweight="bold", pad=22)
    ax2.text(0.5, 1.015, "Valores > 1,0× indicam PennyLane mais rápido (18/18 pares)",
             transform=ax2.transAxes, ha="center", va="bottom", fontsize=9.8, color="#5B21B6", fontweight="bold")
    ax2.tick_params(axis="x", labelsize=10.0)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.50, -0.11), fontsize=9.8, frameon=True, ncol=2, edgecolor="#CBD5E1")

    fig.suptitle("Fatores de Aceleração Operacional PQC 4×5 Qubits (100 Épocas, Lote 128)",
                 fontsize=13.8, fontweight="bold", y=0.965)
    fig.text(
        0.50, 0.915,
        f"Melhor quântico (9/9 bases): PQC Mac PennyLane ({fmt_pt(t_m_pl.sum()/3600.0, 2)} h; "
        f"{fmt_pt(vals_pl_wm[-1], 2)}×–{fmt_pt(float(t_w_qk.sum()/t_m_pl.sum()), 2)}× mais rápido, Macro-F1 médio 82,17%)  |  "
        f"Melhor clássico: Dense20 vetorial Mac ({fmt_pt(t_v_mac.sum(), 2)} s)",
        ha="center", va="top", fontsize=9.8, fontweight="bold", color="#0F172A",
        bbox=dict(boxstyle="round,pad=0.30", facecolor="#F8FAFC", edgecolor="#CBD5E1", lw=0.9)
    )

    out_path = OUT_DIR / "fig_fatores_aceleracao_ambientes_simuladores.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.14, facecolor="#FFFFFF")
    plt.close(fig)
    print(f"Gerado: {out_path} (max_diff_csv={max_diff:.2e})")


def gerar_fig_custo_macro_f1():
    df = pd.read_csv(CSV_FIG26)

    fig, (ax0, ax1, ax2) = plt.subplots(
        1, 3, figsize=(15.5, 6.2), dpi=300,
        gridspec_kw={"width_ratios": [0.95, 1.0, 1.0], "wspace": 0.22}
    )

    order_cfg = [
        ("Dense20 vetorial Mac", "Vetorial Mac", "#0F766E"),
        ("Dense20 vetorial Linux", "Vetorial Linux", "#65A30D"),
        ("Dense20 imagem", "Dense20 imagem", "#D97706"),
        ("CNN FP32", "CNN origem", "#334155"),
        ("PQC Mac PennyLane", "PQC Mac PL", "#7C3AED"),
        ("PQC Windows PennyLane", "PQC Win PL", "#2563EB"),
        ("PQC Mac Qiskit", "PQC Mac QK", "#EA580C"),
        ("PQC Windows Qiskit", "PQC Win QK", "#B91C1C"),
    ]
    sums = df.groupby("model_label")["training_hours"].sum()
    y0 = np.arange(len(order_cfg))[::-1]
    vals_h = [float(sums[k]) for k, _, _ in order_cfg]
    lbls_cfg = [lbl for _, lbl, _ in order_cfg]
    cols_cfg = [c for _, _, c in order_cfg]

    bars = ax0.barh(y0, vals_h, height=0.62, color=cols_cfg, zorder=3)
    for bar, v in zip(bars, vals_h):
        txt = f"{fmt_pt(v, 2)} h" if v >= 1.0 else f"{fmt_pt(v*3600, 1)} s"
        ax0.text(v + 4.0, bar.get_y() + bar.get_height()/2, txt, va="center", ha="left", fontsize=9.0, fontweight="bold", color="#1E293B")

    ax0.set_yticks(y0)
    ax0.set_yticklabels(lbls_cfg, fontsize=9.8, fontweight="bold")
    ax0.set_xlim(0, 265)
    ax0.set_xlabel("Tempo acumulado das 9 bases (h)", fontsize=9.8)
    ax0.set_title("A. Carga horária por família", fontsize=11.0, fontweight="bold", pad=10)
    ax0.grid(True, axis="x", alpha=0.8)
    ax0.spines["top"].set_visible(False)
    ax0.spines["right"].set_visible(False)

    # Rotulos espacados sem linhas cruzadas nem colisao com marcadores
    offsets_win = {
        "GTSRB": (6.2, 103.5),
        "MNIST": (24.0, 103.5),
        "KMNIST": (37.0, 98.4),
        "SVHN": (39.5, 92.6),
        "Fashion-MNIST": (9.8, 86.2),
        "EMNIST Balanced": (42.5, 83.2),
        "CIFAR-10": (13.0, 77.2),
        "FER2013": (6.8, 53.5),
        "CIFAR-100 Coarse": (16.5, 42.6),
    }

    offsets_mac = {
        "GTSRB": (4.0, 103.5),
        "MNIST": (14.5, 103.5),
        "KMNIST": (25.5, 98.4),
        "SVHN": (27.5, 92.8),
        "Fashion-MNIST": (7.5, 85.8),
        "EMNIST Balanced": (23.0, 83.2),
        "CIFAR-10": (9.5, 77.2),
        "FER2013": (5.5, 53.5),
        "CIFAR-100 Coarse": (11.5, 42.6),
    }

    def plot_env(ax, env_label, pl_key, qk_key, c_pl, c_qk, title_str, xmax, off_map):
        pl = df[df["model_key"] == pl_key].set_index("dataset")
        qk = df[df["model_key"] == qk_key].set_index("dataset")
        for ds in DATASET_ORDER:
            x1 = float(pl.loc[ds, "training_hours"])
            y1 = float(pl.loc[ds, "macro_f1"]) * 100.0
            x2 = float(qk.loc[ds, "training_hours"])
            y2 = float(qk.loc[ds, "macro_f1"]) * 100.0
            ax.plot([x1, x2], [y1, y2], color="#94A3B8", linewidth=1.3, zorder=2)

        ax.scatter([float(pl.loc[d, "training_hours"]) for d in DATASET_ORDER],
                   [float(pl.loc[d, "macro_f1"])*100 for d in DATASET_ORDER],
                   color=c_pl, marker="o", s=68, edgecolors="#FFFFFF", linewidths=0.7, label="PennyLane", zorder=4)
        ax.scatter([float(qk.loc[d, "training_hours"]) for d in DATASET_ORDER],
                   [float(qk.loc[d, "macro_f1"])*100 for d in DATASET_ORDER],
                   color=c_qk, marker="^", s=74, edgecolors="#FFFFFF", linewidths=0.7, label="Qiskit", zorder=4)

        for ds in DATASET_ORDER:
            x1 = float(pl.loc[ds, "training_hours"])
            x2 = float(qk.loc[ds, "training_hours"])
            ym = float(pl.loc[ds, "macro_f1"]) * 100.0
            if ds in ("GTSRB", "Fashion-MNIST", "FER2013"):
                xm = x1
            elif ds in ("KMNIST", "SVHN"):
                xm = x2
            else:
                xm = 0.5 * (x1 + x2)
            tx, ty = off_map[ds]
            ax.annotate(
                SHORT_NAMES[ds], xy=(xm, ym), xytext=(tx, ty),
                ha="center", va="center", fontsize=8.2, fontweight="bold", color="#1E293B",
                bbox=dict(boxstyle="round,pad=0.18", facecolor="#FFFFFF", edgecolor="#CBD5E1", alpha=0.95),
                arrowprops=dict(arrowstyle="-", color="#64748B", lw=0.8, shrinkA=2, shrinkB=4),
                zorder=5
            )

        ax.set_xlim(0, xmax)
        ax.set_ylim(39.0, 107.0)
        ax.set_xlabel("Soma das 100 épocas (horas)", fontsize=9.8)
        ax.set_ylabel("Macro-F1 de teste (%)" if env_label == "Windows" else "", fontsize=9.8)
        ax.set_title(title_str, fontsize=11.0, fontweight="bold", pad=10)
        ax.grid(True, alpha=0.7)
        ax.legend(loc="lower right", fontsize=9.0, frameon=True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    plot_env(ax1, "Windows", "q_windows_pennylane", "q_windows_qiskit", "#2563EB", "#B91C1C",
             "B. Windows (100,4 h PL vs. 200,3 h QK)", 64.0, offsets_win)
    plot_env(ax2, "Mac", "q_mac_pennylane", "q_mac_qiskit", "#7C3AED", "#D97706",
             "C. iMac M4 (55,2 h PL vs. 147,8 h QK)", 36.0, offsets_mac)

    out_path = OUT_DIR / "fig_custo_vs_macro_f1_ambientes.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_fig_explicabilidade():
    with open(JSON_OCL, encoding="utf-8") as f:
        m = json.load(f)

    flips_by_ds = defaultdict(lambda: {"desfoque": 0, "media": 0})
    for s in m["summaries"]:
        flips_by_ds[s["dataset"]][s["method"]] += int(s["flips"])

    id_to_name = {
        "mnist": "MNIST",
        "fashion_mnist": "Fashion-MNIST",
        "kmnist": "KMNIST",
        "emnist_balanced": "EMNIST Balanced",
        "cifar10": "CIFAR-10",
        "cifar100_coarse": "CIFAR-100 Coarse",
        "svhn": "SVHN",
        "gtsrb": "GTSRB",
        "fer2013": "FER2013",
    }
    ds_ids = ["mnist", "fashion_mnist", "kmnist", "emnist_balanced", "cifar10", "cifar100_coarse", "svhn", "gtsrb", "fer2013"]

    img_gc = Image.open(IMG_GRADCAM)
    img_oc = Image.open(IMG_OCLUSAO)

    fig = plt.figure(figsize=(15.0, 12.0), dpi=300)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 0.85], hspace=0.30, wspace=0.14)

    ax_gc = fig.add_subplot(gs[0, 0])
    ax_oc = fig.add_subplot(gs[0, 1])
    ax_bar = fig.add_subplot(gs[1, :])

    ax_gc.imshow(img_gc)
    ax_gc.axis("off")
    ax_gc.set_title("A. Grad-CAM em block4_activation2 (gtsrb_01 · classe 16)", fontsize=10.5, fontweight="bold", pad=8)

    ax_oc.imshow(img_oc)
    ax_oc.axis("off")
    ax_oc.set_title("B. Oclusão 8×8 pela média (gtsrb_01 · queda de margem logit)", fontsize=10.5, fontweight="bold", pad=8)

    x = np.arange(len(ds_ids))
    w = 0.36
    vals_desf = [flips_by_ds[d]["desfoque"] for d in ds_ids]
    vals_med = [flips_by_ds[d]["media"] for d in ds_ids]

    b1 = ax_bar.bar(x - w/2, vals_desf, width=w, color="#0284C7", label="Borramento gaussiano (4.096 oclusões/base)")
    b2 = ax_bar.bar(x + w/2, vals_med, width=w, color="#DC2626", label="Preenchimento pela média da imagem (4.096 oclusões/base)")

    for bar, v in zip(b1, vals_desf):
        pct = 100.0 * v / 4096.0
        ax_bar.text(bar.get_x() + bar.get_width()/2, v + 15, f"{v}\n({fmt_pt(pct, 1)}%)",
                    ha="center", va="bottom", fontsize=7.8, fontweight="bold", color="#0369A1")
    for bar, v in zip(b2, vals_med):
        pct = 100.0 * v / 4096.0
        ax_bar.text(bar.get_x() + bar.get_width()/2, v + 15, f"{v}\n({fmt_pt(pct, 1)}%)",
                    ha="center", va="bottom", fontsize=7.8, fontweight="bold", color="#991B1B")

    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels([SHORT_NAMES[id_to_name[d]] for d in ds_ids], fontsize=10.0, fontweight="bold")
    ax_bar.set_ylim(0, 1180)
    ax_bar.set_ylabel("Trocas de classe\n(em 4.096 blocos)", fontsize=10.0)
    ax_bar.set_title(
        "C. Sensibilidade global nas 73.728 oclusões (8 amostras × 8 modelos × 64 blocos × 2 métodos) — mediana Spearman Grad-CAM vs. queda logit: ρ = 0,002",
        fontsize=10.5, fontweight="bold", pad=10
    )
    ax_bar.grid(True, axis="y", alpha=0.8)
    ax_bar.legend(loc="upper left", fontsize=9.5, frameon=True)
    ax_bar.spines["top"].set_visible(False)
    ax_bar.spines["right"].set_visible(False)

    fig.suptitle(
        "Explicabilidade Espacial Auditada: Saliência por Grad-CAM vs. Perturbação Causal por Oclusão em Blocos 8×8",
        fontsize=13.5, fontweight="bold", y=0.98
    )
    out_path = OUT_DIR / "fig_explicabilidade_gradcam_oclusao.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.14)
    plt.close(fig)
    print("Gerado:", out_path)


if __name__ == "__main__":
    gerar_fig_tempos_100_epocas()
    gerar_fig_aceleracao()
    gerar_fig_custo_macro_f1()
    print("Todas as figuras de tempos, aceleracao e custo foram geradas com sucesso!")
