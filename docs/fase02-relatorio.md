
# Atualização de entrega da Fase 2

O relatório a seguir consolida a evolução do projeto na segunda entrega.

A `Fase 2` compreende a correção e parametrização do mundo inclinado, a definição lógica da área da meta (onde o experimento termina), a aquisição do estímulo da aceleração e a aquisição do estímulo da maraca, a implementação **inicial** da rede plástica de quatro neurônios como uma **primeira versão** das equações envolvidas e sua integração ao modo `LEARNING` da simulação (neste ponto para validação de acoplamento à simulação somente), a telemetria experimental e a geração de artefatos a cada execução também fazem parte dessa entrega. A forma final da rede neural plástica e do protocolo de aprendizagem deverá ser assunto central da `Fase 3`.

No estado atual, a implementação de engenharia e o fluxo experimental estão concluídos mas as execuções realizadas neste ponto ainda têm caráter exploratório: demonstram o funcionamento do sistema mas não constituem um experimento controlado nem evidência suficiente para atribuir o comportamento observado à plasticidade neural.

Está nos planos a implementação na Fase 3 de um modo de disparo não supervisionado de um conjunto de simulações que permita variar determinados parâmetros e comparar o resultado do conjunto de experimentos, isso será um facilitador para estudar impacto de diferentes plasticidades neurais, mais detalhes na seção `Sugestão de experimento para a Fase 3`.

O experimento e a simulação até este ponto foram criados com reprodutibilidade ampla em mente, mais detalhes na seção `Apêndice A - Guia de reprodução`. O código integral do projeto está disponível em https://github.com/lnncrs/DomanNeurocomputationalModel

Como o relatório ficou extenso mesmo após repetidas remoções de conteúdo, e uma boa parte dele foi somente modificada do relatório 1, tomei a liberdade de marcar trechos com informação realmente nova ou de especial interesse para a entrega da `Fase 2` com <mark>MARCADOR DE TEXTO</mark>. Uma leitura rápida do relatório pode ser feita apenas com a leitura dos trechos marcados.

![logotipo-ufabc-extenso](../assets/logotipo-ufabc-extenso.png)

# Modelo neurocomputacional de reorganização motora

Lenin Cristi

CMCC - Universidade Federal do ABC (UFABC)
Santo André - SP - Brasil

lenin.cristi@aluno.ufabc.edu.br

Resumo. Este trabalho tem como objetivo a reprodução computacional e robótica do experimento Doman's Inclined Floor Method for Early Motor Organization Simulated with a Four Neurons Robot (2011) de Ropero Peláez e Lucas Santana, no qual um robô controlado por uma rede neural plástica de quatro neurônios aprende a organizar seu comportamento motor em um plano inclinado, inspirado no método de estimulação motora precoce de Glenn Doman.

## Sumário

- Resumo
- Objetivo do Projeto
- Introdução
  - O experimento original
  - A rede neural utilizada
  - Mapeamento motor
  - Sensoriamento
- Metodologia
  - Estratégia incremental de construção e validação
  - Simulação de mundo
  - Desenvolvimento
  - Estado do projeto ao final da Fase 2
  - Execução de uma simulação
  - Mapeamento detalhado dos modos de controle
- Funções e equações
  - Normalização e soma sensorial
  - Ativação, saída sigmoidal e competição
  - Plasticidade sináptica
  - Plasticidade intrínseca
  - Distância, deslocamento e classificação do movimento
  - Aceleração, maraca e critérios de aprendizagem
- Parâmetros experimentais
  - Parâmetros da rede neural
  - Parâmetros do protocolo de aprendizagem
  - Parâmetros do mundo Webots
  - Parâmetros do robô e dos sensores
- Conclusão
- Referências
- Apêndices
  - Apêndice A - Guia de reprodução
    - Requisitos de software
    - Requisitos de hardware
    - Instalação de GCC, G++ e make
    - Instalação do Git
    - Clonagem do repositório
    - Instalação do Webots
    - Ambiente Python recomendado com uv
    - Alternativa com pip
    - Alternativa com conda
    - Editor e extensões opcionais
    - Validação do ambiente
    - Lista mínima de verificação
  - Apêndice B - Estrutura do repositório
    - Arquivos de configuração na raiz
    - Código-fonte do modelo
    - Estrutura da simulação Webots
    - Documentação, exemplos e validação
    - Testes automatizados
  - Apêndice C - Evolução histórica da simulação
    - Simulação de física
    - Simulação de colisão do robô
    - Simulação de controle
  - Apêndice D - Localização e configuração dos parâmetros
    - Parâmetros da rede neural
    - Parâmetros do protocolo de aprendizagem
    - Parâmetros do mundo Webots
    - Parâmetros do robô e dos sensores

## Resumo

Este trabalho tem como objetivo a reprodução computacional e robótica do experimento *Doman's Inclined Floor Method for Early Motor Organization Simulated with a Four Neurons Robot (2011)* de Ropero Peláez e Lucas Santana, no qual um robô controlado por uma rede neural plástica de quatro neurônios aprende a organizar seu comportamento motor em um plano inclinado, inspirado no método de estimulação motora precoce de Glenn Doman.

A implementação original foi realizada utilizando *LEGO Mindstorms NXT* em *MATLAB* e dependia de sensores e estímulos relacionados à aceleração, à visão e ao som, representados respectivamente por um mecanismo de detecção de aceleração, por um sensor de luz apontado para a rampa listrada para detectar transições e por um microfone captando o som de uma maraca na meta. Este projeto desenvolve uma versão reproduzível do experimento utilizando uma linguagem multiparadigma flexível e uma arquitetura modular de sensoriamento e controle. O código integral do projeto está disponível em https://github.com/lnncrs/DomanNeurocomputationalModel

A reconstrução foi conduzida deliberadamente de forma incremental, separando a modelagem do mundo, a validação da física neste mundo, a construção do robô e sua instrumentação com sensores, a interface de controle do Webots e por fim sua integração com a rede neural.

Essa organização permitiu testar isoladamente cada componente em cada camada antes de integrá-lo ao experimento completo, reduzindo a dificuldade de identificar falhas e aumentando a reprodutibilidade do sistema. Nesta fase no entanto, foram integrados somente os estímulos de aceleração e som, enquanto o canal visual permanece previsto, mas desativado.

<mark>
Foram criados ambientes de simulação do Webots versionados em `webots\worlds`, sendo o principal deles o `webots\worlds\experiment_inclined_plane.wbt` já integrado a uma primeira tentativa de rede neural recorrente e plástica de quatro neurônios. Este ambiente simula o plano inclinado, a meta, o robô e os estímulos de aceleração e som, permitindo a execução de experimentos controlados:
</mark>
<br/><br/>

![experiment with robot](../assets/experiment.png)

Imagem: Simulador pronto para o experimento

<mark>
Esta simulação conta também com tela de acompanhamento do experimento com telemetria detalhada dos sensores, experimento, controle e motor, o estímulo de uma maraca sintética que premia deslocamento para a meta inspirada no artigo é visível e o registro detalhado das execuções é salvo:
</mark>
<br/><br/>

![experiment with robot](../assets/experiment_telemetry.png)

Imagem: Tela de acompanhamento da telemetria do robô

## Objetivo do Projeto

Os objetivos centrais do experimento original são:

- Simular condições de aprendizado motor infantil;

- Observar o surgimento de comportamento emergente;

- Analisar, a partir desse comportamento, possíveis paralelos com processos de neuroplasticidade.

> **Nota:** Neste ponto entendemos que a simulação, o robô e mesmo o aprendizado são tratados como meios e não como objetivos fim.

## Introdução

### O experimento original

Antes da construção do projeto, foi imprescindível realizar uma leitura detalhada do artigo que descreve o experimento original *Doman's Inclined Floor Method for Early Motor Organization Simulated with a Four Neurons Robot (2011)*, também disponível no repositório em `docs\Testing the inclined plane technique with a four neurons robot.pdf`.

Essa leitura revelou um ponto fundamental sobre o experimento: o objetivo do experimento não era simplesmente fazer o robô aprender a se locomover, mas sim utilizar uma arquitetura robótica e neural simples para investigar como estímulos sensoriais e determinados mecanismos de plasticidade poderiam contribuir para a organização inicial do comportamento motor.

O experimento procura reproduzir, de maneira simplificada, alguns elementos presentes no método do plano inclinado de Doman:

- aceleração produzida durante o movimento sobre o plano inclinado, como analogia ao estímulo vestibular;

- transições visuais geradas pelas faixas pretas e brancas da rampa;

- estímulo sonoro produzido por uma maraca após movimentos descendentes em direção a meta;

- ambiente físico formado pelo plano inclinado;

- sistema neural simples, composto por quatro neurônios plásticos interconectados.

Inicialmente, o robô não possui uma direção preferencial. Quando uma sequência de comandos motores produz um movimento descendente, a ação da gravidade resulta em maior aceleração e em transições mais rápidas entre as faixas visuais da rampa. Além disso, o movimento descendente é seguido pelo estímulo sonoro da maraca. Esses estímulos influenciam os mecanismos de plasticidade sináptica e intrínseca, favorecendo a formação de sequências neurais associadas ao deslocamento sobre a rampa. No artigo, considera-se que o robô aprendeu quando executa movimentos na mesma direção durante cinco iterações consecutivas.

O modelo não pretende reproduzir integralmente o sistema nervoso infantil ou demonstrar diretamente como uma criança aprende a se locomover. Ele constitui uma analogia computacional controlada, utilizada para observar a relação entre estímulos sensoriais, plasticidade e organização motora e, a partir dela, formular hipóteses sobre processos envolvidos na aquisição inicial do movimento.

Assim, o aprendizado do robô não constitui o objetivo final do experimento, mas um meio para investigar, em um sistema simplificado e controlável, como estímulos sensoriais e mecanismos de plasticidade podem participar da organização do comportamento motor.

### A rede neural utilizada

<mark>
O artigo descreve uma rede totalmente interconectada composta por quatro unidades neuronais excitatórias do tipo rate-code. Cada neurônio recebe a soma dos estímulos sensoriais e sinais provenientes da atividade anterior dos demais neurônios e de sua própria conexão recorrente. Um mecanismo de competição mantém ativo apenas o neurônio mais ativado (maior saída sigmoidal) em cada iteração.
</mark>
<br/><br/>

> **Nota:** A implementação apresentada aqui é uma primeira tentativa de reproduzir a apresentada no artigo, assim como leituras subsequentes do artigo levaram a correção do mecanismo de locomoção de diferencial para por eixos, a rede será revista.

A arquitetura possui quatro conexões recorrentes, cada uma ligando um neurônio a si mesmo, cujos pesos são mantidos fixos em *0,7*. As doze conexões entre neurônios diferentes possuem pesos modificáveis ou *plásticos*.

| **Recebe de / Saída de** | **N1** | **N2** | **N3** | **N4** |
| ------------------------ | -----: | -----: | -----: | -----: |
| **N1**                   |    0,7 |    w₁₂ |    w₁₃ |    w₁₄ |
| **N2**                   |    w₂₁ |    0,7 |    w₂₃ |    w₂₄ |
| **N3**                   |    w₃₁ |    w₃₂ |    0,7 |    w₃₄ |
| **N4**                   |    w₄₁ |    w₄₂ |    w₄₃ |    0,7 |

