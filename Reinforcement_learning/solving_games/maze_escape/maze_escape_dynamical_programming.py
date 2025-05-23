# Joachim JOBARD id:20020216-T352 & Farouk MILED id:20010524-T517
# Copyright [2024] [KTH Royal Institute of Technology] 
# Licensed under the Educational Community License, Version 2.0 (ECL-2.0)
# This file is part of the Computer Lab 1 for EL2805 - Reinforcement Learning.

from collections import defaultdict
from matplotlib.ticker import FuncFormatter
import numpy as np
import matplotlib.pyplot as plt
import time
from IPython import display
import random

# Implemented methods
methods = ['DynProg', 'ValIter']

# Some colours
LIGHT_RED    = '#FFC4CC'
LIGHT_GREEN  = '#95FD99'
BLACK        = '#000000'
WHITE        = '#FFFFFF'
LIGHT_PURPLE = '#E8D0FF'

class Maze:

    # Actions
    STAY       = 0
    MOVE_LEFT  = 1
    MOVE_RIGHT = 2
    MOVE_UP    = 3
    MOVE_DOWN  = 4

    # Give names to actions
    actions_names = {
        STAY: "stay",
        MOVE_LEFT: "move left",
        MOVE_RIGHT: "move right",
        MOVE_UP: "move up",
        MOVE_DOWN: "move down"
    }

    # Reward values 
    STEP_REWARD = -1          #put 1 and see what happens
    GOAL_REWARD = 100          #100 times higher.
    IMPOSSIBLE_REWARD = -1 #One for test for the time depending policy    #opposite to posible moves. Can be set lower
    MINOTAUR_REWARD = -100      #opposite to the goal reward

    def __init__(self, maze):
        """ Constructor of the environment Maze.
        """
        self.maze                     = maze
        self.actions                  = self.__actions()
        self.states, self.map         = self.__states()
        self.n_actions                = len(self.actions)
        self.n_states                 = len(self.states)
        self.transition_probabilities = self.__transitions()
        self.rewards                  = self.__rewards()

    def __actions(self):
        actions = dict()
        actions[self.STAY]       = (0, 0)
        actions[self.MOVE_LEFT]  = (0,-1)
        actions[self.MOVE_RIGHT] = (0, 1)
        actions[self.MOVE_UP]    = (-1,0)
        actions[self.MOVE_DOWN]  = (1,0)
        return actions

    def __states(self):
        
        states = dict()
        map = dict()
        s = 0
        for i in range(self.maze.shape[0]):
            for j in range(self.maze.shape[1]):
                for k in range(self.maze.shape[0]):
                    for l in range(self.maze.shape[1]):
                        if self.maze[i,j] != 1:
                            states[s] = ((i,j), (k,l))
                            map[((i,j), (k,l))] = s
                            s += 1
        
        states[s] = 'Eaten'
        map['Eaten'] = s
        s += 1
        
        states[s] = 'Win'
        map['Win'] = s
        
        return states, map

    def __move(self, state, action):               
        """ Makes a step in the maze, given a current position and an action. 
            If the action STAY or an inadmissible action is used, the player stays in place.
        
            :return list of tuples next_state: Possible states ((x,y), (x',y')) on the maze that the system can transition to.
        """
        
        if self.states[state] == 'Eaten' or self.states[state] == 'Win': # In these states, the game is over
            return [self.states[state]]
        
        else: # Compute the future possible positions given current (state, action)
            row_player = self.states[state][0][0] + self.actions[action][0] # Row of the player's next position 
            col_player = self.states[state][0][1] + self.actions[action][1] # Column of the player's next position 
            
            # Is the player getting out of the limits of the maze or hitting a wall?
            impossible_action_player = (row_player == -1) or \
                                             (row_player == self.maze.shape[0]) or \
                                             (col_player == -1) or \
                                             (col_player == self.maze.shape[1]) or\
                                             (self.maze[row_player,col_player] == 1)
        
            actions_minotaur = [[0, -1], [0, 1], [-1, 0], [1, 0]] # Possible moves for the Minotaur
            rows_minotaur, cols_minotaur = [], []
            for i in range(len(actions_minotaur)):
                # Is the minotaur getting out of the limits of the maze?
                impossible_action_minotaur = (self.states[state][1][0] + actions_minotaur[i][0] == -1) or \
                                             (self.states[state][1][0] + actions_minotaur[i][0] == self.maze.shape[0]) or \
                                             (self.states[state][1][1] + actions_minotaur[i][1] == -1) or \
                                             (self.states[state][1][1] + actions_minotaur[i][1] == self.maze.shape[1])
            
                if not impossible_action_minotaur:
                    rows_minotaur.append(self.states[state][1][0] + actions_minotaur[i][0])
                    cols_minotaur.append(self.states[state][1][1] + actions_minotaur[i][1])  
          

            # Based on the impossiblity check return the next possible states.
            if impossible_action_player: # The action is not possible, so the player remains in place
                states = []
                for i in range(len(rows_minotaur)):
                    
                    if self.states[state][0][0] == rows_minotaur[i] and self.states[state][0][1] == cols_minotaur[i]:                          # TODO: We met the minotaur
                        states.append('Eaten')
                    
                    elif self.maze[self.states[state][0][0], self.states[state][0][1]]==2:                           # TODO: We are at the exit state, without meeting the minotaur
                        states.append('Win')
                
                    else:     # The player remains in place, the minotaur moves randomly
                        states.append(((self.states[state][0][0], self.states[state][0][1]), (rows_minotaur[i], cols_minotaur[i])))
                
                return states
          
            else: # The action is possible, the player and the minotaur both move
                states = []
                for i in range(len(rows_minotaur)):
                
                    if row_player == rows_minotaur[i] and col_player == cols_minotaur[i]:      # TODO: We met the minotaur
                        states.append('Eaten')
                    
                    elif self.maze[row_player,col_player] == 2:       # TODO:We are at the exit state, without meeting the minotaur
                        states.append('Win')
                    
                    else: # The player moves, the minotaur moves randomly
                        states.append(((row_player, col_player), (rows_minotaur[i], cols_minotaur[i])))
              
                return states
        
        
        

    def __transitions(self):
        """ Computes the transition probabilities for every state action pair.
            :return numpy.tensor transition probabilities: tensor of transition
            probabilities of dimension S*S*A
        """
        # Initialize the transition probailities tensor (S,S,A)
        dimensions = (self.n_states,self.n_states,self.n_actions)
        transition_probabilities = np.zeros(dimensions)
        
        # TODO: Compute the transition probabilities.
        for state in range(self.n_states):
            for action in range(self.n_actions):
                next_states=self.__move(state,action)
                number_of_next_states=len(next_states)
                for next_state in next_states:
                    next_state = self.map[next_state]
                    transition_probabilities[state,next_state,action]=1/number_of_next_states
        print('ended calculation transition probabilities')
        return transition_probabilities


    def __rewards(self):
        
        """ Computes the rewards for every state action pair """

        rewards = np.zeros((self.n_states, self.n_actions))
        
        for s in range(self.n_states):
            for a in range(self.n_actions):
                
                if self.states[s] == 'Eaten': # The player has been eaten
                    rewards[s, a] = self.MINOTAUR_REWARD
                
                elif self.states[s] == 'Win': # The player has won
                    rewards[s, a] = self.GOAL_REWARD
                
                else:                
                    next_states = self.__move(s,a)
                    next_s = next_states[0] # The reward does not depend on the next position of the minotaur, we just consider the first one
                    
                    if self.states[s][0] == next_s[0] and a != self.STAY: # The player hits a wall
                        rewards[s, a] = self.IMPOSSIBLE_REWARD
                    
                    # elif a == self.STAY:
                    #     rewards[s,a] = 0 #modified
                    
                    else: # Regular move
                        rewards[s, a] = self.STEP_REWARD

        return rewards




    def simulate(self, start, policy, method):
        
        if method not in methods:
            error = 'ERROR: the argument method must be in {}'.format(methods)
            raise NameError(error)

        path = list()
        
        if method == 'DynProg':
            horizon = policy.shape[1] # Deduce the horizon from the policy shape
            t = 0 # Initialize current time
            s = self.map[start] # Initialize current state 
            path.append(start) # Add the starting position in the maze to the path
            
            while t < horizon - 1:
                a = policy[s, t] # Move to next state given the policy and the current state

                next_states = self.__move(s, int(a)) 
                next_s = next_states[np.random.randint(len(next_states))]
                path.append(next_s) # Add the next state to the path
                t +=1 # Update time and state for next iteration
                s = self.map[next_s]
                
        if method == 'ValIter': 
            t = 1 # Initialize current state, next state and time
            s = self.map[start]
            path.append(start) # Add the starting position in the maze to the path
            next_states = self.__move(s, policy[s]) # Move to next state given the policy and the current state
            next_s = next_states[np.random.randint(len(next_states))]
            path.append(next_s) # Add the next state to the path
            
            horizon = 20                              # Question e
            # Loop while state is not the goal state
            while s != next_s and t <= horizon:
                s = self.map[next_s] # Update state
                next_states = self.__move(s, policy[s]) # Move to next state given the policy and the current state
                next_s = next_states[np.random.randint(len(next_states))]
                path.append(next_s) # Add the next state to the path
                t += 1 # Update time for next iteration
        
        return [path, horizon] # Return the horizon as well, to plot the histograms for the VI


    def simulate_with_time(self, start, policy, method):
        
        if method not in methods:
            error = 'ERROR: the argument method must be in {}'.format(methods)
            raise NameError(error)

        path = list()
        
        if method == 'DynProg':
            horizon = policy.shape[1] # Deduce the horizon from the policy shape
            t = 0 # Initialize current time
            s = self.map[start] # Initialize current state 
            path.append(start) # Add the starting position in the maze to the path
            
            while t < horizon - 1:
                a = policy[s, t] # Move to next state given the policy and the current state

                next_states = self.__move(s, int(a)) 
                next_s = next_states[np.random.randint(len(next_states))]
                path.append(next_s) # Add the next state to the path
                t +=1 # Update time and state for next iteration
                s = self.map[next_s]
                
        if method == 'ValIter': 
            p=1/30
            t = 1 # Initialize current state, next state and time
            s = self.map[start]
            path.append(start) # Add the starting position in the maze to the path
            next_states = self.__move(s, policy[s,t-1]) # Move to next state given the policy and the current state
            next_s = next_states[np.random.randint(len(next_states))]
            path.append(next_s) # Add the next state to the path
            
            horizon = np.random.geometric(p)
            if horizon >= policy.shape[1]:
                horizon = policy.shape[1]-1                            # Question e
            # Loop while state is not the goal state
            while s != next_s and t < horizon:
                s = self.map[next_s] # Update state
                next_states = self.__move(s, policy[s,t]) # Move to next state given the policy and the current state
                next_s = next_states[np.random.randint(len(next_states))]
                path.append(next_s) # Add the next state to the path
                t += 1 # Update time for next iteration
        
        return [path, horizon] # Return the horizon as well, to plot the histograms for the VI



    def show(self):
        print('The states are :')
        print(self.states)
        print('The actions are:')
        print(self.actions)
        print('The mapping of the states:')
        print(self.map)
        print('The rewards:')
        print(self.rewards)



