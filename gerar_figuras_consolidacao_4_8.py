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
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

OUT_DIR = pathlib.Path(r"C:\Users\matheus.sduda\repos\TCC\TCC_Senac\figuras")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ROOT_OUT = pathlib.Path(r"C:\Users\matheus.sduda\Documents\ChatGPT\projeto-do-tcc\outputs")
DIR_HW_IO = ROOT_OUT / "graficos-hardware-io-batch128-2026-11-18"
CSV_EPOCAS = DIR_HW_IO / "dados_por_epoca.csv"
CSV_SESSOES = DIR_HW_IO / "sessoes_e_fontes.csv"
CSV_TEL = DIR_HW_IO / "dados_telemetria_por_intervalo.csv"
CSV_FIG26 = ROOT_OUT / "analise-ilustrada-2026-10-27" / "dados_dos_graficos" / "figura_26_comparacao_matriz.csv"
CSV_72_BEST = ROOT_OUT / "analise-estagnacao-2026-11-06" / "resultados-72-modelos.csv"

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


def carregar_dados_melhor_epoca(df_f26):
    """Lê os 72 históricos auditados e consolida tempos até best.keras, 100 épocas e patience=15."""
    df_72 = pd.read_csv(CSV_72_BEST)
    merged = df_72.merge(
        df_f26[["dataset", "model_key", "accuracy", "macro_f1", "training_hours", "session_hours", "best_epoch"]],
        on=["dataset", "model_key"],
        how="left",
    )
    rows = []
    histories = {}
    for _, r in merged.iterrows():
        h = pd.read_csv(r["fonte_historico"])
        be = int(r["melhor_epoca"])
        p15_stop = int(r["simulacao_patience15_epoca_parada"])
        cum_s = h["epoch_seconds"].cumsum().to_numpy(dtype=float)
        tot_s = float(cum_s[-1])
        best_s = float(cum_s[be - 1])
        p15_s = float(cum_s[p15_stop - 1])
        assert abs(tot_s / 3600.0 - float(r["training_hours"])) < 1e-6, (
            f"Divergência em {r['dataset']} / {r['model_key']}: {tot_s/3600} vs {r['training_hours']}"
        )
        histories[(r["dataset"], r["model_key"])] = {
            "cum_s": cum_s,
            "val_f1_pct": h["val_macro_f1"].to_numpy(dtype=float) * 100.0,
            "val_acc_pct": h["val_accuracy"].to_numpy(dtype=float) * 100.0,
            "best_ep": be,
            "p15_stop": p15_stop,
        }
        rows.append({
            "dataset": r["dataset"],
            "etapa": int(r["etapa"]),
            "modelo": r["modelo"],
            "model_key": r["model_key"],
            "melhor_epoca": be,
            "sem_recorde": int(r["epocas_apos_melhor_sem_novo_recorde"]),
            "plato_epocas": int(r["acuracia_treino_faixa_final_epocas"]),
            "plato_valido": bool(r["acuracia_treino_plato_final_10ep"]),
            "antes_plato": str(r["melhor_checkpoint_antes_do_plato_final"]) == "True",
            "tot_s": tot_s,
            "best_s": best_s,
            "p15_s": p15_s,
            "tot_h": tot_s / 3600.0,
            "best_h": best_s / 3600.0,
            "p15_h": p15_s / 3600.0,
            "session_h": float(r["session_hours"]),
            "p15_stop": p15_stop,
            "p15_f1_lost_pp": float(r["simulacao_patience15_f1_perdido_pp"]),
            "test_f1_pct": float(r["macro_f1"]) * 100.0,
            "test_acc_pct": float(r["accuracy"]) * 100.0,
            "val_f1_best_pct": float(r["macro_f1_validacao_melhor"]) * 100.0,
            "val_f1_final_pct": float(r["macro_f1_validacao_final"]) * 100.0,
        })
    return pd.DataFrame(rows), histories


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


