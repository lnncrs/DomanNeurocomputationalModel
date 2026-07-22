<!--
Registro histórico da Fase 1.
Fonte: docs/not-versioned/Relatorio01.docx
A redação original foi preservada; apenas a marcação foi adaptada para Markdown.
-->

> [!NOTE]
> **Documento de trabalho da Fase 2.** Este arquivo foi criado como cópia
> integral de `docs/fase01-relatorio.md` para permitir uma revisão incremental
> e rastreável. O conteúdo herdado permanece, por enquanto, como registro da
> Fase 1 e pode conter descrições, próximos passos e conclusões obsoletos.

## [atualizar] Escopo e estado da Fase 2

Este relatório consolidará a evolução do projeto após a primeira entrega. A
Fase 2 de implementação e integração compreende a correção e parametrização do
mundo inclinado, a definição lógica da meta, a aquisição de aceleração, a
produção causal da maraca, a implementação da rede plástica de quatro
neurônios, sua integração ao modo `LEARNING`, a telemetria experimental e a
geração dos artefatos de cada execução.

No estado atual, a implementação de engenharia e o fluxo experimental de ponta
a ponta estão concluídos e cobertos por testes automatizados. As execuções já
realizadas são exploratórias: demonstram o funcionamento do sistema, mas não
constituem ainda uma campanha científica controlada nem evidência suficiente
para atribuir o comportamento observado à plasticidade neural.

As próximas revisões deste documento deverão corrigir as passagens herdadas
que descrevem a rede e sua integração como trabalho futuro, documentar as
equações e hipóteses operacionais, consolidar os parâmetros em tabelas e
definir o protocolo dos ensaios formais.

### [preservar] Legenda editorial

- `[preservar]`: conteúdo historicamente e tecnicamente válido, sujeito apenas
  a revisão textual leve;
- `[corrigir]`: conteúdo com erro factual, inconsistência ou afirmação que
  precisa ser qualificada;
- `[atualizar]`: conteúdo válido na Fase 1, mas que precisa refletir o estado da
  Fase 2;
- `[adicionar]`: seção nova reservada para conteúdo ainda não redigido.

![logotipo-ufabc-extenso](../assets/logotipo-ufabc-extenso.png)

# Modelo neurocomputacional de reorganizacao motora

Lenin Cristi

CMCC – Universidade Federal do ABC (UFABC)
Santo André – SP – Brasil

lenin.cristi@aluno.ufabc.edu.br

Resumo. Este trabalho tem como objetivo a reprodução computacional e robótica do experimento Doman's Inclined Floor Method for Early Motor Organization Simulated with a Four Neurons Robot (2010) de Ropero Peláez e Lucas Santana, no qual um robô controlado por uma rede neural plástica de quatro neurônios aprende a organizar seu comportamento motor em um plano inclinado, inspirado no método de estimulação motora precoce de Glenn Doman.

## Sumário

- `[atualizar]` Resumo
- `[preservar]` Objetivo do Projeto
- `[preservar]` Introdução
  - `[corrigir]` O experimento original
  - `[corrigir]` A rede neural "não convencional"
    - `[corrigir]` Resumo das diferenças
    - `[corrigir]` Rede proposta
- `[atualizar]` Metodologia
  - `[atualizar]` Como construir (e testar) em camadas
  - `[atualizar]` Arquitetura de cada camada
  - `[preservar]` Simulação de mundo
  - `[atualizar]` Desenvolvimento
    - `[atualizar]` Fase atual
    - `[atualizar]` Visão geral do repositório
    - `[preservar]` Simulação de física
    - `[preservar]` Simulação de colisão do robô
    - `[preservar]` Simulação de controle
  - `[atualizar]` Próximos passos
    - `[atualizar]` Modelagem da rede neural
    - `[atualizar]` Diversidade de sensores
    - `[atualizar]` Modelo físico
- `[adicionar]` Arquitetura detalhada da rede
  - `[adicionar]` Topologia e conectividade
  - `[adicionar]` Mapeamento neural-motor
  - `[adicionar]` Ordem temporal e fluxo causal
- `[adicionar]` Funções e equações
  - `[adicionar]` Normalização e soma sensorial
  - `[adicionar]` Ativação, saída sigmoidal e competição
  - `[adicionar]` Plasticidade sináptica
  - `[adicionar]` Plasticidade intrínseca
  - `[adicionar]` Distância, deslocamento e classificação do movimento
  - `[adicionar]` Aceleração, maraca e critérios de aprendizagem
