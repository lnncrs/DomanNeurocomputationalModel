
# Interpretação da rede

O artigo descreve quatro neurônios excitatórios do tipo *rate-code*, totalmente interconectados, que recebem uma soma comum de estímulos sensoriais e controlam quatro ações motoras possíveis sobre dois conjuntos de rodas.

O código implementa essa ideia geral mas acrescenta algumas hipóteses porque o artigo não fornece todos os detalhes computacionais.

- **plasticidade sináptica**: modifica as conexões **entre** os neurônios;
- **plasticidade intrínseca**: modifica a excitabilidade **do próprio neurônio**.

## Por que se chama sináptica?

Uma **sinapse** é a conexão pela qual um neurônio influencia outro.

Se o neurônio de origem esteve ativo, a conexão dele para o neurônio atual pode aumentar ou diminuir conforme a ativação atual e o peso que já existia.

Porque aquilo que muda é a eficácia da sinapse, representada pelo peso da conexão.

Não é o neurônio que se torna diretamente mais ou menos excitável. É o efeito de um neurônio sobre outro que muda.

## Por que se chama intrínseca?

Porque a mudança ocorre **dentro do modelo do próprio neurônio**, em sua função de excitabilidade.

"Intrínseco" significa próprio, interno ao elemento.

A plasticidade intrínseca não muda a conexão entre dois neurônios. Ela muda uma característica interna de cada neurônio: o `shift` da sua função sigmoidal.

## Comparação direta

| Característica     | Sináptica                               | Intrínseca                               |
| ------------------ | --------------------------------------- | ---------------------------------------- |
| O que muda?        | Peso da conexão                         | `shift` do neurônio                      |
| Onde ocorre?       | Entre dois neurônios                    | No próprio neurônio                      |
| Representação      | Matriz (W)                              | Vetor de quatro `shifts`                 |
| Efeito principal   | Altera quais transições são favorecidas | Altera quão fácil é cada neurônio vencer |
| Memória aproximada | Relação entre ações consecutivas        | Histórico de atividade individual        |
| Papel no sistema   | Formação de sequências                  | Regulação da excitabilidade              |


# 1. O que cada neurônio representa

No código:

```python
class MotorAction(Enum):
    FRONT_CLOCKWISE = 0
    FRONT_COUNTERCLOCKWISE = 1
    REAR_CLOCKWISE = 2
    REAR_COUNTERCLOCKWISE = 3
```

Cada neurônio está associado a uma ação motora abstrata:

| Neurônio | Ação                                      |
| -------- | ----------------------------------------- |
| N1       | conjunto frontal no sentido horário       |
| N2       | conjunto frontal no sentido anti-horário  |
| N3       | conjunto traseiro no sentido horário      |
| N4       | conjunto traseiro no sentido anti-horário |

O artigo afirma explicitamente que cada neurônio controla um movimento específico, horário ou anti-horário, de um dos dois conjuntos de rodas. Também fornece como exemplo que o neurônio 1 produz movimento horário no conjunto frontal.

**Portanto, a competição entre os neurônios também é uma competição entre quatro ações motoras.**

---

# 2. A rede é totalmente interconectada

A matriz de pesos tem quatro linhas e quatro colunas:

```text
weights[target][source]
```

A convenção usada no código é:

```text
weights[i][j] = conexão de Nj para Ni
```

Assim:

* linha: neurônio que recebe;
* coluna: neurônio que envia.

A rede possui:

* 4 conexões autorrecorrentes;
* 12 conexões entre neurônios diferentes.

As conexões autorrecorrentes têm peso fixo `0,7`, conforme o artigo. As outras doze podem mudar durante a aprendizagem.

No método `reset()`:

```python
if target == source:
    weight = self.config.recurrent_weight
else:
    weight = self._rng.uniform(
        self.config.initial_weight_min,
        self.config.initial_weight_max,
    )
```

Isso significa:

* diagonal: sempre `0,7`;
* fora da diagonal: valores aleatórios entre `0,1` e `0,9`.

**A parte aleatória é uma hipótese da reconstrução, porque o artigo não publica claramente os valores iniciais das doze conexões modificáveis.**

---

# 3. Entradas sensoriais

O artigo utiliza três modalidades:

* aceleração;
* visão, por meio de um sensor de luz detectando faixas pretas e brancas;
* som, produzido por uma maraca após movimentos corretos.

As contribuições dos três sensores são somadas e aumentam a ativação dos quatro neurônios.

No código:

```python
@dataclass(frozen=True)
class SensoryInput:
    acceleration: float = 0.0
    visual: float = 0.0
    sound: float = 0.0
```

Cada canal passa por uma transformação linear:

```python
valor_normalizado = (valor - offset) * escala
```

Depois:

```python
total=sum(values)
```

Portanto:

$$
S(t)=a(t)+v(t)+s(t)
$$

após a normalização.

Esse total é comum aos quatro neurônios. Ou seja, os sensores não enviam valores diferentes para cada neurônio. Todos recebem a mesma soma sensorial.

**A normalização explícita não aparece dessa forma no artigo. É uma adaptação necessária para integrar sensores com grandezas e escalas diferentes.**

---

# 4. O estado anterior da rede influencia o estado atual

Aqui entra a recorrência. O código calcula a ativação de cada neurônio assim:

```python
recurrent_input += (
    self._weights[target][source] * previous_output[source]
)
```

e depois:

```python
activations.append(sensory_total + recurrent_input)
```

Em termos matemáticos:

$$
a_i(t)=S(t)+\sum_{j=1}^{4} W_{ij}(t)\,O_j^c(t-1)
$$

A ativação atual de cada neurônio é formada por:

1. entrada sensorial atual;
2. atividade da rede na iteração anterior;
3. pesos das conexões.

Como a competição normalmente deixa apenas um neurônio ativo, em geral somente o vencedor anterior contribui efetivamente para a próxima ativação.

Exemplo:

* na iteração anterior venceu N2;
* então somente (O_2^c(t-1)) é diferente de zero;
* cada neurônio atual recebe uma contribuição associada à conexão que sai de N2.

Assim:

```text
N2 venceu antes
→ a coluna de origem N2 influencia a próxima iteração
→ o valor de cada peso N2 → Ni altera a chance de Ni vencer agora
```

É assim que a rede pode aprender **sequências** de ações.

---

# 5. A sigmoide transforma ativação em saída

O código usa:

```python
def sigmoid_output(activation, shift, gain=25.0):
    return _stable_sigmoid(gain * (activation - shift))
```

Isso corresponde à equação 3 do artigo:

$$
O_i(t)=\frac{1}{1+\exp[-25(a_i(t)-\theta_i(t))]}
$$

O resultado fica entre zero e um.

A interpretação é:

* se a ativação está muito abaixo do `shift`, a saída fica próxima de zero;
* se está próxima do `shift`, a saída fica perto de `0,5`;
* se está acima do `shift`, a saída se aproxima de um.

## Por que aparece `25`?

O `25` é o ganho da sigmoide. Ele controla o quão abrupta é a transição.

Com ganho pequeno, a curva é suave. Com ganho `25`, ela é bastante inclinada:

```text
ativação ligeiramente abaixo do shift → saída baixa
ativação ligeiramente acima do shift → saída alta
```

O artigo utiliza esse valor diretamente na equação, mas não oferece uma justificativa experimental detalhada para a escolha exata de `25`.

Portanto, a afirmação segura é:

> O valor 25 foi adotado do artigo e funciona como ganho da função sigmoidal; a publicação não apresenta uma análise de sensibilidade que justifique exclusivamente esse valor.

---

# 6. Competição entre os quatro neurônios

Após obter as quatro saídas sigmoidais, o código seleciona a maior:

```python
maximum = max(raw_output)
```

Se houver empate, sorteia entre os empatados:

```python
return self._rng.choice(tied)
```

Depois preserva apenas a saída do vencedor:

```python
competitive_output = tuple(
    output if neuron == winner else 0.0
    for neuron, output in enumerate(raw_output)
)
```

Então:

$$
O_i^c(t)=
\begin{cases}
O_i(t), & i=w(t)\\
0, & i\neq w(t)
\end{cases}
$$

O artigo diz que o neurônio mais ativado permanece ativo e os demais são inativados.

O desempate aleatório é uma hipótese do código, porque o artigo não explica o que fazer quando dois neurônios têm exatamente a mesma ativação.

---

