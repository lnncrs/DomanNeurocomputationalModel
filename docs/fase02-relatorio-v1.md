<!--
Documento de trabalho da Fase 2.
Base histórica: docs/fase01-relatorio.md.
O conteúdo está sendo revisado incrementalmente e permanece sujeito às tags editoriais.
-->

> **Documento de trabalho da Fase 2:** Este arquivo foi criado como cópia integral de `docs/fase01-relatorio.md` para permitir uma revisão incremental e rastreável. As seções marcadas como `[preservar]` já foram revistas, as demais ainda podem conter descrições, próximos passos e conclusões obsoletas.

## [atualizar] Escopo e estado da Fase 2

Este relatório consolida a evolução do projeto na segunda entrega. A Fase 2 compreende a correção e parametrização do mundo inclinado, a definição lógica da meta, a aquisição de aceleração e do estimulo da maraca, a implementação da rede plástica de quatro neurônios e sua integração ao modo `LEARNING` da simulação, a telemetria experimental e a geração de artefatos a cada execução também fazem parte dessa entrega.

No estado atual, a implementação de engenharia e o fluxo experimental de ponta a ponta estão concluídos mas as execuções realizadas neste ponto têm caráter exploratório: demonstram o funcionamento do sistema mas não constituem um experimento controlado nem evidência suficiente para atribuir o comportamento observado à plasticidade neural.

No entanto, a simulação implementada com um protocolo de experimento definido e posterior análise dos artefatos gerados podem sim ser a base para uma análise desse tipo.

Está nos planos a implementção na Fase 3 de um modo de disparo não supervisionado de um conjunto de simulações que permita variar determinados parâmetros e comparar o resultado do conjunto de experimentos, isso será um facilitador para estudar impacto de diferentes plasticidades neurais.

### Legenda editorial

- `[preservar]`: conteúdo tecnicamente válido, sujeito apenas a revisão textual leve;
- `[corrigir]`: conteúdo com erro factual, inconsistência ou afirmação que precisa ser qualificada;
- `[atualizar]`: conteúdo válido na Fase 1, mas que precisa refletir o estado da Fase 2;
- `[adicionar]`: seção nova reservada para conteúdo ainda não redigido.
- `[esclarecer]`: sessão que necessita de mais clareza ou pesquisa, deve ser omitida ou comentada

![logotipo-ufabc-extenso](../assets/logotipo-ufabc-extenso.png)

# [preservar] Modelo neurocomputacional de reorganização motora

Lenin Cristi

CMCC - Universidade Federal do ABC (UFABC)
Santo André - SP - Brasil

lenin.cristi@aluno.ufabc.edu.br

Resumo. Este trabalho tem como objetivo a reprodução computacional e robótica do experimento Doman's Inclined Floor Method for Early Motor Organization Simulated with a Four Neurons Robot (2011) de Ropero Peláez e Lucas Santana, no qual um robô controlado por uma rede neural plástica de quatro neurônios aprende a organizar seu comportamento motor em um plano inclinado, inspirado no método de estimulação motora precoce de Glenn Doman.

## [preservar] Sumário

- `[preservar]` Resumo
- `[preservar]` Objetivo do Projeto
- `[preservar]` Introdução
  - `[preservar]` O experimento original
  - `[preservar]` A rede neural "não convencional"
  - `[preservar]` Resumo das diferenças
  - `[preservar]` Arquitetura e mapeamento motor
- `[preservar]` Metodologia
  - `[preservar]` Estratégia incremental de construção e validação
  - `[preservar]` Simulação de mundo
  - `[preservar]` Desenvolvimento
  - `[preservar]` Estado ao final da Fase 2
- `[atualizar]` Arquitetura detalhada da rede
  - `[atualizar]` Topologia e conectividade
  - `[atualizar]` Mapeamento neural-motor
  - `[atualizar]` Ordem temporal e fluxo causal
- `[atualizar]` Funções e equações
  - `[atualizar]` Normalização e soma sensorial
  - `[atualizar]` Ativação, saída sigmoidal e competição
  - `[atualizar]` Plasticidade sináptica
  - `[atualizar]` Plasticidade intrínseca
  - `[atualizar]` Distância, deslocamento e classificação do movimento
  - `[atualizar]` Aceleração, maraca e critérios de aprendizagem
- `[atualizar]` Parâmetros experimentais
  - `[atualizar]` Parâmetros da rede neural
  - `[atualizar]` Parâmetros do protocolo de aprendizagem
  - `[atualizar]` Parâmetros do mundo Webots
  - `[atualizar]` Parâmetros do robô e dos sensores
- `[atualizar]` Implementação e reprodutibilidade
  - `[atualizar]` Validação automatizada
  - `[atualizar]` Ensaios exploratórios
  - `[atualizar]` Telas da interface e da telemetria
  - `[atualizar]` Vídeos das execuções
- `[atualizar]` Limitações e hipóteses operacionais
- `[atualizar]` Protocolo dos ensaios formais
- `[atualizar]` Conclusão
- `[atualizar]` Anexos
  - `[atualizar]` Visão geral do repositório
  - `[atualizar]` Simulação de física
  - `[atualizar]` Simulação de colisão do robô
  - `[atualizar]` Simulação de controle
  - `[preservar]` Como clonar o repositório do projeto
  - `[atualizar]` Organização detalhada do repositório
  - `[atualizar]` Montagem do ambiente de desenvolvimento e simulação
   - `[atualizar]` Lista de software requerido
  - `[atualizar]` Webots
    - `[atualizar]` Nota sobre uso do Webots no Windows
  - `[atualizar]` Ambiente virtual e instalação de dependências
    - `[atualizar]` Usando pip
    - `[atualizar]` Usando conda
- `[corrigir]` Referências

## [preservar] Resumo

Este trabalho tem como objetivo a reprodução computacional e robótica do experimento *Doman's Inclined Floor Method for Early Motor Organization Simulated with a Four Neurons Robot (2011)* de Ropero Peláez e Lucas Santana, no qual um robô controlado por uma rede neural plástica de quatro neurônios aprende a organizar seu comportamento motor em um plano inclinado, inspirado no método de estimulação motora precoce de Glenn Doman.

A implementação original foi realizada utilizando *LEGO Mindstorms NXT* em *MATLAB* e dependia de sensores e estímulos relacionados à aceleração, à visão e ao som, representados respectivamente pela detecção de aceleração, por uma câmera apontada para a rampa listrada e por um microfone captando o som de uma maraca na meta. Este projeto desenvolve uma versão reproduzível do experimento utilizando uma linguagem multiparadigma flexível e uma arquitetura modular de sensoriamento e controle. O código integral do projeto está disponível em https://github.com/lnncrs/DomanNeurocomputationalModel

