# -*- coding: utf-8 -*-
"""Gera figuras limpas (sem excesso de texto interno, caixas sobrepostas ou rotulos legados) em 300 DPI."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

PROJ_ROOT = Path(r"C:\Users\matheus.sduda\repos\projeto-TCC")
SRC_ROOT = PROJ_ROOT / "src"
VIS_ROOT = PROJ_ROOT / "reports" / "visualizacoes-augmentation-feature-maps"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(VIS_ROOT) not in sys.path:
    sys.path.insert(0, str(VIS_ROOT))

import tensorflow as tf
import gerar_visualizacoes as gv

OUT_DIR = Path(r"C:\Users\matheus.sduda\repos\TCC\TCC_Senac\figuras")
OUT_DIR.mkdir(parents=True, exist_ok=True)
FEATURES_ROOT = PROJ_ROOT / "outputs" / "classic-dense20"

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


def fmt_pt(val: float, decimals: int = 2) -> str:
    return f"{val:.{decimals}f}".replace(".", ",")


def gerar_metricas_classificacao():
    """Substitui o rascunho legado sem acentos por um exemplo generico limpo em 2x2."""
    cm = np.array([
        [42, 5, 3],
        [4, 31, 9],
        [2, 6, 38],
    ])
    classes = ["Classe 0", "Classe 1", "Classe 2"]

    tp = np.diag(cm).astype(float)
    fn = (cm.sum(axis=1) - tp).astype(float)
    fp = (cm.sum(axis=0) - tp).astype(float)
    prec = tp / (tp + fp) * 100.0
    rec = tp / (tp + fn) * 100.0
    f1 = 2 * prec * rec / (prec + rec)
    macro_f1 = float(np.mean(f1))

    # Foco um-contra-todos na Classe 2 (indice 2)
    tp2 = int(tp[2])
    fn2 = int(fn[2])
    fp2 = int(fp[2])
    tn2 = int(cm.sum() - tp2 - fn2 - fp2)

    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.2), dpi=300,
                             gridspec_kw={"hspace": 0.34, "wspace": 0.28})
    ax_cm, ax_ovr, ax_bar, ax_roc = axes.ravel()

    # A. Matriz de confusao 3x3
    im = ax_cm.imshow(cm, cmap="Blues", vmin=0, vmax=45)
    cbar = fig.colorbar(im, ax=ax_cm, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=8.5)
    ax_cm.set_xticks(np.arange(3))
    ax_cm.set_yticks(np.arange(3))
    ax_cm.set_xticklabels(classes, fontsize=9.5, fontweight="bold")
    ax_cm.set_yticklabels(classes, fontsize=9.5, fontweight="bold")
    ax_cm.set_xlabel("Classe prevista", fontsize=10.0, fontweight="bold")
    ax_cm.set_ylabel("Classe real", fontsize=10.0, fontweight="bold")
    ax_cm.set_title("A. Matriz de confusão (exemplo 3 classes)", fontsize=11.0, fontweight="bold", pad=10)
    for i in range(3):
        for j in range(3):
            v = int(cm[i, j])
            ax_cm.text(j, i, str(v), ha="center", va="center", fontsize=12.0, fontweight="bold",
                       color="#FFFFFF" if v >= 26 else "#0F172A")

    # B. Decomposicao um contra todos para a Classe 2
    ax_ovr.set_xlim(0.0, 1.0)
    ax_ovr.set_ylim(0.0, 1.0)
    ax_ovr.axis("off")
    ax_ovr.set_title("B. Decomposição um contra todos (Classe 2)", fontsize=11.0, fontweight="bold", pad=10)

    ax_ovr.text(0.41, 0.88, "Prev.: Classe 2", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1E293B")
    ax_ovr.text(0.77, 0.88, "Prev.: Outras", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1E293B")
    ax_ovr.text(0.11, 0.62, "Real:\nClasse 2", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1E293B")
    ax_ovr.text(0.11, 0.26, "Real:\nOutras", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1E293B")

    cells = [
        (0.25, 0.46, 0.32, 0.32, f"TP = {tp2}\nAcerto Classe 2", "#DCFCE7", "#15803D", "#14532D"),
        (0.61, 0.46, 0.32, 0.32, f"FN = {fn2}\nOmissão Classe 2", "#FEE2E2", "#DC2626", "#7F1D1D"),
        (0.25, 0.10, 0.32, 0.32, f"FP = {fp2}\nFalso alarme", "#FEF3C7", "#D97706", "#78350F"),
        (0.61, 0.10, 0.32, 0.32, f"TN = {tn2}\nOutras corretas", "#E0F2FE", "#0284C7", "#0C4A6E"),
    ]
    for x, y, w, h, txt, fc, ec, tc in cells:
        patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.03",
                               facecolor=fc, edgecolor=ec, linewidth=1.6)
        ax_ovr.add_patch(patch)
        ax_ovr.text(x + w / 2.0, y + h / 2.0, txt, ha="center", va="center",
                    fontsize=9.6, fontweight="bold", color=tc, linespacing=1.35)

    # C. Barras agrupadas de Precisao, Revocacao e F1 + Macro-F1
    x = np.arange(3)
    bw = 0.24
    b1 = ax_bar.bar(x - bw, prec, width=bw * 0.92, color="#1D4ED8", label="Precisão", zorder=3)
    b2 = ax_bar.bar(x, rec, width=bw * 0.92, color="#0F766E", label="Revocação", zorder=3)
    b3 = ax_bar.bar(x + bw, f1, width=bw * 0.92, color="#D97706", label="F1-score", zorder=3)
    ax_bar.axhline(macro_f1, color="#DC2626", linestyle="--", linewidth=1.6,
                   label=f"Macro-F1 = {fmt_pt(macro_f1, 1)}%", zorder=3.5)

    for bars, col in ((b1, "#1E40AF"), (b2, "#115E59"), (b3, "#92400E")):
        for bar in bars:
            v = bar.get_height()
            ax_bar.text(bar.get_x() + bar.get_width() / 2.0, v + 1.8, fmt_pt(v, 1),
                        ha="center", va="bottom", fontsize=8.2, fontweight="bold", color=col, zorder=6,
                        bbox=dict(boxstyle="square,pad=0.05", facecolor="#FFFFFF", edgecolor="none", alpha=0.88))

    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(classes, fontsize=9.5, fontweight="bold")
    ax_bar.set_ylim(0, 118)
    ax_bar.set_yticks([0, 20, 40, 60, 80, 100])
    ax_bar.set_ylabel("Valor (%)", fontsize=10.0, fontweight="bold")
    ax_bar.set_title("C. Métricas por classe e Macro-F1", fontsize=11.0, fontweight="bold", pad=10)
    ax_bar.grid(True, axis="y", alpha=0.8)
    ax_bar.legend(loc="upper right", fontsize=8.2, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1", ncol=2)
    ax_bar.spines["top"].set_visible(False)
    ax_bar.spines["right"].set_visible(False)

    # D. Curva ROC / AUC um contra todos
    fpr = np.array([0.0, 0.06, 0.12, 0.22, 0.36, 0.56, 0.78, 1.0])
    tpr = np.array([0.0, 0.34, 0.54, 0.72, 0.84, 0.92, 0.97, 1.0])
    auc_val = float(np.trapezoid(tpr, fpr)) if hasattr(np, "trapezoid") else float(np.trapz(tpr, fpr))
    ax_roc.plot(fpr, tpr, color="#1D4ED8", linewidth=2.4, label=f"Curva ROC (AUC = {fmt_pt(auc_val, 2)})", zorder=4)
    ax_roc.fill_between(fpr, tpr, 0, color="#DBEAFE", alpha=0.55, zorder=2)
    ax_roc.plot([0, 1], [0, 1], color="#64748B", linestyle="--", linewidth=1.4, label="Classificador ao acaso (0,50)", zorder=3)
    ax_roc.text(0.58, 0.34, f"Área sob a curva\nAUC = {fmt_pt(auc_val, 2)}",
                ha="center", va="center", fontsize=9.8, fontweight="bold", color="#1E3A8A")
    ax_roc.set_xlim(-0.02, 1.02)
    ax_roc.set_ylim(-0.02, 1.04)
    ax_roc.set_xlabel("Taxa de falsos positivos (FPR)", fontsize=10.0, fontweight="bold")
    ax_roc.set_ylabel("Taxa de verdadeiros positivos (TPR)", fontsize=10.0, fontweight="bold")
    ax_roc.set_title("D. Curva ROC / AUC (um contra todos)", fontsize=11.0, fontweight="bold", pad=10)
    ax_roc.grid(True, alpha=0.8)
    ax_roc.legend(loc="lower right", fontsize=8.6, frameon=True)
    ax_roc.spines["top"].set_visible(False)
    ax_roc.spines["right"].set_visible(False)

    out_path = OUT_DIR / "metricas_classificacao_exemplos.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_equilibrio_9_datasets():
    """Regenera equilibrio_classes_9_datasets.png sem caixas flutuantes sobrepostas as barras."""
    specs = [
        ("mnist", "MNIST"),
        ("fashion_mnist", "Fashion-MNIST"),
        ("kmnist", "KMNIST"),
        ("emnist_balanced", "EMNIST Balanced"),
        ("cifar10", "CIFAR-10"),
        ("cifar100_coarse", "CIFAR-100 Coarse"),
        ("svhn", "SVHN"),
        ("gtsrb", "GTSRB"),
        ("fer2013", "FER2013"),
    ]
    fer_names = ["0:Raiva", "1:Desg.", "2:Medo", "3:Feliz", "4:Triste", "5:Surpr.", "6:Neutro"]

    fig = plt.figure(figsize=(14.4, 17.5), dpi=300)
    gs = fig.add_gridspec(5, 2, hspace=0.38, wspace=0.18, top=0.95, bottom=0.05, left=0.07, right=0.97)

    c_train = "#1E5AA8"
    c_val = "#5B9BD5"
    c_test = "#A5C8E4"

    axes = []
    for idx, (ds, label) in enumerate(specs):
        r, c = divmod(idx, 2)
        if idx < 8:
            ax = fig.add_subplot(gs[r, c])
        else:
            # Ultimo painel centralizado na linha inferior
            sub_gs = gs[4, :].subgridspec(1, 3, width_ratios=[0.5, 1.4, 0.5])
            ax = fig.add_subplot(sub_gs[0, 1])
        axes.append(ax)

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
        ax.axhline(mean_v, color="#B91C1C", linestyle="--", linewidth=1.35,
                   label="Média uniforme (N / K)" if idx == 0 else None, zorder=4)

        ax.set_title(f"{label} (K={K} | IR={fmt_pt(ir, 2)}×)", fontsize=11.0, fontweight="bold", pad=7)
        ax.set_ylim(0, tot.max() * 1.15)
        ax.grid(True, axis="y", alpha=0.6)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.set_major_formatter(lambda val, pos: f"{int(val):,}".replace(",", "."))

        if ds == "fer2013":
            ax.set_xticks(x)
            ax.set_xticklabels(fer_names, fontsize=9.0, rotation=22, ha="right")
        elif K <= 10:
            ax.set_xticks(x)
            ax.set_xticklabels([str(i) for i in x], fontsize=9.0)
        elif K == 20:
            ax.set_xticks(np.arange(0, 20, 2))
        else:
            ax.set_xticks(np.arange(0, K, 5))

        if c == 0 or ds == "fer2013":
            ax.set_ylabel("Amostras por classe", fontsize=9.8, fontweight="bold")
        if idx >= 6:
            ax.set_xlabel("Índice / categoria da classe", fontsize=9.6, fontweight="bold")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.52, 0.992),
               ncol=4, fontsize=10.5, frameon=True, facecolor="#FFFFFF", edgecolor="#CBD5E1")

    out_path = OUT_DIR / "equilibrio_classes_9_datasets.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.10)
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_aug_pipeline_limpo(sample: dict, filename: str, base_seed: int = 42):
    cfg = gv.AugmentationConfig(flip_lr=False)
    img = sample["tensor"]
    example_index = gv.find_rich_aug_index(img, cfg, base_seed=base_seed)
    steps = gv.isolated_step_outputs(img, cfg, base_seed=base_seed, example_index=example_index)
    orig = steps[0][2]

    fig = plt.figure(figsize=(18.5, 5.2), dpi=260)
    gs = fig.add_gridspec(
        2, 9,
        width_ratios=[1, 1, 1, 1, 1, 1, 1, 1, 0.08],
        left=0.045, right=0.945, top=0.90, bottom=0.09, wspace=0.15, hspace=0.22,
    )

    diff_vmax = 0.12
    im_diff = None
    short_titles = [
        "Original",
        "1. Translação",
        "2. Zoom",
        "3. Brilho",
        "4. Contraste",
        "5. Ruído",
        "6. Cutout",
        "7. Composto",
    ]
    for col, (stitle, (_, param_txt, arr)) in enumerate(zip(short_titles, steps)):
        ax_top = fig.add_subplot(gs[0, col])
        gv.imshow_image(ax_top, arr)
        ax_top.set_title(stitle, fontsize=10.0, fontweight="bold", pad=5)
        ax_top.set_xlabel(param_txt, fontsize=8.2, color="#475569", labelpad=3)

        ax_bot = fig.add_subplot(gs[1, col])
        dmap = gv.rms_diff_map(arr, orig)
        rmse = float(np.sqrt(np.mean(np.square(arr - orig))))
        im_diff = ax_bot.imshow(dmap, cmap="inferno", vmin=0.0, vmax=diff_vmax, interpolation="nearest")
        ax_bot.set_xticks([])
        ax_bot.set_yticks([])
        lbl_bot = "Referência" if col == 0 else f"RMS = {fmt_pt(rmse, 4)}"
        ax_bot.set_xlabel(lbl_bot, fontsize=8.4, fontweight="bold" if col > 0 else "normal",
                          color="#0F172A" if col > 0 else "#475569", labelpad=4)

    fig.text(0.015, 0.69, "Imagem", rotation=90, va="center", ha="center", fontsize=10.5, fontweight="bold")
    fig.text(0.015, 0.27, "|Δ| RMS", rotation=90, va="center", ha="center", fontsize=10.5, fontweight="bold")

    cax = fig.add_subplot(gs[1, 8])
    cbar = fig.colorbar(im_diff, cax=cax)
    cbar.set_label("|Δ| RMS", fontsize=8.8)
    cbar.ax.tick_params(labelsize=8.2)

    out_path = OUT_DIR / filename
    fig.savefig(out_path, dpi=260, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_flip_lr_limpo(samples: dict):
    items = [
        ("gtsrb_left", "GTSRB (cl. 34)"),
        ("mnist_3", "MNIST ('3')"),
        ("emnist_r", "EMNIST ('R')"),
        ("svhn_5", "SVHN ('5')"),
        ("cifar10_horse", "CIFAR-10 (cavalo)"),
    ]
    row_labels = ["Original", "flip_lr = False\n(atual)", "flip_lr = True\n(legado)"]

    fig = plt.figure(figsize=(15.5, 8.2), dpi=260)
    gs = fig.add_gridspec(3, 5, left=0.11, right=0.98, top=0.93, bottom=0.07, wspace=0.16, hspace=0.26)

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
                ax.set_title(title, fontsize=10.2, fontweight="bold", pad=7)
            is_asym = (key != "cifar10_horse")
            if row == 1:
                col_sp = "#15803D"
                for sp in ax.spines.values():
                    sp.set_edgecolor(col_sp)
                    sp.set_linewidth(2.0)
            elif row == 2:
                col_sp = "#B91C1C" if is_asym else "#0284C7"
                for sp in ax.spines.values():
                    sp.set_edgecolor(col_sp)
                    sp.set_linewidth(2.0)
            else:
                col_sp = "#475569"

            ax.set_xlabel(f"Pred.: cl. {pred_cls} ({fmt_pt(pred_prob, 1)}%)",
                          fontsize=8.6, color=col_sp, fontweight="bold" if row > 0 else "normal", labelpad=4)
        tf.keras.backend.clear_session()

    for row, rlabel in enumerate(row_labels):
        y_center = 0.80 - row * 0.305
        fig.text(0.052, y_center, rlabel, va="center", ha="center", fontsize=10.0, fontweight="bold")

    out_path = OUT_DIR / "aug_03_comparacao_flip_lr_semantico.png"
    fig.savefig(out_path, dpi=260, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print("Gerado:", out_path)


def gerar_piramide_limpa(sample: dict, filename: str, include_block5_prepool: bool = False):
    ds_name = sample["dataset"]
    model = gv.load_fp32_model(ds_name)
    img_t = sample["tensor"]
    img_np = img_t.numpy()
    hw = sample["size"]

    layer_names = ["block1_pool", "block2_pool", "block3_pool", "block4_pool"]
    if include_block5_prepool:
        layer_names.append("block5_activation2")
    layer_names.extend(["block5_pool", "global_average_pool", "logits"])

    probe = tf.keras.Model(model.input, [model.get_layer(n).output for n in layer_names])
    outs = probe(img_t[None, ...], training=False)
    out_map = {name: val.numpy()[0] for name, val in zip(layer_names, outs)}
    gap128 = out_map["global_average_pool"]

    block_rows = [
        ("Bloco 1", out_map["block1_pool"]),
        ("Bloco 2", out_map["block2_pool"]),
        ("Bloco 3", out_map["block3_pool"]),
        ("Bloco 4", out_map["block4_pool"]),
        ("Bloco 5" if not include_block5_prepool else "Bloco 5 pré",
         out_map["block5_activation2"] if include_block5_prepool else out_map["block5_pool"]),
    ]

    fig = plt.figure(figsize=(17.5, 11.4), dpi=240)
    gs = fig.add_gridspec(
        7, 8,
        width_ratios=[1.15, 1.05, 1, 1, 1, 1, 1, 1],
        height_ratios=[0.95, 1, 1, 1, 1, 1, 0.90],
        left=0.035, right=0.975, top=0.96, bottom=0.055, wspace=0.16, hspace=0.30,
    )

    # Linha 0 simplificada: Entrada + espaco limpo + grade 8x16 do features128
    ax_in = fig.add_subplot(gs[0, 0])
    gv.imshow_image(ax_in, img_np)
    ax_in.set_title("Entrada", fontsize=9.8, fontweight="bold")
    ax_in.set_xlabel(f"{hw}×{hw}×{sample['channels']}", fontsize=8.4, color="#475569")

    ax_b5grid = fig.add_subplot(gs[0, 1:4])
    grid_128 = (out_map["block5_pool"] if (out_map["block5_pool"].shape[:2] == (1, 1)) else gap128).reshape(8, 16)
    ax_b5grid.imshow(grid_128, cmap="viridis", aspect="auto", interpolation="nearest")
    ax_b5grid.set_title("GAP(Bloco 5) → 128 canais (grade 8×16)", fontsize=9.8, fontweight="bold")
    ax_b5grid.set_xticks([])
    ax_b5grid.set_yticks([])

    ax_hdr_note = fig.add_subplot(gs[0, 4:8])
    ax_hdr_note.axis("off")
    ax_hdr_note.text(
        0.02, 0.5,
        f"Base: {ds_name.upper()} ({hw}×{hw}×{sample['channels']})\n"
        f"Ativos > 0 em features128: {int((gap128 > 0).sum())}/128",
        va="center", ha="left", fontsize=10.5, fontweight="bold", color="#1E293B",
        bbox=dict(boxstyle="round,pad=0.45", facecolor="#F8FAFC", edgecolor="#CBD5E1"),
    )

    for r_offset, (b_title, fmap) in enumerate(block_rows, start=1):
        h_f, w_f, c_f = fmap.shape
        ax_meta = fig.add_subplot(gs[r_offset, 0])
        ax_meta.axis("off")
        ax_meta.text(
            0.50, 0.50,
            f"{b_title}\n{h_f}×{w_f}×{c_f}",
            va="center", ha="center", fontsize=9.6, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.40", facecolor="#F1F5F9", edgecolor="#CBD5E1"),
        )

        ax_ov = fig.add_subplot(gs[r_offset, 1])
        gv.overlay_attention(ax_ov, img_np, fmap, hw)
        if r_offset == 1:
            ax_ov.set_title("Atenção Média", fontsize=9.4, fontweight="bold")

        top_chs = gv.select_diverse_channels(fmap, k=6)
        for j, ch in enumerate(top_chs):
            ax_ch = fig.add_subplot(gs[r_offset, 2 + j])
            ch_map = fmap[:, :, ch]
            vmin, vmax = float(ch_map.min()), float(ch_map.max())
            if vmax - vmin < 1e-8:
                vmax = vmin + 1e-6
            ax_ch.imshow(ch_map, cmap="viridis", vmin=vmin, vmax=vmax, interpolation="nearest")
            ax_ch.set_xticks([])
            ax_ch.set_yticks([])
            ax_ch.set_title(f"Canal #{ch}", fontsize=8.8, fontweight="bold", pad=3)

    ax_vec = fig.add_subplot(gs[-1, :])
    x_idx = np.arange(128)
    colors = ["#136B83" if v >= 0 else "#DC2626" for v in gap128]
    ax_vec.bar(x_idx, gap128, color=colors, width=0.8)
    ax_vec.axhline(0.0, color="#0F172A", linewidth=0.8)
    ax_vec.set_xlim(-1, 128)
    ax_vec.set_title(f"Vetor features128 (mín={fmt_pt(float(gap128.min()), 2)}, máx={fmt_pt(float(gap128.max()), 2)})",
                     fontsize=9.8, fontweight="bold", loc="left")
    ax_vec.set_xlabel("Índice do canal (0 a 127)", fontsize=9.0, fontweight="bold")
    ax_vec.set_ylabel("Ativação GAP", fontsize=9.0, fontweight="bold")
    ax_vec.grid(True, axis="y", alpha=0.3)

    out_path = OUT_DIR / filename
    fig.savefig(out_path, dpi=240, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    tf.keras.backend.clear_session()
    print("Gerado:", out_path)


def gerar_grayscale_limpo(samples: dict):
    pairs = [
        ("fashion_boot", "Fashion-MNIST (Bota, cl. 9)"),
        ("fer2013_happy", "FER2013 (Happy, cl. 3)"),
    ]
    block_layers = [
        ("B1 (16×16×32)", "block1_pool"),
        ("B2 (8×8×48)", "block2_pool"),
        ("B3 (4×4×64)", "block3_pool"),
        ("B4 (2×2×96)", "block4_pool"),
        ("B5 pré (2×2×128)", "block5_activation2"),
    ]
    fig = plt.figure(figsize=(18.0, 10.6), dpi=240)
    gs = fig.add_gridspec(7, 11, width_ratios=[1, 1, 1, 1, 1, 0.35, 1, 1, 1, 1, 1],
                          left=0.04, right=0.98, top=0.95, bottom=0.06, wspace=0.14, hspace=0.34)

    for side_idx, (s_key, side_title) in enumerate(pairs):
        col_offset = 0 if side_idx == 0 else 6
        s = samples[s_key]
        model = gv.load_fp32_model(s["dataset"])
        layer_names = [n for _, n in block_layers] + ["global_average_pool"]
        probe = tf.keras.Model(model.input, [model.get_layer(n).output for n in layer_names])
        outs = probe(s["tensor"][None, ...], training=False)
        omap = {n: v.numpy()[0] for n, v in zip(layer_names, outs)}

        ax_in = fig.add_subplot(gs[0, col_offset])
        gv.imshow_image(ax_in, s["tensor"].numpy())
        ax_in.set_title("Entrada", fontsize=9.2, fontweight="bold")

        ax_hdr = fig.add_subplot(gs[0, col_offset + 1:col_offset + 5])
        ax_hdr.axis("off")
        ax_hdr.text(0.02, 0.5, side_title, va="center", ha="left", fontsize=11.0, fontweight="bold",
                    color="#0F172A",
                    bbox=dict(boxstyle="round,pad=0.4", facecolor="#F8FAFC", edgecolor="#CBD5E1"))

        for r_idx, (b_lbl, lname) in enumerate(block_layers, start=1):
            fmap = omap[lname]
            ax_ov = fig.add_subplot(gs[r_idx, col_offset])
            gv.overlay_attention(ax_ov, s["tensor"].numpy(), fmap, 64)
            ax_ov.set_ylabel(b_lbl, fontsize=8.8, fontweight="bold", labelpad=5)
            if r_idx == 1:
                ax_ov.set_title("Atenção Média", fontsize=8.8, fontweight="bold")

            top4 = gv.select_diverse_channels(fmap, k=4)
            for j, ch in enumerate(top4):
                ax_c = fig.add_subplot(gs[r_idx, col_offset + 1 + j])
                ch_m = fmap[:, :, ch]
                vmin, vmax = float(ch_m.min()), float(ch_m.max())
                if vmax - vmin < 1e-8:
                    vmax = vmin + 1e-6
                ax_c.imshow(ch_m, cmap="viridis", vmin=vmin, vmax=vmax, interpolation="nearest")
                ax_c.set_xticks([])
                ax_c.set_yticks([])
                ax_c.set_title(f"#{ch}", fontsize=8.6, fontweight="bold", pad=2)

        gap = omap["global_average_pool"]
        ax_v = fig.add_subplot(gs[6, col_offset:col_offset + 5])
        cols_bar = ["#136B83" if v >= 0 else "#DC2626" for v in gap]
        ax_v.bar(np.arange(128), gap, color=cols_bar, width=0.8)
        ax_v.axhline(0.0, color="#0F172A", linewidth=0.7)
        ax_v.set_xlim(-1, 128)
        ax_v.set_title(f"features128 (ativos > 0: {int((gap > 0).sum())}/128)", fontsize=9.2, fontweight="bold", loc="left")
        ax_v.set_xlabel("Canal (0..127)", fontsize=8.5, color="#475569")
        ax_v.grid(True, axis="y", alpha=0.25)
        tf.keras.backend.clear_session()

    out_path = OUT_DIR / "fmap_03_piramide_blocos_grayscale.png"
    fig.savefig(out_path, dpi=240, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print("Gerado:", out_path)


if __name__ == "__main__":
    gerar_metricas_classificacao()
    gerar_equilibrio_9_datasets()
    samples = gv.load_verified_samples()
    gerar_aug_pipeline_limpo(samples["gtsrb_stop"], "aug_01_pipeline_etapas_gtsrb.png")
    gerar_aug_pipeline_limpo(samples["cifar10_ship"], "aug_02_pipeline_etapas_cifar10.png")
    gerar_flip_lr_limpo(samples)
    gerar_piramide_limpa(samples["gtsrb_stop"], "fmap_01_piramide_blocos_gtsrb.png", include_block5_prepool=False)
    gerar_piramide_limpa(samples["cifar10_ship"], "fmap_02_piramide_blocos_cifar10.png", include_block5_prepool=True)
    gerar_grayscale_limpo(samples)
    # Compatibilidade para scripts antigos caso alguma referencia use o nome anterior:
    shutil.copyfile(OUT_DIR / "fig_arq_etapa3_hibrida_4x5.png", OUT_DIR / "fig_arquitetura_hibrida_4x5_qubits.png")
    print("Todas as figuras limpas complementares foram geradas!")
