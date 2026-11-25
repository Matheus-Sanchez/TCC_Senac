# -*- coding: utf-8 -*-
"""Gera a animacao passo a passo da Esfera de Bloch (|0> -> RX -> RY -> RZ -> Pauli-Y).

Saidas geradas em TCC_Senac/figuras/gifs/:
- 09a_bloch_passo0_init.png            : Estado inicial |0> (300 DPI)
- 09b_bloch_passo1_rx.gif              : Animacao 1-shot de RX(pi/3) + hold final
- 09b_bloch_passo1_rx_final.png        : Quadro final estatico de RX (300 DPI)
- 09c_bloch_passo2_ry.gif              : Animacao 1-shot de RY(3pi/4) + hold final
- 09c_bloch_passo2_ry_final.png        : Quadro final estatico de RY (300 DPI)
- 09d_bloch_passo3_rz.gif              : Animacao 1-shot de RZ(2pi/3) + hold final
- 09d_bloch_passo3_rz_final.png        : Quadro final estatico de RZ (300 DPI)
- 09e_bloch_passo4_pauli_y.gif         : Animacao 1-shot da medicao Pauli-Y <Y> in [-1, 1]
- 09e_bloch_passo4_pauli_y_final.png   : Quadro final estatico da medicao Pauli-Y (300 DPI)
- 09_esfera_bloch_completo_loop.gif    : Versao completa continua em loop (bonus)
"""

from __future__ import annotations

import io
from pathlib import Path
import numpy as np
from PIL import Image
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse, Rectangle

BASE_DIR = Path(__file__).resolve().parent
GIF_DIR = BASE_DIR / "figuras" / "gifs"
GIF_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "mathtext.fontset": "dejavusans",
    "figure.facecolor": "#FFFFFF",
    "axes.facecolor": "#FFFFFF",
    "text.color": "#0F172A",
})

# ---------------------------------------------------------------------------
# Operadores quanticos exatos (2x2) e angulos escolhidos para maxima clareza 3D
# ---------------------------------------------------------------------------
SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
EYE2 = np.eye(2, dtype=complex)

ALPHA_X = np.pi / 3.0        # 60 deg
ALPHA_Y = 3.0 * np.pi / 4.0  # 135 deg
ALPHA_Z = 2.0 * np.pi / 3.0  # 120 deg

AZ = np.deg2rad(32.0)
EL = np.deg2rad(20.0)

# Paleta coerente com fig_261_esfera_bloch.png e identidade SENAC/TCC
COL_BLUE = "#1D4ED8"
COL_RX = "#DC2626"      # Vermelho para eixo/rotacao X
COL_RY = "#059669"      # Verde esmeralda para eixo/rotacao Y
COL_RZ = "#7C3AED"      # Violeta para eixo/rotacao Z
COL_PY = "#0F766E"      # Teal para medicao Pauli-Y
COL_NEG = "#E11D48"     # Rosa-vermelho para polo -1 do medidor
COL_SLATE_DARK = "#0F172A"
COL_SLATE_MID = "#334155"
COL_SLATE_MUTED = "#64748B"
COL_SLATE_LIGHT = "#CBD5E1"
COL_CARD_BG = "#F8FAFC"


def rx_mat(theta: float) -> np.ndarray:
    return np.cos(theta / 2.0) * EYE2 - 1.0j * np.sin(theta / 2.0) * SIGMA_X


def ry_mat(theta: float) -> np.ndarray:
    return np.cos(theta / 2.0) * EYE2 - 1.0j * np.sin(theta / 2.0) * SIGMA_Y


def rz_mat(theta: float) -> np.ndarray:
    return np.cos(theta / 2.0) * EYE2 - 1.0j * np.sin(theta / 2.0) * SIGMA_Z


def state_to_bloch(psi: np.ndarray) -> np.ndarray:
    return np.array([
        float(np.real(np.vdot(psi, SIGMA_X @ psi))),
        float(np.real(np.vdot(psi, SIGMA_Y @ psi))),
        float(np.real(np.vdot(psi, SIGMA_Z @ psi))),
    ])


def ease_in_out(t: float) -> float:
    t = float(np.clip(t, 0.0, 1.0))
    return 0.5 * (1.0 - np.cos(np.pi * t))


def fmt_pt(val: float, signed: bool = True, decimals: int = 2) -> str:
    if abs(val) < 0.5 * (10.0 ** (-decimals)):
        val = 0.0
    if signed:
        if val > 0:
            s = f"+{val:.{decimals}f}"
        elif val < 0:
            s = f"\u2212{abs(val):.{decimals}f}"
        else:
            s = f" {0.0:.{decimals}f}"
    else:
        s = f"{val:.{decimals}f}"
    return s.replace(".", ",")


def proj(x, y, z):
    u = -x * np.sin(AZ) + y * np.cos(AZ)
    v = (-x * np.cos(AZ) - y * np.sin(AZ)) * np.sin(EL) + z * np.cos(EL)
    depth = (x * np.cos(AZ) + y * np.sin(AZ)) * np.cos(EL) + z * np.sin(EL)
    return u, v, depth


# Estados de marco exatos
PSI_0 = np.array([1.0, 0.0], dtype=complex)
PSI_1 = rx_mat(ALPHA_X) @ PSI_0
PSI_2 = ry_mat(ALPHA_Y) @ PSI_1
PSI_3 = rz_mat(ALPHA_Z) @ PSI_2

R0 = state_to_bloch(PSI_0)
R1 = state_to_bloch(PSI_1)
R2 = state_to_bloch(PSI_2)
R3 = state_to_bloch(PSI_3)


