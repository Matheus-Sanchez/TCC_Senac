# -*- coding: utf-8 -*-
"""Gera todas as figuras consolidadas da Seção 4.8 (Tempos, Diferenças, Fatores, Custo×F1 e Telemetria Hardware/I/O, incluindo telemetria completa do iMac M4).

Diretriz visual: mínimo texto dentro dos gráficos, tipografia ampliada e legível em escala A4,
sem caixas de rodapé extensas; explicações metodológicas detalhadas acompanham cada figura no texto LaTeX.
"""

import pathlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

OUT_DIR = pathlib.Path(r"C:\Users\matheus.sduda\repos\TCC\TCC_Senac\figuras")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ROOT_OUT = pathlib.Path(r"C:\Users\matheus.sduda\Documents\ChatGPT\projeto-do-tcc\outputs")
DIR_HW_IO = ROOT_OUT / "graficos-hardware-io-batch128-2026-11-18"
CSV_EPOCAS = DIR_HW_IO / "dados_por_epoca.csv"
CSV_SESSOES = DIR_HW_IO / "sessoes_e_fontes.csv"
CSV_TEL = DIR_HW_IO / "dados_telemetria_por_intervalo.csv"
CSV_FIG26 = ROOT_OUT / "analise-ilustrada-2026-10-27" / "dados_dos_graficos" / "figura_26_comparacao_matriz.csv"

DIR_MAC_COMP = ROOT_OUT / "telemetria-mac-completa-2026-11-19"
CSV_MAC_RESUMO = DIR_MAC_COMP / "resumo_por_dataset.csv"
CSV_MAC_PROJ = DIR_MAC_COMP / "cenario-100-epocas" / "projecao_100_epocas_por_base.csv"
CSV_MAC_TOT = DIR_MAC_COMP / "cenario-100-epocas" / "totais_100_epocas.csv"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.edgecolor": "#94A3B8",
    "axes.linewidth": 1.0,
    "grid.color": "#E2E8F0",
    "grid.linestyle": "-",
    "grid.linewidth": 0.7,
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


def carregar_dados_mac_completos():
    df_mac = pd.read_csv(CSV_MAC_RESUMO, sep=";", decimal=",", encoding="utf-8-sig")
    df_proj = pd.read_csv(CSV_MAC_PROJ, sep=";", decimal=",", encoding="utf-8-sig")
    df_tot = pd.read_csv(CSV_MAC_TOT, sep=";", decimal=",", encoding="utf-8-sig")
    return df_mac, df_proj, df_tot


def _s_by_group(df_runs, grp):
    sub = df_runs[df_runs["grupo"] == grp].set_index("dataset")["epoch_seconds"]
    return np.array([float(sub.loc[d]) for d in DATASET_ORDER], dtype=float)


