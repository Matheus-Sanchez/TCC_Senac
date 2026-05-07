# Avaliação simulada de banca acadêmica - TCC

**Trabalho avaliado:** *Classificação de câncer de mama em mamografias: um estudo comparativo entre CNNs clássicas e híbridas quântico-clássicas*  
**Autor:** Matheus Sanchez Duda  
**Escopo avaliado:** Introdução, Contexto, Justificativa, Objetivos, Hipótese e Limitações  
**Formato:** Simulação de banca acadêmica composta por sete avaliadores, com rodadas individuais e parecer final consolidado.

---

## Dinâmica da banca

A avaliação foi organizada em rodadas. Em cada rodada, um professor avaliador analisou o trabalho a partir de sua área de especialidade, considerando clareza do problema de pesquisa, relevância do tema, qualidade da fundamentação teórica, coerência entre introdução, objetivos, hipótese e limitações, viabilidade técnica e metodológica, pontos fortes, fragilidades, sugestões de melhoria e possíveis perguntas de banca.

A ordem das falas foi:

1. Professor especialista em Inteligência Artificial;
2. Professor especialista em Ciência da Computação;
3. Professor entusiasta em tecnologia e inovação;
4. Professor especialista em Computação Quântica;
5. Professor especialista em física quântica;
6. Professor especialista em pesquisa científica;
7. Professor especialista em matemática avançada.

---

# Rodada 1 - Professor especialista em Inteligência Artificial

## Avaliação do professor

Como avaliador da área de Inteligência Artificial, considero que o trabalho apresenta um **tema relevante, atual e com bom potencial acadêmico**, especialmente por propor uma comparação entre CNNs clássicas e modelos híbridos quântico-clássicos em mamografias. A introdução situa bem o problema em três eixos: saúde pública, visão computacional médica e aprendizado de máquina quântico. O texto deixa claro que a mamografia é uma tarefa difícil por envolver achados sutis, variações anatômicas, densidade mamária e alto volume de exames analisados por especialistas. Isso cria uma justificativa coerente para o uso de IA como apoio à análise de imagens médicas.

O **problema de pesquisa está bem direcionado**, principalmente quando o texto afirma que falta uma avaliação comparativa controlada entre uma CNN clássica e uma arquitetura híbrida quântico-clássica aplicada à classificação de mamografias sob o mesmo protocolo experimental. Esse é um ponto forte, porque demonstra preocupação metodológica: a comparação só será válida se base, pré-processamento, divisão dos dados e métricas forem equivalentes.

Entretanto, há uma fragilidade importante: a seção **“Pergunta de pesquisa” aparece vazia**. Para uma banca, isso é um problema formal e conceitual. O texto tem problema, objetivo e hipótese, mas falta transformar isso em uma pergunta explícita. A pergunta poderia ser algo como: *“Em uma tarefa controlada de classificação de mamografias em três classes, modelos híbridos quântico-clássicos apresentam desempenho competitivo em relação a CNNs clássicas quando avaliados por métricas preditivas, estabilidade e custo computacional?”*

Outro ponto crítico é o uso do termo **“desempenho competitivo”**. Em IA, esse termo precisa ser operacionalizado. Competitivo significa ter acurácia semelhante? F1-score macro próximo? AUC equivalente? Diferença máxima de 5%? Melhor estabilidade entre execuções? Menor overfitting? Sem uma definição quantitativa, a hipótese fica academicamente interessante, mas metodologicamente aberta demais.

Os objetivos específicos são bons, especialmente ao mencionar base de dados, classes, pré-processamento, divisão dos dados, arquitetura clássica, arquitetura híbrida, número de qubits, feature map, profundidade do circuito, métricas e custo computacional. Porém, eu sugeriria separar melhor os objetivos em dois grupos: **objetivos de construção do experimento** e **objetivos de avaliação comparativa**. Hoje eles estão corretos, mas ainda um pouco listados como tarefas de desenvolvimento.

A hipótese está bem escrita porque não promete “vantagem quântica” definitiva. Isso é positivo. O texto reconhece que a abordagem quântica pode ser limitada por custo computacional, número reduzido de qubits, sensibilidade a hiperparâmetros, codificação dos dados e restrições NISQ. Essa cautela aumenta a maturidade acadêmica do trabalho.

Minha principal preocupação, como especialista em IA, é que o texto ainda precisa antecipar melhor alguns riscos típicos de aprendizado de máquina em imagens médicas: vazamento de dados entre treino e teste, divisão por imagem em vez de divisão por paciente, desbalanceamento de classes, validação externa, escolha de métricas adequadas para classes minoritárias e comparação justa entre modelos com capacidades muito diferentes.

## Pontos fortes

O tema é relevante e interdisciplinar. A justificativa social, acadêmica e científica está bem estruturada. A hipótese é prudente e não exagera a promessa da computação quântica. A proposta de comparação controlada entre CNN clássica e modelo híbrido é adequada para um TCC experimental.

## Fragilidades e lacunas

A pergunta de pesquisa está ausente. O conceito de “competitivo” ainda não está mensurável. A possibilidade de “ampliação para uma classificação mais detalhada” no objetivo geral pode abrir demais o escopo. Para TCC1/TCC2, talvez seja melhor fixar claramente a classificação em três classes: normal, benigno e maligno. Também falta explicitar, já nas limitações, que o trabalho não validará uso clínico, não substituirá radiologistas e dependerá fortemente das condições do dataset e do simulador.

## Sugestões concretas

1. Preencher imediatamente a seção **1.4 Pergunta de pesquisa**.
2. Definir quantitativamente o que será considerado “competitivo”.
3. Remover ou restringir a frase “possibilidade de ampliação para uma classificação mais detalhada”, a menos que isso realmente vá entrar no experimento.
4. Adicionar nas limitações: divisão por paciente, risco de viés de base, ausência de validação clínica, dependência de simulação quântica e impossibilidade de afirmar vantagem quântica geral.
5. Explicitar qual será a métrica principal de comparação: F1-score macro, AUC macro/OVR, recall da classe maligna ou outra.

## Perguntas que eu faria em uma banca real

1. O que exatamente significa um modelo híbrido ser “competitivo” em relação à CNN clássica?
2. Qual será a métrica principal para decidir se um modelo foi melhor ou equivalente?
3. A divisão treino/validação/teste será feita por imagem ou por paciente? Como você evitará vazamento de dados?
4. Por que usar uma arquitetura híbrida quântico-clássica nesse problema, e não apenas uma CNN clássica mais forte ou transfer learning?
5. Se o modelo quântico tiver desempenho semelhante, mas custo computacional muito maior, como você interpretará esse resultado?

## Parecer deste avaliador

O trabalho tem uma proposta forte e promissora, mas precisa transformar melhor a intenção comparativa em critérios mensuráveis. Como projeto de TCC, é viável, desde que o escopo seja mantido controlado e que a pergunta de pesquisa seja formalizada com clareza.