def gerar_fig_48_tempo_100ep_vs_melhor_epoca(df_be):
    """Figura 4.8-4 (NOVA): Tempo acumulado até best.keras vs. 100 épocas e mapa da melhor época (72 modelos)."""
    order_stages = [
        ("cnn", "CNN FP32", "#1E293B"),
        ("image20", "Dense20 imagem", "#EA580C"),
        ("vector_linux", "Vet. Linux", "#65A30D"),
        ("vector_mac", "Vet. Mac", "#0F766E"),
        ("q_mac_pennylane", "PQC Mac PL", "#7C3AED"),
        ("q_windows_pennylane", "PQC Win PL", "#2563EB"),
        ("q_mac_qiskit", "PQC Mac QK", "#D97706"),
        ("q_windows_qiskit", "PQC Win QK", "#B91C1C"),
    ]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(12.6, 6.4), dpi=300,
        gridspec_kw={"width_ratios": [1.08, 1.15], "wspace": 0.28}
    )

    # Painel A: Barras empilhadas (até best.keras vs pós-melhor até 100 ép.) + marcador patience=15
    y_a = np.arange(len(order_stages))[::-1]
    for yi, (mk, lbl, col) in zip(y_a, order_stages):
        sub = df_be[df_be["model_key"] == mk]
        best_s = float(sub["best_s"].sum())
        tot_s = float(sub["tot_s"].sum())
        best_h = best_s / 3600.0
        tot_h = tot_s / 3600.0
        p15_h = float(sub["p15_s"].sum()) / 3600.0
        saved_pct = (1.0 - best_s / tot_s) * 100.0

        ax1.barh(yi, best_h, height=0.62, color=col, edgecolor="#1E293B", linewidth=0.8, alpha=0.94, zorder=3)
        ax1.barh(yi, tot_h - best_h, left=best_h, height=0.62, color="#E2E8F0",
                 edgecolor=col, hatch="///", linewidth=0.8, alpha=0.90, zorder=3)
        ax1.scatter([p15_h], [yi], marker="D", s=62, color="#0F172A",
                    edgecolors="#FFFFFF", linewidths=0.9, zorder=5)

        if mk in ("vector_linux", "vector_mac"):
            txt = f"{fmt_pt(best_s, 1)} / {fmt_pt(tot_s, 1)} s (−{fmt_pt(saved_pct, 0)}%)"
        else:
            txt = f"{fmt_pt(best_h, 1)} / {fmt_pt(tot_h, 1)} h (−{fmt_pt(saved_pct, 0)}%)"
        ax1.text(tot_h + 4.5, yi, txt, va="center", ha="left", fontsize=10.6, fontweight="bold", color="#0F172A")

    ax1.axhline(3.5, color="#94A3B8", ls="--", lw=1.0, zorder=2)
    ax1.set_yticks(y_a)
    ax1.set_yticklabels([s[1] for s in order_stages], fontsize=11.8, fontweight="bold")
    ax1.set_xlim(0, 315)
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 0)))
    ax1.set_xlabel("Tempo acumulado nas 9 bases (h)", fontsize=12.0, fontweight="bold")
    ax1.set_title("A. Tempo: best.keras vs. 100 épocas", fontsize=13.5, fontweight="bold", pad=12)
    ax1.tick_params(axis="x", labelsize=11.0)
    ax1.grid(True, axis="x", alpha=0.75)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    leg_a = [
        Patch(facecolor="#475569", edgecolor="#1E293B", label="Até best.keras"),
        Patch(facecolor="#E2E8F0", edgecolor="#475569", hatch="///", label="Pós-melhor época (até 100)"),
        Line2D([0], [0], marker="D", color="w", markerfacecolor="#0F172A", markeredgecolor="#FFFFFF",
               markersize=8, label="Simulação patience=15"),
    ]
    ax1.legend(handles=leg_a, loc="upper center", bbox_to_anchor=(0.48, -0.14),
               ncol=2, fontsize=10.0, frameon=True, edgecolor="#CBD5E1")

    # Painel B: Mapa de calor da melhor época (9 bases × 8 etapas)
    heat_cols = [
        ("cnn", "CNN"),
        ("image20", "D20 img"),
        ("vector_linux", "Vet Lin"),
        ("vector_mac", "Vet Mac"),
        ("q_windows_pennylane", "Win PL"),
        ("q_windows_qiskit", "Win QK"),
        ("q_mac_pennylane", "Mac PL"),
        ("q_mac_qiskit", "Mac QK"),
    ]
    mat = np.zeros((len(DATASET_ORDER), len(heat_cols)), dtype=float)
    annots = [["" for _ in heat_cols] for _ in DATASET_ORDER]
    lookup = df_be.set_index(["dataset", "model_key"])

    for i, ds in enumerate(DATASET_ORDER):
        for j, (mk, _) in enumerate(heat_cols):
            row = lookup.loc[(ds, mk)]
            ep = int(row["melhor_epoca"])
            mat[i, j] = ep
            annots[i][j] = f"{ep}†" if bool(row["antes_plato"]) else f"{ep}"

    im = ax2.imshow(mat, cmap="YlGnBu", vmin=1, vmax=100, aspect="auto")
    for i in range(len(DATASET_ORDER)):
        for j in range(len(heat_cols)):
            val = mat[i, j]
            txt_col = "#FFFFFF" if val >= 55 else "#0F172A"
            ax2.text(j, i, annots[i][j], ha="center", va="center",
                     fontsize=10.4, fontweight="bold", color=txt_col)

    ax2.set_xticks(np.arange(len(heat_cols)))
    ax2.set_xticklabels([c[1] for c in heat_cols], fontsize=10.8, fontweight="bold", rotation=32, ha="right")
    ax2.set_yticks(np.arange(len(DATASET_ORDER)))
    ax2.set_yticklabels([SHORT_NAMES[d] for d in DATASET_ORDER], fontsize=11.4, fontweight="bold")
    ax2.set_xticks(np.arange(-0.5, len(heat_cols), 1), minor=True)
    ax2.set_yticks(np.arange(-0.5, len(DATASET_ORDER), 1), minor=True)
    ax2.grid(which="minor", color="#FFFFFF", linestyle="-", linewidth=1.6)
    ax2.tick_params(which="minor", bottom=False, left=False)
    ax2.axvline(3.5, color="#0F172A", linewidth=1.8, zorder=4)
    ax2.set_title("B. Melhor época por base e etapa", fontsize=13.5, fontweight="bold", pad=12)
    ax2.set_xlabel("† Melhor época anterior ao platô de treino", fontsize=10.5, fontweight="bold", labelpad=8)

    cbar = fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.03)
    cbar.set_label("Época de seleção (1–100)", fontsize=11.0, fontweight="bold")
    cbar.ax.tick_params(labelsize=10.2)

    out_path = OUT_DIR / "fig_48_tempo_100ep_vs_melhor_epoca.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.14, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_fig_48_metricas_por_tempo(df_be, histories):
    """Figura 4.8-5 (NOVA): Evolução temporal do Macro-F1 de validação nas 9 bases até best.keras e pós-recorde."""
    series_cfg = [
        ("vector_mac", "Vet. Mac", "#0F766E", "o"),
        ("vector_linux", "Vet. Linux", "#65A30D", "s"),
        ("image20", "D20 imagem", "#EA580C", "D"),
        ("cnn", "CNN FP32", "#1E293B", "P"),
        ("q_mac_pennylane", "PQC Mac PL", "#7C3AED", "^"),
        ("q_windows_qiskit", "PQC Win QK", "#B91C1C", "v"),
    ]
    ylims_map = {
        "MNIST": (93.0, 100.0),
        "Fashion-MNIST": (82.5, 93.5),
        "KMNIST": (88.5, 99.6),
        "EMNIST Balanced": (73.5, 90.2),
        "CIFAR-10": (43.0, 75.5),
        "CIFAR-100 Coarse": (19.0, 51.5),
        "SVHN": (73.0, 94.0),
        "GTSRB": (25.0, 102.5),
        "FER2013": (21.0, 52.0),
    }

    fig, axes = plt.subplots(3, 3, figsize=(12.4, 11.4), dpi=300,
                             gridspec_kw={"hspace": 0.36, "wspace": 0.22})
    axes_flat = axes.ravel()

    for idx, ds in enumerate(DATASET_ORDER):
        ax = axes_flat[idx]
        for mk, lbl, col, _ in series_cfg:
            hist = histories[(ds, mk)]
            t = hist["cum_s"]
            f1 = hist["val_f1_pct"]
            be = hist["best_ep"]  # 1-based

            # Traço sólido até best.keras e tracejado translúcido pós-recorde
            ax.plot(t[:be], f1[:be], color=col, lw=2.0, alpha=0.95, zorder=3)
            if be < len(t):
                ax.plot(t[be - 1:], f1[be - 1:], color=col, lw=1.35, ls="--", alpha=0.55, zorder=2)

            # Marcador estrela exatamente no best.keras
            ax.scatter([t[be - 1]], [f1[be - 1]], marker="*", s=135, color=col,
                       edgecolors="#FFFFFF", linewidths=0.75, zorder=5)

        ax.set_xscale("log")
        ax.set_xlim(0.25, 3.2e5)
        ax.set_ylim(*ylims_map[ds])
        ax.set_xticks([1, 100, 1e4, 1e5])
        ax.set_title(SHORT_NAMES[ds], fontsize=13.0, fontweight="bold", pad=8)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 0)))
        ax.tick_params(labelsize=10.4)
        ax.grid(True, which="major", alpha=0.72)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        if idx >= 6:
            ax.set_xlabel("Tempo acumulado (s, log)", fontsize=11.4, fontweight="bold")
        if idx % 3 == 0:
            ax.set_ylabel("Macro-F1 val. (%)", fontsize=11.4, fontweight="bold")

    handles = [
        Line2D([0], [0], color=col, lw=2.2, marker="*", markersize=10,
               markerfacecolor=col, markeredgecolor="#FFFFFF", label=lbl)
        for _, lbl, col, _ in series_cfg
    ]
    handles.extend([
        Line2D([0], [0], color="#475569", lw=2.0, ls="-", label="Época 1 até best.keras"),
        Line2D([0], [0], color="#475569", lw=1.5, ls="--", alpha=0.65, label="Pós-melhor época (até 100)"),
    ])
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.50, 0.035),
               ncol=4, fontsize=10.6, frameon=True, edgecolor="#CBD5E1")

    out_path = OUT_DIR / "fig_48_metricas_por_tempo.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.14, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_fig_48_eficiencia_melhor_epoca_patience15(df_be):
    """Figura 4.8-6 (NOVA): Deslocamento de custo×desempenho (100 ép. → best.keras) e impacto de patience=15."""
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(12.4, 5.8), dpi=300,
        gridspec_kw={"width_ratios": [1.08, 1.0], "wspace": 0.25}
    )

    stage_specs = [
        ("vector_mac", "Vet. Mac", "#0F766E", 0.0, (0.017, 82.07), "best"),
        ("vector_linux", "Vet. Linux", "#65A30D", 0.0, (0.11, 82.31), "100"),
        ("image20", "D20 imagem", "#EA580C", 0.0, (2.3, 82.08), "best"),
        ("cnn", "CNN FP32", "#1E293B", 0.0, (24.5, 81.81), "best"),
        ("q_mac_pennylane", "PQC Mac PL", "#7C3AED", 0.18, (11.5, 82.35), "best"),
        ("q_windows_pennylane", "PQC Win PL", "#2563EB", -0.22, (58.0, 82.03), "best"),
        ("q_mac_qiskit", "PQC Mac QK", "#D97706", 0.22, (150.0, 82.35), "100"),
        ("q_windows_qiskit", "PQC Win QK", "#B91C1C", -0.18, (165.0, 81.88), "100"),
    ]

    # Painel A: Deslocamento 100 ép. -> best.keras para Macro-F1 e Acurácia médias (9 bases)
    for mk, lbl, col, rad, txt_pos, anchor_pt in stage_specs:
        sub = df_be[df_be["model_key"] == mk]
        x_100 = float(sub["tot_h"].sum())
        x_best = float(sub["best_h"].sum())
        y_f1 = float(sub["test_f1_pct"].mean())
        y_acc = float(sub["test_acc_pct"].mean())

        # Macro-F1 (setas + círculos/estrelas)
        ax1.annotate(
            "", xy=(x_best, y_f1), xytext=(x_100, y_f1),
            arrowprops=dict(arrowstyle="-|>,head_length=0.45,head_width=0.25",
                            color=col, lw=1.7, connectionstyle=f"arc3,rad={rad}"),
            zorder=3
        )
        ax1.scatter([x_100], [y_f1], marker="o", s=62, facecolor="#FFFFFF", edgecolor=col, linewidths=1.8, zorder=4)
        ax1.scatter([x_best], [y_f1], marker="*", s=140, color=col, edgecolors="#FFFFFF", linewidths=0.7, zorder=5)

        # Acurácia média (marcadores no topo para contraste com Macro-F1)
        ax1.plot([x_best, x_100], [y_acc, y_acc], color=col, lw=1.0, ls=":", alpha=0.55, zorder=2)
        ax1.scatter([x_100], [y_acc], marker="s", s=34, facecolor="#FFFFFF", edgecolor=col, linewidths=1.3, alpha=0.85, zorder=4)
        ax1.scatter([x_best], [y_acc], marker="s", s=40, color=col, alpha=0.88, zorder=4)

        ax_x = x_best if anchor_pt == "best" else x_100
        ax1.annotate(
            lbl, xy=(ax_x, y_f1), xytext=txt_pos,
            fontsize=9.2, fontweight="bold", color=col, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.14", facecolor="#FFFFFF", edgecolor="none", alpha=0.88),
            arrowprops=dict(arrowstyle="-", color=col, lw=0.75, alpha=0.55, shrinkB=5),
            zorder=6
        )

    ax1.set_xscale("log")
    xticks_h = [1 / 60.0, 5 / 60.0, 0.5, 3.0, 25.0, 200.0]
    xtick_lbls = ["1 min", "5 min", "30 min", "3 h", "25 h", "200 h"]
    ax1.set_xticks(xticks_h)
    ax1.set_xticklabels(xtick_lbls, fontsize=10.6)
    ax1.set_xlim(0.006, 320.0)
    ax1.set_ylim(81.72, 82.82)
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 1)))
    ax1.set_xlabel("Tempo acumulado nas 9 bases (escala log)", fontsize=11.8, fontweight="bold")
    ax1.set_ylabel("Média de teste nas 9 bases (%)", fontsize=11.8, fontweight="bold")
    ax1.set_title("A. Deslocamento de custo: 100 ép. → best.keras", fontsize=13.2, fontweight="bold", pad=12)
    ax1.tick_params(axis="y", labelsize=10.8)
    ax1.grid(True, alpha=0.7)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    leg_1 = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#FFFFFF", markeredgecolor="#334155",
               markeredgewidth=1.6, markersize=7, label="Macro-F1 (100 ép.)"),
        Line2D([0], [0], marker="*", color="w", markerfacecolor="#334155", markersize=11, label="Macro-F1 (best.keras)"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#334155", markersize=6.5, label="Acurácia média (□ → ■)"),
    ]
    ax1.legend(handles=leg_1, loc="lower left", fontsize=9.5, frameon=True, edgecolor="#CBD5E1")

    # Painel B: Simulação patience=15 nos 72 modelos
    df_p15 = df_be.copy()
    df_p15["eco_pct"] = (1.0 - df_p15["p15_s"] / df_p15["tot_s"]) * 100.0
    fam_groups = [
        ("CNN FP32", df_p15["etapa"] == 1, "#1E293B", "P", 78),
        ("Dense20 imagem", df_p15["etapa"] == 2, "#EA580C", "D", 66),
        ("Dense20 vetorial", df_p15["etapa"].isin([3, 4]), "#0F766E", "o", 60),
        ("PQC 4×5 qubits", df_p15["etapa"] >= 5, "#7C3AED", "^", 66),
    ]
    ax2.axhline(0.0, color="#64748B", lw=1.0, ls="--", zorder=1)
    for flbl, mask, col, mk, sz in fam_groups:
        sub = df_p15[mask]
        ax2.scatter(sub["eco_pct"], sub["p15_f1_lost_pp"], label=flbl,
                    color=col, marker=mk, s=sz, alpha=0.84, edgecolors="#FFFFFF", linewidths=0.7, zorder=3)

    # Anotar casos mais sensíveis sem sobreposição
    ann_cases = [
        ("CNN FP32", "CIFAR-100 Coarse", "CNN · CIFAR-100 C.", (39.0, 1.1565), (14.5, 1.07)),
        ("CNN FP32", "EMNIST Balanced", "CNN · EMNIST", (51.0, 0.6109), (60.0, 0.66)),
        ("Dense20 imagem", "EMNIST Balanced", "D20 img · EMNIST", (64.5, 0.1703), (64.0, 0.34)),
        ("PQC Windows PennyLane", "FER2013", "PQC · FER2013 (4 exec.)", (26.0, 0.1456), (26.5, 0.42)),
    ]
    for mod_name, ds_name, txt, (xy_x_def, xy_y_def), (tx, ty) in ann_cases:
        row = df_p15[(df_p15["modelo"] == mod_name) & (df_p15["dataset"] == ds_name)]
        if not row.empty:
            rx = float(row["eco_pct"].iloc[0])
            ry = float(row["p15_f1_lost_pp"].iloc[0])
        else:
            rx, ry = xy_x_def, xy_y_def
        ax2.annotate(
            txt, xy=(rx, ry), xytext=(tx, ty),
            fontsize=9.3, fontweight="bold", color="#1E293B",
            bbox=dict(boxstyle="round,pad=0.16", facecolor="#FFFFFF", edgecolor="#CBD5E1", alpha=0.95),
            arrowprops=dict(arrowstyle="-", color="#64748B", lw=0.9, shrinkB=4),
            zorder=5
        )

    ax2.set_xlim(-2, 87)
    ax2.set_ylim(-0.07, 1.28)
    ax2.xaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 0)))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 2)))
    ax2.set_xlabel("Economia temporal simulada (%)", fontsize=11.8, fontweight="bold")
    ax2.set_ylabel("Perda de Macro-F1 val. (p.p.)", fontsize=11.8, fontweight="bold")
    ax2.set_title("B. Risco da parada antecipada (patience=15)", fontsize=13.2, fontweight="bold", pad=12)
    ax2.tick_params(labelsize=10.8)
    ax2.grid(True, alpha=0.7)
    ax2.legend(loc="upper right", fontsize=9.8, frameon=True, edgecolor="#CBD5E1")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    out_path = OUT_DIR / "fig_48_eficiencia_melhor_epoca_patience15.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.14, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_fig_48_telemetria_hardware_io(df_runs, df_ses, df_tel, df_mac, df_proj):
    """Figura 4.8-7 (Fig 62 atualizada): Telemetria histórica 100 ép. + GPU AGX e disco complementar do iMac M4."""
    df_tel = df_tel.copy()
    df_tel["cpu_eff"] = df_tel["cpu_tree"].fillna(df_tel["cpu_process"])
    df_tel["rss_eff"] = df_tel["rss_tree_mib_max"].fillna(df_tel["rss_process_mib_max"])

    run_meta = df_ses.drop_duplicates(subset=["codigo"])[["codigo", "dataset", "ambiente", "grupo"]]
    tel_m = df_tel.merge(run_meta, on="codigo", how="left")

    mac_fam_map = {
        "Dense20 vetorial Mac": "classico",
        "PQC Mac PennyLane": "pennylane",
        "PQC Mac Qiskit": "qiskit",
    }

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
            fk = mac_fam_map[grp_key]
            m_sub = df_mac[df_mac["familia"] == fk]
            w = m_sub["n_treino"].values
            gpu_mean = float((m_sub["gpu_agx_media_pct"].values * w).sum() / w.sum())
            p_sub = df_proj[df_proj["familia"] == fk]
            read_gib = float(p_sub["io_principal_leitura_100_epocas_gib"].sum())
            write_gib = float(p_sub["io_principal_escrita_100_epocas_gib"].sum())
            mac_comp = True
        else:
            g_valid = sub_t.dropna(subset=["gpu_util", "samples"])
            gpu_mean = float((g_valid["gpu_util"] * g_valid["samples"]).sum() / g_valid["samples"].sum())
            read_gib = float(sub_s["leitura_mib"].fillna(0.0).sum() / 1024.0)
            write_gib = float(sub_s["escrita_mib"].fillna(0.0).sum() / 1024.0)
            mac_comp = False

        stats.append({
            "key": grp_key, "label": lbl, "amb": amb, "color": col,
            "cpu_mean": cpu_mean,
            "rss_mean": rss_mean, "rss_max": rss_abs_max,
            "gpu_mean": gpu_mean,
            "read_gib": read_gib, "write_gib": write_gib,
            "mac_comp": mac_comp,
        })

    fig, axes = plt.subplots(2, 2, figsize=(11.6, 8.2), dpi=300, sharey=True,
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
    ax_b.legend(loc="lower right", fontsize=10.6, frameon=True, edgecolor="#CBD5E1")

    # Painel C: GPU RTX A2000 (100 ép.) + Apple AGX (coleta complementar 1 ép.*)
    for yi, s in zip(y, stats):
        gv = s["gpu_mean"]
        if s["mac_comp"]:
            ax_c.barh(yi, gv, height=0.60, color=s["color"], edgecolor="#FFFFFF",
                      hatch="///", linewidth=0.8, alpha=0.90, zorder=3)
            txt = f"{fmt_pt(gv, 2)}%*"
        else:
            ax_c.barh(yi, gv, height=0.60, color=s["color"], alpha=0.93, zorder=3)
            txt = f"{fmt_pt(gv, 1)}%"
        ax_c.text(gv + 1.1, yi, txt, va="center", ha="left",
                  fontsize=11.2, fontweight="bold", color="#0F172A")
    ax_c.set_xlim(0, 58)
    ax_c.set_yticks(y)
    ax_c.set_yticklabels(y_labels, fontsize=12.0, fontweight="bold")
    ax_c.set_xlabel("Utilização média (%)", fontsize=12.0, fontweight="bold")
    ax_c.set_title("C. Utilização média de GPU", fontsize=13.8, fontweight="bold", pad=10)
    leg_c = [
        Patch(facecolor="#475569", edgecolor="#1E293B", label="RTX A2000 (100 ép.)"),
        Patch(facecolor="#7C3AED", edgecolor="#FFFFFF", hatch="///", label="Apple AGX (compl. 1 ép.)*"),
    ]
    ax_c.legend(handles=leg_c, loc="lower right", fontsize=10.0, frameon=True, edgecolor="#CBD5E1")

    # Painel D: Volume de I/O acumulado (GiB) — medido em Linux/Win + projeção condicional 100 ép. no Mac*
    h_io = 0.36
    for yi, s in zip(y, stats):
        r_v, w_v = s["read_gib"], s["write_gib"]
        if s["mac_comp"]:
            ax_d.barh(yi + h_io / 2, r_v, height=h_io * 0.88, color="#0284C7",
                      edgecolor="#FFFFFF", hatch="///", linewidth=0.7, alpha=0.90, zorder=3)
            ax_d.barh(yi - h_io / 2, w_v, height=h_io * 0.88, color="#F97316",
                      edgecolor="#FFFFFF", hatch="///", linewidth=0.7, alpha=0.90, zorder=3)
            if r_v >= 1.0 or w_v >= 1.0:
                ax_d.text(r_v + 4.5, yi + h_io / 2, f"{fmt_pt(r_v, 2)}*", va="center", ha="left",
                          fontsize=10.4, fontweight="bold", color="#0369A1")
                ax_d.text(w_v + 4.5, yi - h_io / 2, f"{fmt_pt(w_v, 2)}*", va="center", ha="left",
                          fontsize=10.4, fontweight="bold", color="#C2410C")
            else:
                ax_d.text(max(r_v, w_v) + 4.5, yi, f"{fmt_pt(r_v, 3)} / {fmt_pt(w_v, 2)}*",
                          va="center", ha="left", fontsize=10.2, fontweight="bold", color="#334155")
        else:
            ax_d.barh(yi + h_io / 2, r_v, height=h_io * 0.88, color="#0284C7", zorder=3)
            ax_d.barh(yi - h_io / 2, w_v, height=h_io * 0.88, color="#F97316", zorder=3)
            if r_v >= 1.0 or w_v >= 1.0:
                ax_d.text(r_v + 4.5, yi + h_io / 2, f"{fmt_pt(r_v, 1)}", va="center", ha="left",
                          fontsize=10.6, fontweight="bold", color="#0369A1")
                ax_d.text(w_v + 4.5, yi - h_io / 2, f"{fmt_pt(w_v, 1)}" if w_v >= 0.1 else "0,02",
                          va="center", ha="left", fontsize=10.6, fontweight="bold", color="#C2410C")
            else:
                ax_d.text(max(r_v, w_v) + 4.5, yi, f"{fmt_pt(r_v, 2)} / {fmt_pt(w_v, 2)}",
                          va="center", ha="left", fontsize=10.4, fontweight="bold", color="#334155")
    ax_d.set_xlim(0, 295)
    ax_d.set_xlabel("I/O acumulado em 100 épocas (GiB)", fontsize=12.0, fontweight="bold")
    ax_d.set_title("D. Disco (processo principal)", fontsize=13.8, fontweight="bold", pad=10)
    leg_d = [
        Patch(facecolor="#0284C7", label="Leitura"),
        Patch(facecolor="#F97316", label="Escrita"),
        Patch(facecolor="#64748B", edgecolor="#FFFFFF", hatch="///", label="Proj. 100 ép. Mac*"),
    ]
    ax_d.legend(handles=leg_d, loc="upper right", bbox_to_anchor=(0.99, 0.99),
                fontsize=10.2, frameon=True, edgecolor="#CBD5E1")

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
    df_be, histories = carregar_dados_melhor_epoca(df_f26)

    gerar_fig_48_tempos_etapas_consolidado(df_runs, df_f26)
    gerar_fig_48_diferencas_ambientes_simuladores(df_runs)
    gerar_fig_fatores_aceleracao(df_runs)
    gerar_fig_48_tempo_100ep_vs_melhor_epoca(df_be)
    gerar_fig_48_metricas_por_tempo(df_be, histories)
    gerar_fig_48_eficiencia_melhor_epoca_patience15(df_be)
    gerar_fig_48_telemetria_hardware_io(df_runs, df_ses, df_tel, df_mac, df_proj)
    gerar_fig_48_mac_hardware_io_complementar(df_mac)
    gerar_fig_48_mac_hardware_sensores_macmon(df_mac, df_proj)
    print("Todas as 9 figuras da Seção 4.8 foram geradas com sucesso!")