A reconstrução foi conduzida deliberadamente de forma incremental, separando a modelagem do mundo, a validação da física neste mundo, a construção do robô e sua equipagem com sensores, a interface de controle webots e por fim sua integração com a rede neural. Essa organização permitiu testar isoladamente cada componente em cada camada antes de integrá-lo ao experimento completo, reduzindo a dificuldade de identificar falhas e aumentando a reprodutibilidade do sistema.

Como resultado, foram obtidos varios ambientes experimentais reproduzíveis no Webots versionados em `webots\worlds`, sendo o principal deles `webots\worlds\experiment_inclined_plane.wbt` já integrado a uma rede neural recorrente e plástica de quatro neurônios, com controle motor, aquisição de telemetria detalhada para diversos sensores incluindo aceleração, retorno do estímulo de uma maraca sintética que premia deslocamento para a meta e registro detalhado das execuções.

<!-- ! TODO
Os planos inclinados e normais devem ser revisados para garantir que estao sendo usados os artefatos mais recentes e mesma perspectiva, plano com boxes precisa ser renomeado para melhor entendimento
-->

Os ensaios exploratórios já demonstram o funcionamento do fluxo completo, enquanto a avaliação do aprendizado e do comportamento emergente será realizada posteriormente por meio de uma série de experimentos controlados.

## [preservar] Objetivo do Projeto

Os objetivos centrais do experimento original são:

- Simular condições de aprendizado motor infantil;

- Observar o surgimento de comportamento emergente;

- Analisar, a partir desse comportamento, possíveis paralelos com processos de neuroplasticidade.

> **Nota:** Neste ponto entendemos que a simulação, o robô e mesmo o aprendizado são tratados como meios e não como objetivos fim.

## [preservar] Introdução

### [preservar] O experimento original

Antes da construção do projeto, foi imprescindível realizar uma leitura detalhada do artigo que descreve o experimento original *Doman's Inclined Floor Method for Early Motor Organization Simulated with a Four Neurons Robot (2011)*, também disponível no repositório em `docs\Testing the inclined plane technique with a four neurons robot.pdf`.

Essa leitura revelou um ponto fundamental sobre o experimento: O objetivo do experimento não era simplesmente fazer o robô aprender a se locomover, mas sim utilizar uma arquitetura robótica e neural simples para investigar como estímulos sensoriais e determinados mecanismos de plasticidade poderiam contribuir para a organização inicial do comportamento motor.

O experimento procura reproduzir, de maneira simplificada, alguns elementos presentes no método do plano inclinado de Doman:

- aceleração produzida durante o movimento sobre o plano inclinado, como analogia ao estímulo vestibular;

- transições visuais geradas pelas faixas pretas e brancas da rampa;

- estímulo sonoro produzido por uma maraca após movimentos descendentes em direção a meta;

- ambiente físico formado pelo plano inclinado;

- sistema neural simples, composto por quatro neurônios plásticos interconectados.

Inicialmente, o robô não possui uma direção preferencial. Quando uma sequência de comandos motores produz um movimento descendente, a ação da gravidade resulta em maior aceleração e em transições mais rápidas entre as faixas visuais da rampa. Além disso, o movimento descendente é seguido pelo estímulo sonoro da maraca. Esses estímulos influenciam os mecanismos de plasticidade sináptica e intrínseca, favorecendo a formação de sequências neurais associadas ao deslocamento sobre a rampa. No artigo, considera-se que o robô aprendeu quando executa movimentos na mesma direção durante cinco iterações consecutivas.

O modelo não pretende reproduzir integralmente o sistema nervoso infantil ou demonstrar diretamente como uma criança aprende a se locomover. Ele constitui uma analogia computacional controlada, utilizada para observar a relação entre estímulos sensoriais, plasticidade e organização motora e, a partir dela, formular hipóteses sobre processos envolvidos na aquisição inicial do movimento.

Assim, o aprendizado do robô não constitui o objetivo final do experimento, mas um meio para investigar, em um sistema simplificado e controlável, como estímulos sensoriais e mecanismos de plasticidade podem participar da organização do comportamento motor.

### [preservar] A rede neural utilizada

O artigo descreve uma rede totalmente interconectada composta por quatro unidades neuronais excitatórias do tipo *rate-code*. Cada neurônio recebe a soma dos estímulos sensoriais e sinais provenientes da atividade anterior dos demais neurônios e de sua própria conexão recorrente. Um mecanismo de competição mantém ativo apenas o neurônio com maior saída em cada iteração.

A arquitetura possui quatro conexões recorrentes, cada uma ligando um neurônio a si próprio, cujos pesos são mantidos fixos em *0,7*. As doze conexões entre neurônios diferentes possuem pesos modificáveis.

| **Recebe de / Saída de** | **N1** | **N2** | **N3** | **N4** |
| ------------------------ | -----: | -----: | -----: | -----: |
| **N1**                   |    0,7 |    w₁₂ |    w₁₃ |    w₁₄ |
| **N2**                   |    w₂₁ |    0,7 |    w₂₃ |    w₂₄ |
| **N3**                   |    w₃₁ |    w₃₂ |    0,7 |    w₃₄ |
| **N4**                   |    w₄₁ |    w₄₂ |    w₄₃ |    0,7 |

Tabela 1: Conexões neuronais na rede

Sendo:
- $w_{12}$: conexão de **N2 para N1**
- $w_{21}$: conexão de **N1 para N2**
- Os valores `0,7` na diagonal representam as conexões autorrecorrentes fixas.

O aprendizado ocorre de forma incremental a cada iteração por meio de dois mecanismos complementares: plasticidade sináptica, que altera os pesos entre os neurônios, e plasticidade intrínseca, que desloca a função de ativação de cada unidade de acordo com seu histórico de atividade.

Esses neurônios continuam sendo modelos artificiais, mas diferem daqueles empregados em muitas redes neurais convencionais. Não há camadas profundas, função de perda, dados rotulados ou retropropagação de erro.

A adaptação ocorre a partir do retorno sensorial produzido pelas consequências das ações do robô, que modula a atividade neuronal e, indiretamente, as alterações sinápticas.

A pequena quantidade de neurônios torna possível acompanhar diretamente os pesos, as ativações, os neurônios vencedores e as sequências motoras produzidas. Essa interpretabilidade é uma propriedade útil da arquitetura, embora o artigo não afirme explicitamente que a escolha de quatro neurônios tenha sido determinada exclusivamente por esse objetivo.