def dynamic_programming(env:Maze, horizon):
    """ Solves the shortest path problem using dynamic programming
        :input Maze env           : The maze environment in which we seek to
                                    find the shortest path.
        :input int horizon        : The time T up to which we solve the problem.
        :return numpy.array V     : Optimal values for every state at every
                                    time, dimension S*T
        :return numpy.array policy: Optimal time-varying policy at every state,
                                    dimension S*T
    """
    #TODO
    # première chose calculer V
    policy = np.zeros((env.n_states, horizon),dtype=int)
    V = np.zeros((env.n_states,horizon))
    V[env.n_states-1,:] = env.GOAL_REWARD # If we win
    V[env.n_states-2,:] = env.MINOTAUR_REWARD #if we get eaten
    #V[:,horizon-1] = env.MINOTAUR_REWARD # if we run out of time, can be changed
    for t in range(horizon-2, -1, -1):
        for state in range(env.n_states):
            transition_probabilities = env.transition_probabilities[state, :, :]
            next_states = np.unique(np.nonzero(transition_probabilities)[0])
            if len(next_states)!= 0:
                bellman_array = np.array([env.rewards[state, action]+
                                            sum(env.transition_probabilities[state, next_state, action]*V[next_state, t+1] for next_state in next_states) 
                                            for action in env.actions.keys()])
                V[state,t] = np.max(bellman_array)
                best_action = np.argmax(bellman_array)
                policy[state,t] = best_action
                # print(bellman_array)
        print(f'finished t={t}', flush=True)
    return V, policy