def sample_arc(psi_start: np.ndarray, gate_fn, angle: float, n: int = 80) -> np.ndarray:
    ts = np.linspace(0.0, 1.0, n)
    return np.array([state_to_bloch(gate_fn(t * angle) @ psi_start) for t in ts])


ARC_RX_FULL = sample_arc(PSI_0, rx_mat, ALPHA_X, 80)
ARC_RY_FULL = sample_arc(PSI_1, ry_mat, ALPHA_Y, 80)
ARC_RZ_FULL = sample_arc(PSI_2, rz_mat, ALPHA_Z, 80)


def _plot_3d_curve_depth(ax, pts: np.ndarray, color: str, lw_front: float, lw_back: float | None = None,
                         alpha_front: float = 0.95, alpha_back: float = 0.35,
                         ls_front: str = "-", ls_back: str = "--", z_front: int = 5, z_back: int = 1):
    if len(pts) < 2:
        return
    u, v, d = proj(pts[:, 0], pts[:, 1], pts[:, 2])
    front = d >= -0.02
    if lw_back is None:
        lw_back = lw_front * 0.82
    ax.plot(np.where(~front, u, np.nan), np.where(~front, v, np.nan),
            color=color, lw=lw_back, ls=ls_back, alpha=alpha_back, zorder=z_back, solid_capstyle="round")
    ax.plot(np.where(front, u, np.nan), np.where(front, v, np.nan),
            color=color, lw=lw_front, ls=ls_front, alpha=alpha_front, zorder=z_front, solid_capstyle="round")


def _draw_axis_rotation_ring(ax, axis: str, color: str):
    """Desenha um pequeno anel 3D com seta indicando o sentido positivo (regra da mao direita) em torno do eixo."""
    rad = 0.145
    pos = 0.90
    if axis == "X":
        phi = np.linspace(0.15 * np.pi, 1.65 * np.pi, 60)
        xs = np.full_like(phi, pos)
        ys = rad * np.cos(phi)
        zs = rad * np.sin(phi)
    elif axis == "Y":
        phi = np.linspace(0.15 * np.pi, 1.65 * np.pi, 60)
        xs = rad * np.sin(phi)
        ys = np.full_like(phi, pos)
        zs = rad * np.cos(phi)
    else:  # Z: termina na frente apontando da esquerda (+X) para a direita (+Y)
        phi = np.linspace(-0.85 * np.pi, 0.55 * np.pi, 60)
        xs = rad * np.cos(phi)
        ys = rad * np.sin(phi)
        zs = np.full_like(phi, 0.72)
    u, v, _ = proj(xs, ys, zs)
    ax.plot(u[:-1], v[:-1], color=color, lw=1.7, alpha=0.92, zorder=8)
    ax.annotate(
        "", xy=(u[-1], v[-1]), xytext=(u[-4], v[-4]),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.7, mutation_scale=10),
        zorder=9,
    )


def _draw_orbit_guide(ax, axis: str, r_ref: np.ndarray, color: str):
    """Desenha o circulo-guia tracejado da orbita de rotacao em torno do eixo ativo."""
    ang = np.linspace(0.0, 2.0 * np.pi, 180)
    if axis == "X":
        rad = np.hypot(r_ref[1], r_ref[2])
        pts = np.column_stack([np.full_like(ang, r_ref[0]), rad * np.cos(ang), rad * np.sin(ang)])
    elif axis == "Y":
        rad = np.hypot(r_ref[0], r_ref[2])
        pts = np.column_stack([rad * np.cos(ang), np.full_like(ang, r_ref[1]), rad * np.sin(ang)])
    else:
        rad = np.hypot(r_ref[0], r_ref[1])
        pts = np.column_stack([rad * np.cos(ang), rad * np.sin(ang), np.full_like(ang, r_ref[2])])
    _plot_3d_curve_depth(ax, pts, color=color, lw_front=1.15, lw_back=0.9,
                         alpha_front=0.38, alpha_back=0.18, ls_front="--", ls_back=":", z_front=2, z_back=1)


def _psi_label_offset(pu: float, pv: float) -> tuple[float, float]:
    """Posiciona o rotulo |psi> para fora do vetor sem colidir com eixos ou polos."""
    norm = max(np.hypot(pu, pv), 1e-6)
    ux, uy = pu / norm, pv / norm
    if pv > 0.80 and abs(pu) < 0.25:
        return pu - 0.24, pv - 0.04
    if pu < -0.50 and pv > 0.25:
        return pu - 0.16, pv + 0.14
    if pu < -0.55 and pv <= 0.25:
        return pu - 0.16, pv + 0.16
    if pu > 0.15 and pv < -0.35:
        return pu + 0.16, pv - 0.12
    return pu + 0.18 * ux, pv + 0.18 * uy