O modelo não pretende reproduzir toda a complexidade de um sistema neural biológico. Ele representa uma estrutura computacional simplificada, utilizada para investigar como plasticidade, competição e feedback sensorial podem contribuir para a organização progressiva do comportamento motor.

<!-- ! TODO
duvida se esta exata a sessao seguinte inclinado a omitir na fase 2 do relatorio e retornar com ela na fase 3
-->

### [esclarecer] Resumo das diferenças

Em comparação com redes neurais convencionalmente treinadas, o modelo apresenta:

- quatro neurônios excitadores totalmente interconectados;

- conexões recorrentes fixas e conexões não diagonais plásticas;

- função de ativação sigmoidal com deslocamento adaptável;

- plasticidade sináptica e intrínseca;

- competição entre os neurônios;

- adaptação contínua durante a interação com o ambiente;

- ausência de retropropagação de erro e de dados rotulados.

Esse conjunto de características permite observar diretamente como o estado da rede se modifica durante o experimento e como sequências de atividade neural se relacionam com as ações motoras executadas.

### [preservar] Arquitetura e mapeamento motor

O fluxo geral do sistema é:

```text
ação anterior
→ resposta do ambiente
→ aceleração + visão + som
→ normalização e soma sensorial
→ ativação recorrente
→ saída sigmoidal
→ competição
→ neurônio vencedor
→ atualização sináptica e intrínseca
→ nova ação motora
→ resposta do ambiente
→ próxima iteração
```

O mapeamento adotado na reconstrução é:

| Neurônio | Primitiva motora |
|---|---|
| N1 | conjunto frontal, sentido horário |
| N2 | conjunto frontal, sentido anti-horário |
| N3 | conjunto traseiro, sentido horário |
| N4 | conjunto traseiro, sentido anti-horário |

Tabela 2: Mapeamentos neurônio → movimento

<!-- ! TODO
o paragrafo seguinte nao conecta com o texto
-->

O artigo apresenta explicitamente o primeiro exemplo; a numeração das demais ações foi reconstruída a partir da combinação entre dois conjuntos de rodas e dois sentidos de rotação.


No robô virtual, cada roda possui um motor independente. Para preservar a organização funcional do experimento original, o adaptador do modo `LEARNING` agrupa esses motores em conjuntos frontal e traseiro. Como a competição mantém apenas um neurônio ativo por iteração, o comportamento motor emerge da sequência temporal das ações selecionadas.

> **Nota sobre a implementação atual:** O retorno de **aceleração** é calculado a partir da variação da aceleração longitudinal medida durante cada janela motora. O retorno do estímulo sonoro da **maraca** é produzido sinteticamente quando existe redução da distância até a área retangular da meta e ela é suficiente para que o movimento seja classificado como descendente. Portanto, a implementação atual não utiliza um par físico de microfone e alto-falante e o canal visual de detecção de listras permanece não implementado nesta etapa. Esses mecanismos serão detalhados nas seções de funções, equações e protocolo experimental.

> **Nota histórica:** Nas primeiras versões da simulação, o mapeamento `neuronios → movimento` foi interpretado como uma configuração diferencial entre os lados esquerdo e direito. A releitura do artigo levou à correção do modo `LEARNING` para a organização `neuronios → movimento` para os eixos frontal/traseiro em sentido horário e anti-horário. Os modos manual de controle `MANUAL` e automático anti colisão `AUTOMATIC` continuam utilizando controle diferencial e não foram afetados por essa mudança.

## [preservar] Metodologia

A reconstrução do experimento envolve componentes interdependentes:

- o ambiente inclinado;
- a dinâmica física;
- a estrutura do robô;
- os sensores embarcados;
- os estímulos externos;
- o controle motor;
- a rede neural.

Alterações em qualquer um desses elementos podem modificar o comportamento observado e, consequentemente, dificultar a identificação da origem de eventuais falhas.

No experimento original, a estrutura robótica foi construída com *LEGO Mindstorms NXT*, enquanto a rede neural e os comandos sensório-motores foram implementados em *MATLAB* por meio da *RWTH Mindstorms NXT Toolbox*.

A reprodução direta dessa estrutura em uma nova plataforma física exigiria que problemas mecânicos, eletrônicos, sensoriais e computacionais fossem tratados simultaneamente.

### [preservar] Estratégia incremental de construção e validação

Para reduzir essa complexidade, foi adotada uma estratégia incremental em camadas. Cada componente é inicialmente construído e validado de forma isolada e, posteriormente, integrado aos demais. Essa abordagem permite distinguir problemas relacionados ao ambiente, à física, ao robô, ao controle e ao modelo neural.

A simulação foi utilizada como ambiente inicial de desenvolvimento porque permite:

- controlar as condições experimentais;

- repetir ensaios sob configurações equivalentes;

- observar diretamente posições, velocidades, acelerações e comandos motores;

- testar componentes isoladamente;

- reduzir o custo de alterações mecânicas;

- registrar de forma sistemática as variáveis de cada execução.

A construção de um robô físico foi mantida como uma etapa posterior à validação do comportamento no ambiente simulado. O núcleo neural e o protocolo experimental foram separados da interface do simulador para favorecer sua reutilização futura.

> **Nota:** Por mais que a estrutura em camadas favoreça o reuso de código, uma implementação física ainda exigirá um adaptador específico para os sensores, motores, unidades de medida e restrições temporais da plataforma escolhida.

Para evitar confusão com as fases de entrega e documentação do projeto, os cinco blocos de desenvolvimento são tratados neste relatório como **etapas técnicas de implementação**.

| Etapa | Escopo | Estado ao final da Fase 2 |
|---|---|---|
| 1 - Ambiente | Construção dos planos inclinado e horizontal e validação de sua geometria | concluída |
| 2 - Física | Testes de gravidade, colisão, contato com a rampa e comportamento de sólidos | concluída |
| 3 - Robô | Modelagem do corpo, das rodas, dos motores, das juntas e dos sensores | concluída |
| 4 - Controle e instrumentação | Implementação dos modos de controle `MANUAL` e `AUTO`, telemetria e aquisição das variáveis experimentais | concluída |
| 5 - Integração neural | Implementação da rede de quatro neurônios, protocolo temporal e integração ao modo `LEARNING` | integração concluída; validação científica pendente |

Tabela 3: Completude técnica do projeto

> **Nota:** Na etapa técnica 4, foi necessário implementar dois modos adicionais de controle não previstos: `PASSIVE_FREE` e `PASSIVE_REALISTIC`. No primeiro, o torque disponível dos motores é desativado, deixando as rodas livres. No segundo, o torque disponível é limitado a 0,03 N·m por roda, representando uma pequena resistência dos motores. Esses modos foram utilizados para testar o deslizamento e a influência da gravidade sobre o robô nos planos inclinados.

