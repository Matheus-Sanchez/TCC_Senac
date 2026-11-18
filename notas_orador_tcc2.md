# Notas do orador — TCC2 (40 min)

Arquivos dos slides: [apresentacao_tcc2_final.tex](file:///c:/Users/matheus.sduda/repos/TCC/TCC_Senac/apresentacao_tcc2_final.tex) (PDF) e [apresentacao_tcc2_final.pptx](file:///c:/Users/matheus.sduda/repos/TCC/TCC_Senac/apresentacao_tcc2_final.pptx) (PowerPoint editável) · Tempo falado: **36:30** + 3:30 de reserva. Os números de slide seguem o rodapé do PDF e do `.pptx`.

> [!IMPORTANT]
> Frase-guia (repita no início e no fim): *"Comparei CNN, CNN com gargalo de 20 dimensões e CNN com cabeça quântica simulada em 9 bases. O híbrido é estável e competitivo, mas o controle clássico mostra que não há vantagem quântica comprovada."*

## Abertura (1:00)
**1 · Capa (0:30)** Apresentar-se, citar orientador (**Prof. Samuel Mendes Sanches Junior**) e coorientador (**Prof. Thyago Conchado Quintas**), dizer o tema em uma frase.
**2 · Roteiro (0:30)** "Seis blocos: problema, fundamentos, literatura, desenvolvimento, resultados e conclusão."

## 1. Introdução (4:30)
**3 · Contexto (1:15)** Classificação de imagens é fundamental; CNNs dominam; QML promete algo novo, mas na era NISQ tem limites. Fechar com a pergunta: *como se comparam em vários domínios?*
**4 · Problema e justificativa (1:15)** Literatura de QML testa em recortes pequenos (3 vs. 5 no MNIST, 4 classes), só com acurácia, e compara com lotes diferentes. Justificativa em três dimensões: tecnológica, acadêmica e metodológica.
**5 · Objetivos (1:15)** Ler o objetivo geral. Resumir os objetivos específicos em 3 eixos: bases e pipeline, modelos, avaliação.
**6 · Hipótese e delimitações (0:45)** Hipótese: estável e competitivo, **sem** prometer superioridade. Delimitação-chave: imagens estáticas 2D e circuitos exclusivamente simulados (sem QPU física).

## 2. Fundamentação (8:30) — ritmo direto, só o necessário
**7 · Imagem como matriz (0:45)** Imagem = matriz/tensor. Nossas bases variam em tamanho e canais.
**8 · Métricas (1:15)** Explicar TP/FP/FN, F1 por classe e Macro-F1 = média igual entre classes. "Por isso escolhi Macro-F1: GTSRB, FER2013 e SVHN são desbalanceadas."
**9 · Convolução e pooling (0:45)** Filtro desliza e detecta padrão local; pooling reduz tamanho.
**10 · Mapas de características `FMAP3` (0:45)** Mostrar Fashion-MNIST (bota, 100,00%, 62/128 ativos) vs. FER2013 (happy, 97,40%, 63/128 ativos): bordas em B1–B2, abstração semântica até B5 pré e vetor `features128` via GAP.
**11 · Pipeline composto de aumento de dados (0:45)** Seis etapas determinísticas (`src/data_prep/data.py`): translação `REFLECT`, zoom, brilho, contraste, ruído $\sigma=0{,}005$ e *cutout* 8%, com mapas $|\Delta|$ e RMS (`0,2967` no GTSRB; `0,1084` no CIFAR-10).
**12 · Preservação semântica e `flip_lr=False` (0:45)** Mostrar `aug_03`: espelhar horizontalmente inverte direção/símbolos em GTSRB (cl. 34), MNIST (`3`), EMNIST (`R`) e SVHN (`5`), mantendo invariância só em objetos naturais (CIFAR-10). Registrar com transparência que checkpoints FP32 legados usaram `flip_lr=True` e o código atual foi corrigido para `flip_lr=False`.
**13 · Qubits e circuitos (0:45)** Superposição, portas H/X/CNOT, medição. *Dizer: figura da documentação IBM, apenas ilustrativa.*
**14 · Codificação e ansatz (1:00)** Feature map codifica dado clássico; ansatz tem rotações treináveis. *Dizer: figuras Qiskit ilustrativas; experimento implementado com PennyLane e Qiskit Aer.*
**15 · Simulação e limites (1:00)** $2^n$ estados: 20 qubits ($2^{20}$) são caros; *barren plateaus*. Por isso a decisão de decompor em 4×5 qubits.

## 3. Trabalhos correlatos (4:00)
**16 · Revisão (1:00)** Funil: 5.925 → 3.297 → 1.025 → 28 verificados. Ressaltar: mapeamento *preliminar* + conferência manual da fonte primária.
**17 · Clássicos (1:00)** CNNs bem estabelecidas: 99% em dígitos, ~73% em CIFAR-10 e FER2013. Avisar que acurácia ≠ Macro-F1.
**18 · Quânticos (1:15)** Recortes binários/4 classes; NNQE cai no GTSRB (73,4% vs. 82,2% clássico). **CIFAR-100 Coarse: nenhum estudo confirmado nas 20 superclasses.**
**19 · Lacuna (0:45)** Três pontos: protocolos fragmentados, só acurácia, variáveis de confusão. Minha contribuição responde aos três.

## 4. Desenvolvimento (9:30)
**20 · Tipo de pesquisa (0:45)** Aplicada, quantitativa, exploratória/descritiva/comparativa. Ler a pergunta de pesquisa.
**21 · Pipeline (0:45)** Seis etapas, de inventário e partições SHA-256 até auditoria (Macro-F1, calibração, Grad-CAM, oclusão 8×8) e telemetria.
**22 · Bases (1:00)** Destacar diversidade: 7 a 47 classes, cinza e RGB. Partições estratificadas (70/15/15) são da campanha, não as oficiais.
**23 · Equilíbrio (1:00)** Três regimes de IR (Seção 3.4.1). FER2013: 16,43× (desgosto com 547 imagens). Validação e teste mantêm a distribuição original.
**24 · Balanceamento e escolha de `all_raw` (1:00)** 36 execuções na CNN original (lote 512, `mixed_fp16`, 88,86 h): `all_raw` tem a maior média (`82,464%`) e mediana (`92,010%`) em `22,46 h`; `undersample` colapsa em FER2013 (`−19,28 p.p.`) e GTSRB (`−13,69 p.p.`); `class_weight` cai `−6,12 p.p.` no FER2013; `oversample` soma `+15,1%` de tempo (`9,90 h` vs. `5,20 h` no GTSRB).
**25 · Pré-processamento e auditoria (0:45)** Mesma preparação para todos os modelos. Limitações auditadas: GTSRB com 3.990/5.876 imagens de teste compartilhando *track* com treino; FER2013 com 378 duplicatas exatas no teste e 57 grupos com conflito de rótulo.
**26 · Três famílias (0:45)** CNN original (`SeparableConv2D + GroupNormalization(16) + SiLU`), `Dense20` (controle) e híbrido 4×5 qubits. 72 checkpoints = 9×8.
**27 · Arquitetura clássica (0:45)** Mostrar o diagrama separado: extrator comum (`66.905`/`67.019` pesos) exportando `features128` (`.npy`) e os 3 fluxos clássicos.
**28 · Cabeça híbrida (1:15)** Seguir o diagrama separado da esquerda para a direita: `features128` → `Dense(128, ReLU)` → `Dense(20, linear)` → 4 subcircuitos de 5 qubits (`RX` + 3 blocos `RZ-RY-RZ` + `CNOT` circular) → medição **Pauli-Y ($\langle Y \rangle \in [-1, 1]^{20}$)** → linear. 180 pesos quânticos (`19.272 + 21K` na cabeça), `404` avaliações no treino / `4` na validação, **sem emaranhamento entre os blocos**.
**29 · Protocolo (0:45)** 100 épocas (Adam, $\eta=3\times 10^{-4}$, `seed=42`), seleção em validação, Macro-F1 e critérios de auditoria.
**30 · Dois ambientes computacionais (0:45)** Apresentar as tabelas completas das **duas máquinas físicas**: (1) Estação Windows / WSL2 Ubuntu 22.04.5 LTS (`i7-14700K`, `15 GiB` RAM WSL, `RTX A2000 12GB`, CUDA 13.2, TF 2.21.0 / Keras 3.12.4) e (2) iMac `Mac16,3` Apple M4 (`macOS 15.5`, `16 GB` unificada, `.venv` CPython 3.12.3, TF 2.18.1 + Metal, PyTorch 2.8.0, PennyLane 0.44.1, Qiskit 2.3.0 / Aer 0.17.2).

## 5. Resultados (8:00)
**31 · Tabela Macro-F1 (1:00)** Guiar o olhar: coluna Híbrido vs. CNN e vs. `Dense20`. Mostrar proximidade e citar o asterisco do GTSRB.
**32 · Gráfico de $\Delta$ (1:00)** Barras azuis (vs. CNN) parecem ganhos; barras laranja (vs. `Dense20`) ficam em torno de zero. Médias: `+0,23` e `−0,01 p.p.`
**33 · Papel do `Dense20` (1:15)** *Slide-chave:* EMNIST `+0,755` vs. CNN, mas `Dense20` já chega a `88,642`. O ganho vem da projeção de 20 dimensões, não do circuito.
**34 · Complexidade do domínio (1:00)** O domínio governa: 99% → 73% → 47% (CIFAR-100 Coarse e FER2013).
**35 · GTSRB (0:45)** 99,4%–99,6% refletem a sobreposição de *tracks* na partição, não generalização para placas inéditas.
**36 · Explicabilidade global (0:45)** 73.728 oclusões 8×8: média constante provoca mais trocas que borramento (pico 23,4% CIFAR-100 Coarse); Spearman Grad-CAM vs. oclusão tem mediana $\rho = 0{,}002$.
**37 · Painéis causais RGB (0:45)** `gtsrb_07_media` (híbridos preveem cl. 10 com sensibilidade no símbolo, queda até `+9,02`) e `cifar100_coarse_01_desfoque` (híbridos trocam 3/64 para *flowers* ao borrar o inseto).
**38 · Painéis causais monocromáticos (0:45)** `fashion_mnist_06_media` (fronteira instável cl. 2 vs. cl. 6: até 31/64 trocas nos híbridos) e `mnist_06_desfoque` (sensibilidade na base do dígito "2" levando à predição "7").
**39 · Custo computacional (0:45)** 36 híbridos = `503,66 h` (`20,99` dias) vs. 18 vetoriais = `558,88 s` (`9,31 min`) — **778× a 2.854×** mais lento. Pico de `54,93 h` (EMNIST Win/Qiskit). iMac M4 até `3,18×` mais rápido no PennyLane.
**40 · Síntese (0:30)** Três ✓ e um ✗: estável, competitivo, sem vantagem quântica; sem atribuição causal pela semente única.

## 6. Conclusão (3:00)
**41 · Retomada (0:45)** Responder à pergunta e à hipótese. Repetir a frase-guia.
**42 · Contribuições (0:45)** Quatro pontos: campanha/revisão nas 9 bases (CIFAR-100 Coarse), controle `Dense20`, decomposição 4×5 qubits e auditoria crítica.
**43 · Limitações e futuro (0:45)** Multi-seed, GTSRB *track-aware*, emaranhamento/cuQuantum, paridade de parâmetros e ruído NISQ/QPUs reais.
**44 · Obrigado (0:45)** Agradecer aos orientadores e abrir para perguntas da banca.

---

## Slides de apoio no Apêndice (A1–A7) e respostas prontas para arguição

| Pergunta / Tópico | Resposta curta e slide de apoio |
|---|---|
| **Sobreamostragem e subamostragem (A1)** | Ilustração das estratégias de balanceamento de Silva (2025) que embasam o experimento de 36 execuções da Seção 3.4. |
| **Calibração e confiança nos erros (A2)** | No FER2013, `CNN FP32` (`label smoothing`) tem ECE `2,08%` e `42,76%` de confiança nos erros; sobre `features128` congeladas sem *temperature scaling*, `Vet Mac` sobe para ECE `31,43%` (`75,45%` nos erros) e `PQC Mac PL` para ECE `36,62%` (`82,82%` nos erros). |
| **Gradientes e ruído/*shots* (A3)** | MNIST decai naturalmente de `0,13` para `10⁻⁷`; FER2013 segue ativo (`0,043–0,113`) até a época 100. Sob ruído de canal até `2,0` (fidelidade `0,51`) e `256` *shots*, a variação típica em Macro-F1 é `< 0,10 p.p.` (máx. `−0,38 p.p.` no CIFAR-10). |
| **Telemetria Windows × macOS e simuladores (A4)** | iMac M4 foi `1,43×–3,18×` mais rápido que Windows no PennyLane e `1,07×–1,79×` no Qiskit; PennyLane foi `2,64×–2,74×` mais rápido que Qiskit no Mac, com uso estável de `383,9%–385,0%` de CPU (~4 núcleos) e pico de RSS entre `2,40` e `3,28 GiB`. |
| **Por que não houve vantagem quântica?** | Diferenças vs. `Dense20` ficam entre `−0,44` e `+0,62 p.p.`, com uma semente e cabeças de parametrização diferente. |
| **Por que 4 circuitos de 5 qubits?** | Um circuito de 20 qubits exige $2^{20}$ amplitudes por amostra: intratável para treinar nas 9 bases. Custo: sem emaranhamento entre ramos. |
| **Por que Pauli-Y em vez de Pauli-Z?** | A medição configurada nos 4 circuitos (`circuit.txt` / `model_summary.txt`) extrai os 20 valores esperados do observável $\langle Y \rangle \in [-1, 1]$ antes da camada linear final. |
| **Por que Macro-F1?** | Pesa todas as classes igualmente; acurácia esconde falhas em classes minoritárias (FER2013, GTSRB, SVHN). |
| **O GTSRB é confiável?** | Só como consistência interna: 3.990 de 5.876 imagens de teste compartilham *track* com o treino. Refazer com divisão *track-aware*. |
| **Rodou em hardware quântico?** | Não; apenas simulação ideal local (`default.qubit` / Aer). Modelos de ruído NISQ no treino e QPU física estão nos trabalhos futuros (A6). |
