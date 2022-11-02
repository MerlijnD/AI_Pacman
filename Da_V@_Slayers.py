
# Dit is de Reinforcement Learning agent, mogelijk kunnen we ook een Evolutionary Alghorithm maken?
# Om de file te runnen kan de de volgende command gebruiken:
# python .\capture.py -r baselineTeam -b Da_V@_Slayers
CONTACT = 'mart.veldkamp@hva.nl', 'merlijn.dascher@hva.nl'

from msilib.schema import Environment
from sre_parse import State
import string
from tkinter import Y
from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense
from tensorflow.keras.optimizers import Adam

# -=-=-=- Team creation -=-=-=-

def createTeam(firstIndex, secondIndex, isRed,
               first = 'ChonkyBoy', second = 'ChonkyBoy'):

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

#  -=-=-=- Agents -=-=-=-

class ChonkyBoy(CaptureAgent):

  # NOTE: Dit wordt als init 1x gerunned. Voor ons belangrijk voor mogelijk:
  def registerInitialState(self, gameState):
    
    self.state_size = len(self.calc_state_size(gameState)) # walls, food, pac-man loc in vizier, hoeveel food heeft pac-man, time left, current score
    self.action_size = 5
     
    self.memory = list() # maxlen=2000
    
    self.gamma = 0.95
    
    self.epsilon = 1.0
    self.epsilon_decay = 0.995
    self.epsilon_min = 0.01
    
    self.learning_rate = 0.001
    
    self.model = self._build_model_()
    
    # self.env = self.FriendlyFood(gameState)
    # print(self.env)
    # self.caps = self.FriendlyCapsules(gameState)
    # print(self.caps)
    # self.walls_temp = self.WallsNormalization(gameState)
    # print(self.walls_temp)
    
    CaptureAgent.registerInitialState(self, gameState)
  
  # NOTE: Dit wordt herhaald gerunned, nu zijn beide agents deze class
  def chooseAction(self, gameState): 
    
    # Dit is de stappen die je moet zetten om een Reinforcement Learning (vgm)
    """ 
      Geef een Reward / Q-value.
      indien er een punt is gepakt, terug gebracht, etc...
      of pac-man is gegeten (als ghost zijnde)
      Of General Gamestates zoals in het midden van het veld zich bevinden
    """

    """
      Krijg de state van le ChonkyBoy 
      (Dit kan alle relevante informatie over het speelveld zijn)
      Alles wat we relevante informatie kunnen vinden
    """
    self.state = self.calc_state_size(gameState)
    """
      Voorspel de beste Actie die daarna gegeven kan worden.
      Nu is dat een random actie van de list "Possible_Actions"
    """
    if util.flipCoin(self.epsilon):
      action = random.choice(gameState.getLegalActions(self.index))
    else:
      action = self.model_predict(self.state)
    
    return action
    
  def _build_model_(self):
    model = Sequential()
    
    model.add(Dense(5, input_dim = self.state_size, activation='relu'))
    model.add(Dense(12, activation='relu'))
    model.add(Dense(24, activation='relu'))
    model.add(Dense(12, activation='relu'))
    model.add(Dense(5,  activation='relu'))
    model.add(Dense(self.action_size, activation='linear')) # maybe verranderen
    
    model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate)) # mse verranderen?
    
    return model

  def remember(self, state, action, reward, next_state, done):
    self.memory.append((state, action, reward, next_state, done))
  
  # returns best legal action
  def model_predict(self, state):
    act_values = self.model.predict(state)
    # Model predict output vergelijken met legal states, en bool list aanpassen
    return np.argmax(act_values[0])

  # returned all the relevant state info
  def calc_state_size(self, gameState):
    
    mylist = []
    mylist.append(int(gameState.isOnRedTeam(self.index)))
    mylist.append(int(gameState.getScore()))
    
    for distance in gameState.getAgentDistances():
      mylist.append(int(distance))
      print(distance)
    
    for x,y in self.WallsNormalization(gameState):
      mylist.append(int(x))
      mylist.append(int(y))
    
    
    
    # print(mylist)s
    return mylist

  # Train?
  def replay(self, batch_size):
    
    minibatch = random.sample(self.memory, batch_size)
    
    for state, action, reward, next_state, done in minibatch:
      target= reward
      if not done:
        target = (reward + self.gamma * np.amax(self.model.predict(next_state)[0]))
      target_f = self.model.predict(state)
      target_f[0][action] = target
      
      self.model.fit(state, target_f, epochs=1, verbose=0)
  
  def load(self, name):
    self.model.load_weights(name)
  
  def save(self, name):
    self.model.save_weights(name)

  def FriendlyFood(self, gameState):
    if gameState.isOnRedTeam(self.index):
      Friendly_food = gameState.getRedFood()
    else:
      Friendly_food = gameState.getBlueFood()
    
    Friendly_food_copy = []
    
    for row in Friendly_food:
      Friendly_food_copy.append(row)
    
    np_friendly_food = np.array(Friendly_food_copy).astype(bool)
    
    Food_coordinates = []
    row = 0
    column = 0
    
    for i in np_friendly_food:
      column = 0
      for j in i:
        if j == True:
          Food_coordinates.append((row, column))
        column += 1
      row += 1
    
    pacman_position = gameState.getAgentPosition(self.index)    
    
    Food_coordinates_norm = []

    for coordinate in Food_coordinates:
      Food_coordinates_norm.append(tuple(map(lambda i, j: i - j, coordinate, pacman_position)))

    return Food_coordinates_norm
  
  def EnemyFood(self, gameState):
    if gameState.isOnRedTeam(self.index):
      enemy_food = gameState.getBlueFood()
    else:
      enemy_food = gameState.getRedFood()
    
    Enemy_food_copy = []

    for row in enemy_food:
      Enemy_food_copy.append(row)

    np_enemy_food = np.array(Enemy_food_copy).astype(bool)

    Food_coordinates = []
    row = 0
    column = 0

    for i in np_enemy_food:
      column = 0
      for j in i:
        if j == True:
          Food_coordinates.append((row, column))
        column += 1
      row += 1
    
    pacman_position = gameState.getAgentPosition(self.index)

    Food_coordinates_norm = []

    for coordinate in Food_coordinates:
      Food_coordinates_norm.append(tuple(map(lambda i, j: i - j, coordinate, pacman_position)))

    return Food_coordinates_norm
  
  def FriendlyCapsules(self, gameState):
    # [a, Q(s,a) for a in s.getlegalactions]
  
    if gameState.isOnRedTeam(self.index):
      friendly_caps = gameState.getRedCapsules()
    else:
      friendly_caps = gameState.getBlueCapsules()
    
    pac_pos = gameState.getAgentPosition(self.index)
    
    normal_friendly_caps = []
    
    for coordinate in friendly_caps:
      normal_friendly_caps.append(tuple(map(lambda i, j: i - j, coordinate, pac_pos)))

    return normal_friendly_caps

  def EnemyCapsules(self, gameState):
    # [a, Q(s,a) for a in s.getlegalactions]
  
    if gameState.isOnRedTeam(self.index):
      enemy_caps = gameState.getBlueCapsules()
    else:
      enemy_caps = gameState.getRedCapsules()
    
    pac_pos = gameState.getAgentPosition(self.index)
    normal_enemy_caps = []
    
    for coordinate in enemy_caps:
      normal_enemy_caps.append(tuple(map(lambda i, j: i - j, coordinate, pac_pos)))
    
    return normal_enemy_caps
      
  def WallsNormalization(self, gameState):
    walls = gameState.getWalls()
    
    walls_copy = []
    
    for row in walls:
      walls_copy.append(row)
    
    np_walls = np.array(walls_copy).astype(bool)
    
    wall_coordinates = []
    row = 0
    column = 0
    
    for i in np_walls:
      column = 0
      for j in i:
        if j == True:
          wall_coordinates.append((row, column))
        column += 1
      row += 1
    
    pacman_position = gameState.getAgentPosition(self.index)    
    
    wall_coordinates_norm = []

    for coordinate in wall_coordinates:
      wall_coordinates_norm.append(tuple(map(lambda i, j: i - j, coordinate, pacman_position)))

    return wall_coordinates_norm
  