def render_frame(step: int, progress: float, dpi: int = 160) -> Image.Image:
    """Renderiza um quadro completo da Esfera de Bloch.

    step:
      0 -> Estado inicial |0>
      1 -> Rotacao RX(pi/3)
      2 -> Rotacao RY(3pi/4)
      3 -> Rotacao RZ(2pi/3)
      4 -> Medicao Pauli-Y -> <Y> in [-1, +1]
    progress: float em [0, 1] (valor bruto; ease_in_out e aplicado internamente).
    """
    p = ease_in_out(progress)

    # Estado atual e metadados por passo
    if step == 0:
        accent = COL_BLUE
        subtitle = r"Estado inicial $|0\rangle$ no polo $+Z$"
        psi_cur = PSI_0
        r_cur = R0
        active_axis = None
        angle_label = "Estado inicial"
        angle_val = r"$|0\rangle$ (polo $+Z$)"
        eq_top = r"$|\psi_0\rangle = |0\rangle = [1,\; 0]^T \quad (\theta = 0,\; \vec{r} = (0,\, 0,\, +1))$"
        eq_bot = "Todo circuito quântico inicia no polo norte da esfera antes das rotações"
        meas_p = 0.0
    elif step == 1:
        accent = COL_RX
        subtitle = r"Passo 1/4: Rotação $R_X(\pi/3)$ em torno do eixo $X$"
        ang = p * ALPHA_X
        psi_cur = rx_mat(ang) @ PSI_0
        r_cur = state_to_bloch(psi_cur)
        active_axis = "X"
        angle_label = r"Ângulo $R_X$"
        angle_val = f"{np.rad2deg(ang):.0f}°  (alvo: 60° = π/3)"
        eq_top = r"$|\psi_1\rangle = R_X(\pi/3)|0\rangle = e^{-i\frac{\pi}{6}X}|0\rangle$"
        eq_bot = "Rotação de 60° em torno do eixo X leva o estado à superposição de |0⟩ e |1⟩"
        meas_p = 0.0
    elif step == 2:
        accent = COL_RY
        subtitle = r"Passo 2/4: Rotação $R_Y(3\pi/4)$ em torno do eixo $Y$"
        ang = p * ALPHA_Y
        psi_cur = ry_mat(ang) @ PSI_1
        r_cur = state_to_bloch(psi_cur)
        active_axis = "Y"
        angle_label = r"Ângulo $R_Y$"
        angle_val = f"{np.rad2deg(ang):.0f}°  (alvo: 135° = 3π/4)"
        eq_top = r"$|\psi_2\rangle = R_Y(3\pi/4)|\psi_1\rangle = e^{-i\frac{3\pi}{8}Y}|\psi_1\rangle$"
        eq_bot = "Rotação de 135° em torno do eixo Y mantém y fixo e redistribui x e z"
        meas_p = 0.0
    elif step == 3:
        accent = COL_RZ
        subtitle = r"Passo 3/4: Rotação $R_Z(2\pi/3)$ em torno do eixo $Z$"
        ang = p * ALPHA_Z
        psi_cur = rz_mat(ang) @ PSI_2
        r_cur = state_to_bloch(psi_cur)
        active_axis = "Z"
        angle_label = r"Ângulo $R_Z$"
        angle_val = f"{np.rad2deg(ang):.0f}°  (alvo: 120° = 2π/3)"
        eq_top = r"$|\psi_3\rangle = R_Z(2\pi/3)|\psi_2\rangle = e^{-i\frac{\pi}{3}Z}|\psi_2\rangle$"
        eq_bot = "Rotação de 120° em torno do eixo Z ajusta a fase relativa φ sem mudar z"
        meas_p = 0.0
    else:  # step == 4
        accent = COL_PY
        subtitle = r"Passo 4/4: Medição Pauli-$Y$ $\rightarrow$ $\langle Y \rangle \in [-1,\; +1]$"
        psi_cur = PSI_3
        r_cur = R3
        active_axis = "PAULI_Y"
        angle_label = "Observável"
        angle_val = r"Pauli-$Y$ ($\lambda = \pm 1$)"
        eq_top = r"$\langle Y \rangle = \langle \psi_3 | Y | \psi_3 \rangle = r_y = +0{,}74 \in [-1,\; +1]$"
        eq_bot = "Projeção ortogonal no eixo Y converte o qubit em valor real contínuo em [−1, +1]"
        meas_p = p

    # Figura fixa 7.6 x 5.4 (mesma proporcao de fig_261_circuito_bell.png)
    fig = plt.figure(figsize=(7.6, 5.4), dpi=dpi)
    fig.patch.set_facecolor("#FFFFFF")
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_axis_off()

    # Cartao externo
    bg = FancyBboxPatch(
        (0.012, 0.014), 0.976, 0.972,
        boxstyle="round,pad=0.004,rounding_size=0.020",
        facecolor=COL_CARD_BG, edgecolor=COL_SLATE_LIGHT, linewidth=1.3,
        transform=ax.transAxes, zorder=0,
    )
    ax.add_patch(bg)

    # Cabecalho
    header = FancyBboxPatch(
        (0.028, 0.870), 0.944, 0.100,
        boxstyle="round,pad=0.004,rounding_size=0.015",
        facecolor="#FFFFFF", edgecolor=accent, linewidth=1.5,
        transform=ax.transAxes, zorder=1,
    )
    ax.add_patch(header)
    ax.text(
        0.50, 0.938, "Estado de 1 Qubit na Esfera de Bloch",
        ha="center", va="center", fontsize=14.0, fontweight="bold",
        color=COL_SLATE_DARK, transform=ax.transAxes, zorder=2,
    )
    ax.text(
        0.50, 0.892, subtitle,
        ha="center", va="center", fontsize=11.4, fontweight="bold" if step > 0 else "normal",
        color=accent if step > 0 else "#475569", transform=ax.transAxes, zorder=2,
    )

    # Barra de progresso das 5 etapas (pilulas conectadas)
    pills = [
        (r"$|0\rangle$", COL_BLUE),
        (r"$R_X$", COL_RX),
        (r"$R_Y$", COL_RY),
        (r"$R_Z$", COL_RZ),
        (r"Pauli-$Y$", COL_PY),
    ]
    pill_w = 0.150
    pill_h = 0.050
    gap = 0.044
    total_w = len(pills) * pill_w + (len(pills) - 1) * gap
    x0 = 0.50 - total_w / 2.0
    py_pill = 0.802

    for idx, (label, pcol) in enumerate(pills):
        px = x0 + idx * (pill_w + gap)
        if idx == step:
            fc, ec, tc, lw = pcol, pcol, "#FFFFFF", 1.5
        elif idx < step:
            fc, ec, tc, lw = "#FFFFFF", pcol, pcol, 1.3
        else:
            fc, ec, tc, lw = "#F1F5F9", "#CBD5E1", "#94A3B8", 1.0
        box = FancyBboxPatch(
            (px, py_pill), pill_w, pill_h,
            boxstyle="round,pad=0.002,rounding_size=0.012",
            facecolor=fc, edgecolor=ec, linewidth=lw,
            transform=ax.transAxes, zorder=2,
        )
        ax.add_patch(box)
        ax.text(
            px + pill_w / 2.0, py_pill + pill_h / 2.0, label,
            ha="center", va="center", fontsize=10.6, fontweight="bold",
            color=tc, transform=ax.transAxes, zorder=3,
        )
        if idx < len(pills) - 1:
            ax.text(
                px + pill_w + gap / 2.0, py_pill + pill_h / 2.0, "→",
                ha="center", va="center", fontsize=11.5, fontweight="bold",
                color=pcol if idx < step else "#94A3B8",
                transform=ax.transAxes, zorder=2,
            )

    # -----------------------------------------------------------------------
    # Esfera de Bloch 3D (lado esquerdo / centro)
    # -----------------------------------------------------------------------
    ax_in = fig.add_axes([0.025, 0.155, 0.595, 0.635])
    ax_in.set_xlim(-1.66, 1.66)
    ax_in.set_ylim(-1.38, 1.38)
    ax_in.set_aspect("equal")
    ax_in.axis("off")

    # Esfera com preenchimento suave + brilho sutil 3D
    t_ext = np.linspace(0.0, 2.0 * np.pi, 240)
    ax_in.fill(np.cos(t_ext), np.sin(t_ext), color="#EFF6FF", alpha=0.52, zorder=0)
    ax_in.add_patch(Ellipse((-0.26, 0.30), 0.72, 0.56, angle=28, facecolor="#FFFFFF", edgecolor="none", alpha=0.52, zorder=0))
    ax_in.plot(np.cos(t_ext), np.sin(t_ext), color="#94A3B8", lw=1.45, zorder=2)

    # Equador (z = 0) e meridiano de referencia (x = 0)
    ts = np.linspace(0.0, 2.0 * np.pi, 300)
    eq_pts = np.column_stack([np.cos(ts), np.sin(ts), np.zeros_like(ts)])
    _plot_3d_curve_depth(ax_in, eq_pts, color="#64748B", lw_front=1.35, lw_back=1.05,
                         alpha_front=0.82, alpha_back=0.40, ls_front="-", ls_back="--", z_front=2, z_back=1)
    mer_pts = np.column_stack([np.zeros_like(ts), np.cos(ts), np.sin(ts)])
    _plot_3d_curve_depth(ax_in, mer_pts, color="#94A3B8", lw_front=0.85, lw_back=0.75,
                         alpha_front=0.28, alpha_back=0.14, ls_front=":", ls_back=":", z_front=1, z_back=1)

    # Eixos coordenados (+X, +Y, +Z) com destaque no eixo ativo
    x_col = COL_RX if active_axis == "X" else "#475569"
    y_col = COL_RY if active_axis == "Y" else (COL_PY if active_axis == "PAULI_Y" else "#475569")
    z_col = COL_RZ if active_axis == "Z" else "#334155"

    x_lw = 2.3 if active_axis == "X" else 1.25
    y_lw = 2.3 if active_axis in ("Y", "PAULI_Y") else 1.25
    z_lw = 2.3 if active_axis == "Z" else 1.25

    axes_spec = [
        ((-1.14, 0, 0), (1.18, 0, 0), x_col, x_lw),
        ((0, -1.14, 0), (0, 1.20, 0), y_col, y_lw),
        ((0, 0, -1.12), (0, 0, 1.18), z_col, z_lw),
    ]
    for p0, p1, col, lw in axes_spec:
        u0, v0, _ = proj(*p0)
        u1, v1, _ = proj(*p1)
        ax_in.annotate(
            "", xy=(u1, v1), xytext=(u0, v0),
            arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, mutation_scale=12 if lw > 1.8 else 10),
            zorder=3,
        )

    # Rotulos dos eixos e polos
    ux, vx, _ = proj(1.18, 0, 0)
    uy, vy, _ = proj(0, 1.20, 0)
    uy_neg, vy_neg, _ = proj(0, -1.14, 0)
    u_n, v_n, _ = proj(0, 0, 1.0)
    u_s, v_s, _ = proj(0, 0, -1.0)

    ax_in.scatter([u_n, u_s], [v_n, v_s], s=32, color=COL_SLATE_DARK, zorder=6)
    ax_in.text(u_n + 0.08, v_n + 0.16, r"$|0\rangle$ (+Z)", fontsize=10.8, fontweight="bold",
               color=COL_RZ if active_axis == "Z" else COL_SLATE_DARK, ha="left", va="center")
    ax_in.text(u_s + 0.08, v_s - 0.18, r"$|1\rangle$ (−Z)", fontsize=10.8, fontweight="bold",
               color=COL_RZ if active_axis == "Z" else COL_SLATE_DARK, ha="left", va="center")
    ax_in.text(ux * 1.44 - 0.18, vx * 1.44 - 0.19, r"$+X\;(|+\rangle)$", fontsize=10.4, fontweight="bold",
               color=COL_RX if active_axis == "X" else COL_SLATE_MID, ha="center", va="center")

    if active_axis == "PAULI_Y":
        ax_in.text(uy * 1.32 + 0.05, vy * 1.32 - 0.02, r"$+Y\;(|+i\rangle)$" + "\n(+1)",
                   fontsize=10.2, fontweight="bold", color=COL_PY, ha="center", va="center", linespacing=1.08)
        ax_in.text(uy_neg * 1.24 - 0.05, vy_neg * 1.24 + 0.08, r"$-Y\;(|-i\rangle)$" + "\n(−1)",
                   fontsize=9.6, fontweight="bold", color=COL_NEG, ha="center", va="center", linespacing=1.08)
        # Marcadores nos autovalores +1 e -1 do eixo Y
        u_yp, v_yp, _ = proj(0, 1.0, 0)
        u_ym, v_ym, _ = proj(0, -1.0, 0)
        ax_in.scatter([u_yp], [v_yp], s=38, color=COL_PY, zorder=6)
        ax_in.scatter([u_ym], [v_ym], s=34, color=COL_NEG, zorder=6)
    else:
        ax_in.text(uy * 1.36 + 0.04, vy * 1.36 - 0.02, r"$+Y\;(|+i\rangle)$",
                   fontsize=10.4, fontweight="bold",
                   color=COL_RY if active_axis == "Y" else COL_SLATE_MID, ha="center", va="center")

    # Guia de orbita e anel de rotacao no eixo ativo
    if active_axis == "X":
        _draw_orbit_guide(ax_in, "X", R0, COL_RX)
        _draw_axis_rotation_ring(ax_in, "X", COL_RX)
    elif active_axis == "Y":
        _draw_orbit_guide(ax_in, "Y", R1, COL_RY)
        _draw_axis_rotation_ring(ax_in, "Y", COL_RY)
    elif active_axis == "Z":
        _draw_orbit_guide(ax_in, "Z", R2, COL_RZ)
        _draw_axis_rotation_ring(ax_in, "Z", COL_RZ)

    # Trilhas acumuladas das rotacoes anteriores (suaves) + trilha ativa (destaque)
    if step >= 2:
        _plot_3d_curve_depth(ax_in, ARC_RX_FULL, color=COL_RX, lw_front=1.5, lw_back=1.1,
                             alpha_front=0.34, alpha_back=0.18, ls_front="-", ls_back="--", z_front=3, z_back=2)
    if step >= 3:
        _plot_3d_curve_depth(ax_in, ARC_RY_FULL, color=COL_RY, lw_front=1.5, lw_back=1.1,
                             alpha_front=0.34, alpha_back=0.18, ls_front="-", ls_back="--", z_front=3, z_back=2)
    if step >= 4:
        _plot_3d_curve_depth(ax_in, ARC_RZ_FULL, color=COL_RZ, lw_front=1.5, lw_back=1.1,
                             alpha_front=0.34, alpha_back=0.18, ls_front="-", ls_back="--", z_front=3, z_back=2)

    if step == 1 and p > 1e-3:
        cur_arc = sample_arc(PSI_0, rx_mat, p * ALPHA_X, max(8, int(60 * p)))
        _plot_3d_curve_depth(ax_in, cur_arc, color=COL_RX, lw_front=3.0, lw_back=2.2,
                             alpha_front=0.95, alpha_back=0.55, ls_front="-", ls_back="--", z_front=6, z_back=3)
    elif step == 2 and p > 1e-3:
        cur_arc = sample_arc(PSI_1, ry_mat, p * ALPHA_Y, max(8, int(60 * p)))
        _plot_3d_curve_depth(ax_in, cur_arc, color=COL_RY, lw_front=3.0, lw_back=2.2,
                             alpha_front=0.95, alpha_back=0.55, ls_front="-", ls_back="--", z_front=6, z_back=3)
        u_st, v_st, _ = proj(*R1)
        ax_in.scatter([u_st], [v_st], s=30, facecolor="#FFFFFF", edgecolor=COL_RY, lw=1.6, zorder=7)
    elif step == 3 and p > 1e-3:
        cur_arc = sample_arc(PSI_2, rz_mat, p * ALPHA_Z, max(8, int(60 * p)))
        _plot_3d_curve_depth(ax_in, cur_arc, color=COL_RZ, lw_front=3.0, lw_back=2.2,
                             alpha_front=0.95, alpha_back=0.55, ls_front="-", ls_back="--", z_front=6, z_back=3)
        u_st, v_st, _ = proj(*R2)
        ax_in.scatter([u_st], [v_st], s=30, facecolor="#FFFFFF", edgecolor=COL_RZ, lw=1.6, zorder=7)

    # Projecao ortogonal no eixo Y durante Passo 4 (Medicao Pauli-Y)
    if step == 4 and meas_p > 1e-3:
        drop_t = min(1.0, meas_p / 0.55)
        bar_t = max(0.0, min(1.0, (meas_p - 0.35) / 0.65))

        r_proj_target = np.array([0.0, R3[1], 0.0])
        r_drop_tip = R3 + drop_t * (r_proj_target - R3)
        u_r3, v_r3, _ = proj(*R3)
        u_dt, v_dt, _ = proj(*r_drop_tip)
        ax_in.plot([u_r3, u_dt], [v_r3, v_dt], color=COL_PY, lw=2.2, ls="--", alpha=0.95, zorder=7)

        if bar_t > 1e-3:
            u_pt, v_pt, _ = proj(0.0, R3[1] * bar_t, 0.0)
            ax_in.plot([0.0, u_pt], [0.0, v_pt], color="#FFFFFF", lw=6.0, solid_capstyle="round", zorder=7)
            ax_in.plot([0.0, u_pt], [0.0, v_pt], color=COL_PY, lw=3.8, solid_capstyle="round", zorder=8)
            ax_in.scatter([u_pt], [v_pt], s=62, facecolor="#14B8A6", edgecolor="#FFFFFF", lw=1.4, zorder=9)
            if bar_t > 0.72:
                u_pf, v_pf, _ = proj(0.0, R3[1], 0.0)
                ax_in.text(
                    u_pf - 0.09, v_pf + 0.20, r"$\langle Y\rangle = +0{,}74$",
                    fontsize=9.6, fontweight="bold", color=COL_PY, ha="center", va="bottom",
                    bbox=dict(boxstyle="round,pad=0.18", facecolor="#FFFFFF", edgecolor=COL_PY, lw=1.0, alpha=0.96),
                    zorder=10,
                )

    # Vetor de estado |psi> com halo branco para contraste impecavel
    pu, pv, _ = proj(*r_cur)
    ax_in.annotate(
        "", xy=(pu, pv), xytext=(0.0, 0.0),
        arrowprops=dict(arrowstyle="-|>", color="#FFFFFF", lw=4.8, mutation_scale=17),
        zorder=8,
    )
    ax_in.annotate(
        "", xy=(pu, pv), xytext=(0.0, 0.0),
        arrowprops=dict(arrowstyle="-|>", color=COL_BLUE, lw=2.8, mutation_scale=15),
        zorder=9,
    )
    ax_in.scatter([pu], [pv], s=36, facecolor=COL_BLUE, edgecolor="#FFFFFF", lw=1.0, zorder=10)

    lx, ly = _psi_label_offset(pu, pv)
    psi_lbl = r"$|\psi_0\rangle$" if step == 0 else r"$|\psi\rangle$"
    ax_in.text(
        lx, ly, psi_lbl,
        fontsize=13.2, fontweight="bold", color=COL_BLUE, ha="center", va="center",
        bbox=dict(boxstyle="round,pad=0.10", facecolor="#F8FAFC", edgecolor="none", alpha=0.72),
        zorder=11,
    )

    # -----------------------------------------------------------------------
    # Painel lateral direito: Coordenadas de Bloch + Medidor Pauli-Y [-1, +1]
    # -----------------------------------------------------------------------
    rx_p = 0.635
    rw_p = 0.335

    # Mini-cartao superior: Vetor de Bloch & Operacao
    c1_y, c1_h = 0.482, 0.298
    ax.add_patch(FancyBboxPatch(
        (rx_p, c1_y), rw_p, c1_h,
        boxstyle="round,pad=0.003,rounding_size=0.014",
        facecolor="#FFFFFF", edgecolor="#CBD5E1", linewidth=1.1,
        transform=ax.transAxes, zorder=2,
    ))
    ax.add_patch(FancyBboxPatch(
        (rx_p, c1_y + c1_h - 0.056), rw_p, 0.056,
        boxstyle="round,pad=0.002,rounding_size=0.012",
        facecolor=accent, edgecolor="none",
        transform=ax.transAxes, zorder=3,
    ))
    ax.text(
        rx_p + rw_p / 2.0, c1_y + c1_h - 0.028, "Vetor de Bloch  (x, y, z)",
        ha="center", va="center", fontsize=10.2, fontweight="bold",
        color="#FFFFFF", transform=ax.transAxes, zorder=4,
    )

    coord_rows = [
        ("x = ⟨X⟩", r_cur[0], COL_RX, active_axis == "X"),
        ("y = ⟨Y⟩", r_cur[1], COL_PY if step == 4 else COL_RY, active_axis in ("Y", "PAULI_Y")),
        ("z = ⟨Z⟩", r_cur[2], COL_RZ, active_axis == "Z"),
    ]
    for i_row, (cname, cval, ccol, is_hi) in enumerate(coord_rows):
        ry_row = c1_y + c1_h - 0.098 - i_row * 0.053
        if is_hi:
            ax.add_patch(FancyBboxPatch(
                (rx_p + 0.012, ry_row - 0.021), rw_p - 0.024, 0.042,
                boxstyle="round,pad=0.001,rounding_size=0.008",
                facecolor="#F0FDFA" if step == 4 else "#F8FAFC",
                edgecolor=ccol, linewidth=1.0,
                transform=ax.transAxes, zorder=3,
            ))
        ax.text(
            rx_p + 0.026, ry_row, cname,
            ha="left", va="center", fontsize=10.0,
            fontweight="bold" if is_hi else "normal",
            color=ccol if is_hi else COL_SLATE_MID,
            transform=ax.transAxes, zorder=4,
        )
        ax.text(
            rx_p + rw_p - 0.024, ry_row, fmt_pt(cval, signed=True, decimals=2),
            ha="right", va="center", fontsize=10.6, fontweight="bold",
            family="DejaVu Sans Mono",
            color=ccol if is_hi else COL_SLATE_DARK,
            transform=ax.transAxes, zorder=4,
        )

    # Linha separadora + angulo/operacao atual
    ax.plot([rx_p + 0.018, rx_p + rw_p - 0.018], [c1_y + 0.068, c1_y + 0.068],
            color="#E2E8F0", lw=1.0, transform=ax.transAxes, zorder=3)
    ax.text(
        rx_p + rw_p / 2.0, c1_y + 0.048, angle_label,
        ha="center", va="center", fontsize=9.0, color=COL_SLATE_MUTED,
        transform=ax.transAxes, zorder=4,
    )
    ax.text(
        rx_p + rw_p / 2.0, c1_y + 0.020, angle_val,
        ha="center", va="center", fontsize=9.6, fontweight="bold", color=accent,
        transform=ax.transAxes, zorder=4,
    )

    # Mini-cartao inferior: Medicao Pauli-Y in [-1, +1]
    c2_y, c2_h = 0.168, 0.296
    c2_ec = COL_PY if step == 4 else "#CBD5E1"
    c2_lw = 1.6 if step == 4 else 1.1
    ax.add_patch(FancyBboxPatch(
        (rx_p, c2_y), rw_p, c2_h,
        boxstyle="round,pad=0.003,rounding_size=0.014",
        facecolor="#F0FDFA" if step == 4 else "#FFFFFF",
        edgecolor=c2_ec, linewidth=c2_lw,
        transform=ax.transAxes, zorder=2,
    ))
    ax.add_patch(FancyBboxPatch(
        (rx_p, c2_y + c2_h - 0.056), rw_p, 0.056,
        boxstyle="round,pad=0.002,rounding_size=0.012",
        facecolor=COL_PY if step == 4 else "#64748B", edgecolor="none",
        transform=ax.transAxes, zorder=3,
    ))
    ax.text(
        rx_p + rw_p / 2.0, c2_y + c2_h - 0.028, "Saída Pauli-Y   ⟨Y⟩ ∈ [−1, +1]",
        ha="center", va="center", fontsize=9.8, fontweight="bold",
        color="#FFFFFF", transform=ax.transAxes, zorder=4,
    )

    # Barra divergente [-1, 0, +1]
    bx = rx_p + 0.026
    bw = rw_p - 0.052
    by = c2_y + 0.145
    bh = 0.042
    bx_mid = bx + bw / 2.0

    ax.add_patch(FancyBboxPatch(
        (bx, by), bw, bh,
        boxstyle="round,pad=0.001,rounding_size=0.008",
        facecolor="#E2E8F0", edgecolor="#CBD5E1", linewidth=0.9,
        transform=ax.transAxes, zorder=3,
    ))

    # Preenchimento da barra
    if step == 4:
        bar_t = max(0.0, min(1.0, (meas_p - 0.35) / 0.65))
        shown_y = R3[1] * bar_t
        fill_w = abs(shown_y) * (bw / 2.0)
        if fill_w > 0.001:
            fx = bx_mid if shown_y >= 0 else bx_mid - fill_w
            ax.add_patch(Rectangle(
                (fx, by), fill_w, bh,
                facecolor=COL_PY if shown_y >= 0 else COL_NEG,
                edgecolor="none", transform=ax.transAxes, zorder=4,
            ))
        # Marcador da ponta
        tip_x = bx_mid + shown_y * (bw / 2.0)
        ax.plot([tip_x, tip_x], [by - 0.008, by + bh + 0.008],
                color=COL_SLATE_DARK, lw=2.0, transform=ax.transAxes, zorder=6)
    else:
        # Indicador discreto do valor instantaneo de y antes da medicao
        preview_x = bx_mid + r_cur[1] * (bw / 2.0)
        ax.plot([preview_x, preview_x], [by - 0.004, by + bh + 0.004],
                color="#94A3B8", lw=1.6, ls="--", transform=ax.transAxes, zorder=5)

    # Linha central 0 e rotulos -1, 0, +1
    ax.plot([bx_mid, bx_mid], [by - 0.008, by + bh + 0.008],
            color="#475569", lw=1.2, transform=ax.transAxes, zorder=5)
    ax.text(bx, by - 0.028, "−1", ha="center", va="center", fontsize=9.2, fontweight="bold",
            color=COL_NEG if step == 4 else "#64748B", transform=ax.transAxes, zorder=4)
    ax.text(bx_mid, by - 0.028, "0", ha="center", va="center", fontsize=9.2, fontweight="bold",
            color="#475569", transform=ax.transAxes, zorder=4)
    ax.text(bx + bw, by - 0.028, "+1", ha="center", va="center", fontsize=9.2, fontweight="bold",
            color=COL_PY if step == 4 else "#64748B", transform=ax.transAxes, zorder=4)

    # Valor de leitura em destaque
    if step == 4:
        bar_t = max(0.0, min(1.0, (meas_p - 0.35) / 0.65))
        shown_y = R3[1] * bar_t
        p_plus = 0.5 * (1.0 + shown_y) * 100.0
        p_minus = 100.0 - p_plus
        ax.text(
            rx_p + rw_p / 2.0, c2_y + 0.072,
            f"⟨Y⟩ = {fmt_pt(shown_y, signed=True, decimals=2)}",
            ha="center", va="center", fontsize=14.0, fontweight="bold",
            color=COL_PY, transform=ax.transAxes, zorder=5,
        )
        ax.text(
            rx_p + rw_p / 2.0, c2_y + 0.026,
            f"P(|+i⟩) = {p_plus:.0f}%   |   P(|−i⟩) = {p_minus:.0f}%",
            ha="center", va="center", fontsize=8.9, fontweight="bold",
            color=COL_SLATE_MID, transform=ax.transAxes, zorder=5,
        )
    else:
        ax.text(
            rx_p + rw_p / 2.0, c2_y + 0.074, "Aguardando medição",
            ha="center", va="center", fontsize=10.2, fontweight="bold",
            color="#64748B", transform=ax.transAxes, zorder=5,
        )
        ax.text(
            rx_p + rw_p / 2.0, c2_y + 0.030, "Projeção no eixo Y ao final",
            ha="center", va="center", fontsize=8.8, color="#94A3B8",
            transform=ax.transAxes, zorder=5,
        )

    # -----------------------------------------------------------------------
    # Caixa de equacao inferior
    # -----------------------------------------------------------------------
    eq_box = FancyBboxPatch(
        (0.028, 0.030), 0.944, 0.118,
        boxstyle="round,pad=0.004,rounding_size=0.015",
        facecolor="#FFFFFF", edgecolor="#BFDBFE" if step != 4 else "#99F6E4", linewidth=1.2,
        transform=ax.transAxes, zorder=2,
    )
    ax.add_patch(eq_box)
    ax.text(
        0.50, 0.109, eq_top,
        ha="center", va="center", fontsize=11.8, fontweight="bold",
        color=COL_SLATE_DARK, transform=ax.transAxes, zorder=3,
    )
    ax.text(
        0.50, 0.057, eq_bot,
        ha="center", va="center", fontsize=10.0,
        color="#475569", transform=ax.transAxes, zorder=3,
    )

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor="#FFFFFF")
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")


