#!/usr/bin/env python3
"""Regenerate the figures in figures/ from the data in this repository (light and dark variants).
usage: python3 figures/make_figures.py        (needs matplotlib)"""
import json, os
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "figures")
THEMES = {
    "light": dict(surface="#fcfcfb", ink="#0b0b0b", ink2="#52514e", muted="#898781", grid="#e1e0d9",
                  axis="#c3c2b7", empty="#f0efec", mark="#2a78d6"),
    "dark": dict(surface="#1a1a19", ink="#ffffff", ink2="#c3c2b7", muted="#898781", grid="#2c2c2a",
                 axis="#383835", empty="#262624", mark="#3987e5"),
}
CASES = [("C17_8_3", "(17,8,3)", 17, "runs/C17_8_3_b17/results.jsonl", "data/links_16_7.json", "coverings/C17_8_3_b18.txt"),
         ("C20_10_3", "(20,10,3)", 20, "runs/C20_10_3_b14/results.jsonl", "data/links_19_9.json", "coverings/C20_10_3_b15.txt")]


def style(ax, t):
    ax.set_facecolor(t["surface"])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(t["axis"])
    ax.tick_params(colors=t["muted"], labelsize=9, length=0)
    ax.xaxis.label.set_color(t["ink2"]); ax.yaxis.label.set_color(t["ink2"])


def fig_coverings(t, name):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), gridspec_kw=dict(width_ratios=[17, 20]))
    fig.patch.set_facecolor(t["surface"])
    for ax, (_, label, v, _, _, cov) in zip(axes, CASES):
        B = [sorted(map(int, l.split())) for l in open(os.path.join(ROOT, cov)) if l.strip()]
        M = np.zeros((len(B), v))
        for i, b in enumerate(B):
            M[i, b] = 1
        for i in range(len(B)):
            for j in range(v):
                ax.add_patch(plt.Rectangle((j + 0.08, i + 0.08), 0.84, 0.84, linewidth=0,
                                           facecolor=t["mark"] if M[i, j] else t["empty"]))
        ax.set_xlim(0, v); ax.set_ylim(len(B), 0); ax.set_aspect("equal")
        ax.set_xticks([x + 0.5 for x in range(0, v, 4)]); ax.set_xticklabels(range(0, v, 4))
        ax.set_yticks([y + 0.5 for y in range(0, len(B), 3)]); ax.set_yticklabels(range(1, len(B) + 1, 3))
        style(ax, t); ax.spines["bottom"].set_visible(False)
        ax.set_xlabel("point"); ax.set_ylabel("block")
        ax.set_title(f"{len(B)}-block {label} covering", color=t["ink"], fontsize=11, loc="left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), facecolor=t["surface"])
    plt.close(fig)


def fig_instances(t, name):
    fig, axes = plt.subplots(2, 2, figsize=(10, 5.6))
    fig.patch.set_facecolor(t["surface"])
    for col, (_, label, _, res, _, _) in enumerate(CASES):
        R = [json.loads(l) for l in open(os.path.join(ROOT, res))]
        for row, (key, xl, scale) in enumerate([("solve_s", "CaDiCaL time per formula (s)", 1),
                                                 ("drat_bytes", "DRAT proof size per formula (kB)", 1e-3)]):
            ax = axes[row, col]
            x = np.array([r[key] * scale for r in R])
            bins = np.logspace(np.log10(x.min() * 0.9), np.log10(x.max() * 1.1), 30)
            ax.hist(x, bins=bins, color=t["mark"], rwidth=0.85)
            ax.set_xscale("log")
            ax.grid(axis="y", color=t["grid"], linewidth=0.6); ax.set_axisbelow(True)
            style(ax, t); ax.set_xlabel(xl, fontsize=9)
            if col == 0:
                ax.set_ylabel("formulas", fontsize=9)
            if row == 0:
                ax.set_title(f"{label}: {len(R)} formulas, all UNSAT", color=t["ink"], fontsize=11, loc="left")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), facecolor=t["surface"])
    plt.close(fig)


def fig_links(t, name):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), gridspec_kw=dict(width_ratios=[4, 8]))
    fig.patch.set_facecolor(t["surface"])
    for ax, (_, label, v, _, links, _) in zip(axes, CASES):
        d = json.load(open(os.path.join(ROOT, links)))
        seqs = Counter()
        for c in d["classes"]:
            deg = sorted((bin(m).count("1") for m in c["masks"]), reverse=True)
            s = "$" + r"\ ".join(f"{k}^{{{n}}}" if n > 1 else f"{k}" for k, n in sorted(Counter(deg).items(), reverse=True)) + "$"
            seqs[s] += 1
        items = sorted(seqs.items(), key=lambda kv: -kv[1])
        y = np.arange(len(items))
        ax.barh(y, [n for _, n in items], height=0.7, color=t["mark"])
        for yi, (_, n) in zip(y, items):
            ax.text(n, yi, f" {n}", va="center", ha="left", fontsize=9, color=t["ink2"])
        ax.set_yticks(y); ax.set_yticklabels([s for s, _ in items], fontsize=9)
        ax.invert_yaxis()
        style(ax, t); ax.spines["bottom"].set_visible(False); ax.set_xticks([])
        ax.set_title(f"link classes for {label}: {len(d['classes'])}\n(point-degree sequence)", color=t["ink"],
                     fontsize=11, loc="left")
        ax.tick_params(axis="y", colors=t["ink2"])
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), facecolor=t["surface"])
    plt.close(fig)


if __name__ == "__main__":
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "none"})
    for mode, t in THEMES.items():
        fig_coverings(t, f"coverings_{mode}.svg")
        fig_instances(t, f"instances_{mode}.svg")
        fig_links(t, f"links_{mode}.svg")
    print("wrote figures to", OUT)
