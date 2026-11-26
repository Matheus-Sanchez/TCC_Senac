# -*- coding: utf-8 -*-
"""Gera figuras otimizadas para projeção em slides (fontes ampliadas, 300 DPI) e GIFs recortados.

Isolamento rigoroso:
- NÃO sobrescreve nenhuma figura em TCC_Senac/figuras/ usada por tcc2-adaptado.tex.
- Salva PNGs específicos para slides em TCC_Senac/figuras/slides/.
- Salva GIFs recortados (sem faixa inferior de fórmulas) em TCC_Senac/figuras/gifs_slides/.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
from PIL import Image

BASE_DIR = pathlib.Path(__file__).resolve().parent
FIG_DIR = BASE_DIR / "figuras"
SLIDE_FIG_DIR = FIG_DIR / "slides"
GIF_SRC_DIR = FIG_DIR / "gifs"
GIF_SLIDE_DIR = FIG_DIR / "gifs_slides"
SLIDE_FIG_DIR.mkdir(parents=True, exist_ok=True)
GIF_SLIDE_DIR.mkdir(parents=True, exist_ok=True)

PROJ_ROOT = pathlib.Path(r"C:\Users\matheus.sduda\repos\projeto-TCC")
FEATURES_ROOT = PROJ_ROOT / "outputs" / "classic-dense20"
ROOT_OUT = pathlib.Path(r"C:\Users\matheus.sduda\Documents\ChatGPT\projeto-do-tcc\outputs")
CSV_FIG26 = ROOT_OUT / "analise-ilustrada-2026-10-27" / "dados_dos_graficos" / "figura_26_comparacao_matriz.csv"
ROOT_OCL = ROOT_OUT / "oclusao-completa-2026-11-07"
ROOT_GC = ROOT_OUT / "explicabilidade-gradcam-2026-11-05"

# Importa helpers existentes do repositorio sem duplicar logica
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
import gerar_figuras_revisao_tcc2 as gfr
import gerar_figuras_consolidacao_4_8 as gf48

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


def fmt_pt(val: float, decimals: int = 2) -> str:
    return f"{val:.{decimals}f}".replace(".", ",")


# =====================================================================
# 1A. RECORTAR GIFS ANIMADOS (REMOVER FAIXA DE FORMULAS / CALCULO)
# =====================================================================
def crop_animated_gif(src_path: pathlib.Path, dst_path: pathlib.Path, crop_box: tuple[int, int, int, int]) -> None:
    """Recorta todos os quadros de um GIF preservando animacao e duracoes originais."""
    with Image.open(src_path) as im:
        n_frames = getattr(im, "n_frames", 1)
        frames_rgb = []
        durations = []
        for idx in range(n_frames):
            im.seek(idx)
            durations.append(int(im.info.get("duration", 140)))
            rgba = im.convert("RGBA")
            bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
            comp = Image.alpha_composite(bg, rgba).convert("RGB")
            cropped = comp.crop(crop_box)
            frames_rgb.append(cropped.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE))

        frames_rgb[0].save(
            dst_path,
            save_all=True,
            append_images=frames_rgb[1:],
            duration=durations,
            loop=0,
            disposal=2,
            optimize=False,
        )
    print(f"GIF recortado: {dst_path.name} {crop_box[2]-crop_box[0]}x{crop_box[3]-crop_box[1]} ({n_frames} frames)")


def crop_all_gifs() -> None:
    specs = [
        ("07_sepconv_numerico.gif", "07_sepconv_numerico_clean.gif", (0, 99, 1204, 481)),
        ("05_zoom_bloco_cnn.gif", "05_zoom_bloco_cnn_clean.gif", (0, 0, 1204, 470)),
        ("02_fluxo_dense20_imagem.gif", "02_fluxo_dense20_imagem_clean.gif", (0, 0, 1204, 473)),
        ("03_fluxo_classico_tanh.gif", "03_fluxo_classico_tanh_clean.gif", (0, 0, 1204, 473)),
        ("04_fluxo_hibrido_4xpqc.gif", "04_fluxo_hibrido_4xpqc_clean.gif", (0, 0, 1204, 473)),
        ("06_zoom_pqc_5qubits.gif", "06_zoom_pqc_5qubits_clean.gif", (0, 0, 1204, 470)),
        ("08_comparativo_4_etapas.gif", "08_comparativo_4_etapas_clean.gif", (0, 0, 1204, 495)),
    ]
    for src_name, dst_name, box in specs:
        crop_animated_gif(GIF_SRC_DIR / src_name, GIF_SLIDE_DIR / dst_name, box)


# =====================================================================
# 1B. METRICAS DE CLASSIFICACAO (SLIDE 8)
# =====================================================================
def gerar_metricas_slide() -> None:
    cm = np.array([[42, 5, 3], [4, 31, 9], [2, 6, 38]])
    classes = ["Classe 0", "Classe 1", "Classe 2"]

    tp = np.diag(cm).astype(float)
    fn = (cm.sum(axis=1) - tp).astype(float)
    fp = (cm.sum(axis=0) - tp).astype(float)
    prec = tp / (tp + fp) * 100.0
    rec = tp / (tp + fn) * 100.0
    f1 = 2 * prec * rec / (prec + rec)
    macro_f1 = float(np.mean(f1))

    tp2, fn2, fp2 = int(tp[2]), int(fn[2]), int(fp[2])
    tn2 = int(cm.sum() - tp2 - fn2 - fp2)

    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.0), dpi=300,
                             gridspec_kw={"hspace": 0.42, "wspace": 0.38})
    ax_cm, ax_ovr, ax_bar, ax_roc = axes.ravel()

    # A. Matriz de confusao
    im = ax_cm.imshow(cm, cmap="Blues", vmin=0, vmax=45, aspect="auto")
    cbar = fig.colorbar(im, ax=ax_cm, fraction=0.048, pad=0.04)
    cbar.ax.tick_params(labelsize=12.0)
    ax_cm.set_xticks(np.arange(3))
    ax_cm.set_yticks(np.arange(3))
    ax_cm.set_xticklabels(classes, fontsize=12.5, fontweight="bold")
    ax_cm.set_yticklabels(classes, fontsize=12.5, fontweight="bold")
    ax_cm.set_xlabel("Classe prevista", fontsize=13.5, fontweight="bold")
    ax_cm.set_ylabel("Classe real", fontsize=13.5, fontweight="bold")
    ax_cm.set_title("A. Matriz de confusão", fontsize=14.8, fontweight="bold", pad=10)
    for i in range(3):
        for j in range(3):
            v = int(cm[i, j])
            ax_cm.text(j, i, str(v), ha="center", va="center", fontsize=18.0, fontweight="bold",
                       color="#FFFFFF" if v >= 26 else "#0F172A")

    # B. Decomposicao um-contra-todos
    ax_ovr.set_xlim(0.0, 1.0)
    ax_ovr.set_ylim(0.0, 1.0)
    ax_ovr.axis("off")
    ax_ovr.set_title("B. Um contra todos (Classe 2)", fontsize=14.8, fontweight="bold", pad=10)

    ax_ovr.text(0.42, 0.90, "Prev.: Cl. 2", ha="center", va="center", fontsize=12.8, fontweight="bold", color="#1E293B")
    ax_ovr.text(0.79, 0.90, "Prev.: Outras", ha="center", va="center", fontsize=12.8, fontweight="bold", color="#1E293B")
    ax_ovr.text(0.11, 0.63, "Real:\nCl. 2", ha="center", va="center", fontsize=12.8, fontweight="bold", color="#1E293B")
    ax_ovr.text(0.11, 0.24, "Real:\nOutras", ha="center", va="center", fontsize=12.8, fontweight="bold", color="#1E293B")

    cells = [
        (0.25, 0.45, 0.34, 0.35, f"TP = {tp2}\nAcerto", "#DCFCE7", "#15803D", "#14532D"),
        (0.62, 0.45, 0.34, 0.35, f"FN = {fn2}\nOmissão", "#FEE2E2", "#DC2626", "#7F1D1D"),
        (0.25, 0.06, 0.34, 0.35, f"FP = {fp2}\nAlarme", "#FEF3C7", "#D97706", "#78350F"),
        (0.62, 0.06, 0.34, 0.35, f"TN = {tn2}\nCorretas", "#E0F2FE", "#0284C7", "#0C4A6E"),
    ]
    for x, y, w, h, txt, fc, ec, tc in cells:
        patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.03",
                               facecolor=fc, edgecolor=ec, linewidth=1.8)
        ax_ovr.add_patch(patch)
        ax_ovr.text(x + w / 2.0, y + h / 2.0, txt, ha="center", va="center",
                    fontsize=13.5, fontweight="bold", color=tc, linespacing=1.25)

    # C. Barras agrupadas
    x = np.arange(3)
    bw = 0.27
    b1 = ax_bar.bar(x - bw, prec, width=bw * 0.90, color="#1D4ED8", label="Precisão", zorder=3)
    b2 = ax_bar.bar(x, rec, width=bw * 0.90, color="#0F766E", label="Revocação", zorder=3)
    b3 = ax_bar.bar(x + bw, f1, width=bw * 0.90, color="#D97706", label="F1-score", zorder=3)
    ax_bar.axhline(macro_f1, color="#DC2626", linestyle="--", linewidth=2.0,
                   label=f"Macro-F1 = {fmt_pt(macro_f1, 1)}%", zorder=3.5)

    for bars, col in ((b1, "#1E40AF"), (b2, "#115E59"), (b3, "#92400E")):
        for bar in bars:
            v = bar.get_height()
            ax_bar.text(bar.get_x() + bar.get_width() / 2.0, v + 2.2, fmt_pt(v, 1),
                        ha="center", va="bottom", fontsize=10.0, fontweight="bold", color=col, zorder=6,
                        bbox=dict(boxstyle="square,pad=0.02", facecolor="#FFFFFF", edgecolor="none", alpha=0.85))

    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(classes, fontsize=12.5, fontweight="bold")
    ax_bar.set_xlim(-0.54, 2.54)
    ax_bar.set_ylim(0, 130)
    ax_bar.set_yticks([0, 20, 40, 60, 80, 100])
    ax_bar.tick_params(axis="y", labelsize=12.0)
    ax_bar.set_ylabel("Valor (%)", fontsize=13.5, fontweight="bold")
    ax_bar.set_title("C. Métricas por classe e Macro-F1", fontsize=14.8, fontweight="bold", pad=10)
    ax_bar.grid(True, axis="y", alpha=0.8)
    ax_bar.legend(loc="upper right", fontsize=11.0, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1", ncol=2)
    ax_bar.spines["top"].set_visible(False)
    ax_bar.spines["right"].set_visible(False)

    # D. Curva ROC
    fpr = np.array([0.0, 0.06, 0.12, 0.22, 0.36, 0.56, 0.78, 1.0])
    tpr = np.array([0.0, 0.34, 0.54, 0.72, 0.84, 0.92, 0.97, 1.0])
    auc_val = float(np.trapezoid(tpr, fpr)) if hasattr(np, "trapezoid") else float(np.trapz(tpr, fpr))
    ax_roc.plot(fpr, tpr, color="#1D4ED8", linewidth=2.8, label=f"ROC (AUC = {fmt_pt(auc_val, 2)})", zorder=4)
    ax_roc.fill_between(fpr, tpr, 0, color="#DBEAFE", alpha=0.55, zorder=2)
    ax_roc.plot([0, 1], [0, 1], color="#64748B", linestyle="--", linewidth=1.6, label="Acaso (0,50)", zorder=3)
    ax_roc.text(0.57, 0.38, f"AUC = {fmt_pt(auc_val, 2)}",
                ha="center", va="center", fontsize=14.0, fontweight="bold", color="#1E3A8A")
    ax_roc.set_xlim(-0.02, 1.02)
    ax_roc.set_ylim(-0.02, 1.04)
    ax_roc.tick_params(labelsize=12.0)
    ax_roc.set_xlabel("Falsos positivos (FPR)", fontsize=13.2, fontweight="bold")
    ax_roc.set_ylabel("Verdadeiros positivos (TPR)", fontsize=13.2, fontweight="bold")
    ax_roc.set_title("D. Curva ROC / AUC", fontsize=14.8, fontweight="bold", pad=10)
    ax_roc.grid(True, alpha=0.8)
    ax_roc.legend(loc="lower right", fontsize=11.5, frameon=True, edgecolor="#CBD5E1")
    ax_roc.spines["top"].set_visible(False)
    ax_roc.spines["right"].set_visible(False)

    out_path = SLIDE_FIG_DIR / "metricas_classificacao_exemplos_slide.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)
    print("Gerado:", out_path.name)


# =====================================================================
# 1B. AUGMENTATION & FLIP_LR (SLIDES 11 e 12)
# =====================================================================
def gerar_augmentations_e_flip_slide() -> None:
    vis_root = PROJ_ROOT / "reports" / "visualizacoes-augmentation-feature-maps"
    src_root = PROJ_ROOT / "src"
    for p in (str(src_root), str(vis_root)):
        if p not in sys.path:
            sys.path.insert(0, p)

    import tensorflow as tf
    import gerar_visualizacoes as gv

    samples = gv.load_verified_samples()
    cfg = gv.AugmentationConfig(flip_lr=False)

    for key, fname in (("gtsrb_stop", "aug_01_pipeline_etapas_gtsrb_slide.png"),
                       ("cifar10_ship", "aug_02_pipeline_etapas_cifar10_slide.png")):
        sample = samples[key]
        img = sample["tensor"]
        ex_idx = gv.find_rich_aug_index(img, cfg, base_seed=42)
        steps = gv.isolated_step_outputs(img, cfg, base_seed=42, example_index=ex_idx)
        orig = steps[0][2]

        fig = plt.figure(figsize=(16.5, 4.35), dpi=260)
        gs = fig.add_gridspec(
            2, 9,
            width_ratios=[1, 1, 1, 1, 1, 1, 1, 1, 0.12],
            left=0.045, right=0.945, top=0.90, bottom=0.09, wspace=0.11, hspace=0.30,
        )
        short_titles = [
            "Original", "1. Translação", "2. Zoom", "3. Brilho",
            "4. Contraste", "5. Ruído", "6. Cutout", "7. Composto",
        ]
        im_diff = None
        for col, (stitle, (_, param_txt, arr)) in enumerate(zip(short_titles, steps)):
            ax_top = fig.add_subplot(gs[0, col])
            gv.imshow_image(ax_top, arr)
            ax_top.set_title(stitle, fontsize=14.0, fontweight="bold", pad=6)
            ax_top.set_xlabel(param_txt, fontsize=11.0, color="#334155", fontweight="bold", labelpad=4)

            ax_bot = fig.add_subplot(gs[1, col])
            dmap = gv.rms_diff_map(arr, orig)
            rmse = float(np.sqrt(np.mean(np.square(arr - orig))))
            im_diff = ax_bot.imshow(dmap, cmap="inferno", vmin=0.0, vmax=0.12, interpolation="nearest")
            ax_bot.set_xticks([])
            ax_bot.set_yticks([])
            lbl_bot = "Referência" if col == 0 else f"RMS={fmt_pt(rmse, 4)}"
            ax_bot.set_xlabel(lbl_bot, fontsize=11.4, fontweight="bold" if col > 0 else "normal",
                              color="#0F172A" if col > 0 else "#475569", labelpad=4)

        fig.text(0.015, 0.70, "Imagem", rotation=90, va="center", ha="center", fontsize=14.0, fontweight="bold")
        fig.text(0.015, 0.27, "|Δ| RMS", rotation=90, va="center", ha="center", fontsize=14.0, fontweight="bold")
        cax = fig.add_subplot(gs[1, 8])
        cbar = fig.colorbar(im_diff, cax=cax)
        cbar.set_label("|Δ| RMS", fontsize=11.5, fontweight="bold")
        cbar.ax.tick_params(labelsize=11.0)

        out_path = SLIDE_FIG_DIR / fname
        fig.savefig(out_path, dpi=260, bbox_inches="tight", pad_inches=0.06)
        plt.close(fig)
        print("Gerado:", out_path.name)

    # Flip LR semantico
    items = [
        ("gtsrb_left", "GTSRB (cl. 34)"),
        ("mnist_3", "MNIST ('3')"),
        ("emnist_r", "EMNIST ('R')"),
        ("svhn_5", "SVHN ('5')"),
        ("cifar10_horse", "CIFAR-10 (cavalo)"),
    ]
    row_labels = ["Original", "flip_lr = False\n(atual)", "flip_lr = True\n(legado)"]

    fig = plt.figure(figsize=(15.0, 7.2), dpi=260)
    gs = fig.add_gridspec(3, 5, left=0.12, right=0.98, top=0.93, bottom=0.07, wspace=0.14, hspace=0.28)

    for col, (key, title) in enumerate(items):
        s = samples[key]
        model = gv.load_fp32_model(s["dataset"])
        img = s["tensor"]
        cfg_no_flip = gv.AugmentationConfig(flip_lr=False, cutout_prob=0.0)
        aug_no_flip = gv.augment_image(img, cfg_no_flip, base_seed=42, example_index=2)
        flipped_only = tf.image.flip_left_right(img)

        imgs = [img.numpy(), aug_no_flip.numpy(), flipped_only.numpy()]
        preds = tf.nn.softmax(model(np.stack(imgs, axis=0), training=False)).numpy()

        for row in range(3):
            ax = fig.add_subplot(gs[row, col])
            gv.imshow_image(ax, imgs[row])
            pred_cls = int(np.argmax(preds[row]))
            pred_prob = float(preds[row, pred_cls]) * 100.0
            if row == 0:
                ax.set_title(title, fontsize=14.2, fontweight="bold", pad=8)
            is_asym = (key != "cifar10_horse")
            if row == 1:
                col_sp = "#15803D"
                for sp in ax.spines.values():
                    sp.set_edgecolor(col_sp)
                    sp.set_linewidth(2.4)
            elif row == 2:
                col_sp = "#B91C1C" if is_asym else "#0284C7"
                for sp in ax.spines.values():
                    sp.set_edgecolor(col_sp)
                    sp.set_linewidth(2.4)
            else:
                col_sp = "#475569"

            ax.set_xlabel(f"Pred.: cl. {pred_cls} ({fmt_pt(pred_prob, 1)}%)",
                          fontsize=12.0, color=col_sp, fontweight="bold", labelpad=5)
        tf.keras.backend.clear_session()

    for row, rlabel in enumerate(row_labels):
        y_center = 0.80 - row * 0.305
        fig.text(0.055, y_center, rlabel, va="center", ha="center", fontsize=13.5, fontweight="bold")

    out_flip = SLIDE_FIG_DIR / "aug_03_comparacao_flip_lr_semantico_slide.png"
    fig.savefig(out_flip, dpi=260, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print("Gerado:", out_flip.name)


# =====================================================================
# 1B. EQUILIBRIO DE CLASSES HORIZONTAL 3x3 (SLIDE 23 / ANTIGO 25)
# =====================================================================
def gerar_equilibrio_horizontal_slide() -> None:
    specs = [
        ("mnist", "MNIST", False),
        ("fashion_mnist", "Fashion-MNIST", False),
        ("kmnist", "KMNIST", False),
        ("emnist_balanced", "EMNIST Balanced", False),
        ("cifar10", "CIFAR-10", False),
        ("cifar100_coarse", "CIFAR-100 Coarse", False),
        ("svhn", "SVHN", True),
        ("gtsrb", "GTSRB", True),
        ("fer2013", "FER2013", True),
    ]
    fer_names = ["Raiva", "Desg.", "Medo", "Feliz", "Triste", "Surpr.", "Neutro"]

    fig, axes = plt.subplots(3, 3, figsize=(16.2, 8.6), dpi=300,
                             gridspec_kw={"hspace": 0.44, "wspace": 0.18})
    axes_flat = axes.ravel()

    c_train, c_val, c_test = "#1E5AA8", "#5B9BD5", "#A5C8E4"

    for idx, (ds, label, is_unbal) in enumerate(specs):
        ax = axes_flat[idx]
        f128_dir = FEATURES_ROOT / ds / "runs" / f"{ds}__dense20_fp32_aug05__seed-42" / "artifacts" / "features128"
        y_tr = np.bincount(np.load(f128_dir / "train_labels.npy").astype(int))
        y_va = np.bincount(np.load(f128_dir / "val_labels.npy").astype(int))
        y_te = np.bincount(np.load(f128_dir / "test_labels.npy").astype(int))
        tot = y_tr + y_va + y_te
        K = len(tot)
        ir = float(tot.max()) / float(tot.min())
        x = np.arange(K)
        bw = 0.80 if K <= 20 else 0.85

        ax.bar(x, y_tr, width=bw, color=c_train, label="Treino (70%)" if idx == 0 else None, zorder=3)
        ax.bar(x, y_va, bottom=y_tr, width=bw, color=c_val, label="Validação (15%)" if idx == 0 else None, zorder=3)
        ax.bar(x, y_te, bottom=y_tr + y_va, width=bw, color=c_test, label="Teste (15%)" if idx == 0 else None, zorder=3)

        mean_v = float(tot.sum()) / float(K)
        ax.axhline(mean_v, color="#B91C1C", linestyle="--", linewidth=1.6,
                   label="Média uniforme (N / K)" if idx == 0 else None, zorder=4)

        title_col = "#B91C1C" if is_unbal else "#0F172A"
        ax.set_title(f"{label} (K={K} | IR={fmt_pt(ir, 2)}×)", fontsize=13.5, fontweight="bold", color=title_col, pad=7)
        ax.set_ylim(0, tot.max() * 1.15)
        ax.grid(True, axis="y", alpha=0.6)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.set_major_formatter(lambda val, pos: f"{int(val):,}".replace(",", "."))
        ax.tick_params(axis="y", labelsize=11.0)

        if ds == "fer2013":
            ax.set_xticks(x)
            ax.set_xticklabels(fer_names, fontsize=10.5, fontweight="bold", rotation=18, ha="right")
        elif K <= 10:
            ax.set_xticks(x)
            ax.set_xticklabels([str(i) for i in x], fontsize=11.0)
        elif K == 20:
            ax.set_xticks(np.arange(0, 20, 4))
            ax.tick_params(axis="x", labelsize=11.0)
        else:
            ax.set_xticks(np.arange(0, K, 10))
            ax.tick_params(axis="x", labelsize=11.0)

        if idx % 3 == 0:
            ax.set_ylabel("Amostras", fontsize=12.5, fontweight="bold")
        if idx >= 6:
            ax.set_xlabel("Classe", fontsize=12.0, fontweight="bold")

    handles, labels = axes_flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.50, 0.995),
               ncol=4, fontsize=13.5, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1")
    fig.subplots_adjust(top=0.90)

    out_path = SLIDE_FIG_DIR / "equilibrio_classes_9_datasets_horiz.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)
    print("Gerado:", out_path.name)


# =====================================================================
# 1B. BALANCEAMENTO: MACRO-F1 E TEMPO (SLIDE 24 / ANTIGO 26)
# =====================================================================
def gerar_balanceamento_slide() -> None:
    df = gfr.parse_notebook_table(6)
    x = np.arange(len(gfr.DS_CANONICAL_ORDER))
    w = 0.20
    offsets = [-1.5 * w, -0.5 * w, 0.5 * w, 1.5 * w]
    lookup = df.set_index(["dataset", "balance_mode"])

    # Primeiro grafico: Macro-F1 com legenda ampliada (pedido explicito do usuario)
    fig, ax = plt.subplots(figsize=(8.4, 5.8), dpi=300)
    for (mode, label, color), off in zip(gfr.MODE_META, offsets):
        vals = [float(lookup.loc[(ds, mode), "test_macro_f1"]) * 100.0 for ds, _ in gfr.DS_CANONICAL_ORDER]
        bars = ax.bar(x + off, vals, width=w * 0.90, color=color, label=label, alpha=0.93, zorder=3)
        for bar, v, (ds, _) in zip(bars, vals, gfr.DS_CANONICAL_ORDER):
            if ds in ("svhn", "gtsrb", "fer2013"):
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0, v + 1.5, fmt_pt(v, 1),
                    ha="center", va="bottom", fontsize=11.2, fontweight="bold",
                    color=color, rotation=90
                )

    ax.axvspan(5.55, 8.45, color="#FEF3C7", alpha=0.42, zorder=1)
    ax.text(7.0, 117.0, "IR > 3×", ha="center", va="top", fontsize=13.5, fontweight="bold", color="#92400E")

    ax.set_xticks(x)
    ax.set_xticklabels([lbl for _, lbl in gfr.DS_CANONICAL_ORDER], fontsize=13.0, fontweight="bold", rotation=26, ha="right")
    ax.set_ylim(0, 121)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.tick_params(axis="y", labelsize=13.0)
    ax.set_ylabel("Macro-F1 de teste (%)", fontsize=15.0, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(
        loc="lower center", bbox_to_anchor=(0.5, 1.02),
        ncol=2, fontsize=14.2, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1",
        columnspacing=1.0, handletextpad=0.5
    )

    out1 = SLIDE_FIG_DIR / "fig_balanceamento_macro_f1_slide.png"
    fig.savefig(out1, dpi=300, bbox_inches="tight", pad_inches=0.08, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out1.name)

    # Segundo grafico: Tempo de treino
    fig, ax1 = plt.subplots(figsize=(7.2, 5.8), dpi=300)
    for (mode, label, color), off in zip(gfr.MODE_META, offsets):
        hrs = [float(lookup.loc[(ds, mode), "training_hours"]) for ds, _ in gfr.DS_CANONICAL_ORDER]
        bars = ax1.bar(x + off, hrs, width=w * 0.90, color=color, label=label, alpha=0.93, zorder=3)
        for bar, h_val in zip(bars, hrs):
            if h_val >= 4.4:
                ax1.text(
                    bar.get_x() + bar.get_width() / 2.0, h_val + 0.22, f"{fmt_pt(h_val, 2)} h",
                    ha="center", va="bottom", fontsize=12.4, fontweight="bold", color=color, rotation=90
                )

    ax1.set_xticks(x)
    ax1.set_xticklabels([lbl for _, lbl in gfr.DS_CANONICAL_ORDER], fontsize=13.0, fontweight="bold", rotation=26, ha="right")
    ax1.tick_params(axis="y", labelsize=13.0)
    ax1.set_ylim(0, 12.8)
    ax1.set_ylabel("Tempo total de treino (h)", fontsize=15.0, fontweight="bold")
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 0)))
    ax1.set_title("Tempo de treino (88,86 h)", fontsize=15.0, fontweight="bold", pad=72)
    ax1.grid(True, axis="y", alpha=0.8)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(
        loc="lower center", bbox_to_anchor=(0.5, 1.02),
        ncol=2, fontsize=13.8, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1",
        columnspacing=0.9, handletextpad=0.45
    )

    out2 = SLIDE_FIG_DIR / "fig_342_balanceamento_tempo_treino_slide.png"
    fig.savefig(out2, dpi=300, bbox_inches="tight", pad_inches=0.08, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out2.name)


# =====================================================================
# 1B. DIAGRAMA ETAPA 1 COM FONTES MAIORES (SLIDE 28 / ANTIGO 30)
# =====================================================================
def gerar_diagrama_etapa1_slide() -> None:
    fig, ax = plt.subplots(figsize=(14.4, 4.9), dpi=300)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    top_bg = FancyBboxPatch((0.008, 0.490), 0.984, 0.495,
                            boxstyle="round,pad=0.004,rounding_size=0.012",
                            facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.2, zorder=1)
    ax.add_patch(top_bg)
    ax.text(0.022, 0.968, "Fluxo completo da CNN de origem (treinamento ponta a ponta em FP32)",
            ha="left", va="top", fontsize=13.2, fontweight="bold", color="#1E3A5F", zorder=4)

    gfr.draw_box(ax, 0.018, 0.595, 0.100, 0.225,
                 "Entrada\n64×64×C\n(128×128×3)", fc="#E2E8F0", ec="#475569", fs=11.0)

    ext_bg = FancyBboxPatch((0.132, 0.525), 0.398, 0.375,
                            boxstyle="round,pad=0.004,rounding_size=0.012",
                            facecolor="#EFF6FF", edgecolor="#3B82F6", linewidth=1.3, linestyle="--", zorder=2)
    ax.add_patch(ext_bg)
    ax.text(0.331, 0.888, "Extrator Convolucional (5 Blocos)",
            ha="center", va="top", fontsize=11.4, fontweight="bold", color="#1D4ED8", zorder=4)
    ax.text(0.331, 0.540, "66.905 pesos (C=1)  |  67.019 pesos (C=3)",
            ha="center", va="bottom", fontsize=10.4, fontweight="bold", color="#1E40AF", zorder=4)

    gfr.draw_arrow(ax, 0.120, 0.708, 0.142, 0.708, color="#334155")

    blocks = [("B1", "32 ch"), ("B2", "48 ch"), ("B3", "64 ch"), ("B4", "96 ch"), ("B5", "128 ch")]
    bx0, bw, gap = 0.144, 0.063, 0.016
    for i, (bname, bch) in enumerate(blocks):
        bx = bx0 + i * (bw + gap)
        gfr.draw_box(ax, bx, 0.610, bw, 0.195, f"{bname}\n{bch}", fc="#DBEAFE", ec="#2563EB", fs=11.0)
        if i < len(blocks) - 1:
            gfr.draw_arrow(ax, bx + bw + 0.001, 0.708, bx + bw + gap - 0.001, 0.708, color="#2563EB", lw=1.5)

    head_bg = FancyBboxPatch((0.544, 0.525), 0.438, 0.375,
                             boxstyle="round,pad=0.004,rounding_size=0.012",
                             facecolor="#F0F9FF", edgecolor="#0284C7", linewidth=1.3, linestyle="--", zorder=2)
    ax.add_patch(head_bg)
    ax.text(0.763, 0.888, "Cabeça Original (131,6k + 257k pesos)",
            ha="center", va="top", fontsize=11.2, fontweight="bold", color="#0369A1", zorder=4)

    gfr.draw_box(ax, 0.555, 0.720, 0.080, 0.095, "GAP\n128D", fc="#E0F2FE", ec="#0284C7", fs=10.6)
    gfr.draw_box(ax, 0.555, 0.590, 0.080, 0.095, "GMP\n128D", fc="#E0F2FE", ec="#0284C7", fs=10.6)
    gfr.draw_arrow(ax, 0.530, 0.720, 0.553, 0.768, color="#0284C7")
    gfr.draw_arrow(ax, 0.530, 0.695, 0.553, 0.638, color="#0284C7")

    gfr.draw_box(ax, 0.650, 0.612, 0.076, 0.185, "Concat\n256D", fc="#BAE6FD", ec="#0369A1", fs=10.6)
    gfr.draw_arrow(ax, 0.637, 0.768, 0.648, 0.730, color="#0369A1")
    gfr.draw_arrow(ax, 0.637, 0.638, 0.648, 0.680, color="#0369A1")

    gfr.draw_box(ax, 0.740, 0.612, 0.142, 0.185, "2× [Drop(0,4) →\nDense(256, SiLU)]", fc="#DBEAFE", ec="#1D4ED8", fs=10.4)
    gfr.draw_arrow(ax, 0.728, 0.705, 0.738, 0.705, color="#1D4ED8")

    gfr.draw_box(ax, 0.896, 0.612, 0.078, 0.185, "Drop(0,4)\nDense(K)", fc="#1D4ED8", ec="#1E3A8A", fs=10.6, text_color="#FFFFFF")
    gfr.draw_arrow(ax, 0.884, 0.705, 0.894, 0.705, color="#1D4ED8")

    bot_bg = FancyBboxPatch((0.060, 0.030), 0.880, 0.390,
                            boxstyle="round,pad=0.004,rounding_size=0.012",
                            facecolor="#F8FAFC", edgecolor="#64748B", linewidth=1.2, zorder=1)
    ax.add_patch(bot_bg)
    ax.text(0.500, 0.398, "Estrutura interna de cada Bloco Convolucional (B1 a B5)",
            ha="center", va="top", fontsize=12.4, fontweight="bold", color="#334155", zorder=4)

    ax.plot([0.280, 0.065], [0.522, 0.420], color="#94A3B8", linestyle=":", linewidth=1.5, zorder=1)
    ax.plot([0.380, 0.935], [0.522, 0.420], color="#94A3B8", linestyle=":", linewidth=1.5, zorder=1)

    substeps = [
        ("Entrada\ndo bloco", "#E2E8F0", "#475569"),
        ("SepConv2D\n5×5", "#DBEAFE", "#2563EB"),
        ("GroupNorm(16)\n+ SiLU", "#E0F2FE", "#0284C7"),
        ("SepConv2D\n3×3", "#DBEAFE", "#2563EB"),
        ("GroupNorm(16)\n+ SiLU", "#E0F2FE", "#0284C7"),
        ("MaxPool2D\n2×2", "#FEF3C7", "#D97706"),
    ]
    sx0, sw, sgap = 0.082, 0.122, 0.022
    for i, (stxt, sfc, sec) in enumerate(substeps):
        sx = sx0 + i * (sw + sgap)
        gfr.draw_box(ax, sx, 0.105, sw, 0.215, stxt, fc=sfc, ec=sec, fs=10.8)
        if i < len(substeps) - 1:
            gfr.draw_arrow(ax, sx + sw + 0.002, 0.212, sx + sw + sgap - 0.002, 0.212, color="#475569")

    ax.text(0.500, 0.055, "(passo s=2 no Bloco 1; passo s=1 nos Blocos 2 a 5)",
            ha="center", va="bottom", fontsize=10.5, color="#475569", style="italic")

    out_path = SLIDE_FIG_DIR / "fig_arq_etapa1_cnn_original_slide.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print("Gerado:", out_path.name)


# =====================================================================
# 1B. HEATMAP MACRO-F1 9x8 (SLIDE 37 / ANTIGO 39)
# =====================================================================
def gerar_heatmap_macro_f1_slide() -> None:
    df = pd.read_csv(CSV_FIG26)
    ds_rows = [
        ("MNIST", "MNIST"),
        ("Fashion-MNIST", "Fashion-MNIST"),
        ("KMNIST", "KMNIST"),
        ("EMNIST Balanced", "EMNIST Bal."),
        ("CIFAR-10", "CIFAR-10"),
        ("CIFAR-100 Coarse", "CIFAR-100 C."),
        ("SVHN", "SVHN"),
        ("GTSRB", "GTSRB*"),
        ("FER2013", "FER2013"),
    ]
    model_cols = [
        ("CNN FP32", "CNN"),
        ("Dense20 imagem", "D20 imagem"),
        ("Dense20 vetorial Linux", "Vet Linux"),
        ("Dense20 vetorial Mac", "Vet Mac"),
        ("PQC Windows PennyLane", "Q Win PL"),
        ("PQC Windows Qiskit", "Q Win QK"),
        ("PQC Mac PennyLane", "Q Mac PL"),
        ("PQC Mac Qiskit", "Q Mac QK"),
    ]

    lookup = df.set_index(["dataset", "model_label"])["macro_f1"]
    mat = np.zeros((len(ds_rows), len(model_cols)), dtype=float)
    for i, (ds_key, _) in enumerate(ds_rows):
        for j, (mod_key, _) in enumerate(model_cols):
            mat[i, j] = float(lookup.loc[(ds_key, mod_key)]) * 100.0

    fig, ax = plt.subplots(figsize=(14.0, 6.8), dpi=300)
    im = ax.imshow(mat, cmap="YlGnBu", vmin=0.0, vmax=100.0, aspect="auto")

    for i in range(len(ds_rows)):
        for j in range(len(model_cols)):
            v = mat[i, j]
            txt_col = "#FFFFFF" if v >= 60.0 else "#0F172A"
            ax.text(j, i, fmt_pt(v, 3), ha="center", va="center",
                    fontsize=14.5, fontweight="bold", color=txt_col)

    ax.set_yticks(np.arange(len(ds_rows)))
    ax.set_yticklabels([lbl for _, lbl in ds_rows], fontsize=14.5, fontweight="bold")
    ax.set_xticks(np.arange(len(model_cols)))
    ax.set_xticklabels([lbl for _, lbl in model_cols], fontsize=13.8, fontweight="bold", rotation=22, ha="right")

    cbar = fig.colorbar(im, ax=ax, fraction=0.032, pad=0.025)
    cbar.set_label("Macro-F1 de teste (%)", fontsize=14.5, fontweight="bold", labelpad=10)
    cbar.ax.tick_params(labelsize=13.0)

    out_path = SLIDE_FIG_DIR / "figura_26_comparacao_matriz_slide.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.10, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path.name)


# =====================================================================
# 1B. PAINEIS CAUSAIS DE OCLUSAO COM LETRAS GRANDES (SLIDES 43-44)
# =====================================================================
def gerar_paineis_oclusao_slide() -> None:
    models = (
        ("cnn", "CNN FP32"),
        ("image20", "D20 imagem"),
        ("vector_linux", "Vet Linux"),
        ("vector_mac", "Vet Mac"),
        ("q_windows_pennylane", "Win PL"),
        ("q_windows_qiskit", "Win QK"),
        ("q_mac_pennylane", "Mac PL"),
        ("q_mac_qiskit", "Mac QK"),
    )
    specs = [
        ("gtsrb", "gtsrb_07", "media", "GTSRB · gtsrb_07 · Média", "painel_oclusao_gtsrb_07_media_slide.png"),
        ("cifar100_coarse", "cifar100_coarse_01", "desfoque", "CIFAR-100C · cifar100_01 · Desfoque", "painel_oclusao_cifar100_coarse_01_desfoque_slide.png"),
        ("fashion_mnist", "fashion_mnist_06", "media", "Fashion-MNIST · fashion_06 · Média", "painel_oclusao_fashion_mnist_06_media_slide.png"),
        ("mnist", "mnist_06", "desfoque", "MNIST · mnist_06 · Desfoque", "painel_oclusao_mnist_06_desfoque_slide.png"),
    ]

    for ds, sid, method, sup_txt, out_name in specs:
        am = json.loads((ROOT_GC / "amostras" / ds / "amostras.json").read_text(encoding="utf-8-sig"))
        idx = [i for i, s in enumerate(am["samples"]) if s["sample_id"] == sid][0]
        src_img = np.asarray(np.load(ROOT_GC / "amostras" / ds / "imagens_preprocessadas.npy")[idx], np.float32)
        true_name = str(am["samples"][idx]["class_name"]).replace("_", " ")
        true_disp = f"cl. {true_name}" if true_name.isdigit() else true_name

        fig, axes = plt.subplots(3, 3, figsize=(10.6, 10.8), dpi=240, constrained_layout=True)
        ax0 = axes.flat[0]
        disp0 = src_img[..., 0] if src_img.shape[-1] == 1 else src_img
        ax0.imshow(disp0, cmap="gray" if src_img.shape[-1] == 1 else None,
                   vmin=0 if src_img.shape[-1] == 1 else None, vmax=1 if src_img.shape[-1] == 1 else None)
        ax0.set_xticks([])
        ax0.set_yticks([])
        for sp in ax0.spines.values():
            sp.set_visible(False)
        ax0.set_title(f"Original\nReal: {true_disp}", fontsize=13.5, fontweight="bold", pad=6)

        sel = slice(1, 65) if method == "desfoque" else slice(65, 129)
        for ax, (m_key, m_short) in zip(axes.flat[1:], models):
            d = ROOT_OCL / "resultados" / ds / sid / m_key
            rj = json.loads((d / "resultado.json").read_text(encoding="utf-8-sig"))
            with np.load(d / "valores.npz") as saved:
                md = saved["margin_drop"][sel].reshape(8, 8)
                preds = saved["predicted"][sel]
            flips = int(np.count_nonzero(preds != rj["target_class"]))
            max_drop = float(md.max())

            img_m = src_img.astype(np.float16).astype(np.float32) if m_key == "cnn" else src_img
            disp_m = img_m[..., 0] if img_m.shape[-1] == 1 else img_m
            ax.imshow(disp_m, cmap="gray" if img_m.shape[-1] == 1 else None,
                      vmin=0 if img_m.shape[-1] == 1 else None, vmax=1 if img_m.shape[-1] == 1 else None)
            lim = float(np.max(np.abs(md)))
            lim = lim if lim > 1e-12 else 1.0
            h, w = img_m.shape[:2]
            ax.imshow(md, cmap="coolwarm", vmin=-lim, vmax=lim, alpha=0.72,
                      interpolation="nearest", extent=(-0.5, w - 0.5, h - 0.5, -0.5))
            ax.set_xticks([])
            ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_visible(False)

            pred_raw = str(rj["target_name"]).replace("_", " ")
            pred_disp = f"cl. {pred_raw}" if pred_raw.isdigit() else pred_raw
            drop_sign = "+" if max_drop >= 0 else "−"
            drop_txt = f"{drop_sign}{fmt_pt(abs(max_drop), 2)}"
            ax.set_title(f"{m_short} · {pred_disp}\n{flips}/64 trocas · {drop_txt}",
                         fontsize=12.6, fontweight="bold", pad=5)

        fig.suptitle(sup_txt, fontsize=16.5, fontweight="bold")
        out_path = SLIDE_FIG_DIR / out_name
        fig.savefig(out_path, dpi=240, facecolor="#FFFFFF")
        plt.close(fig)
        print("Gerado:", out_path.name)


# =====================================================================
# 1B. CUSTO E TELEMETRIA (SLIDES 45-49 / ANTIGOS 47-51)
# =====================================================================
def gerar_tempos_etapas_slide(df_runs, df_f26) -> None:
    """Sem CNN b128 fp16 e sem CNN b128 aug2*, com fontes ampliadas para slide."""
    cnn_orig = df_f26[df_f26["model_label"] == "CNN FP32"].set_index("dataset")["training_hours"] * 3600.0
    t_cnn_orig = np.array([float(cnn_orig.loc[d]) for d in gf48.DATASET_ORDER], dtype=float)
    t_d20_img = gf48._s_by_group(df_runs, "Dense20 imagem")
    t_vec_mac = gf48._s_by_group(df_runs, "Dense20 vetorial Mac")
    t_vec_lin = gf48._s_by_group(df_runs, "Dense20 vetorial Linux")
    t_pqc_m_pl = gf48._s_by_group(df_runs, "PQC Mac PennyLane")
    t_pqc_w_pl = gf48._s_by_group(df_runs, "PQC Windows PennyLane")
    t_pqc_m_qk = gf48._s_by_group(df_runs, "PQC Mac Qiskit")
    t_pqc_w_qk = gf48._s_by_group(df_runs, "PQC Windows Qiskit")

    bar_specs = [
        ("CNN FP32", t_cnn_orig.sum() / 3600.0, "#1E293B", ""),
        ("Dense20 imagem", t_d20_img.sum() / 3600.0, "#EA580C", ""),
        ("Vetorial Mac ★", t_vec_mac.sum() / 3600.0, "#0F766E", f"{fmt_pt(t_vec_mac.sum(), 1)} s"),
        ("Vetorial Linux", t_vec_lin.sum() / 3600.0, "#65A30D", f"{fmt_pt(t_vec_lin.sum(), 1)} s"),
        ("PQC Mac PL ★", t_pqc_m_pl.sum() / 3600.0, "#7C3AED", ""),
        ("PQC Win PL", t_pqc_w_pl.sum() / 3600.0, "#2563EB", ""),
        ("PQC Mac QK", t_pqc_m_qk.sum() / 3600.0, "#D97706", ""),
        ("PQC Win QK", t_pqc_w_qk.sum() / 3600.0, "#B91C1C", ""),
    ]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(12.4, 6.4), dpi=300,
        gridspec_kw={"width_ratios": [1.0, 1.16], "wspace": 0.34}
    )

    y_a = np.arange(len(bar_specs))[::-1]
    for yi, (lbl, val_h, col, custom_txt) in zip(y_a, bar_specs):
        ax1.barh(yi, val_h, height=0.64, color=col, edgecolor="#1E293B", linewidth=0.8, alpha=0.94, zorder=3)
        txt = custom_txt if custom_txt else f"{fmt_pt(val_h, 2)} h"
        ax1.text(val_h + 4.5, yi, txt, va="center", ha="left", fontsize=13.5, fontweight="bold", color="#0F172A")

    for sep_y in (6.5, 5.5, 3.5):
        ax1.axhline(sep_y, color="#94A3B8", ls="--", lw=1.1, zorder=2)

    ax1.set_yticks(y_a)
    ax1.set_yticklabels([b[0] for b in bar_specs], fontsize=13.8, fontweight="bold")
    ax1.set_xlim(0, 285)
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 0)))
    ax1.set_xlabel("Tempo acumulado (h)", fontsize=14.2, fontweight="bold")
    ax1.set_title("A. Tempo acumulado por etapa", fontsize=15.8, fontweight="bold", pad=12)
    ax1.tick_params(axis="x", labelsize=12.8)
    ax1.grid(True, axis="x", alpha=0.75)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # Painel B sem CNN b128
    y_b = np.arange(len(gf48.DATASET_ORDER))[::-1]
    series_b = [
        ("Vet. Mac", t_vec_mac, "o", "#0F766E", 0.0),
        ("D20 imagem", t_d20_img, "s", "#EA580C", 0.0),
        ("CNN FP32", t_cnn_orig, "P", "#1E293B", -0.14),
        ("PQC Mac PL", t_pqc_m_pl, "^", "#7C3AED", +0.14),
        ("PQC Win QK", t_pqc_w_qk, "v", "#B91C1C", 0.0),
    ]
    for i, ds in enumerate(gf48.DATASET_ORDER):
        vals_i = [s[1][i] for s in series_b]
        x_row_max = max(vals_i)
        ax2.hlines(y_b[i], min(vals_i), x_row_max, color="#CBD5E1", lw=2.2, zorder=1)
        ax2.text(t_vec_mac[i] * 0.65, y_b[i], f"{fmt_pt(t_vec_mac[i], 1)} s",
                 ha="right", va="center", fontsize=12.0, fontweight="bold", color="#0F766E")
        x_lbl = x_row_max * 1.50
        if t_cnn_orig[i] > t_pqc_w_qk[i]:
            ax2.text(x_lbl, y_b[i] + 0.19, f"{fmt_pt(t_cnn_orig[i] / 3600.0, 2)} h",
                     ha="left", va="center", fontsize=11.6, fontweight="bold", color="#1E293B")
            ax2.text(x_lbl, y_b[i] - 0.19, f"{fmt_pt(t_pqc_w_qk[i] / 3600.0, 2)} h",
                     ha="left", va="center", fontsize=11.6, fontweight="bold", color="#991B1B")
        else:
            ax2.text(x_lbl, y_b[i], f"{fmt_pt(t_pqc_w_qk[i] / 3600.0, 2)} h",
                     ha="left", va="center", fontsize=12.0, fontweight="bold", color="#991B1B")

    for lbl, arr, mk, col, dy in series_b:
        ax2.scatter(arr, y_b + dy, label=lbl, marker=mk, s=90, color=col, edgecolors="#FFFFFF", linewidths=0.9, zorder=4)

    ax2.set_xscale("log")
    ax2.set_xlim(0.7, 2.2e6)
    ax2.set_yticks(y_b)
    ax2.set_yticklabels([gf48.SHORT_NAMES[d] for d in gf48.DATASET_ORDER], fontsize=13.2, fontweight="bold")
    ax2.set_xlabel("Duração por base (s, escala log)", fontsize=14.2, fontweight="bold")
    ax2.set_title("B. Distribuição por dataset", fontsize=15.8, fontweight="bold", pad=12)
    ax2.tick_params(axis="x", labelsize=12.8)
    ax2.grid(True, axis="x", which="major", alpha=0.75)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.48, -0.15), ncol=3, fontsize=12.4, frameon=True, edgecolor="#CBD5E1")

    out_path = SLIDE_FIG_DIR / "fig_48_tempos_etapas_slide.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.12, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path.name)


def gerar_fatores_aceleracao_slide(df_runs) -> None:
    t_m_pl = gf48._s_by_group(df_runs, "PQC Mac PennyLane")
    t_w_pl = gf48._s_by_group(df_runs, "PQC Windows PennyLane")
    t_m_qk = gf48._s_by_group(df_runs, "PQC Mac Qiskit")
    t_w_qk = gf48._s_by_group(df_runs, "PQC Windows Qiskit")

    vals_pl_wm = list(t_w_pl / t_m_pl) + [float(t_w_pl.sum() / t_m_pl.sum())]
    vals_qk_wm = list(t_w_qk / t_m_qk) + [float(t_w_qk.sum() / t_m_qk.sum())]
    vals_win_qp = list(t_w_qk / t_w_pl) + [float(t_w_qk.sum() / t_w_pl.sum())]
    vals_mac_qp = list(t_m_qk / t_m_pl) + [float(t_m_qk.sum() / t_m_pl.sum())]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 6.8), dpi=300, sharey=True,
                                   gridspec_kw={"wspace": 0.14})
    y = np.arange(10)[::-1]
    ds_labels = [gf48.SHORT_NAMES[d] for d in gf48.DATASET_ORDER] + ["Total (9 bases)"]
    h = 0.39

    for ax in (ax1, ax2):
        ax.axhline(0.5, color="#94A3B8", lw=1.2, zorder=1)
        ax.axhspan(-0.5, 0.5, color="#F1F5F9", zorder=0)
        ax.axvline(1.0, color="#0F172A", linestyle="--", linewidth=1.4, zorder=4)
        ax.grid(True, axis="x", alpha=0.75, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelsize=12.8)

    b1 = ax1.barh(y + h / 2, vals_pl_wm, height=h * 0.88, color="#2563EB", label="PennyLane", zorder=3)
    b2 = ax1.barh(y - h / 2, vals_qk_wm, height=h * 0.88, color="#D97706", label="Qiskit", zorder=3)
    for bar, v in zip(b1, vals_pl_wm):
        ax1.text(v + 0.06, bar.get_y() + bar.get_height() / 2, f"{fmt_pt(v, 2)}×",
                 va="center", ha="left", fontsize=12.6, fontweight="bold", color="#1E40AF")
    for bar, v in zip(b2, vals_qk_wm):
        ax1.text(v + 0.06, bar.get_y() + bar.get_height() / 2, f"{fmt_pt(v, 2)}×",
                 va="center", ha="left", fontsize=12.6, fontweight="bold", color="#92400E")

    ax1.set_xlim(0, 4.15)
    ax1.set_yticks(y)
    ax1.set_yticklabels(ds_labels, fontsize=13.8, fontweight="bold")
    ax1.set_xlabel(r"$T_{\mathrm{Win}} / T_{\mathrm{Mac}}$", fontsize=14.5, fontweight="bold")
    ax1.set_title(r"A. Ambientes ($R_{\mathrm{Win/Mac}}$)", fontsize=15.8, fontweight="bold", pad=12)
    ax1.legend(loc="upper center", bbox_to_anchor=(0.50, -0.13), fontsize=13.5, frameon=True, ncol=2, edgecolor="#CBD5E1")

    b3 = ax2.barh(y + h / 2, vals_win_qp, height=h * 0.88, color="#0F766E", label="Windows", zorder=3)
    b4 = ax2.barh(y - h / 2, vals_mac_qp, height=h * 0.88, color="#7C3AED", label="iMac M4", zorder=3)
    for bar, v in zip(b3, vals_win_qp):
        ax2.text(v + 0.06, bar.get_y() + bar.get_height() / 2, f"{fmt_pt(v, 2)}×",
                 va="center", ha="left", fontsize=12.6, fontweight="bold", color="#115E59")
    for bar, v in zip(b4, vals_mac_qp):
        ax2.text(v + 0.06, bar.get_y() + bar.get_height() / 2, f"{fmt_pt(v, 2)}×",
                 va="center", ha="left", fontsize=12.6, fontweight="bold", color="#5B21B6")

    ax2.set_xlim(0, 3.70)
    ax2.set_xlabel(r"$T_{\mathrm{QK}} / T_{\mathrm{PL}}$", fontsize=14.5, fontweight="bold")
    ax2.set_title(r"B. Simuladores ($R_{\mathrm{QK/PL}}$)", fontsize=15.8, fontweight="bold", pad=12)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.50, -0.13), fontsize=13.5, frameon=True, ncol=2, edgecolor="#CBD5E1")

    out_path = SLIDE_FIG_DIR / "fig_fatores_aceleracao_slide.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.12, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path.name)


def gerar_telemetria_hardware_io_slide(df_ses, df_tel, df_mac, df_proj) -> None:
    df_tel = df_tel.copy()
    df_tel["cpu_eff"] = df_tel["cpu_tree"].fillna(df_tel["cpu_process"])
    df_tel["rss_eff"] = df_tel["rss_tree_mib_max"].fillna(df_tel["rss_process_mib_max"])
    run_meta = df_ses.drop_duplicates(subset=["codigo"])[["codigo", "dataset", "ambiente", "grupo"]]
    tel_m = df_tel.merge(run_meta, on="codigo", how="left")

    mac_fam_map = {"Dense20 vetorial Mac": "classico", "PQC Mac PennyLane": "pennylane", "PQC Mac Qiskit": "qiskit"}
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
            "label": lbl, "color": col, "cpu_mean": cpu_mean,
            "rss_mean": rss_mean, "rss_max": rss_abs_max,
            "gpu_mean": gpu_mean, "read_gib": read_gib, "write_gib": write_gib, "mac_comp": mac_comp,
        })

    fig, axes = plt.subplots(2, 2, figsize=(12.2, 8.2), dpi=300, sharey=True,
                             gridspec_kw={"hspace": 0.38, "wspace": 0.14})
    (ax_a, ax_b), (ax_c, ax_d) = axes
    y = np.arange(len(stats))[::-1]
    y_labels = [s["label"] for s in stats]

    for ax in (ax_a, ax_b, ax_c, ax_d):
        ax.axhline(3.5, color="#94A3B8", ls="--", lw=1.1, zorder=1)
        ax.grid(True, axis="x", alpha=0.75, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelsize=12.8)

    cols = [s["color"] for s in stats]
    bars_a = ax_a.barh(y, [s["cpu_mean"] for s in stats], height=0.62, color=cols, alpha=0.93, zorder=3)
    for bar, s in zip(bars_a, stats):
        ax_a.text(s["cpu_mean"] + 8.0, bar.get_y() + bar.get_height() / 2,
                  f"{fmt_pt(s['cpu_mean'], 1)}%", va="center", ha="left", fontsize=12.8, fontweight="bold", color="#0F172A")
    ax_a.set_xlim(0, 515)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(y_labels, fontsize=13.6, fontweight="bold")
    ax_a.set_xlabel("CPU da árvore (%)", fontsize=13.8, fontweight="bold")
    ax_a.set_title("A. Uso médio de CPU", fontsize=15.6, fontweight="bold", pad=10)

    bars_b = ax_b.barh(y, [s["rss_mean"] for s in stats], height=0.60, color=cols, alpha=0.88, zorder=3, label="Média dos picos")
    ax_b.scatter([s["rss_max"] for s in stats], y, marker="D", s=78, color="#0F172A", edgecolors="#FFFFFF", linewidths=0.9, zorder=5, label="Máx. absoluto")
    for bar, s in zip(bars_b, stats):
        ax_b.text(s["rss_max"] + 0.25, bar.get_y() + bar.get_height() / 2,
                  f"{fmt_pt(s['rss_mean'], 2)} / {fmt_pt(s['rss_max'], 2)}",
                  va="center", ha="left", fontsize=12.4, fontweight="bold", color="#0F172A")
    ax_b.set_xlim(0, 12.2)
    ax_b.set_xlabel("RSS: média / máx. (GiB)", fontsize=13.8, fontweight="bold")
    ax_b.set_title("B. Pico de memória (RSS)", fontsize=15.6, fontweight="bold", pad=10)
    ax_b.legend(loc="lower right", fontsize=12.0, frameon=True, edgecolor="#CBD5E1")

    for yi, s in zip(y, stats):
        gv = s["gpu_mean"]
        if s["mac_comp"]:
            ax_c.barh(yi, gv, height=0.60, color=s["color"], edgecolor="#FFFFFF", hatch="///", linewidth=0.8, alpha=0.90, zorder=3)
            txt = f"{fmt_pt(gv, 2)}%*"
        else:
            ax_c.barh(yi, gv, height=0.60, color=s["color"], alpha=0.93, zorder=3)
            txt = f"{fmt_pt(gv, 1)}%"
        ax_c.text(gv + 1.2, yi, txt, va="center", ha="left", fontsize=12.8, fontweight="bold", color="#0F172A")
    ax_c.set_xlim(0, 62)
    ax_c.set_yticks(y)
    ax_c.set_yticklabels(y_labels, fontsize=13.6, fontweight="bold")
    ax_c.set_xlabel("Utilização média (%)", fontsize=13.8, fontweight="bold")
    ax_c.set_title("C. Utilização média de GPU", fontsize=15.6, fontweight="bold", pad=10)
    leg_c = [
        Patch(facecolor="#475569", edgecolor="#1E293B", label="RTX A2000 (100 ép.)"),
        Patch(facecolor="#7C3AED", edgecolor="#FFFFFF", hatch="///", label="Apple AGX (1 ép.)*"),
    ]
    ax_c.legend(handles=leg_c, loc="lower right", fontsize=11.5, frameon=True, edgecolor="#CBD5E1")

    h_io = 0.40
    for yi, s in zip(y, stats):
        r_v, w_v = s["read_gib"], s["write_gib"]
        if s["mac_comp"]:
            ax_d.barh(yi + h_io / 2, r_v, height=h_io * 0.86, color="#0284C7", edgecolor="#FFFFFF", hatch="///", linewidth=0.7, alpha=0.90, zorder=3)
            ax_d.barh(yi - h_io / 2, w_v, height=h_io * 0.86, color="#F97316", edgecolor="#FFFFFF", hatch="///", linewidth=0.7, alpha=0.90, zorder=3)
            if r_v >= 1.0 or w_v >= 1.0:
                ax_d.text(r_v + 4.5, yi + 0.22, f"{fmt_pt(r_v, 2)}*", va="center", ha="left", fontsize=10.8, fontweight="bold", color="#0369A1")
                ax_d.text(w_v + 4.5, yi - 0.22, f"{fmt_pt(w_v, 2)}*", va="center", ha="left", fontsize=10.8, fontweight="bold", color="#C2410C")
            else:
                ax_d.text(max(r_v, w_v) + 4.5, yi, f"{fmt_pt(r_v, 3)} / {fmt_pt(w_v, 2)}*", va="center", ha="left", fontsize=11.0, fontweight="bold", color="#334155")
        else:
            ax_d.barh(yi + h_io / 2, r_v, height=h_io * 0.86, color="#0284C7", zorder=3)
            ax_d.barh(yi - h_io / 2, w_v, height=h_io * 0.86, color="#F97316", zorder=3)
            if r_v >= 1.0 or w_v >= 1.0:
                ax_d.text(r_v + 4.5, yi + 0.22, f"{fmt_pt(r_v, 1)}", va="center", ha="left", fontsize=11.0, fontweight="bold", color="#0369A1")
                ax_d.text(w_v + 4.5, yi - 0.22, f"{fmt_pt(w_v, 1)}" if w_v >= 0.1 else "0,02", va="center", ha="left", fontsize=11.0, fontweight="bold", color="#C2410C")
            else:
                ax_d.text(max(r_v, w_v) + 4.5, yi, f"{fmt_pt(r_v, 2)} / {fmt_pt(w_v, 2)}", va="center", ha="left", fontsize=11.0, fontweight="bold", color="#334155")
    ax_d.set_xlim(0, 305)
    ax_d.set_xlabel("I/O acumulado 100 ép. (GiB)", fontsize=13.8, fontweight="bold")
    ax_d.set_title("D. Disco (processo principal)", fontsize=15.6, fontweight="bold", pad=10)
    leg_d = [
        Patch(facecolor="#0284C7", label="Leitura"),
        Patch(facecolor="#F97316", label="Escrita"),
        Patch(facecolor="#64748B", edgecolor="#FFFFFF", hatch="///", label="Proj. Mac*"),
    ]
    ax_d.legend(handles=leg_d, loc="upper right", bbox_to_anchor=(0.99, 0.99), fontsize=11.8, frameon=True, edgecolor="#CBD5E1")

    out_path = SLIDE_FIG_DIR / "fig_48_telemetria_hardware_io_slide.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.12, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path.name)


def gerar_mac_sensores_macmon_slide(df_mac, df_proj) -> None:
    pl_m = df_mac[df_mac["familia"] == "pennylane"].set_index("nome")
    qk_m = df_mac[df_mac["familia"] == "qiskit"].set_index("nome")
    cl_m = df_mac[(df_mac["familia"] == "classico") & (df_mac["n_macmon_treino"] > 0)]
    turbo_ghz = float(cl_m["pcpu_freq_mhz_medio"].mean() / 1000.0)
    pl_p = df_proj[df_proj["familia"] == "pennylane"].set_index("nome")
    qk_p = df_proj[df_proj["familia"] == "qiskit"].set_index("nome")

    p_pl = np.array([float(pl_m.loc[d, "cpu_power_medio"]) for d in gf48.DATASET_ORDER])
    p_qk = np.array([float(qk_m.loc[d, "cpu_power_medio"]) for d in gf48.DATASET_ORDER])
    t_pl = np.array([float(pl_m.loc[d, "cpu_temp_media_c"]) for d in gf48.DATASET_ORDER])
    t_qk = np.array([float(qk_m.loc[d, "cpu_temp_media_c"]) for d in gf48.DATASET_ORDER])
    f_pl = np.array([float(pl_m.loc[d, "pcpu_freq_mhz_medio"]) / 1000.0 for d in gf48.DATASET_ORDER])
    f_qk = np.array([float(qk_m.loc[d, "pcpu_freq_mhz_medio"]) / 1000.0 for d in gf48.DATASET_ORDER])
    e_pl = np.array([float(pl_p.loc[d, "energia_cpu_global_100_treinos_wh"]) for d in gf48.DATASET_ORDER])
    e_qk = np.array([float(qk_p.loc[d, "energia_cpu_global_100_treinos_wh"]) for d in gf48.DATASET_ORDER])

    fig, axes = plt.subplots(2, 2, figsize=(12.2, 8.8), dpi=300, sharey=True,
                             gridspec_kw={"hspace": 0.38, "wspace": 0.14})
    (ax_a, ax_b), (ax_c, ax_d) = axes
    y = np.arange(len(gf48.DATASET_ORDER))[::-1]
    ds_labels = [gf48.SHORT_NAMES[d] for d in gf48.DATASET_ORDER]
    h = 0.40

    for ax in (ax_a, ax_b, ax_c, ax_d):
        ax.grid(True, axis="x", alpha=0.75, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="x", labelsize=12.8)

    b1 = ax_a.barh(y + h / 2, p_pl, height=h * 0.84, color="#7C3AED", label="PennyLane", zorder=3)
    b2 = ax_a.barh(y - h / 2, p_qk, height=h * 0.84, color="#D97706", label="Qiskit", zorder=3)
    for bar, v in zip(b1, p_pl):
        ax_a.text(v + 0.35, bar.get_y() + bar.get_height() / 2 + 0.03, f"{fmt_pt(v, 1)}", va="center", ha="left", fontsize=11.6, fontweight="bold", color="#5B21B6")
    for bar, v in zip(b2, p_qk):
        ax_a.text(v + 0.35, bar.get_y() + bar.get_height() / 2 - 0.03, f"{fmt_pt(v, 1)}", va="center", ha="left", fontsize=11.6, fontweight="bold", color="#92400E")
    ax_a.set_xlim(0, 23.0)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels(ds_labels, fontsize=13.4, fontweight="bold")
    ax_a.set_xlabel("Potência da CPU (W)", fontsize=13.8, fontweight="bold")
    ax_a.set_title("A. Potência média da CPU", fontsize=15.4, fontweight="bold", pad=10)

    b3 = ax_b.barh(y + h / 2, t_pl, height=h * 0.84, color="#7C3AED", zorder=3)
    b4 = ax_b.barh(y - h / 2, t_qk, height=h * 0.84, color="#D97706", zorder=3)
    for bar, v in zip(b3, t_pl):
        ax_b.text(v + 1.4, bar.get_y() + bar.get_height() / 2 + 0.03, f"{fmt_pt(v, 1)}", va="center", ha="left", fontsize=11.6, fontweight="bold", color="#5B21B6")
    for bar, v in zip(b4, t_qk):
        ax_b.text(v + 1.4, bar.get_y() + bar.get_height() / 2 - 0.03, f"{fmt_pt(v, 1)}", va="center", ha="left", fontsize=11.6, fontweight="bold", color="#92400E")
    ax_b.set_xlim(0, 112)
    ax_b.set_xlabel("Temperatura da CPU (°C)", fontsize=13.8, fontweight="bold")
    ax_b.set_title("B. Temperatura média da CPU", fontsize=15.4, fontweight="bold", pad=10)

    b5 = ax_c.barh(y + h / 2, f_pl, height=h * 0.84, color="#7C3AED", zorder=3)
    b6 = ax_c.barh(y - h / 2, f_qk, height=h * 0.84, color="#D97706", zorder=3)
    ax_c.axvline(turbo_ghz, color="#0F766E", ls="--", lw=1.5, zorder=4)
    ax_c.text(turbo_ghz + 0.06, 8.35, f"{fmt_pt(turbo_ghz, 2)} GHz", va="center", ha="left", fontsize=11.8, fontweight="bold", color="#0F766E")
    for bar, v in zip(b5, f_pl):
        ax_c.text(v + 0.08, bar.get_y() + bar.get_height() / 2 + 0.03, f"{fmt_pt(v, 2)}", va="center", ha="left", fontsize=11.6, fontweight="bold", color="#5B21B6")
    for bar, v in zip(b6, f_qk):
        ax_c.text(v + 0.08, bar.get_y() + bar.get_height() / 2 - 0.03, f"{fmt_pt(v, 2)}", va="center", ha="left", fontsize=11.6, fontweight="bold", color="#92400E")
    ax_c.set_xlim(0, 5.75)
    ax_c.set_yticks(y)
    ax_c.set_yticklabels(ds_labels, fontsize=13.4, fontweight="bold")
    ax_c.set_xlabel("Frequência P-cores (GHz)", fontsize=13.8, fontweight="bold")
    ax_c.set_title("C. Frequência dos núcleos P", fontsize=15.4, fontweight="bold", pad=10)

    b7 = ax_d.barh(y + h / 2, e_pl, height=h * 0.84, color="#7C3AED", edgecolor="#FFFFFF", hatch="///", alpha=0.90, zorder=3)
    b8 = ax_d.barh(y - h / 2, e_qk, height=h * 0.84, color="#D97706", edgecolor="#FFFFFF", hatch="///", alpha=0.90, zorder=3)
    for bar, v in zip(b7, e_pl):
        ax_d.text(v + 8.0, bar.get_y() + bar.get_height() / 2 + 0.03, f"{fmt_pt(v, 0)}", va="center", ha="left", fontsize=11.8, fontweight="bold", color="#5B21B6")
    for bar, v in zip(b8, e_qk):
        ax_d.text(v + 8.0, bar.get_y() + bar.get_height() / 2 - 0.03, f"{fmt_pt(v, 0)}", va="center", ha="left", fontsize=11.8, fontweight="bold", color="#92400E")
    ax_d.set_xlim(0, 600)
    ax_d.set_xlabel("Energia estimada (Wh)*", fontsize=13.8, fontweight="bold")
    ax_d.set_title("D. Energia CPU — proj. 100 ép.*", fontsize=15.4, fontweight="bold", pad=10)

    handles, leg_labels = ax_a.get_legend_handles_labels()
    fig.legend(handles, leg_labels, loc="upper center", bbox_to_anchor=(0.52, 0.99),
               ncol=2, fontsize=14.4, frameon=True, edgecolor="#CBD5E1")
    fig.subplots_adjust(top=0.89)

    out_path = SLIDE_FIG_DIR / "fig_48_mac_hardware_sensores_macmon_slide.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.12, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path.name)


def gerar_mac_io_complementar_slide(df_mac) -> None:
    fams = [("classico", "Clássico", "#0F766E"), ("pennylane", "PennyLane", "#7C3AED"), ("qiskit", "Qiskit", "#D97706")]
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

    fig, axes = plt.subplots(2, 2, figsize=(11.6, 7.4), dpi=300,
                             gridspec_kw={"hspace": 0.40, "wspace": 0.26})
    (ax_a, ax_b), (ax_c, ax_d) = axes

    for ax in (ax_a, ax_b, ax_c, ax_d):
        ax.grid(True, axis="y", alpha=0.75, zorder=1)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=14.0, fontweight="bold")
        ax.tick_params(axis="y", labelsize=13.0)

    bars_a = ax_a.bar(x, cpu_w, width=0.54, color=colors, edgecolor="#1E293B", linewidth=0.8, alpha=0.93, zorder=3)
    for bar, v in zip(bars_a, cpu_w):
        ax_a.text(bar.get_x() + bar.get_width() / 2, v + 12, f"{fmt_pt(v, 1)}%", ha="center", va="bottom", fontsize=13.6, fontweight="bold", color="#0F172A")
    ax_a.set_ylim(0, 480)
    ax_a.set_ylabel("CPU da árvore (%)", fontsize=14.0, fontweight="bold")
    ax_a.set_title("A. Uso médio de CPU", fontsize=15.8, fontweight="bold", pad=10)

    bars_b = ax_b.bar(x, rss_mean, width=0.54, color=colors, edgecolor="#1E293B", linewidth=0.8, alpha=0.88, zorder=3, label="Média")
    ax_b.scatter(x, rss_max, marker="D", s=90, color="#0F172A", edgecolors="#FFFFFF", linewidths=0.9, zorder=5, label="Máx.")
    for bar, m_v, mx_v in zip(bars_b, rss_mean, rss_max):
        ax_b.text(bar.get_x() + bar.get_width() / 2, mx_v + 0.13, f"{fmt_pt(m_v, 2)} / {fmt_pt(mx_v, 2)}", ha="center", va="bottom", fontsize=13.0, fontweight="bold", color="#0F172A")
    ax_b.set_ylim(0, 3.6)
    ax_b.set_ylabel("RSS (GiB)", fontsize=14.0, fontweight="bold")
    ax_b.set_title("B. Pico de memória (RSS)", fontsize=15.8, fontweight="bold", pad=10)
    ax_b.legend(loc="upper center", ncol=2, fontsize=12.6, frameon=True, edgecolor="#CBD5E1")

    bars_c = ax_c.bar(x, gpu_w, width=0.54, color=colors, edgecolor="#1E293B", linewidth=0.8, alpha=0.93, zorder=3)
    for bar, v in zip(bars_c, gpu_w):
        ax_c.text(bar.get_x() + bar.get_width() / 2, v + 0.14, f"{fmt_pt(v, 2)}%", ha="center", va="bottom", fontsize=13.6, fontweight="bold", color="#0F172A")
    ax_c.set_ylim(0, 5.0)
    ax_c.set_ylabel("GPU AGX global (%)", fontsize=14.0, fontweight="bold")
    ax_c.set_title("C. GPU Apple AGX", fontsize=15.8, fontweight="bold", pad=10)

    w_bar = 0.36
    b_r = ax_d.bar(x - w_bar / 2 - 0.02, io_r, width=w_bar, color="#0284C7", edgecolor="#1E293B", linewidth=0.7, label="Leitura", zorder=3)
    b_w = ax_d.bar(x + w_bar / 2 + 0.02, io_w, width=w_bar, color="#F97316", edgecolor="#1E293B", linewidth=0.7, label="Escrita", zorder=3)
    for bar, v in zip(b_r, io_r):
        txt = f"{fmt_pt(v, 2)}" if v < 1.0 else f"{fmt_pt(v, 1)}"
        ax_d.text(bar.get_x() + bar.get_width() / 2, v + 2.5, txt, ha="center", va="bottom", fontsize=12.0, fontweight="bold", color="#0369A1")
    for bar, v in zip(b_w, io_w):
        ax_d.text(bar.get_x() + bar.get_width() / 2, v + 2.5, f"{fmt_pt(v, 1)}", ha="center", va="bottom", fontsize=12.0, fontweight="bold", color="#C2410C")
    ax_d.set_ylim(0, 115)
    ax_d.set_ylabel("I/O em 9 sessões (MiB)", fontsize=14.0, fontweight="bold")
    ax_d.set_title("D. Disco (processo principal)", fontsize=15.8, fontweight="bold", pad=10)
    ax_d.legend(loc="upper left", fontsize=12.6, frameon=True, edgecolor="#CBD5E1")

    out_path = SLIDE_FIG_DIR / "fig_48_mac_hardware_io_complementar_slide.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.12, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path.name)


def gerar_tempo_100ep_vs_melhor_epoca_slide(df_be: pd.DataFrame) -> None:
    """Versao otimizada para slides (fontes ampliadas) de fig_48_tempo_100ep_vs_melhor_epoca.png."""
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
        1, 2, figsize=(13.8, 5.75), dpi=300,
        gridspec_kw={"width_ratios": [1.05, 1.15], "wspace": 0.25}
    )

    y_a = np.arange(len(order_stages))[::-1]
    for yi, (mk, lbl, col) in zip(y_a, order_stages):
        sub = df_be[df_be["model_key"] == mk]
        best_s = float(sub["best_s"].sum())
        tot_s = float(sub["tot_s"].sum())
        best_h = best_s / 3600.0
        tot_h = tot_s / 3600.0
        p15_h = float(sub["p15_s"].sum()) / 3600.0
        saved_pct = (1.0 - best_s / tot_s) * 100.0

        ax1.barh(yi, best_h, height=0.64, color=col, edgecolor="#1E293B", linewidth=0.9, alpha=0.94, zorder=3)
        ax1.barh(yi, tot_h - best_h, left=best_h, height=0.64, color="#E2E8F0",
                 edgecolor=col, hatch="///", linewidth=0.9, alpha=0.90, zorder=3)
        ax1.scatter([p15_h], [yi], marker="D", s=74, color="#0F172A",
                    edgecolors="#FFFFFF", linewidths=1.0, zorder=5)

        if mk in ("vector_linux", "vector_mac"):
            txt = f"{fmt_pt(best_s, 1)} / {fmt_pt(tot_s, 1)} s (−{fmt_pt(saved_pct, 0)}%)"
            x_txt = tot_h + 8.5
        else:
            txt = f"{fmt_pt(best_h, 1)} / {fmt_pt(tot_h, 1)} h (−{fmt_pt(saved_pct, 0)}%)"
            x_txt = tot_h + 6.5
        ax1.text(x_txt, yi, txt, va="center", ha="left", fontsize=12.0, fontweight="bold", color="#0F172A")

    ax1.axhline(3.5, color="#94A3B8", ls="--", lw=1.1, zorder=2)
    ax1.set_yticks(y_a)
    ax1.set_yticklabels([s[1] for s in order_stages], fontsize=13.2, fontweight="bold")
    ax1.set_xlim(0, 355)
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt_pt(v, 0)))
    ax1.set_xlabel("Tempo acumulado nas 9 bases (h)", fontsize=13.0, fontweight="bold")
    ax1.set_title("A. Tempo: best.keras vs. 100 épocas", fontsize=15.0, fontweight="bold", pad=12)
    ax1.tick_params(axis="x", labelsize=12.0)
    ax1.grid(True, axis="x", alpha=0.75)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    leg_a = [
        Patch(facecolor="#475569", edgecolor="#1E293B", label="Até best.keras"),
        Patch(facecolor="#E2E8F0", edgecolor="#475569", hatch="///", label="Pós-melhor época (até 100)"),
        Line2D([0], [0], marker="D", color="w", markerfacecolor="#0F172A", markeredgecolor="#FFFFFF",
               markersize=9, label="Simulação patience=15"),
    ]
    ax1.legend(handles=leg_a, loc="upper center", bbox_to_anchor=(0.48, -0.15),
               ncol=2, fontsize=11.2, frameon=True, edgecolor="#CBD5E1")

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
    mat = np.zeros((len(gf48.DATASET_ORDER), len(heat_cols)), dtype=float)
    annots = [["" for _ in heat_cols] for _ in gf48.DATASET_ORDER]
    lookup = df_be.set_index(["dataset", "model_key"])

    for i, ds in enumerate(gf48.DATASET_ORDER):
        for j, (mk, _) in enumerate(heat_cols):
            row = lookup.loc[(ds, mk)]
            ep = int(row["melhor_epoca"])
            mat[i, j] = ep
            annots[i][j] = f"{ep}†" if bool(row["antes_plato"]) else f"{ep}"

    im = ax2.imshow(mat, cmap="YlGnBu", vmin=1, vmax=100, aspect="auto")
    for i in range(len(gf48.DATASET_ORDER)):
        for j in range(len(heat_cols)):
            val = mat[i, j]
            txt_col = "#FFFFFF" if val >= 55 else "#0F172A"
            ax2.text(j, i, annots[i][j], ha="center", va="center",
                     fontsize=12.0, fontweight="bold", color=txt_col)

    ax2.set_xticks(np.arange(len(heat_cols)))
    ax2.set_xticklabels([c[1] for c in heat_cols], fontsize=12.2, fontweight="bold", rotation=30, ha="right")
    ax2.set_yticks(np.arange(len(gf48.DATASET_ORDER)))
    ax2.set_yticklabels([gf48.SHORT_NAMES[d] for d in gf48.DATASET_ORDER], fontsize=12.6, fontweight="bold")
    ax2.set_xticks(np.arange(-0.5, len(heat_cols), 1), minor=True)
    ax2.set_yticks(np.arange(-0.5, len(gf48.DATASET_ORDER), 1), minor=True)
    ax2.grid(which="minor", color="#FFFFFF", linestyle="-", linewidth=1.8)
    ax2.tick_params(which="minor", bottom=False, left=False)
    ax2.axvline(3.5, color="#0F172A", linewidth=2.0, zorder=4)
    ax2.set_title("B. Melhor época por base e etapa", fontsize=15.0, fontweight="bold", pad=12)
    ax2.set_xlabel("† Melhor época anterior ao platô de treino", fontsize=11.6, fontweight="bold", labelpad=8)

    cbar = fig.colorbar(im, ax=ax2, fraction=0.046, pad=0.03)
    cbar.set_label("Época de seleção (1–100)", fontsize=12.2, fontweight="bold")
    cbar.ax.tick_params(labelsize=11.4)

    out_path = SLIDE_FIG_DIR / "fig_48_tempo_100ep_vs_melhor_epoca_slide.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.12, facecolor="#FFFFFF")
    plt.close(fig)
    print("Gerado:", out_path.name)


def main() -> None:
    crop_all_gifs()
    gerar_metricas_slide()
    gerar_augmentations_e_flip_slide()
    gerar_equilibrio_horizontal_slide()
    gerar_balanceamento_slide()
    gerar_diagrama_etapa1_slide()
    gerar_heatmap_macro_f1_slide()
    gerar_paineis_oclusao_slide()

    df_runs, df_ses, df_tel, df_f26 = gf48.carregar_dados_consolidados()
    df_mac, df_proj, _ = gf48.carregar_dados_mac_completos()
    df_be, _ = gf48.carregar_dados_melhor_epoca(df_f26)
    gerar_tempos_etapas_slide(df_runs, df_f26)
    gerar_fatores_aceleracao_slide(df_runs)
    gerar_telemetria_hardware_io_slide(df_ses, df_tel, df_mac, df_proj)
    gerar_mac_sensores_macmon_slide(df_mac, df_proj)
    gerar_mac_io_complementar_slide(df_mac)
    gerar_tempo_100ep_vs_melhor_epoca_slide(df_be)
    print("Todas as figuras e GIFs otimizados para slides foram gerados com sucesso!")


if __name__ == "__main__":
    main()