Tabela: Conexões neuronais na rede

Sendo:
- $w_{12}$: conexão de **N2 para N1**
- $w_{21}$: conexão de **N1 para N2**
- Os valores `0,7` na diagonal representam as conexões autorrecorrentes fixas.

<mark>
O aprendizado ocorre de forma incremental a cada iteração por meio de dois mecanismos complementares: plasticidade sináptica, que altera os pesos entre os neurônios, e plasticidade intrínseca, que desloca a função de ativação de cada unidade de acordo com seu histórico de atividade.
</mark>
<br/><br/>

Esses neurônios continuam sendo modelos artificiais, mas diferem daqueles empregados em muitas redes neurais convencionais: Não há camadas profundas, função de perda, dados rotulados ou retropropagação de erro.

A adaptação ocorre a partir do retorno sensorial produzido pelas consequências das ações do robô, que modula a atividade neuronal e, indiretamente, as alterações sinápticas.

A pequena quantidade de neurônios torna possível acompanhar diretamente os pesos, as ativações, os neurônios vencedores e as sequências motoras produzidas. Essa interpretabilidade é uma propriedade útil da arquitetura, embora o artigo não afirme explicitamente que a escolha de quatro neurônios tenha sido determinada exclusivamente por esse objetivo.

O modelo não pretende reproduzir toda a complexidade de um sistema neural biológico. Ele representa uma estrutura computacional simplificada, utilizada para investigar como plasticidade, competição e feedback sensorial podem contribuir para a organização progressiva do comportamento motor.

> **Nota:** Numa primeira visita a aula *Modelagem de redes bioinspiradas. Prof. Javier Ropero Peláez (UFABC)* disponível em https://www.youtube.com/watch?v=j9ElSxpLWzw acredito que este modelo pode ser considerado fenomenológico (porque não modelamos detalhadamente canais ionicos, potenciais, membranas etc) e frequencial pela característica de *taxa de disparo* usada

### Mapeamento motor

<!-- todo isto não está claro
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
-->

<mark>
No robô virtual, cada roda possui um motor independente. Para preservar a organização funcional do experimento original, o adaptador do modo `LEARNING` agrupa esses motores em conjuntos frontal e traseiro. Cada neurônio corresponde assim a uma primitiva motora e a competição mantém apenas um neurônio ativo por iteração, o modelo neural conhece apenas as ações abstratas e a conversão para os quatro motores do robô é feita por um adaptador.
</mark>
<br/><br/>

| Neurônio | Primitiva motora |
|---|---|
| N1 | conjunto frontal, sentido horário |
| N2 | conjunto frontal, sentido anti-horário |
| N3 | conjunto traseiro, sentido horário |
| N4 | conjunto traseiro, sentido anti-horário |

Tabela: Tradução das ações abstratas em primitivas motoras

![experiment with robot](../assets/robot_axes.png)

Imagem: *Closeup* no robô onde se vêem os dois eixos frontal / traseiro em perspectiva

> **Nota sobre a implementação atual:** O retorno de **aceleração** é calculado a partir da variação da aceleração longitudinal medida durante cada janela motora. O retorno do estímulo sonoro da **maraca** é produzido sinteticamente quando existe redução da distância até a área retangular da meta e ela é suficiente para que o movimento seja classificado como descendente. Portanto, a implementação atual não utiliza um par físico de microfone e alto-falante e o canal visual de detecção de listras permanece não implementado nesta etapa. Esses mecanismos serão detalhados nas seções de funções, equações e protocolo experimental.

> **Nota histórica:** Nas primeiras versões da simulação, o mapeamento `neuronios → movimento` foi interpretado incorretamente como uma configuração diferencial entre os lados esquerdo e direito. A releitura do artigo levou à correção do modo `LEARNING` para a organização `neuronios → movimento` para os eixos frontal/traseiro em sentido horário e anti-horário. Os modos manual de controle `MANUAL` e automático anti colisão `AUTOMATIC` continuam utilizando controle diferencial e não foram afetados por essa mudança.

### Sensoriamento

<mark>
O robô usado como base é do tutorial do Webots preservado em `webots\tutorials\4_wheels_robot.wbt`, ele foi adaptado e ganhou 4 sensores de proximidade externos adicionais em cada direção, teve mantido os sensores de proximidade frontais diagonais originais e recebeu os seguintes sensores adicionais não visíveis:
</mark>
<br/><br/>

- Acelerômetro
- Giroscópio
- GPS
- Bússola

![experiment with robot](../assets/robot_sensors.png)

Imagem: *Closeup* no robô onde se vêem os sensores de proximidade originais e adicionais (somente estes são visíveis)

## Metodologia

A reconstrução do experimento envolve componentes interdependentes:

- o ambiente inclinado;
- a dinâmica física;
- a estrutura do robô;
- os sensores embarcados;
- os estímulos externos;
- o controle motor;
- a rede neural.

Alterações nestes elementos podem modificar o comportamento observado e, consequentemente, dificultar a identificação da origem de falhas. No experimento original, a estrutura robótica foi construída com *LEGO Mindstorms NXT*, enquanto a rede neural e os comandos sensório-motores foram implementados em *MATLAB* por meio da *RWTH Mindstorms NXT Toolbox*. A reprodução direta dessa estrutura em uma nova plataforma física exigiria que problemas mecânicos, eletrônicos, sensoriais e computacionais fossem tratados simultaneamente.

### Estratégia incremental de construção e validação

Para reduzir a chance de falha não identificada ou não rastreável, foi adotada uma estratégia incremental em camadas. Cada componente é construído e validado de forma isolada e, posteriormente, integrado aos demais. Essa abordagem permite distinguir problemas relacionados ao ambiente, à física, ao robô, ao controle e ao modelo neural.

A simulação foi utilizada como ambiente inicial de desenvolvimento porque permite:

- controlar as condições experimentais;
- repetir ensaios sob configurações equivalentes;
- observar diretamente posições, velocidades, acelerações e comandos motores;
- testar componentes isoladamente;
- reduzir o custo de alterações mecânicas;
- registrar de forma sistemática as variáveis de cada execução.

A construção de um robô físico foi mantida como uma etapa posterior à validação do comportamento no ambiente simulado. O núcleo neural e o protocolo experimental foram separados da interface do simulador para favorecer sua reutilização futura.

> **Nota:** Por mais que a estrutura em camadas favoreça o reuso de código, uma implementação física ainda exigirá um adaptador específico para os sensores, motores, unidades de medida e restrições temporais da plataforma escolhida.

<mark>
Para evitar confusão com as fases de entrega e documentação do projeto, os cinco blocos de desenvolvimento são tratados neste relatório como etapas técnicas de implementação.
</mark>
<br/><br/>

| Etapa | Escopo | Estado ao final da Fase 2 |
|---|---|---|
| 1 - Ambiente | Construção dos planos inclinado e horizontal e validação de sua geometria | concluída |
| 2 - Física | Testes de gravidade, colisão, contato com a rampa e comportamento de sólidos | concluída |
| 3 - Robô | Modelagem do corpo, das rodas, dos motores, das juntas e dos sensores | concluída |
| 4 - Controle e instrumentação | Implementação dos modos de controle `MANUAL` e `AUTOMATIC`, telemetria e aquisição das variáveis experimentais | concluída |
| 5 - Integração neural | Implementação da rede inicial de quatro neurônios e integração ao modo `LEARNING` | integração concluída validação pendente |

Tabela: Completude técnica do projeto

> **Nota:** Na etapa técnica 4, foi necessário implementar dois modos adicionais de controle não previstos: `PASSIVE_FREE` e `PASSIVE_REALISTIC`. No primeiro, o torque disponível dos motores é desativado, deixando as rodas livres. No segundo, o torque disponível é limitado a 0,03 N·m por roda, representando uma pequena resistência dos motores. Esses modos foram imprescindíveis para testar o deslizamento e a influência da gravidade sobre o robô nos planos inclinados.

A conclusão de uma etapa técnica indica que seus componentes essenciais estão implementados e funcionalmente integrados.

### Simulação de mundo

Para a simulação, foi realizada uma pesquisa na qual foram considerados dois ambientes principais: *Webots* e *PyBullet*. O Webots foi escolhido por oferecer maior capacidade de representar motores, atuadores e sensores de maneira próxima a uma implementação física, dentro de um ambiente integrado de simulação. A plataforma também oferece suporte a controladores em Python, C e C++, além de uma biblioteca de mundos e componentes reutilizáveis.

Os principais motivos para a escolha do Webots foram:

- modelagem integrada de sensores, motores e atuadores;
- suporte a controladores em Python, C e C++;
- simulação da interação entre corpos, juntas e superfícies;
- biblioteca de mundos e componentes reutilizáveis;
- proximidade conceitual com uma futura implementação física.

Um ponto importante do Webots é permitir o desenvolvimento inicial dos controladores em Python, oferecendo maior flexibilidade para a implementação e validação do modelo neural. A plataforma também suporta controladores em C e C++, o que amplia as possibilidades de integração com outras plataformas e de futuras adaptações para hardware físico.

<mark>
A implementação foi organizada de forma que o modelo neural e o protocolo experimental não dependam diretamente dos detalhes internos do robô simulado. Essa separação favorece a reutilização do núcleo do sistema, embora uma implementação física ainda exija um adaptador específico para os sensores, motores, unidades de medida e restrições temporais do hardware escolhido.
</mark>
<br/><br/>

![experiment with robot](../assets/normal_plane.png)

Imagem: Plano *half-size* não inclinado utilizado em testes

A biblioteca de mundos, objetos e exemplos disponibilizada pelo Webots parcialmente preservada em `webots\tutorials` também foi um fator relevante para a escolha, pois forneceu referências para a construção inicial dos ambientes, das juntas, dos sensores e dos controladores utilizados no projeto.

### Desenvolvimento

O projeto foi desenvolvido com ferramentas abertas e organizado para favorecer a reprodução dos experimentos.

O Webots é utilizado para a simulação física, enquanto Python implementa a rede neural, a integração com o controlador e a geração dos artefatos de cada execução. As dependências de sistema como o *gcc* e o *make* bem como dependências Python estão integralmente mapeadas no apêndice.

Uma listagem preliminar do *software* utilizado é a que segue:

- Plataformas *Windows* e *Linux* suportadas com instruções disponíveis para ambas pois a reprodução dos experimentos é agnóstica a sistema operacional.

- Ferramentas *Git* para clonar e operar o repositório de projeto;

- O *Webots R2025a* para rodar as simulações;

- Compilador *gcc* com *make* e *sh* disponíveis pois é utilizado pelo *Webots R2025a* quando da criação das bibliotecas de *controllers* e *plugins*;

- Ambiente *uv* recomendado, mas pode-se usar *pip* ou *conda*;

- Python 3.13 fornecido pelo ambiente de escolha acima;

- Uma validação da rede com dados sintéticos usa um notebook *Jupyter*, adicionalmente *numpy*, *pandas* e *matplotlib* são recomendados;

- Os testes automatizados usam *pytest*;

### Estado do projeto ao final da Fase 2

<mark>
Ao final da Fase 2, o ambiente físico, o robô, a instrumentação e a primeira rede neural encontram-se integrados no modo `LEARNING`. A rede neural executa um deslocamento que é classificado como "desceu ou não" em direção a meta e, em caso positivo, a "maraca virtual" é ativada e combinada ao estímulo do acelerômetro que alimentam o passo neural seguinte.
</mark>
<br/><br/>

