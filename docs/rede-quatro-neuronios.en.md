# The four-neuron network

This document presents the plastic neural network used in the experiment in a progressive way: first the structure and concepts, then each mathematical transformation in the same order in which it occurs during an actual simulation iteration.

## What this network does

The network receives signals from the environment, selects one of four possible motor actions, and modifies its own state to favor actions that in the past produced movement toward the goal.

It does not use deep layers, a loss function, labeled data, or backpropagation. Adaptation occurs from the sensory feedback produced by the consequences of the robot's own actions.

## But first, a step back: Why?

### The starting point - Doman and babies

The starting point is not robotics. It is an observation about babies.

Glenn Doman observed that children with neurological lesions, when repeatedly placed on an inclined plane, tended to develop movement patterns toward the downhill direction. The gravitational stimulus, combined with the sensory feedback produced by the movement itself, appeared to contribute to motor organization even in compromised neural systems. The method became known as the *Doman inclined plane method*.

![doman](../assets/original-baby.png)

Baby in action: https://www.youtube.com/watch?v=6yrWI3MedFc

### The question posed by the 2011 paper

In the paper *Doman's Inclined Floor Method for Early Motor Organization Simulated with a Four Neurons Robot (2011)* by Ropero Peláez and Lucas Santana, the question posed is: is it possible to reproduce, even in simplified form, the mechanism by which these stimuli translate into motor organization? Here we see an inversion of what a neural network normally sets out to do - instead of training it to solve a problem, the network is built to observe a phenomenon.

> **This is an important point**: the network is not an end in itself, but a means to study plasticity and emergent motor organization.

The answer was to build a robot connected to four plastic neurons with a well-defined architecture, placed on an inclined plane with equally controlled stimuli. The robot receives acceleration, visual stimuli from the ramp stripes, and the sound of a rattle when it moves toward the goal. These stimuli modulate the network's plasticity mechanisms, which over iterations tends to favor the motor sequences that produced them.

The robot and the network are means to better understand plasticity and motor organization in babies.

![robot](../assets/original-robot.png)

Robot in action: https://www.youtube.com/shorts/DoPYKvXyYS8

### This project

This project computationally reproduces that experiment, maintaining fidelity to the paper where details were published and explicitly documenting where assumptions were necessary, while updating the computational and hardware means and keeping reproducibility and code open.

### The open direction

At this point the project opens an interesting door: the 2011 network was built with what was available in neuroscience and plasticity concepts at that time - now over a decade ago. The neuroscience of the last decade has brought deep advances and more detailed descriptions of how plasticity operates in small networks, including metaplasticity and homeostatic mechanisms that were not yet formalized in the same way.

Reproducing the paper is the starting point, but having a platform where the network can be reviewed, compared, and updated with these more recent findings is what makes the project relevant beyond mere reproduction.

![simulation](../assets/experiment.png)


## The four neurons and what each one controls

Each neuron is associated with an abstract motor action over two wheel sets of the robot:

| Neuron | Action                                   |
| ------ | ---------------------------------------- |
| N1     | front set, clockwise                     |
| N2     | front set, counterclockwise              |
| N3     | rear set, clockwise                      |
| N4     | rear set, counterclockwise               |

The neuron does not directly command individual wheel speeds. It selects an abstract action. A separate adapter translates that choice into the concrete commands sent to the simulator.

**Competition between neurons is, at the same time, competition between four motor actions.**



## The connection matrix

The network is fully interconnected: each neuron receives signals from all others and from itself.

The matrix convention is:

```text
W[i][j] = weight of the connection from Nj to Ni
row    = receiving neuron
column = sending neuron
```

The full matrix has 4 × 4 = 16 entries:

| **Receives ↓ / Sends →** | **N1** | **N2** | **N3** | **N4** |
| ------------------------ | -----: | -----: | -----: | -----: |
| **N1**                   |    0.7 |    w₁₂ |    w₁₃ |    w₁₄ |
| **N2**                   |    w₂₁ |    0.7 |    w₂₃ |    w₂₄ |
| **N3**                   |    w₃₁ |    w₃₂ |    0.7 |    w₃₄ |
| **N4**                   |    w₄₁ |    w₄₂ |    w₄₃ |    0.7 |

The four diagonal entries (N1→N1, N2→N2, etc.) are the **recurrent self-connections**. They have a fixed weight of **0.7** and never change during the experiment.

The other twelve entries are the **plastic connections**: they start with random values between 0.1 and 0.9 and can increase or decrease each iteration.

> The choice of random initial values is a reconstruction hypothesis, since the paper does not publish the initial values of the twelve modifiable connections.



## The three sensory inputs

The network receives, at each iteration, three signals from the environment:

| Channel      | What it represents                                                         |
| ------------ | -------------------------------------------------------------------------- |
| Acceleration | variation in longitudinal acceleration measured by the accelerometer       |
| Vision       | transitions detected by a light sensor on the ramp stripes                 |
| Sound        | stimulus produced by a rattle after movements toward the goal              |

