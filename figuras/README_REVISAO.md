# Inventário de Revisão das Figuras (`TCC_Senac/figuras/`)

Gerado automaticamente após a sincronização entre `tcc2-adaptado.tex` e os slides (`apresentacao_tcc2.tex`, `apresentacao_tcc2_final.tex`, `gerar_apresentacao_pptx.py`).

## Resumo Numérico
- **TCC escrito (`tcc2-adaptado.tex`):** 69 imagens únicas
- **Slides Beamer (`apresentacao_tcc2.tex`, 63 págs.):** 43 imagens únicas (+ `assets/logo-senac.png`)
- **Slides PPTX (`gerar_apresentacao_pptx.py`, 62 slides):** 35 imagens estáticas + 7 GIFs animados em `gifs/` (+ `assets/logo-senac.png`)
- **Presentes em ambos (TCC ∩ Slides Beamer):** 43 imagens (sendo 8 diagramas arquiteturais/`SeparableConv2D` promovidos para frames nativos `1204px` sem perdas extraídos diretamente dos GIFs `02..08`, e `fig_arq_etapa1_cnn_original.png` mantida em ambos)
- **Apenas no TCC escrito (`revisao_somente_tcc/`):** 26 imagens
- **Apenas nos slides atualmente:** 0 imagens
- **Antigas que existiam apenas nos slides (`revisao_somente_slides_antigas/`):** 8 imagens
- **Backups antes da substituição (`backup_substituidas/`):** 6 arquivos
- **Pendente de correção (`revisao_pendente/`):** 2 arquivos (PNG + GIF da Etapa 1)
- **GIFs ativos no PPTX (`gifs/`):** 7 arquivos
- **Outros arquivos de imagem legados na raiz de `figuras/` (fora `revisao_somente_slides_antigas/`):** 30 arquivos