---

# Rodada 2 - Professor especialista em Ciência da Computação

## Avaliação do professor

Do ponto de vista da Ciência da Computação, o trabalho apresenta uma proposta tecnicamente interessante porque não se limita a “usar IA em mamografia”, mas propõe uma **comparação experimental entre duas famílias de arquitetura**: CNNs clássicas e modelos híbridos quântico-clássicos. Isso é positivo, porque o foco deixa de ser apenas aplicação e passa a envolver arquitetura, protocolo experimental, controle de variáveis, custo computacional e reprodutibilidade.

A introdução contextualiza bem o problema computacional ao afirmar que a tarefa envolve imagens médicas de alta dimensão, classificação supervisionada e comparação entre modelos sob condições controladas. O texto também reconhece desafios importantes para Ciência da Computação aplicada: generalização, desbalanceamento de classes, qualidade dos rótulos, custo computacional e confiabilidade dos modelos. Esses pontos tornam o problema mais sólido do que uma simples aplicação de rede neural.

Vejo como ponto forte a formulação do problema central: o texto afirma que há ausência de uma avaliação comparativa controlada entre uma CNN clássica e uma arquitetura híbrida quântico-clássica aplicada à classificação de mamografias sob o mesmo protocolo experimental. Essa formulação é adequada, porque em Ciência da Computação uma comparação só é válida se houver controle sobre variáveis como base de dados, pré-processamento, divisão de treino/validação/teste, métricas e ambiente computacional.

Entretanto, minha crítica principal é que o texto ainda está **mais forte na intenção metodológica do que na definição técnica concreta**. O objetivo geral fala em comparar desempenho, custo computacional, estabilidade experimental e viabilidade prática, mas ainda não define com precisão como esses elementos serão medidos. Por exemplo: custo computacional será tempo de treinamento? tempo por época? uso máximo de RAM? uso de VRAM? número de parâmetros? complexidade assintótica? número de circuitos simulados? Isso precisa aparecer com mais clareza ainda na introdução ou nas delimitações.

Outro ponto importante: a seção **Pergunta de pesquisa está vazia**. Para Ciência da Computação, isso prejudica a rastreabilidade entre problema, hipótese, objetivo e método. A banca precisa conseguir olhar para a pergunta e depois verificar se os objetivos específicos respondem diretamente a ela. Hoje, o trabalho tem um bom problema e bons objetivos, mas falta essa “ponte formal”.

Os objetivos específicos estão tecnicamente bem encaminhados. Eles incluem definição da base, protocolo padronizado, aprimoramento da CNN clássica, projeto da arquitetura híbrida, investigação de número de qubits, feature map, profundidade do circuito, estratégia de codificação, métricas, tempo de treinamento, memória, estabilidade e escalabilidade. Isso mostra maturidade técnica. Porém, eles ainda misturam atividades de implementação com critérios de avaliação.

Eu recomendaria reorganizar os objetivos específicos em uma sequência mais computacional:

1. Preparar os dados e definir classes;
2. Construir o pipeline experimental;
3. Implementar baseline clássico;
4. Implementar modelo híbrido;
5. Executar experimentos controlados;
6. Avaliar desempenho preditivo;
7. Avaliar custo computacional e estabilidade;
8. Comparar criticamente os resultados.

Essa ordem deixa o projeto mais “executável”.

Também considero importante fortalecer a noção de **baseline**. O texto diz que uma CNN clássica será aprimorada para servir como modelo de referência. Mas uma banca pode perguntar: essa CNN será comparada apenas com o modelo híbrido criado pelo aluno, ou também com arquiteturas clássicas conhecidas, como ResNet, EfficientNet ou MobileNet? Se o baseline clássico for fraco, o modelo híbrido pode parecer competitivo artificialmente. Se o baseline for forte demais, o modelo híbrido pode parecer inviável sem uma análise justa. Portanto, o texto deve explicar melhor que tipo de baseline será usado e por quê.

A hipótese é cuidadosa ao dizer que não se pressupõe superioridade geral da abordagem quântica. Isso é cientificamente correto e metodologicamente saudável. O texto reconhece limitações como custo computacional, número reduzido de qubits, sensibilidade a hiperparâmetros, codificação dos dados e restrições de dispositivos NISQ. Para Ciência da Computação, isso é um ponto forte, pois evita uma promessa tecnológica exagerada.

## Pontos fortes

O trabalho tem bom recorte experimental, tema interdisciplinar e uma preocupação clara com comparação controlada. Os objetivos específicos indicam variáveis computacionais relevantes, como número de qubits, feature map, profundidade do circuito, memória, tempo de treinamento e estabilidade. A hipótese é prudente e evita afirmar vantagem quântica sem evidência.

## Fragilidades e lacunas

A pergunta de pesquisa está ausente. O conceito de custo computacional ainda está genérico. A ideia de estabilidade experimental precisa ser definida: estabilidade entre quantas execuções? com quais sementes aleatórias? quais métricas serão usadas para medir variação? Também falta explicitar melhor qual será o baseline clássico e como será garantida uma comparação justa entre arquiteturas com capacidades diferentes.

## Sugestões concretas de melhoria

Eu recomendaria inserir ainda nesta parte inicial uma frase delimitando operacionalmente a comparação. Por exemplo:

> “A comparação considerará como métricas preditivas principais F1-score macro, AUC multiclasse e recall da classe maligna; como métricas computacionais, serão avaliados tempo médio de treinamento, uso de memória, número de parâmetros e estabilidade entre execuções com sementes distintas.”

Também sugiro trocar expressões amplas como “viabilidade prática” por critérios observáveis. Viabilidade prática pode significar: o modelo roda no hardware disponível? o tempo de treinamento é aceitável? a simulação quântica escala para o número de qubits escolhido? o ganho preditivo compensa o custo?

## Perguntas que eu faria em uma banca real

1. Qual será exatamente a CNN clássica de referência? Ela será uma arquitetura própria ou uma arquitetura consolidada da literatura?
2. Como você garantirá que a comparação entre CNN clássica e modelo híbrido seja justa?
3. O que será medido como custo computacional? Tempo, memória, parâmetros, FLOPs, uso de GPU, uso de CPU ou custo da simulação quântica?
4. Como você avaliará estabilidade experimental? Quantas execuções serão feitas por modelo?
5. O modelo híbrido será comparado com uma CNN clássica de capacidade equivalente ou apenas com o melhor modelo clássico que você conseguir treinar?
6. Como você evitará vazamento de dados entre treino e teste, especialmente se houver múltiplas imagens por paciente?

## Parecer deste avaliador

O projeto é viável e tecnicamente relevante, mas precisa transformar melhor os conceitos computacionais em critérios mensuráveis. A estrutura geral está boa, porém a pergunta de pesquisa, a definição de baseline e os critérios de custo/estabilidade precisam ser fechados antes do TCC2.

