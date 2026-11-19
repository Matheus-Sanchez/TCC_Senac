# -*- coding: utf-8 -*-
"""Gera as 3 figuras consolidadas da Seção 4.8 (Custo Computacional, Tempos e Telemetria Hardware/I/O)."""

import pathlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import FuncFormatter

OUT_DIR = pathlib.Path(r"C:\Users\matheus.sduda\repos\TCC\TCC_Senac\figuras")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ROOT_OUT = pathlib.Path(r"C:\Users\matheus.sduda\Documents\ChatGPT\projeto-do-tcc\outputs")
DIR_HW_IO = ROOT_OUT / "graficos-hardware-io-batch128-2026-11-18"
CSV_EPOCAS = DIR_HW_IO / "dados_por_epoca.csv"
CSV_SESSOES = DIR_HW_IO / "sessoes_e_fontes.csv"
CSV_TEL = DIR_HW_IO / "dados_telemetria_por_intervalo.csv"
CSV_FIG26 = ROOT_OUT / "analise-ilustrada-2026-10-27" / "dados_dos_graficos" / "figura_26_comparacao_matriz.csv"

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


def carregar_dados_consolidados():
    df_ep = pd.read_csv(CSV_EPOCAS, sep=";", decimal=",", encoding="utf-8-sig")
    df_ses = pd.read_csv(CSV_SESSOES, sep=";", decimal=",", encoding="utf-8-sig")
    df_tel = pd.read_csv(CSV_TEL, sep=";", decimal=",", encoding="utf-8-sig")
    df_f26 = pd.read_csv(CSV_FIG26)

    # Classificar grupo metodologico por codigo (distingue T118-T126 fp16 de T142-T144 aug2)
    def classify_group(row):
        cod = str(row["codigo"])
        mod = str(row["modelo"])
        src = str(row["fonte_telemetria"])
        if mod == "CNN batch · batch-128":
            if "controlled-augmentation2" in src or cod in ("T142", "T143", "T144"):
                return "CNN batch-128 aug2"
            return "CNN batch-128 (T118–T126)"
        return mod

    df_ses["grupo"] = df_ses.apply(classify_group, axis=1)
    run_meta = df_ses.drop_duplicates(subset=["codigo"])[["codigo", "dataset", "modelo", "ambiente", "backend", "grupo"]]
    ep_sums = df_ep.groupby("codigo", as_index=False)["epoch_seconds"].sum()
    df_runs = ep_sums.merge(run_meta, on="codigo", how="left")
    return df_runs, df_ses, df_tel, df_f26