- `[adicionar]` Parâmetros experimentais
  - `[adicionar]` Parâmetros da rede neural
  - `[adicionar]` Parâmetros do protocolo de aprendizagem
  - `[adicionar]` Parâmetros do mundo Webots
  - `[adicionar]` Parâmetros do robô e dos sensores
- `[adicionar]` Implementação e reprodutibilidade
- `[adicionar]` Validação automatizada
- `[adicionar]` Ensaios exploratórios
- `[adicionar]` Limitações e hipóteses operacionais
- `[adicionar]` Protocolo dos ensaios formais
- `[atualizar]` Conclusão
- `[atualizar]` Anexos
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

Este trabalho tem como objetivo a reprodução computacional e robótica do experimento Doman's Inclined Floor Method for Early Motor Organization Simulated with a Four Neurons Robot (2010) de Ropero Peláez e Lucas Santana, no qual um robô controlado por uma rede neural plástica de quatro neurônios aprende a organizar seu comportamento motor em um plano inclinado, inspirado no método de estimulação motora precoce de Glenn Doman.

A implementação original foi realizada em MATLAB e dependente de sensores ambientais externos posicionais, visuais e sonoros (sensor de aceleração, rampa listrada e maraca sonora), este projeto visa desenvolver uma versão totalmente reprodutível do experimento utilizando linguagem multiparadigma flexível e sensoriamento embarcado. O código do projeto está disponível em https://github.com/lnncrs/DomanNeurocomputationalModel

A reconstrução foi conduzida de forma incremental, separando a modelagem do mundo, a validação da física, a construção do robô, a interface de controle e a integração neural. Essa organização permitiu testar isoladamente cada componente antes de integrá-lo ao experimento completo, reduzindo a dificuldade de identificar falhas e aumentando a reprodutibilidade do sistema.

Como resultado, foi obtido um ambiente experimental reproduzível no Webots, integrado a uma rede neural recorrente e plástica de quatro neurônios, com aquisição de aceleração, produção causal de estímulo sonoro, controle motor e registro detalhado das execuções. Os ensaios exploratórios demonstram o funcionamento do fluxo completo, enquanto a avaliação do aprendizado e do comportamento emergente será realizada posteriormente por meio de uma campanha experimental controlada e de métricas quantitativas.

## [preservar] Objetivo do Projeto

Os objetivos centrais do experimento são:

- Simular condições de aprendizado motor infantil;

- Observar o surgimento de comportamento emergente;

- Analisar, a partir desse comportamento, possíveis paralelos com processos de neuroplasticidade.

Ou seja a simulação, o robô e o aprendizado são tratados como meios, não fins.

## [preservar] Introdução

### [preservar] O experimento original

Antes da construção do projeto, foi imprescindível realizar uma leitura detalhada do artigo que descreve o experimento original *Doman's Inclined Floor Method for Early Motor Organization Simulated with a Four Neurons Robot (2011)*, também disponível no repositório. Essa leitura revelou um ponto fundamental sobre o experimento:

O objetivo do experimento não era simplesmente fazer o robô aprender a se locomover, mas sim utilizar uma arquitetura robótica e neural simples para investigar como estímulos sensoriais e mecanismos de plasticidade poderiam contribuir para a organização inicial do comportamento motor.

O experimento procura reproduzir, de maneira simplificada, alguns elementos presentes no método do plano inclinado de Doman:

- aceleração produzida durante o movimento sobre o plano inclinado, como analogia ao estímulo vestibular;

- transições visuais geradas pelas faixas pretas e brancas da rampa;

- estímulo sonoro produzido por uma maraca após movimentos descendentes;

- ambiente físico formado pelo plano inclinado;

- sistema neural simples, composto por quatro neurônios plásticos interconectados.

Inicialmente, o robô não possui uma direção preferencial. Quando uma sequência de comandos motores produz um movimento descendente, a ação da gravidade resulta em maior aceleração e em transições mais rápidas entre as faixas visuais da rampa. Além disso, o movimento descendente é seguido pelo estímulo sonoro da maraca. Esses estímulos influenciam os mecanismos de plasticidade sináptica e intrínseca, favorecendo a formação de sequências neurais associadas ao deslocamento sobre a rampa. No artigo, considera-se que o robô aprendeu quando executa movimentos na mesma direção durante cinco iterações consecutivas.