The three channels are summed and the result is presented equally to all four neurons. There is no sensor exclusive to any single neuron.



## The two plasticity mechanisms

The network has two distinct adaptation mechanisms that operate in parallel each iteration:

| Feature            | Synaptic                                  | Intrinsic                                  |
| ------------------ | ----------------------------------------- | ------------------------------------------ |
| What changes?      | Connection weight between neurons         | `shift` internal to each neuron            |
| Where does it occur? | Between two neurons                     | Inside the neuron itself                   |
| Representation     | Matrix W (12 modifiable values)           | Vector of four `shifts`                    |
| Main effect        | Alters which transitions are favored      | Alters how easily each neuron can win      |
| Role in the system | Formation of motor sequences              | Regulation of individual excitability      |

**Synaptic plasticity** changes the efficacy of the connection: the effect one neuron exerts on another.

**Intrinsic plasticity** changes the excitability of the neuron itself: how much activation it needs to produce a high output.



## The complete flow of one iteration

The sequence below describes exactly what happens inside the `step()` method at each simulation iteration, in the order each transformation occurs.



### Steps 1 to 3 - Receive and combine sensory stimuli

The network receives the raw values of the three channels. Before using them, each channel goes through an independent linear transformation:

$$
\widetilde{x}_k(t) = \bigl(x_k(t) - o_k\bigr)\, s_k, \qquad k \in \{a, v, s\}
$$

Where $x_k(t)$ is the raw value of channel $k$, $o_k$ is a reference offset, and $s_k$ is a scale factor.

> **In plain words:** subtract a reference value and multiply by a scale. This allows channels with different physical units to enter the network in a comparable range.

The three normalized values are then summed into a single sensory input common to all four neurons:

$$
S(t) = \widetilde{x}_a(t) + \widetilde{x}_v(t) + \widetilde{x}_s(t)
$$

> **In plain words:** transformed acceleration + transformed vision + transformed sound. All four neurons receive exactly this same total.



### Steps 4 and 5 - Compute each neuron's activation

Each neuron's activation combines the current sensory input with the activity the network produced in the previous iteration:

$$
a_i(t) = S(t) + \sum_{j=1}^{4} W_{ij}(t)\, O_j^c(t-1)
$$

Where $W_{ij}(t)$ is the weight of the connection from $N_j$ to $N_i$, and $O_j^c(t-1)$ is the output of neuron $j$ after competition in the previous iteration.

> **In plain words:** add the sensory input to the contribution of each previous neuron, weighted by the connections. Since competition normally leaves only one neuron active, in general only the previous winner contributes to the recurrent sum.

This is what allows the network to learn **sequences**: if N2 won before, column N2 of matrix W determines how much each current neuron will be favored now.



### Step 6 - Transform activation into output via the sigmoid function

Each neuron's activation is converted into an output between 0 and 1:

$$
O_i(t) = \frac{1}{1 + \exp\!\bigl[-25\,(a_i(t) - \theta_i(t))\bigr]}
$$

Where $\theta_i(t)$ is the individual `shift` of neuron $i$ and 25 is the sigmoid gain (value adopted from the paper).

> **In plain words:** compare the activation to the neuron's `shift`. If well above the `shift`, the output approaches 1. If well below, it approaches 0. The gain of 25 makes this transition quite steep: a small difference between activation and `shift` already produces clearly high or low outputs.

The `shift` $\theta_i$ is the point at which neuron $i$'s sigmoid is centered. It can change each iteration through intrinsic plasticity, effectively sliding the curve left or right.



### Step 7 - Select the winning neuron

After computing the four outputs, the network selects the one with the highest value:

$$
w(t) = \underset{i \in \{1,2,3,4\}}{\operatorname{arg\,max}}\; O_i(t)
$$

> **In plain words:** the neuron with the highest sigmoid output wins. In the event of an exact tie, the winner is drawn randomly among the tied neurons (an operational hypothesis, since the paper does not specify this case).



### Step 8 - Zero the losers

After selection, the competitive output is defined:

$$
O_i^c(t) =
\begin{cases}
O_i(t), & \text{if } i = w(t) \\
0,       & \text{if } i \neq w(t)
\end{cases}
$$

> **In plain words:** the winner retains its sigmoid value. All others receive zero. This implements competition: in each iteration, only one action is selected.



### Step 9 - Update synaptic weights

With the winner defined, the weights of the connections arriving at it are adjusted by Grossberg's pre-synaptic rule:

$$
\Delta W_{ij}(t) = \varepsilon\, O_j^c(t-1)\, \bigl(a_i(t) - W_{ij}(t)\bigr)
$$

The new weight is:

$$
W_{ij}(t+1) = W_{ij}(t) + \Delta W_{ij}(t)
$$

Where $\varepsilon$ is the synaptic plasticity rate and $O_j^c(t-1)$ is the competitive output of the source neuron in the previous iteration.

