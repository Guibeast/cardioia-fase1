"""CardioIA - Fase 1 / Parte 3: coleta e inventario do corpus visual (ECG).

Fonte: https://huggingface.co/datasets/Amarsaish/ecg_images (publico, sem token).

O mirror mistura DOIS conjuntos com origens diferentes, medido em 20/08/2026:
  - 523 imagens 227x227 RGB (~41 KB) -> corpus entregue, vai para assets/ecg/
  - 136 capturas de tela RGBA/RGB de 624x300 a 1678x778 (~700 KB), 114 MB no
    total -> ficam em _interno/, fora do repositorio.
O criterio de corte e MEDIDO, nao a extensao do arquivo: uma delas
(data/train/normal/5.jpg) tem extensao .jpg mas e captura de 1280x596.
Todas as 659 sao medidas e entram no inventario; a coluna no_repositorio separa.

Reexecutar nao rebaixa o que ja existe.
"""

import csv
import json
import shutil
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

REPO = "Amarsaish/ecg_images"
API = f"https://huggingface.co/api/datasets/{REPO}"
RAW = f"https://huggingface.co/datasets/{REPO}/resolve/main/"

RAIZ = Path(__file__).resolve().parent.parent
ECG = RAIZ / "assets" / "ecg"
FORA = RAIZ / "_interno" / "ecg_png_alta_resolucao"
AMOSTRAS = RAIZ / "assets" / "amostras"
INVENTARIO = RAIZ / "data" / "inventario_imagens.csv"

SPLIT = {"train": "treino", "test": "teste"}
CLASSE = {"normal": "normal", "myocardial infarctions": "infarto"}


def listar():
    """[(caminho_no_hf, split_pt, classe_pt)] das imagens do repositorio."""
    dados = json.load(urllib.request.urlopen(API))
    itens = []
    for s in dados["siblings"]:
        p = Path(s["rfilename"])
        if p.suffix.lower() not in (".jpg", ".png") or len(p.parts) != 4:
            continue
        _, split, classe, _ = p.parts
        itens.append((s["rfilename"], SPLIT[split], CLASSE[classe]))
    return sorted(itens)


def destino(remoto, split, classe):
    nome = Path(remoto).name
    base = ECG if nome.lower().endswith(".jpg") else FORA
    return base / split / classe / nome


def baixar(item):
    alvo = destino(*item)
    if alvo.exists() and alvo.stat().st_size > 0:
        return alvo
    alvo.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(RAW + urllib.parse.quote(item[0])) as r, open(alvo, "wb") as f:
        shutil.copyfileobj(r, f)
    return alvo


PADRAO = ((227, 227), "RGB")


def separar(itens):
    """Move para fora de assets/ tudo que nao bate com o padrao 227x227 RGB."""
    for remoto, split, classe in itens:
        atual = destino(remoto, split, classe)
        with Image.open(atual) as im:
            padrao = (im.size, im.mode) == PADRAO
        certo = (ECG if padrao else FORA) / split / classe / atual.name
        if atual != certo:
            certo.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(atual), str(certo))


def inventariar(itens):
    linhas = []
    for remoto, split, classe in itens:
        alvo = destino(remoto, split, classe)
        if not alvo.exists():
            alvo = (FORA if alvo.is_relative_to(ECG) else ECG) / split / classe / alvo.name
        with Image.open(alvo) as im:
            largura, altura = im.size
            modo, formato = im.mode, im.format
        linhas.append({
            "arquivo": alvo.relative_to(RAIZ).as_posix(),
            "classe": classe,
            "split_origem": split,
            "largura_px": largura,
            "altura_px": altura,
            "modo_cor": modo,
            "canais": len(Image.new(modo, (1, 1)).getbands()),
            "formato": formato,
            "bytes": alvo.stat().st_size,
            "no_repositorio": "sim" if ((largura, altura), modo) == PADRAO else "nao",
            "origem_hf": remoto,
        })
    linhas.sort(key=lambda l: l["arquivo"])
    with open(INVENTARIO, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)
    return linhas


def amostrar(linhas, n_por_classe=4):
    """4 normais + 4 infartos do split de teste, renomeadas para leitura humana."""
    AMOSTRAS.mkdir(parents=True, exist_ok=True)
    nomes = []
    for classe in ("normal", "infarto"):
        pool = [l for l in linhas if l["classe"] == classe
                and l["split_origem"] == "teste" and l["no_repositorio"] == "sim"]
        for i, l in enumerate(sorted(pool, key=lambda x: x["arquivo"])[:n_por_classe], 1):
            alvo = AMOSTRAS / f"{classe}_{i:02d}.jpg"
            shutil.copyfile(RAIZ / l["arquivo"], alvo)
            nomes.append(alvo.name)
    return nomes


def amostrar_alta(linhas):
    """2 exames em alta resolucao (1/1) para o README contrastar com os 227x227."""
    alvo_dir = AMOSTRAS / "alta_resolucao"
    alvo_dir.mkdir(parents=True, exist_ok=True)
    nomes = []
    for classe in ("normal", "infarto"):
        pool = [l for l in linhas if l["classe"] == classe and l["no_repositorio"] == "nao"]
        l = max(pool, key=lambda x: x["largura_px"] * x["altura_px"])
        alvo = alvo_dir / f"{classe}_{l['largura_px']}x{l['altura_px']}.png"
        shutil.copyfile(RAIZ / l["arquivo"], alvo)
        nomes.append(alvo.name)
    return nomes


def resumo(linhas):
    entregues = [l for l in linhas if l["no_repositorio"] == "sim"]
    for titulo, grupo in (("TOTAL medido", linhas), ("no repositorio", entregues),
                          ("fora (medida)", [l for l in linhas if l["no_repositorio"] == "nao"])):
        mb = sum(l["bytes"] for l in grupo) / 2**20
        print(f"{titulo:16} n={len(grupo):4}  {mb:6.1f} MB  "
              f"{dict(Counter(l['classe'] for l in grupo))}")
    print("  resolucao entregue:", dict(Counter((l["largura_px"], l["altura_px"]) for l in entregues)))
    print("  modo entregue:", dict(Counter(l["modo_cor"] for l in entregues)))
    print("  split entregue:", dict(Counter(l["split_origem"] for l in entregues)))
    p = [l for l in linhas if l["no_repositorio"] == "nao"]
    if p:
        print(f"  fora: {min(l['largura_px'] for l in p)}x{min(l['altura_px'] for l in p)} a "
              f"{max(l['largura_px'] for l in p)}x{max(l['altura_px'] for l in p)}, "
              f"modos {dict(Counter(l['modo_cor'] for l in p))}, "
              f"formatos {dict(Counter(l['formato'] for l in p))}")
    return entregues


if __name__ == "__main__":
    itens = listar()
    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(baixar, itens))
    separar(itens)
    linhas = inventariar(itens)
    entregues = resumo(linhas)
    print("amostras:", amostrar(linhas))
    print("amostras alta resolucao:", amostrar_alta(linhas))

    assert len(entregues) >= 100, "enunciado exige 100+ imagens"
    assert all(l["canais"] in (1, 3) for l in entregues)
    assert len({(l["largura_px"], l["altura_px"]) for l in entregues}) == 1, "corpus entregue nao e homogeneo"
    assert len(list(AMOSTRAS.glob("*.jpg"))) == 8
    assert len(list((AMOSTRAS / "alta_resolucao").glob("*.png"))) == 2
    assert sum(l["bytes"] for l in entregues) < 90 * 2**20, "peso excede o limite do GitHub sem LFS"
    print("OK")