---

# Rodada 3 - Professor entusiasta em tecnologia e inovação

## Avaliação do professor

Como avaliador com foco em tecnologia e inovação, vejo no trabalho um **potencial de destaque maior do que um TCC convencional**, porque ele tenta unir três áreas de forte impacto: saúde, inteligência artificial e computação quântica. A proposta tem apelo inovador, principalmente por não se limitar ao uso tradicional de CNNs em mamografias, mas por investigar se uma arquitetura híbrida quântico-clássica pode agregar algo a esse cenário.

O texto acerta ao apresentar o trabalho como uma pesquisa situada na interseção entre **visão computacional médica, aprendizado profundo e aprendizado de máquina quântico**. Essa escolha deixa claro que o objetivo não é apenas construir um classificador, mas avaliar uma tecnologia emergente em um problema realista e socialmente relevante.

Também considero positivo o fato de a justificativa reconhecer três dimensões: social, acadêmica e científica. O texto afirma que o trabalho não tem objetivo de uso clínico imediato, mas se insere em uma linha de pesquisa com impacto potencial na saúde. Essa ressalva é muito importante, porque evita vender a proposta como uma solução médica pronta.

Do ponto de vista de inovação, o ponto mais forte está na postura crítica: o trabalho não promete que computação quântica será superior, mas propõe investigar quando ela pode ser competitiva, limitada ou inviável. Essa é uma inovação mais madura: não é propaganda tecnológica, é avaliação experimental. A hipótese reconhece que a viabilidade prática depende de custo computacional, número reduzido de qubits, sensibilidade a hiperparâmetros, codificação dos dados e restrições NISQ.

No entanto, eu faria uma crítica importante: a **narrativa de inovação ainda pode ficar mais forte**. O texto explica bem o problema técnico, mas poderia destacar melhor qual é a contribuição inovadora do aluno. Hoje, a contribuição aparece diluída em frases como “comparação experimental controlada” e “investigar benefícios mensuráveis”. Isso é correto, mas ainda pouco marcante. Para uma banca, seria interessante deixar mais explícito algo como:

> “A contribuição deste trabalho está na construção de um protocolo experimental reprodutível para avaliar, em mamografias, se a inserção de um bloco quântico variacional em uma arquitetura de classificação traz ganhos mensuráveis ou apenas aumenta a complexidade computacional.”

Essa frase comunica melhor o valor inovador do projeto.

Outro ponto: o trabalho usa termos como **“viabilidade prática”**, **“impacto potencial”** e **“benefícios mensuráveis”**, mas ainda precisa tomar cuidado para não deixar esses conceitos abstratos. Em inovação tecnológica, viabilidade prática não é apenas “funcionar”. É preciso considerar se o modelo é executável no hardware disponível, se o custo de treinamento é aceitável, se o ganho justifica a complexidade, se a abordagem pode ser reproduzida e se existe algum caminho futuro de aplicação.

Também vejo risco na expressão “possibilidade de ampliação para uma classificação mais detalhada” no objetivo geral. Como proposta inovadora, isso parece interessante, mas como TCC pode soar como escopo aberto demais. Se o trabalho já envolve CNN, modelo híbrido, mamografia, três classes, métricas, estabilidade e custo computacional, ampliar a classificação pode tornar o projeto excessivamente ambicioso. Minha sugestão é deixar essa ampliação como **trabalho futuro**, não como parte do objetivo principal.

## Pontos fortes

O tema tem forte apelo tecnológico e interdisciplinar. A conexão entre IA médica e computação quântica é atual e pode gerar interesse em apresentações, artigos e eventos. A proposta evita promessas exageradas e assume uma postura crítica diante da tecnologia quântica. A ideia de comparar modelos considerando desempenho, custo computacional, estabilidade e viabilidade prática é muito boa.

## Fragilidades e lacunas

A contribuição inovadora ainda não está destacada com força suficiente. A seção de pergunta de pesquisa está vazia, o que enfraquece a comunicação do projeto. O objetivo geral ainda abre uma possibilidade de ampliação que pode comprometer o foco. Além disso, falta explicar melhor qual seria o “produto científico-tecnológico” do TCC: um pipeline? uma arquitetura? um protocolo experimental? um estudo comparativo? um conjunto de resultados reprodutíveis?

## Sugestões concretas de melhoria

Eu recomendaria inserir, ainda na introdução ou no final da justificativa, um pequeno parágrafo de **contribuição esperada**. Por exemplo:

> “Como contribuição, este trabalho pretende entregar um protocolo experimental comparativo, reprodutível e controlado para avaliar CNNs clássicas e modelos híbridos quântico-clássicos em mamografias, analisando não apenas desempenho preditivo, mas também custo computacional, estabilidade e limitações de escalabilidade.”

Também sugiro deixar claro que a inovação não está em criar uma ferramenta clínica, mas em avaliar uma arquitetura emergente em um domínio de alta complexidade. Isso protege o trabalho de críticas médicas e fortalece o caráter acadêmico-computacional.

## Perguntas que eu faria em uma banca real

1. Qual é exatamente a inovação do seu trabalho: a arquitetura, o protocolo experimental, a comparação ou a aplicação em mamografias?
2. Por que esse trabalho é mais do que apenas “testar um modelo diferente”?
3. O que o seu TCC entrega ao final: código, pipeline, arquitetura, relatório experimental, métricas comparativas?
4. Em quais condições você consideraria que o modelo híbrido vale a pena, mesmo que não supere a CNN clássica?
5. Como você evitará transformar computação quântica em apenas um argumento de marketing tecnológico?
6. A proposta tem algum caminho futuro para validação externa, publicação ou continuidade em iniciação científica/artigo?

## Parecer deste avaliador

O projeto tem alto potencial de inovação, mas precisa comunicar melhor sua contribuição tecnológica. A maior força está em propor uma avaliação crítica de uma tecnologia emergente, e não em prometer superioridade quântica. Para fortalecer o TCC, recomendo explicitar a contribuição esperada, fechar melhor o escopo e transformar “viabilidade prática” em critérios observáveis.

---

# Rodada 4 - Professor especialista em Computação Quântica

## Avaliação do professor

Como avaliador da área de Computação Quântica, considero que o trabalho está bem posicionado ao tratar os modelos híbridos quântico-clássicos como uma abordagem **experimental e exploratória**, e não como uma solução já comprovadamente superior às CNNs clássicas. Esse cuidado é essencial. O texto reconhece que essas arquiteturas ainda estão em estágio exploratório, especialmente em imagens médicas de alta dimensão, como mamografias.

O problema de pesquisa está coerente ao afirmar que a simples inclusão de um componente quântico não garante contribuição real. O texto coloca corretamente a necessidade de avaliar se o bloco quântico melhora a representação dos dados ou apenas aumenta a complexidade computacional. Esse é um ponto muito positivo para a área, porque muitos trabalhos em QML caem no erro de assumir vantagem quântica apenas por inserir qubits no pipeline.