## (a) Imagens presentes em ambos — TCC escrito e Slides (43)
| Imagem | Linha(s) em `tcc2-adaptado.tex` | Slide(s) em `apresentacao_tcc2.tex` |
| :--- | :--- | :--- |
| `aug_01_pipeline_etapas_gtsrb.png` | L1249 | Slide 13 (Aumento de dados: pipeline composto em 6 etapas) |
| `aug_02_pipeline_etapas_cifar10.png` | L1252 | Slide 13 (Aumento de dados: pipeline composto em 6 etapas) |
| `aug_03_comparacao_flip_lr_semantico.png` | L1224 | Slide 14 (Preservação semântica e \texttt{flip\_lr=False}) |
| `balanceamento_oversampling_silva2025.png` | L575 | Slide 58 (Apoio A1: sobreamostragem e subamostragem) |
| `balanceamento_undersampling_silva2025.png` | L580 | Slide 58 (Apoio A1: sobreamostragem e subamostragem) |
| `convolutional-pooling.png` | L1051 | Slide 9 (CNN: convolução e \textit{pooling}) |
| `equilibrio_classes_9_datasets.png` | L2057 | Slide 26 (Equilíbrio de classes: três regimes) |
| `fig_261_circuito_bell.png` | L1365 | Slide 15 (Qubits, superposição, emaranhamento e medição) |
| `fig_261_esfera_bloch.png` | L1324 | Slide 15 (Qubits, superposição, emaranhamento e medição) |
| `fig_263_codificacoes_vetoriais.png` | L1537 | Slide 16 (Codificação de dados e laço variacional (VQA)) |
| `fig_264_laco_vqa.png` | L1625 | Slide 16 (Codificação de dados e laço variacional (VQA)) |
| `fig_265_variancia_gradiente.png` | L1673 | Slide 17 (Simulação, \textit{barren plateaus} e escalabilidade) |
| `fig_266_fluxo_backends_simulacao.png` | L1711 | Slide 17 (Simulação, \textit{barren plateaus} e escalabilidade) |
| `fig_342_balanceamento_tempo_treino.png` | L2101 | Slide 27 (Modos de balanceamento: Macro-F1 e tempo (36 execuções)) |
| `fig_48_mac_hardware_io_complementar.png` | L2894 | Slide 52 (Telemetria complementar no iMac M4 (27 sessões, 1 ép.)) |
| `fig_48_mac_hardware_sensores_macmon.png` | L2906 | Slide 51 (Sensores \texttt{macmon} e energia no iMac M4) |
| `fig_48_telemetria_hardware_io.png` | L2848 | Slide 50 (Telemetria de hardware e I/O (campanha 100 épocas)) |
| `fig_48_tempos_etapas_consolidado.png` | L2682 | Slide 48 (Custo computacional por etapa (100 épocas, lote 128)) |
| `fig_arq_bloco_cnn_anatomia.png` | L2223 | Slide 32 (Bloco B3 — `1204×676` lossless do f10 de `05_zoom_bloco_cnn.gif`) |
| `fig_arq_comparativo_mudancas.png` | L2370 | Slide 37 (Comparativo — `1204×701` lossless do f23 de `08_comparativo_4_etapas.gif`) |
| `fig_arq_etapa1_cnn_original.png` | L2215 | Slide 31 (Etapa 1: CNN clássica de origem (FP32)) |
| `fig_arq_etapa2a_dense20_imagem.png` | L2279 | Slide 33 (Etapa 2A — `1204×679` lossless do f34 de `02_fluxo_dense20_imagem.gif`) |
| `fig_arq_etapa2b_dense20_vetorial.png` | L2287 | Slide 34 (Etapa 2B — `1204×679` lossless do f42 de `03_fluxo_classico_tanh.gif`) |
| `fig_arq_etapa3_hibrida_4x5.png` | L2305 | Slide 35 (Etapa 3 — `1204×679` lossless do f42 de `04_fluxo_hibrido_4xpqc.gif`) |
| `fig_arxiv2304_hqnn_parallel_arquitetura.jpg` | L1848 | Slide 18 (Modelo de referência: HQNN-Parallel (Senokosov et al., 2024)) |
| `fig_arxiv2304_mnist_loss_acc.png` | L1865 | Slide 61 (Apoio A4: resultados originais de Senokosov et al.\ (2024)) |
| `fig_balanceamento_macro_f1.png` | L2093 | Slide 27 (Modos de balanceamento: Macro-F1 e tempo (36 execuções)) |
| `fig_circuito_quantico_5qubits.png` | L2315 | Slide 36 (Circuito 5Q — `1204×676` lossless do f21 de `06_zoom_pqc_5qubits.gif`) |
| `fig_fatores_aceleracao_ambientes_simuladores.png` | L2718 | Slide 49 (Aceleração entre ambientes e simuladores) |
| `fig_funil_pesquisa.png` | L474 | Slide 19 (Como foi a revisão da literatura) |
| `fig_sepconv2d_etapa1_depthwise.png` | L1119 | Slide 10 (`1204×687` lossless do f3 de `07_sepconv_numerico.gif`; PPTX unifica em S10) |
| `fig_sepconv2d_etapa2_pointwise.png` | L1127 | Slide 11 (`1204×687` lossless do f33 de `07_sepconv_numerico.gif`; PPTX unifica em S10) |
| `figura_19_gradientes.png` | L2614 | Slide 60 (Apoio A3: gradientes por ramo e ruído/\textit{shots}) |
| `figura_22_ruido_shots.png` | L2624 | Slide 60 (Apoio A3: gradientes por ramo e ruído/\textit{shots}) |
| `figura_28_calibracao_fer.png` | L2596 | Slide 59 (Apoio A2: calibração probabilística no FER2013) |
| `fmap_03a_piramide_blocos_fashion_mnist.png` | L1146 | Slide 12 (Mapas de características em entradas $64\times 64\times 1$) |
| `fmap_03b_piramide_blocos_fer2013.png` | L1154 | Slide 12 (Mapas de características em entradas $64\times 64\times 1$) |
| `imagem_matriz_5x5.png` | L616 | Slide 7 (Imagem digital como matriz de intensidades) |
| `metricas_classificacao_exemplos.png` | L938 | Slide 8 (Métricas: por que o Macro-F1?) |
| `painel_oclusao_cifar100_coarse_01_desfoque.png` | L2668 | Slide 46 (Painéis causais de oclusão: domínios RGB) |
| `painel_oclusao_fashion_mnist_06_media.png` | L2652 | Slide 47 (Painéis causais de oclusão: monocromáticos) |
| `painel_oclusao_gtsrb_07_media.png` | L2644 | Slide 46 (Painéis causais de oclusão: domínios RGB) |
| `painel_oclusao_mnist_06_desfoque.png` | L2660 | Slide 47 (Painéis causais de oclusão: monocromáticos) |

