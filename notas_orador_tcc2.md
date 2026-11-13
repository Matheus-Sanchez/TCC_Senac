# Notas do orador — TCC2 (40 min)

Arquivo dos slides: [apresentacao_tcc2_final.tex](file:///c:/Users/matheus.sduda/repos/TCC/TCC_Senac/apresentacao_tcc2_final.tex) · Tempo falado: **36:30** + 3:30 de reserva. Os números de slide seguem o rodapé do PDF.

> [!IMPORTANT]
> Frase-guia (repita no início e no fim): *"Comparei CNN, CNN com gargalo de 20 dimensões e CNN com cabeça quântica simulada em 9 bases. O híbrido é estável e competitivo, mas o controle clássico mostra que não há vantagem quântica comprovada."*

## Abertura (1:00)
**1 · Capa (0:30)** Apresentar-se, citar orientador e coorientador, dizer o tema em uma frase.
**2 · Roteiro (0:30)** "Seis blocos: problema, fundamentos, literatura, método, resultados e conclusão."

## 1. Introdução (4:30)
**3 · Contexto (1:15)** Classificação de imagens é fundamental; CNNs dominam; QML promete algo novo, mas na era NISQ tem limites. Fechar com a pergunta: *como se comparam em vários domínios?*
**4 · Problema e justificativa (1:15)** Literatura de QML testa em recortes pequenos (3 vs. 5 no MNIST, 4 classes), só com acurácia, e compara com lotes diferentes. Justificativa em três dimensões: tecnológica, acadêmica e metodológica.
**5 · Objetivos (1:15)** Ler o objetivo geral. Resumir os 7 específicos em 3 eixos: bases e pipeline, modelos, avaliação.
**6 · Hipótese e delimitações (0:45)** Hipótese: estável e competitivo, **sem** prometer superioridade. Delimitação-chave: tudo é simulado.

## 2. Fundamentação (8:00) — ritmo rápido, só o necessário
**7 · Imagem como matriz (0:45)** Imagem = matriz/tensor. Nossas bases variam em tamanho e canais.
**8 · Métricas (1:15)** Explicar TP/FP/FN, F1 por classe e Macro-F1 = média igual entre classes. "Por isso escolhi Macro-F1: GTSRB, FER2013 e SVHN são desbalanceadas."
**9 · Convolução e pooling (1:00)** Filtro desliza e detecta padrão local; pooling reduz tamanho.
**10 · Mapas de características (0:45)** Bordas no início, abstração no fim; o vetor final alimenta a cabeça.
**11 · Aumento de dados (0:45)** Variações que preservam o rótulo; combate overfitting (exemplo: 94% treino vs. 73% teste no CIFAR-10).
**12 · Qubits e circuitos (1:00)** Superposição, portas H/X/CNOT, medição. *Dizer: figura da documentação IBM, apenas ilustrativa.*
**13 · Codificação e ansatz (1:15)** Feature map codifica dado clássico; ansatz tem rotações treináveis. *Dizer: figuras Qiskit ilustrativas; **implementei em PennyLane**.*
**14 · Simulação e limites (1:15)** $2^n$ estados: 20 qubits são caros; barren plateaus. Por isso a decisão de 4×5 qubits.

## 3. Trabalhos correlatos (4:00)
**15 · Revisão (1:00)** Funil: 5.925 → 3.297 → 1.025 → 28 verificados. Ressaltar: mapeamento *preliminar* + conferência manual da fonte primária.
**16 · Clássicos (1:00)** CNNs bem estabelecidas: 99% em dígitos, ~73% em CIFAR-10 e FER2013. Avisar que acurácia ≠ Macro-F1.
**17 · Quânticos (1:15)** Recortes binários/4 classes; NNQE cai no GTSRB (73,4% vs. 82,2% clássico). **CIFAR-100 Coarse: nenhum estudo achado.**
**18 · Lacuna (0:45)** Três pontos: protocolos fragmentados, só acurácia, variáveis de confusão. Minha contribuição responde aos três.

## 4. Desenvolvimento (8:30)
**19 · Tipo de pesquisa (0:45)** Aplicada, quantitativa, exploratória/descritiva/comparativa. Ler a pergunta de pesquisa.
**20 · Pipeline (0:45)** Seis etapas, de inventário a auditoria. Não detalhar; só o fluxo.
**21 · Bases (1:15)** Destacar diversidade: 7 a 47 classes, cinza e RGB. Partições são da campanha, não as oficiais.
**22 · Equilíbrio (1:15)** Três regimes de IR. FER2013: 16,43× (desgosto com 547 imagens). Validação e teste mantêm a distribuição original.
**23 · Pré-processamento e GTSRB (1:00)** Mesma preparação para todos os modelos. **Antecipar a limitação do GTSRB aqui**: 3.990 de 5.876 imagens de teste compartilham *track* com o treino.
**24 · Três famílias (1:00)** CNN original, Dense20 (controle) e híbrido. "O Dense20 existe para isolar o efeito do gargalo." 72 checkpoints = 9×8.
**25 · Cabeça híbrida (1:30)** Seguir o diagrama da esquerda para a direita: CNN → vetor de 20 → 4 subvetores de 5 → 4 circuitos → ⟨Z⟩ → linear. Justificar o 4×5 e **admitir: não há emaranhamento entre os blocos**.
**26 · Protocolo (1:00)** Uma semente por configuração; checkpoint escolhido na validação; Macro-F1 de teste; Windows e macOS.

## 5. Resultados (7:00)
**27 · Tabela (1:30)** Guiar o olhar: coluna Híbrido vs. CNN e vs. Dense20. Mostrar que todos ficam muito próximos. Citar o asterisco do GTSRB.
**28 · Gráfico de Δ (1:15)** Barras azuis (vs. CNN) parecem ganhos; barras laranja (vs. Dense20) ficam em torno de zero. Médias: +0,23 e −0,01 p.p.
**29 · Papel do Dense20 (1:30)** *Este é o slide mais importante.* EMNIST: +0,755 vs. CNN, mas Dense20 já chega a 88,642. O ganho vem da projeção de 20 dimensões, não do circuito.
**30 · Complexidade (1:15)** O domínio manda: 99% → 73% → 47%. Explicar CIFAR-100 Coarse (superclasses heterogêneas) e FER2013 (desbalanceamento).
**31 · GTSRB (0:45)** Números altos refletem a partição, não generalização a placas inéditas.
**32 · Síntese (0:45)** Três ✓ e um ✗: estável, competitivo, sem vantagem quântica; mas **sem atribuição causal** por causa da semente única.

## 6. Conclusão (3:30)
**33 · Retomada (1:00)** Responder a pergunta e a hipótese. Repetir a frase-guia.
**34 · Contribuições (1:00)** Quatro pontos; enfatizar o controle Dense20 e a cobertura do CIFAR-100 Coarse.
**35 · Limitações e futuro (1:00)** Cada limitação tem seu trabalho futuro: multi-seed, GTSRB track-aware, emaranhamento, paridade de parâmetros, ruído/QPU.
**36 · Obrigado (0:30)** Agradecer e abrir para perguntas.

---

## Respostas prontas para perguntas prováveis

| Pergunta | Resposta curta |
|---|---|
| **Por que não houve vantagem quântica?** | As diferenças vs. Dense20 ficam entre −0,44 e +0,62 p.p., com uma semente e cabeças com parametrização diferente. Não há evidência estatística de vantagem nem de desvantagem. |
| **Por que 4 circuitos de 5 qubits?** | Um circuito de 20 qubits exige $2^{20}$ estados por amostra: intratável para treinar nas 9 bases. Custo: sem emaranhamento entre blocos. |
| **Por que Macro-F1?** | Pesa todas as classes igualmente; acurácia esconde falhas em classes minoritárias (FER2013, GTSRB, SVHN). |
| **O que o Dense20 controla?** | O efeito de comprimir para 20 dimensões. Sem ele, EMNIST pareceria ter +0,755 p.p. de ganho quântico. |
| **Por que PennyLane e não Qiskit?** | A cabeça auditada foi executada com PyTorch+PennyLane; Qiskit entra na fundamentação e como trabalho futuro (Aer/cuQuantum em GPU). |
| **O GTSRB é confiável?** | Só como consistência interna: 3.990 de 5.876 imagens de teste compartilham *track* com o treino. Refazer com divisão *track-aware*. |
| **Rodou em hardware quântico?** | Não; apenas simulação ideal. Ruído NISQ e QPU estão nos trabalhos futuros. |
| **E ativações, lote, quantização e telemetria Windows × macOS?** | ⚠️ **Preparar resposta com seus dados.** O Cap. 4 só mostra 3 das 8 configurações por base; se os resultados existirem nos artefatos, adicione um slide de apoio. |
| **Por que CIFAR-100 Coarse tem Macro-F1 ~47%?** | 20 superclasses, cada uma agrupa 5 classes finas visualmente distintas; uma CNN compacta, sem residuais profundas, capta só parte. |
