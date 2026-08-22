# Fontes dos corpora textual e visual — CardioIA Fase 1 (Partes 2 e 3)

## Parte 2 — corpus textual

Dois documentos em português brasileiro sobre a **mesma doença** (isquemia miocárdica),
escritos para **públicos opostos**. O contraste entre eles é o objeto de estudo: o mesmo
conceito clínico aparece como `disfunção sistólica do ventrículo esquerdo` em um texto e
como `o coração fica fraco` no outro. Um modelo de PLN treinado só no registro técnico
não entende o paciente; treinado só no registro leigo, não entende o prontuário.

Ambos são de **acesso aberto**, sem login, e foram baixados na íntegra da fonte primária.

---

## `texto1-tecnico.txt` — registro técnico-científico

| Campo | Valor |
|---|---|
| Título | Uso da Inteligência Artificial Aplicada ao Eletrocardiograma para Diagnóstico de Disfunção Sistólica Ventricular Esquerda |
| Autores | Wilton Batista de Santana Júnior; Marcelo M. Pinto Filho; Sandhi Maria Barreto; Murilo Foppa; Luana Giatti; Rohan Khera; Antonio Luiz Pinho Ribeiro |
| Instituição | Universidade Federal de Minas Gerais (UFMG) — coorte ELSA-Brasil |
| Publicação | *Arquivos Brasileiros de Cardiologia*, v. 122, n. 4, e20240740, abr. 2025 |
| DOI | https://doi.org/10.36660/abc.20240740 |
| URL | https://www.scielo.br/j/abc/a/GRvMnbbzdLLyJzTCfjN577L/?lang=pt |
| Licença | Creative Commons Attribution (CC-BY) — declarada na própria página |
| Data de acesso | 20/08/2026 |
| Extensão | **20.503 caracteres**, 3.136 palavras, 75 parágrafos |
| Codificação | UTF-8, texto corrido, sem marcação |

**Por que este artigo.** É a interseção exata do projeto: IA aplicada a ECG, em coorte
**brasileira** (ELSA-Brasil, 2.567 indivíduos), publicada por revista nacional indexada.
Traz vocabulário métrico que o modelo precisa reconhecer — sensibilidade, especificidade,
VPP, VPN, ASC-ROC, razão de verossimilhança, *diagnostic odds ratio* — e um caso real de
prevalência baixa (FEVE < 40% em 1,13% da amostra), que é o mesmo problema de classe rara
que a nossa base numérica enfrenta.

**O que foi removido do arquivo baixado**, e por quê:
- o *abstract* em inglês e a *Central Illustration* — o corpus é deliberadamente monolíngue PT-BR;
- a lista de referências bibliográficas e os blocos de metadados do portal (datas de
  submissão, editor responsável, vinculação acadêmica) — são citações e navegação, não prosa clínica.

Nenhuma palavra foi reescrita, resumida ou traduzida. O texto restante é literal.

---

## `texto2-leigo.txt` — registro de divulgação ao público

| Campo | Valor |
|---|---|
| Título | Infarto |
| Autoria institucional | Ministério da Saúde — Governo Federal do Brasil |
| Publicação | Portal gov.br, seção Saúde de A a Z (©2025) |
| URL | https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/i/infarto |
| Licença | Conteúdo público do Governo Federal, reprodução permitida com citação da fonte |
| Data de acesso | 20/08/2026 |
| Extensão | **3.124 caracteres**, 494 palavras, 27 parágrafos |
| Codificação | UTF-8, texto corrido, sem marcação |

**Por que este texto.** É a linguagem em que o paciente descreve o próprio sintoma —
"dor no peito", "suor frio", "falta de ar", "mal-estar súbito" — e é exatamente essa a
entrada que um triador automatizado receberia por telefone ou chat. Também é a fonte
oficial dos números epidemiológicos brasileiros usados na descrição do projeto (300 a
400 mil infartos/ano; um óbito a cada 5 a 7 casos) e do fluxo do SAMU 192, que define a
janela de tempo em que qualquer modelo de triagem precisa responder.

