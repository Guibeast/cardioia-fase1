"""CardioIA - Fase 1 | Geracao da base numerica.

Bloco 1  auditoria de proveniencia do UCI Heart Disease (funil 920 -> 297)
Bloco 2  base clinica principal (Kaggle heart.csv)
Bloco 3  camada de telemetria IoT SIMULADA, semente fixa
Bloco 4  asserts e relatorio de vies por sexo

Uso: python data/gerar_dataset.py
"""

import io
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).parent
UCI_ZIP = "https://archive.ics.uci.edu/static/public/45/heart+disease.zip"
COLUNAS_UCI = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
               "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"]
ORIGENS = {"cleveland": "Cleveland (EUA)", "hungarian": "Hungarian (Hungria)",
           "switzerland": "Switzerland (Suica)", "va": "VA Long Beach (EUA)"}

rng = np.random.default_rng(42)


# --- Bloco 1: auditoria de proveniencia -------------------------------------

def baixar_uci():
    """Retorna {origem: DataFrame cru} das 4 bases processadas do UCI."""
    with urllib.request.urlopen(UCI_ZIP, timeout=60) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    bases = {}
    for chave in ORIGENS:
        with z.open(f"processed.{chave}.data") as f:
            bases[chave] = pd.read_csv(f, header=None, names=COLUNAS_UCI)
    return bases


def auditar(bases, destino):
    linhas = ["AUDITORIA DE PROVENIENCIA - UCI Heart Disease (ID 45)",
              f"Fonte: {UCI_ZIP}",
              f"Data de execucao: {pd.Timestamp.today():%Y-%m-%d}", "",
              "FUNIL DE COMPLETUDE POR ORIGEM", ""]
    total_bruto = total_completo = 0
    for chave, rotulo in ORIGENS.items():
        df = bases[chave]
        bruto = len(df)
        completo = int((df != "?").all(axis=1).sum())
        total_bruto += bruto
        total_completo += completo
        linhas.append(f"  {rotulo:<22} {bruto:>4} registros | {completo:>4} sem '?' "
                      f"({completo / bruto:.1%})")
    linhas += ["", f"  {'TOTAL':<22} {total_bruto:>4} registros | {total_completo:>4} "
                   f"sem '?' ({total_completo / total_bruto:.1%})", "",
               "AUSENCIAS ('?') POR VARIAVEL, TODAS AS ORIGENS", ""]
    juntas = pd.concat(bases.values(), ignore_index=True)
    for col in COLUNAS_UCI:
        faltas = int((juntas[col] == "?").sum())
        if faltas:
            linhas.append(f"  {col:<12} {faltas:>4} ausentes ({faltas / len(juntas):.1%})")
    zeros_chol = int((pd.to_numeric(bases["switzerland"]["chol"],
                                    errors="coerce") == 0).sum())
    linhas += ["", "OBSERVACAO CRITICA",
               f"  Switzerland registra colesterol = 0 em {zeros_chol}/"
               f"{len(bases['switzerland'])} pacientes. Zero fisiologicamente impossivel:",
               "  e ausencia codificada como zero, nao medicao. Tratar como dado faltante.",
               ""]
    texto = "\n".join(linhas)
    destino.write_text(texto, encoding="utf-8")
    print(texto)
    return total_bruto, total_completo


# --- Bloco 2: base clinica principal ----------------------------------------

def carregar_base():
    """Base clinica real: heart.csv do Kaggle (fedesoriano), 5 origens do UCI."""
    print()
    print("[base] heart_kaggle.csv (fedesoriano/Kaggle, 5 origens do UCI)")
    return pd.read_csv(AQUI / "heart_kaggle.csv")


# --- Bloco 3: camada IoT simulada -------------------------------------------

def acrescentar_iot(df):
    """Telemetria vestivel SIMULADA, correlacionada ao desfecho clinico."""
    n = len(df)
    doente = df["HeartDisease"].to_numpy()
    df.insert(0, "id_paciente", [f"PAC-{i:04d}" for i in range(1, n + 1)])
    # SpO2 cai em quadro cardiaco descompensado
    df["spo2_pct"] = np.clip(rng.normal(97 - 2 * doente, 1.5), 85, 100).round(1)
    # HRV (SDNN) reduzida e marcador consolidado de risco cardiovascular
    df["hrv_sdnn_ms"] = np.clip(rng.normal(55 - 18 * doente, 12), 10, 120).round(1)
    df["temp_corporal_c"] = np.clip(rng.normal(36.6, 0.3, n), 35.0, 38.5).round(1)
    df["dispositivo_iot"] = rng.choice(["wearable-A", "wearable-B", "holter-C"], n)
    df["data_coleta"] = (pd.to_datetime("2026-08-01")
                         + pd.to_timedelta(rng.integers(0, 30, n), "D")).date
    return df


# --- Bloco 4: verificacao e relatorio ---------------------------------------

def main():
    bases = baixar_uci()
    auditar(bases, AQUI / "auditoria_uci.txt")

    df = acrescentar_iot(carregar_base())

    assert len(df) >= 100, f"apenas {len(df)} linhas, minimo do enunciado e 100"
    assert df.isna().sum().sum() == 0, "ha celulas vazias no dataset final"
    assert df["id_paciente"].is_unique

    saida = AQUI / "cardioia_dataset.csv"
    df.to_csv(saida, index=False, encoding="utf-8")

    print(f"\n{saida.name}: {len(df)} linhas x {len(df.columns)} colunas, "
          f"{df.isna().sum().sum()} vazios")
    print("\nDISTRIBUICAO DO DESFECHO POR SEXO (dado da secao de Governanca)")
    vies = df.groupby("Sex")["HeartDisease"].agg(["count", "mean"])
    vies.columns = ["pacientes", "prevalencia"]
    print(vies.to_string(float_format=lambda v: f"{v:.1%}"))
    print(f"\nprevalencia geral: {df['HeartDisease'].mean():.1%}")


if __name__ == "__main__":
    main()