<mark>
O fluxo experimental completo já produz telemetria, registros por iteração, metadados, resumos e relatórios HTML. Os testes automatizados validam os componentes de software, e as execuções exploratórias demonstram que o robô consegue completar o percurso.
</mark>
<br/><br/>

<mark>
Esses resultados confirmam a integração do sistema somente, ainda não é possivel atribuir o comportamento observado (de fato o carrinho desce a rampa) à plasticidade neural, a rampa do artigo é deliberadamente e levemente escorregadia, e isso foi reproduzido fielmente no ambiente simulado. Portanto, é necessário simular diferentes aderências da rampa para excluir o deslizamento como causa chave da descida. Em outras palavras, a ativação da maraca confirma que a ação foi classificada como descendente pelo protocolo, entretanto, ela não constitui evidência de aprendizagem, pois é produzida deterministicamente a partir dessa mesma classificação.
</mark>
<br/><br/>

Uma lista com capacidades chave do projeto funcionais nesta fase é a que segue:

- Mapas webots foram criados em separado dos artefatos de robô, que por sua vez tem sensoriamento embarcado independente do mapa, isso pode permitir reutilizacao do robô e da rede gerada em diferentes mapas, e no futuro medição da robustez do treinamento por exemplo, treinando num mapa e testando num outro;
- Area de meta criada em verde para fácil identificacao (essa cor é usada no projeto só na meta), desacoplada e parametrizada para facilitar o reuso em diferentes mapas;
- Robô com suporte a diferentes modos e controle incluindo modo manual por *joystick*;
- Variaveis de simulacao e experimento identificadas;
- Tela interativa de acompanhamento da simulacao com telemetria e dados de treinamento em tempo real;
- Geração de metadados e logs do experimento em JSONL acompanhados de um relatório HTML com detalhes da rede gerada;

> **Nota:** Existe duplicidade na entrega do parâmetro da meta e do controlador, pois os dois tem de receber a localização da meta, será removida no futuro

> **Nota:** As variáveis e parâmetros do experimento estão mapeadas mas não centralizadas, elas serão centralizadas e completamente desacopladas (possivelmente em locais distintos) no futuro

### Sugestão de experimento para a Fase 3

<mark>
Uma sugestão de conjunto de experimentos para a Fase 3 é a que segue:
</mark>
<br/><br/>

| Condição                 | Plasticidade sináptica | Plasticidade intrínseca | Estímulos        |
| ------------------------ | ---------------------: | ----------------------: | ---------------- |
| Rede completa            |                 ligada |                  ligada | aceleração + som |
| Sem plasticidade         |              desligada |               desligada | aceleração + som |
| Apenas sináptica         |                 ligada |               desligada | aceleração + som |
| Apenas intrínseca        |              desligada |                  ligada | aceleração + som |
| Sem som                  |                 ligada |                  ligada | aceleração       |
| Controle motor aleatório |          não aplicável |           não aplicável | —                |
| Deslizamento passivo     |       motores passivos |           não aplicável | —                |

<mark>
Para cada condição:
</mark>
<br/><br/>

- várias seeds;
- mesma posição inicial ou conjunto controlado de posições;
- mesma orientação inicial;
- mesma condição de atrito;
- limite máximo de iterações;
- número de chegadas à meta;
- iterações até critério;
- proporção de descidas;
- tempo até a meta;
- evolução dos pesos;
- evolução dos shifts.

<mark>
Dúvida: A rede com plasticidade apresenta desempenho significativamente diferente da rede sem plasticidade e dos controles passivos/aleatórios?
</mark>
<br/><br/>

> **Nota:** O conjunto de experimentos e dúvida acima é apenas uma sugestão, a definição final do protocolo experimental será discutida com o orientador na Fase 3.

### Uso de ferramentas de inteligência artificial

<mark>
Durante a Fase 2 foram utilizadas ferramentas de inteligência artificial como apoio à implementação, refatoração e documentação.
</mark>
<br/><br/>

<mark>
O nível de participação dessas ferramentas não foi uniforme entre os componentes do projeto, e foi selecionado como critério de uso a natureza do componente e a necessidade de compreensão científica do mesmo. A tabela a seguir resume a participação da IA em cada categoria de componente:
</mark>
<br/><br/>

<!--
| Categoria | Exemplos | Exigência de domínio | Uso |
|---|---|---|---|
| Simulação Webots Fase 1 | Mapas, artefatos  | Baseado nos tutoriais | -
| Simulação Webots Fase 2 | Mapas, artefatos  | Baseado nos exemplos válidos no repositório | Assistido
| Relatório | Relatório, atualização e README  | Inteiramente baseado no relatório anterior com revisão assistida | Revisão
| Núcleo científico | equações, estímulos, plasticidade, competição e critério de aprendizagem | Manual com assistência, com revisão integral de formulas extraídas do artigo e da aula fornecida quando aplicável | Assistido
| Integração experimental | Webots, sensores, motores, cálculo de deslocamento e runtime | Manual com assistência, com adaptações assistidas declaradas | Assistido
| Plugin de telemetria | Janela de telemetria | Assistido por IA com adaptações funcionais e resultado conferido | Médio
| Artefatos auxiliares | Log e relatório de experimentos, coleta de telemetria | Geração por IA com revisão arquivo a arquivo e resultado conferido | Alto
| Verificação | testes automatizados | Geração por IA com revisão arquivo a arquivo e resultado conferido | Alto
-->

| Categoria | Exemplos | Uso da ferramenta | Validação realizada |
|---|---|---|---|
| Mundo e robô no Webots (Fase 1) | Mapas, artefatos  | - | - |
| Mundo e robô no Webots (Fase 2) | Mapas, artefatos  | Apoio pontual à edição | Inspeção visual e testes físicos no simulador |
| Texto | Relatório, documentação e README  | Revisão linguística e estrutural | Revisão integral pelo autor |
| Núcleo neural inicial (Fase 2) | equações, estímulos, plasticidade, competição e critério de aprendizagem | Apoio à implementação e revisão | Comparação das equações com o artigo, inspeção ou refatoração do código |
| Integração experimental | Webots, sensores, motores, cálculo de deslocamento e runtime | Apoio à implementação e refatoração | Testes de sensores, motores, telemetria, dirigibilidade, física da simulação |
| Plugin de telemetria | Janela de telemetria | Maior apoio na geração inicial | Revisão do código e conferência dos arquivos produzidos |
| Artefatos auxiliares | Log e relatório de experimentos, coleta de telemetria, testes unitários | Maior apoio na geração inicial | Revisão do código e conferência dos arquivos produzidos |

<mark>
O "Núcleo neural inicial" e a "Integração experimental" estão em processo de reescrita buscando melhor didática, organização mais simples de classes e métodos, diminuição de verbosidade e buscando aproximar o código da base científica adotada no artigo e na aula. Na Fase 2 o objetivo foi viabilizar o experimento com coleta de métricas, a reconstrução fina e evolução da arquitetura da rede plástica devem ser assuntos centrais da Fase 3.
</mark>
<br/><br/>

> **Nota:** Não obstante, mesmo os componentes com maior participação assistida podem ser reescritos ou suprimidos, isso será objeto de discussão com o orientador para a Fase 3, quando da implementação do experimento formal em hardware (o que pode exigir reescrita da rede em C ou C++) e o foco passar a ser a análise dos resultados. Ressaltando que as ferramentas não foram utilizadas como fonte científica.

#### Curiosidade breve sobre contexto

Os mundos iniciais do Webots e os protótipos desenvolvidos durante a Fase 1 tiveram de ser integralmente construídos manualmente, a partir da exploração dos tutoriais, montagem progressiva dos objetos e testes de colisão, física e elasticidade realizados no simulador.

Isso ocorreu porque os modelos de linguagem (LLMs) curiosamente (ou especificamente por serem *decoders* baseados na arquitetura *Transformers*) não tinham ou não têm qualquer capacidade de raciocínio espacial, mesmo em tarefas simples como gerar ou unir dois cubos num plano, adicionar uma junta de rotação a um cubo ou mesmo incluir uma superfície com colisão a um plano.

Foram necessárias várias visitas à documentação para sistemas simples como juntas e juntas de rotação. Isso é perceptível na extensa biblioteca legada de mundos preservadas com propósito de referência e histórico.

Os controles iniciais do Webots em C, C++ e Python igualmente tiveram de ser adaptados diretamente dos tutoriais fornecidos com montagem progressiva dos objetos e de testes realizados no simulador.

Já na Fase 2, as mesmas ferramentas assistivas foram capazes de fazer ajustes finos nestes elementos, como por exemplo unir superficies levemente desniveladas, adicionar sensores e alterar parâmetros de física, acredito que o contexto gerado pelos arquivos Webots e Proto válidos no repositório fez com que a assistência de IA fosse capaz de fazer estes ajustes não possíveis para ela na Fase 1.

![experiment with robot](../assets/experiment_llm.png)

Imagem: Exemplo de ajuste fino na simulação que antes era impossível para a LLM, deixado deliberadamente incompleto na simulação para ser usado aqui como exemplo

### Execução de uma simulação

> **Nota:** É necessário montar o ambiente de desenvolvimento como descrito no apendice *Guia de reprodução* antes de iniciar a simulação

<mark>
A seguir é descrito como iniciar uma simulação e interagir com o ambiente.
</mark>
<br/><br/>

<mark>
Após validar o ambiente de simulação:
</mark>
<br/><br/>

1. Conecte o controle compatível.

2. Inicie o Webots a partir do terminal associado ao ambiente Python configurado para a simulação.

![experiment with robot](../assets/webots.png)

Imagem: Icone do webots na bandeja do sistema

3. Abra o mundo `webots/worlds/experiment_inclined_plane.wbt`.

4. Inicie ou reinicie a simulação no botão "play".

5. Abra a janela de telemetria do experimento clicando com o botão direito do mouse sobre o item "InclinedFourWheelRobot" e depois em "Show Robot Window"

![experiment with robot](../assets/telemetry_open.png)

Imagem: Localização do comando de abertura da janela de telemetria

6. Observe a abertura de uma janela no browser como esta:

![experiment with robot](../assets/telemetry_control.png)

Imagem: Topo da janela de telemetria

> **Nota:** O mundo integrado inicia em `PASSIVE_REALISTIC`, conforme seus `controllerArgs` portanto, apenas iniciar a simulação não ativa automaticamente o aprendizado. Na implementação atual, a seleção de `LEARNING` é feita pelo controle.

6. Pressione o botão do modo desejado no controle (exemplo: **A** para `AUTOMATIC`, **B** para `MANUAL`, **Y** para `LEARNING`).

![experiment with robot](../assets/robot_control.png)

Imagem: Diagrama do mapeamento dos botões para o *joystick* modelo Xbox One S

> **Nota:** A matriz de mapeamento é aberta para adaptar outros controles e existe retorno dos botoes pressionados no console do Webots o que facilita portar para outros controles, será adicionado suporte a teclado no futuro

8. Acompanhe no console e na telemetria a ação selecionada, estado do experimento, sensores de proximidade, motores e sensores internos.

![experiment with robot](../assets/telemetry_experiment.png)

Imagem: Sessão da telemetria correspondente ao estado do experimento

