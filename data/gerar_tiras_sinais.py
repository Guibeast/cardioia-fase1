"""
CardioIA — Fase 1: Batimentos de Dados
Script de geração da camada complementar de sinal bruto (Parte 3 — Dados Visuais).

Renderiza tiras de 10 segundos de sinais reais de ECG (bases públicas do
PhysioNet, distribuídas com o pacote oficial wfdb-python do MIT-LCP) como
imagens .png com grade de papel de ECG.

Uso:
    pip install wfdb matplotlib numpy
    git clone --depth 1 https://github.com/MIT-LCP/wfdb-python.git
    python gerar_tiras_sinais.py  (executar na pasta wfdb-python/sample-data)

Saída: ~108 imagens .png em ../assets/ecg_sinais/
"""

import os

import matplotlib
import numpy as np
import wfdb

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "ecg_sinais")
WIN = 10  # segundos por tira


def plot_strip(sig, fs, title, fname):
    """Desenha uma tira de ECG com grade estilo papel milimetrado."""
    t = np.arange(len(sig)) / fs
    fig, ax = plt.subplots(figsize=(12, 3), dpi=100)
    ax.set_facecolor("#fff5f5")
    ymin, ymax = np.nanmin(sig), np.nanmax(sig)
    pad = 0.15 * (ymax - ymin if ymax > ymin else 1)
    ymin, ymax = ymin - pad, ymax + pad
    for x in np.arange(0, t[-1] + 0.04, 0.04):  # grade fina (40 ms)
        ax.axvline(x, color="#f7caca", lw=0.3, zorder=0)
    for x in np.arange(0, t[-1] + 0.2, 0.2):  # grade grossa (200 ms)
        ax.axvline(x, color="#f0a0a0", lw=0.6, zorder=0)
    for y in np.linspace(ymin, ymax, 25):
        ax.axhline(y, color="#f7caca", lw=0.3, zorder=0)
    for y in np.linspace(ymin, ymax, 6):
        ax.axhline(y, color="#f0a0a0", lw=0.6, zorder=0)
    ax.plot(t, sig, color="#1a1a1a", lw=0.9, zorder=2)
    ax.set_xlim(0, t[-1])
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("mV")
    ax.set_title(title, fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, fname))
    plt.close(fig)


def main():
    os.makedirs(OUT, exist_ok=True)
    count = 0

    # 1) MIT-BIH Arrhythmia Database — registro 100 (MLII e V5, 360 Hz)
    rec = wfdb.rdrecord("100")
    fs = int(rec.fs)
    for li, lead in enumerate(rec.sig_name):
        n_strips = 25 if lead == "MLII" else 15
        for k in range(n_strips):
            s0 = k * WIN * fs * 4  # janelas espacadas para maior diversidade
            seg = rec.p_signal[s0 : s0 + WIN * fs, li]
            if len(seg) < WIN * fs:
                break
            count += 1
            plot_strip(seg, fs,
                       f"MIT-BIH 100 | Derivação {lead} | janela {k+1} (10 s)",
                       f"ecg_{count:03d}_mitbih100_{lead}_{k+1:02d}.png")

    # 2) PTB Diagnostic ECG — s0010_re (12 derivações, 1000 Hz)
    rec = wfdb.rdrecord("s0010_re")
    fs = int(rec.fs)
    for li, lead in enumerate(rec.sig_name[:12]):
        for k in range(3):
            s0 = k * WIN * fs
            seg = rec.p_signal[s0 : s0 + WIN * fs, li]
            if len(seg) < WIN * fs:
                break
            count += 1
            plot_strip(seg, fs,
                       f"PTB s0010_re | Derivação {lead.upper()} | janela {k+1} (10 s)",
                       f"ecg_{count:03d}_ptb_s0010_{lead}_{k+1:02d}.png")

    # 3) PhysioNet/CinC Challenge 2015 — a103l (II e V, 250 Hz)
    # 4) PhysioNet v102s (II e V, 250 Hz)
    for rname, spacing in [("a103l", 4), ("v102s", 3)]:
        rec = wfdb.rdrecord(rname)
        fs = int(rec.fs)
        for li, lead in enumerate(rec.sig_name[:2]):
            for k in range(8):
                s0 = k * WIN * fs * spacing
                seg = rec.p_signal[s0 : s0 + WIN * fs, li]
                if len(seg) < WIN * fs or np.all(np.isnan(seg)):
                    continue
                count += 1
                plot_strip(seg, fs,
                           f"PhysioNet {rname} | Derivação {lead} | janela {k+1} (10 s)",
                           f"ecg_{count:03d}_{rname}_{lead}_{k+1:02d}.png")

    print("Total de imagens geradas:", count)


if __name__ == "__main__":
    main()
