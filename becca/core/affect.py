"""
The Affect class.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

import becca.core.tools as tools

class Affect(object):
    """
    Assign reward to the appropriate features and track it over time.

    Affect or mood, is the level of arousal of the brain.
    It is influenced by the recent history of reward and in turn
    influences the intensity with which a brain pursues
    its goals and makes plans.

    Attributes
    ----------
    cumulative_reward : float
        The total reward amassed since the last visualization.
    reward_history : list of floats
        A time series of reward accumulated during the periods between
        each time ``Affect`` is visualized..
    reward_steps : list of ints
        A time series of the brain's age in time steps corresponding
        to each of the rewards in ``reward_history``.
    satisfaction : float
        A filtered average of the reward.
    satisfaction_time_constant : float
        The time constant of the leaky integrator used to filter
        reward into a rough average of the recent reward history.
    time_since_reward_log : int
        Number of time steps since reward was last logged. It gets
        logged every time ``Affect`` is visualized.
    """


    def __init__(self):
        """
        Set up``Affect``.

        Parameters
        ----------
        num_features : int
            The number of features in the ``brain``. ``Affect`` will
            learn the reward associated with each of these.
        """
        self.satisfaction_time_constant = 1e3
        self.satisfaction = 0.
        self.cumulative_reward = 0.
        self.time_since_reward_log = 0.
        self.reward_history = []
        self.reward_steps = []


    def update(self, reward):
        """
        Update the current level of satisfaction and record the reward.

        Parameters
        ----------
        new_features : array of floats
            The most recently observed set of feature activities.
        reward : float
            The most recently observed reward value.

        Returns
        -------
        self.satisfaction : float
        """
        # Clip the reward so that it falls between -1 and 1.
        reward = np.maximum(np.minimum(reward, 1.), -1.)

        # Update the satisfaction, a filtered version of the reward.
        rate = 1. / self.satisfaction_time_constant
        self.satisfaction = self.satisfaction * (1. - rate) + reward * rate

        # Log the reward.
        self.cumulative_reward += reward
        self.time_since_reward_log += 1

        return self.satisfaction


    def visualize(self, timestep, brain_name, log_dir):
        """
        Update the reward history, create plots, and save them to a file.

        Parameters
        ----------
        timestep : int
            See docstring for ``brain.py``.
        brain_name : str
            See docstring for ``brain.py``.
        log_dir : str
            See docstring for ``brain.py``.

        Returns
        -------
        performance : float
            The average reward over the lifespan of the ``brain``.
        """
        # Check whether any time has passed since the last update.
        if self.time_since_reward_log > 0:
            # Update the lifetime record of the reward.
            self.reward_history.append(float(self.cumulative_reward) /
                                       (self.time_since_reward_log + 1))
            self.cumulative_reward = 0
            self.time_since_reward_log = 0
            self.reward_steps.append(timestep)

        performance = np.mean(self.reward_history)

        # Plot the lifetime record of the reward.
        fig = plt.figure(11111)
        color = (np.array(tools.copper) +
                 np.random.normal(size=3, scale=.1))
        color = np.maximum(np.minimum(color, 1.), 0.)
        color = tuple(color)
        linewidth = np.random.normal(loc=2.5)
        linewidth = 2
        linewidth = np.maximum(1., linewidth)
        plt.plot(self.reward_steps, self.reward_history, color=color,
                 linewidth=linewidth)
        plt.gca().set_axis_bgcolor(tools.copper_highlight)
        plt.xlabel('Time step')
        plt.ylabel('Average reward')
        plt.title('Reward history for {0}'.format(brain_name))
        fig.show()
        fig.canvas.draw()

        # Save a copy of the plot.
        filename = 'reward_history_{0}.png'.format(brain_name)
        pathname = os.path.join(log_dir, filename)
        plt.savefig(pathname, format='png')

        return performance