A hipótese também é prudente. O trabalho não promete superioridade geral da abordagem quântica; pelo contrário, assume que a viabilidade prática dependerá de custo computacional, número reduzido de qubits, sensibilidade a hiperparâmetros, estratégia de codificação e restrições NISQ. Essa formulação é academicamente adequada e evita uma defesa exagerada da computação quântica.

Minha principal crítica está na necessidade de deixar mais claro **qual será exatamente o papel do componente quântico**. Ele será uma camada intermediária treinável? Um classificador final? Um bloco variacional depois da CNN? Uma camada de transformação de características? O texto sugere que será um componente treinável complementar às camadas clássicas, mas isso ainda está genérico. Para uma banca de Computação Quântica, não basta dizer “modelo híbrido”: é preciso especificar a estrutura mínima do circuito, o tipo de codificação, o ansatz, o número inicial de qubits, o tipo de medição e como os parâmetros serão otimizados.

O objetivo específico 5 é bom porque menciona número de qubits, feature map, profundidade do circuito e estratégia de codificação. Porém, eu recomendaria transformar isso em uma delimitação mais concreta. Por exemplo: “serão avaliadas configurações com 4, 6 e 8 qubits”, ou “serão testados angle encoding e ZZFeatureMap”, caso essa seja a intenção. Sem isso, a proposta parece correta, mas ainda aberta demais.

Outro ponto importante é a **codificação de dados clássicos em estados quânticos**. O trabalho reconhece corretamente que mamografias possuem alta dimensionalidade e que a aplicação direta de circuitos quânticos é limitada; por isso, modelos híbridos normalmente usam redes clássicas para extrair ou reduzir características antes de inserir um bloco quântico. Essa é uma boa fundamentação. Mas agora o texto precisa mostrar como essa escolha será feita no seu experimento: quais características saem da CNN? Elas serão normalizadas? Como serão mapeadas para ângulos? Haverá projeção densa para o número de qubits? O circuito receberá um vetor de dimensão igual ao número de qubits?

Também é positivo que o trabalho reconheça as limitações de simulação e escalabilidade. A revisão aponta que um sistema com n qubits possui 2^n amplitudes complexas, fazendo a memória crescer exponencialmente, e também discute barren plateaus e ruído em dispositivos NISQ. Esse conteúdo fortalece a base teórica. Porém, na parte inicial do TCC, essas limitações precisam aparecer de forma mais objetiva nas delimitações: até quantos qubits o trabalho pretende testar? O modelo será executado apenas em simulador? Usará statevector, shots ou ambos? O custo será medido por tempo, memória e número de avaliações do circuito?

## Pontos fortes

O trabalho não promete vantagem quântica definitiva. A hipótese é cautelosa e bem formulada. A proposta reconhece as limitações reais de NISQ, simulação, qubits reduzidos e sensibilidade a hiperparâmetros. A comparação controlada com CNN clássica é uma escolha metodológica correta.

## Fragilidades e lacunas

O papel exato do circuito quântico ainda está pouco definido. A pergunta de pesquisa está vazia, o que prejudica a amarração conceitual. O texto ainda não especifica qual codificação será usada, qual ansatz será testado, quantos qubits serão considerados e como a saída quântica será integrada à classificação final. Também falta explicar como será isolada a contribuição do bloco quântico em relação às camadas clássicas.

## Sugestões concretas de melhoria

Eu recomendo inserir uma delimitação técnica curta ainda na introdução ou nas limitações. Por exemplo:

> “Neste trabalho, o componente quântico será tratado como uma camada variacional simulada, inserida após a extração de características por uma CNN clássica. As características serão projetadas para uma dimensão compatível com o número de qubits, codificadas por um feature map e processadas por um circuito parametrizado raso, cuja saída será medida por valores esperados e enviada a camadas clássicas de classificação.”

Essa frase ajudaria muito a banca a entender o que você realmente pretende construir.

Também recomendo adicionar um pequeno controle experimental: comparar a CNN com bloco quântico contra uma CNN com uma camada densa clássica de dimensão equivalente. Sem esse controle, fica difícil afirmar que a diferença veio do circuito quântico e não apenas do aumento de parâmetros ou da mudança de arquitetura.

## Perguntas que eu faria em uma banca real

1. Qual é exatamente a função do circuito quântico dentro da arquitetura?
2. Qual estratégia de codificação será usada para transformar características clássicas em estados quânticos?
3. Quantos qubits você pretende utilizar e por que esse número é adequado ao hardware/simulador disponível?
4. O circuito será treinável ou terá parâmetros fixos?
5. Qual ansatz será utilizado e como você justificará sua escolha?
6. A simulação será por statevector ou por shots? Como isso afeta custo e reprodutibilidade?
7. Como você vai verificar se o bloco quântico realmente contribuiu para o resultado e não apenas aumentou a complexidade do modelo?
8. Qual será o critério para dizer que o modelo híbrido é inviável?

## Parecer deste avaliador

O projeto é pertinente para Computação Quântica aplicada, mas precisa tornar a arquitetura híbrida mais concreta. A fundamentação mostra consciência das limitações atuais da área; agora o texto precisa especificar melhor o desenho do circuito, a codificação, o número de qubits, o tipo de simulação e os controles necessários para avaliar a contribuição quântica.

---

# Rodada 5 - Professor especialista em física quântica

## Avaliação do professor

Como avaliador da área de física quântica, minha análise é um pouco diferente da avaliação de computação quântica. Aqui, eu observo principalmente se os conceitos físicos usados no trabalho estão sendo apresentados com precisão, sem simplificações perigosas, e se a proposta evita atribuir ao “quântico” um efeito mágico ou mal definido.

Nesse aspecto, o trabalho está em um bom caminho. A revisão bibliográfica apresenta os conceitos de qubit, superposição, emaranhamento e medição de maneira acessível, com equações adequadas para um TCC de Ciência da Computação. O texto explica que um qubit pode ser representado como combinação linear dos estados |0> e |1>, com amplitudes complexas alpha e beta, respeitando a condição de normalização |alpha|^2 + |beta|^2 = 1. Também explica corretamente que |alpha|^2 e |beta|^2 correspondem às probabilidades observadas após a medição.

Também considero positivo o texto reconhecer que o crescimento do espaço de estados com n qubits é exponencial, com dimensão 2^n. Isso é importante porque ajuda o leitor a entender tanto o interesse pela computação quântica quanto o custo de simular circuitos quânticos em computadores clássicos. O trabalho não apresenta esse crescimento apenas como vantagem, mas também como limitação prática de simulação, o que demonstra maturidade conceitual.