def gerar_fig_48_tempos_etapas_consolidado(df_runs, df_f26):
    """Figura 4.8-A: Consolidacao de tempos por etapa (anexos #1, #4, #6)."""
    cnn_orig = df_f26[df_f26["model_label"] == "CNN FP32"].set_index("dataset")["training_hours"] * 3600.0

    def _s_by_group(grp):
        sub = df_runs[df_runs["grupo"] == grp].set_index("dataset")["epoch_seconds"]
        return np.array([float(sub.loc[d]) for d in DATASET_ORDER], dtype=float)

    t_cnn_orig = np.array([float(cnn_orig.loc[d]) for d in DATASET_ORDER], dtype=float)
    t_cnn_b128 = _s_by_group("CNN batch-128 (T118–T126)")
    t_cnn_aug2 = df_runs[df_runs["grupo"] == "CNN batch-128 aug2"]["epoch_seconds"].values
    t_d20_img = _s_by_group("Dense20 imagem")
    t_vec_mac = _s_by_group("Dense20 vetorial Mac")
    t_vec_lin = _s_by_group("Dense20 vetorial Linux")
    t_pqc_m_pl = _s_by_group("PQC Mac PennyLane")
    t_pqc_w_pl = _s_by_group("PQC Windows PennyLane")
    t_pqc_m_qk = _s_by_group("PQC Mac Qiskit")
    t_pqc_w_qk = _s_by_group("PQC Windows Qiskit")

    # Extras MNIST (T094, T095, T096, T155)
    extras = df_runs[df_runs["codigo"].isin(["T094", "T095", "T096", "T155"])].set_index("codigo")["epoch_seconds"] / 3600.0

    # Ordem top-to-bottom para Painel A (y=9 no topo ate y=0 na base)
    bar_specs = [
        ("CNN origem FP32 (9 bases, lotes orig.)", t_cnn_orig.sum() / 3600.0, "#1E293B", False, ""),
        ("CNN batch-128 fp16 (T118–T126, 9 bases)", t_cnn_b128.sum() / 3600.0, "#475569", False, ""),
        ("CNN batch-128 aug2 (T142–T144, 3 bases*)", t_cnn_aug2.sum() / 3600.0, "#94A3B8", True, ""),
        ("Dense20 imagem (Linux, 9 bases)", t_d20_img.sum() / 3600.0, "#EA580C", False, ""),
        ("Dense20 vetorial Mac (9 bases) ★", t_vec_mac.sum() / 3600.0, "#0F766E", False, f"{fmt_pt(t_vec_mac.sum(), 2)} s (0,05 h) — 1.019× menor que PQC Mac PL"),
        ("Dense20 vetorial Linux (9 bases)", t_vec_lin.sum() / 3600.0, "#65A30D", False, f"{fmt_pt(t_vec_lin.sum(), 2)} s (0,10 h)"),
        ("PQC Mac · PennyLane (9 bases) ★", t_pqc_m_pl.sum() / 3600.0, "#7C3AED", False, ""),
        ("PQC Windows · PennyLane (9 bases)", t_pqc_w_pl.sum() / 3600.0, "#2563EB", False, ""),
        ("PQC Mac · Qiskit (9 bases)", t_pqc_m_qk.sum() / 3600.0, "#D97706", False, ""),
        ("PQC Windows · Qiskit (9 bases)", t_pqc_w_qk.sum() / 3600.0, "#B91C1C", False, ""),
    ]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(13.6, 8.0), dpi=300,
        gridspec_kw={"width_ratios": [1.08, 1.12], "wspace": 0.22}
    )
    fig.subplots_adjust(bottom=0.22, top=0.90)

    y_a = np.arange(len(bar_specs))[::-1]
    for yi, (lbl, val_h, col, hatched, custom_txt) in zip(y_a, bar_specs):
        hatch_kw = {"hatch": "///", "edgecolor": "#334155"} if hatched else {"edgecolor": "#1E293B"}
        ax1.barh(yi, val_h, height=0.64, color=col, linewidth=0.7, alpha=0.92, zorder=3, **hatch_kw)
        txt = custom_txt if custom_txt else f"{fmt_pt(val_h, 2)} h"
        ax1.text(val_h + 3.5, yi, txt, va="center", ha="left", fontsize=9.4, fontweight="bold", color="#0F172A")

    # Separadores entre etapas (entre idx 2-3, 3-4, 5-6) -> y = 6.5, 5.5, 3.5
    for sep_y in (6.5, 5.5, 3.5):
        ax1.axhline(sep_y, color="#94A3B8", ls="--", lw=1.0, zorder=2)

    ax1.set_yticks(y_a)
    ax1.set_yticklabels([b[0] for b in bar_specs], fontsize=9.8, fontweight="bold")
    ax1.set_xlim(0, 265)
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 0)))
    ax1.set_xlabel("Tempo acumulado de treino (horas)", fontsize=10.5, fontweight="bold")
    ax1.set_title("A. Tempo acumulado por etapa e configuração", fontsize=11.5, fontweight="bold", pad=10)
    ax1.tick_params(axis="x", labelsize=9.8)
    ax1.grid(True, axis="x", alpha=0.75)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # Painel B: Distribuicao por dataset e etapa (s, log)
    y_b = np.arange(len(DATASET_ORDER))[::-1]
    series_b = [
        ("Dense20 vetorial Mac", t_vec_mac, "o", "#0F766E", 0.0),
        ("Dense20 imagem", t_d20_img, "s", "#EA580C", 0.0),
        ("CNN batch-128 fp16", t_cnn_b128, "D", "#475569", +0.13),
        ("CNN origem FP32", t_cnn_orig, "P", "#1E293B", -0.13),
        ("PQC Mac PennyLane ★", t_pqc_m_pl, "^", "#7C3AED", +0.13),
        ("PQC Windows Qiskit", t_pqc_w_qk, "v", "#B91C1C", 0.0),
    ]
    for i, ds in enumerate(DATASET_ORDER):
        vals_i = [s[1][i] for s in series_b]
        x_row_max = max(vals_i)
        ax2.hlines(y_b[i], min(vals_i), x_row_max, color="#CBD5E1", lw=1.8, zorder=1)
        ax2.text(t_vec_mac[i] * 0.72, y_b[i], f"{fmt_pt(t_vec_mac[i], 1)} s",
                 ha="right", va="center", fontsize=8.8, fontweight="bold", color="#0F766E")
        x_lbl = x_row_max * 1.42
        if t_cnn_orig[i] > t_pqc_w_qk[i]:
            ax2.text(x_lbl, y_b[i] + 0.16, f"{fmt_pt(t_cnn_orig[i] / 3600.0, 2)} h (CNN FP32)",
                     ha="left", va="center", fontsize=8.4, fontweight="bold", color="#1E293B")
            ax2.text(x_lbl, y_b[i] - 0.16, f"{fmt_pt(t_pqc_w_qk[i] / 3600.0, 2)} h (PQC Win QK)",
                     ha="left", va="center", fontsize=8.4, fontweight="bold", color="#991B1B")
        else:
            ax2.text(x_lbl, y_b[i], f"{fmt_pt(t_pqc_w_qk[i] / 3600.0, 2)} h",
                     ha="left", va="center", fontsize=8.8, fontweight="bold", color="#991B1B")

    for lbl, arr, mk, col, dy in series_b:
        ax2.scatter(arr, y_b + dy, label=lbl, marker=mk, s=56, color=col, edgecolors="#FFFFFF", linewidths=0.7, zorder=4)

    ax2.set_xscale("log")
    ax2.set_xlim(1.2, 1.1e6)
    ax2.set_yticks(y_b)
    ax2.set_yticklabels([SHORT_NAMES[d] for d in DATASET_ORDER], fontsize=10.2, fontweight="bold")
    ax2.set_xlabel("Duração das 100 épocas por base em segundos (escala log)", fontsize=10.5, fontweight="bold")
    ax2.set_title("B. Distribuição das 100 épocas por dataset e etapa", fontsize=11.5, fontweight="bold", pad=10)
    ax2.tick_params(axis="x", labelsize=9.8)
    ax2.grid(True, axis="x", which="major", alpha=0.75)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.48, -0.11), ncol=2, fontsize=9.2, frameon=True, edgecolor="#CBD5E1")

    fig.text(
        0.50, 0.015,
        f"*T142–T144 aug2 cobre 3 bases (Fashion-MNIST 5,26 h; KMNIST 5,62 h; MNIST 5,43 h). "
        f"Ablações individuais em MNIST:\nT094 relu ({fmt_pt(float(extras['T094']), 2)} h), "
        f"T095 sigmoid ({fmt_pt(float(extras['T095']), 2)} h), T096 softmax ({fmt_pt(float(extras['T096']), 2)} h), "
        f"T155 fp16 ({fmt_pt(float(extras['T155']), 2)} h). T120/T123 com sessões retomadas consolidadas em 100 épocas.",
        ha="center", va="bottom", fontsize=9.0, color="#475569", linespacing=1.32,
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#F8FAFC", edgecolor="#CBD5E1", lw=0.8)
    )

    out_path = OUT_DIR / "fig_48_tempos_etapas_consolidado.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.14, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_fig_48_diferencas_ambientes_simuladores(df_runs):
    """Figura 4.8-B: Diferencas pareadas (anexos #2, #3, #5) em grade 2x2."""
    def _s_by_group(grp):
        sub = df_runs[df_runs["grupo"] == grp].set_index("dataset")["epoch_seconds"]
        return np.array([float(sub.loc[d]) for d in DATASET_ORDER], dtype=float)

    t_v_mac = _s_by_group("Dense20 vetorial Mac")
    t_v_lin = _s_by_group("Dense20 vetorial Linux")
    t_m_pl = _s_by_group("PQC Mac PennyLane")
    t_w_pl = _s_by_group("PQC Windows PennyLane")
    t_m_qk = _s_by_group("PQC Mac Qiskit")
    t_w_qk = _s_by_group("PQC Windows Qiskit")

    fig, axes = plt.subplots(2, 2, figsize=(13.2, 9.4), dpi=300, sharey=True,
                             gridspec_kw={"hspace": 0.36, "wspace": 0.14})
    (ax_a, ax_b), (ax_c, ax_d) = axes
    y = np.arange(len(DATASET_ORDER))[::-1]
    ds_labels = [SHORT_NAMES[d] for d in DATASET_ORDER]

    for ax in (ax_a, ax_b, ax_c, ax_d):
        ax.axvline(0.0, color="#0F172A", lw=1.1, zorder=4)
        ax.grid(True, axis="x", alpha=0.75, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelsize=9.6)

    # Painel A: Clássico vetorial Linux - Mac (s)
    d_vec = t_v_lin - t_v_mac
    bars_a = ax_a.barh(y, d_vec, height=0.60, color="#0F766E", alpha=0.92, zorder=3)
    for bar, v in zip(bars_a, d_vec):
        ax_a.text(v + 0.6, bar.get_y() + bar.get_height() / 2, f"+{fmt_pt(v, 2)} s",
                  va="center", ha="left", fontsize=9.2, fontweight="bold", color="#115E59")
    ax_a.set_xlim(0, float(np.max(d_vec)) * 1.28)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(ds_labels, fontsize=10.2, fontweight="bold")
    ax_a.set_xlabel("Diferença de duração: Linux − Mac (s)", fontsize=10.0, fontweight="bold")
    ax_a.set_title("A. Clássico vetorial: Linux − Mac (s)", fontsize=11.4, fontweight="bold", pad=10)
    ax_a.text(
        0.97, 0.06,
        f"Total (9 bases): +{fmt_pt(d_vec.sum(), 2)} s ({fmt_pt(t_v_lin.sum() / t_v_mac.sum(), 2)}×)",
        transform=ax_a.transAxes, ha="right", va="bottom", fontsize=9.2, fontweight="bold", color="#0F766E",
        bbox=dict(boxstyle="round,pad=0.28", facecolor="#ECFDF5", edgecolor="#0F766E", lw=0.9)
    )

    # Painel B: Hibridos PQC Windows - Mac (h)
    d_wm_pl = (t_w_pl - t_m_pl) / 3600.0
    d_wm_qk = (t_w_qk - t_m_qk) / 3600.0
    h2 = 0.36
    b_b1 = ax_b.barh(y + h2 / 2, d_wm_pl, height=h2 * 0.88, color="#2563EB", label=f"PennyLane (Total: +{fmt_pt(d_wm_pl.sum(), 2)} h)", zorder=3)
    b_b2 = ax_b.barh(y - h2 / 2, d_wm_qk, height=h2 * 0.88, color="#D97706", label=f"Qiskit (Total: +{fmt_pt(d_wm_qk.sum(), 2)} h)", zorder=3)
    for bar, v in zip(b_b1, d_wm_pl):
        ax_b.text(v + 0.35, bar.get_y() + bar.get_height() / 2, f"+{fmt_pt(v, 2)} h", va="center", ha="left", fontsize=8.8, fontweight="bold", color="#1E40AF")
    for bar, v in zip(b_b2, d_wm_qk):
        ax_b.text(v + 0.35, bar.get_y() + bar.get_height() / 2, f"+{fmt_pt(v, 2)} h", va="center", ha="left", fontsize=8.8, fontweight="bold", color="#92400E")
    ax_b.set_xlim(0, max(float(np.max(d_wm_pl)), float(np.max(d_wm_qk))) * 1.26)
    ax_b.set_xlabel("Diferença de duração: Windows − Mac (h)", fontsize=10.0, fontweight="bold")
    ax_b.set_title("B. Híbridos PQC: Windows − Mac (h)", fontsize=11.4, fontweight="bold", pad=10)
    ax_b.legend(loc="lower right", fontsize=8.8, frameon=True, edgecolor="#CBD5E1")

    # Painel C: Simuladores PQC Qiskit - PennyLane (h)
    d_qp_win = (t_w_qk - t_w_pl) / 3600.0
    d_qp_mac = (t_m_qk - t_m_pl) / 3600.0
    b_c1 = ax_c.barh(y + h2 / 2, d_qp_win, height=h2 * 0.88, color="#0F766E", label=f"Windows (Total: +{fmt_pt(d_qp_win.sum(), 2)} h)", zorder=3)
    b_c2 = ax_c.barh(y - h2 / 2, d_qp_mac, height=h2 * 0.88, color="#7C3AED", label=f"iMac M4 (Total: +{fmt_pt(d_qp_mac.sum(), 2)} h)", zorder=3)
    for bar, v in zip(b_c1, d_qp_win):
        ax_c.text(v + 0.45, bar.get_y() + bar.get_height() / 2, f"+{fmt_pt(v, 2)} h", va="center", ha="left", fontsize=8.8, fontweight="bold", color="#115E59")
    for bar, v in zip(b_c2, d_qp_mac):
        ax_c.text(v + 0.45, bar.get_y() + bar.get_height() / 2, f"+{fmt_pt(v, 2)} h", va="center", ha="left", fontsize=8.8, fontweight="bold", color="#5B21B6")
    ax_c.set_xlim(0, max(float(np.max(d_qp_win)), float(np.max(d_qp_mac))) * 1.25)
    ax_c.set_yticks(y)
    ax_c.set_yticklabels(ds_labels, fontsize=10.2, fontweight="bold")
    ax_c.set_xlabel("Diferença de duração: Qiskit − PennyLane (h)", fontsize=10.0, fontweight="bold")
    ax_c.set_title("C. Simuladores PQC: Qiskit − PennyLane (h)", fontsize=11.4, fontweight="bold", pad=10)
    ax_c.legend(loc="lower right", fontsize=8.8, frameon=True, edgecolor="#CBD5E1")

    # Painel D: Sobrecarga quantica PQC - Dense20 vetorial (h)
    d_ov_mpl = (t_m_pl - t_v_mac) / 3600.0
    d_ov_wpl = (t_w_pl - t_v_lin) / 3600.0
    d_ov_mqk = (t_m_qk - t_v_mac) / 3600.0
    d_ov_wqk = (t_w_qk - t_v_lin) / 3600.0
    h4 = 0.195
    ov_specs = [
        (f"Mac PL − Vec Mac (+{fmt_pt(d_ov_mpl.sum(), 2)} h)", d_ov_mpl, "#7C3AED", +1.5 * h4),
        (f"Win PL − Vec Lin (+{fmt_pt(d_ov_wpl.sum(), 2)} h)", d_ov_wpl, "#2563EB", +0.5 * h4),
        (f"Mac QK − Vec Mac (+{fmt_pt(d_ov_mqk.sum(), 2)} h)", d_ov_mqk, "#D97706", -0.5 * h4),
        (f"Win QK − Vec Lin (+{fmt_pt(d_ov_wqk.sum(), 2)} h)", d_ov_wqk, "#B91C1C", -1.5 * h4),
    ]
    for lbl, arr, col, off in ov_specs:
        bars = ax_d.barh(y + off, arr, height=h4 * 0.90, color=col, label=lbl, zorder=3)
        for bar, v in zip(bars, arr):
            if col in ("#7C3AED", "#B91C1C"):
                ax_d.text(v + 0.6, bar.get_y() + bar.get_height() / 2, f"+{fmt_pt(v, 2)}", va="center", ha="left", fontsize=7.8, fontweight="bold", color=col)
    ax_d.set_xlim(0, float(np.max(d_ov_wqk)) * 1.25)
    ax_d.set_xlabel("Sobrecarga quântica: PQC − Dense20 vetorial (h)", fontsize=10.0, fontweight="bold")
    ax_d.set_title("D. Sobrecarga quântica: PQC − Dense20 vetorial (h)", fontsize=11.4, fontweight="bold", pad=10)
    ax_d.legend(loc="lower right", fontsize=8.3, frameon=True, edgecolor="#CBD5E1")

    out_path = OUT_DIR / "fig_48_diferencas_ambientes_simuladores.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.14, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_fig_48_telemetria_hardware_io(df_runs, df_ses, df_tel):
    """Figura 4.8-C: Telemetria cruzada de hardware (CPU, RSS, GPU/VRAM) e I/O."""
    df_tel = df_tel.copy()
    df_tel["cpu_eff"] = df_tel["cpu_tree"].fillna(df_tel["cpu_process"])
    df_tel["rss_eff"] = df_tel["rss_tree_mib_max"].fillna(df_tel["rss_process_mib_max"])

    run_meta = df_ses.drop_duplicates(subset=["codigo"])[["codigo", "dataset", "ambiente", "grupo"]]
    tel_m = df_tel.merge(run_meta, on="codigo", how="left")

    groups_order = [
        ("Dense20 vetorial Mac", "Dense20 vetorial (Mac)", "Mac", "#0F766E"),
        ("Dense20 vetorial Linux", "Dense20 vetorial (Linux)", "Linux", "#65A30D"),
        ("Dense20 imagem", "Dense20 imagem (Linux)", "Linux", "#EA580C"),
        ("CNN batch-128 (T118–T126)", "CNN batch-128 fp16 (Linux)", "Linux", "#475569"),
        ("PQC Mac PennyLane", "PQC Mac · PennyLane", "Mac", "#7C3AED"),
        ("PQC Mac Qiskit", "PQC Mac · Qiskit", "Mac", "#D97706"),
        ("PQC Windows PennyLane", "PQC Win · PennyLane", "Windows", "#2563EB"),
        ("PQC Windows Qiskit", "PQC Win · Qiskit", "Windows", "#B91C1C"),
    ]

    stats = []
    for grp_key, lbl, amb, col in groups_order:
        sub_t = tel_m[tel_m["grupo"] == grp_key]
        sub_s = df_ses[df_ses["grupo"] == grp_key]

        # CPU ponderada por amostras
        c_valid = sub_t.dropna(subset=["cpu_eff", "samples"])
        cpu_mean = float((c_valid["cpu_eff"] * c_valid["samples"]).sum() / c_valid["samples"].sum())

        # Filhos max
        ch_max = sub_t["child_processes"].max()
        ch_int = int(ch_max) if pd.notna(ch_max) else 0

        # RSS pico medio e max por run (GiB)
        per_run_rss = sub_t.groupby("codigo")["rss_eff"].max() / 1024.0
        rss_mean = float(per_run_rss.mean())
        rss_abs_max = float(per_run_rss.max())

        # GPU util ponderada e VRAM max
        if amb == "Mac":
            gpu_mean = None
            vram_max = None
            read_gib = None
            write_gib = None
        else:
            g_valid = sub_t.dropna(subset=["gpu_util", "samples"])
            gpu_mean = float((g_valid["gpu_util"] * g_valid["samples"]).sum() / g_valid["samples"].sum())
            vram_max = float(sub_t["gpu_memory_mib_max"].max())
            read_gib = float(sub_s["leitura_mib"].fillna(0.0).sum() / 1024.0)
            write_gib = float(sub_s["escrita_mib"].fillna(0.0).sum() / 1024.0)

        stats.append({
            "key": grp_key, "label": lbl, "amb": amb, "color": col,
            "cpu_mean": cpu_mean, "child_max": ch_int,
            "rss_mean": rss_mean, "rss_max": rss_abs_max,
            "gpu_mean": gpu_mean, "vram_max": vram_max,
            "read_gib": read_gib, "write_gib": write_gib,
        })

    fig, axes = plt.subplots(2, 2, figsize=(13.8, 8.8), dpi=300, sharey=True,
                             gridspec_kw={"hspace": 0.36, "wspace": 0.16})
    fig.subplots_adjust(bottom=0.14, top=0.92)
    (ax_a, ax_b), (ax_c, ax_d) = axes
    y = np.arange(len(stats))[::-1]
    y_labels = [s["label"] for s in stats]

    for ax in (ax_a, ax_b, ax_c, ax_d):
        ax.axhline(3.5, color="#94A3B8", ls="--", lw=1.0, zorder=1)
        ax.grid(True, axis="x", alpha=0.75, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelsize=9.6)

    # Painel A: CPU efetiva media ponderada (%)
    cpu_vals = [s["cpu_mean"] for s in stats]
    cols = [s["color"] for s in stats]
    bars_a = ax_a.barh(y, cpu_vals, height=0.60, color=cols, alpha=0.92, zorder=3)
    for bar, s in zip(bars_a, stats):
        suffix = f" ({s['child_max']} filhos)" if s["child_max"] > 0 else ""
        ax_a.text(s["cpu_mean"] + 8.0, bar.get_y() + bar.get_height() / 2,
                  f"{fmt_pt(s['cpu_mean'], 1)}%{suffix}", va="center", ha="left",
                  fontsize=8.8, fontweight="bold", color="#0F172A")
    ax_a.set_xlim(0, 565)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(y_labels, fontsize=10.0, fontweight="bold")
    ax_a.set_xlabel("CPU efetiva média ponderada (% por núcleo)", fontsize=9.8, fontweight="bold")
    ax_a.set_title("A. Uso médio de CPU (% por núcleo, pond. amostras)", fontsize=11.0, fontweight="bold", pad=10)

    # Painel B: Memoria residente maxima RSS (GiB)
    rss_means = [s["rss_mean"] for s in stats]
    rss_maxs = [s["rss_max"] for s in stats]
    bars_b = ax_b.barh(y, rss_means, height=0.58, color=cols, alpha=0.88, zorder=3, label="Média dos picos (9 bases)")
    ax_b.scatter(rss_maxs, y, marker="D", s=54, color="#0F172A", edgecolors="#FFFFFF", linewidths=0.7, zorder=5, label="Máximo absoluto (1 base)")
    for bar, s in zip(bars_b, stats):
        ax_b.text(s["rss_max"] + 0.18, bar.get_y() + bar.get_height() / 2,
                  f"{fmt_pt(s['rss_mean'], 2)} [máx {fmt_pt(s['rss_max'], 2)}] GiB",
                  va="center", ha="left", fontsize=8.8, fontweight="bold", color="#0F172A")
    ax_b.set_xlim(0, 12.2)
    ax_b.set_xlabel("RSS máximo por execução (GiB)", fontsize=9.8, fontweight="bold")
    ax_b.set_title("B. Memória residente máxima — RSS (GiB)", fontsize=11.0, fontweight="bold", pad=10)
    ax_b.legend(loc="lower right", fontsize=8.6, frameon=True, edgecolor="#CBD5E1")

    # Painel C: GPU RTX A2000 util (%) e pico VRAM
    for yi, s in zip(y, stats):
        if s["gpu_mean"] is None:
            ax_c.barh(yi, 60.0, height=0.58, color="#E2E8F0", edgecolor="#94A3B8", hatch="///", alpha=0.75, zorder=2)
            ax_c.text(30.0, yi, "N/D (sem telemetria GPU no macOS)", va="center", ha="center",
                      fontsize=8.3, fontweight="bold", color="#475569",
                      bbox=dict(boxstyle="round,pad=0.16", facecolor="#FFFFFF", edgecolor="none", alpha=0.85), zorder=4)
        else:
            ax_c.barh(yi, s["gpu_mean"], height=0.58, color=s["color"], alpha=0.92, zorder=3)
            vram_txt = f"{fmt_pt(s['vram_max'], 0).replace(',', '')}"
            # Formato milhar com ponto em portugues
            vram_pt = f"{int(round(s['vram_max'])):,}".replace(",", ".")
            extra = " (ociosa*)" if "PQC" in s["label"] or "vetorial" in s["label"] else ""
            ax_c.text(s["gpu_mean"] + 1.2, yi, f"{fmt_pt(s['gpu_mean'], 1)}%{extra} | {vram_pt} MiB",
                      va="center", ha="left", fontsize=8.6, fontweight="bold", color="#0F172A")
    ax_c.set_xlim(0, 82)
    ax_c.set_yticks(y)
    ax_c.set_yticklabels(y_labels, fontsize=10.0, fontweight="bold")
    ax_c.set_xlabel("Utilização média do dispositivo GPU (%)", fontsize=9.8, fontweight="bold")
    ax_c.set_title("C. GPU RTX A2000: utilização média (%) e pico VRAM", fontsize=11.0, fontweight="bold", pad=10)

    # Painel D: Volume acumulado de I/O (GiB)
    h_io = 0.34
    for yi, s in zip(y, stats):
        if s["read_gib"] is None:
            ax_d.barh(yi, 230.0, height=0.58, color="#E2E8F0", edgecolor="#94A3B8", hatch="///", alpha=0.75, zorder=2)
            ax_d.text(115.0, yi, "N/D (sem contadores I/O no macOS)", va="center", ha="center",
                      fontsize=8.3, fontweight="bold", color="#475569",
                      bbox=dict(boxstyle="round,pad=0.16", facecolor="#FFFFFF", edgecolor="none", alpha=0.85), zorder=4)
        else:
            r_v, w_v = s["read_gib"], s["write_gib"]
            lbl_r = "Leitura acumulada (GiB)" if s["key"] == "PQC Windows Qiskit" else None
            lbl_w = "Escrita acumulada (GiB)" if s["key"] == "PQC Windows Qiskit" else None
            ax_d.barh(yi + h_io / 2, r_v, height=h_io * 0.88, color="#0284C7", label=lbl_r, zorder=3)
            ax_d.barh(yi - h_io / 2, w_v, height=h_io * 0.88, color="#F97316", label=lbl_w, zorder=3)
            star = "**" if "CNN" in s["key"] else ""
            txt_io = f"L: {fmt_pt(r_v, 2)}{star} | E: {fmt_pt(w_v, 2)} GiB"
            ax_d.text(max(r_v, w_v) + 4.5, yi, txt_io, va="center", ha="left",
                      fontsize=8.6, fontweight="bold", color="#0F172A")
    ax_d.set_xlim(0, 340)
    ax_d.set_xlabel("Volume acumulado no processo principal (GiB)", fontsize=9.8, fontweight="bold")
    ax_d.set_title("D. Volume acumulado de I/O do processo principal (GiB)", fontsize=11.0, fontweight="bold", pad=10)
    ax_d.legend(loc="center right", bbox_to_anchor=(0.99, 0.68), fontsize=8.8, frameon=True, edgecolor="#CBD5E1")

    fig.text(
        0.50, 0.015,
        "Ressalvas de telemetria (LEIA_PRIMEIRO.txt): macOS sem contadores GPU/I/O (27 sessões marcadas N/D ≠ 0). "
        "*GPU em Windows/Linux mede o dispositivo inteiro\n(mediana PQC Windows: 0,55% PL e 0,58% QK, simulação em CPU). "
        "**CNN b128: 38,99 de 39,12 GiB lidos em GTSRB T123 (2 sessões). "
        "8 extras: CPU 96–192%, RSS 2,90–5,47 GiB.",
        ha="center", va="bottom", fontsize=8.8, color="#475569", linespacing=1.32,
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#F8FAFC", edgecolor="#CBD5E1", lw=0.8)
    )

    out_path = OUT_DIR / "fig_48_telemetria_hardware_io.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.14, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path)


if __name__ == "__main__":
    df_runs, df_ses, df_tel, df_f26 = carregar_dados_consolidados()
    gerar_fig_48_tempos_etapas_consolidado(df_runs, df_f26)
    gerar_fig_48_diferencas_ambientes_simuladores(df_runs)
    gerar_fig_48_telemetria_hardware_io(df_runs, df_ses, df_tel)
    print("Todas as figuras consolidadas da Seção 4.8 foram geradas com sucesso!")