# 7. O vencedor seleciona a ação

Depois da competição:

```python
action=MotorAction(winner)
```

Isso transforma diretamente:

```text
índice 0 → FRONT_CLOCKWISE
índice 1 → FRONT_COUNTERCLOCKWISE
índice 2 → REAR_CLOCKWISE
índice 3 → REAR_COUNTERCLOCKWISE
```

A rede não controla diretamente quatro velocidades de rodas. Ela escolhe uma ação abstrata. Outro módulo transforma essa ação nos comandos concretos enviados ao robô.

Esse desacoplamento não é uma exigência do artigo, mas é uma boa decisão de engenharia.

---

# 8. Plasticidade sináptica

Depois da seleção do vencedor, os pesos podem ser alterados.

A função é:

```python
def grossberg_delta(
    *,
    input_j,
    activation_i,
    weight_ij,
    epsilon,
):
    return epsilon * input_j * (activation_i - weight_ij)
```

Isso corresponde à equação 2 do artigo:

$$
\Delta W_{ij}=\varepsilon\,I_j\,(a_i-W_{ij})
$$

No seu código, (I_j) é representado pela saída competitiva da iteração anterior:

```python
input_j=previous_output[source]
```

A leitura é:

> Se o neurônio de origem esteve ativo antes, o peso dele para o neurônio atual é ajustado em direção à ativação atual.

## Quando o peso aumenta?

Se:

$$
a_i > W_{ij}
$$

então:

$$
\Delta W_{ij}>0
$$

e o peso aumenta.

## Quando diminui?

Se:

$$
a_i < W_{ij}
$$

então:

$$
\Delta W_{ij}<0
$$

e o peso diminui.

## Quando não muda?

Se o neurônio de origem não esteve ativo:

$$
I_j=0
$$

então:

$$
\Delta W_{ij}=0
$$

O termo:

$$
a_i-W_{ij}
$$

funciona como uma realimentação negativa. Quanto maior o peso já existente, menor tende a ser o aumento adicional. O artigo relaciona essa propriedade à metaplasticidade.

---

# 9. `WINNER_ONLY` e `ALL_POSTSYNAPTIC`

No código:

```python
class PlasticityScope(str, Enum):
    WINNER_ONLY = "winner_only"
    ALL_POSTSYNAPTIC = "all_postsynaptic"
```

No modo padrão:

```python
if self.config.plasticity_scope == PlasticityScope.WINNER_ONLY:
    targets_to_update = (current_winner,)
```

Somente os pesos que chegam ao vencedor atual são examinados.

Exemplo:

```text
N2 venceu antes
N4 vence agora
```

A conexão relevante é:

```text
N2 → N4
```

porque:

* N2 forneceu a atividade pré-sináptica anterior;
* N4 é o vencedor atual.

Isso faz com que a rede fortaleça ou enfraqueça transições entre vencedores consecutivos.

Entretanto, o artigo não deixa completamente explícito se a equação deve ser aplicada somente ao vencedor pós-sináptico ou a todos os neurônios. Portanto, `WINNER_ONLY` é uma **hipótese operacional**.

A opção `ALL_POSTSYNAPTIC` permite aplicar a regra a todos os neurônios receptores, embora somente a origem anteriormente ativa tenha entrada pré-sináptica diferente de zero.

---

# 10. Por que a diagonal não muda

Dentro da atualização:

```python
if target == source:
    continue
```

E depois:

```python
self._weights[neuron][neuron] = self.config.recurrent_weight
```

Isso garante:

$$
W_{11}=W_{22}=W_{33}=W_{44}=0,7
$$

O artigo afirma que as conexões do neurônio consigo próprio não são modificáveis e receberam arbitrariamente peso `0,7`.

Uma consequência importante é:

```text
se o mesmo neurônio vence duas vezes seguidas
→ a transição seria Ni → Ni
→ essa conexão é diagonal
→ ela não é aprendida
```

A rede aprende principalmente transições entre neurônios diferentes, isto é, sequências formadas por ações distintas.

---

# 11. Plasticidade intrínseca

Além dos pesos, cada neurônio possui um `shift` individual.

A função é:

```python
def intrinsic_shift(
    *,
    previous_shift,
    output,
    xi,
):
    return (xi * output + previous_shift) / (1.0 + xi)
```

