
& "C:\Program Files\Webots\msys64\mingw64\bin\webots.exe" --stdout --stderr

# 🧠 Dorman Network - Aprendizado em Rampa Inclinada

Projeto TCC UFABC: Rede neural de 4 neurônios com aprendizado por reforço online em ambiente Webots.

## 📋 Conceito

**Objetivo**: Robô de 4 rodas aprende a descer uma rampa inclinada até a base usando apenas 4 neurônios com plasticidade sináptica.

**Inspiração**: Paper original sobre redes neurais mínimas com aprendizado emergente.

## 🎯 Especificações do Ambiente

### Mundo Webots
- **Rampa**: comprida (10m) e ampla (2m), inclinação ~10°
- **Guardrails**: laterais vermelhos para conter o robô
- **Base**: objetivo verde na parte inferior (Y = -5.5)
- **Física**: gravidade terrestre, atrito realista

### Robô
- **Differential drive**: 2 motores principais (um por lado)
- **Configuração física**: 2 rodas motorizadas + 2 esferas de estabilização
- **Motores**:
  - Motor esquerdo: controla rodas do lado esquerdo
  - Motor direito: controla rodas do lado direito
- **Sensores**:
  - 4 sensores de proximidade (frente, trás, esquerda, direita)
  - Giroscópio (velocidade angular)
  - Bússola (orientação para o objetivo)
  - GPS (posição global)

## 🧠 Arquitetura Neural

**Modelo fiel ao paper original:**

```
Sensores (6 inputs) → [N1: Esquerdo Frente  ]  \n                      [N2: Esquerdo Trás   ]  → Motor Esquerdo
                      [N3: Direito Frente  ]  \n                      [N4: Direito Trás    ]  → Motor Direito
```

**Mapeamento:**
- N1 (esquerdo, horário) + N2 (esquerdo, anti-horário) → Motor Esquerdo
- N3 (direito, horário) + N4 (direito, anti-horário) → Motor Direito
- Comando motor = N_frente - N_trás

**Comportamentos emergentes:**
- Frente: N1 + N3 ativos
- Ré: N2 + N4 ativos
- Giro direita: N1 + N4 ativos
- Giro esquerda: N2 + N3 ativos

**Aprendizado**: Reforço online baseado em progresso até a base.

📖 Detalhes completos em: [`docs/neural_architecture.md`](docs/neural_architecture.md)

## 🚀 Setup

### Requisitos
- Python 3.13
- Webots R2023b
- Dependências: `numpy`, `matplotlib`, `tqdm`, `python-dotenv`

### Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Ou com o projeto
pip install -e .
```

### Configurar Webots

1. Abrir Webots
2. **Tools → Preferences → Python command**
3. Apontar para Python 3.13: `python` ou caminho completo

## 🎮 Como Usar

### 1. Abrir mundo no Webots

```
File → Open World → worlds/inclined_plane.wbt
```

### 2. Iniciar simulação

Clicar em **Play** ▶️

O robô começa com pesos aleatórios e aprende em tempo real.

### 3. Acompanhar aprendizado

Terminal mostra progresso a cada 100 steps:

```
Step 100, Avg Reward: -0.0234
Step 200, Avg Reward: 0.1456
Step 300, Avg Reward: 0.8901
```

### 4. Testar sem Webots (simulação simplificada)

```bash
python experiments/test_learning.py
```

## 📁 Estrutura do Projeto

```
ufabc-dorman/
├── worlds/                  # 🌍 Mundos Webots
│   └── inclined_plane.wbt
├── protos/                  # 🤖 Definição do robô
│   └── FourNeuronRobot.proto
├── controllers/             # 🎮 Controller Webots
│   └── main_controller/
├── src/                     # 🧠 Algoritmo (independente)
│   ├── neural/             # Neurônios e rede
│   ├── control/            # Controladores
│   └── interfaces/         # Abstração simulador
├── experiments/            # 📊 Testes
├── data/                   # 📁 Logs
└── notebooks/              # 📓 Análise
```

## 🧪 Experimentos

### Manual Override (sem aprendizado)

```python
from src.control.manual_controller import ManualController

controller = ManualController(interface)
controller.forward(speed=1.0)
```

### Análise de Logs

Jupyter notebook disponível em `notebooks/exploratory_analysis.ipynb`

## 🎓 Paper Original

Baseado em: *[nome do paper aqui]*

**Diferenças desta implementação**:
- Rampa em vez de plano horizontal
- Objetivo explícito (base da rampa)
- Sensores de proximidade + giroscópio
- 4 rodas (2 motores + 2 passivas)

## 📊 Métricas

- **Reward**: progresso em direção à base
- **Convergência**: tempo até aprender comportamento estável
- **Robustez**: performance com pesos iniciais diferentes

## 🔧 Desenvolvimento

### Tecnologias
- **Simulador**: Webots R2023b
- **Linguagem**: Python 3.13
- **Build**: setuptools
- **Linter**: (adicionar ruff/black se necessário)

### Próximos Passos
- [ ] Salvar logs de treinamento
- [ ] Plotar evolução do reward
- [ ] Comparar diferentes taxas de aprendizado
- [ ] Exportar para robô físico