**O que foi removido do arquivo baixado**: parágrafos repetidos pelo carrossel da própria
página, o rodapé institucional do portal (Ouvidoria-Geral do SUS, selo da Vaccine Safety
Net/OMS, aviso de copyright) e os elementos de navegação. Nada foi reescrito.

---

## Método de coleta

Download direto por HTTP das URLs acima em 20/08/2026, extração do texto com
`html.parser` da biblioteca padrão do Python e gravação em UTF-8 com quebras `\n`.
Os dois arquivos são recortes literais da fonte — o único processamento foi a remoção
dos blocos declarados acima.

## Assimetria proposital do corpus

O texto técnico é **6,6 vezes maior** que o leigo (20.503 contra 3.124 caracteres).
A assimetria é da natureza das fontes, não um defeito da coleta: a literatura científica
brasileira sobre cardiologia é abundante e a comunicação oficial ao paciente é curta e
padronizada. Qualquer treinamento sobre este corpus precisa ponderar as classes — caso
contrário o modelo aprende a falar como artigo e não como gente, que é o oposto do que
um assistente de triagem deve fazer.


---

# Parte 3 — corpus visual (ECG)

## Fonte primária

| Campo | Valor |
|---|---|
| Título | ECG Images dataset of Cardiac Patients |
| Autoria | Khan, Ali Haider (com Muzammil Hussain, citado na publicação derivada) |
| Instituição | Ch. Pervaiz Elahi Institute of Cardiology — Multan, **Paquistão** |
| Publicação | Mendeley Data, 19/03/2021 |
| DOI | https://doi.org/10.17632/gwbz3fsgp8.2 |
| Licença | **CC-BY 4.0** — confirmada na API do DataCite em 20/08/2026 (`rightsIdentifier: cc-by-4.0`) |
| Data de acesso | 20/08/2026 |

## Mirror efetivamente usado no download

| Campo | Valor |
|---|---|
| Repositório | `Amarsaish/ecg_images` — https://huggingface.co/datasets/Amarsaish/ecg_images |
| Acesso | público, não-*gated*, sem token; HTTP 200 em 20/08/2026 |
| Última modificação na origem | 05/10/2023 |
| Licença declarada no mirror | **nenhuma** — o card do dataset está vazio |
| Conteúdo | 659 imagens em `data/{train,test}/{normal, myocardial infarctions}/` |

**Por que isto importa.** O mirror não declara licença; quem redistribui sem verificar
está redistribuindo no escuro. A licença vem da fonte primária (CC-BY 4.0), que exige
atribuição — feita aqui e no README. Rastrear mirror → fonte primária → licença é
requisito de governança de dados, não formalidade.

## O que foi medido (não estimado)

Tudo abaixo saiu de `data/inventario_imagens.csv`, gerado por `data/baixar_imagens.py`
com Pillow sobre as 659 imagens baixadas.

| Grupo | N | Resolução | Modo | Peso | No repositório |
|---|---|---|---|---|---|
| Imagens padronizadas | **523** | 227×227 (todas) | RGB, 3 canais | 21,0 MB | sim → `assets/ecg/` |
| Exames em alta resolução | **136** | 624×300 a 1678×778 | RGBA (135) / RGB (1) | 114,5 MB | não |
| **Total do mirror** | **659** | — | — | 135,5 MB | — |

Distribuição do corpus entregue: **284 normal / 239 infarto** (54,3% / 45,7%),
sendo 363 do split `treino` e 160 do `teste` da origem. O split original foi preservado
na estrutura de pastas — refazer a divisão sem preservá-lo causaria vazamento de dados.