Correspondente à equação 4:

$$
\theta_i(t+1)=\frac{\xi O_i(t)+\theta_i(t)}{1+\xi}
$$

No código, é usada a saída após competição:

```python
output=competitive_output[neuron]
```

Isso significa:

* vencedor: saída positiva;
* perdedores: saída zero.

## Para o vencedor

Seu `shift` se move em direção à sua saída atual.

Se a saída for alta, o `shift` aumenta. Na iteração seguinte, esse neurônio precisará de mais ativação para produzir a mesma saída.

## Para os perdedores

Como a saída competitiva é zero:

$$
\theta_i(t+1)=\frac{\theta_i(t)}{1+\xi}
$$

O `shift` diminui.

Com o `shift` menor, esses neurônios ficam mais fáceis de ativar futuramente.

Assim, a plasticidade intrínseca atua como uma regulação homeostática:

```text
neurônio vence muito
→ shift tende a aumentar
→ fica mais difícil vencer novamente

neurônio perde muito
→ shift tende a diminuir
→ fica mais fácil voltar a competir
```

É justamente isso que a Figura 4 do artigo ilustra: baixa atividade desloca a sigmoide para a esquerda; alta atividade a desloca para a direita.

O artigo diz que (\xi) varia entre `0,1` e `0,0001`. Valores maiores produzem adaptação mais rápida; valores menores, convergência mais lenta e potencialmente mais precisa.

O código usa:

```python
intrinsic_learning_rate = 0.01
```

que está dentro dessa faixa.

---

# 12. O que acontece em uma iteração completa

O método `step()` segue esta sequência:

```text
1. recebe aceleração, visão e som
2. normaliza os três canais
3. soma os canais
4. combina a soma sensorial com a saída recorrente anterior
5. calcula a ativação dos quatro neurônios
6. aplica a sigmoide
7. escolhe o vencedor
8. zera os perdedores
9. atualiza os pesos sinápticos
10. atualiza os shifts intrínsecos
11. guarda a saída competitiva atual
12. converte o vencedor em ação motora
```

Em forma causal:

```text
consequência da ação anterior
→ estímulos sensoriais
→ estado atual da rede
→ neurônio vencedor
→ plasticidade
→ próxima ação
```

---

# 13. Como a rede aprende uma sequência de descida

Imagine a sequência:

```text
N1 → N3 → N2
```

e que essas ações produzem descida.

A descida gera entradas sensoriais maiores:

* maior aceleração;
* mais transições visuais;
* som da maraca.

Essas entradas aumentam a ativação da rede.

Quando N1 foi ativo antes e N3 vence agora, a conexão:

```text
N1 → N3
```

pode ser reforçada.

Na transição seguinte:

```text
N3 → N2
```

também pode ser reforçada.

Depois de repetições, forma-se uma cadeia:

```text
N1 favorece N3
N3 favorece N2
```

Essa cadeia representa uma sequência motora que tende a produzir descida.

Esse é o mecanismo central proposto no artigo: estímulos mais intensos após movimentos descendentes favorecem a formação de cadeias de neurônios conectadas por pesos fortalecidos.

---

# 14. O que é fiel ao artigo e o que é hipótese

## Diretamente sustentado pelo artigo

* quatro neurônios;
* rede totalmente interconectada;
* neurônios excitatórios *rate-code*;
* soma dos três estímulos;
* quatro ações motoras;
* autorrecorrência fixa em `0,7`;
* doze conexões modificáveis;
* sigmoide com ganho `25`;
* regra pré-sináptica de Grossberg;
* plasticidade intrínseca;
* competição com apenas um neurônio ativo;
* aprendizagem associada às consequências sensoriais das ações.

## Hipóteses ou decisões da reconstrução

* pesos iniciais uniformes entre `0,1` e `0,9`;
* `epsilon = 0,01`;
* `shift inicial = 0,5`;
* usar a saída competitiva anterior como (I_j);
* atualizar somente o vencedor atual;
* usar a saída pós-competição na plasticidade intrínseca;
* desempatar por sorteio;
* normalização linear explícita;
* ordem computacional exata das atualizações.

Essas decisões não estão necessariamente erradas. O importante é classificá-las como hipóteses e testá-las na Fase 3.