O modelo não pretende reproduzir integralmente o sistema nervoso infantil nem demonstrar diretamente como uma criança aprende a se locomover. Ele constitui uma analogia computacional controlada, utilizada para observar a relação entre estímulos sensoriais, plasticidade e organização motora e, a partir dela, formular hipóteses sobre processos envolvidos na aquisição inicial do movimento.

Assim, o aprendizado do robô não constitui o objetivo final do experimento, mas um meio para investigar, em um sistema simplificado e controlável, como estímulos sensoriais e mecanismos de plasticidade podem participar da organização do comportamento motor.

### [preservar] A rede neural "não convencional"

O artigo descreve uma rede totalmente interconectada composta por quatro unidades neuronais excitatórias do tipo rate-code. Cada neurônio recebe a soma dos estímulos sensoriais e sinais provenientes da própria rede. Um mecanismo de competição mantém ativo apenas o neurônio com maior saída em cada iteração.

A arquitetura possui quatro conexões recorrentes, cada uma ligando um neurônio a si próprio, cujos pesos são mantidos fixos em *0,7*. As doze conexões entre neurônios diferentes possuem pesos modificáveis. O aprendizado ocorre continuamente por meio de dois mecanismos complementares: plasticidade sináptica, que altera os pesos entre os neurônios, e plasticidade intrínseca, que desloca a função de ativação de cada unidade de acordo com seu histórico de atividade.

Esses neurônios continuam sendo modelos artificiais, mas diferem daqueles empregados em muitas redes neurais convencionais. Não há camadas profundas, função de perda, dados rotulados ou retropropagação de erro. A adaptação ocorre a partir das consequências sensoriais das ações executadas pelo robô, por meio de regras locais de plasticidade.

A pequena quantidade de neurônios torna possível acompanhar diretamente os pesos, as ativações, os neurônios vencedores e as sequências motoras produzidas. Essa interpretabilidade é uma propriedade útil da arquitetura, embora o artigo não afirme explicitamente que a escolha de quatro neurônios tenha sido determinada exclusivamente por esse objetivo.

O modelo não pretende reproduzir toda a complexidade de um sistema neural biológico. Ele representa uma estrutura computacional simplificada, utilizada para investigar como plasticidade, competição e feedback sensorial podem contribuir para a organização progressiva do comportamento motor.

#### [preservar] Resumo das diferenças

Em comparação com redes neurais convencionalmente treinadas, o modelo apresenta:

- quatro neurônios excitadores totalmente interconectados;

- conexões recorrentes fixas e conexões não diagonais plásticas;

- função de ativação sigmoidal com deslocamento adaptável;

- plasticidade sináptica e intrínseca;

- competição entre os neurônios;

- adaptação contínua durante a interação com o ambiente;

- ausência de retropropagação de erro e de dados rotulados.

Esse conjunto de características permite observar diretamente como o estado da rede se modifica durante o experimento e como sequências de atividade neural se relacionam com as ações motoras executadas.

#### [preservar] Arquitetura e mapeamento motor

O fluxo geral do sistema é:

```text
aceleração + visão + som
→ normalização e soma sensorial
→ ativação recorrente
→ saída sigmoidal
→ competição
→ neurônio vencedor
→ ação sobre um conjunto de rodas
→ resposta do ambiente
→ novos estímulos sensoriais
```

O mapeamento adotado na reconstrução é:

| Neurônio | Primitiva motora |
|---|---|
| N1 | conjunto frontal, sentido horário |
| N2 | conjunto frontal, sentido anti-horário |
| N3 | conjunto traseiro, sentido horário |
| N4 | conjunto traseiro, sentido anti-horário |

O artigo apresenta explicitamente o primeiro exemplo; a numeração das demais ações foi reconstruída a partir da combinação entre dois conjuntos de rodas e dois sentidos de rotação.

No robô virtual, cada roda possui um motor independente. Para preservar a organização funcional do experimento original, o adaptador do modo `LEARNING` agrupa esses motores em conjuntos frontal e traseiro. Como a competição mantém apenas um neurônio ativo por iteração, o comportamento motor emerge da sequência temporal das ações selecionadas.

> **Nota sobre a implementação atual:** a entrada de aceleração é calculada a partir da variação da aceleração longitudinal medida durante cada janela motora. O estímulo sonoro da maraca é produzido logicamente quando a redução da distância até a área retangular da meta é suficiente para que o movimento seja classificado como descendente. Portanto, a implementação atual não utiliza um par físico de microfone e alto-falante. O canal visual permanece desativado nesta etapa e recebe valor zero. Esses mecanismos serão detalhados nas seções de funções, equações e protocolo experimental.