## (b) Imagens presentes apenas no TCC escrito (`revisao_somente_tcc/`, 26)
| Imagem | Linha(s) em `tcc2-adaptado.tex` |
| :--- | :--- |
| `03_features_estatisticas.png` | L2267 |
| `feature-map-converted.png` | L1099 |
| `fig_261_shots_bell.png` | L1401 |
| `fig_263_qir_psnr.png` | L1561 |
| `fig_263_qkm_gcq.png` | L1506 |
| `fig_264_parameter_shift.png` | L1633 |
| `fig_265_canais_kraus.png` | L1692 |
| `fig_265_paisagem_barren_plateau.png` | L1665 |
| `fig_266_memoria_statevector.png` | L1719 |
| `fig_342_balanceamento_delta_f1.png` | L2109 |
| `fig_48_diferencas_ambientes_simuladores.png` | L2692 |
| `fig_48_eficiencia_melhor_epoca_patience15.png` | L2831 |
| `fig_48_metricas_por_tempo.png` | L2821 |
| `fig_48_tempo_100ep_vs_melhor_epoca.png` | L2769 |
| `fig_funcoes_ativacao_praticas.png` | L1009 |
| `fig_taxonomia_modelos_hibridos_visao.png` | L1734 |
| `figura_02_populacao.png` | L2031 |
| `figura_10_dense_deltas.png` | L2523 |
| `figura_16_quantico_deltas.png` | L2547 |
| `figura_26_comparacao_matriz.png` | L2504 |
| `figura_31_parametros.png` | L2535 |
| `figura_42_confusao_cifar10.png` | L2567 |
| `figura_43_confusao_fer2013.png` | L2577 |
| `fmap_01_piramide_blocos_gtsrb.png` | L2239 |
| `fmap_02_piramide_blocos_cifar10_parte1.png` | L2247 |
| `fmap_02_piramide_blocos_cifar10_parte2.png` | L2255 |

## (c) Imagens exclusivas dos slides (atuais = 0; antigas arquivadas em `revisao_somente_slides_antigas/` = 8)
Atualmente não resta nenhuma imagem exclusiva dos slides (`slides - tcc = ∅`).

As 8 imagens antigas que estavam apenas nos slides antes da sincronização permanecem arquivadas em `revisao_somente_slides_antigas/`:
- `ibm_visualize_circuits_latex.png`: Antigo Slide 13 (Qubits/circuitos) — substituída por `fig_261_esfera_bloch.png` e `fig_261_circuito_bell.png`
- `qiskit_ml_torch_connector_qnn_circuit.png`: Antigo Slide 14 (Codificação/ansatz) — substituída por `fig_263_codificacoes_vetoriais.png` e `fig_264_laco_vqa.png`
- `ibm_real_amplitudes_1.png`: Antigo Slide 14 (Codificação/ansatz) — substituída pelas figuras da Seção 2.6 do TCC
- `qiskit_aer_cuquantum_workflow_faj2023.png`: Antigo Slide 15 (Simulação/barren plateaus) — substituída por `fig_265_variancia_gradiente.png` e `fig_266_fluxo_backends_simulacao.png`
- `fig_balanceamento_tempo_treino.png`: Antigo Slide 24 (Balanceamento) — substituída por `fig_342_balanceamento_tempo_treino.png`
- `fig_oclusao_trocas_globais.png`: Antigo Slide 39 (Oclusão global) — removida na sincronização dos slides com o TCC
- `fig_tempos_100_epocas_comparativo.png`: Antigo Slide 42 (Tempos 100 épocas) — substituída por `fig_48_tempos_etapas_consolidado.png`
- `2plus1CNN-converted.png`: Antigo Apoio A5 — substituída por `fig_arxiv2304_mnist_loss_acc.png` (Senokosov et al., 2024)