A explicação sobre emaranhamento também está adequada para o nível do trabalho. O exemplo do estado de Bell |Phi+> = 1/sqrt(2)(|00> + |11>) é bem escolhido, pois permite mostrar que o estado global não pode ser tratado como simples produto de estados individuais. O texto também acerta ao dizer que a medição transforma informação quântica em informação clássica e que, em modelos de aprendizado de máquina quântico, as saídas podem ser obtidas por probabilidades de medição ou valores esperados de observáveis, como <Z>.

No entanto, minha crítica principal é que o trabalho precisa tomar cuidado com a **interpretação física das vantagens esperadas**. O texto menciona que modelos híbridos buscam explorar “novas formas de representação e processamento da informação”, o que é aceitável, mas ainda genérico. Do ponto de vista da física, seria melhor evitar qualquer sugestão indireta de que superposição ou emaranhamento, por si só, garantem melhora no aprendizado. Eles são recursos físicos importantes, mas seu efeito útil depende da codificação, do circuito, da medição, do ruído, da profundidade e da relação com a estrutura dos dados.

Outro ponto: a física quântica aparece bem na revisão, mas ainda pouco conectada à hipótese experimental. A hipótese diz que circuitos quânticos simulados podem atuar como componente treinável complementar às camadas clássicas e apresentar desempenho competitivo. Porém, falta explicitar qual propriedade física do circuito será relevante para o modelo. Será a superposição? O emaranhamento? A interferência? A dimensionalidade do espaço de Hilbert? Ou apenas a não linearidade induzida pela codificação e pela medição? Essa distinção é importante para não transformar a física em ornamentação teórica.

Também vejo um risco conceitual na comparação com imagens médicas de alta dimensão. O próprio texto reconhece que codificar diretamente uma mamografia de 1024 x 1024, com mais de um milhão de pixels, é impraticável nos dispositivos atuais e em simuladores clássicos; por isso, modelos híbridos dependem de compressão, extração de características ou processamento local. Essa limitação deveria aparecer com mais força na parte inicial, porque ela afeta diretamente a validade física e computacional da proposta. O bloco quântico não estará “vendo” a mamografia completa; ele estará processando uma representação reduzida gerada por uma CNN ou camada clássica. Isso precisa ser dito de forma muito transparente.

## Pontos fortes

O trabalho apresenta os conceitos físicos básicos de maneira clara e didática. O uso de equações para qubit, normalização, estado de Bell, operações unitárias e valores esperados é adequado. A proposta reconhece limitações reais da tecnologia atual, como ruído, poucos qubits, circuitos rasos, custo de simulação e barren plateaus. Isso evita uma visão ingênua da computação quântica.

## Fragilidades e lacunas

A conexão entre física quântica e hipótese experimental ainda está genérica. O texto explica superposição e emaranhamento, mas ainda não deixa claro se esses recursos serão analisados, medidos ou apenas usados como fundamentação. Também falta uma delimitação física mais explícita: o trabalho usará apenas simulação ideal? Considerará ruído? Usará shots ou valores esperados analíticos? O circuito será tratado como modelo físico realista ou como camada matemática inspirada em computação quântica?

## Sugestões concretas de melhoria

Eu recomendo acrescentar uma frase de cautela na introdução ou nas delimitações, como:

> “Neste trabalho, os circuitos quânticos serão investigados como componentes variacionais simulados, sem pressupor vantagem física intrínseca decorrente de superposição ou emaranhamento. A contribuição do bloco quântico será avaliada empiricamente, considerando as limitações de codificação, medição, custo de simulação e escalabilidade.”

Também sugiro diferenciar claramente **computação quântica física** de **simulação quântica clássica**. Se o trabalho será feito em simulador, a banca pode perguntar: “onde está o ganho quântico se tudo roda em computador clássico?”. A resposta precisa estar pronta: o objetivo não é demonstrar aceleração física, mas avaliar experimentalmente uma arquitetura híbrida inspirada em circuitos quânticos, sob limitações realistas.

## Perguntas que eu faria em uma banca real

1. O seu circuito quântico simulado representa uma vantagem física real ou apenas uma camada matemática inspirada em computação quântica?
2. Qual recurso quântico você espera que contribua para a classificação: superposição, emaranhamento, interferência ou dimensionalidade do espaço de Hilbert?
3. O trabalho medirá algum indicador do circuito, como distribuição dos valores esperados, saturação, gradientes ou emaranhamento?
4. Se o circuito for simulado em computador clássico, como você justifica o uso da abordagem quântica?
5. O modelo considerará ruído ou será uma simulação ideal?
6. Como a medição probabilística afeta a estabilidade dos resultados?
7. A redução dimensional feita antes do circuito pode eliminar justamente os sinais sutis importantes da mamografia?

## Parecer deste avaliador

A fundamentação física está adequada para o nível do TCC, mas precisa ser melhor conectada à hipótese e às limitações experimentais. O trabalho deve deixar claro que não está demonstrando vantagem física quântica, e sim investigando, de forma simulada e controlada, se um componente variacional quântico pode contribuir para uma tarefa de classificação.

---

# Rodada 6 - Professor especialista em pesquisa científica

## Avaliação do professor

Como avaliador da área de pesquisa científica, minha preocupação central é verificar se o trabalho apresenta **problema, justificativa, objetivos, hipótese e delimitações de forma articulada, testável e metodologicamente defensável**. Nesse sentido, o TCC tem uma base promissora, mas ainda precisa de ajustes importantes antes de ser considerado plenamente maduro como projeto científico.

O primeiro ponto positivo é que o trabalho já apresenta uma **lacuna de pesquisa compreensível**. O texto afirma que modelos híbridos quântico-clássicos ainda são frequentemente avaliados em bases pequenas, imagens de baixa resolução, tarefas simplificadas ou ambientes simulados, dificultando a avaliação de sua viabilidade prática em mamografias. Em seguida, formula o problema como ausência de uma comparação controlada entre CNN clássica e arquitetura híbrida sob o mesmo protocolo experimental. Isso é uma formulação científica adequada, pois transforma uma lacuna da literatura em um problema investigável.

A justificativa também está bem organizada em três dimensões: social, acadêmica e científica. O texto não se limita a dizer que “câncer de mama é importante”; ele conecta a relevância social da detecção precoce com a relevância acadêmica da comparação entre aprendizado profundo e modelos híbridos, e com a lacuna científica relacionada à reprodutibilidade e à validação comparativa rigorosa. Isso é um ponto forte.

Entretanto, há uma falha grave para um projeto científico: a seção **1.4 Pergunta de pesquisa está sem conteúdo**. Esse é um problema estrutural. A pergunta de pesquisa é o eixo que organiza o trabalho. Sem ela, o leitor precisa inferir a pergunta a partir do problema, do objetivo e da hipótese. Em uma banca real, isso seria cobrado imediatamente. O texto já tem material suficiente para formular a pergunta, mas ela precisa estar escrita.

Eu sugeriria algo como:

> “Em um protocolo experimental controlado de classificação de mamografias em três classes, modelos híbridos quântico-clássicos apresentam desempenho competitivo em relação a CNNs clássicas quando avaliados por métricas preditivas, estabilidade experimental e custo computacional?”

Essa pergunta é melhor do que uma formulação genérica porque já explicita população/dados, intervenção/modelo, comparação e critérios de avaliação.

O objetivo geral está coerente com o problema, pois propõe investigar comparativamente CNNs clássicas e modelos híbridos quântico-clássicos considerando desempenho preditivo, custo computacional, estabilidade experimental e viabilidade prática. Porém, ele contém uma fragilidade: a frase **“possibilidade de ampliação para uma classificação mais detalhada”** abre escopo demais. Como projeto científico, o objetivo deve ser fechado. A ampliação pode aparecer como trabalho futuro, mas não deve ficar dentro do objetivo geral se não houver garantia de execução.

Os objetivos específicos são bons, mas alguns ainda estão formulados como tarefas técnicas amplas, não como objetivos científicos verificáveis. Por exemplo, “aprimorar uma CNN clássica” é uma tarefa de desenvolvimento; cientificamente, seria mais forte dizer “definir e implementar uma CNN clássica de referência para servir como baseline experimental”. O mesmo vale para “projetar uma arquitetura híbrida”: seria melhor explicitar que ela será avaliada sob as mesmas condições do modelo clássico. Os objetivos 6 e 7 são os mais fortes, porque já apontam métricas e critérios observáveis: acurácia, precisão, recall, F1-score, AUC, matriz de confusão, tempo de treinamento, memória, estabilidade e escalabilidade.

A hipótese é prudente e cientificamente defensável. Ela não afirma que a computação quântica será superior; afirma que pode apresentar desempenho competitivo e que isso será avaliado sob protocolo controlado, com mesma base, pré-processamento, divisão de dados, métricas e ambiente computacional. Esse cuidado é muito bom. Mas ainda falta definir o que conta como “competitivo”. Sem uma regra de decisão, a hipótese fica difícil de testar. Por exemplo: o híbrido será competitivo se tiver F1-score macro dentro de uma margem de 5% da CNN clássica? Se tiver melhor recall para classe maligna? Se tiver desempenho semelhante mas custo maior, ainda será competitivo? Isso precisa ser definido.

As delimitações estão corretas ao restringir o estudo a uma classificação supervisionada de mamografias, inicialmente em três classes: normal, benigno e maligno; também indicam que a comparação manterá constantes base, pré-processamento, critérios de divisão e métricas. Ainda assim, eu acrescentaria delimitações mais fortes: não haverá validação clínica, não haverá diagnóstico médico, não haverá teste em ambiente hospitalar, não será demonstrada vantagem quântica física, e os resultados serão válidos apenas para o conjunto de dados, arquitetura e ambiente computacional utilizados.

## Pontos fortes

O trabalho tem tema relevante, lacuna identificável, justificativa bem estruturada e hipótese cautelosa. A proposta de comparação controlada é cientificamente adequada. Os objetivos incluem métricas preditivas e computacionais, o que fortalece a avaliação experimental.

## Fragilidades e lacunas

A pergunta de pesquisa está ausente. O termo “competitivo” não está operacionalizado. O objetivo geral ainda abre escopo com “classificação mais detalhada”. Algumas atividades aparecem como tarefas de implementação, mas precisam ser convertidas em objetivos científicos mensuráveis. As limitações ainda precisam deixar mais explícito o que o trabalho não pretende provar.

## Sugestões concretas de melhoria

Eu recomendo cinco ajustes prioritários:

1. Preencher imediatamente a pergunta de pesquisa.
2. Definir uma métrica principal e métricas secundárias.
3. Estabelecer uma margem objetiva para “desempenho competitivo”.
4. Retirar do objetivo geral a ampliação para classificação mais detalhada, deixando isso como trabalho futuro.
5. Reescrever as delimitações incluindo ausência de validação clínica, uso de simulador, dependência do dataset e impossibilidade de generalizar os achados para todos os modelos quânticos.

## Perguntas que eu faria em uma banca real

1. Qual é exatamente sua pergunta de pesquisa?
2. Sua hipótese é testável? Como você saberá se ela foi confirmada ou refutada?
3. O que significa “competitivo” em termos quantitativos?
4. Qual será a variável independente do estudo? A arquitetura do modelo? O número de qubits? O tipo de codificação?
5. Quais serão as variáveis dependentes? Acurácia, F1-score, AUC, tempo, memória, estabilidade?
6. Como você controlará ameaças à validade interna, como vazamento de dados, overfitting e desbalanceamento de classes?
7. Até que ponto os resultados poderão ser generalizados além da base utilizada?

## Parecer deste avaliador

O projeto é cientificamente viável, mas ainda precisa de maior rigor formal. O principal problema não é o tema, nem a relevância, mas a necessidade de transformar boas intenções metodológicas em critérios testáveis, mensuráveis e claramente delimitados.

---

# Rodada 7 - Professor especialista em matemática avançada

## Avaliação do professor

Como avaliador da área de matemática avançada, observo que o trabalho tem uma preocupação positiva em apresentar os fundamentos matemáticos por trás da aprendizagem supervisionada, das métricas de avaliação, das redes neurais e dos modelos híbridos quântico-clássicos. Isso é importante porque o tema não pode ser defendido apenas como uma aplicação computacional; ele depende de conceitos matemáticos de otimização, probabilidade, álgebra linear, estatística, funções parametrizadas e espaços vetoriais complexos.

Um ponto forte é que o texto já apresenta a tarefa de aprendizado supervisionado como um conjunto de exemplos rotulados D = {(x1,y1), (x2,y2), ..., (xN,yN)}, em que xi representa a entrada e yi o rótulo associado. Essa formulação é adequada para introduzir a classificação de mamografias como um problema matemático de mapeamento entre uma representação numérica da imagem e uma classe diagnóstica.

Também é positivo o trabalho representar um modelo de aprendizado profundo como uma função parametrizada f_theta: R^D -> R^K, em que D é a dimensão da entrada, K é o número de classes e theta representa os parâmetros aprendidos. Essa formulação ajuda a explicar que a CNN não “entende” a imagem como um humano, mas aprende uma função que transforma dados de entrada em pontuações ou probabilidades de classe.

A parte de métricas também está bem encaminhada. O texto apresenta F1-score, Macro-F1, Weighted-F1, acurácia balanceada, TPR, FPR e AUC. Isso é muito importante porque, em bases médicas desbalanceadas, a acurácia isolada pode ser enganosa. O texto acerta ao destacar que a média macro dá peso igual para todas as classes e que isso é relevante quando classes clinicamente importantes, como benigno e maligno, têm menos amostras que a classe normal.