> **Nota histórica:** nas primeiras versões da simulação, o mapeamento motor foi interpretado como uma configuração diferencial entre os lados esquerdo e direito. A releitura do artigo levou à correção do modo `LEARNING` para a organização frontal/traseira. Os modos manual e automático continuam utilizando controle diferencial e não foram afetados por essa mudança.

## [preservar] Metodologia

A reconstrução do experimento envolve componentes interdependentes: o ambiente inclinado, a dinâmica física, a estrutura do robô, os sensores, os estímulos externos, o controle motor e a rede neural. Alterações em qualquer um desses elementos podem modificar o comportamento observado e, consequentemente, dificultar a identificação da origem de eventuais falhas.

No experimento original, a estrutura robótica foi construída com LEGO Mindstorms NXT, enquanto a rede neural e os comandos sensório-motores foram implementados em MATLAB por meio da RWTH Mindstorms NXT Toolbox. A reprodução direta dessa estrutura em uma nova plataforma física exigiria que problemas mecânicos, eletrônicos, sensoriais e computacionais fossem tratados simultaneamente.

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

> **Nota de implementação:** Por mais que a estrutura em camadas favoreça o reuso de código, uma implementação física ainda exigirá um adaptador específico para os sensores, motores, unidades de medida e restrições temporais da plataforma escolhida.

Para evitar confusão com as fases de entrega e documentação do projeto, os cinco blocos de desenvolvimento são tratados neste relatório como **etapas técnicas de implementação**.

| Etapa | Escopo | Estado ao final da Fase 2 |
|---|---|---|
| 1 - Ambiente | Construção dos planos inclinado e horizontal e validação de sua geometria | concluída |
| 2 - Física | Testes de gravidade, colisão, contato com a rampa e comportamento de sólidos | concluída |
| 3 - Robô | Modelagem do corpo, das rodas, dos motores, das juntas e dos sensores | concluída |
| 4 - Controle e instrumentação | Implementação dos modos de controle, telemetria e aquisição das variáveis experimentais | concluída |
| 5 - Integração neural | Implementação da rede de quatro neurônios, protocolo temporal e integração ao modo `LEARNING` | integração concluída; validação científica pendente |

A conclusão de uma etapa técnica indica que seus componentes essenciais estão implementados e funcionalmente integrados. Isso não significa, por si só, que todas as hipóteses científicas associadas tenham sido validadas. Em particular, a integração neural permite executar o experimento completo, mas a atribuição do comportamento observado à plasticidade exige ensaios controlados e comparações com condições de referência.

### [preservar] Simulação de mundo

Para a simulação, foi realizada uma pesquisa na qual foram considerados dois ambientes principais: Webots e PyBullet. O Webots foi escolhido por oferecer maior capacidade de representar motores, atuadores e sensores de maneira próxima a uma implementação física, dentro de um ambiente integrado de simulação. A plataforma também oferece suporte a controladores em Python e C++, além de uma biblioteca de mundos e componentes reutilizáveis.

Os principais motivos para a escolha do Webots foram:

- modelagem integrada de sensores, motores e atuadores;

- suporte a controladores em Python e C++;

- simulação da interação entre corpos, juntas e superfícies;

- biblioteca de mundos e componentes reutilizáveis;

- proximidade conceitual com uma futura implementação física.

Um ponto importante do Webots é permitir o desenvolvimento inicial dos controladores em Python, oferecendo maior flexibilidade para a implementação e validação do modelo neural. A plataforma também suporta controladores em C++, o que amplia as possibilidades de integração com outras plataformas e de futuras adaptações para hardware físico.

A implementação foi organizada de forma que o modelo neural e o protocolo experimental não dependam diretamente dos detalhes internos do robô simulado. Essa separação favorece a reutilização do núcleo do sistema, embora uma implementação física ainda exija um adaptador específico para os sensores, motores, unidades de medida e restrições temporais do hardware escolhido.

A biblioteca de mundos, objetos e exemplos disponibilizada pelo Webots também foi um fator relevante para a escolha, pois forneceu referências para a construção inicial dos ambientes, das juntas, dos sensores e dos controladores utilizados no projeto.

### [preservar] Desenvolvimento

O projeto foi desenvolvido com ferramentas abertas e organizado para favorecer a reprodução dos experimentos. O Webots é utilizado para a simulação física, enquanto Python implementa a rede neural, o protocolo experimental, a integração com o controlador e a geração dos artefatos de cada execução. As dependências são declaradas no pyproject.toml e consolidadas pelo uv, com alternativas para pip e Conda.