def gerar_fig_48_tempos_etapas_consolidado(df_runs, df_f26):
    """Figura 4.8-1: Tempos acumulados por etapa e dispersão por dataset (texto mínimo, fontes grandes)."""
    cnn_orig = df_f26[df_f26["model_label"] == "CNN FP32"].set_index("dataset")["training_hours"] * 3600.0

    t_cnn_orig = np.array([float(cnn_orig.loc[d]) for d in DATASET_ORDER], dtype=float)
    t_cnn_b128 = _s_by_group(df_runs, "CNN batch-128 (T118–T126)")
    t_cnn_aug2 = df_runs[df_runs["grupo"] == "CNN batch-128 aug2"]["epoch_seconds"].values
    t_d20_img = _s_by_group(df_runs, "Dense20 imagem")
    t_vec_mac = _s_by_group(df_runs, "Dense20 vetorial Mac")
    t_vec_lin = _s_by_group(df_runs, "Dense20 vetorial Linux")
    t_pqc_m_pl = _s_by_group(df_runs, "PQC Mac PennyLane")
    t_pqc_w_pl = _s_by_group(df_runs, "PQC Windows PennyLane")
    t_pqc_m_qk = _s_by_group(df_runs, "PQC Mac Qiskit")
    t_pqc_w_qk = _s_by_group(df_runs, "PQC Windows Qiskit")

    bar_specs = [
        ("CNN FP32", t_cnn_orig.sum() / 3600.0, "#1E293B", False, ""),
        ("CNN b128 fp16", t_cnn_b128.sum() / 3600.0, "#475569", False, ""),
        ("CNN b128 aug2*", t_cnn_aug2.sum() / 3600.0, "#94A3B8", True, ""),
        ("Dense20 imagem", t_d20_img.sum() / 3600.0, "#EA580C", False, ""),
        ("Vetorial Mac ★", t_vec_mac.sum() / 3600.0, "#0F766E", False, f"{fmt_pt(t_vec_mac.sum(), 1)} s"),
        ("Vetorial Linux", t_vec_lin.sum() / 3600.0, "#65A30D", False, f"{fmt_pt(t_vec_lin.sum(), 1)} s"),
        ("PQC Mac PL ★", t_pqc_m_pl.sum() / 3600.0, "#7C3AED", False, ""),
        ("PQC Win PL", t_pqc_w_pl.sum() / 3600.0, "#2563EB", False, ""),
        ("PQC Mac QK", t_pqc_m_qk.sum() / 3600.0, "#D97706", False, ""),
        ("PQC Win QK", t_pqc_w_qk.sum() / 3600.0, "#B91C1C", False, ""),
    ]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(11.6, 6.4), dpi=300,
        gridspec_kw={"width_ratios": [1.0, 1.15], "wspace": 0.30}
    )

    y_a = np.arange(len(bar_specs))[::-1]
    for yi, (lbl, val_h, col, hatched, custom_txt) in zip(y_a, bar_specs):
        hatch_kw = {"hatch": "///", "edgecolor": "#334155"} if hatched else {"edgecolor": "#1E293B"}
        ax1.barh(yi, val_h, height=0.66, color=col, linewidth=0.8, alpha=0.93, zorder=3, **hatch_kw)
        txt = custom_txt if custom_txt else f"{fmt_pt(val_h, 2)} h"
        ax1.text(val_h + 4.5, yi, txt, va="center", ha="left", fontsize=11.5, fontweight="bold", color="#0F172A")

    for sep_y in (6.5, 5.5, 3.5):
        ax1.axhline(sep_y, color="#94A3B8", ls="--", lw=1.0, zorder=2)

    ax1.set_yticks(y_a)
    ax1.set_yticklabels([b[0] for b in bar_specs], fontsize=12.0, fontweight="bold")
    ax1.set_xlim(0, 275)
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 0)))
    ax1.set_xlabel("Tempo acumulado (h)", fontsize=12.5, fontweight="bold")
    ax1.set_title("A. Tempo acumulado por etapa", fontsize=14.0, fontweight="bold", pad=12)
    ax1.tick_params(axis="x", labelsize=11.5)
    ax1.grid(True, axis="x", alpha=0.75)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # Painel B: Distribuição por base (s, log)
    y_b = np.arange(len(DATASET_ORDER))[::-1]
    series_b = [
        ("Vet. Mac", t_vec_mac, "o", "#0F766E", 0.0),
        ("D20 imagem", t_d20_img, "s", "#EA580C", 0.0),
        ("CNN b128", t_cnn_b128, "D", "#475569", +0.13),
        ("CNN FP32", t_cnn_orig, "P", "#1E293B", -0.13),
        ("PQC Mac PL", t_pqc_m_pl, "^", "#7C3AED", +0.13),
        ("PQC Win QK", t_pqc_w_qk, "v", "#B91C1C", 0.0),
    ]
    for i, ds in enumerate(DATASET_ORDER):
        vals_i = [s[1][i] for s in series_b]
        x_row_max = max(vals_i)
        ax2.hlines(y_b[i], min(vals_i), x_row_max, color="#CBD5E1", lw=2.0, zorder=1)
        ax2.text(t_vec_mac[i] * 0.68, y_b[i], f"{fmt_pt(t_vec_mac[i], 1)} s",
                 ha="right", va="center", fontsize=10.5, fontweight="bold", color="#0F766E")
        x_lbl = x_row_max * 1.48
        if t_cnn_orig[i] > t_pqc_w_qk[i]:
            ax2.text(x_lbl, y_b[i] + 0.18, f"{fmt_pt(t_cnn_orig[i] / 3600.0, 2)} h",
                     ha="left", va="center", fontsize=10.2, fontweight="bold", color="#1E293B")
            ax2.text(x_lbl, y_b[i] - 0.18, f"{fmt_pt(t_pqc_w_qk[i] / 3600.0, 2)} h",
                     ha="left", va="center", fontsize=10.2, fontweight="bold", color="#991B1B")
        else:
            ax2.text(x_lbl, y_b[i], f"{fmt_pt(t_pqc_w_qk[i] / 3600.0, 2)} h",
                     ha="left", va="center", fontsize=10.5, fontweight="bold", color="#991B1B")

    for lbl, arr, mk, col, dy in series_b:
        ax2.scatter(arr, y_b + dy, label=lbl, marker=mk, s=72, color=col, edgecolors="#FFFFFF", linewidths=0.8, zorder=4)

    ax2.set_xscale("log")
    ax2.set_xlim(1.0, 1.4e6)
    ax2.set_yticks(y_b)
    ax2.set_yticklabels([SHORT_NAMES[d] for d in DATASET_ORDER], fontsize=11.8, fontweight="bold")
    ax2.set_xlabel("Duração por base (s, escala log)", fontsize=12.5, fontweight="bold")
    ax2.set_title("B. Distribuição por dataset", fontsize=14.0, fontweight="bold", pad=12)
    ax2.tick_params(axis="x", labelsize=11.5)
    ax2.grid(True, axis="x", which="major", alpha=0.75)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.48, -0.15), ncol=3, fontsize=10.8, frameon=True, edgecolor="#CBD5E1")

    out_path = OUT_DIR / "fig_48_tempos_etapas_consolidado.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.14, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_fig_48_diferencas_ambientes_simuladores(df_runs):
    """Figura 4.8-2: Diferenças pareadas 2×2 (texto mínimo, fontes grandes)."""
    t_v_mac = _s_by_group(df_runs, "Dense20 vetorial Mac")
    t_v_lin = _s_by_group(df_runs, "Dense20 vetorial Linux")
    t_m_pl = _s_by_group(df_runs, "PQC Mac PennyLane")
    t_w_pl = _s_by_group(df_runs, "PQC Windows PennyLane")
    t_m_qk = _s_by_group(df_runs, "PQC Mac Qiskit")
    t_w_qk = _s_by_group(df_runs, "PQC Windows Qiskit")

    fig, axes = plt.subplots(2, 2, figsize=(11.6, 9.2), dpi=300, sharey=True,
                             gridspec_kw={"hspace": 0.34, "wspace": 0.14})
    (ax_a, ax_b), (ax_c, ax_d) = axes
    y = np.arange(len(DATASET_ORDER))[::-1]
    ds_labels = [SHORT_NAMES[d] for d in DATASET_ORDER]

    for ax in (ax_a, ax_b, ax_c, ax_d):
        ax.axvline(0.0, color="#0F172A", lw=1.1, zorder=4)
        ax.grid(True, axis="x", alpha=0.75, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelsize=11.2)

    # Painel A: Linux - Mac (s)
    d_vec = t_v_lin - t_v_mac
    bars_a = ax_a.barh(y, d_vec, height=0.62, color="#0F766E", alpha=0.93, zorder=3)
    for bar, v in zip(bars_a, d_vec):
        ax_a.text(v + 0.6, bar.get_y() + bar.get_height() / 2, f"+{fmt_pt(v, 1)} s",
                  va="center", ha="left", fontsize=11.0, fontweight="bold", color="#115E59")
    ax_a.set_xlim(0, float(np.max(d_vec)) * 1.30)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(ds_labels, fontsize=11.8, fontweight="bold")
    ax_a.set_xlabel("Linux − Mac (s)", fontsize=12.0, fontweight="bold")
    ax_a.set_title("A. Vetorial: Linux − Mac", fontsize=13.5, fontweight="bold", pad=10)

    # Painel B: PQC Windows - Mac (h)
    d_wm_pl = (t_w_pl - t_m_pl) / 3600.0
    d_wm_qk = (t_w_qk - t_m_qk) / 3600.0
    h2 = 0.38
    b_b1 = ax_b.barh(y + h2 / 2, d_wm_pl, height=h2 * 0.84, color="#2563EB", label="PennyLane", zorder=3)
    b_b2 = ax_b.barh(y - h2 / 2, d_wm_qk, height=h2 * 0.84, color="#D97706", label="Qiskit", zorder=3)
    for bar, v in zip(b_b1, d_wm_pl):
        ax_b.text(v + 0.4, bar.get_y() + bar.get_height() / 2 + 0.03, f"+{fmt_pt(v, 1)}", va="center", ha="left", fontsize=10.2, fontweight="bold", color="#1E40AF")
    for bar, v in zip(b_b2, d_wm_qk):
        ax_b.text(v + 0.4, bar.get_y() + bar.get_height() / 2 - 0.03, f"+{fmt_pt(v, 1)}", va="center", ha="left", fontsize=10.2, fontweight="bold", color="#92400E")
    ax_b.set_xlim(0, max(float(np.max(d_wm_pl)), float(np.max(d_wm_qk))) * 1.24)
    ax_b.set_xlabel("Windows − Mac (h)", fontsize=12.0, fontweight="bold")
    ax_b.set_title("B. PQC: Windows − Mac", fontsize=13.5, fontweight="bold", pad=10)
    ax_b.legend(loc="lower right", fontsize=11.0, frameon=True, edgecolor="#CBD5E1")

    # Painel C: Qiskit - PennyLane (h)
    d_qp_win = (t_w_qk - t_w_pl) / 3600.0
    d_qp_mac = (t_m_qk - t_m_pl) / 3600.0
    b_c1 = ax_c.barh(y + h2 / 2, d_qp_win, height=h2 * 0.84, color="#0F766E", label="Windows", zorder=3)
    b_c2 = ax_c.barh(y - h2 / 2, d_qp_mac, height=h2 * 0.84, color="#7C3AED", label="iMac M4", zorder=3)
    for bar, v in zip(b_c1, d_qp_win):
        ax_c.text(v + 0.5, bar.get_y() + bar.get_height() / 2 + 0.03, f"+{fmt_pt(v, 1)}", va="center", ha="left", fontsize=10.2, fontweight="bold", color="#115E59")
    for bar, v in zip(b_c2, d_qp_mac):
        ax_c.text(v + 0.5, bar.get_y() + bar.get_height() / 2 - 0.03, f"+{fmt_pt(v, 1)}", va="center", ha="left", fontsize=10.2, fontweight="bold", color="#5B21B6")
    ax_c.set_xlim(0, max(float(np.max(d_qp_win)), float(np.max(d_qp_mac))) * 1.24)
    ax_c.set_yticks(y)
    ax_c.set_yticklabels(ds_labels, fontsize=11.8, fontweight="bold")
    ax_c.set_xlabel("Qiskit − PennyLane (h)", fontsize=12.0, fontweight="bold")
    ax_c.set_title("C. PQC: Qiskit − PennyLane", fontsize=13.5, fontweight="bold", pad=10)
    ax_c.legend(loc="lower right", fontsize=11.0, frameon=True, edgecolor="#CBD5E1")

    # Painel D: PQC - Vetorial (h)
    d_ov_mpl = (t_m_pl - t_v_mac) / 3600.0
    d_ov_wpl = (t_w_pl - t_v_lin) / 3600.0
    d_ov_mqk = (t_m_qk - t_v_mac) / 3600.0
    d_ov_wqk = (t_w_qk - t_v_lin) / 3600.0
    h4 = 0.195
    ov_specs = [
        ("Mac PL", d_ov_mpl, "#7C3AED", +1.55 * h4),
        ("Win PL", d_ov_wpl, "#2563EB", +0.52 * h4),
        ("Mac QK", d_ov_mqk, "#D97706", -0.52 * h4),
        ("Win QK", d_ov_wqk, "#B91C1C", -1.55 * h4),
    ]
    for lbl, arr, col, off in ov_specs:
        bars = ax_d.barh(y + off, arr, height=h4 * 0.84, color=col, label=lbl, zorder=3)
        for bar, v in zip(bars, arr):
            if col == "#7C3AED":
                ax_d.text(v + 0.8, bar.get_y() + bar.get_height() / 2 + 0.04, f"+{fmt_pt(v, 1)}", va="center", ha="left", fontsize=9.6, fontweight="bold", color=col)
            elif col == "#B91C1C":
                ax_d.text(v + 0.8, bar.get_y() + bar.get_height() / 2 - 0.03, f"+{fmt_pt(v, 1)}", va="center", ha="left", fontsize=9.6, fontweight="bold", color=col)
    ax_d.set_xlim(0, float(np.max(d_ov_wqk)) * 1.24)
    ax_d.set_xlabel("PQC − Vetorial (h)", fontsize=12.0, fontweight="bold")
    ax_d.set_title("D. Sobrecarga quântica", fontsize=13.5, fontweight="bold", pad=10)
    ax_d.legend(loc="lower right", fontsize=10.8, frameon=True, edgecolor="#CBD5E1")

    out_path = OUT_DIR / "fig_48_diferencas_ambientes_simuladores.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.14, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_fig_fatores_aceleracao(df_runs):
    """Figura 4.8-3 (Fig 43): Fatores de aceleração R_Win/Mac e R_QK/PL (limpa, sem caixas de texto)."""
    t_m_pl = _s_by_group(df_runs, "PQC Mac PennyLane")
    t_w_pl = _s_by_group(df_runs, "PQC Windows PennyLane")
    t_m_qk = _s_by_group(df_runs, "PQC Mac Qiskit")
    t_w_qk = _s_by_group(df_runs, "PQC Windows Qiskit")

    vals_pl_wm = list(t_w_pl / t_m_pl) + [float(t_w_pl.sum() / t_m_pl.sum())]
    vals_qk_wm = list(t_w_qk / t_m_qk) + [float(t_w_qk.sum() / t_m_qk.sum())]
    vals_win_qp = list(t_w_qk / t_w_pl) + [float(t_w_qk.sum() / t_w_pl.sum())]
    vals_mac_qp = list(t_m_qk / t_m_pl) + [float(t_m_qk.sum() / t_m_pl.sum())]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.4, 6.8), dpi=300, sharey=True,
                                   gridspec_kw={"wspace": 0.14})

    y = np.arange(10)[::-1]
    ds_labels = [SHORT_NAMES[d] for d in DATASET_ORDER] + ["Total (9 bases)"]
    h = 0.37

    for ax in (ax1, ax2):
        ax.axhline(0.5, color="#94A3B8", lw=1.2, zorder=1)
        ax.axhspan(-0.5, 0.5, color="#F1F5F9", zorder=0)
        ax.axvline(1.0, color="#0F172A", linestyle="--", linewidth=1.3, zorder=4)
        ax.grid(True, axis="x", alpha=0.75, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelsize=11.8)

    # Painel A: Ambientes
    b1 = ax1.barh(y + h / 2, vals_pl_wm, height=h * 0.88, color="#2563EB", label="PennyLane", zorder=3)
    b2 = ax1.barh(y - h / 2, vals_qk_wm, height=h * 0.88, color="#D97706", label="Qiskit", zorder=3)
    for bar, v in zip(b1, vals_pl_wm):
        ax1.text(v + 0.06, bar.get_y() + bar.get_height() / 2, f"{fmt_pt(v, 2)}×",
                 va="center", ha="left", fontsize=11.4, fontweight="bold", color="#1E40AF")
    for bar, v in zip(b2, vals_qk_wm):
        ax1.text(v + 0.06, bar.get_y() + bar.get_height() / 2, f"{fmt_pt(v, 2)}×",
                 va="center", ha="left", fontsize=11.4, fontweight="bold", color="#92400E")

    ax1.set_xlim(0, 3.95)
    ax1.set_yticks(y)
    ax1.set_yticklabels(ds_labels, fontsize=12.4, fontweight="bold")
    ax1.set_xlabel(r"$T_{\mathrm{Win}} / T_{\mathrm{Mac}}$", fontsize=13.0, fontweight="bold")
    ax1.set_title(r"A. Ambientes ($R_{\mathrm{Win/Mac}}$)", fontsize=14.5, fontweight="bold", pad=12)
    ax1.legend(loc="upper center", bbox_to_anchor=(0.50, -0.12), fontsize=12.0, frameon=True, ncol=2, edgecolor="#CBD5E1")

    # Painel B: Simuladores
    b3 = ax2.barh(y + h / 2, vals_win_qp, height=h * 0.88, color="#0F766E", label="Windows", zorder=3)
    b4 = ax2.barh(y - h / 2, vals_mac_qp, height=h * 0.88, color="#7C3AED", label="iMac M4", zorder=3)
    for bar, v in zip(b3, vals_win_qp):
        ax2.text(v + 0.06, bar.get_y() + bar.get_height() / 2, f"{fmt_pt(v, 2)}×",
                 va="center", ha="left", fontsize=11.4, fontweight="bold", color="#115E59")
    for bar, v in zip(b4, vals_mac_qp):
        ax2.text(v + 0.06, bar.get_y() + bar.get_height() / 2, f"{fmt_pt(v, 2)}×",
                 va="center", ha="left", fontsize=11.4, fontweight="bold", color="#5B21B6")

    ax2.set_xlim(0, 3.55)
    ax2.set_xlabel(r"$T_{\mathrm{QK}} / T_{\mathrm{PL}}$", fontsize=13.0, fontweight="bold")
    ax2.set_title(r"B. Simuladores ($R_{\mathrm{QK/PL}}$)", fontsize=14.5, fontweight="bold", pad=12)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.50, -0.12), fontsize=12.0, frameon=True, ncol=2, edgecolor="#CBD5E1")

    out_path = OUT_DIR / "fig_fatores_aceleracao_ambientes_simuladores.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.14, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_fig_custo_macro_f1(df_f26):
    """Figura 4.8-4: Carga horária por família e pares Tempo × Macro-F1 (fontes ampliadas)."""
    df = df_f26
    fig, (ax0, ax1, ax2) = plt.subplots(
        1, 3, figsize=(12.6, 5.4), dpi=300,
        gridspec_kw={"width_ratios": [0.92, 1.04, 1.04], "wspace": 0.24}
    )

    order_cfg = [
        ("Dense20 vetorial Mac", "Vet. Mac", "#0F766E"),
        ("Dense20 vetorial Linux", "Vet. Linux", "#65A30D"),
        ("Dense20 imagem", "D20 imagem", "#D97706"),
        ("CNN FP32", "CNN FP32", "#334155"),
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

    bars = ax0.barh(y0, vals_h, height=0.64, color=cols_cfg, zorder=3)
    for bar, v in zip(bars, vals_h):
        txt = f"{fmt_pt(v, 1)} h" if v >= 1.0 else f"{fmt_pt(v * 3600, 0)} s"
        ax0.text(v + 5.0, bar.get_y() + bar.get_height() / 2, txt,
                 va="center", ha="left", fontsize=11.0, fontweight="bold", color="#1E293B")

    ax0.set_yticks(y0)
    ax0.set_yticklabels(lbls_cfg, fontsize=11.8, fontweight="bold")
    ax0.set_xlim(0, 275)
    ax0.set_xlabel("Tempo total (h)", fontsize=12.0, fontweight="bold")
    ax0.set_title("A. Tempo total", fontsize=13.5, fontweight="bold", pad=10)
    ax0.tick_params(axis="x", labelsize=11.0)
    ax0.grid(True, axis="x", alpha=0.75)
    ax0.spines["top"].set_visible(False)
    ax0.spines["right"].set_visible(False)

    offsets_win = {
        "GTSRB": (7.5, 104.2),
        "MNIST": (25.0, 104.2),
        "KMNIST": (40.5, 98.4),
        "SVHN": (42.5, 92.6),
        "Fashion-MNIST": (12.0, 84.5),
        "EMNIST Balanced": (43.0, 82.0),
        "CIFAR-10": (15.0, 77.6),
        "FER2013": (8.5, 54.0),
        "CIFAR-100 Coarse": (18.5, 42.2),
    }

    offsets_mac = {
        "GTSRB": (4.5, 104.2),
        "MNIST": (15.5, 104.2),
        "KMNIST": (26.5, 98.4),
        "SVHN": (28.5, 92.8),
        "Fashion-MNIST": (9.2, 84.5),
        "EMNIST Balanced": (23.5, 82.0),
        "CIFAR-10": (10.5, 77.6),
        "FER2013": (6.2, 54.0),
        "CIFAR-100 Coarse": (9.2, 41.8),
    }

    def plot_env(ax, env_label, pl_key, qk_key, c_pl, c_qk, title_str, xmax, off_map):
        pl = df[df["model_key"] == pl_key].set_index("dataset")
        qk = df[df["model_key"] == qk_key].set_index("dataset")
        for ds in DATASET_ORDER:
            x1 = float(pl.loc[ds, "training_hours"])
            y1 = float(pl.loc[ds, "macro_f1"]) * 100.0
            x2 = float(qk.loc[ds, "training_hours"])
            y2 = float(qk.loc[ds, "macro_f1"]) * 100.0
            ax.plot([x1, x2], [y1, y2], color="#94A3B8", linewidth=1.5, zorder=2)

        ax.scatter([float(pl.loc[d, "training_hours"]) for d in DATASET_ORDER],
                   [float(pl.loc[d, "macro_f1"]) * 100 for d in DATASET_ORDER],
                   color=c_pl, marker="o", s=78, edgecolors="#FFFFFF", linewidths=0.8, label="PennyLane", zorder=4)
        ax.scatter([float(qk.loc[d, "training_hours"]) for d in DATASET_ORDER],
                   [float(qk.loc[d, "macro_f1"]) * 100 for d in DATASET_ORDER],
                   color=c_qk, marker="^", s=84, edgecolors="#FFFFFF", linewidths=0.8, label="Qiskit", zorder=4)

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
                ha="center", va="center", fontsize=9.2, fontweight="bold", color="#1E293B",
                bbox=dict(boxstyle="round,pad=0.18", facecolor="#FFFFFF", edgecolor="#CBD5E1", alpha=0.95),
                arrowprops=dict(arrowstyle="-", color="#64748B", lw=0.85, shrinkA=2, shrinkB=4),
                zorder=5
            )

        ax.set_xlim(0, xmax)
        ax.set_ylim(38.5, 108.0)
        ax.set_xlabel("Tempo (h)", fontsize=12.0, fontweight="bold")
        ax.set_ylabel("Macro-F1 (%)" if env_label == "Windows" else "", fontsize=12.0, fontweight="bold")
        ax.set_title(title_str, fontsize=13.5, fontweight="bold", pad=10)
        ax.tick_params(labelsize=11.0)
        ax.grid(True, alpha=0.7)
        ax.legend(loc="lower right", fontsize=10.4, frameon=True, edgecolor="#CBD5E1")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    plot_env(ax1, "Windows", "q_windows_pennylane", "q_windows_qiskit", "#2563EB", "#B91C1C",
             "B. Windows", 64.0, offsets_win)
    plot_env(ax2, "Mac", "q_mac_pennylane", "q_mac_qiskit", "#7C3AED", "#D97706",
             "C. iMac M4", 36.5, offsets_mac)

    out_path = OUT_DIR / "fig_custo_vs_macro_f1_ambientes.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.14, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_fig_48_telemetria_hardware_io(df_runs, df_ses, df_tel):
    """Figura 4.8-5: Telemetria histórica de 100 épocas nas 8 configurações (texto mínimo, fontes grandes)."""
    df_tel = df_tel.copy()
    df_tel["cpu_eff"] = df_tel["cpu_tree"].fillna(df_tel["cpu_process"])
    df_tel["rss_eff"] = df_tel["rss_tree_mib_max"].fillna(df_tel["rss_process_mib_max"])

    run_meta = df_ses.drop_duplicates(subset=["codigo"])[["codigo", "dataset", "ambiente", "grupo"]]
    tel_m = df_tel.merge(run_meta, on="codigo", how="left")

    groups_order = [
        ("Dense20 vetorial Mac", "Vet. Mac", "Mac", "#0F766E"),
        ("Dense20 vetorial Linux", "Vet. Linux", "Linux", "#65A30D"),
        ("Dense20 imagem", "D20 imagem", "Linux", "#EA580C"),
        ("CNN batch-128 (T118–T126)", "CNN b128 fp16", "Linux", "#475569"),
        ("PQC Mac PennyLane", "PQC Mac PL", "Mac", "#7C3AED"),
        ("PQC Mac Qiskit", "PQC Mac QK", "Mac", "#D97706"),
        ("PQC Windows PennyLane", "PQC Win PL", "Windows", "#2563EB"),
        ("PQC Windows Qiskit", "PQC Win QK", "Windows", "#B91C1C"),
    ]

    stats = []
    for grp_key, lbl, amb, col in groups_order:
        sub_t = tel_m[tel_m["grupo"] == grp_key]
        sub_s = df_ses[df_ses["grupo"] == grp_key]

        c_valid = sub_t.dropna(subset=["cpu_eff", "samples"])
        cpu_mean = float((c_valid["cpu_eff"] * c_valid["samples"]).sum() / c_valid["samples"].sum())

        per_run_rss = sub_t.groupby("codigo")["rss_eff"].max() / 1024.0
        rss_mean = float(per_run_rss.mean())
        rss_abs_max = float(per_run_rss.max())

        if amb == "Mac":
            gpu_mean = None
            read_gib = None
            write_gib = None
        else:
            g_valid = sub_t.dropna(subset=["gpu_util", "samples"])
            gpu_mean = float((g_valid["gpu_util"] * g_valid["samples"]).sum() / g_valid["samples"].sum())
            read_gib = float(sub_s["leitura_mib"].fillna(0.0).sum() / 1024.0)
            write_gib = float(sub_s["escrita_mib"].fillna(0.0).sum() / 1024.0)

        stats.append({
            "key": grp_key, "label": lbl, "amb": amb, "color": col,
            "cpu_mean": cpu_mean,
            "rss_mean": rss_mean, "rss_max": rss_abs_max,
            "gpu_mean": gpu_mean,
            "read_gib": read_gib, "write_gib": write_gib,
        })

    fig, axes = plt.subplots(2, 2, figsize=(11.6, 8.0), dpi=300, sharey=True,
                             gridspec_kw={"hspace": 0.34, "wspace": 0.14})
    (ax_a, ax_b), (ax_c, ax_d) = axes
    y = np.arange(len(stats))[::-1]
    y_labels = [s["label"] for s in stats]

    for ax in (ax_a, ax_b, ax_c, ax_d):
        ax.axhline(3.5, color="#94A3B8", ls="--", lw=1.0, zorder=1)
        ax.grid(True, axis="x", alpha=0.75, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelsize=11.4)

    # Painel A: CPU (%)
    cpu_vals = [s["cpu_mean"] for s in stats]
    cols = [s["color"] for s in stats]
    bars_a = ax_a.barh(y, cpu_vals, height=0.62, color=cols, alpha=0.93, zorder=3)
    for bar, s in zip(bars_a, stats):
        ax_a.text(s["cpu_mean"] + 8.0, bar.get_y() + bar.get_height() / 2,
                  f"{fmt_pt(s['cpu_mean'], 1)}%", va="center", ha="left",
                  fontsize=11.4, fontweight="bold", color="#0F172A")
    ax_a.set_xlim(0, 490)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(y_labels, fontsize=12.0, fontweight="bold")
    ax_a.set_xlabel("CPU da árvore (%)", fontsize=12.0, fontweight="bold")
    ax_a.set_title("A. Uso médio de CPU", fontsize=13.8, fontweight="bold", pad=10)

    # Painel B: RSS (GiB)
    rss_means = [s["rss_mean"] for s in stats]
    rss_maxs = [s["rss_max"] for s in stats]
    bars_b = ax_b.barh(y, rss_means, height=0.60, color=cols, alpha=0.88, zorder=3, label="Média dos picos")
    ax_b.scatter(rss_maxs, y, marker="D", s=68, color="#0F172A", edgecolors="#FFFFFF", linewidths=0.8, zorder=5, label="Máx. absoluto")
    for bar, s in zip(bars_b, stats):
        ax_b.text(s["rss_max"] + 0.22, bar.get_y() + bar.get_height() / 2,
                  f"{fmt_pt(s['rss_mean'], 2)} / {fmt_pt(s['rss_max'], 2)}",
                  va="center", ha="left", fontsize=11.0, fontweight="bold", color="#0F172A")
    ax_b.set_xlim(0, 11.4)
    ax_b.set_xlabel("RSS: média / máx. (GiB)", fontsize=12.0, fontweight="bold")
    ax_b.set_title("B. Pico de memória (RSS)", fontsize=13.8, fontweight="bold", pad=10)
    ax_b.legend(loc="lower right", fontsize=10.8, frameon=True, edgecolor="#CBD5E1")

    # Painel C: GPU RTX A2000 (%)
    for yi, s in zip(y, stats):
        if s["gpu_mean"] is None:
            ax_c.barh(yi, 48.0, height=0.60, color="#E2E8F0", edgecolor="#94A3B8", hatch="///", alpha=0.75, zorder=2)
            ax_c.text(24.0, yi, "N/D*", va="center", ha="center",
                      fontsize=11.5, fontweight="bold", color="#475569",
                      bbox=dict(boxstyle="round,pad=0.16", facecolor="#FFFFFF", edgecolor="none", alpha=0.88), zorder=4)
        else:
            ax_c.barh(yi, s["gpu_mean"], height=0.60, color=s["color"], alpha=0.93, zorder=3)
            ax_c.text(s["gpu_mean"] + 1.2, yi, f"{fmt_pt(s['gpu_mean'], 1)}%",
                      va="center", ha="left", fontsize=11.4, fontweight="bold", color="#0F172A")
    ax_c.set_xlim(0, 58)
    ax_c.set_yticks(y)
    ax_c.set_yticklabels(y_labels, fontsize=12.0, fontweight="bold")
    ax_c.set_xlabel("Utilização média (%)", fontsize=12.0, fontweight="bold")
    ax_c.set_title("C. GPU RTX A2000", fontsize=13.8, fontweight="bold", pad=10)

    # Painel D: Volume de I/O acumulado (GiB)
    h_io = 0.36
    for yi, s in zip(y, stats):
        if s["read_gib"] is None:
            ax_d.barh(yi, 228.0, height=0.60, color="#E2E8F0", edgecolor="#94A3B8", hatch="///", alpha=0.75, zorder=2)
            ax_d.text(114.0, yi, "N/D*", va="center", ha="center",
                      fontsize=11.5, fontweight="bold", color="#475569",
                      bbox=dict(boxstyle="round,pad=0.16", facecolor="#FFFFFF", edgecolor="none", alpha=0.88), zorder=4)
        else:
            r_v, w_v = s["read_gib"], s["write_gib"]
            lbl_r = "Leitura" if s["key"] == "PQC Windows Qiskit" else None
            lbl_w = "Escrita" if s["key"] == "PQC Windows Qiskit" else None
            ax_d.barh(yi + h_io / 2, r_v, height=h_io * 0.88, color="#0284C7", label=lbl_r, zorder=3)
            ax_d.barh(yi - h_io / 2, w_v, height=h_io * 0.88, color="#F97316", label=lbl_w, zorder=3)
            if r_v >= 1.0 or w_v >= 1.0:
                ax_d.text(r_v + 4.5, yi + h_io / 2, f"{fmt_pt(r_v, 1)}", va="center", ha="left",
                          fontsize=10.6, fontweight="bold", color="#0369A1")
                ax_d.text(w_v + 4.5, yi - h_io / 2, f"{fmt_pt(w_v, 1)}" if w_v >= 0.1 else "0,02", va="center", ha="left",
                          fontsize=10.6, fontweight="bold", color="#C2410C")
            else:
                ax_d.text(max(r_v, w_v) + 4.5, yi, f"{fmt_pt(r_v, 2)} / {fmt_pt(w_v, 2)}", va="center", ha="left",
                          fontsize=10.4, fontweight="bold", color="#334155")
    ax_d.set_xlim(0, 290)
    ax_d.set_xlabel("I/O acumulado (GiB)", fontsize=12.0, fontweight="bold")
    ax_d.set_title("D. Disco (processo principal)", fontsize=13.8, fontweight="bold", pad=10)
    ax_d.legend(loc="center right", bbox_to_anchor=(0.99, 0.72), fontsize=11.0, frameon=True, edgecolor="#CBD5E1")

    out_path = OUT_DIR / "fig_48_telemetria_hardware_io.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.14, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_fig_48_mac_hardware_io_complementar(df_mac):
    """Figura 4.8-6 (NOVA): Telemetria observada complementar no iMac M4 (27 sessões de 1 época)."""
    fams = [
        ("classico", "Clássico", "#0F766E"),
        ("pennylane", "PennyLane", "#7C3AED"),
        ("qiskit", "Qiskit", "#D97706"),
    ]

    cpu_w, rss_mean, rss_max, gpu_w, io_r, io_w = [], [], [], [], [], []
    for fk, _, _ in fams:
        sub = df_mac[df_mac["familia"] == fk]
        w = sub["n_treino"].values
        cpu_w.append(float((sub["cpu_arvore_media_pct"] * w).sum() / w.sum()))
        rss_mean.append(float(sub["rss_arvore_pico_sessao_gib"].mean()))
        rss_max.append(float(sub["rss_arvore_pico_sessao_gib"].max()))
        gpu_w.append(float((sub["gpu_agx_media_pct"] * w).sum() / w.sum()))
        io_r.append(float(sub["io_principal_leitura_sessao_mib"].sum()))
        io_w.append(float(sub["io_principal_escrita_sessao_mib"].sum()))

    labels = [f[1] for f in fams]
    colors = [f[2] for f in fams]
    x = np.arange(len(fams))

    fig, axes = plt.subplots(2, 2, figsize=(11.0, 7.2), dpi=300,
                             gridspec_kw={"hspace": 0.36, "wspace": 0.24})
    (ax_a, ax_b), (ax_c, ax_d) = axes

    for ax in (ax_a, ax_b, ax_c, ax_d):
        ax.grid(True, axis="y", alpha=0.75, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=12.4, fontweight="bold")
        ax.tick_params(axis="y", labelsize=11.6)

    # A. CPU média ponderada (%)
    bars_a = ax_a.bar(x, cpu_w, width=0.54, color=colors, edgecolor="#1E293B", linewidth=0.8, alpha=0.93, zorder=3)
    for bar, v in zip(bars_a, cpu_w):
        ax_a.text(bar.get_x() + bar.get_width() / 2, v + 12, f"{fmt_pt(v, 1)}%",
                  ha="center", va="bottom", fontsize=12.2, fontweight="bold", color="#0F172A")
    ax_a.set_ylim(0, 470)
    ax_a.set_ylabel("CPU da árvore (%)", fontsize=12.2, fontweight="bold")
    ax_a.set_title("A. Uso médio de CPU", fontsize=14.0, fontweight="bold", pad=10)

    # B. Pico de RSS (GiB)
    bars_b = ax_b.bar(x, rss_mean, width=0.54, color=colors, edgecolor="#1E293B", linewidth=0.8, alpha=0.88, zorder=3, label="Média")
    ax_b.scatter(x, rss_max, marker="D", s=80, color="#0F172A", edgecolors="#FFFFFF", linewidths=0.9, zorder=5, label="Máx.")
    for bar, m_v, mx_v in zip(bars_b, rss_mean, rss_max):
        ax_b.text(bar.get_x() + bar.get_width() / 2, mx_v + 0.12, f"{fmt_pt(m_v, 2)} / {fmt_pt(mx_v, 2)}",
                  ha="center", va="bottom", fontsize=11.6, fontweight="bold", color="#0F172A")
    ax_b.set_ylim(0, 3.45)
    ax_b.set_ylabel("RSS (GiB)", fontsize=12.2, fontweight="bold")
    ax_b.set_title("B. Pico de memória (RSS)", fontsize=14.0, fontweight="bold", pad=10)
    ax_b.legend(loc="upper center", ncol=2, fontsize=11.2, frameon=True, edgecolor="#CBD5E1")

    # C. GPU Apple AGX média global (%)
    bars_c = ax_c.bar(x, gpu_w, width=0.54, color=colors, edgecolor="#1E293B", linewidth=0.8, alpha=0.93, zorder=3)
    for bar, v in zip(bars_c, gpu_w):
        ax_c.text(bar.get_x() + bar.get_width() / 2, v + 0.14, f"{fmt_pt(v, 2)}%",
                  ha="center", va="bottom", fontsize=12.2, fontweight="bold", color="#0F172A")
    ax_c.set_ylim(0, 5.0)
    ax_c.set_ylabel("GPU AGX global (%)", fontsize=12.2, fontweight="bold")
    ax_c.set_title("C. GPU Apple AGX", fontsize=14.0, fontweight="bold", pad=10)

    # D. I/O principal acumulado nas 9 sessões (1 época, MiB)
    w_bar = 0.34
    b_r = ax_d.bar(x - w_bar / 2, io_r, width=w_bar, color="#0284C7", edgecolor="#1E293B", linewidth=0.7, label="Leitura", zorder=3)
    b_w = ax_d.bar(x + w_bar / 2, io_w, width=w_bar, color="#F97316", edgecolor="#1E293B", linewidth=0.7, label="Escrita", zorder=3)
    for bar, v in zip(b_r, io_r):
        txt = f"{fmt_pt(v, 2)}" if v < 1.0 else f"{fmt_pt(v, 1)}"
        ax_d.text(bar.get_x() + bar.get_width() / 2, v + 2.5, txt,
                  ha="center", va="bottom", fontsize=11.4, fontweight="bold", color="#0369A1")
    for bar, v in zip(b_w, io_w):
        ax_d.text(bar.get_x() + bar.get_width() / 2, v + 2.5, f"{fmt_pt(v, 1)}",
                  ha="center", va="bottom", fontsize=11.4, fontweight="bold", color="#C2410C")
    ax_d.set_ylim(0, 108)
    ax_d.set_ylabel("I/O em 9 sessões (MiB)", fontsize=12.2, fontweight="bold")
    ax_d.set_title("D. Disco (processo principal)", fontsize=14.0, fontweight="bold", pad=10)
    ax_d.legend(loc="upper left", fontsize=11.2, frameon=True, edgecolor="#CBD5E1")

    out_path = OUT_DIR / "fig_48_mac_hardware_io_complementar.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.14, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_fig_48_mac_hardware_sensores_macmon(df_mac, df_proj):
    """Figura 4.8-7 (NOVA): Sensores macmon (1 época) e energia projetada (100 épocas) no iMac M4."""
    pl_m = df_mac[df_mac["familia"] == "pennylane"].set_index("nome")
    qk_m = df_mac[df_mac["familia"] == "qiskit"].set_index("nome")
    cl_m = df_mac[(df_mac["familia"] == "classico") & (df_mac["n_macmon_treino"] > 0)]
    turbo_ghz = float(cl_m["pcpu_freq_mhz_medio"].mean() / 1000.0)

    pl_p = df_proj[df_proj["familia"] == "pennylane"].set_index("nome")
    qk_p = df_proj[df_proj["familia"] == "qiskit"].set_index("nome")

    p_pl = np.array([float(pl_m.loc[d, "cpu_power_medio"]) for d in DATASET_ORDER])
    p_qk = np.array([float(qk_m.loc[d, "cpu_power_medio"]) for d in DATASET_ORDER])
    t_pl = np.array([float(pl_m.loc[d, "cpu_temp_media_c"]) for d in DATASET_ORDER])
    t_qk = np.array([float(qk_m.loc[d, "cpu_temp_media_c"]) for d in DATASET_ORDER])
    f_pl = np.array([float(pl_m.loc[d, "pcpu_freq_mhz_medio"]) / 1000.0 for d in DATASET_ORDER])
    f_qk = np.array([float(qk_m.loc[d, "pcpu_freq_mhz_medio"]) / 1000.0 for d in DATASET_ORDER])
    e_pl = np.array([float(pl_p.loc[d, "energia_cpu_global_100_treinos_wh"]) for d in DATASET_ORDER])
    e_qk = np.array([float(qk_p.loc[d, "energia_cpu_global_100_treinos_wh"]) for d in DATASET_ORDER])

    fig, axes = plt.subplots(2, 2, figsize=(11.6, 9.4), dpi=300, sharey=True,
                             gridspec_kw={"hspace": 0.34, "wspace": 0.14})
    (ax_a, ax_b), (ax_c, ax_d) = axes
    y = np.arange(len(DATASET_ORDER))[::-1]
    ds_labels = [SHORT_NAMES[d] for d in DATASET_ORDER]
    h = 0.39

    for ax in (ax_a, ax_b, ax_c, ax_d):
        ax.grid(True, axis="x", alpha=0.75, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelsize=11.4)

    # A. Potência CPU (W)
    b1 = ax_a.barh(y + h / 2, p_pl, height=h * 0.84, color="#7C3AED", label="PennyLane", zorder=3)
    b2 = ax_a.barh(y - h / 2, p_qk, height=h * 0.84, color="#D97706", label="Qiskit", zorder=3)
    for bar, v in zip(b1, p_pl):
        ax_a.text(v + 0.35, bar.get_y() + bar.get_height() / 2 + 0.03, f"{fmt_pt(v, 1)}", va="center", ha="left", fontsize=10.0, fontweight="bold", color="#5B21B6")
    for bar, v in zip(b2, p_qk):
        ax_a.text(v + 0.35, bar.get_y() + bar.get_height() / 2 - 0.03, f"{fmt_pt(v, 1)}", va="center", ha="left", fontsize=10.0, fontweight="bold", color="#92400E")
    ax_a.set_xlim(0, 22.0)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(ds_labels, fontsize=11.8, fontweight="bold")
    ax_a.set_xlabel("Potência da CPU (W)", fontsize=12.0, fontweight="bold")
    ax_a.set_title("A. Potência média da CPU", fontsize=13.8, fontweight="bold", pad=10)

    # B. Temperatura CPU (°C)
    b3 = ax_b.barh(y + h / 2, t_pl, height=h * 0.84, color="#7C3AED", zorder=3)
    b4 = ax_b.barh(y - h / 2, t_qk, height=h * 0.84, color="#D97706", zorder=3)
    for bar, v in zip(b3, t_pl):
        ax_b.text(v + 1.4, bar.get_y() + bar.get_height() / 2 + 0.03, f"{fmt_pt(v, 1)}", va="center", ha="left", fontsize=10.0, fontweight="bold", color="#5B21B6")
    for bar, v in zip(b4, t_qk):
        ax_b.text(v + 1.4, bar.get_y() + bar.get_height() / 2 - 0.03, f"{fmt_pt(v, 1)}", va="center", ha="left", fontsize=10.0, fontweight="bold", color="#92400E")
    ax_b.set_xlim(0, 108)
    ax_b.set_xlabel("Temperatura da CPU (°C)", fontsize=12.0, fontweight="bold")
    ax_b.set_title("B. Temperatura média da CPU", fontsize=13.8, fontweight="bold", pad=10)

    # C. Frequência núcleos P (GHz)
    b5 = ax_c.barh(y + h / 2, f_pl, height=h * 0.84, color="#7C3AED", zorder=3)
    b6 = ax_c.barh(y - h / 2, f_qk, height=h * 0.84, color="#D97706", zorder=3)
    ax_c.axvline(turbo_ghz, color="#0F766E", ls="--", lw=1.4, zorder=4)
    ax_c.text(turbo_ghz + 0.06, 8.35, f"{fmt_pt(turbo_ghz, 2)} GHz", va="center", ha="left",
              fontsize=10.2, fontweight="bold", color="#0F766E")
    for bar, v in zip(b5, f_pl):
        ax_c.text(v + 0.08, bar.get_y() + bar.get_height() / 2 + 0.03, f"{fmt_pt(v, 2)}", va="center", ha="left", fontsize=10.0, fontweight="bold", color="#5B21B6")
    for bar, v in zip(b6, f_qk):
        ax_c.text(v + 0.08, bar.get_y() + bar.get_height() / 2 - 0.03, f"{fmt_pt(v, 2)}", va="center", ha="left", fontsize=10.0, fontweight="bold", color="#92400E")
    ax_c.set_xlim(0, 5.45)
    ax_c.set_yticks(y)
    ax_c.set_yticklabels(ds_labels, fontsize=11.8, fontweight="bold")
    ax_c.set_xlabel("Frequência P-cores (GHz)", fontsize=12.0, fontweight="bold")
    ax_c.set_title("C. Frequência dos núcleos P", fontsize=13.8, fontweight="bold", pad=10)

    # D. Energia global da CPU — projeção condicional de 100 épocas (Wh, barras hachuradas)
    b7 = ax_d.barh(y + h / 2, e_pl, height=h * 0.84, color="#7C3AED", edgecolor="#FFFFFF", hatch="///", alpha=0.90, zorder=3)
    b8 = ax_d.barh(y - h / 2, e_qk, height=h * 0.84, color="#D97706", edgecolor="#FFFFFF", hatch="///", alpha=0.90, zorder=3)
    for bar, v in zip(b7, e_pl):
        ax_d.text(v + 8.0, bar.get_y() + bar.get_height() / 2 + 0.03, f"{fmt_pt(v, 0)}", va="center", ha="left", fontsize=10.2, fontweight="bold", color="#5B21B6")
    for bar, v in zip(b8, e_qk):
        ax_d.text(v + 8.0, bar.get_y() + bar.get_height() / 2 - 0.03, f"{fmt_pt(v, 0)}", va="center", ha="left", fontsize=10.2, fontweight="bold", color="#92400E")
    ax_d.set_xlim(0, 580)
    ax_d.set_xlabel("Energia estimada (Wh)*", fontsize=12.0, fontweight="bold")
    ax_d.set_title("D. Energia CPU — proj. 100 épocas*", fontsize=13.8, fontweight="bold", pad=10)

    # Legenda única limpa bem acima dos títulos
    handles, leg_labels = ax_a.get_legend_handles_labels()
    fig.legend(handles, leg_labels, loc="upper center", bbox_to_anchor=(0.52, 0.985),
               ncol=2, fontsize=12.4, frameon=True, edgecolor="#CBD5E1")
    fig.subplots_adjust(top=0.89)

    out_path = OUT_DIR / "fig_48_mac_hardware_sensores_macmon.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.14, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path)


if __name__ == "__main__":
    df_runs, df_ses, df_tel, df_f26 = carregar_dados_consolidados()
    df_mac, df_proj, df_tot = carregar_dados_mac_completos()

    gerar_fig_48_tempos_etapas_consolidado(df_runs, df_f26)
    gerar_fig_48_diferencas_ambientes_simuladores(df_runs)
    gerar_fig_fatores_aceleracao(df_runs)
    gerar_fig_custo_macro_f1(df_f26)
    gerar_fig_48_telemetria_hardware_io(df_runs, df_ses, df_tel)
    gerar_fig_48_mac_hardware_io_complementar(df_mac)
    gerar_fig_48_mac_hardware_sensores_macmon(df_mac, df_proj)
    print("Todas as 7 figuras da Seção 4.8 foram geradas com sucesso!")
