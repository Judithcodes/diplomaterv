MTI1 = ['SpaceInvaders-v0', 'CrazyClimber-v0', 'Seaquest-v0', 'DemonAttack-v0', 'StarGunner-v0'] # disc, obs jó
#actionspace disc 6             disc 9              disc 18         disc 6          disc 18
MTI2 = ["Asterix-v0", "Alien-v0", "Assault-v0", "TimePilot-v0", "Gopher-v0", "ChopperCommand-v0"] #disc, változó obs méret

MTI3 = ['Breakout-v0', 'Centipede-v0', 'Frostbite-v0', 'Qbert-v0', 'KungFuMaster-v0', 'WizardOfWor-v0'] # disc, observation nem jó változik, de csak a méret

MTI4 = ['Atlantis-v0', 'Breakout-v0', 'Bowling-v0', 'CrazyClimber-v0', 'Seaquest-v0', 'SpaceInvaders-v0', 'Pong-v0', 'Enduro-v0'] # disc, observation jo

MTI5 = ['SpaceInvaders-v0', 'Seaquest-v0', 'Asterix-v0', 'Alien-v0', 'Assault-v0', 'BankHeist-v0', 'CrazyClimber-v0', 'DemonAttack-v0', 'Gopher-v0', 'NameThisGame-v0', 'StarGunner-v0', 'Tutankham-v0']

MTI6 = ['Atlantis-v0', 'Amidar-v0', 'Breakout-v0', 'Bowling-v0', 'BeamRider-v0', 'ChopperCommand-v0', 'Centipede-v0', 'Frostbite-v0', 'KungFuMaster-v0', 'Pong-v0', 'RoadRunner-v0', 'Phoenix-v0']

MTI7 = ['SpaceInvaders-v0', 'Seaquest-v0', 'Asterix-v0', 'Alien-v0', 'Assault-v0', 'BankHeist-v0', 'CrazyClimber-v0', 'DemonAttack-v0', 'Gopher-v0', 'NameThisGame-v0', 'StarGunner-v0', 'Tutankham-v0', 'Amidar-v0', 'ChopperCommand-v0', 'Breakout-v0', 'BeamRider-v0', 'Bowling-v0', 'Centipede-v0', 'Krull-v0', 'Kangaroo-v0', 'Phoenix-v0']

MTIC = ['Breakout-v0', 'Seaquest-v0']

target_performances = {
    'SpaceInvaders-v0': 1200,
    'Seaquest-v0': 2700,
    'Asterix-v0': 2400,
    'Alien-v0': 2700,
    'Assault-v0': 1900,
    'TimePilot-v0': 9000,
    'BankHeist-v0': 1700,
    'CrazyClimber-v0': 170000,
    'DemonAttack-v0': 27000,
    'Gropher-v0': 9400,
    'NameThisGame-v0': 12100,
    'StarGunner-v0': 40000,
    'Tutankham-v0': 260,
    'Amidar-v0': 1030,
    'ChopperCommand-v0': 4970,
    'Breakout-v0': 560,
    'BeamRider-v0': 2200,
    'Bowling-v0': 17,
    'Centipede-v0': 3300,
    'Krull-v0': 1025,
    'Kangaroo-v0': 26,
    'Phoenix-v0': 5384,
    'Atlantis-v0': 163660,
    'Frostbite-v0': 300,
    'KungFuMaster-v0': 36000,
    'Pond-v0': 19.5,
    'RoadRunner-v0': 59540,
    'Qbert-v0': 26000,
    'WizardOfWor-v0': 3300,
    'Enduro-v0': 0.77
}

number_of_episodes_for_estimating = 10
uniform_policy_steps = 1_000_000  # Number of training steps for which a uniformly random policy is executed for task selection. At the end of l training steps, the agent must have learned on ≥ n
MaxTrainSteps = 10_000_000  # k x 50_000_000 time stepig futott az eredeti cikkbe tehát kb itt k x 5_000_000 train step kéne
tau = 1
n_steps = 5

logging_frequency = 10  # number of episodes

tensorboard_log = "./data/tb_logs"

log_path = "./data/logs"

if __name__ == '__main__':
    import gym
    for env_name in MTI7:
        env = gym.make(env_name)
        print("{} - {}".format(env_name, env.action_space))