A conclusão de uma etapa técnica indica que seus componentes essenciais estão implementados e funcionalmente integrados. Isso não significa, por si só, que todas as hipóteses científicas associadas tenham sido validadas. Em particular, a integração neural permite executar o experimento completo, mas a atribuição do comportamento observado à plasticidade exige ensaios controlados e comparações com condições de referência.

### [preservar] Simulação de mundo

<!-- ! TODO
Nomes de produtos como Webots, PyBullet e Jupyter, etc em paragrafos ou titulos que nao sejam em paths ou semalhante devem estar em italico
-->

Para a simulação, foi realizada uma pesquisa na qual foram considerados dois ambientes principais: Webots e *PyBullet*. O Webots foi escolhido por oferecer maior capacidade de representar motores, atuadores e sensores de maneira próxima a uma implementação física, dentro de um ambiente integrado de simulação. A plataforma também oferece suporte a controladores em Python, C e C++, além de uma biblioteca de mundos e componentes reutilizáveis.

Os principais motivos para a escolha do Webots foram:

- modelagem integrada de sensores, motores e atuadores;

- suporte a controladores em Python, C e C++;

- simulação da interação entre corpos, juntas e superfícies;

- biblioteca de mundos e componentes reutilizáveis;

- proximidade conceitual com uma futura implementação física.

Um ponto importante do Webots é permitir o desenvolvimento inicial dos controladores em Python, oferecendo maior flexibilidade para a implementação e validação do modelo neural. A plataforma também suporta controladores em C e C++, o que amplia as possibilidades de integração com outras plataformas e de futuras adaptações para hardware físico.

**A implementação foi organizada de forma que o modelo neural e o protocolo experimental não dependam diretamente dos detalhes internos do robô simulado.** Essa separação favorece a reutilização do núcleo do sistema, embora uma implementação física ainda exija um adaptador específico para os sensores, motores, unidades de medida e restrições temporais do hardware escolhido.

<!-- ! todo
aqui entra uma imagem de captura de tela do mapa de experimento com o carrinho
-->

A biblioteca de mundos, objetos e exemplos disponibilizada pelo Webots parcialmente preservada em `webots\tutorials` também foi um fator relevante para a escolha, pois forneceu referências para a construção inicial dos ambientes, das juntas, dos sensores e dos controladores utilizados no projeto.

### [preservar] Desenvolvimento

**O projeto foi desenvolvido com ferramentas abertas e organizado para favorecer a reprodução dos experimentos.**

O Webots é utilizado para a simulação física, enquanto Python implementa a rede neural, o protocolo experimental, a integração com o controlador e a geração dos artefatos de cada execução.

As dependências de sistema como o *gcc* e o *make* estão integralmente mapeadas na sessao `Montagem do ambiente de desenvolvimento e simulação`.

As dependências Python são declaradas no `pyproject.toml` e consolidadas pelo *uv*, com alternativas para *pip* e *conda* e estão também mapeadas na mesma sessão.

Uma listagem preliminar do *software* utilizado é a que segue:

- Plataformas *Windows* e *Linux* suportadas com instruções disponíveis para ambas pois a reprodução dos experimentos é agnóstica a sistema operacional.

- Ferramentas *Git* para clonar e operar o repositório de projeto;

- O *Webots R2025a* para rodar as simulações;

- Compilador *gcc* com *make* e *sh* disponíveis pois é utilizado pelo *Webots R2025a* quando da criação das bibliotecas de *controllers* e *plugins*;

- Ambiente *uv* recomendado, mas pode-se usar *pip* ou *conda*;

- Python 3.13 fornecido pelo ambiente de escolha acima;

- Uma validação da rede com dados sinteticos usa um notebook *Jupyter*, adicionalmente *numpy*, *pandas* e *matplotlib* são recomendados;

- Os testes automatizados usam *pytest*;

### [preservar] Estado do projeto ao final da Fase 2

**Ao final da Fase 2, o ambiente físico, o robô, a instrumentação e a rede neural encontram-se integrados no modo `LEARNING`.** Cada ação neural é mantida durante uma janela temporal, após a qual o deslocamento e a aceleração são agregados. O movimento é então classificado, a maraca é produzida quando ocorre descida e os estímulos resultantes alimentam o passo neural seguinte.

O fluxo experimental completo já produz telemetria, registros por iteração, metadados, resumos e relatórios HTML. Os testes automatizados validam os componentes de software, e as execuções exploratórias demonstram que o robô consegue completar o percurso. Esses resultados confirmam a integração do sistema, mas ainda não permitem atribuir o comportamento observado à plasticidade neural.

Uma lista com *features* chave do projeto funcionais nesta fase é a que segue:

- Mapas webots criados em separado dos artefatos de robo para permitir reutilizacao com exemplares planos e inclinados

- Area de meta criada em verde para facil identificacao e parametrizada para reuso

- Instrumentacao embarcada do robo criada acoplada ao robo e independente do mapa

- Controle do robo independente e parametrizavel

- Todas as variaveis de simulacao e experimento identificadas e parametrizaveis centralmente para facilitar alteracao

- Tela interativa de acompanhamento da simulacao com telemetria e dados de treinamento em tempo real;

- Controle manual baseado em joystic para exploracao livre do mapa;

- Geração de metadados e logs do experimento em JSONL acompanhados de um relatório HTML com detalhes da rede gerada;

<!-- ! todo
aqui entram duas imagens de um close no carrinho e da tela de treinamento lado a lado
-->


## [atualizar] Arquitetura detalhada da rede

<!-- ! todo
paragrafo seguinte nao conecta com o texto, talvez uma introducao simples
-->

A implementação mantém separadas a arquitetura descrita no artigo e as hipóteses necessárias para torná-la executável. A rede não depende do Webots: ela recebe três valores sensoriais e devolve uma das quatro ações motoras abstratas.

<!-- ! todo
incluir referencia ao arquivo principal e classe da implementacao neuronal
-->

### [atualizar] Topologia e conectividade

<!-- ! todo
esse trecho seguinte em parte esta redundante com a explicacao em tabela anterior, talvez remontar os paragrafos seguintes
-->

A rede possui quatro neurônios excitatórios do tipo *rate-code*, totalmente
interconectados. A matriz `W[i][j]` representa a conexão do neurônio `j` para o
neurônio `i`. As quatro conexões diagonais são recorrentes e permanecem fixas
em `0,7`; as doze conexões não diagonais são plásticas.