No entanto, minha crítica principal é que o trabalho ainda precisa conectar melhor essas métricas à **decisão matemática da hipótese**. O texto diz que o modelo híbrido pode apresentar “desempenho competitivo”, mas não define uma condição matemática para isso. Para a banca, essa indefinição é problemática. Competitivo precisa virar uma regra de comparação.

Por exemplo, o trabalho poderia definir algo como:

> “O modelo híbrido será considerado competitivo se apresentar Macro-F1 ou AUC multiclasse dentro de uma margem máxima de 5 pontos percentuais em relação à CNN clássica, mantendo estabilidade entre execuções e custo computacional interpretável.”

Não estou dizendo que a margem precisa ser exatamente 5%, mas é necessário definir algum critério. Sem isso, qualquer resultado pode ser interpretado subjetivamente.

Outro ponto importante: o trabalho menciona estabilidade experimental, mas ainda não define matematicamente como ela será medida. Estabilidade pode ser desvio padrão entre execuções, intervalo de confiança, variação da métrica principal entre sementes aleatórias ou consistência da matriz de confusão. Se a hipótese inclui estabilidade, então ela precisa ser mensurável.

Também considero relevante reforçar a diferença entre **média macro** e **média ponderada**. Para o seu caso, a Macro-F1 provavelmente deve ter destaque maior do que a Weighted-F1, porque o problema envolve classes com pesos clínicos diferentes e possível desbalanceamento. Se a classe normal for muito maior, a métrica ponderada pode mascarar baixo desempenho nas classes benigno e maligno.

Na parte quântica, o trabalho apresenta uma boa formalização do modelo híbrido: uma rede clássica extrai características v = g_phi(x), depois ocorre uma projeção u = Wv + b, o vetor é codificado em um circuito quântico por U_enc(u), seguido de um circuito variacional U(theta). Essa é uma formulação matematicamente adequada e deveria ser mais aproveitada na introdução ou nas delimitações, porque ela deixa claro que o componente quântico não recebe a imagem inteira, mas uma representação reduzida.

A discussão sobre barren plateaus também está bem colocada. O texto explica que, em certas famílias de circuitos, a variância dos gradientes pode decair exponencialmente com o número de qubits, fazendo com que dE(theta)/dtheta_k seja aproximadamente zero. Esse ponto é matematicamente importante porque mostra que o problema do modelo híbrido não é apenas “ter poucos qubits”, mas também conseguir otimizar os parâmetros de forma efetiva.

## Pontos fortes

O trabalho já possui boa base matemática para aprendizado supervisionado, funções parametrizadas, métricas de classificação e modelos híbridos. A escolha de métricas como Macro-F1, acurácia balanceada e AUC é adequada para imagens médicas. A formulação do pipeline híbrido com extração clássica, projeção, codificação quântica e circuito variacional é promissora.

## Fragilidades e lacunas

A hipótese ainda não possui critério matemático claro de aceitação ou rejeição. O termo “competitivo” é qualitativo demais. A estabilidade experimental ainda não foi definida formalmente. Falta indicar qual métrica será principal e quais serão secundárias. Também falta explicitar se a comparação usará média, desvio padrão, intervalo de confiança ou apenas valores finais.

## Sugestões concretas de melhoria

Eu recomendo acrescentar uma pequena subseção ou parágrafo com **critérios quantitativos de comparação**. Por exemplo:

> “A métrica principal de comparação será a Macro-F1, por atribuir peso equivalente às classes normal, benigna e maligna. Como métricas secundárias, serão utilizadas AUC one-vs-rest, recall da classe maligna, acurácia balanceada e matriz de confusão. A estabilidade será avaliada pela média e desvio padrão das métricas em múltiplas execuções com sementes distintas.”

Também recomendo definir uma notação simples para comparação entre modelos. Por exemplo:

Delta_F1 = F1_macro^hibrido - F1_macro^CNN

Assim, você pode dizer que o híbrido foi superior se Delta_F1 > 0, equivalente se estiver dentro de uma margem definida, ou inferior se ficar abaixo dessa margem. Isso daria mais rigor matemático ao TCC.

## Perguntas que eu faria em uma banca real

1. Qual será a métrica principal para aceitar ou rejeitar sua hipótese?
2. Como você define matematicamente “desempenho competitivo”?
3. Por que usar Macro-F1 em vez de apenas acurácia?
4. Como você vai medir estabilidade experimental?
5. Quantas execuções serão feitas para estimar média e desvio padrão?
6. A diferença entre os modelos será analisada apenas visualmente ou com algum critério estatístico?
7. Como o desbalanceamento das classes afeta a interpretação das métricas?
8. A projeção u = Wv + b antes do circuito quântico pode gerar perda de informação relevante? Como isso será avaliado?

## Parecer deste avaliador

O trabalho tem boa base matemática, mas precisa transformar seus conceitos avaliativos em critérios quantitativos. A fundamentação está adequada, porém a hipótese só ficará realmente testável quando “competitivo”, “estável” e “viável” forem definidos por métricas, margens e procedimentos de comparação.

---

# Parecer final consolidado da banca

**Relator:** Professor especialista em pesquisa científica, reunindo as observações dos sete avaliadores.

Após a análise das seções apresentadas - **Introdução, Contexto, Justificativa, Objetivos, Hipótese e Limitações** -, a banca considera que o TCC possui **tema relevante, atual e academicamente promissor**, especialmente por articular câncer de mama, mamografia, redes neurais convolucionais e modelos híbridos quântico-clássicos.

O trabalho apresenta uma boa contextualização inicial: situa o câncer de mama como problema de saúde pública, destaca a complexidade da interpretação de mamografias e justifica o uso de IA como ferramenta de apoio à análise de imagens médicas. Também delimita bem a proposta como uma investigação comparativa entre CNN clássica e arquitetura híbrida quântico-clássica, considerando desempenho, custo computacional e limitações práticas.

A banca entende que o projeto **pode seguir para o TCC2**, mas com ajustes obrigatórios antes da etapa experimental.

## 1. Resumo geral da avaliação

O TCC tem uma proposta forte: investigar se a inserção de um componente quântico em uma arquitetura de classificação de mamografias gera algum benefício mensurável ou apenas aumenta a complexidade computacional. Esse recorte é relevante porque o próprio texto reconhece que modelos híbridos quântico-clássicos ainda são exploratórios em imagens médicas de alta dimensão e que falta avaliação comparativa controlada sob o mesmo protocolo experimental.

A banca avalia positivamente o fato de o trabalho **não prometer vantagem quântica definitiva**. A hipótese é cautelosa ao afirmar que o modelo híbrido pode ser competitivo, mas que sua viabilidade depende de custo computacional, número reduzido de qubits, hiperparâmetros, codificação dos dados e restrições NISQ.