def value_iteration(env, gamma, epsilon):
    """ Solves the shortest path problem using value iteration
        :input Maze env           : The maze environment in which we seek to
                                    find the shortest path.
        :input float gamma        : The discount factor.
        :input float epsilon      : accuracy of the value iteration procedure.
        :return numpy.array V     : Optimal values for every state at every
                                    time, dimension S*T
        :return numpy.array policy: Optimal time-varying policy at every state,
                                    dimension S*T
    """
    #TODO
    V=np.zeros(env.n_states)
    V_new=np.zeros(env.n_states)
    policy=np.zeros(env.n_states)
    n=0
    delta=1000000
    max_iter=100
    while (n<max_iter and delta>epsilon*(1-gamma)/gamma):
        for state in range(env.n_states):
            transition_probabilities = env.transition_probabilities[state, :, :]
            next_states = np.unique(np.nonzero(transition_probabilities)[0])
            if len(next_states)!= 0:
                fixed_point_eq = np.array([env.rewards[state, action]+
                                            gamma*sum(env.transition_probabilities[state, next_state, action]*V[next_state] for next_state in next_states) 
                                            for action in env.actions.keys()])
                V_new[state]=np.max(fixed_point_eq)
                best_action = np.argmax(fixed_point_eq)
                policy[state] = best_action
        delta=np.sum(np.abs(V-V_new))
        V=np.copy(V_new)
        n+=1
        print('done',n,'iter(s)', 'delta =',delta)
    return V, policy