9. Somente no modo `LEARNING`: Cada simulação de aprendizagem gera um diretório dentro de `experiments/runs`:

```text
experiments/runs/learning_{timestamp_UTC}_{seed}/
```

Esse diretório contém:

- `metadata.json`, com a configuração neural, experimental e de runtime;

- `iterations.jsonl`, com um registro estruturado para cada iteração;

- `summary.json`, com o resultado consolidado da execução;

- `report.html`, com a visualização derivada dos registros.

Os arquivos de uma rodada devem permanecer juntos, pois o relatório HTML e o resumo são derivados dos mesmos metadados e registros por iteração.


![experiment with robot](../assets/report_summary.png)

Imagem: Topo do relatório HTML gerado numa rodada

![experiment with robot](../assets/report_neural.png)

Imagem: Sessão do relatório com o esboço da rede gerada

> **Nota:** Assim como a rede o relatório neste ponto do desenvolvimento é fornecido como funcionalidade em beta

### Mapeamento detalhado dos modos de controle

| Modo | Acionamento no joystick | Descrição |
|---|---|---|
| `AUTOMATIC` | botão **A**, ao completar o ciclo dos modos passivos; ou botão **START**, ao sair da parada de emergência | Executa o controle automático de desvio de obstáculos. Utiliza os sensores de proximidade e controle diferencial das rodas. Também é o modo inicial quando nenhum modo é informado nos argumentos do controlador. |
| `MANUAL` | botão **B** | Permite conduzir o robô manualmente pelo direcional digital (*D-pad*). Ao soltar o direcional, as rodas recebem velocidade zero. |
| `PASSIVE_FREE` | botão **A**, a partir de `AUTOMATIC` | Desativa o torque disponível dos quatro motores, deixando as rodas livres para os testes de deslizamento e ação da gravidade. |
| `PASSIVE_REALISTIC` | botão **A**, a partir de `PASSIVE_FREE` | Mantém as rodas sem comando de movimento, mas limita o torque disponível a `0,03 N·m` por roda, representando uma pequena resistência dos motores. |
| `LEARNING` | botão **Y** | Ativa o protocolo experimental controlado pela rede neural. Cada neurônio vencedor seleciona uma das quatro primitivas motoras, enquanto sensores, estímulos, plasticidade e telemetria são atualizados a cada janela de ação. |
| `EMERGENCY_STOP` | botão **X** | Interrompe imediatamente os comandos motores e mantém todas as velocidades em zero. Enquanto esse modo estiver ativo, os demais botões de seleção são ignorados. |

Tabela: Modos de controle do robô

O botão **A** percorre ciclicamente os modos:

```text
AUTOMATIC
→ PASSIVE_FREE
→ PASSIVE_REALISTIC
→ AUTOMATIC
```

## Funções e equações

<mark>
A implementação atual utiliza uma primeira versão das equações de ativação, competição e plasticidade descritas no artigo de referência. A apresentação formal, a justificativa dos parâmetros, a análise detalhada dessas equações e seus localizadores finais no código (elas serão derivadas em métodos próprios para facilitar inspeção) serão desenvolvidas na Fase 3, após revisão conceitual e validação sistemática da implementação.
</mark>
<br/><br/>

| Função ou equação | Finalidade | Origem |
|---|---|---|
| normalização e soma sensorial | transformar e combinar aceleração, visão e som | soma sensorial descrita no artigo; normalização aplicada |
| ativação, saída sigmoidal e competição | calcular a atividade e selecionar o neurônio vencedor | sigmoide correspondente à equação 3 do artigo; ativação e competição adaptadas |
| plasticidade sináptica | atualizar os pesos entre neurônios diferentes | equação 2 do artigo |
| plasticidade intrínseca | atualizar o deslocamento da função sigmoidal | equação 4 do artigo |
| distância, deslocamento e classificação | medir a aproximação à meta e classificar o movimento | não apresentada como equação no artigo, mas imediata |
| aceleração, maraca e critérios | agregar o estímulo, produzir o estímulo e registrar aprendizagem | critério descrito no artigo; agregação e critério adicional adaptados |

> **Nota:** Com uma implementação inicial das equações definidas, a complexidade de adaptá-las é consideravelmente menor

<!--
### Normalização e soma sensorial

Os três canais sensoriais são representados por aceleração, visão e som. Antes de serem apresentados à rede, seus valores passam por uma transformação de normalização independente, composta pela correção de um valor de referência e pela aplicação de um fator de escala:

$$
\widetilde{x}_k(t) =
\left(x_k(t)-o_k\right)s_k,
\qquad k \in \{a,v,s\}
$$

Onde:

- $t$: iteração do protocolo experimental;
- $k$: canal sensorial considerado;
- $a$, $v$ e $s$: aceleração, visão e som, respectivamente;
- $x_k(t)$: valor do canal $k$ recebido pelo normalizador na iteração $t$;
- $o_k$: deslocamento ou *offset* aplicado ao canal $k$;
- $s_k$: fator de escala do canal $k$;
- $\widetilde{x}_k(t)$: valor do canal após a normalização.

Cada entrada sensorial pode ter seu ponto de referência corrigido e sua intensidade ajustada antes de ser apresentada à rede, ou seja:

> **Esta equação quer dizer:** Pegue o valor recebido de um sensor, subtraia um valor de referência e multiplique o resultado por um fator de escala.

> **Localizador no código:** `src/neural/four_neuron_network.py` - `SensoryNormalization.normalize`.

Os valores normalizados são somados e formam uma entrada sensorial comum aos quatro neurônios:

$$
S(t)
=
\sum_{k \in \{a,v,s\}}\widetilde{x}_k(t)
=
\widetilde{x}_a(t)
+
\widetilde{x}_v(t)
+
\widetilde{x}_s(t)
$$

Onde:

- $S(t)$: entrada sensorial total apresentada a cada neurônio na iteração $t$;
- $\widetilde{x}_a(t)$: aceleração longitudinal agregada e normalizada;
- $\widetilde{x}_v(t)$: entrada visual normalizada;
- $\widetilde{x}_s(t)$: intensidade normalizada do estímulo da maraca.

> **Esta equação quer dizer:** entrada total = aceleração transformada + visão transformada + som transformado

> **Localizador no código:** `src/neural/four_neuron_network.py` - `SensoryNormalization.normalize`, no cálculo de `NormalizedSensoryInput.total`.

Na configuração atual:
- Todos os *offsets* são zero e todas as escalas são `1,0`.
- O canal visual permanece desativado e recebe `0,0`.
- O canal sonoro recebe `0,1` quando a iteração anterior é classificada como descendente e `0,0` nos demais casos.

### Ativação, saída sigmoidal e competição

Após a normalização e a soma dos estímulos sensoriais, a rede calcula a ativação de cada neurônio. Essa ativação combina a entrada sensorial da iteração atual com a atividade produzida pela rede na iteração anterior:

$$
a_i(t)
=
S(t)
+
\sum_{j=1}^{4} W_{ij}(t)O_j^c(t-1)
+
\eta_i(t)
$$

Onde:

- $t$: iteração atual do protocolo;
- $i$: neurônio cuja ativação está sendo calculada;
- $j$: neurônio que envia sua saída para o neurônio $i$;
- $a_i(t)$: ativação do neurônio $i$ na iteração $t$;
- $S(t)$: soma das entradas sensoriais normalizadas;
- $W_{ij}(t)$: peso da conexão do neurônio $j$ para o neurônio $i$;
- $O_j^c(t-1)$: saída do neurônio $j$ após a competição na iteração anterior;
- $\eta_i(t)$: ruído opcional acrescentado à ativação.

> **Esta equação quer dizer:** Para calcular a ativação de um neurônio, some a entrada sensorial atual, as saídas da iteração anterior multiplicadas pelos pesos de suas conexões e um ruído opcional.

> **Localizador no código:** `src/neural/four_neuron_network.py` - `FourNeuronNetwork.step`, no cálculo de `activation`.

Como a competição mantém somente um neurônio ativo, normalmente apenas a saída do vencedor anterior contribui para o termo recorrente. Na primeira iteração, as saídas anteriores são zero e a escolha inicial depende da competição entre as saídas produzidas com esse estado inicial.

Em seguida, a ativação é transformada em uma saída limitada ao intervalo entre zero e um por meio de uma função sigmoidal, correspondente à equação 3 do artigo:

$$
O_i(t)
=
\frac{1}
{1+\exp\left[-g\left(a_i(t)-\theta_i(t)\right)\right]}
$$

Onde:

- $O_i(t)$: saída do neurônio $i$ antes da competição;
- $a_i(t)$: ativação calculada para o neurônio $i$;
- $\theta_i(t)$: deslocamento individual da sigmoide do neurônio $i$, chamado
  `shift` na implementação;
- $g$: ganho da sigmoide;
- $\exp$: função exponencial.

> **Esta equação quer dizer:** Compare a ativação do neurônio com o deslocamento de sua sigmoide e transforme essa diferença em uma saída entre zero e um. Quanto maior a ativação em relação ao deslocamento, mais próxima de um será a saída.

> **Localizador no código:** `src/neural/four_neuron_network.py` - funções `sigmoid_output` e `_stable_sigmoid`; chamada por `FourNeuronNetwork.step` no cálculo de `raw_output`.

Quando $a_i(t)=\theta_i(t)$, a saída da sigmoide é `0,5`. Na configuração atual, o ganho $g$ é `25`, valor adotado do artigo. Esse ganho torna a transição ao redor do deslocamento relativamente acentuada.

Depois do cálculo das quatro saídas, a competição seleciona o neurônio com a maior saída:

$$
w(t)=\underset{i \in \{1,2,3,4\}}{\operatorname{arg\,max}}\;O_i(t)
$$

A saída após a competição é:

$$
O_i^c(t)
=
\begin{cases}
O_i(t), & \text{se } i=w(t),\\
0, & \text{caso contrário.}
\end{cases}
$$

> **Localizador da seleção do vencedor:** `src/neural/four_neuron_network.py` - `FourNeuronNetwork._select_winner`.

> **Localizador da saída competitiva:** `src/neural/four_neuron_network.py` - `FourNeuronNetwork.step`, no cálculo de `competitive_output`.

Onde:

- $w(t)$: índice do neurônio vencedor na iteração $t$;
- $\operatorname{arg\,max}$: operação que retorna o índice do maior valor;
- $O_i^c(t)$: saída do neurônio $i$ depois da competição.

> **Estas equações querem dizer:** Compare as saídas dos quatro neurônios, escolha aquele que possui a maior saída, preserve o valor do vencedor e atribua zero aos demais.

Na configuração atual:

- a competição utiliza o modo determinístico, no qual vence a maior saída;
- empates exatos são resolvidos pelo gerador pseudoaleatório associado à seed neural;
- o desvio do ruído de ativação é `0,0` e, portanto, $\eta_i(t)=0$;
- a saída competitiva do vencedor é preservada com seu valor sigmoidal, e não substituída por `1,0`.

### Plasticidade sináptica

A plasticidade sináptica modifica os pesos das conexões entre neurônios
diferentes. A variação de cada peso segue a regra pré-sináptica de Grossberg,
apresentada como equação 2 do artigo:

$$
\Delta W_{ij}(t)
=
\varepsilon\,
O_j^c(t-1)
\left[a_i(t)-W_{ij}(t)\right]
$$

