# Rede neural de quatro neurônios

Esta pasta reconstrói a rede descrita em *Doman's inclined floor method for
early motor organization simulated with a four neurons robot*. O objetivo é
manter no código uma separação verificável entre informações publicadas e
hipóteses necessárias para completar a implementação.

## Arquitetura publicada

- Quatro neurônios excitadores rate-code totalmente interconectados.
- `W[i][j]` representa a conexão do neurônio `j` para o neurônio `i`.
- As quatro recorrências `W[i][i]` são fixas em `0.7`.
- As doze conexões não diagonais são plásticas.
- A soma dos estímulos de aceleração, visão e som chega aos quatro neurônios.
- Somente o neurônio vencedor da competição permanece ativo.
- Cada neurônio executa uma direção de um dos dois conjuntos de rodas.

Mapeamento adotado:

| Neurônio | Ação abstrata |
|---|---|
| N1 | conjunto frontal, horário |
| N2 | conjunto frontal, anti-horário |
| N3 | conjunto traseiro, horário |
| N4 | conjunto traseiro, anti-horário |

O artigo explicita N1. A numeração de N2 a N4 é inferida da combinação de duas
direções para dois conjuntos. A rede não conhece nomes de motores físicos.

## Equações

A ativação operacional é:

```text
activation_i(t) = sensory_total(t)
                  + sum_j(W[i][j] * competitive_output_j(t-1))
```

Essa expressão reúne a descrição textual do artigo; ela não é apresentada
como uma única equação na publicação.

A saída sigmoidal (equação 3) é:

```text
O_i = 1 / (1 + exp(-gain * (activation_i - shift_i)))
```

com `gain = 25`. A saída é tratada como taxa/probabilidade contínua. Não há
amostragem Bernoulli no modo padrão.

A plasticidade sináptica de Grossberg (equação 2) é:

```text
delta_W[i][j] = epsilon * I_j * (activation_i - W[i][j])
```

`I_j` é a saída competitiva do passo anterior. No modo padrão `winner_only`,
somente pesos que chegam ao vencedor atual são candidatos à atualização. Como
somente o vencedor anterior tem saída não nula, isso reforça uma transição de
uma cadeia neuronal. Esse escopo é uma hipótese operacional, não uma escolha
explicitada pelo artigo. O modo `all_postsynaptic` permite testar a leitura
literal da equação para todos os neurônios pós-sinápticos.

A plasticidade intrínseca (equação 4) é:

```text
shift_i(t+1) = (xi * O_i(t) + shift_i(t)) / (1 + xi)
```

Por padrão `O_i` é a saída após a competição. A saída anterior à competição
está disponível como variante experimental.

## Ordem temporal

O método `FourNeuronNetwork.step()` recebe o feedback produzido pela ação
anterior e devolve a próxima ação:

```text
ação anterior
-> resposta do ambiente
-> entrada sensorial atual
-> ativação com W(t)
-> competição
-> plasticidade, produzindo W(t+1)
-> próxima ação
```

O `ExperimentRunner` formaliza uma iteração como uma ação mantida por uma
janela temporal. A maraca é produzida somente depois que o deslocamento da
ação anterior é classificado como descida. Ela é uma entrada sensorial sonora,
e não uma variável de reward de reinforcement learning.

## Hipóteses configuráveis

O artigo não informa todos os valores necessários. Os defaults abaixo são
pontos de partida e devem constar nos metadados dos ensaios:

| Parâmetro | Default | Situação |
|---|---:|---|
| pesos não diagonais iniciais | uniforme `[0.1, 0.9]` | hipótese |
| taxa sináptica `epsilon` | `0.01` | hipótese |
| taxa intrínseca `xi` | `0.01` | dentro da faixa publicada |
| shift inicial | `0.5` | hipótese |
| duração do movimento | `0.5 s` | hipótese |
| intensidade sonora | `1.0` | hipótese; constante como no artigo |
| limiar de deslocamento | `0.005 m` | hipótese |
| ruído de ativação | `0.0` | opcional, desligado |
| limites dos pesos | nenhum | clipping não publicado |

No primeiro passo todas as ativações podem empatar, pois ainda não existe uma
saída recorrente anterior. O empate é resolvido pelo RNG configurado; a seed
torna essa decisão reprodutível. Nos passos seguintes, pesos e históricos
distintos quebram a simetria.

## Critério de aprendizagem

São registrados separadamente:

- cinco movimentos consecutivos na mesma direção, critério literal do artigo;
- cinco movimentos consecutivos para baixo, objetivo do experimento.

Uma repetição do mesmo neurônio não prova aprendizagem: a classificação usa o
deslocamento físico observado durante cada iteração.

## Limites atuais

- A entrada visual ainda precisa de um detector de transições de faixas.
- Normalização e agregação temporal da aceleração devem ser calibradas.
- O adaptador Webots ainda não foi conectado ao modo `LEARNING`.
- Os sinais físicos de rotação horária de cada eixo precisam ser validados no
  robô virtual antes da integração.