O maior problema identificado é que a proposta ainda precisa transformar vários conceitos importantes em **critérios mensuráveis**. Termos como “competitivo”, “estabilidade experimental”, “viabilidade prática” e “benefícios mensuráveis” ainda aparecem de forma ampla demais. Para o TCC2, esses termos precisam virar métricas, margens, procedimentos e critérios de decisão.

## 2. Principais pontos fortes

O primeiro ponto forte é a **relevância do tema**. O trabalho aborda um problema socialmente importante e conecta essa relevância com uma proposta computacional clara. A justificativa está bem dividida em relevância social, acadêmica e científica, destacando que o trabalho não pretende uso clínico imediato, mas se insere em uma linha de pesquisa com impacto potencial em saúde.

O segundo ponto forte é a **lacuna de pesquisa**. O texto identifica corretamente que muitos estudos quânticos ou híbridos usam bases pequenas, imagens de baixa resolução, tarefas simplificadas ou simulações, o que dificulta avaliar a viabilidade prática em problemas mais realistas.

O terceiro ponto forte é a **coerência da hipótese**. A hipótese não exagera a proposta e não afirma que o modelo quântico será superior. Ela propõe investigar em quais condições a abordagem híbrida pode ser competitiva, limitada ou inviável. Isso demonstra maturidade científica.

O quarto ponto forte é a **boa escolha das dimensões de comparação**. Os objetivos específicos mencionam métricas preditivas, como acurácia, precisão, recall, F1-score, AUC e matriz de confusão, além de tempo de treinamento, memória, estabilidade e escalabilidade.

## 3. Principais pontos fracos

A fragilidade mais grave é que a seção **1.4 Pergunta de pesquisa está vazia**. Isso precisa ser corrigido imediatamente. O trabalho tem problema, justificativa, objetivos e hipótese, mas falta a pergunta central que organiza tudo.

O segundo problema é a falta de definição quantitativa de **“desempenho competitivo”**. A banca não conseguirá avaliar se a hipótese foi confirmada ou rejeitada se o trabalho não disser previamente o que conta como competitivo.

O terceiro problema é o objetivo geral estar um pouco aberto demais ao mencionar a “possibilidade de ampliação para uma classificação mais detalhada”. Para TCC2, isso pode gerar risco de escopo. O trabalho já é suficientemente complexo com classificação em três classes, CNN clássica, modelo híbrido, simulação quântica, métricas, custo computacional e estabilidade.

O quarto problema é que o componente quântico ainda precisa ser descrito com mais precisão. A banca espera encontrar, antes da metodologia final, uma definição mais clara de número de qubits, codificação, feature map, ansatz, tipo de medição, tipo de simulação e integração com a CNN.

O quinto problema é a necessidade de reforçar as limitações. A delimitação atual diz que será uma classificação supervisionada em três classes e que a comparação manterá constantes base, pré-processamento, divisão dos dados e métricas. Isso é bom, mas ainda falta explicitar: ausência de validação clínica, ausência de diagnóstico médico, uso de simulador, risco de viés do dataset, divisão por paciente e impossibilidade de afirmar vantagem quântica geral.

## 4. Mudanças recomendadas

A banca recomenda inserir uma pergunta de pesquisa como:

> **Em um protocolo experimental controlado de classificação de mamografias em três classes, modelos híbridos quântico-clássicos apresentam desempenho competitivo em relação a CNNs clássicas quando avaliados por métricas preditivas, estabilidade experimental e custo computacional?**

Também recomenda ajustar o objetivo geral para ficar mais fechado:

> **Investigar comparativamente o desempenho de uma CNN clássica e de uma arquitetura híbrida quântico-clássica na classificação supervisionada de mamografias em três classes - normal, benigna e maligna - considerando métricas preditivas, estabilidade experimental, custo computacional e limitações de simulação.**

A banca recomenda remover do objetivo geral a ideia de “classificação mais detalhada” e colocar isso apenas como trabalho futuro.

Também recomenda definir um critério quantitativo de comparação, por exemplo:

> **O modelo híbrido será considerado competitivo se apresentar Macro-F1 ou AUC multiclasse dentro de uma margem previamente definida em relação à CNN clássica, considerando também estabilidade entre execuções e custo computacional.**

Além disso, o trabalho deve deixar explícito que a métrica principal provavelmente deve ser **Macro-F1**, porque o problema envolve classes clínicas diferentes e possível desbalanceamento. AUC one-vs-rest, recall da classe maligna, acurácia balanceada e matriz de confusão podem ficar como métricas secundárias.

## 5. Ajustes prioritários antes do TCC2

A banca recomenda priorizar estes ajustes, nesta ordem:

1. **Preencher a pergunta de pesquisa.**  
   Essa é a correção mais urgente.

2. **Definir o que significa “competitivo”.**  
   Sem isso, a hipótese fica subjetiva.

3. **Fechar o escopo em três classes.**  
   Normal, benigno e maligno já são suficientes para o TCC2.

4. **Definir a métrica principal.**  
   Recomenda-se Macro-F1 ou AUC multiclasse, com justificativa.

5. **Explicitar o baseline clássico.**  
   Dizer se será CNN própria, ResNet, EfficientNet ou outro modelo.

6. **Detalhar melhor o bloco quântico.**  
   Indicar número de qubits, codificação, feature map, ansatz, medição e tipo de simulação.

7. **Adicionar controle experimental.**  
   Comparar o modelo híbrido contra uma CNN com camada densa clássica equivalente ajudaria a verificar se o ganho vem do bloco quântico ou apenas da mudança arquitetural.

8. **Reforçar as limitações.**  
   Incluir ausência de validação clínica, uso de simulador, dependência do dataset, risco de viés, custo de simulação e impossibilidade de afirmar vantagem quântica ampla.

9. **Explicitar como evitar vazamento de dados.**  
   A divisão por paciente deve ser discutida, especialmente se houver múltiplas imagens por paciente.

10. **Definir estabilidade experimental.**  
    Indicar se serão usadas múltiplas execuções com sementes diferentes, média, desvio padrão e variação das métricas.

## 6. Parecer final sobre a continuidade do projeto

**Parecer da banca: aprovado para continuidade, com ressalvas metodológicas.**

A banca considera que o trabalho possui **potencial acadêmico real** e pode evoluir para um TCC2 consistente. O tema é atual, a justificativa é relevante, a hipótese é prudente e o recorte comparativo é defensável. O projeto não deve ser abandonado nem simplificado demais, mas precisa ser **mais preciso, mensurável e delimitado**.

A principal recomendação da banca é: **não tente provar que computação quântica é melhor que CNN clássica**. O caminho mais forte é defender que o TCC investiga, com rigor experimental, **se a inserção de um bloco quântico em uma arquitetura híbrida traz ganhos mensuráveis, estabilidade aceitável ou apenas maior custo computacional**.

Com os ajustes indicados, o trabalho tem condições de se tornar um TCC sólido, crítico e bem alinhado à proposta de uma pesquisa experimental em Ciência da Computação.
