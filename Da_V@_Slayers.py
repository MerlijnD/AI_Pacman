
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

# -=-=-=- Team creation -=-=-=-

def createTeam(firstIndex, secondIndex, isRed,
               first = 'ChonkyBoy', second = 'ChonkyBoy'):

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

#  -=-=-=- Agents -=-=-=-

class ChonkyBoy(CaptureAgent):

  def registerInitialState(self, gameState):
    """
      NOTE: Dit wordt als init 1x gerunned. Voor ons belangrijk voor mogelijk:
        - Default parameters init
          - alpha:    learning rate
          - epsilon:  exploration rate
          - gamma:    discount factor
        - Welke kleur we zijn?
        - De algemene enviroment uitlezen?
    """
    
    self.epsilon = 0.05
    self.gamma = 0.8
    self.alpha = 0.2
    self.numTraining = 0
    self.observationHistory = []
    self.QValue = util.Counter()
    
    # f = open('./Da_V@_Slayers.py', 'r')
    # content = f.read()
    # print(content)
    # f.close()
    self.env = self.FriendlyFood(gameState)
    print(self.env)
    
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
    # new_env = self.UpdateEnvironment(gameState, self.env)
    
    Possible_Actions = gameState.getLegalActions(self.index)
    """
      Voorspel de beste Actie die daarna gegeven kan worden.
      Nu is dat een random actie van de list "Possible_Actions"
    """
    
    return random.choice(Possible_Actions)
    

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
      Friendly_capsules = gameState.getRedCapsules()
    else:
      Friendly_capsules = gameState.getBlueCapsules()
    
    Pac_Pos = gameState.getAgentPosition(self.index)
    Pac_Pos = list(Pac_Pos)
    Normal_Friendly_capsules = [0,0]
    Normal_Friendly_capsules[0] = Pac_Pos[0] - Friendly_capsules[0][0]
    Normal_Friendly_capsules[1] = Pac_Pos[1] - Friendly_capsules[0][1]

    return Normal_Friendly_capsules

  def EnemyCapsules(self, gameState):
    # [a, Q(s,a) for a in s.getlegalactions]
  
    if gameState.isOnRedTeam(self.index):
      Friendly_capsules = gameState.getBlueCapsules()
    else:
      Friendly_capsules = gameState.getRedCapsules()
    
    Pac_Pos = gameState.getAgentPosition(self.index)
    Pac_Pos = list(Pac_Pos)
    Normal_Friendly_capsules = [0,0]
    Normal_Friendly_capsules[0] = Pac_Pos[0] - Friendly_capsules[0][0]
    Normal_Friendly_capsules[1] = Pac_Pos[1] - Friendly_capsules[0][1]
    print(Normal_Friendly_capsules)
    return Normal_Friendly_capsules
      
  
  def getEnvironment(self, gameState):
    """
      Returned 2D-numpy array (datatype: str) met alle belangrijke init environment info:
        - Walls         = 'W'
        - Food          = 'FF, EF'
        - powercapsule  = 'FP, EP'
        - Empty space   = '_'
        - Agent         = 'A, FA'
    """
    
    # Krijg de locatie van de walls en stops ze in de array
    env = gameState.getWalls()
    cop_env = []
    for r in env:       # Voor elke row in env
      cop_env.append(r)
    np_env = np.array(cop_env).astype(str)
    
    # Intereer over de np array en verrander de values
    np_env[np_env == "True"] = "W"
    np_env[np_env == "False"] = "_"
    

    # Krijg de locatie van de power capsules, en voeg toe aan np_env
    Is_red = gameState.isOnRedTeam(self.index)
    R_caps = gameState.getRedCapsules()
    B_caps = gameState.getBlueCapsules()
    
    for r in R_caps:
      if(Is_red):
        np_env[r[0]][r[1]] = "FP"
      else:
        np_env[r[0]][r[1]] = "EP"
    
    for r in B_caps:
      if(Is_red == 0):
        np_env[r[0]][r[1]] = "FP"
      else:
        np_env[r[0]][r[1]] = "EP"
    
    # Krijg de locatie van alle food
    R_food = gameState.getRedFood()
    B_food = gameState.getBlueFood()
    cop_env_R_food = []
    cop_env_B_food = []
    
    
    for r in R_food:
      cop_env_R_food.append(r)
    np_env_R_food = np.array(cop_env_R_food).astype(str)

    for r in B_food:
      cop_env_B_food.append(r)
    np_env_B_food = np.array(cop_env_B_food).astype(str)
    
    # Intereer over de np array en verrander de values
    solutions1 = np.argwhere(np_env_R_food == "True")
    for p in solutions1:
      if(Is_red):
        np_env[p[0]][p[1]] = "1"
      else:
        np_env[p[0]][p[1]] = "0"
        
    solutions2 = np.argwhere(np_env_B_food == "True")
    for p in solutions2:
      if(Is_red == 0):
        np_env[p[0]][p[1]] = "1"
      else:
        np_env[p[0]][p[1]] = "0"

    
    # Krijg positie van Agent
    pos = gameState.getAgentPosition(self.index)
    np_env[pos[0]][pos[1]] = "A"
    
    # Je kan deze print aanzetten voor debugging / check hoe de env er uit ziet.
    print(np_env)
    
    return np_env
  
  def UpdateEnvironment(self, gameState, np_env):
    # Updates agent data in the env
    np_env[np_env == "A"] = "_"
    
    pos = gameState.getAgentPosition(self.index)
    np_env[pos[0]][pos[1]] = "A"
    
    return np_env
  