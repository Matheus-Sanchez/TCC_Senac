# Relatório de Auditoria e Revisão do TCC2 com Base no Obsidian Vault (`TCC`)

**Data da auditoria:** 13/11/2026  
**Acervo de referência ("cérebro"):** `C:\Users\matheus.sduda\Documents\Obsidian Vault\TCC`  
**Arquivos revisados e atualizados no repositório:**
- [tcc2-adaptado.tex](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex) (`2.025` linhas)
- [tcc_math.bib](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc_math.bib) (`103` entradas válidas após limpeza)
- [apresentacao_tcc2_final.tex](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/apresentacao_tcc2_final.tex) (`905` linhas; Slides 16 e 17 atualizados)
- [notas_orador_tcc2.md](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/notas_orador_tcc2.md) (`72` linhas; inspecionado)

---

## 1. Panorama da Investigação no Obsidian Vault

A investigação completa do Obsidian Vault inventariou **31 pastas e 583 arquivos** (sendo **538 arquivos Markdown**), incluindo **32 PDFs** (`565` páginas com texto extraível) vinculados à wiki em [Auditoria do Acervo.md](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/Wiki/Topicos/Auditoria%20do%20Acervo.md), além de todo o lote adicional de 2026:

- **`10_Fontes`**: **76 arquivos**, dos quais **49 fichas** receberam conferência direta parcial contra os PDFs/fontes locais em `13/11/2026` (`23` da fila complementar e `26` da importação anterior), conforme [Andamento revisao direta 2026-11-13.md](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/90_Sistema/Andamento%20revisao%20direta%202026-11-13.md).
- **`Wiki\Fontes` e `Wiki\Topicos`**: **37 notas** em `Wiki\Fontes`, [Auditoria do Acervo.md](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/Wiki/Topicos/Auditoria%20do%20Acervo.md), [Citacoes para conferencia.md](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/Wiki/Topicos/Citacoes%20para%20conferencia.md) (99 blocos verificados, 77 literais e 22 para conferência manual) e [Reavaliacao das Fontes.md](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/Wiki/Topicos/Reavaliacao%20das%20Fontes.md) (auditoria semântica sobre 260 notas/32 PDFs em `05/11/2026`).
- **`Raw\Files`**: inventário de **32 referências novas** em [Referencias novas 2026-11-06.md](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/Raw/Files/Referencias%20bibliografia%202026-11-06/Referencias%20novas%202026-11-06.md) e leitura direta integral dos PDFs primários [an2024lenet5gtsrb.pdf](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/Raw/Files/Referencias%20bibliografia%202026-11-06/an2024lenet5gtsrb.pdf) (10 páginas) e [s41598-026-45140-w.pdf](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/Raw/Files/s41598-026-45140-w.pdf) (`daka2026noqcnn`, 23 páginas).

### Escopo documental no Vault × TCC2
- **Núcleo do TCC2**: fontes teóricas de visão computacional/QML e estudos empíricos vinculados às **9 bases de referência** (MNIST, Fashion-MNIST, KMNIST, EMNIST Balanced, CIFAR-10, CIFAR-100 Coarse, SVHN, GTSRB e FER2013).
- **Fontes legadas/paralelas no Vault fora do escopo comparativo do TCC2**: o Vault contém ainda fontes clínicas/mamográficas de etapa exploratória anterior (p. ex., `lee2017cbisddsm`, `nguyen2023vindr`, `bhalla2023mammographyreview`, `Bhole2025MammoBench`, `WHO2026BreastCancer`, `mckinney2020international`, `wu2020deep`, `gupta2025qmldigitalhealth`) e tópicos não avaliados nos experimentos (`thapak2020transformerpp`, `behrouz2024titans`, `watkins2023differentialprivacy`, `dallapozza2022qrl`), corretamente mantidos fora das tabelas comparativas das 9 bases.

### Diagnóstico bibliométrico antes e depois da revisão
- **Antes da revisão**: [tcc_math.bib](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc_math.bib) possuía **107 entradas**, das quais **100 chaves únicas** eram citadas em `530` ocorrências no [tcc2-adaptado.tex](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex), com **0 chaves indefinidas** e **7 entradas não citadas** (`ponti2017comofunciona`, `ibmQuantumMeasureQubits2026`, `ibmQuantumCircuitLibrary2026`, `thapak2020transformerpp`, `behrouz2024titans`, `watkins2023differentialprivacy`, `dallapozza2022qrl`).
- **Após a revisão**: o `.bib` foi enxugado para **103 entradas**, todas (**103 de 103**, `577` ocorrências de citação) devidamente citadas no texto, com **0 chaves faltantes** e **0 chaves órfãs**.

---

## 2. Acertos Verificados no TCC2

O cotejo sistemático com o Vault confirmou importantes qualidades que foram preservadas e fortalecidas:

1. **Separação estrita entre resultados próprios e literatura**: o TCC2 declara explicitamente em [tcc2-adaptado.tex#L1569](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L1569) e [tcc2-adaptado.tex#L1851](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L1851) que os resultados experimentais próprios (campanha de `30/10/2026`, medidos em **Macro-F1 de teste (%)**) não são equiparados diretamente às acurácias reportadas pelos artigos correlatos (em resoluções, partições e métricas distintas).
2. **Controle metodológico por gargalo clássico (`Dense20 vetorial Mac`)**: o desenho experimental ([tcc2-adaptado.tex#L1528-L1531](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L1528-L1531) e [L1856](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L1856)) isola o efeito da compressão dimensional (`u \in \mathbb{R}^n`) antes de comparar a CNN clássica ao modelo híbrido (`Híbrido Mac/PennyLane`, 4 circuitos independentes de 5 qubits).
3. **Detecção prévia de várias inconsistências clássicas e quânticas** já registradas antes desta rodada:
   - `kabir2023spinalnet`: valores exatos de média (`99,69%` MNIST, `99,05%` KMNIST, `90,73%` EMNIST Balanced) e máximos (`99,72%`, `99,15%`, `91,05%`), distinguindo explicitamente média de melhor execução ([kabir2023spinalnet--cd6b89b781.md](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/kabir2023spinalnet--cd6b89b781.md#L21)).
   - `khanday2021filter`: alerta sobre a divergência entre resumo (`93,68%`) e Tabela 3/conclusão (`92,68%` teste, `92,35%` validação) no Fashion-MNIST e entre Tabela 1 (`73,04%`) e texto corrido (`63,5%`) no CIFAR-10 ([ijai--a66f717cb1.md](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/ijai--a66f717cb1.md#L21)).
   - `chen2023handwritten`: alerta de que `89,36%` corresponde ao conjunto de **validação**, e não de teste ([chen2023handwritten--e0b9f8e1b9.md](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/chen2023handwritten--e0b9f8e1b9.md#L21)).
   - `riaz2023nnqe`: valores corretos de MNIST (`93,8%` vs `92,0%`), CIFAR-10 (`36,0%` vs `30,5%`) e GTSRB (`73,4%` vs `82,2%` clássico, usando o GTSRB como contraexemplo empírico de degradação quântica), conferidos em [riaz2023nnqe--8fbd8559ad.md](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/riaz2023nnqe--8fbd8559ad.md#L52-L58).
   - `long2025qcqcnn`: `98,85 ± 0,25%` vs `98,79 ± 0,13%` (MNIST binário 3 vs 5) e `99,41 ± 0,14%` (Fashion-MNIST binário), identificando o viés de tamanho de lote (`1` vs `4`).
   - `guo2018cnnrnn`: `88,23%` vs `85,38%` nas 20 superclasses oficiais do CIFAR-100 Coarse.
   - `huang2017densenet`: erro de teste `1,59%` (~`98,41%`) no SVHN com ressalva do conjunto extra de treino.
   - Integridade na não-citação do registro `C06` (Shen; Yang; Zhang, 2022) por não localização nas bases oficiais ([tcc2-adaptado.tex#L1958](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L1958)).

---

## 3. Erros e Inconsistências Encontrados e Corrigidos

### 3.1. Erro metodológico ao citar `daka2026noqcnn` e `schetakis2022qmlframeworks` na retropropagação conjunta de CNN+PQC
- **Problema original**: Em [tcc2-adaptado.tex#L1526](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L1526), afirmava-se que *"o otimizador clássico ajusta simultaneamente os pesos convolucionais $\phi$, a projeção de entrada $(W, b)$, os parâmetros quânticos $\theta$ e a cabeça de classificação $(W_c, b_c)$"*, citando `\cite{bergholm2018pennylane,schetakis2022qmlframeworks,long2025qcqcnn,daka2026noqcnn}`.
- **Evidência no PDF/Vault**: O PDF [s41598-026-45140-w.pdf](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/Raw/Files/s41598-026-45140-w.pdf) (`daka2026noqcnn`, pp. 1, 3 e 10) e [a-novel-quantum-convolutional-neural-network-framework-for-quantum-enhanced-classification--61912d32a1.md](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/Wiki/Fontes/a-novel-quantum-convolutional-neural-network-framework-for-quantum-enhanced-classification--61912d32a1.md) demonstram que a *No-QCNN* **não possui bloco CNN clássico intermediário** e utiliza o algoritmo **livre de derivadas COBYLA** sobre o VQC; já `schetakis2022qmlframeworks` foca comparações binárias em conjuntos sintéticos 2D/3D.
- **Correção aplicada**: Em [tcc2-adaptado.tex#L1526](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L1526), a citação da retropropagação ponta a ponta foi ajustada para `\cite{bergholm2018pennylane,qiskitMachineLearningTorchConnector2026,long2025qcqcnn}`, diferenciando explicitamente propostas sem CNN intermediária otimizadas com COBYLA (`daka2026noqcnn`) ou testadas em problemas sintéticos binários (`schetakis2022qmlframeworks`).

### 3.2. Caracterização incompleta e omissão de protocolo de `daka2026noqcnn` na Seção 2.8.2 e Quadro A.1
- **Problema original**: Em `tcc2-adaptado.tex` (L1645 e L2014 originais), `daka2026noqcnn` era resumido apenas como *"um conjunto sintético próprio de 50 imagens de linhas coloridas em 6 classes (relatando 82,05% de acurácia de validação)"*.
- **Evidência no PDF integral**: O PDF [s41598-026-45140-w.pdf](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/Raw/Files/s41598-026-45140-w.pdf) (Tabelas 3 e 5, pp. 15 e 19) revela dois cenários distintos (divisão 70:30, 16 qubits, COBYLA):
  1. **Binário (`4×4` linhas amarelas, 10 a 100 imagens)**: em 50 imagens (Tabela 3), No-QCNN alcança `89,7%` de validação (`73,14%` treino, `4866,43 s`, 100 iterações) contra `100%` da CNN clássica (`4,72 s`, 50 épocas).
  2. **6 classes (`8×8` RGB reduzido por PCA de 64 para 16 atributos, 50 a 100 imagens)**: em 50 imagens (Tabela 3), No-QCNN obtém `82,05%` de validação (`66,20%` treino, `3917,64 s`) contra `40,00%` da CNN clássica em 50 épocas (`4,36 s`); contudo, o **Apêndice B (Tabela 5, p. 19)** do próprio artigo mostra que a mesma CNN clássica atinge **86,67% de validação** (`97,14%` treino, em `8,42 s`) quando treinada por **100 épocas**.
- **Correção aplicada**: O parágrafo final da Seção 2.8.2 ([tcc2-adaptado.tex#L1645](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex)) e o item `Adic. 2` do Quadro A.1 foram reescritos com todos esses dados e com a ressalva do Apêndice B.

### 3.3. Ano errado da errata `bokhan2022corrigendum`
- **Problema original**: [tcc_math.bib](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc_math.bib) trazia `year = {2022}` para `bokhan2022corrigendum`.
- **Evidência no Vault**: [bokhan2022corrigendum--4e14b590c3.md](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/bokhan2022corrigendum--4e14b590c3.md#L21) comprova publicação em **18 de abril de 2023**.
- **Correção aplicada**: Atualizado para `year = {2023}` em [tcc_math.bib#L597-L606](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc_math.bib#L597-L606) e explicitado o ano `2023` na Seção 2.8.2 e no item `Q02` do Quadro A.1.

### 3.4. Três divergências DOI × título apontadas em `Referencias novas 2026-11-06.md`
Conforme [Referencias novas 2026-11-06.md#L36-L41](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/Raw/Files/Referencias%20bibliografia%202026-11-06/Referencias%20novas%202026-11-06.md#L36-L41):

| Chave | Achado original no TCC2 | Título associado ao DOI segundo o Vault | Ação aplicada |
| :--- | :--- | :--- | :--- |
| `kong2026cqnas` | Expandido como *Collaborative Quantum Neural Architecture Search* na lista de siglas ([L172](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L172)), Tabela 2.3 e `.bib` | *CQNAS: Convolutional quantum hybrid neural network architecture search for image classification* (`10.1016/j.neucom.2026.133236`) | Título corrigido na sigla (`L172`), no [tcc_math.bib#L670-L677](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc_math.bib#L670-L677), na Tabela 2.3, na Seção 2.8.2 e em `Adic. 6`. |
| `riaz2026emnist` | Título *Quantum-Enhanced Neural Network for Handwritten Character Recognition on EMNIST* sem ressalva | *Development of a Novel Quantum Pre-processing Filter to Improve Image Classification Accuracy of Neural Network Models* (`10.47852/bonviewJDSIS52024231`) | Nota explícita adicionada em [tcc_math.bib#L661-L668](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc_math.bib#L661-L668), na Tabela 2.3, na Seção 2.8.2 e em `Adic. 5`. |
| `alsubai2024quantumfer` | Título *Quantum-enhanced ResNet-18 for facial expression recognition* sem ressalva de DOI | *Facial emotion recognition using deep quantum and advanced transfer learning mechanism* (`10.3389/fncom.2024.1435956`) | Nota explícita adicionada em [tcc_math.bib#L679-L688](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc_math.bib#L679-L688), na Tabela 2.3, na Seção 2.8.2 e em `Adic. 7`. |

### 3.5. Ambiguidade entre `val_accuracy` e teste em `an2024lenet5gtsrb`
- **Evidência direta no PDF/ficha**: [an2024lenet5gtsrb.pdf](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/Raw/Files/Referencias%20bibliografia%202026-11-06/an2024lenet5gtsrb.pdf) (pp. 3–8) e [a-lightweight-network-architecture-for-traffic-sign-recognition-based-on-enhanced-lenet-5---b6c3a1fc18.md](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/a-lightweight-network-architecture-for-traffic-sign-recognition-based-on-enhanced-lenet-5---b6c3a1fc18.md) mostram que as imagens são convertidas para **tons de cinza 32×32** (`0,30R + 0,59G + 0,11B` + equalização de histograma + normalização `[-1, 1]`), a soma da Tabela 3 totaliza **414.443 parâmetros**, e na p. 8 a Tabela 8 rotula a linha sob `Test` como `val_accuracy` (`0.9753` para PReLU), enquanto a Tabela 9 reporta o mesmo `0.9753` no conjunto de teste.
- **Correção aplicada**: Incluída a especificação (`32×32` tons de cinza, `414.443` parâmetros e ambiguidade Tab. 8 `val_accuracy` vs. Tab. 9 teste) na Tabela 2.2 ([tcc2-adaptado.tex#L1592](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L1592)), Seção 2.8.1, Quadro A.1 (`C16`) e Slide 16 ([apresentacao_tcc2_final.tex#L398](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/apresentacao_tcc2_final.tex#L398)).

### 3.6. Inconsistências internas de fontes documentadas nas fichas de `13/11/2026`
Foram incorporadas ao TCC2 as ressalvas primárias verificadas em `10_Fontes`:
- **`nocentini2022fashionmnist`** ([nocentini2022fashionmnist--b29d8d7959.md#L21](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/nocentini2022fashionmnist--b29d8d7959.md#L21)): divergência interna para a MCNN15 entre `94,04%` na seção de resultados e `94,09%` na discussão e conclusão, além de testes externos de `60%` e `40%` restritos a 100 e 50 imagens.
- **`cohen2017emnist`** ([cohen2017emnist--bb2240174d.md#L21](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/cohen2017emnist--bb2240174d.md#L21)): erro tipográfico na Tabela II da p. 4 do artigo original (imprime `37` classes para *Letters* embora o texto especifique `26`), além de `78,02% ± 0,09%` com OPIUM.
- **`goodfellow2013fer2013`** ([goodfellow2013fer2013--f860d2771c.md#L21](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/goodfellow2013fer2013--f860d2771c.md#L21)): esclarecimento de que `70,22%` refere-se ao subconcurso *black-box*, enquanto o desempenho humano estimado na FER2013 é `65 ± 5%`.
- **`riaz2023nnqe`** ([riaz2023nnqe--8fbd8559ad.md#L21](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/riaz2023nnqe--8fbd8559ad.md#L21)): explicitação de que CIFAR-10 e GTSRB foram convertidos para **escala de cinza** e confrontados apenas com rede densa (*fully connected*), adicionando também os valores comparativos do QuanvNN (`93,0%` MNIST, `34,9%` CIFAR-10, `71,9%` GTSRB).

---

## 4. Lacunas Preenchidas e Fontes Pendentes

### 4.1. Dados e restrições de protocolo incorporados ao TCC2
Diversos estudos citados anteriormente de forma genérica foram enriquecidos com os números e limitações verificados nas fichas de `13/11/2026`:

- **`bokhan2022qcnn`** ([bokhan2022qcnn--4b7bec4c2c.md](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/bokhan2022qcnn--4b7bec4c2c.md)) e Slide 17 ([apresentacao_tcc2_final.tex#L418](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/apresentacao_tcc2_final.tex#L418)): incluídos **ambos** os recortes de 4 classes em `16×16` com codificação por amplitude (`149` parâmetros na QCNN vs. `188` na CNN): MNIST `(3,4,5,6)` (`85,14%` vs `94,25%`) e `(0,1,2,3)` (`90,03%` vs `95,85%`); Fashion-MNIST `(0,1,2,3)` (`85,93%` vs `89,69%`) e `(1,2,8,9)` (`93,63%` vs `97,42%`).
- **`zhao2024qksan`** ([zhao2024qksan--72edf42da3.md#L21](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/zhao2024qksan--72edf42da3.md#L21)): `99%` (MNIST) e `98,05%` (Fashion-MNIST) são médias dos últimos 10 passos em tarefa **binária (`0 vs 1`)**, PCA para 8 dimensões, apenas `1.000` treino e `100` teste, em simulação sem ruído.
- **`shi2025qsan`** ([shi2025qsan--325c9499c2.md#L21](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/shi2025qsan--325c9499c2.md#L21)): `100%` refere-se ao MNIST **binário (`0 vs 1`)**, imagens reduzidas para `4×4`, com `50` amostras de treino e `30` de teste.
- **`easommccaldin2024singlequbit`** ([16890985d339c094--16890985d3.md#L21](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/16890985d339c094--16890985d3.md#L21)): `94,6%` (filtro `3×3`) e `95,8%` (filtro `4×4`) no MNIST binário, `89,5%` no Fashion-MNIST binário e queda para `72,1%` no MNIST de **3 classes** (`6` parâmetros por filtro).
- **`song2024resourceefficient`** ([song2024resourceefficient--f4cb8d1c2d.md#L21](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/song2024resourceefficient--f4cb8d1c2d.md#L21)): faixa `92,20% a 92,94%` (média `92,59%`) em 5 inicializações e natureza teórica da redução de complexidade.
- **`abosamra2021optimized`** (`10_Fontes`, 13/11/2026): médias individuais de `95,91%` (*Letters*) e `90,90%` (*Balanced*), chegando a `95,98%` e `91,06%` em comitê de 5 modelos (`40×40` -> `224×224`, 3 canais).
- **`tanveer2021darts`** ([tanveer2021darts--8108ce920d.md#L21](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/tanveer2021darts--8108ce920d.md#L21)): `97,52%` CIFAR-10 (`3,9M`), `84,10%` CIFAR-100 (`3,9M`) e `96,91%` Fashion-MNIST (`3,2M`), esclarecendo que `1 GPU-day` refere-se apenas à etapa de busca.
- **`wei2024lightweightgtsrb`** ([wei2024lightweightgtsrb--d0f8b3e1c4.md#L21](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/10_Fontes/wei2024lightweightgtsrb--d0f8b3e1c4.md#L21)): ConvNeSe com `99,99%` na verificação (7:3 em `224×224`), precisão/revocação/F1 `>= 98%`, e `26,87M` parâmetros / `4,46G` FLOPs frente a `0,9M` e `0,21G` da ENet.
- **`lecun1998gradient`**, **`clanuwat2018kmnist`**, **`netzer2011svhn`**, **`kabir2023spinalnet`**, **`guo2018cnnrnn`**, **`huang2017densenet`**: complementados com contagens de parâmetros/conexões da LeNet-5 (`~60.000` e `345.308`), médias por classe no KMNIST (`95,12%` / `97,82%` / `98,83%`), SVHN original (`90,6%` vs `98,0%` humano), VGG-19 Spinal FC em CIFAR-10/100 (`91,40%` / `64,77%`), erro fino do `guo2018cnnrnn` (`20,86%`) e DenseNet-BC em CIFAR-10/100 (`3,46%` / `17,18%`).

### 4.2. Pendências documentais remanescentes no Vault
1. **7 referências marcadas como pendentes de PDF local** em [Referencias novas 2026-11-06.md](file:///C:/Users/matheus.sduda/Documents/Obsidian%20Vault/TCC/Raw/Files/Referencias%20bibliografia%202026-11-06/Referencias%20novas%202026-11-06.md): `stallkamp2012gtsrb`, `mukhamediev2024fashionmnist`, `li2021autofernet`, `dong2025weightremapping`, `riaz2026emnist`, `kong2026cqnas` e `alsubai2024quantumfer`.
2. **Registros preliminares não citados no Quadro A.1** aguardando leitura integral futura: `C13`, `C14`, `C15`, `C19`, `Q04` e `Q06` (além de `C06`, não localizado).

---

## 5. Citações Faltantes Adicionadas e Limpeza do `tcc_math.bib`

### 5.1. Seções do [tcc2-adaptado.tex](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex) onde faltavam referências

| Seção / Subseção | Diagnóstico anterior | Referências inseridas na revisão |
| :--- | :--- | :--- |
| `2.2` introdução ([L351–354](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L351-L354)) | 0 citações | `gonzalez2008digital`, `szeliski2022computer` |
| `2.2.1` Caracteres e dígitos ([L355–360](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L355-L360)) | Só `LeCun2015` | `lecun1998gradient`, `cohen2017emnist`, `clanuwat2018kmnist`, `netzer2011svhn` |
| `2.2.2` Vestuário, objetos e placas ([L361–366](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L361-L366)) | Só `gonzalez2008digital`, `szeliski2022computer` | `xiao2017fashionmnist`, `krizhevsky2009learning`, `stallkamp2012gtsrb` |
| `2.2.3` Expressões faciais ([L367–372](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L367-L372)) | Só `goodfellow2013fer2013` em `L371` | `goodfellow2013fer2013` (intro), `li2021autofernet` |
| `2.3` e `2.3.1` Bases de referência ([L373–382](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L373-L382)) | 0 citações | `Wazlawick2020`, `goodfellow2016deep`, `LeCun2015`, `mcclean2018barren`, `schuld2021effect` |
| `2.4.5` Seleção de métricas ([L894–899](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L894-L899)) | 0 citações | `fawcett2006roc`, `sokolova2009systematic`, `silva2025balanceamento`, `hand2001simple` |
| `2.5` Redes neurais ([L934](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L934)) | `ponti2017comofunciona` órfã no `.bib` | Incorporada `ponti2017comofunciona` |
| `2.6.1` Medição quântica ([L1255](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L1255)) | `ibmQuantumMeasureQubits2026` órfã no `.bib` | Incorporada `nielsen2010quantum`, `ibmQuantumMeasureQubits2026` |
| `2.6.2` Circuitos parametrizados ([L1289](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L1289)) | `ibmQuantumCircuitLibrary2026` órfã no `.bib` | Incorporada `cerezo2021variational`, `ibmQuantumCircuitLibrary2026` |
| `2.7.5` e `2.7.6` Gargalo e comparação ([L1528–1536](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L1528-L1536)) | Pouco lastreadas em protocolo/implementação | `Wazlawick2020`, `cerezo2021variational`, `LeCun2015`, `bergholm2018pennylane` |
| `2.8` introdução ([L1564–1570](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L1564-L1570)) | 0 citações | `Wazlawick2020`, `fawcett2006roc`, `sokolova2009systematic` |
| `Cap. 4` introdução ([L1848–1851](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L1848-L1851)) | 0 citações | `Wazlawick2020`, `fawcett2006roc`, `sokolova2009systematic` |
| `Apêndice A` introdução ([L1942–1945](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc2-adaptado.tex#L1942-L1945)) | 0 citações | `Wazlawick2020` |

*Observação transparente*: seções puramente estruturais/administrativas (`Objetivo geral`, `Cronograma de trabalho`, `Conclusão`) ou já apoiadas por referência específica (`Métricas de custo computacional e estabilidade experimental` com `goodfellow2016deep`; `Explicabilidade...` com `selvaraju2020gradcam`; `Configuração dos 72 modelos...` com `Wazlawick2020`; `Desempenho comparativo em Macro-F1...` com `bergholm2018pennylane`) foram mantidas como estão.

### 5.2. Destino das 7 entradas originalmente não citadas no [tcc_math.bib](file:///C:/Users/matheus.sduda/repos/TCC/TCC_Senac/tcc_math.bib)
- **3 chaves pertinentes integradas ao texto**: `ponti2017comofunciona` (`L934`), `ibmQuantumMeasureQubits2026` (`L1255`) e `ibmQuantumCircuitLibrary2026` (`L1289`).
- **4 chaves fora de escopo removidas do `.bib`**: `thapak2020transformerpp` (*Transformer++*), `behrouz2024titans` (*Titans: Learning to Memorize at Test Time*), `watkins2023differentialprivacy` (*Quantum machine learning with differential privacy*) e `dallapozza2022qrl` (*Quantum reinforcement learning: the maze problem*).


---

## Atualização completa — Revisão Matemática, Pré-Textual e Bibliográfica (17/11/2026)

Esta atualização complementa a conferência de 13/11/2026 incorporando as adições do Vault de 16/11/2026 (`gradient-based-learning-applied-to-document-recognition` / `lecun1998gradient`, `krizhevsky2009learning`, `deisenroth2020mathematics`, `goodfellow2016deep` e o lote de 14 páginas em `Raw/Files/Documentacao oficial PennyLane e Qiskit 2026-11-16/`), além da formalização matemática completa e da criação da **Lista de Fórmulas Matemáticas**.

### 1. Alterações na Bibliografia (`TCC_Senac/tcc_math.bib`)
- **Atualização de URLs oficiais da IBM Quantum**: `ibmQuantumCircuitLibrary2026`, `ibmQuantumMeasureQubits2026`, `ibmQuantumRealAmplitudes2026`, `ibmQuantumVisualizeCircuits2026` e `ibmQuantumAerSimulation2026` atualizadas para `https://quantum.cloud.ibm.com/docs/en/...` conforme `manifesto.json`.
- **Novas entradas oficiais de documentação (2026-11-16)**:
  - `ibmQuantumPrimitives2026`: documentação oficial sobre primitivas exatas e de estimação/amostragem (`StatevectorEstimator`, `StatevectorSampler` vs. `AerSimulator`).
  - `pennylaneDocsTorch2026`: documentação oficial da interface PyTorch do PennyLane (`QNode(interface="torch")`, `TorchLayer` e promoção numérica `float32 -> float64`).
- **Complemento em `cohen2017emnist`**: inclusão de nota bibliográfica com o título do depósito arXiv.
- **Estado final**: `110` entradas em `tcc_math.bib`, todas citadas em `tcc2-adaptado.tex` (`111` entradas no `.blg` contando `abntex2-options`), com **0 citações indefinidas**, **0 chaves não utilizadas** e **0 warnings** no BibTeX.

### 2. Listas Pré-Textuais (`TCC_Senac/tcc2-adaptado.tex`)
- **Nova `Lista de Fórmulas Matemáticas`** (inserida em `longtable` imediatamente após a `Lista de Abreviaturas e Siglas` e antes do sumário): indexa **todas as 83 equações numeradas** do trabalho em ordem sequencial (`Equação (2.1)` a `Equação (4.1)`), com correspondência exata **1-para-1** entre os rótulos `\label{eq:...}` do corpo do texto e as referências hiperlinkadas `\eqref{eq:...}`.
- **Ampliação da `Lista de Abreviaturas e Siglas`**: inclusão em ordem alfabética de `DBN`, `FLOPs`, `MLP`, `PCA`, `RBF`, `RBM`, `SGD`, `SVC`, `SVD`, `VQC` e `ZCA`.

### 3. Numeração, Deduplicação e Adição de Fórmulas Matemáticas
- Todos os blocos anteriormente não numerados (`\[...\]`) no Capítulo 2 foram convertidos para ambientes `\begin{equation}\label{eq:...}` (restam **0** blocos `\[...\]` no arquivo `.tex`).
- Blocos matemáticos repetidos em seções consecutivas (Seções 2.4.1–2.5.4) foram unificados e substituídos por referências cruzadas `\eqref{...}`.
- **Novas formulações matemáticas inseridas** (cobrindo lacunas teóricas e a formalização experimental nos Capítulos 2, 3 e 4):
  - **Capítulo 2**: `eq:ir_cv` (razão de desbalanceamento `IR` e coeficiente de variação `CV`), `eq:auc_multiclasse_hand_till` (medida multiclasse `M` de Hand & Till), `eq:fourier_qml` (representação em série parcial de Fourier de modelos variacionais quânticos), `eq:parameter_shift` (regra de deslocamento de parâmetros), `eq:zca_whitening` (branqueamento ZCA em `krizhevsky2009learning`).
  - **Capítulo 3**: `eq:pqc_ramo_4x5` (circuito completo de cada ramo independente de 5 qubits com codificação $R_X$ e 3 camadas $R_Z$--$R_Y$--$R_Z$ + `CNOT` circular), `eq:pauli_y_custo_404` (medição Pauli-$Y$ e cálculo das $4 \times (1 + 2(5+45)) = 404$ avaliações por amostra de treino via *parameter-shift*), `eq:contagem_parametros` (contagem paramétrica exata de `CNN`, `D20-img`, `Vet`, `Hib` e `P_ext(C)`), `eq:calibracao_nll_brier_ece` (NLL, escore de Brier multiclasse e ECE em 10 faixas), `eq:bayes_f1_posterior` (modelagem bayesiana marginal com priori de Jeffreys $\text{Dirichlet}(0{,}5)$, posterior Beta e $F_1 = 2q/(1+q)$), `eq:queda_margem_oclusao` (margem de *logit* e queda causal $\Delta m(x^{(b)})$ na oclusão em grade $8 \times 8$).
  - **Capítulo 4**: `eq:speedup_operacional` (fator de aceleração operacional $S_{A/B} = T_B / T_A$ entre plataformas e simuladores).

### 4. Correções Factuais, Citações, Ressalvas e `hyperref`
- **Correção factual em `netzer2011svhn` (Seção 2.8.1)**: corrigida a atribuição de `90,6%` no SVHN de teste, que pertence ao método *K-means*, enquanto autoencoders esparsos empilhados obtiveram `89,7%` (frente a `85,0%` HOG, `63,3%` WDCH e `98,0%` desempenho humano).
- **Refinamento em `wei2024lightweightgtsrb` (Seção 2.8.1 e Apêndice A, `C17`)**: precisão, revocação e F1 registrados a partir de `0,980` (`98,0%`, em vez de afirmação estrita `>= 98%` ambígua), explicitando que a Tabela 5 traz apenas parâmetros (`26,87M` vs. `0,9M` da ENet) e FLOPs (`4,46G` vs. `0,21G`), sem tempos de inferência.
- **Enriquecimentos e ressalvas de conferência direta**:
  - `goodfellow2016deep` (contexto histórico de volume de dados e otimização);
  - `zhao2024improvedpooling` (`T-Max-Avg` pooling) e `selvaraju2020gradcam` (distinção explícita entre erros top-1 de classificação e localização);
  - `biamonte2017qml` (gargalos de entrada/saída de dados em QML e necessidade de comparação justa) e `perezsalinas2020data` (caráter teórico construtivo da aproximação universal em 1 qubit);
  - `lecun1998gradient` (`0,95%` -> `0,8%` com distorções, `0,7%` *Boosted LeNet-4*), `xiao2017fashionmnist` (catálogo Zalando sem produtos brancos; médias em 5 embaralhamentos na Tab. 3: `0,897` SVC RBF e `0,871` MLP ReLU), `cohen2017emnist` (`78,02 ± 0,09%` na p. 5 vs. `78,02 ± 0,92%` na Tab. III da p. 9), `krizhevsky2009learning` (80M imagens minúsculas, 79k termos WordNet, ZCA, RBMs/DBNs com CD-1 e ressalva de que os experimentos desse relatório restringem-se ao CIFAR-10), `he2016resnet` (ResNet-110 `6,43%`, média `6,61 ± 0,16%`, ResNet-1202 `7,93%`, ImageNet top-5 `3,57%`, atualizados também em `C10`) e `cubuk2019autoaugment` (`1,5%` CIFAR-10, `1,0%` SVHN, `83,5%` top-1 ImageNet, `6,4% -> 5,2%` Stanford Cars, atualizados também em `C12`).
- **`hyperref` em títulos com matemática**: substituídos títulos das Seções `3.4.4`, `4.3` e `4.7` usando `\texorpdfstring{...}{...}`, eliminando todos os warnings de símbolos matemáticos em *bookmarks* PDF.

### 5. Verificação Final da Compilação
- Ciclo executado em 17/11/2026: `pdflatex` → `bibtex` → `pdflatex` (×3).
- Saída: `TCC_Senac/tcc2-adaptado.pdf` (**145 páginas**, `17.127.460` bytes), saída com código `0`.
- Auditoria de logs e auxiliares (`.log`, `.blg`, `.aux`):
  - **0 erros** de LaTeX ou BibTeX;
  - **0 citações indefinidas**, **0 chaves não utilizadas** em `tcc_math.bib`, **0 warnings** no BibTeX;
  - **0 referências ou equações indefinidas (`??`)** e correspondência exata de **83/83** equações (`eq:ir_cv` [`2.1`] até `eq:speedup_operacional` [`4.1`]);
  - Restam apenas 3 warnings estruturais do próprio template `abntex2`/`babel`/`memoir` (nenhum warning matemático de `hyperref`).

---

## Atualização — Enriquecimento Teórico Quântico e Substituição das Figuras em 300 DPI (18/11/2026)

Revisão completa dos capítulos teóricos de Computação Quântica, QML e Modelos Híbridos (`Seções 2.6, 2.7 e 2.8.2`) em `TCC_Senac/tcc2-adaptado.tex` guiada pelo Obsidian Vault e pelos artigos locais em `TCC_Senac/artigos/`, acompanhada da geração de 6 figuras didáticas inéditas (300 DPI, português) em `TCC_Senac/figuras/` via `TCC_Senac/gerar_figuras_revisao_tcc2.py`.

### 1. Novas Figuras (300 DPI, Português) e Inspeção Visual
Substituíram-se 4 capturas antigas de baixa resolução/inglês e acrescentaram-se 2 novas figuras conceituais nas Seções `2.6` e `2.7` (mantendo atualização nos nomes legados `qubit_portas_probabilidades.png`, `simulacao_qiskit_fluxo.png` e `modelo_hibrido_quantico_classico.png`):
- `fig_conceitos_qubit_esfera_bell.png` (Figura 9, Seção `2.6.1`, substitui `ibm_visualize_circuits_latex.png`): Esfera de Bloch, circuito de Bell $|\Phi^+\rangle$ com rotações de base e contraste entre regime exato (*statevector*) e amostragem binomial por *shots* ($\propto 1/\sqrt{S}$).
- `fig_codificacao_dados_e_qir.png` (Figura 10, Seção `2.6.3`, substitui `qiskit_ml_torch_connector_qnn_circuit.png`): *Amplitude/Angle/Data Re-uploading*, Núcleos Quânticos (QKM), Diferença Geométrica $g_{CQ}$ (`egginger2024hyperparameter`) e QIRs (QL, FRQI $\mathrm{PSNR}_m \approx 10\log_{10}(m)+9{,}94\text{ dB}$, NEQR $E_N = N H_N$ segundo `okada2025measurementlimits`).
- `fig_vqa_ciclo_e_parameter_shift.png` (Figura 11, Seção `2.6.4`, substitui `ibm_real_amplitudes_1.png`): laço híbrido VQA com bloco *N-local*/*RealAmplitudes* e comparação geométrica da regra *parameter-shift* frente a diferenciação adjunta e diferenças finitas.
- `fig_barren_plateaus_escalabilidade.png` (Figura 12, Seção `2.6.5`, figura nova): paisagem treinável vs. platô estéril, escalonamento da variância $\mathcal{O}(2^{-n})$ em *2-designs* vs. custos locais rasos ($n=5$) e canais de Kraus ($T_1$, $T_2$, despolarizante).
- `fig_fluxo_simulacao_pennylane_qiskit_gpu.png` (Figura 13, Seção `2.6.6`, substitui `qiskit_aer_cuquantum_workflow_faj2023.png`): fluxo unificado PennyLane + Qiskit V2 + otimizações *gate fusion*/*cache blocking* em CPU/GPU (`cuStateVec`, `cuTensorNet`) e consumo exponencial `complex128` ($16\cdot 2^n$ bytes).
- `fig_taxonomia_modelos_hibridos_visao.png` (Figura 14, Seção `2.7`, figura nova): taxonomia das 4 famílias arquiteturais híbridas para classificação de imagens destacando o desenho paralelo $4\times 5$ qubits de `senokosov2024qml`.

### 2. Aprofundamento Conceitual e Equações (`TCC_Senac/tcc2-adaptado.tex`)
- **Seção `2.6` e `2.6.1`**: quatro gargalos de QML (*input*, *output*, *costing*, *benchmarking*; `biamonte2017qml`), era NISQ / *entanglement frontier* / *quantum chasm* (`preskill2018nisq`), esfera de Bloch (`eq:esfera_bloch`), matriz densidade, pureza e entropia de von Neumann (`eq:matriz_densidade`), e erro estatístico por *shots* (`eq:erro_shots`).
- **Seção `2.6.2` e `2.6.3`**: decomposição geral de Euler $\mathcal{R}(\alpha,\beta,\gamma)$ (`eq:euler_rotacao`), codificação em amplitude vs. angular e QRAM (`eq:amplitude_encoding`), núcleos RDM projetados e Diferença Geométrica $g_{CQ}$ (`eq:diferenca_geometrica`), teorema da não clonagem em *data re-uploading*, e limites de leitura QIR para FRQI (`eq:frqi_psnr`) e NEQR (`eq:neqr_cupons`).
- **Seção `2.6.4`, `2.6.5` e `2.6.6`**: VQE, QAOA, QNG, diferenciação adjunta vs. *parameter-shift*, concentração de medida pelo lema de Lévy em *2-designs* (`eq:variancia_bp`), evolução ruidosa via operadores de Kraus (`eq:operadores_kraus`), e simulação via redes tensoriais (MPS/PEPS) vs. vetor de estado com *gate fusion* e *cache blocking*.
- **Seção `2.7` e `2.8.2` + `tcc_math.bib`**: adicionada taxonomia das quatro famílias híbridas na Seção `2.7`; adicionada a entrada verificada `@article{xiang2024qccnn}` em `tcc_math.bib` e discutida na Seção `2.8.2` com ressalva explícita de domínio tabular clínico (GBSG, SEER, WDBC), fora das nove bases de visão computacional do TCC.
- **Listas Pré-Textuais**: ampliada a `Lista de Abreviaturas e Siglas` (`COBYLA`, `GD`, `HQNN`, `MPS`, `PEPS`, `PSNR`, `QIR`, `QKM`, `QL`, `QNG`, `QRAM`, `RDM`, `VQA`, `VQE`) e sincronizada a `Lista de Fórmulas Matemáticas` com **93/93** equações numeradas (correspondência sequencial 1-para-1 exata e **0** blocos `\[...\]`).

### 3. Verificação Final da Compilação (18/11/2026)
- Ciclo executado: `pdflatex` → `bibtex` → `pdflatex` × 2.
- Saída: `TCC_Senac/tcc2-adaptado.pdf` (**159 páginas**, `19.011.866` bytes), código de saída `0`.
- Auditoria automática: **93/93** equações em ordem exata, **0** blocos `\[...\]`, **112** referências em `tcc_math.bib` + `abntex2-options` (**113** entradas citadas, **0** chaves não usadas, **0** warnings no BibTeX), **0** citações/referências indefinidas (`??`).
