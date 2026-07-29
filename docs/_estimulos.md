# Estímulos sensoriais no Webots

Sugestão de desenho:

| Estímulo original     | Sensoriamento no Webots                              | Cálculo recomendado                                             |
| --------------------- | ---------------------------------------------------- | --------------------------------------------------------------- |
| Vestibular/aceleração | GPS + orientação da rampa, ou acelerômetro           | aceleração ou velocidade descendente projetada no eixo da rampa |
| Visual/listras        | sensor de luz simulado ou posição relativa às faixas | frequência de transições preto–branco durante a ação            |
| Auditivo/palmas       | evento controlado pelo supervisor                    | intensidade fixa quando houver avanço descendente correto       |

O artigo descreve justamente aceleração corporal, transições visuais das faixas e som de maraca associado ao movimento correto.

## 1. Estímulo vestibular: movimento ao longo da rampa

A melhor medida não é simplesmente o eixo longitudinal local do robô, porque ele pode girar. O ideal é medir o movimento no **eixo fixo de descida da rampa**.

Defina:

- $\vec{r}$: vetor unitário apontando para baixo na rampa;
- $\vec{p}(t)$: posição atual do robô;
- $\Delta t$: duração entre medições.

Primeiro calcule a velocidade descendente:

$$
v_r(t)=\frac{\vec{p}(t)-\vec{p}(t-\Delta t)}{\Delta t}\cdot\vec{r}$$

Depois, se realmente quiser aceleração:

$$
a_r(t)=\frac{v_r(t)-v_r(t-\Delta t)}{\Delta t}
$$

O estímulo deve considerar somente a componente favorável à descida:

$$
S_{\text{vest}}=\max(0,a_r)
$$

No experimento, **a velocidade descendente média pode ser mais estável do que a aceleração**, porque a aceleração numérica tende a ser ruidosa. Podemos registrar ambas, mas começar usando:

$$
S_{\text{vest}}=\max(0,\overline{v_r})
$$

Isso responde diretamente:

> Quanto o robô avançou para baixo durante a última ação?

### Recomendação prática

Usar o GPS para calcular deslocamento/velocidade no eixo da rampa. Manter o acelerômetro como medida complementar de deslizamento ou impacto.

---

## 2. Estímulo visual: fluxo das listras

Para reproduzir o artigo, o sinal visual não deveria a princípio, medir alinhamento com a meta. Ele deveria medir **quantas mudanças entre preto e branco foram percebidas durante o deslocamento**.

Duas sugestões:

### Sensor de luz simulado

Colocar um sensor voltado para uma parede ou superfície listrada e ler sua intensidade luminosa:

```text
branco → valor alto
preto  → valor baixo
```

Convertendo em estado binário:

$$
c(t)=
\begin{cases}
1, & L(t)\geq L_{\text{limiar}}\\
0, & L(t)<L_{\text{limiar}}
\end{cases}
$$

Contando uma transição quando:

$$
c(t)\neq c(t-1)
$$

Durante uma ação:

$$
N_{\text{transições}} = \sum_t \mathbf{1}[c(t)\neq c(t-1)]
$$

A frequência visual seria:

$$
f_{\text{visual}} = \frac{N_{\text{transições}}}{T_{\text{ação}}}
$$

Quanto mais rápido o robô desce, mais transições ocorrem.

### Cálculo geométrico sem sensor

Sabendo a distância entre as faixas, é possível calcular quantas fronteiras o robô atravessou usando sua posição no eixo da rampa. É mais limpo, mas menos parecido com um sensor real.

### Nota sobre cone visual

Um cone visual da meta pode ser testado como uma **variante experimental**, denominada `goal_alignment`, mas não substitui diretamente o canal visual na reprodução mais fiel do artigo **se o tutor da criança não estiver na meta**, se estiver, o cone visual pode ser testado.

---

## 3. Estímulo auditivo: reforço contingente

No artigo a maraca é tocada quando o robô realiza um movimento correto. Diferentemente da aceleração e da visão, sua intensidade não depende de quanto ele desliza.

O supervisor (não é usado supervisor neste momento) pode avaliar o deslocamento descendente durante a ação:

$$
\Delta x_r = [\vec{p}_{\text{final}} - \vec{p}_{\text{inicial}}]\cdot\vec{r}
$$

Então:

$$
S_{\text{som}}=
\begin{cases}
S_{\max}, & \Delta x_r\geq d_{\min}\\
0, & \text{caso contrário}
\end{cases}
$$

Depois da normalização (exemplo):

```text
movimento correto para baixo → 0,9
sem avanço suficiente         → 0,0
```

## Como normalizar os três

Cada modalidade deve ser convertida para uma faixa comum, como $[0, 0.9]$.

Uma normalização limitada pode ser:

$$
S_{\text{norm}} = 0.9 \cdot \operatorname{clip}\left(\frac{x-x_{\min}}{x_{\max}-x_{\min}}, 0, 1\right)
$$

Para estímulos presentes, mas mínimos podemos usar $[0, 1]$ e $[0, 0.9]$:

$$
S_{\text{norm}}=
\begin{cases}
0, & x\leq x_{\text{limiar}}\\
0.1 + 0.8 \cdot \operatorname{clip}\left(\frac{x-x_{\text{limiar}}}{x_{\max}-x_{\text{limiar}}}, 0, 1\right), & x>x_{\text{limiar}}
\end{cases}
$$

Assim, $0$ significa ausência do estímulo; valores entre $0.1$ e $0.9$ indicam presença com intensidade crescente.

## Ordem causal correta

O ciclo deveria ser:

```text
1. neurônio vencedor escolhe a ação
2. robô executa a ação durante uma janela
3. ambiente responde
4. mede-se:
   - avanço/aceleração na rampa
   - transições visuais
   - ocorrência do reforço sonoro
5. os três valores são normalizados e somados
6. essa soma entra na próxima iteração neural
```

Isso preserva a lógica do artigo:

```text
ação anterior
→ consequência ambiental
→ estímulos sensoriais
→ plasticidade
→ próxima ação
```