**Dois conjuntos, uma pasta.** O mirror mistura duas coleções: recortes 227×227 (resolução
de entrada do AlexNet) e os exames de 12 derivações completos, em alta resolução, dos quais
os recortes derivam. O corte entre eles foi feito **por medida, não por extensão**: o arquivo
`data/train/normal/5.jpg` tem extensão `.jpg` mas é uma captura de 1280×596 — foi para fora
do corpus entregue junto dos 135 `.png`. Treinar com as duas coleções misturadas ensinaria o
modelo a separar por origem da imagem, não por patologia.

**O que se perde a 227×227.** Nos exames em alta resolução as 12 derivações estão rotuladas
(I, II, III, aVR, aVL, aVF, V1–V6) sobre grade milimetrada calibrada. A 227×227 os rótulos
ficam ilegíveis e a grade não é mensurável: não há morfometria (supradesnivelamento de ST em
mm, intervalo QT) nem localização do território do infarto (anterior, inferior, lateral).
Restam textura e forma global da onda. Por isso a Parte 3 justifica **classificação por CNN**,
e não medida automatizada. Duas amostras em alta resolução ficam em
`assets/amostras/alta_resolucao/` exatamente para tornar essa perda visível.

## Por que os 114,5 MB de alta resolução ficaram fora

O repositório inteiro passaria de 135 MB, acima do que o GitHub aceita sem Git LFS. O corpus
entregue (523 imagens, 21 MB) já supera com folga o mínimo de 100 do enunciado e é homogêneo.
As 136 imagens excluídas continuam **inventariadas e citadas** em
`data/inventario_imagens.csv` com a coluna `no_repositorio = nao`, e `data/baixar_imagens.py`
rebaixa qualquer uma delas da fonte original em uma execução.

## Viés geográfico declarado

As três camadas do projeto vêm de populações diferentes: base numérica dos EUA e Europa
(Cleveland, Hungria, Suíça, VA Long Beach), corpus textual do Brasil (SciELO e Ministério da
Saúde) e corpus visual do **Paquistão** (centro único, Multan). Equipamento, protocolo de
aquisição e perfil de paciente diferem entre elas. Nenhum modelo treinado aqui pode ser
apresentado como validado para a população brasileira sem recalibração em dados locais.

## Método de coleta

`python data/baixar_imagens.py` — lista os arquivos pela API pública do Hugging Face,
baixa por HTTP em 8 conexões paralelas, mede cada arquivo com Pillow, separa os grupos
pelo padrão medido (227×227 RGB), escreve `data/inventario_imagens.csv` e copia 8 amostras
balanceadas (4 normal / 4 infarto, do split de teste) para `assets/amostras/`. É idempotente:
reexecutar não rebaixa o que já existe. Os asserts ao final falham se o corpus entregue cair
abaixo de 100 imagens, deixar de ser homogêneo ou passar de 90 MB.

---

# Parte 1 — base numérica

| Campo | Valor |
|---|---|
| Título | Heart Failure Prediction Dataset |
| Autoria | fedesoriano (consolidação) |
| Origem primária | UCI Heart Disease (ID 45) — Janosi, Steinbrunn, Pfisterer, Detrano, 1989 |
| URL | https://www.kaggle.com/datasets/fedesoriano/heart-failure-prediction |
| Licença | **ODbL 1.0** — *Database: Open Database, Contents: © Original Authors*, http://opendatacommons.org/licenses/odbl/1.0/ |
| Verificação | metadados estruturados da própria página, consultados em 20/08/2026 |
| Data de acesso | 20/08/2026 |
| Extensão | 918 linhas, 12 variáveis (11 preditoras + alvo) |

A ODbL exige **atribuição** e que qualquer banco derivado seja compartilhado sob a mesma
licença. `data/cardioia_dataset.csv` é banco derivado: a atribuição está no README e nesta
página, e a redistribuição segue a mesma licença. A auditoria de proveniência em
`data/auditoria_uci.txt` foi feita sobre a base original do UCI, de acesso irrestrito.