A mesma soma sensorial chega aos quatro neurônios. A diferença entre suas
ativações surge do estado recorrente, dos pesos e dos deslocamentos individuais
das funções sigmoidais. Após o cálculo das saídas, uma competição mantém ativo
somente o neurônio vencedor.

### [atualizar] Mapeamento neural-motor

Cada neurônio corresponde a uma primitiva motora,o modelo neural conhece apenas as ações abstratas e a conversão para os quatro motores do robô é feita
por um adaptador.

| Neurônio | Ação abstrata | Comando no robô virtual |
|---|---|---|
| N1 | conjunto frontal, horário | rodas 1 e 2 com velocidade positiva |
| N2 | conjunto frontal, anti-horário | rodas 1 e 2 com velocidade negativa |
| N3 | conjunto traseiro, horário | rodas 3 e 4 com velocidade positiva |
| N4 | conjunto traseiro, anti-horário | rodas 3 e 4 com velocidade negativa |

Tabela 4: Tradução das açoes abstratas em primitivas motoras

<!-- ! todo
esse trecho seguinte esta desconexo
-->

Os sinais físicos de rotação são parâmetros do adaptador e precisam ser confirmados visualmente sempre que a orientação dos motores ou dos eixos for
alterada.

<!-- ! todo
incluir referencia do codigo onde é feita a tradução acao -> primitiva
-->


### [atualizar] Ordem temporal e fluxo causal

Uma iteração representa a consequência de uma ação já selecionada. No início, a rede recebe entradas nulas e escolhe a primeira ação. Em seguida, cada ciclo obedece à ordem:

<!-- ! todo
escolhe como? criterio? e esse trecho nao duplica a explicacao inicial sobre a ordem de etapas?
-->

```text
ação anterior
-> movimento mantido durante uma janela temporal
-> deslocamento e aceleração observados
-> classificação do movimento
-> produção dos estímulos sensoriais
-> ativação e competição neural
-> plasticidade sináptica e intrínseca
-> seleção da próxima ação
```

Essa ordem impede que a maraca influencie a ação que a produziu: o som gerado por uma descida alimenta somente a decisão neural seguinte.

<!-- ! todo
incluir como esse "impede" é implementado no codigo
-->

## [atualizar] Funções e equações

As equações publicadas foram implementadas diretamente quando possível. As expressões de ativação, normalização, competição e integração com o ambiente completam pontos que não são especificados integralmente no artigo.

<!-- ! todo
incluir uma tabela que indique a equacao, descritivo curto, se foi trazida do artigo e sem sim qual, se não porque foi escolhida
-->

<!-- ! todo
para as equacoes abaixo, incluir a notacao matematica e sempre incluir abaixo uma sessao "Onde:" descrevendo cada item da equacao e na sequencia, a referencia da implementacao em codigo
-->

### [atualizar] Normalização e soma sensorial

Cada canal sensorial `k` é normalizado por uma transformação linear:

```text
x'_k(t) = (x_k(t) - offset_k) * scale_k
```

A entrada comum aos quatro neurônios é:

```text
S(t) = acceleration'(t) + visual'(t) + sound'(t)
```

Na configuração atual, todos os offsets são zero, todas as escalas são `1,0` e o canal visual recebe zero.

### [atualizar] Ativação, saída sigmoidal e competição

A ativação operacional combina a entrada sensorial atual com a saída
competitiva do passo anterior:

```text
a_i(t) = S(t) + sum_j(W_ij(t) * O^c_j(t-1)) + noise_i(t)
```

A saída sigmoidal corresponde à equação 3 do artigo:

```text
O_i(t) = 1 / (1 + exp(-gain * (a_i(t) - shift_i(t))))
```

<!-- ! todo
25 veio da onde? e esta nao fluido
-->

O ganho é `25`. No modo padrão, vence o neurônio de maior saída; os demais recebem saída competitiva zero. Empates são resolvidos pelo gerador pseudoaleatório associado à seed do ensaio. O ruído de ativação é opcional e
permanece desligado.

### [atualizar] Plasticidade sináptica

A variação dos pesos segue a regra pré-sináptica de Grossberg, equação 2 do
artigo:

```text
delta_W_ij(t) = epsilon * I_j(t) * (a_i(t) - W_ij(t))
W_ij(t+1) = W_ij(t) + delta_W_ij(t)
```

<!-- ! todo
confuso abaixo
-->

Na implementação, `I_j(t)` é a saída competitiva do passo anterior. Por padrão, somente os pesos que chegam ao vencedor atual são candidatos à atualização. Esse escopo, denominado `winner_only`, é uma hipótese operacional; uma variante permite atualizar todos os neurônios pós-sinápticos. As conexões diagonais são
reafirmadas em `0,7` após cada passo.

### [atualizar] Plasticidade intrínseca

O deslocamento da sigmoide segue a equação 4:

```text
shift_i(t+1) = (xi * O_i(t) + shift_i(t)) / (1 + xi)
```

<!-- ! todo
confuso abaixo
-->

No modo padrão, `O_i(t)` é a saída após a competição. Consequentemente, apenas
o vencedor apresenta saída diferente de zero, enquanto os deslocamentos dos
demais neurônios também evoluem pela divisão por `1 + xi`. A saída anterior à
competição permanece disponível como variante experimental.

### [atualizar] Distância, deslocamento e classificação do movimento

A posição do robô é comparada com o retângulo da meta, e não apenas com seu
centro. Para uma meta de centro `(x_g, y_g)`, largura `w` e comprimento `l`:

```text
d_x = max(abs(x - x_g) - w/2, 0)
d_y = max(abs(y - y_g) - l/2, 0)
d   = sqrt(d_x^2 + d_y^2)
```

O deslocamento da janela é `delta_d = d_final - d_inicial`. Como aproximar-se
da meta reduz a distância, define-se `q = -delta_d`. Com limiar `tau`:

```text
q > tau    -> DOWN
q < -tau   -> UP
caso contrário -> STATIONARY
```

### [atualizar] Aceleração, maraca e critérios de aprendizagem

A aceleração de uma janela é a média da variação absoluta da componente longitudinal em relação ao início da ação:

```text
acceleration = mean_k(abs(a_x(k) - a_x(initial)))
```

Quando o movimento é classificado como `DOWN`, a entrada sonora da iteração seguinte recebe a intensidade da maraca; nos demais casos, recebe zero. São registrados dois critérios: cinco movimentos consecutivos na mesma direção,
como no artigo, e cinco movimentos consecutivos para baixo, como medida adicional desta reconstrução. A repetição de um neurônio vencedor, por si só, não é considerada aprendizagem.

