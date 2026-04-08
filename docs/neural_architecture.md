# 🧠 Arquitetura Neural - 4 Neurônios (Paper Original)

## Modelo do Paper

Baseado em: *Testing the inclined plane technique with a four neurons robot* (Dorman et al.)

### Estrutura Motor

**2 motores** (differential drive):
- **Motor Esquerdo**: controla todas as rodas do lado esquerdo
- **Motor Direito**: controla todas as rodas do lado direito

Cada motor pode girar em **2 direções**:
- Sentido horário (clockwise) → frente
- Sentido anti-horário (anticlockwise) → trás

### Mapeamento Neurônio → Motor

```
┌────────┬─────────────────┬────────────────┬──────────┐
│ Neuron │ Motor           │ Direção        │ Ação     │
├────────┼─────────────────┼────────────────┼──────────┤
│ N1     │ Esquerdo        │ Horário        │ Frente   │
│ N2     │ Esquerdo        │ Anti-horário   │ Trás     │
│ N3     │ Direito         │ Horário        │ Frente   │
│ N4     │ Direito         │ Anti-horário   │ Trás     │
└────────┴─────────────────┴────────────────┴──────────┘
```

### Conversão para Comandos

Cada motor recebe um comando resultante da **diferença** entre neurônios:

```python
motor_esquerdo = N1 - N2  # frente - trás
motor_direito  = N3 - N4  # frente - trás
```

**Exemplo de comportamento emergente:**

| N1 | N2 | N3 | N4 | Ação                    |
|----|----|----|----|-----------------------|
| +1 | 0  | +1 | 0  | Frente reto           |
| 0  | +1 | 0  | +1 | Ré reto               |
| +1 | 0  | 0  | +1 | Gira direita (N1+N4)  |
| 0  | +1 | +1 | 0  | Gira esquerda (N2+N3) |
| +1 | 0  | 0  | 0  | Curva suave esquerda  |

### Implementação no Robô

**Configuração física:**
- 2 rodas motorizadas principais (1 de cada lado)
- 2 esferas de estabilização (frente + trás)
- Differential drive simples

**Por que não 4 rodas motorizadas independentes?**

❌ Não é o modelo do paper
❌ Aumentaria complexidade sem necessidade
✅ Paper usa: "two servomotors acting over two wheel sets"

### Citações Relevantes do Paper

> "Each of these neurons is interconnected to each other and also to two servomotors."
> — Página 2

> "Each neuron activates either a clockwise or anticlockwise direction of each motor."
> — Página 2

> "each one of them controlling a specific clockwise or anticlockwise movement of two servomotors acting over two wheel sets."
> — Página 4

### Diferenças em Relação ao Paper Original

| Aspecto          | Paper Original           | Nossa Implementação      |
|------------------|--------------------------|--------------------------|
| Ambiente         | Plano horizontal         | Rampa inclinada (~10°)   |
| Tarefa           | Evitar queda             | Descer até base          |
| Sensores         | Não especificado         | 4 proximity + gyro       |
| Motores          | 2 servomotores           | 2 motores (differential) |
| Aprendizado      | Reforço online           | Reforço online (igual)   |

### Fidelidade ao Paper

✅ **Mantido:**
- 4 neurônios
- 2 motores (1 por lado)
- Mapeamento neurônio → motor + direção
- Aprendizado por reforço online
- Comportamento emergente

⚠️ **Adaptado:**
- Objetivo explícito (base da rampa)
- Sensores adicionais para navegação
- Ambiente com inclinação

### Para o TCC

Esta arquitetura pode ser descrita assim:

> "O sistema motor é composto por dois motores independentes em configuração *differential drive*, cada um controlando um conjunto de rodas de um lado do robô. A rede neural possui quatro neurônios, sendo que cada neurônio está associado a um movimento específico (sentido horário ou anti-horário) de um dos motores, resultando em quatro primitivas de ação: esquerda-frente, esquerda-trás, direita-frente, direita-trás. O comportamento motor emerge da combinação das ativações desses quatro neurônios."