def value_iteration_with_time(env, gamma, epsilon, time=100):
    """ Solves the shortest path problem using value iteration
        :input Maze env           : The maze environment in which we seek to
                                    find the shortest path.
        :input float gamma        : The discount factor.
        :input float epsilon      : accuracy of the value iteration procedure.
        :return numpy.array V     : Optimal values for every state at every
                                    time, dimension S*T
        :return numpy.array policy: Optimal time-varying policy at every state,
                                    dimension S*T
    """
    #TODO
    V=np.zeros((env.n_states, time))
    V_new=np.zeros((env.n_states, time))
    policy=np.zeros((env.n_states, time))
    n=0
    p = 1/30
    q = 1-p
    delta=1_000_000
    max_iter=60
    while (n<max_iter and delta>epsilon*(1-gamma)/gamma):
        for t in range(time-2, -1, -1):
            for state in range(env.n_states):
                transition_probabilities = env.transition_probabilities[state, :, :]
                next_states = np.unique(np.nonzero(transition_probabilities)[0])
                if len(next_states)!= 0:
                    fixed_point_eq = np.array([env.rewards[state, action]+
                                                gamma*sum((q**t)*env.transition_probabilities[state, next_state, action]*V[next_state,t+1] for next_state in next_states) 
                                                for action in env.actions.keys()])
                    V_new[state,t]=np.max(fixed_point_eq)
                    best_action = np.argmax(fixed_point_eq)
                    policy[state,t] = best_action
            if t%10 ==0:print(t)
        delta=np.sum(np.sum(np.abs(V-V_new)))
        V=np.copy(V_new)
        n+=1
        print('done',n,'iter(s)', 'delta =',delta)
    return V, policy