O novo peso é obtido acrescentando essa variação ao valor anterior:

$$
W_{ij}(t+1)
=
W_{ij}(t)
+
\Delta W_{ij}(t)
$$

Onde:

- $t$: iteração atual do protocolo;
- $i$: neurônio que recebe a conexão, chamado neurônio pós-sináptico;
- $j$: neurônio que envia a conexão, chamado neurônio pré-sináptico;
- $W_{ij}(t)$: peso da conexão do neurônio $j$ para o neurônio $i$;
- $\Delta W_{ij}(t)$: alteração calculada para esse peso;
- $\varepsilon$: taxa de plasticidade sináptica;
- $O_j^c(t-1)$: saída do neurônio $j$ após a competição na iteração anterior;
- $a_i(t)$: ativação atual do neurônio $i$.

> **Estas equações querem dizer:** Se o neurônio $j$ esteve ativo na iteração anterior, compare a ativação atual do neurônio $i$ com o peso da conexão de $j$ para $i$. Uma pequena fração dessa diferença é acrescentada ao peso.

> **Localizador da variação $\Delta W_{ij}$:** `src/neural/four_neuron_network.py` - função `grossberg_delta`.

> **Localizador da atualização $W_{ij}(t+1)$:** `src/neural/four_neuron_network.py` - `FourNeuronNetwork._update_synaptic_weights`.

Quando $a_i(t)$ é maior que $W_{ij}(t)$, a variação é positiva e o peso tende a
aumentar. Quando $a_i(t)$ é menor, a variação é negativa e o peso tende a
diminuir. Se $O_j^c(t-1)=0$, o neurônio pré-sináptico não contribuiu na
iteração anterior e o peso correspondente não se altera.

Na configuração atual:

- a taxa sináptica $\varepsilon$ é `0,01`;
- somente os pesos que chegam ao neurônio vencedor atual são considerados para
  atualização, comportamento denominado `winner_only`;
- como somente o vencedor anterior possui saída competitiva diferente de
  zero, no máximo uma conexão não diagonal recebe uma alteração diferente de
  zero em cada iteração;
- quando o mesmo neurônio vence duas iterações consecutivas, essa possível
  conexão seria diagonal e, portanto, permanece fixa;
- as quatro conexões diagonais não participam da regra de plasticidade e são
  reafirmadas em `0,7` após cada passo;
- não são aplicados limites adicionais aos pesos.

O uso da saída competitiva anterior como atividade pré-sináptica e a
restrição `winner_only` constituem hipóteses operacionais da reconstrução. A
implementação também oferece a alternativa `all_postsynaptic`, na qual todos
os neurônios pós-sinápticos são considerados para atualização, preservando
ainda as conexões diagonais fixas.

### Plasticidade intrínseca

A plasticidade intrínseca não modifica os pesos das conexões. Ela altera o
deslocamento individual da função sigmoidal de cada neurônio e, com isso,
modifica a quantidade de ativação necessária para que esse neurônio produza
uma saída elevada em iterações futuras.

Na configuração atual, a atualização utiliza a saída após a competição e segue
a forma operacional da equação 4 do artigo:

$$
\theta_i(t+1)
=
\frac{
\xi O_i^c(t)+\theta_i(t)
}{
1+\xi
}
$$

Onde:

- $t$: iteração atual do protocolo;
- $i$: neurônio cujo deslocamento está sendo atualizado;
- $\theta_i(t)$: deslocamento da sigmoide do neurônio $i$ antes da atualização,
  chamado `shift` na implementação;
- $\theta_i(t+1)$: deslocamento que será utilizado na próxima iteração;
- $O_i^c(t)$: saída do neurônio $i$ após a competição;
- $\xi$: taxa de plasticidade intrínseca.

> **Esta equação quer dizer:** Calcule o novo deslocamento como uma média ponderada entre o deslocamento anterior e a saída atual do neurônio. A taxa $\xi$ determina a velocidade com que o deslocamento se aproxima dessa saída.

> **Localizador no código:** `src/neural/four_neuron_network.py` - função `intrinsic_shift`; aplicada por `FourNeuronNetwork._update_intrinsic_shifts`.

Se a saída for maior que o deslocamento atual, o deslocamento aumenta. Se for
menor, o deslocamento diminui. Um deslocamento maior move a sigmoide para a
direita, fazendo o neurônio precisar de uma ativação maior para produzir a
mesma saída. Um deslocamento menor move a sigmoide para a esquerda, tornando o
neurônio mais responsivo a ativações menores.

Na configuração atual:

- o deslocamento inicial de todos os neurônios é `0,5`;
- a taxa intrínseca $\xi$ é `0,01`;
- a fonte utilizada é `post_competition`, isto é, a saída após a competição;
- somente o vencedor possui saída competitiva diferente de zero;
- os neurônios não vencedores também são atualizados: como suas saídas
  competitivas são zero, seus deslocamentos são divididos por $1+\xi$ e
  diminuem gradualmente em direção a zero.

Para o neurônio vencedor, o deslocamento se move em direção ao valor de sua
saída sigmoidal preservada pela competição. Para os demais, a redução do
deslocamento aumenta progressivamente sua capacidade de competir em iterações
posteriores. Esse mecanismo funciona como uma adaptação da excitabilidade
individual dos neurônios.

O uso da saída após a competição é uma hipótese operacional da reconstrução.
A implementação também oferece a alternativa `pre_competition`, na qual a
saída sigmoidal dos quatro neurônios é utilizada antes que os não vencedores
sejam zerados.

### Distância, deslocamento e classificação do movimento

A direção do movimento é determinada pela variação da distância entre o robô
e a meta durante uma janela motora. Como a meta ocupa uma área retangular, a
distância é calculada até a borda mais próxima desse retângulo, e não apenas
até seu centro.

Para cada eixo horizontal, calcula-se primeiro a distância até os limites da
meta:

$$
d_x
=
\max\left(
\left|x-x_g\right|-\frac{w}{2},
0
\right)
$$

$$
d_y
=
\max\left(
\left|y-y_g\right|-\frac{l}{2},
0
\right)
$$

A distância horizontal total é então:

$$
d
=
\sqrt{d_x^2+d_y^2}
$$

Onde:

- $x$ e $y$: coordenadas horizontais do robô fornecidas pelo GPS;
- $x_g$ e $y_g$: coordenadas do centro da meta;
- $w$: largura da área da meta;
- $l$: comprimento da área da meta;
- $d_x$: distância até a meta ao longo do eixo $x$;
- $d_y$: distância até a meta ao longo do eixo $y$;
- $d$: menor distância horizontal entre o robô e o retângulo da meta;
- $\max$: operação que escolhe o maior entre os valores apresentados;
- $\left|\,\right|$: valor absoluto, que desconsidera o sinal da diferença.

> **Estas equações querem dizer:** Verifique quanto o robô está fora dos limites da meta em cada direção. Se ele já estiver dentro dos limites de um eixo, a distância naquele eixo será zero. Depois, combine as duas distâncias para encontrar a menor distância horizontal até a área.

> **Localizador de $d_x$, $d_y$ e $d$:** `webots/controllers/four_wheels_manual/learning_runtime.py` - `GoalRegion.distance`.

No início e no final de cada janela motora, essa distância é registrada. Sua
variação é:

$$
\Delta d
=
d_{\mathrm{final}}
-
d_{\mathrm{inicial}}
$$

Como a aproximação da meta reduz a distância, define-se o progresso em direção
à meta como:

$$
q
=
-\Delta d
=
d_{\mathrm{inicial}}
-
d_{\mathrm{final}}
$$

Onde:

- $d_{\mathrm{inicial}}$: distância até a meta no início da janela motora;
- $d_{\mathrm{final}}$: distância até a meta no final da janela;
- $\Delta d$: variação da distância durante a janela;
- $q$: progresso orientado em direção à meta.

> **Estas equações querem dizer:** Se a distância final for menor que a inicial, o robô se aproximou da meta e $q$ será positivo. Se a distância final for maior, ele se afastou e $q$ será negativo.

> **Localizador de $\Delta d$:** `webots/controllers/four_wheels_manual/learning_runtime.py` - `LearningRuntime._begin_action_window` registra $d_{\mathrm{inicial}}$ e `LearningRuntime._finish_action_window` calcula `displacement`.

> **Localizador de $q$:** `src/experiments/experiment_runner.py` - `ExperimentRunner._classify`, onde `displacement` é orientado por `ExperimentConfig.downhill_sign`.

Para evitar que pequenas oscilações ou imprecisões numéricas sejam
classificadas como movimento, utiliza-se um limiar $\tau$:

$$
\operatorname{direção}(q)
=
\begin{cases}
\mathrm{DOWN}, & q>\tau,\\
\mathrm{UP}, & q<-\tau,\\
\mathrm{STATIONARY}, & -\tau\leq q\leq\tau.
\end{cases}
$$

Onde:

- $\tau$: deslocamento mínimo necessário para reconhecer movimento;
- `DOWN`: aproximação da meta;
- `UP`: afastamento da meta;
- `STATIONARY`: variação insuficiente para caracterizar subida ou descida.

> **Esta equação quer dizer:** Uma aproximação maior que o limiar é classificada como descida; um afastamento maior que o limiar é classificado como subida; variações menores são consideradas estacionárias.

> **Localizador no código:** `src/experiments/experiment_runner.py` - `ExperimentRunner._classify`.

Na configuração atual:

- a posição é obtida pelo GPS;
- a meta lógica mede `0,96 × 0,96 m` horizontalmente;
- o limiar $\tau$ é `0,005 m`;
- o sinal de descida é `-1`, porque o protocolo recebe originalmente
  $\Delta d=d_{\mathrm{final}}-d_{\mathrm{inicial}}$;
- `DOWN` representa aproximação da meta, que está localizada na parte inferior
  da rampa, e não uma medição direta da inclinação ou da altitude;
- a distância usada para classificar o movimento é horizontal; a coordenada
  vertical é verificada separadamente para determinar a entrada efetiva na
  região tridimensional da meta.

Neste contexto, "deslocamento" representa a variação da distância até a meta,
e não o comprimento total da trajetória percorrida pelo robô durante a janela.
Esse cálculo é uma decisão geométrica e operacional da reconstrução, pois o
artigo não publica uma equação equivalente para a classificação do movimento.

### Aceleração, maraca e critérios de aprendizagem

Ao entrar no modo `LEARNING`, o controlador registra a componente longitudinal
do acelerômetro como valor de referência. Durante cada janela motora, novas
leituras são comparadas com essa referência. A entrada de aceleração associada
à janela é a média das diferenças absolutas:

$$
A(t)
=
\frac{1}{n_t}
\sum_{r=1}^{n_t}
\left|
a_x(t,r)-a_{x,0}
\right|
$$

Onde:

- $t$: janela motora ou iteração experimental;
- $r$: índice de uma leitura realizada dentro da janela;
- $n_t$: quantidade de leituras de aceleração coletadas na janela $t$;
- $a_x(t,r)$: componente longitudinal do acelerômetro na leitura $r$;
- $a_{x,0}$: valor de referência registrado ao entrar no modo `LEARNING`;
- $A(t)$: aceleração agregada apresentada ao protocolo ao final da janela;
- $\left|\,\right|$: valor absoluto, que considera a magnitude da diferença
  sem preservar seu sinal.