- Webots R2025a;

- Python 3.13;

- uv como ambiente recomendado;

- módulos separados para rede, protocolo experimental e adaptador;

- notebook de validação;

- testes automatizados;

- JSONL e metadados por execução;

- relatório HTML derivado;

- controle de versão.

#### [preservar] Estado ao final da Fase 2

Ao final da Fase 2, o ambiente físico, o robô, a instrumentação e a rede neural encontram-se integrados no modo `LEARNING`. Cada ação neural é mantida durante uma janela temporal, após a qual o deslocamento e a aceleração são agregados. O movimento é então classificado, a maraca é produzida quando ocorre descida e os estímulos resultantes alimentam o passo neural seguinte.

O fluxo experimental completo já produz telemetria, registros por iteração, metadados, resumos e relatórios HTML. Os testes automatizados validam os componentes de software, e as execuções exploratórias demonstram que o robô consegue completar o percurso. Esses resultados confirmam a integração do sistema, mas ainda não permitem atribuir o comportamento observado à plasticidade neural.

### [atualizar] Próximos passos

#### [atualizar] Modelagem da rede neural

A próxima etapa é a modelagem da rede neural, que está nas camadas 4 e 5 do experimento. A implementação da rede neural será feita em Python, utilizando as funções de ativação e dinâmica descritas no artigo original. A rede será integrada com a interface de controle para permitir que o comportamento emergente seja observado e analisado.

#### [atualizar] Diversidade de sensores

Foi reduzida a diversidade de sensores embarcados no primeiro aprendizado para somente aproximação da chegada (é possível ver a "chegada" nos vídeos do plano inclinado) no entanto, o Webots suporta todos os itens de estímulo do artigo, como estímulos visuais e auditivos, e eles serão integrados na fase 5 do experimento após a validação do comportamento emergente com o sensor de aproximação.

#### [atualizar] Modelo físico

Foi escolha de projeto simular em ambiente virtual para a montagem e testagem da camada de software de maneira isolada. Portanto a montagem física do robô é a última etapa do projeto, e somente será iniciada após a validação do comportamento emergente na simulação. É importante relembrar, no entanto, que todo código utilizado é reutilizável na camada de hardware, ou seja, o código de controle do robô virtual é o mesmo código de controle do robô real, e a interface de controle é a mesma para ambos os robôs, portanto, a camada de software é completamente reutilizável na camada de hardware.

## [adicionar] Arquitetura detalhada da rede

### [adicionar] Topologia e conectividade

### [adicionar] Mapeamento neural-motor

### [adicionar] Ordem temporal e fluxo causal

## [adicionar] Funções e equações

### [adicionar] Normalização e soma sensorial

### [adicionar] Ativação, saída sigmoidal e competição

### [adicionar] Plasticidade sináptica

### [adicionar] Plasticidade intrínseca

### [adicionar] Distância, deslocamento e classificação do movimento

### [adicionar] Aceleração, maraca e critérios de aprendizagem

## [adicionar] Parâmetros experimentais

### [adicionar] Parâmetros da rede neural

### [adicionar] Parâmetros do protocolo de aprendizagem

### [adicionar] Parâmetros do mundo Webots

### [adicionar] Parâmetros do robô e dos sensores

## [adicionar] Implementação e reprodutibilidade

## [adicionar] Validação automatizada

## [adicionar] Ensaios exploratórios

## [adicionar] Limitações e hipóteses operacionais

## [adicionar] Protocolo dos ensaios formais

## [atualizar] Conclusão

Apesar de desafios iniciais, principalmente no aprendizado e adaptação ao ambiente Webots, o projeto evoluiu para um estado funcional sólido de simulação com controle, mas ainda sem a rede neural integrada. A construção em camadas permitiu validar cada componente isoladamente, garantindo que o sistema como um todo esteja pronto para a integração da rede neural e a observação do comportamento emergente.

A abordagem em camadas permitiu:

- Reduzir complexidade

- Aumentar controle experimental

- Garantir reprodutibilidade

O projeto encontra-se próximo da etapa de aprendizado efetivo.

## [atualizar] Anexos

#### [atualizar] Visão geral do repositório

A imagem repositorio_visao_geral dá uma ideia da organização atual do repositório.

![repositorio visao geral](../assets/repositorio_visao_geral.png)

Imagem: repositorio_visao_geral

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