## [atualizar] Parâmetros experimentais

As tabelas seguintes registram os valores efetivamente utilizados na configuração atual.

Parâmetros classificados como hipótese deverão ser
mantidos nos metadados e avaliados nos ensaios formais.

### [atualizar] Parâmetros da rede neural

| Parâmetro | Valor | Origem |
|---|---:|---|
| número de neurônios | 4 | artigo |
| peso recorrente | 0,7 | artigo |
| ganho sigmoidal | 25 | artigo |
| pesos não diagonais iniciais | uniforme entre 0,1 e 0,9 | hipótese |
| taxa sináptica `epsilon` | 0,01 | hipótese |
| taxa intrínseca `xi` | 0,01 | faixa publicada |
| deslocamento inicial | 0,5 | hipótese |
| competição | determinística | hipótese operacional |
| escopo da plasticidade | `winner_only` | hipótese operacional |
| fonte da plasticidade intrínseca | saída após competição | hipótese operacional |
| desvio do ruído de ativação | 0,0 | desativado |
| limites adicionais dos pesos | nenhum | não publicado |
| seed da configuração integrada | 42 | reprodutibilidade |

<!-- ! todo
estes parametros estao centralizados? onde sao configurados?
-->

### [atualizar] Parâmetros do protocolo de aprendizagem

| Parâmetro | Valor atual |
|---|---:|
| duração nominal da ação | 0,5 s |
| velocidade das rodas no modo `LEARNING` | 3,0 rad/s |
| limiar de movimento estacionário | 0,005 m |
| intensidade sonora da maraca | 0,1 |
| escala da aceleração | 1,0 |
| entrada visual | 0,0 |
| movimentos consecutivos para o critério | 5 |
| sinal usado para representar descida | -1 |

<!-- ! todo
estes parametros estao centralizados? onde sao configurados?
-->

### [atualizar] Parâmetros do mundo Webots

| Parâmetro | Valor atual |
|---|---:|
| versão dos arquivos Webots | R2025a |
| passo básico do mundo | 16 ms |
| passo do controlador | 64 ms |
| seed do mundo | 42 |
| inclinação da rampa | 12 graus (`0,20943951023932` rad) |
| plataforma de chegada | 1 x 1 m |
| rampa | 2 x 1 m |
| altura dos guardrails | 0,1 m |
| espaçamento das faixas | 0,1 m |
| largura das faixas | 0,01 m |
| largura da linha de chegada | 0,02 m |
| área lógica da meta | 0,96 x 0,96 x 0,30 m |
| permanência configurada na meta | 0,5 s; o modo `LEARNING` atual conclui na entrada |

<!-- ! todo
estes parametros estao centralizados? onde sao configurados?
-->

Gravidade, atrito e alguns parâmetros de contato permanecem herdados dos defaults do Webots e deverão ser explicitados antes da campanha formal.

<!-- ! todo
onde estao definidos estes ou qual o padrão deles? podemos criar uma tabela para eles?
-->

### [atualizar] Parâmetros do robô e dos sensores

| Parâmetro | Valor atual |
|---|---:|
| dimensões do corpo | 0,20 x 0,10 x 0,05 m |
| rodas e motores | 4 |
| raio da roda | 0,04 m |
| espessura da roda | 0,02 m |
| densidade configurada do corpo | 1000 kg/m3 |
| distância inicial ao longo da rampa | 1,45 m |
| torque do modo passivo realista | 0,03 N.m por roda |
| instrumentação | acelerômetro, giroscópio, GPS e bússola |
| sensores de proximidade disponíveis | frontal diagonal esquerdo, frontal diagonal direito, frontal, traseiro, esquerdo e direito |
| posição usada no protocolo | GPS |
| aceleração usada na rede | componente longitudinal do acelerômetro |
| som usado na rede | estímulo lógico, sem microfone ou alto-falante |

<!-- ! todo
estes parametros sao mais fixos certo?
-->

## [atualizar] Implementação e reprodutibilidade

O código separa quatro responsabilidades principais:

- `src/neural`: estado, competição e plasticidade da rede;

- `src/experiments`: ordem causal, critérios, registro e relatório;

- `src/control`: tradução das ações abstratas para comandos de rodas;

<!-- ! todo
esse item abaixo esta certo?
-->

- `webots\controllers\four_wheels_manual`: controlador Webots com aquisição dos sensores, controle motor, execução da janela de acompanhamento.