def save_oneshot_gif(frames: list[Image.Image], out_path: Path, frame_ms: int = 40, final_hold_ms: int = 60000):
    """Salva GIF 1-shot (sem bloco NETSCAPE2.0) com pausa longa no ultimo quadro."""
    pal_frames = [
        im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        for im in frames
    ]
    durations = [frame_ms] * (len(pal_frames) - 1) + [final_hold_ms]
    # Omitir `loop` omite o bloco NETSCAPE2.0 -> reproduz 1 unica vez e para no quadro final
    pal_frames[0].save(
        out_path,
        save_all=True,
        append_images=pal_frames[1:],
        duration=durations,
        optimize=True,
        disposal=2,
    )
    print(f"Salvo GIF 1-shot: {out_path} ({len(pal_frames)} quadros, {frames[0].size})")


def save_loop_gif(frames: list[Image.Image], durations: list[int], out_path: Path):
    """Salva GIF continuo em loop (loop=0)."""
    pal_frames = [
        im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        for im in frames
    ]
    pal_frames[0].save(
        out_path,
        save_all=True,
        append_images=pal_frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"Salvo GIF loop  : {out_path} ({len(pal_frames)} quadros, {frames[0].size})")


def main():
    print(f"Estados exatos de Bloch:")
    print(f"  |0>  -> r0 = {np.round(R0, 4)}")
    print(f"  RX   -> r1 = {np.round(R1, 4)}")
    print(f"  RY   -> r2 = {np.round(R2, 4)}")
    print(f"  RZ   -> r3 = {np.round(R3, 4)}  (<Y> = {R3[1]:+.4f})")

    # Passo 0: Estado inicial |0> (PNG 300 DPI)
    img0_hi = render_frame(0, 1.0, dpi=300)
    p0_png = GIF_DIR / "09a_bloch_passo0_init.png"
    img0_hi.save(p0_png)
    print(f"Salvo PNG 300DPI: {p0_png} ({img0_hi.size})")

    steps_meta = [
        (1, "09b_bloch_passo1_rx"),
        (2, "09c_bloch_passo2_ry"),
        (3, "09d_bloch_passo3_rz"),
        (4, "09e_bloch_passo4_pauli_y"),
    ]

    # Quadros para GIF completo em loop (bonus)
    loop_frames: list[Image.Image] = []
    loop_durs: list[int] = []
    img0_lo = render_frame(0, 1.0, dpi=150)
    loop_frames.append(img0_lo)
    loop_durs.append(1200)

    n_motion_frames = 36  # 36 * 42ms = 1.51s de movimento suave
    frame_ms = 42

    for step_idx, stem in steps_meta:
        # 1) Quadros do GIF 1-shot (150 DPI -> 1140 x 810 px, nitido e leve)
        step_frames = [
            render_frame(step_idx, i / (n_motion_frames - 1), dpi=150)
            for i in range(n_motion_frames)
        ]
        # Repetir o ultimo quadro uma vez para seguranca de transicao antes do hold de 60s
        step_frames.append(step_frames[-1].copy())

        save_oneshot_gif(step_frames, GIF_DIR / f"{stem}.gif", frame_ms=frame_ms, final_hold_ms=60000)

        # 2) Quadro final estatico em 300 DPI (usado como capa de congelamento no PowerPoint)
        final_hi = render_frame(step_idx, 1.0, dpi=300)
        final_png = GIF_DIR / f"{stem}_final.png"
        final_hi.save(final_png)
        print(f"Salvo PNG 300DPI: {final_png} ({final_hi.size})")

        # 3) Acumular para o GIF completo em loop (amostra 18 quadros por passo para manter arquivo leve)
        sub_idx = np.linspace(0, n_motion_frames - 1, 20, dtype=int)
        for k, si in enumerate(sub_idx):
            loop_frames.append(step_frames[si])
            is_last = (k == len(sub_idx) - 1)
            loop_durs.append(2400 if (is_last and step_idx == 4) else (1200 if is_last else 55))

    # Salvar GIF completo continuo em loop (bonus)
    save_loop_gif(loop_frames, loop_durs, GIF_DIR / "09_esfera_bloch_completo_loop.gif")
    print("Concluido com sucesso!")


if __name__ == "__main__":
    main()