def animate_solution(maze, path, save=False):

    # Map a color to each cell in the maze
    col_map = {0: WHITE, 1: BLACK, 2: LIGHT_GREEN, -1: LIGHT_RED, -2: LIGHT_PURPLE}
    
    rows, cols = maze.shape # Size of the maze
    fig = plt.figure(1, figsize=(cols, rows)) # Create figure of the size of the maze

    # Remove the axis ticks and add title
    ax = plt.gca()
    ax.set_title('Policy simulation')
    ax.set_xticks([])
    ax.set_yticks([])

    # Give a color to each cell
    colored_maze = [[col_map[maze[j, i]] for i in range(cols)] for j in range(rows)]

    # Create a table to color
    grid = plt.table(
        cellText = None, 
        cellColours = colored_maze, 
        cellLoc = 'center', 
        loc = (0,0), 
        edges = 'closed'
    )
    
    # Modify the height and width of the cells in the table
    tc = grid.properties()['children']
    for cell in tc:
        cell.set_height(1.0/rows)
        cell.set_width(1.0/cols)

    for i in range(0, len(path)):
        if path[i-1] != 'Eaten' and path[i-1] != 'Win':
            grid.get_celld()[(path[i-1][0])].set_facecolor(col_map[maze[path[i-1][0]]])
            grid.get_celld()[(path[i-1][1])].set_facecolor(col_map[maze[path[i-1][1]]])
        if path[i] != 'Eaten' and path[i] != 'Win':
            grid.get_celld()[(path[i][0])].set_facecolor(col_map[-2]) # Position of the player
            grid.get_celld()[(path[i][1])].set_facecolor(col_map[-1]) # Position of the minotaur
        display.display(fig)
        time.sleep(0.1)
        display.clear_output(wait = True)
        if save:
            plt.savefig(str(i)+'.png')



if __name__ == "__main__":
    # Description of the maze as a numpy array
    maze = np.array([
        [0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0, 1, 1, 1],
        [0, 0, 1, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 1, 2, 0, 0]])
    # With the convention 0 = empty cell, 1 = obstacle, 2 = exit of the Maze
    
    env = Maze(maze) # Create an environment maze
    horizon = 20       # TODO: Finite horizon

    # Solve the MDP problem with dynamic programming
    # Simulate the shortest path starting from position A
    # method = 'DynProg'
    # method='ValIter'
    start  = ((0,0), (6,5))
    # V, policy = value_iteration_with_time(env,0.7, 0.01)
    # path = env.simulate_with_time(start, policy, method)[0]
    
    # V, policy = dynamic_programming(env, 30)
    # V, policy = value_iteration(env, 0.7, 0.11)
    # max_horizon = 30
    # proba = np.zeros(max_horizon)
    # for horizon in range(1,max_horizon+1):
    #     print('horizon =', horizon)
    #     V, policy = dynamic_programming(env, horizon)
    #     for i in range(100):
    #         path = env.simulate(start, policy, method)[0]
    #         if 'Win' in path:
    #             proba[horizon-1] +=1
    # animate_solution(maze, path)
    # plt.plot(proba, color='black')
    # plt.xlabel('Horizon')
    # plt.ylabel('Winning percentage for 100 games')
    # formatter = FuncFormatter(to_percent)
    # plt.gca().yaxis.set_major_formatter(formatter)

    # # Afficher le graphique
    # plt.show()