## (d) Backups (`backup_substituidas/`, 6), Etapa 1 Pendente (`revisao_pendente/`, 2) e GIFs Ativos (`gifs/`, 7)
### `backup_substituidas/`
- `fig_arq_comparativo_mudancas.png`
- `fig_arq_etapa2_dense20_classicas.png`
- `fig_arq_etapa3_hibrida_4x5.png`
- `fig_circuito_quantico_5qubits.png`
- `fmap_02_piramide_blocos_cifar10.png`
- `fmap_03_piramide_blocos_grayscale.png`

### `revisao_pendente/`
- `fig_arq_etapa1_cnn_enviada_2x128_pendente.png` (não aplicada porque exibe `GAP 128-D -> 2×Dense 128` / `101.333 params`, divergindo de `GAP+GMP 256-D -> 2×Dense 256` / `201.059`–`201.173 params` descrito no TCC e nos slides)
- `01_fluxo_cnn_2xdense128.gif` (GIF animado da Etapa 1 com a mesma divergência `2×Dense 128` / `101.333 params`; mantido pendente em vez de substituir a figura estática da Etapa 1)

### `gifs/` (usados em `gerar_apresentacao_pptx.py`)
- `02_fluxo_dense20_imagem.gif` — Slide 32 (Etapa 2A)
- `03_fluxo_classico_tanh.gif` — Slide 33 (Etapa 2B)
- `04_fluxo_hibrido_4xpqc.gif` — Slide 34 (Etapa 3)
- `05_zoom_bloco_cnn.gif` — Slide 31 (Anatomia interna do Bloco B3)
- `06_zoom_pqc_5qubits.gif` — Slide 35 (Circuito variacional de 5 qubits por ramo)
- `07_sepconv_numerico.gif` — Slide 10 (Convolução separável unificada: Depthwise 3×3 + Pointwise 1×1)
- `08_comparativo_4_etapas.gif` — Slide 36 (Comparativo estrutural: 4 etapas; frame 23 exportado também como `fig_arq_comparativo_mudancas.png`)

## (e) Outros arquivos legados na raiz de `figuras/` não referenciados atualmente (30)
- `2plus1CNN.png`
- `F3.large.jpg`
- `F3.large.png`
- `aumento_dados_exemplos.png`
- `camadas.webp`
- `circuito_variacional_exemplo.png`
- `codificacoes_quanticas_imagem.png`
- `convolutional-pooling.webp`
- `feature-map.png`
- `fig_arq_etapa2_dense20_classicas.png`
- `fig_arquitetura_classica_fluxos.png`
- `fig_arquitetura_fluxos_e_cabecas.png`
- `fig_arquitetura_hibrida_4x5_qubits.png`
- `fig_barren_plateaus_escalabilidade.png`
- `fig_codificacao_dados_e_qir.png`
- `fig_conceitos_qubit_esfera_bell.png`
- `fig_custo_vs_macro_f1_ambientes.png`
- `fig_explicabilidade_gradcam_oclusao.png`
- `fig_fluxo_simulacao_pennylane_qiskit_gpu.png`
- `fig_funil_pesquisa.pdf`
- `fig_vqa_ciclo_e_parameter_shift.png`
- `figura_25_recursos.png`
- `figura_30_custo_desempenho.png`
- `fmap_02_piramide_blocos_cifar10.png`
- `fmap_03_piramide_blocos_grayscale.png`
- `fmap_06_comparacao_atencao_multidataset.png`
- `modelo_hibrido_quantico_classico.png`
- `qubit_portas_probabilidades.png`
- `simulacao_qiskit_fluxo.png`
- `tensor-play.png`