> **Esta equação quer dizer:** Compare cada leitura longitudinal com uma referência, desconsidere o sinal dessas diferenças e calcule sua média durante a janela motora.

> **Localizador das diferenças absolutas:** `webots/controllers/four_wheels_manual/learning_runtime.py` - `LearningRuntime.step`.

> **Localizador da média da janela:** `webots/controllers/four_wheels_manual/learning_runtime.py` - `LearningRuntime._finish_action_window`.

Na configuração atual:

- a componente longitudinal corresponde ao primeiro valor, ou eixo $x$, do
  acelerômetro;
- as leituras são obtidas a cada passo de `64 ms` do controlador;
- a escala de normalização da aceleração é `1,0`;
- uma janela nominal dura `0,5 s`;
- uma janela parcial também é finalizada e registrada quando o robô entra na
  meta.

Depois da conclusão da janela, o movimento é classificado. Quando a direção é
`DOWN`, o protocolo produz o estímulo lógico da maraca:

$$
M(t)
=
\begin{cases}
m, & \text{se } D(t)=\mathrm{DOWN},\\
0, & \text{caso contrário.}
\end{cases}
$$

Onde:

- $D(t)$: direção atribuída ao movimento executado na janela $t$;
- $m$: intensidade configurada para a maraca;
- $M(t)$: entrada sonora produzida como consequência dessa janela.

> **Esta equação quer dizer:** Se a ação aproximou o robô da meta o suficiente
> para ser classificada como descida, produza a maraca; em qualquer outro caso,
> mantenha a entrada sonora em zero.

> **Localizador no código:** `src/experiments/experiment_runner.py` - `ExperimentRunner.complete_iteration`, no cálculo de `rewarding_sound` e de `SensoryInput.sound`.

Na configuração atual, $m=0{,}1$. O estímulo não é produzido por microfone e
alto-falante: ele é gerado logicamente pelo protocolo. A maraca é calculada
depois da observação da ação executada e participa do passo neural que
seleciona a ação seguinte. Dessa forma, ela não influencia retroativamente a
ação que a produziu.

O protocolo registra dois critérios baseados em sequências de movimentos:

$$
C_{\mathrm{artigo}}(t)
=
\left[D(t)\neq\mathrm{STATIONARY}\right]
\land
\left[n_{\mathrm{mesma}}(t)\geq 5\right]
$$

$$
C_{\mathrm{descida}}(t)
=
\left[n_{\mathrm{descida}}(t)\geq 5\right]
$$

Onde:

- $C_{\mathrm{artigo}}(t)$: critério de cinco movimentos consecutivos na mesma
  direção;
- $C_{\mathrm{descida}}(t)$: critério adicional de cinco movimentos
  consecutivos para baixo;
- $n_{\mathrm{mesma}}(t)$: quantidade de classificações consecutivas iguais à
  direção atual;
- $n_{\mathrm{descida}}(t)$: quantidade de classificações `DOWN`
  consecutivas;
- $\land$: operador lógico "e"; as duas condições precisam ser verdadeiras.

> **Estas equações querem dizer:** O primeiro critério é alcançado após cinco
> movimentos não estacionários consecutivos na mesma direção, seja subida ou
> descida. O segundo é alcançado somente após cinco descidas consecutivas.

> **Localizador dos dois critérios:** `src/experiments/experiment_runner.py` - `LearningCriterion.update`.

O primeiro critério reproduz a condição descrita no artigo. O segundo foi
adicionado para distinguir uma sequência especificamente orientada para a
meta. Ambos são registrados na telemetria e nos artefatos da execução, mas não
encerram o experimento. Na implementação atual, a execução termina quando o
robô entra na meta. A repetição de um mesmo neurônio vencedor, isoladamente,
não é considerada evidência de aprendizagem.
-->

## Parâmetros experimentais

<mark>
As tabelas seguintes registram os valores efetivamente utilizados na configuração atual. Parâmetros classificados como hipótese deverão ser avaliados nos ensaios formais.
</mark>
<br/><br/>

> **Nota:** A localização dos campos, constantes e argumentos correspondentes está documentada no **Apêndice D - Localização e configuração dos parâmetros**.

### Parâmetros da rede neural

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

Na execução integrada, somente a seed neural é exposta como argumento do
controlador. Os demais valores utilizam a configuração padrão da rede.

### Parâmetros do protocolo de aprendizagem

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

> **Nota:** O canal visual permanece desativado. O sinal negativo usado para descida decorre do cálculo `distância final - distância inicial`, pois a aproximação da meta (não necessariamente ao centro dela) reduz a distância.

### Parâmetros do mundo Webots

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

> **Nota:** A seed do mundo é independente da seed neural. O ângulo deve permanecer igual no plano e no robô. A área da meta está representada tanto no mundo quanto nos argumentos do controlador e os valores devem permanecer sincronizados. Embora a permanência esteja configurada em `0,5 s`, o runtime do modo `LEARNING` atualmente encerra a execução na entrada da área.

Gravidade, atrito e alguns parâmetros de contato permanecem herdados dos defaults do Webots.

### Parâmetros do robô e dos sensores

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

## Conclusão

<mark>
A Fase 2 inicia uma etapa importante no projeto: O mundo inclinado, o robô, os sensores, os modos de controle, a primeira versão da rede neural plástica de quatro neurônios e o protocolo de aprendizagem agora operam em conjunto no modo `LEARNING`.
</mark>
<br/><br/>

<mark>
Durante uma simulação, a rede seleciona as ações motoras, o deslocamento do robô é observado e classificado, e os estímulos de aceleração e maraca retornam como entrada para a iteração seguinte. Ao mesmo tempo, a simulação registra os parâmetros utilizados, o estado da rede, os neurônios vencedores, as ações executadas e os critérios de aprendizagem. Esses dados são preservados em artefatos estruturados e em um relatório HTML, tornando possível acompanhar o experimento e posteriormente comparar diferentes execuções.
</mark>
<br/><br/>

<mark>
As execuções exploratórias realizadas também demonstram que o fluxo completo está funcional e que o robô consegue percorrer o plano inclinado e alcançar a meta, no entanto é cedo para afirmar que o comportamento observado foi produzido especificamente pela plasticidade neural. A gravidade, as condições iniciais, a sequência aleatória de ações e os parâmetros da simulação também podem contribuir para o deslocamento.
</mark>
<br/><br/>

> **Nota:** O robô em `MANUAL` com o D-PAD para qualquer lateral faz com que ele deslize livremente pela rampa, e isso é pretendido do que foi extraido do artigo original, mas demonstra o ponto do parágrafo anterior, no entanto, girar o robô em qualquer direção no início da simulação e entrar em `LEARNING` permite que ele chegue a meta em todas as simulações feitas até agora.

<mark>
Permanecem diversos pontos a serem aperfeiçoados, como a calibração dos estímulos, a revisão da referência utilizada para calcular a aceleração, a segunda revisão das equações e outras visitas ao artigo original e a aula sobre "Modelagem de redes bioinspiradas" para entender a aderencia da implementação atual contra em especial os conceitos de plasticidade e metaplasticidade apresentados nas mesmas.
</mark>
<br/><br/>

<mark>
Assim, o principal resultado da Fase 2 não é demonstrar definitivamente que o robô aprendeu por efeito da plasticidade, mas construir uma plataforma em que essa hipótese possa ser examinada de forma controlada, observável e reproduzível. Na Fase 3, o objetivo sugerido é executar conjuntos de simulações com parâmetros e condições de referência registrados, comparando os efeitos produzidos por diferentes configurações e mecanismos de plasticidade.
</mark>
<br/><br/>

## Referências

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

## Apêndices

### Apêndice A - Guia de reprodução

Este apêndice descreve a preparação do ambiente necessário para inspecionar o código, executar os testes automatizados e reproduzir a simulação integrada da Fase 2. Os comandos devem ser executados a partir da raiz do repositório, salvo quando indicado de outra forma.

O procedimento principal utiliza *uv*, pois `pyproject.toml` e `uv.lock` constituem as fontes de configuração e travamento das dependências Python. Os procedimentos com *pip* e *conda* são mantidos como alternativas.

#### Requisitos de software

A tabela esta em ordem sugerida de instalação

| Software | Versão ou condição | Finalidade |
|---|---|---|
| GCC, G++ e *make* | toolchain compatível com o sistema | compilação de controladores ou *plugins* nativos |
| *Git* | versão recente | obtenção e atualização do repositório |
| *Webots* | `R2025a` | execução dos mundos e do controlador do robô |
| Python | `3.13.x` | rede neural, protocolo, testes e relatórios |
| *uv* | versão recente | instalação reproduzível |
| *conda* (não instale o Python antes se usar esta opção) | versão recente | instalação reproduzível |
| *Visual Studio Code* ou outro editor | opcional | inspeção e desenvolvimento do código |

O experimento integrado utiliza um controlador Python e, por isso, GCC não é necessário para interpretar a rede neural. A toolchain permanece documentada porque o repositório contém controladores e exemplos nativos e porque ela será necessária caso esses componentes sejam recompilados ou modificados.

#### Requisitos de hardware

| Hardware | Versão ou condição | Finalidade |
|---|---|---|
| controle compatível com *joystick* (modelo Xbox One S mapeado) | opcional para testes gerais; necessário na interface atual para selecionar os modos interativos | acionamento de `MANUAL`, `LEARNING` e demais modos |

#### Instalação de GCC, G++ e make

No Ubuntu Linux:

O pacote `build-essential` reúne GCC, G++, *make* e os componentes básicos de compilação:

```bash
sudo apt update
sudo apt install build-essential
gcc --version
g++ --version
make --version
```

No Windows:

O *Webots R2025a* distribui uma cópia própria do MinGW para seus controladores C e C++. Para desenvolvimento também fora do ambiente interno do simulador, pode-se instalar a toolchain UCRT64 do [MSYS2](https://www.msys2.org/).

Após instalar o MSYS2, deve-se abrir o terminal **MSYS2 UCRT64** e atualizar os pacotes:

```bash
pacman -Syu
```

Caso o terminal solicite encerramento após a atualização dos componentes centrais, deve-se abri-lo novamente e repetir `pacman -Syu`. Em seguida, instala-se a toolchain:

```bash
pacman -S --needed \
  mingw-w64-ucrt-x86_64-toolchain \
  mingw-w64-ucrt-x86_64-make \
  make
```

Quando as ferramentas precisarem ser utilizadas também pelo PowerShell ou pelo *Visual Studio Code*, os seguintes diretórios da instalação padrão podem ser adicionados ao `PATH` do usuário:

```text
C:\msys64\ucrt64\bin
C:\msys64\usr\bin
```

A instalação deve ser validada em um novo terminal:

```powershell
gcc --version
g++ --version
make --version
```

No pacote UCRT64, o executável específico do *make* também pode aparecer como `mingw32-make`; o pacote `make` fornece o comando genérico usado pelos procedimentos do projeto.

#### Instalação do Git

No Ubuntu Linux:

```bash
sudo apt update
sudo apt install git
git --version
```

No Windows:

O *Git for Windows* pode ser obtido em <https://git-scm.com/>. Em sistemas com *winget*, a instalação também pode ser realizada em PowerShell:

```powershell
winget install --id Git.Git -e --source winget
git --version
```

Depois da instalação, deve-se abrir um novo terminal para que eventuais alterações no `PATH` sejam reconhecidas.

#### Clonagem do repositório

Usando HTTPS:

```bash
git clone https://github.com/lnncrs/DomanNeurocomputationalModel.git
cd DomanNeurocomputationalModel
```

Usando SSH, quando uma chave já estiver configurada no GitHub:

```bash
git clone git@github.com:lnncrs/DomanNeurocomputationalModel.git
cd DomanNeurocomputationalModel
```

Após a clonagem, os arquivos `pyproject.toml`, `uv.lock`, `requirements.txt` e `environment.yml` devem estar disponíveis na raiz do projeto.

#### Instalação do Webots

Os mundos do repositório declaram `R2025a` no cabeçalho e utilizam recursos dessa versão. Para reproduzir a configuração documentada, deve-se instalar **Webots R2025a**, em vez de substituir automaticamente pela versão mais recente. Os instaladores e as instruções oficiais estão disponíveis em <https://cyberbotics.com/doc/guide/installing-webots> e nas versões publicadas em <https://github.com/cyberbotics/webots/releases>.

No Ubuntu Linux:

Deve-se baixar o pacote `.deb` correspondente ao Webots R2025a e instalá-lo a partir do diretório em que foi salvo:

```bash
sudo apt install ./webots_2025a_amd64.deb
webots --version
```

O nome exato do arquivo pode variar conforme o pacote publicado. Se o executável não for encontrado no `PATH`, o Webots também pode ser iniciado pelo menu de aplicações ou por seu diretório de instalação.

No Windows:

Deve-se baixar e executar o instalador `webots-R2025a_setup.exe`. Na instalação padrão, o executável fica sob `C:\Program Files\Webots`.

Em algumas configurações, o Webots aberto diretamente pelo menu não herda o ambiente Python utilizado pelo projeto. Nesse caso, deve-se primeiro preparar ou ativar o ambiente e abrir o simulador pelo mesmo terminal. Em PowerShell, considerando a instalação padrão:

```powershell
& "C:\Program Files\Webots\msys64\mingw64\bin\webots.exe" --stdout --stderr --clear-cache
```

O caminho deve ser ajustado caso o Webots tenha sido instalado em outro diretório. As opções `--stdout` e `--stderr` mantêm visíveis as mensagens do controlador; `--clear-cache` é útil quando alterações em mundos ou arquivos PROTO não aparecem após uma atualização.

#### Ambiente Python recomendado com uv

O *uv* pode ser instalado pelos procedimentos oficiais disponíveis em <https://docs.astral.sh/uv/getting-started/installation/>.

No Ubuntu Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

No Windows PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Depois de abrir um novo terminal, a instalação pode ser verificada e o ambiente completo do projeto sincronizado:

```bash
uv --version
uv sync --all-groups --all-extras
```

O comando cria ou atualiza `.venv`, instala a versão compatível do Python quando necessário, instala o projeto e inclui os grupos de análise e desenvolvimento empregados nos *notebooks* e testes.

#### Alternativa com pip

Esta alternativa exige que Python `3.13.x` já esteja instalado. Recomenda-se criar um ambiente virtual isolado.

No Ubuntu Linux:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

No Windows PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

O arquivo `requirements.txt` instala o projeto com o conjunto de dependências de análise e inclui o *pytest*. A definição principal das dependências permanece em `pyproject.toml`.

#### Alternativa com conda

Pode-se utilizar Miniforge ou Miniconda seguindo a documentação em <https://docs.conda.io/projects/conda/en/stable/user-guide/install/>. Depois de instalar o gerenciador e abrir um terminal com `conda` disponível, o arquivo `environment.yml` cria o ambiente `webots` com Python 3.13 e as dependências do projeto:

```bash
conda env create -f environment.yml
conda activate webots
```

Quando o ambiente já existir e o arquivo tiver sido alterado, ele pode ser atualizado por:

```bash
conda env update -f environment.yml --prune
conda activate webots
```

#### Editor e extensões opcionais

O projeto não depende de um editor específico. Para desenvolvimento com *Visual Studio Code*, são úteis as extensões oficiais **Python** e **Pylance**, além de suporte a Jupyter para os *notebooks*. O editor deve ser iniciado somente depois da criação ou ativação do ambiente, ou configurado para usar o interpretador localizado em `.venv` ou no ambiente `webots` do *conda*.

#### Validação do ambiente

Com *uv*, todos os testes podem ser executados por:

```bash
uv run pytest
```

Com o ambiente *pip* ou *conda* ativado:

```bash
python -m pytest
```

Os testes cobrem as equações e a plasticidade da rede, a causalidade do protocolo, o mapeamento motor, a telemetria e a geração dos artefatos. Sua aprovação verifica a instalação do núcleo Python, mas não substitui a validação da física e dos sentidos de rotação dentro do Webots.

#### Lista mínima de verificação

- `git --version` responde corretamente;
- o Webots instalado corresponde à versão `R2025a`;
- `uv sync --all-groups --all-extras` ou uma alternativa equivalente termina sem erros;
- `webots/worlds/experiment_inclined_plane.wbt` abre sem erros de PROTO ou de controlador;
- as mensagens do controlador aparecem no terminal;
- o modo `LEARNING` pode ser selecionado;
- uma execução produz os arquivos esperados em `experiments/runs`.

### Apêndice B - Estrutura do repositório

O repositório separa o modelo neural, o protocolo experimental e a adaptação dos comandos motores dos artefatos específicos do Webots. A árvore a seguir apresenta alguns dos componentes do repositório que serão detalhados a seguir.

```text
DomanNeurocomputationalModel/
|-- assets/                                     # imagens utilizadas na documentação
|-- docs/                                       # relatórios e artigo de referência
|   |-- fase01-relatorio.md
|   `-- fase02-relatorio.md
|-- examples/                                   # exemplo mínimo de uso
|   `-- four_neuron_minimal.py
|-- experiments/                                # resultados gerados durante as simulações
|   `-- runs/
|       `-- learning_{timestamp}_{seed}/
|           |-- iterations.jsonl
|           |-- metadata.json
|           |-- report.html
|           `-- summary.json
|-- notebooks/                                  # execução não conectada da rede
|   `-- four_neuron_network_validation.ipynb
|-- src/                                        # rede e controle
|   |-- control/
|   |   `-- robot_adapter.py
|   |-- experiments/
|   |   |-- experiment_logger.py
|   |   |-- experiment_report.py
|   |   `-- experiment_runner.py
|   `-- neural/
|       `-- four_neuron_network.py
|-- tests/                                       # testes unitários
|   |-- test_experiment_runner.py
|   |-- test_four_neuron_network.py
|   |-- test_learning_runtime.py
|   `-- test_robot_adapter.py
|-- webots/                  # mundos, robôs, controladores e interfaces do simulador
|   |-- controllers/
|   |   |-- test_cpp_controller/                 # controle mínimo em C++ (Fase 1)
|   |   |-- test_py_controller/                  # controle mínimo em Python (Fase 1)
|   |   |-- four_wheels_collision_avoidance/     # controle de colisão em C (Fase 1)
|   |   |-- four_wheels_collision_avoidance_py/  # controle de colisão em Python (Fase 1)
|   |   |-- four_wheels_manual/           # controle do experimento em Python (Fase 2)
|   |   |   |-- four_wheels_manual.py     # controle multimodo
|   |   |   `-- learning_runtime.py       # ponte Webots -> aprendizagem
|   |   `-- [...]            # outros controladores usados como referência do Webots
|   |-- plugins/             # plugins para funcionamento da janela de telemetria
|   |   `-- robot_windows/
|   |       |-- custom_robot_window/      # plugin original Webots
|   |       `-- four_wheel_robot_window/  # plugin adaptado
|   |-- protos/
|   |   |-- differential/                 # testes históricos com controle diferencial
|   |   |-- physics/                      # testes históricos com física ativa
|   |   |-- CompactInclinedPlane.proto    # plano inclinado principal do experimento
|   |   |-- CompactInclinedPlaneExperiment.proto # plano inclinado + robô instrumentado
|   |   |-- FourWheelRobot.proto                 # robô de quatro rodas e instrumentação embarcada
|   |   |-- GoalArea.proto                # meta ajustável
|   |   |-- InclinedFourWheelRobot.proto  # wrapper para que o robô seja inclinado junto com a rampa
|   |   `-- SimpleRobot.proto             # robô derivado/desacoplado de `tutorials/4_wheels_robot.wbt` usado como base
|   |-- tutorials/                        # tutoriais do Webots usados como base
|   |   |-- 4_wheels_robot.wbt
|   |   |-- appearance.wbt
|   |   |-- collision_avoidance.wbt
|   |   |-- compound_solid.wbt
|   |   |-- custom_robot_window.wbt
|   |   |-- four_wheels.wbt
|   |   |-- hexapod.wbt
|   |   |-- my_first_simulation.wbt
|   |   `-- obstacles.wbt
|   `-- worlds/                           # mundos criados para o experimento
|       |-- empty_world.wbt               # mundo vazio usado como ponto de partida
|       |-- experiment_inclined_plane.wbt # experimento principal da Fase 2, com rampa, robô, meta e aprendizagem
|       |-- inclined_plane_fs.wbt         # plano inclinado em escala completa (full scale)
|       |-- inclined_plane_fs_balls.wbt   # plano inclinado em escala completa com bolas para validar a física
|       |-- inclined_plane_fs_robot.wbt   # plano inclinado em escala completa com robô
|       |-- inclined_plane_hs.wbt         # plano inclinado em meia escala (half scale)
|       |-- inclined_plane_hs_robot.wbt   # plano inclinado em meia escala com robô
|       |-- normal_plane_fs.wbt           # plano horizontal em escala completa
|       |-- normal_plane_fs_boxes.wbt     # plano horizontal em escala completa com caixas para validar a física
|       |-- normal_plane_fs_robot.wbt     # plano horizontal em escala completa com robô
|       |-- normal_plane_hs.wbt           # plano horizontal em meia escala
|       `-- normal_plane_hs_robot.wbt     # plano horizontal em meia escala com robô
|-- .gitignore
|-- .python-version
|-- environment.yml
|-- pyproject.toml
|-- README.md
|-- requirements.txt
`-- uv.lock
```

> **Nota:** Arquivos de cache, ambientes virtuais, resultados temporários e configurações internas de ferramentas foram omitidos.

#### Arquivos de configuração na raiz

| Arquivo | Função |
|---|---|
| `README.md` | apresentação geral e instruções principais do projeto |
| `pyproject.toml` | metadados, versão do Python e dependências do projeto |
| `uv.lock` | versões resolvidas para reprodução com uv |
| `requirements.txt` | alternativa de instalação com pip |
| `environment.yml` | alternativa de instalação com conda |
| `.python-version` | versão de Python selecionada para o diretório de trabalho |
| `.gitignore` | exclusão de ambientes, caches e resultados gerados |

#### Código-fonte do modelo

O diretório `src` contém o núcleo independente do Webots e está dividido em três responsabilidades:

- `src/neural` implementa o estado da rede de quatro neurônios, a ativação, a competição e as regras de plasticidade;

- `src/control` traduz as quatro ações neurais abstratas em comandos para os motores, sem incorporar a lógica do simulador;

- `src/experiments` organiza a execução do protocolo, registra os dados de cada iteração e produz o resumo e o relatório final.

O arquivo `src/neural/four_neuron_network.py` concentra o modelo neural.

O arquivo `src/control/robot_adapter.py` contém a fronteira entre as ações neurais e as primitivas motoras.

Em `src/experiments`, `experiment_runner.py`, `experiment_logger.py` e `experiment_report.py` separam, respectivamente, execução, persistência e apresentação dos resultados.

#### Estrutura da simulação Webots

O diretório `webots` reúne todos os componentes dependentes do simulador:

- `webots/worlds` contém os ambientes executáveis. `experiment_inclined_plane.wbt` é o mundo principal da Fase 2; os demais mundos preservam configurações intermediárias usadas para validar física, planos, bolas, robôs e diferentes escalas;

- `webots/protos` contém as definições reutilizáveis do plano, da meta, do robô e dos objetos de teste. Os subdiretórios `differential` e `physics` preservam, respectivamente, modelos diferenciais e objetos utilizados na validação física;

- `webots/controllers` contém o controle executado durante a simulação. O controlador atualmente relevante para o experimento integrado é `four_wheels_manual` e apesar do nome histórico, ele reúne os modos `AUTOMATIC`, `MANUAL`, `PASSIVE_FREE`, `PASSIVE_REALISTIC` e `LEARNING`;

- `webots/plugins/robot_windows` contém as interfaces HTML, CSS, JavaScript e C exibidas como janela de telemetria e acompanahmento do robô.  `four_wheel_robot_window` corresponde à interface principal de acompanhamento;

- `webots/tutorials` preserva mundos usados no aprendizado inicial da plataforma e como referência de implementação. Esses mundos não constituem a configuração experimental da Fase 2.

No controlador principal, `four_wheels_manual.py` realiza a leitura dos sensores, a seleção do modo de controle e o envio dos comandos às rodas. `learning_runtime.py` conecta esse ciclo do Webots ao núcleo localizado em `src` e mantém a janela temporal de cada ação neural.

#### Documentação, exemplos e validação

- `docs` contém os relatórios, os documentos de planejamento e o artigo usado como referência.

- `assets` armazena as imagens utilizadas na documentação;

- `notebooks/four_neuron_network_validation.ipynb` permite examinar o modelo neural com dados sintéticos fora do Webots;

- `examples/four_neuron_minimal.py` apresenta uma execução mínima da rede de quatro neurônios;

#### Testes automatizados

O diretório `tests` reproduz a mesma divisão funcional do código:

| Arquivo | Responsabilidade principal |
|---|---|
| `test_four_neuron_network.py` | equações, inicialização, competição e plasticidade neural |
| `test_robot_adapter.py` | tradução das ações abstratas para comandos motores |
| `test_experiment_runner.py` | causalidade, classificação do movimento, critérios e artefatos experimentais |
| `test_learning_runtime.py` | integração temporal, telemetria, meta e funcionamento do runtime usado pelo Webots |

> **Nota:** Esses testes validam o comportamento computacional somente.

### Apêndice C - Evolução histórica da simulação

Foram necessárias diversas simulações para construir o experimento da Fase 2, os principais saltos qualitativos do projeto estão listados abaixo.

#### Simulação de física

O primeiro desafio foi reproduzir física com parâmetros de mundo terrestre com exatidão aproximada(gravidade, atrito, elasticidade, etc), o filme inclined_plane é o plano inclinado com bolas para a simulação de física.

inclined_plane: https://youtu.be/qvbR1wQidVg

![inclined plane](../assets/inclined_plane.png)

Imagem: inclined_plane

> **Nota:** Os planos foram criados especificamente para o projeto.


#### Simulação de colisão do robô

O segundo desafio foi montar um robô e posicioná-lo neste mundo simulado, o filme inclined_plane_with_robot e inclined_plane_with_robot_1 é o plano inclinado com o robô e controle de batida (nao rede neural) para testar se o robô funcionava na simulação, o último tem um guardrail mais baixo (o que impede a queda do robô).

inclined_plane_with_robot: https://youtu.be/1YhcI6GHoAs

inclined_plane_with_robot_1: https://youtu.be/zjciixsm578

![inclined plane with robot](../assets/inclined_plane_with_robot.png)

Imagem: inclined_plane_with_robot

> **Nota:** Nos robôs de teste de batida foram usados modelos de exemplo da biblioteca aberta do Webots adaptados.

#### Simulação de controle

Por fim era necessário conseguir que uma interface de controle baseada em código conseguisse interagir com a simulação, o filme normal_plane_with_rotation é um primeiro teste com juntas, motores e ativação via interface de controle, esse passo foi decisivo no projeto, pois abriu portas para que fosse possível controlar aspectos da simulação via interface programável primeiro em C e depois em Python.

normal_plane_with_rotation: https://youtu.be/ZKbbiObtkQ8

![normal plane with rotation](../assets/normal_plane_with_rotation.png)

Imagem: normal_plane_with_rotation

> **Nota:** As peças rotacionando com controle foram criadas do zero porque era necessário entender a fundo como funcionava exatamente a "junção" entre duas peças nesta simulação.

### Apêndice D - Localização e configuração dos parâmetros

Este apêndice relaciona os parâmetros apresentados no corpo do relatório aos
campos, constantes e argumentos que determinam seus valores na implementação.
A indicação **default interno** significa que o campo é configurável em código,
mas ainda não é exposto pelo mundo principal. A indicação **argumento do
controlador** significa que o valor pode ser informado por `controllerArgs`.

#### Parâmetros da rede neural

| Parâmetro | Campo ou constante | Arquivo | Configuração integrada |
|---|---|---|---|
| número de neurônios | `NEURON_COUNT`; `NeuralConfig.neuron_count` | `src/neural/four_neuron_network.py` | fixado e validado em 4 |
| peso recorrente | `NeuralConfig.recurrent_weight` | `src/neural/four_neuron_network.py` | default interno |
| ganho sigmoidal | `NeuralConfig.sigmoid_gain` | `src/neural/four_neuron_network.py` | default interno |
| pesos não diagonais iniciais | `initial_weight_min`; `initial_weight_max` | `src/neural/four_neuron_network.py` | defaults internos; sorteio uniforme condicionado pela seed |
| taxa sináptica `epsilon` | `NeuralConfig.synaptic_learning_rate` | `src/neural/four_neuron_network.py` | default interno |
| taxa intrínseca `xi` | `NeuralConfig.intrinsic_learning_rate` | `src/neural/four_neuron_network.py` | default interno |
| deslocamento inicial | `NeuralConfig.initial_shift` | `src/neural/four_neuron_network.py` | default interno |
| competição | `NeuralConfig.competition_mode` | `src/neural/four_neuron_network.py` | default `CompetitionMode.DETERMINISTIC` |
| escopo da plasticidade | `NeuralConfig.plasticity_scope` | `src/neural/four_neuron_network.py` | default `PlasticityScope.WINNER_ONLY` |
| fonte da plasticidade intrínseca | `NeuralConfig.intrinsic_output_source` | `src/neural/four_neuron_network.py` | default `IntrinsicOutputSource.POST_COMPETITION` |
| desvio do ruído de ativação | `NeuralConfig.activation_noise_std` | `src/neural/four_neuron_network.py` | default `0.0`; desativado |
| limites adicionais dos pesos | `NeuralConfig.optional_weight_bounds` | `src/neural/four_neuron_network.py` | default `None`; sem limites adicionais |
| seed neural | `LearningRuntimeConfig.random_seed`; `NeuralConfig.random_seed` | `webots/controllers/four_wheels_manual/learning_runtime.py` | argumento `--learning-seed`, definido no mundo principal |

O `LearningRuntime` constrói `NeuralConfig` informando explicitamente a seed e
a normalização da aceleração. Os demais parâmetros neurais utilizam os defaults
centralizados em `src/neural/four_neuron_network.py`.

#### Parâmetros do protocolo de aprendizagem

| Parâmetro | Campo ou constante | Arquivo | Configuração integrada |
|---|---|---|---|
| duração nominal da ação | `LearningRuntimeConfig.action_duration_seconds` | `webots/controllers/four_wheels_manual/learning_runtime.py` | argumento `--learning-action-duration`, definido no mundo principal |
| velocidade no modo `LEARNING` | `LearningRuntimeConfig.wheel_speed` | `webots/controllers/four_wheels_manual/learning_runtime.py` | argumento `--learning-speed`, definido no mundo principal |
| limiar de movimento estacionário | `LearningRuntimeConfig.stationary_threshold` | `webots/controllers/four_wheels_manual/learning_runtime.py` | default interno |
| intensidade da maraca | `LearningRuntimeConfig.sound_intensity` | `webots/controllers/four_wheels_manual/learning_runtime.py` | aceita `--learning-sound-intensity`; o mundo usa o default |
| escala da aceleração | `LearningRuntimeConfig.acceleration_scale` | `webots/controllers/four_wheels_manual/learning_runtime.py` | argumento `--learning-acceleration-scale`, definido no mundo principal |
| entrada visual | `visual=0.0` | `webots/controllers/four_wheels_manual/learning_runtime.py` | fixada; canal visual desativado |
| movimentos consecutivos | `ExperimentConfig.learning_streak` | `webots/controllers/four_wheels_manual/learning_runtime.py` | fixado em `5` na criação do protocolo |
| sinal de descida | `ExperimentConfig.downhill_sign` | `webots/controllers/four_wheels_manual/learning_runtime.py` | fixado em `-1` na criação do protocolo |

Os argumentos configurados pelo mundo principal encontram-se em
`webots/worlds/experiment_inclined_plane.wbt`.

#### Parâmetros do mundo Webots

| Parâmetro | Campo ou constante | Arquivo | Configuração integrada |
|---|---|---|---|
| passo básico do mundo | `WorldInfo.basicTimeStep` | `webots/worlds/experiment_inclined_plane.wbt` | campo do mundo; `16 ms` |
| passo do controlador | `TIME_STEP` | `webots/controllers/four_wheels_manual/four_wheels_manual.py` | constante; `64 ms`, equivalente a quatro passos básicos |
| seed do mundo | `WorldInfo.randomSeed` | `webots/worlds/experiment_inclined_plane.wbt` | campo do mundo; independente de `--learning-seed` |
| inclinação da rampa | `angle` | `webots/worlds/experiment_inclined_plane.wbt` | repetida em `CompactInclinedPlane` e `InclinedFourWheelRobot`; valores devem coincidir |
| área lógica da meta | `GoalArea.size`; `GoalArea.detectionHeight`; `--goal` | `webots/worlds/experiment_inclined_plane.wbt` | configuração duplicada entre mundo e controlador |
| permanência na meta | `GoalArea.dwellTime`; último valor de `--goal` | `webots/worlds/experiment_inclined_plane.wbt` | monitor geral utiliza o valor; `LEARNING` termina na entrada |

Gravidade, atrito e parâmetros de contato não estão explicitados no mundo
principal e permanecem herdados dos defaults do Webots.

#### Parâmetros do robô e dos sensores

| Parâmetro | Campo ou constante | Arquivo | Configuração integrada |
|---|---|---|---|
| torque do modo passivo realista | `PASSIVE_REALISTIC_TORQUE` | `webots/controllers/four_wheels_manual/four_wheels_manual.py` | constante hardcoded; `0,03 N·m` por roda |

CMCC - Universidade Federal do ABC (UFABC) - Santo André - SP - Brasil
