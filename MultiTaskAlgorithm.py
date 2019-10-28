import global_config
import numpy as np
from utils import one_hot, read_params
from stable_baselines.common import SetVerbosity
from MultiTaskAgent import MultiTaskAgent
from MetaAgent import MetaAgent


class MultiTaskLearning:
    def __init__(self, set_of_tasks, algorithm, policy, number_of_episodes_for_estimating, target_performances,
                 uniform_policy_steps, max_train_steps, n_cpus, logging=True, transfer_id=None, tensorboard_logging=None,
                 verbose=1, lambda_=None):
        """

        :param set_of_tasks:
        :param algorithm: Chosen multi-task algorithm. Available: 'A5C','EA4C' ...
        """
        if transfer_id is not None:
            if set_of_tasks is not None:
                print("The given set of tasks is overwritten by the tasks used by the referred model (transfer_id).")
            params = read_params(transfer_id)
            self.tasks = params['tasks']
        else:
            self.tasks = set_of_tasks

        self.algorithm = algorithm
        self.verbose = verbose
        self.logging = logging

        ActiveSamplingMultiTaskAgent = MultiTaskAgent(algorithm, policy, self.tasks, global_config.n_steps, max_train_steps, n_cpus,
                                                      transfer_id, tensorboard_logging=tensorboard_logging)

        meta_decider = None

        if self.algorithm == "A5C":
            self.__A5C_init(self.tasks, number_of_episodes_for_estimating, target_performances,
                            uniform_policy_steps, max_train_steps, ActiveSamplingMultiTaskAgent)
        elif self.algorithm == "EA4C":
            self.__EA4C_init(self.tasks, number_of_episodes_for_estimating, target_performances,
                             uniform_policy_steps, max_train_steps, ActiveSamplingMultiTaskAgent, meta_decider, lambda_)

    def __A5C_init(self, SetOfTasks, NumberOfEpisodesForEstimating, TargetPerformances,
                   uniform_policy_steps, MaxTrainSteps, ActiveSamplingMultiTaskAgent):
        assert isinstance(SetOfTasks, list), "SetOfTask must be a list"
        assert isinstance(TargetPerformances, dict), "TargetPerformance must be a dictionary"
        self.ta = TargetPerformances  # Target score in task Ti. This could be based on expert human performance or even published scores from other technical works
        assert isinstance(NumberOfEpisodesForEstimating, int), "NumberOfEpisodesForEstimating must be integer"
        self.n = NumberOfEpisodesForEstimating  # Number of episodes which are used for estimating current average performance in any task Ti
        self.l = uniform_policy_steps  # Number of training steps for which a uniformly random policy is executed for task selection. At the end of l training steps, the agent must have learned on ≥ n
        self.t = MaxTrainSteps  # Total number of training steps for the algorithm
        self.s = []  # List of last n scores that the multi-tasking agent scored during training on task Ti.
        self.a = []  # Average scores for every task
        self.m = []
        assert isinstance(ActiveSamplingMultiTaskAgent, MultiTaskAgent)
        self.amta = ActiveSamplingMultiTaskAgent  # The Active Sampling multi-tasking agent
        self.p = []  # Probability of training on an episode of task Ti next.
        self.tau = global_config.tau  # Temperature hyper-parameter of the softmax task-selection non-parametric policy

        for _ in range(len(self.tasks)):
            self.p.append(1 / len(self.tasks))
            self.a.append(0.0)
            self.m.append(0.000000001)
        for i in range(len(self.tasks)):
            self.s.append([0.0 for _ in range(self.n)])

    def __A5C_train(self):
        with SetVerbosity(self.verbose):
            episode_learn = 0
            performance = 0
            while self.amta.model.train_step < self.t:
                if self.amta.model.train_step > self.l:
                    for j in range(len(self.tasks)):
                        self.a[j] = sum(self.s[j])/self.n
                        self.m[j] = (self.ta[self.tasks[j]] - self.a[j]) / (self.ta[self.tasks[j]]) #* self.tau) # minél kisebb annál jobban teljesít az ágens az adott gamen
                    for j in range(len(self.tasks)):
                        self.p[j] = np.exp(self.m[j]) / (sum(np.exp(self.m)))
                if episode_learn % global_config.logging_frequency == 0:
                    performance = [1-m for m in self.m]
                    performance = [np.min([m, 1]) for m in performance]
                    performance = np.mean(performance)  # qam
                    self.amta.save_model(performance)
                    self.amta.flush_tbw()
                j = np.random.choice(np.arange(0, len(self.p)), p=self.p)
                ep_scores, train_steps = self.amta.train_for_one_episode(self.tasks[j], logging=self.logging)
                episode_learn += 1
                self.s[j].append(np.mean(ep_scores))
                if len(self.s[j]) > self.n:
                    self.s[j].pop(0)
            self.amta.save_model(performance)
            self.amta.exit_tbw()

    def __EA4C_init(self, SetOfTasks, NumberOfEpisodesForEstimating, TargetPerformances, uniform_policy_steps,
                    MaxTrainSteps, ActiveSamplingMultiTaskAgent, MetaLearningAgent, lambda_):
        assert isinstance(SetOfTasks, list), "SetOfTask must be a list"
        assert isinstance(TargetPerformances, dict), "TargetPerformance must be a dictionary"
        self.ta = TargetPerformances  # Target score in task Ti. This could be based on expert human performance or even published scores from other technical works
        assert isinstance(NumberOfEpisodesForEstimating, int), "NumberOfEpisodesForEstimating must be integer"
        self.n = NumberOfEpisodesForEstimating  # Number of episodes which are used for estimating current average performance in any task Ti
        self.t = MaxTrainSteps  # Total number of training steps for the algorithm
        self.s = []  # List of last n scores that the multi-tasking agent scored during training on task Ti.
        self.p = []  # Probability of training on an episode of task Ti next.
        self.c = np.zeros(len(self.tasks))  # Count of the number of training episodes of task Ti.
        self.r1 = 0
        self.r2 = 0  # First & second component of the reward for meta-learner, defined in lines 93-94
        self.reward = 0  # Reward for meta-learner
        self.l = uniform_policy_steps  # Number of tasks to consider in the computation of r2.
        self.s_avg = []  # Average scores for every task
        assert isinstance(ActiveSamplingMultiTaskAgent, MultiTaskAgent)
        self.amta = ActiveSamplingMultiTaskAgent  # The Active Sampling multi-tasking agent
        assert isinstance(MetaLearningAgent, MetaAgent)
        self.ma = MetaLearningAgent # Meta Learning MultiTaskAgent.
        self.lambda_ = lambda_ # Lambda weighting.
        for _ in range(len(self.tasks)):
            self.p.append(1 / len(self.tasks))
        for i in range(len(self.tasks)):
            self.s.append([0.0 for _ in range(self.n)])
        for i in range(len(self.tasks)):
            self.s_avg.append(0.0)

    def __EA4C_train(self):
        performance = 0
        for train_step in range(self.t):
            j = self.p.index(max(self.p))
            self.c[j] = self.c[j] + 1
            scores = self.amta.train_for_one_episode(self.tasks[j], logging=self.logging)
            self.s[j].append(np.mean(scores))
            if len(self.s[j]) > self.n:
                self.s[j].pop(0)
            for i in range(len(self.s_avg)):
                self.s_avg[i] = sum(self.s[i])/len(self.s[i])
            s_avg_norm = [self.s_avg[i] / self.ta[self.tasks[i]] for i in range(len(self.s_avg))]
            s_avg_norm.sort()
            s_min_l = s_avg_norm[0:self.l]
            performance = None #TODO
            self.r1 = 1 - self.s_avg[j] / self.c[j]
            self.r2 = 1 - np.average(np.clip(s_min_l, 0, 1))
            self.reward = self.lambda_ * self.r1 + (1 - self.lambda_) * self.r2
            self.p = self.ma.train_and_sample(game_input=[self.c / sum(self.c), self.p, one_hot(j, len(self.tasks))], reward=self.reward)
        self.amta.save_model(performance)
        self.amta.exit_tbw()

    def train(self):
        if self.algorithm == "A5C":
            self.__A5C_train()
        elif self.algorithm == "EA4C":
            self.__EA4C_train()
