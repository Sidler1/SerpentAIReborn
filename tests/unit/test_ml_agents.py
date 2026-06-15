"""Phase G smoke tests: the PyTorch RL networks/agents run on the auto-detected device.

These exercise inference on whatever device get_device() selects (CUDA/MPS/CPU),
verifying the torch-2.x device-agnostic migration. They construct networks
directly rather than the full RainbowDQNAgent/PPOAgent (which need a game,
transport, and loggers).
"""

import torch

from serpent.machine_learning.device import get_device
from serpent.machine_learning.reinforcement_learning.ppo.policy import Policy
from serpent.machine_learning.reinforcement_learning.rainbow_dqn.dqn import DQN3
from serpent.machine_learning.reinforcement_learning.rainbow_dqn.noisy_linear import NoisyLinear
from serpent.machine_learning.reinforcement_learning.rainbow_dqn.rainbow_agent import RainbowAgent


def test_get_device_returns_torch_device():
    device = get_device()
    assert isinstance(device, torch.device)
    assert device.type in {"cuda", "mps", "cpu"}


def test_noisy_linear_forward_and_reset():
    device = get_device()
    layer = NoisyLinear(8, 4).to(device)
    layer.reset_noise()

    out = layer(torch.zeros(2, 8, device=device))
    assert out.shape == (2, 4)
    assert out.device.type == device.type


def test_dqn3_forward_shape():
    device = get_device()
    net = DQN3(action_space=5, history=4, atoms=51).to(device)

    out = net(torch.zeros(1, 4, 98, 98, device=device))
    assert out.shape == (1, 5, 51)  # (batch, action_space, atoms)
    assert out.device.type == device.type


def test_rainbow_agent_act_returns_valid_action():
    device = get_device()
    agent = RainbowAgent(action_space=5, device=device, history=4, conv_layers=3)

    action = agent.act(torch.zeros(4, 98, 98, device=device))
    assert isinstance(action, int)
    assert 0 <= action < 5


def test_ppo_policy_act_forward():
    device = get_device()
    policy = Policy((4, 100, 100), action_space=5, recurrent_policy=False).to(device)

    value, action, action_log_probs, states = policy.act(
        torch.zeros(1, 4, 100, 100, device=device),
        torch.zeros(1, policy.state_size, device=device),
        torch.ones(1, 1, device=device),
    )

    assert value.shape == (1, 1)
    assert action.shape == (1, 1)
    assert value.device.type == device.type