> **In plain words:** if the source neuron was active before, the weight of its connection to the current winner is adjusted toward the winner's current activation. If the activation is greater than the existing weight, the weight increases. If less, it decreases. If the source neuron was not active ($O_j^c(t-1) = 0$), the weight does not change.

The term $(a_i - W_{ij})$ acts as negative feedback: the larger the existing weight, the smaller the additional increase tends to be. The paper relates this property to metaplasticity.

**Diagonal connections remain fixed at 0.7 and are reasserted after each step**, because the paper establishes that self-recurrent connections are not modifiable.

A direct consequence: if the same neuron wins two iterations in a row, the transition would involve the diagonal, which is fixed, and no modifiable weight is altered. The network learns primarily transitions between different neurons, that is, sequences formed by distinct actions.



### Step 10 - Update intrinsic `shifts`

Independently of synaptic plasticity, each neuron's `shift` is recalculated:

$$
\theta_i(t+1) = \frac{\xi\, O_i^c(t) + \theta_i(t)}{1 + \xi}
$$

Where $\xi$ is the intrinsic plasticity rate.

> **In plain words:** the new `shift` is a weighted average between the previous `shift` and the neuron's current output. The rate $\xi$ determines the speed of adaptation.

**For the winner:** its competitive output is positive, so the `shift` moves toward that value. If the output is high, the `shift` increases. In the next iteration, this neuron will need more activation to produce the same output - it becomes harder to win again.

**For the losers:** the competitive output is zero, so the formula reduces to:

$$
\theta_i(t+1) = \frac{\theta_i(t)}{1 + \xi}
$$

The `shift` decreases gradually. With a lower `shift`, the sigmoid slides left and the neuron becomes more responsive - easier to compete again.

This mechanism acts as homeostatic regulation of excitability:

```
neuron wins often  → shift increases → harder to win again
neuron loses often → shift decreases → easier to compete again
```



### Step 11 - Store state for the next iteration

The competitive output $O_i^c(t)$ computed in this iteration is stored. It will be used as $O_j^c(t-1)$ in steps 5 and 9 of the next iteration.

> This is the network's short-term memory mechanism: the only state that persists between iterations is the competitive outputs and the accumulated weights.



### Step 12 - Convert the winner into a motor action

The winning neuron's index is converted directly into one of the four actions:

| Index | Motor action                             |
| ----: | ---------------------------------------- |
| 0     | front set, clockwise                     |
| 1     | front set, counterclockwise              |
| 2     | rear set, clockwise                      |
| 3     | rear set, counterclockwise               |

This action is sent to the robot adapter, which translates it into the concrete speed commands for each motor. The network only knows the index; the hardware details are the adapter's responsibility.



## The complete cycle in causal form

```
consequence of previous action (environment)
  → acceleration, vision, and sound      [steps 1–3]
  → sensory sum S(t)                     [step 3]
  → activation a_i(t)                    [steps 4–5]
  → sigmoid output O_i(t)               [step 6]
  → winning neuron w(t)                  [step 7]
  → competitive output O_i^c(t)         [step 8]
  → synaptic plasticity W(t+1)           [step 9]
  → intrinsic plasticity θ(t+1)          [step 10]
  → state saved for next iteration       [step 11]
  → motor action executed                [step 12]
  → new consequence from environment...
```



## How learning emerges

Imagine the sequence of winners N1 → N3 → N2 produces downhill movement on the ramp.

Downhill movement generates more intense sensory stimuli: greater acceleration, more visual transitions, and the sound of the rattle. This increases $S(t)$ and, as a consequence, the activation of all neurons.

With higher activations, the weight updates from step 9 tend to be more expressive. The connections N1→N3 and N3→N2 are reinforced over repetitions.

After many successful iterations, a chain of strengthened weights forms:

```
N1 favors N3
N3 favors N2
```

This chain represents a motor sequence that the system has come to prefer because it was consistently associated with more intense stimuli.



## What comes from the paper and what is a reconstruction hypothesis

### Directly supported by the paper

- four excitatory rate-code neurons;
- fully interconnected network;
- sum of three sensory stimuli;
- four motor actions;
- fixed self-recurrence at 0.7;
- twelve modifiable connections;
- sigmoid with gain 25;
- Grossberg's pre-synaptic rule;
- intrinsic plasticity;
- competition with only one active neuron per iteration.

### Hypotheses or reconstruction decisions

- initial weights drawn uniformly between 0.1 and 0.9;
- $\varepsilon = 0.01$;
- $\xi = 0.01$;
- initial `shift` = 0.5;
- using the previous competitive output as the pre-synaptic input $I_j$;
- updating only the weights arriving at the current winner (`winner_only`);
- using the post-competition output for intrinsic plasticity;
- breaking ties by random draw;
- explicit linear normalization of sensory channels.

These decisions are not necessarily wrong. What matters is classifying them as hypotheses so they can be tested systematically.