Cada execução produz `metadata.json`, `iterations.jsonl`, `summary.json` e um relatório HTML `report.html`derivado na pasta `\experiments\runs\learning_{ISO UTC Timestamp}_{seed}\`.

Os metadados registram as configurações neural,
experimental, do runtime e da meta. A seed torna a inicialização reproduzível;

<!-- ! todo
a sessao abaixo sobre testes e como rodar potencialmente vai para os anexos
-->

### [atualizar] Testes automatizados

A implementação possui testes automatizados distribuídos entre quatro conjuntos:

<!-- ! todo
apontar o caminho relativo em cada teste
-->

- equações, inicialização, competição e plasticidade da rede;

- causalidade, classificação do movimento, critérios e arquivos de execução;

- mapeamento das quatro ações para os motores;

- integração temporal, meta, telemetria e geração do relatório HTML.

Esses testes verificam a consistência do software fora do Webots, mas não
substituem a validação visual dos sentidos motores nem os ensaios científicos.

O ambiente Python 3.13 é descrito pelo `pyproject.toml` e pelo `uv.lock`. O
comando recomendado para instalar dependências e executar os testes é:

```bash
uv sync --all-groups --all-extras
uv run pytest
```

### [atualizar] Ensaios exploratórios

<!-- ! todo
essa sessao deve virar uma explicacao dos dados e arquivos gerados na rodada de um experimento
-->

Há seis execuções exploratórias registradas, todas encerradas por chegada à
meta. O número de iterações variou entre 43 e 129, e três execuções geraram o
relatório HTML completo. Cinco registros já utilizam o esquema atual dos dois
critérios de aprendizagem.

Essas execuções foram realizadas enquanto a implementação ainda evoluía e não
devem ser agregadas como repetições de um mesmo experimento. Elas demonstram o
funcionamento do fluxo completo, mas não permitem atribuir a chegada à meta à
plasticidade da rede.

### [atualizar] Telas da interface e da telemetria

<!-- ! todo
isso aqui vira uma explicacao de operacao do experimento
-->

Esta subseção deverá destacar a execução do modo `LEARNING`, incluindo o
neurônio vencedor, a ação selecionada, a direção observada, o estado da maraca,
os contadores dos critérios e a chegada à meta. Também deverá apresentar uma
tela do relatório HTML produzido ao final da execução.

<!-- ! todo
incluir imagem do mapa
incluir imagem da tela explicando cada grupo de controles
incluir mapoeamento do joystic com cada botao e funcao
incluir nota que a versao fase 3 tera mapeamento no teclado tambem
-->

### [atualizar] Execuções de exemplo

<!-- ! todo
isso aqui vira uma sessao de limitacoes e proximos passos
-->

Serão selecionados vídeos curtos que mostrem as quatro primitivas motoras, uma execução completa no plano inclinado e a correspondência entre movimento, telemetria e estímulo sonoro. Os vídeos deverão informar a versão do código e a
configuração utilizada.

<!-- ! todo
incluir imagem de uma execucao
incluir video no youtube (url) de uma execucao
-->

## [atualizar] Limitações e hipóteses operacionais

<!-- ! todo
isso aqui vira uma sessao de limitacoes e proximos passos
-->

Na configuração atual, a rede utiliza a aceleração longitudinal e o estímulo
sonoro produzido logicamente após movimentos descendentes. O canal visual
permanece desativado e recebe valor zero. A normalização da aceleração e os
parâmetros temporais ainda deverão ser calibrados antes dos ensaios formais.

A meta possui permanência nominal de `0,5 s` em sua configuração, mas o runtime
de aprendizagem encerra a execução assim que o robô entra na região. Esse
comportamento deverá ser mantido como decisão explícita ou alinhado ao tempo de
permanência antes da campanha experimental.

A implementação foi validada no ambiente simulado. Uma futura plataforma
física exigirá um adaptador próprio para sensores, motores, unidades de medida
e restrições temporais.

## [atualizar] Protocolo dos ensaios formais

<!-- ! todo
ressaltar que a fase 3 permitira executar um batch de experimentos com variacoes de parametros para permitir comparar alteracoes de variaveis a plasticidade gerada
-->

Antes da campanha experimental, deverão ser congelados os parâmetros, a versão
do código e as condições de execução. Os ensaios deverão incluir repetições com
seeds registradas e condições de referência capazes de separar o efeito da
plasticidade do deslocamento produzido pela física da rampa.

## [atualizar] Conclusão

<!-- ! todo
atualizar por ultimo
-->

Apesar de desafios iniciais, principalmente no aprendizado e adaptação ao ambiente Webots, o projeto evoluiu para um estado funcional sólido de simulação com controle, mas ainda sem a rede neural integrada. A construção em camadas permitiu validar cada componente isoladamente, garantindo que o sistema como um todo esteja pronto para a integração da rede neural e a observação do comportamento emergente.

A abordagem em camadas permitiu:

- Reduzir complexidade

- Aumentar controle experimental

- Garantir reprodutibilidade

O projeto encontra-se próximo da etapa de aprendizado efetivo.

## [atualizar] Anexos

#### [atualizar] Visão geral do repositório

<!-- ! todo
remover a imagem e atualizar a arvode do repositorio com explicacoes de pastas e arquivos relevantes

introduzir brevemente antes a estrutura do repositorio
-->

A imagem repositorio_visao_geral dá uma ideia da organização atual do repositório.

![repositorio visao geral](../assets/repositorio_visao_geral.png)

Imagem: repositorio_visao_geral

<!-- ! todo
estas sessoes e videos podem ser movidos para depois do video do experrimento com descricao breve e im portancia historica (primeira simulacao com fisica, etc)
-->

#### [atualizar] Simulação de física

O filme inclined_plane é o plano inclinado com bolas para a simulação de física.

inclined_plane: https://youtu.be/qvbR1wQidVg

![inclined plane](../assets/inclined_plane.png)

Imagem: inclined_plane

#### [atualizar] Simulação de colisão do robô

O filme inclined_plane_with_robot e inclined_plane_with_robot_1 é o plano inclinado com o robo e controle de batida (nao rede neural) para testar se o robo funcionava na simulação, o último tem um guardrail mais baixo (o que impede a queda do robo).

inclined_plane_with_robot: https://youtu.be/1YhcI6GHoAs

inclined_plane_with_robot_1: https://youtu.be/zjciixsm578

![inclined plane with robot](../assets/inclined_plane_with_robot.png)

Imagem: inclined_plane_with_robot

#### [atualizar] Simulação de controle

O filme normal_plane_with_rotation é um primeiro teste com juntas, motores e ativação via interface de controle, foi um passo no projeto, pois abriu portas para que fosse possível controlar aspectos da simulação via interface programável.

normal_plane_with_rotation: https://youtu.be/ZKbbiObtkQ8

![normal plane with rotation](../assets/normal_plane_with_rotation.png)

Imagem: normal_plane_with_rotation

Os planos foram criados especificamente para o projeto.

Nos robôs de teste de batida foram usados modelos de exemplo da biblioteca aberta do Webots adaptados.

As peças rotacionando com controle foi necessário criar do zero porque era necessário entender a fundo como funcionava exatamente a "junção" entre duas peças nesta simulação.

### [preservar] Como clonar o repositório do projeto

<!-- ! todo
revisar
-->

Clone o repositório do projeto para acessar o código, os mundos e os protos:

Clonar usando HTTPS:

```text
git clone https://github.com/lnncrs/DomanNeurocomputationalModel.git
cd DomanNeurocomputationalModel
```

Clonar usando SSH (recomendado):

```text
git clone git@github.com:lnncrs/DomanNeurocomputationalModel.git
cd DomanNeurocomputationalModel
```

### [atualizar] Organização detalhada do repositório

<!-- ! todo
ficxa redundante com a sessao anterior, deve ser removida e usada a visao geral do repositorio
-->


O repositório do projeto está organizado da seguinte forma:

```text
├── 📄 README.md                          # Documentação principal
├── 📄 requirements.txt                     # Dependências Python
├── 📄 pyproject.toml                        # Configuração do projeto
│
├── 🖼️ assets/                                   # Imagens e diagramas
│
├── 💾 data/                                      # Dados de experimentos
│
├── 📚 docs/                                   # Documentação técnica
│
├── 🧪 experiments/                       # Scripts de testes e experimentos
│
├── 📓 notebooks/                         # Jupyter notebooks
│
├── 🧠 src/                                    # Código-fonte principal
│   │
│   ├── control/                              # Controladores do robô
│   │
│   ├── interfaces/                         # Interfaces de comunicação
│   │
│   └── neural/                              # Implementação da rede neural
│
└── 🤖 webots/                            # Ambiente de simulação Webots
│
├── controllers/                        # Controladores Webots
│
├── protos/                              # Definições de objetos Webots
│   ├── Ball.proto                                # Bola para testes de física
│   ├── FourNeuronRobot.proto         # Robô de 4 neurônios (uso futuro)
│   ├── Robot.proto                            # Robô genérico
│   ├── SimpleRobot.proto                 # Robô simplificado
│   ├── StableDifferentialRobot.proto # Robô diferencial estável
│   ├── StableRobot.proto                  # Robô estável
│   └── VeriSimpleRobot.proto           # Robô simples para testes
│
├── tutorials/                        # Mundos do tutorial Webots
│   ├── 4_wheels_robot.wbt
│   ├── appearance.wbt
│   ├── collision_avoidance.wbt
│   ├── compound_solid.wbt
│   ├── my_first_simulation.wbt
│   └── obstacles.wbt
│
└── worlds/                           # Mundos de simulação
├── normal_plane.wbt                    # Plano nivelado
├── inclined_plane.wbt                   # Plano inclinado (experimento)
├── inclined_plane_new.wbt          # Versão alternativa do plano inclinado
├── inclined_plane_with_balls.wbt # Teste de física
├── inclined_plane_with_robot.wbt # Experimento com robô
├── hexapod.wbt                            # Teste com hexápode
├── moon.wbt                                 # Teste de gravidade
└── sample.wbt                               # Mundo de exemplo
```

### [atualizar] Montagem do ambiente de desenvolvimento e simulação

<!-- ! todo
revisar, inserir numa ordem temporal

software requerido e como instalar

webots

nota de uso do webots no windows

gcc/make/sh

instalacao linux ubuntu e windows via msys ucrt

usando uv

usando pip

usando conda

vscode

vscode extensoes recomendadas

-->

É necessário ter o ambiente configurado para reproduzir os experimentos. A seguir estão as instruções para configurar o ambiente de desenvolvimento e simulação.

#### [atualizar] Lista de software requerido

- Toolchain C++ de sua preferência (GCC, Clang, MSVC)

- Git

- Webots

- Python +3.13 (Seja via conda ou instalação direta)

- vscode ou editor de código de sua preferência

A reprodução dos experimentos é garantida utilizando plataforma Windows ou Linux com a lista de software apresentada, no entanto outras plataformas podem ser utilizadas, desde que compatíveis com o Webots e Python +3.13.

### [atualizar] Webots

O Webots é o ambiente de simulação utilizado para a construção e teste do experimento. Ele oferece uma plataforma robusta para modelagem de robôs, ambientes físicos e controle de comportamento. Para instalar o Webots, siga as instruções na página oficial: https://cyberbotics.com/doc/guide/installing-webots

Importante: Certifique-se de instalar a versão mais recente do Webots para garantir compatibilidade com os mundos e protos utilizados no projeto.

#### [atualizar] Nota sobre uso do Webots no Windows

O Webots no Windows pode não herdar o caminho correto do Python no disparo, isso faz com que simulações com controle Python (ex: webots\worlds\normal_plane.wbt) falhem de maneira silenciosa, fechando a simulação logo após o carregamento. Para que isso não ocorra, abra o Webots a partir do terminal, com o ambiente Webots já ativo.

Ativar o ambiente webots:

```text
conda activate webots
```

Abrir o Webots:

```text
& "C:\Program Files\Webots\msys64\mingw64\bin\webots.exe" --stdout --stderr
```

A linha de comando do Webots depende da instalação, o caminho apresentado é o caminho padrão, mas pode variar dependendo do local onde o Webots foi instalado. Certifique-se de ajustar o caminho conforme necessário para a sua instalação.

### [atualizar] Ambiente virtual e instalação de dependências

Vamos mostrar a seguir um exemplo de como criar o ambiente necessário usando duas abordagens: pip e conda.

#### [atualizar] Usando pip

Certifique-se de ter instalado o motor Python +3.13 e instale as dependências do projeto com:

```text
pip install -r requirements.txt
```

Dentro do repositório do projeto.

Use preferencialmente um ambiente virtual para isolar as dependências do projeto.

#### [atualizar] Usando conda

Instalando o conda

Utilize a referência oficial Conda-Forge para instalar o conda no seu ambiente https://conda-forge.org/download/

Ou utilize a referência oficial Anaconda para instalar o miniconda no seu ambiente https://docs.anaconda.com/miniconda/install/

Criando o ambiente virtual

Para criar um ambiente virtual chamado webots com Python 3.13 utilizando o conda, use o comando:

```text
conda create -n webots python=3.13
```

Ativando o ambiente

Após a criação do ambiente virtual, ative ele com

```text
conda activate webots
```

Instalando dependências

Com o ambiente virtual ativado, instale as dependências do projeto com:

```text
pip install -r requirements.txt
```

Criando o ambiente a partir de arquivo (Alternativo)

Para criar o ambiente com os pacotes base a partir de arquivo requirements.txt, utilize o comando:

```text
pip install -r requirements.txt
```

Ou para criar o ambiente com os pacotes base a partir de arquivo yml, utilize o comando:

```text
conda env create -f environment.yml
```

Dentro do repositório do projeto.

Use preferencialmente um ambiente virtual para isolar as dependências do projeto.

## [corrigir] Referências

Francisco Javier Ropero Peláez, Lucas Galdiano Ribeiro Santana
Doman's Inclined Floor Method for Early Motor Organization Simulated with a Four Neurons Robot (2011)
https://www.semanticscholar.org/paper/Doman's-Inclined-Floor-Method-for-Early-Motor-with-Peláez-Santana/a1d9815865dcf65b909aeaf985f2f96c99be9dd5

J. R. Peláez, Marcelo Simoes
A computational model of synaptic metaplasticity (1999)
https://www.semanticscholar.org/paper/A-computational-model-of-synaptic-metaplasticity-Peláez-Simoes/ba93f797064a0035c6fe37836b055f84d85c61f1

J. R. Peláez, J. Piqueira
Biological Clues for Up-to-Date Artificial Neurons (2007)
https://www.semanticscholar.org/paper/Biological-Clues-for-Up-to-Date-Artificial-Neurons-Peláez-Piqueira/6dc2349c03495f5465df0d6d1ed93c31adde8189

N S Desai, L C Rutherford, G G Turrigiano
Plasticity in the intrinsic excitability of cortical pyramidal neurons (1999)
https://pubmed.ncbi.nlm.nih.gov/10448215/

Niraj S Desai
Homeostatic plasticity in the CNS: synaptic and intrinsic forms (2003)
https://pubmed.ncbi.nlm.nih.gov/15242651/

CMCC - Universidade Federal do ABC (UFABC) - Santo André - SP - Brasil
