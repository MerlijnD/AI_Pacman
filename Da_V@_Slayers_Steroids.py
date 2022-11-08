''' Vragen aan Patrick en/of Julian:
1. Comments in het engels of nederlands?
2. Hoe werkt het met dezelfde variabelen in loops?
3. 
'''


# Dit is de Reinforcement Learning agent, mogelijk kunnen we ook een Evolutionary Alghorithm maken?
# Om de file te runnen kan de de volgende command gebruiken:
# python .\capture.py -r baselineTeam -b Da_V@_Slayers
CONTACT = 'mart.veldkamp@hva.nl', 'merlijn.dascher@hva.nl'

# Import the necessary libraries
from captureAgents import CaptureAgent
import random, util
from game import Directions

# -=-=-=- Team creation -=-=-=-
def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveChock', second = 'DefensiveChonk'):

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

# Build a few empty lists which can later be called on globally so they can be used by all classes
tunnels = []
defensiveTunnels = []
walls = []

def getTunnels(legalPositions):
  """
  Search the map and find all tunnels. Tunnels are basically dead end places a packman can get 
  cornered in which means we want to 
  """
  tunnels = []
  while len(tunnels) != len(moreTunnels(legalPositions, tunnels)):
    tunnels = moreTunnels(legalPositions, tunnels)
  return tunnels

def moreTunnels(legalPositions, tunnels):
  newTunnels = tunnels
  for legal in legalPositions:
    num1 = 0
    num2 = 0
    x, y = legal
    if (x + 1, y) in tunnels:
      num1 += 1
    if (x + 1, y) in tunnels:
      num1 += 1
    if (x + 1, y) in tunnels:
      num1 += 1
    if (x + 1, y) in tunnels:
      num1 += 1
    x, y = legal
    if (x + 1, y) in legalPositions:
      num2 += 1
    if (x + 1, y) in legalPositions:
      num2 += 1
    if (x + 1, y) in legalPositions:
      num2 += 1
    if (x + 1, y) in legalPositions:
      num2 += 1
    if num2 - num1 == 1 and legal not in tunnels:
      newTunnels.append(legal)
    num1 = 0
    num2 = 0
  return newTunnels

def nextPosition(pos, action):
  x, y = pos
  if action == Directions.NORTH:
    return (x, y + 1)
  if action == Directions.EAST:
    return (x + 1, y)
  if action == Directions.SOUTH:
    return (x, y - 1)
  if action == Directions.WEST:
    return (x - 1, y)
  return pos
  
def getCurrentPosTunnel(pos, tunnels):
  if pos not in tunnels:
    return None
  queue = util.Queue()
  queue.push(pos)
  empty = []
  while not queue.isEmpty():
    currentPos = queue.pop()
    if currentPos not in empty:
      empty.append(currentPos)
      successorPos = getSuccsorsPos(currentPos, tunnels)
      for succPos in successorPos:
        if succPos not in empty:
          queue.push(succPos)

def getSuccsorsPos(pos, legalPositions):
  succsorPos = []
  x, y = pos
  if (x + 1, y) in legalPositions:
    succsorPos.append((x + 1, y))
  if (x + 1, y) in legalPositions:
    succsorPos.append((x - 1, y))
  if (x + 1, y) in legalPositions:
    succsorPos.append((x, y + 1))
  if (x + 1, y) in legalPositions:
    succsorPos.append((x, y - 1))
  return succsorPos

def getTunnelEntrance(pos, tunnels, legalPositions):
  if pos not in tunnels:
    return None
  currentTunnel = getCurrentPosTunnel(pos, tunnels)
  for tnl in currentTunnel:
    entrance = getCurrentPosTunnel(tnl, tunnels, legalPositions)
    if entrance != None:
      return entrance

class Filter:

  def __init__(self, agent, gameState):

    self.start = gameState.getInitialAgentPosition(agent.index)
    self.agent = agent
    self.middle = gameState.data.layout.width / 2
    self.legalPositions = []
    self.enemies = self.agent.getOpponents(gameState)
    self.guesses = {}

    for noWall in gameState.getWalls().asList(False):
      self.legalPositions.append(noWall)

    for enemy in self.enemies:
      self.guesses[enemy] = util.Counter()
      self.guesses[enemy][gameState.getInitialAgentPosition(enemy)] = 1.0
      self.guesses[enemy].normalize()

  def guessEnemyPos(self):

    for enemy in self.enemies:
      distance = util.Counter()

      for legal in self.legalPositions:
        newDistance = util.Counter()

        allPos = [(legal[0] + i, legal[1] + j) for i in [-1,0,1] for j in [-1,0,1] if not (abs(i) == 1 and abs(j) == 1)]

        for legalPos in self.legalPositions:
          if legalPos in allPos:
            newDistance[legalPos] = 1.0
        newDistance.normalize()

        for pos, probability in newDistance.items():
          distance[pos] = distance[pos] + self.guesses[self.enemy][pos] * probability

      distance.normalize()
      self.guesses[enemy] = distance

  def lookAround(self, agent, gameState):

    myPos = gameState.getAgentPosition(agent.index)
    noisyDistance = gameState.getAgentDistances()

    distance = util.Counter()

    for enemy in self.enemies:
      for legal in self.legalPositions:

        manhattan = util.manhattanDistance(myPos, legal)
        probability = gameState.getDistanceProb(manhattan, noisyDistance)

        if agent.red:
          ifPacman = legal[0] < self.middle
        else:
          ifPacman = legal[0] > self.middle

        if manhattan <= 6 or ifPacman != gameState.getAgentState(enemy).isPacman:
          distance[legal] = 0.0
        else:
          distance[legal] = self.guesses[enemy][legal] * probability

      distance.normalize()
      self.guesses[enemy] = distance

  def possiblePos(self, enemy):
    pos = self.guesses[enemy].argMax()
    return pos

#  -=-=-=- Agents -=-=-=-
class reflexCaptureAgent(CaptureAgent):

  def registerInitialState(self, gameState):

    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

    global walls 
    global tunnels
    global freeRoam
    global legalPositions
    global defensiveTunnels

    self.changeEntry = False
    self.nextEntry = None
    self.tunnelEntry = None
    self.capsules = None
    self.nearestSafeFood = None
    self.nearestTunnelFood = None
    self.goToEdge = None
    self.foodEatenByEnemy = None
    self.ifStuck = False
    self.invaderGuess = False

    self.carryFood = 0
    self.stuckStep = 0

    walls = gameState.getWalls().asList()
    width = gameState.data.layout.width
    
    if len(tunnels) == 0:
      legalPositions = []
      for noWall in gameState.getWalls().asList(False):
        legalPositions.append(noWall)
      tunnels = getTunnels(legalPositions)
      freeRoam = list(set(legalPositions).difference(set(tunnels)))

    legalRed = []
    for pos in legalPositions:
      if pos[0] < width / 2:
        legalRed.append(pos)

    legalBlue = []
    for pos in legalPositions:
      if pos[0] >= width / 2:
        legalBlue.append(pos)

    self.enemyGuess = Filter(self, gameState)

    if len(defensiveTunnels) == 0:
      if self.red:
        defensiveTunnels = getTunnels(legalRed)
      else:
        defensiveTunnels = getTunnels(legalBlue)

  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    values = []
    for action in actions:
      values.append(self.evaluate(gameState, action))
    
    Qvalue = max(values)

    bestActions = []

    for action, value in zip(actions, values):
      if value == Qvalue:
        bestActions.append(action)

    if len(self.getFood(gameState).asList()) <= 2:
      bestDistance = float("inf")
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        newPos = successor.getAgentPosition(self.index)
        distance = self.getMazeDistance(self.start, newPos)
        if distance < bestDistance:
          bestActions = action
          bestDistance = distance
      return bestActions

    choice = random.choice(bestActions)

    return choice

  def getSuccessor(self, gameState, action):

    successor = gameState.generateSuccessor(self.index, action)
    position = successor.getAgentState(self.index).getPosition()
    
    if position != util.nearestPoint(position):
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):

    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)

    return features * weights

  def checkIfTunnelEmpty(self, gameState, successor):
    currentPos = gameState.getAgentState(self.index).getPosition()
    successorPos = successor.getAgentState(self.index).getPosition()
    if currentPos not in tunnels and successorPos in tunnels:
      self.tunnelEntry = currentPos

      stack = util.Stack()
      stack.push((successorPos, 1))

      empty = []

      while not stack.isEmpty():
        (x, y), length = stack.pop()
        if self.getFood(gameState)[x][y]:
          return length
        
        if (x, y) not in empty:
          empty.append((x, y))
          successorPos = getSuccsorsPos((x, y), tunnels)
          for pos in successorPos:
            if pos not in empty:
              continuity = length + 1
              stack.push((pos, continuity))
    return 0

  def getFoodFromTunnel(self, gameState):

    currentPos = gameState.getAgentState(self.index).getPosition()
    stack = util.Stack()
    stack.push(currentPos)

    empty = []

    while not stack.isEmpty():
      x, y = stack.pop()
      if self.getFood(gameState)[x][y]:
        return (x, y)

      if (x, y) not in empty:
        empty.append((x, y))
        successorPos = getSuccsorsPos((x, y), tunnels)

        for pos in successorPos:
          if pos not in empty:
            stack.push(pos)
    return None

  def getEntrance(self, gameState):
    width = gameState.data.layout.width
    legalPositions = []
    legalRed = []
    legalBlue = []
    redEntry = []
    blueEntry = []

    for noWall in gameState.getWalls().asList(False):
      legalPositions.append(noWall)

    for legalR in legalPositions:
      if legalR[0] == width / 2 - 1:
        legalRed.append(legalR)
    
    for legalB in legalPositions:
      if legalB[0] == width / 2:
        legalBlue.append(legalB)

    for i in legalRed:
      for j in legalBlue:
        if i[0] + 1 == j[0] and i[1] == j[1]:
          redEntry.append(i)
          blueEntry.append(j)
    if self.red:
      return redEntry
    else:
      return blueEntry

class OffensiveChock(reflexCaptureAgent):

  def getFeatures(self, gameState, action):

    enemies = []
    ghosts = []
    scaredGhosts = []
    activeGhosts = []
    freeRoamFood = []
    tunnelFood = []
    
    successor = self.getSuccessor(gameState, action)
    currentPos = gameState.getAgentState(self.index).getPosition()
    newPos = successor.getAgentState(self.index).getPosition()
    nextPos = nextPosition(currentPos, action)
    currentFood = self.getFood(gameState).asList()
    capsules = self.getCapsules(gameState)
    emptyTunnel = self.checkIfTunnelEmpty(gameState, successor)

    features = util.Counter()
    features["successorScore"] = self.getScore(successor)

    # make lists
    for opponent in self.getOpponents(gameState):
      enemies.append(gameState.getAgentState(opponent))

    for enemy in enemies:
      if not enemy.isPacman and enemy.getPosition() is not None and util.manhattanDistance(currentPos, enemy.getPosition()) <= 5:
        ghosts.append(enemy)
    
    for scared in ghosts:
      if scared.scaredTimer > 1:
        scaredGhosts.append(scared)
    
    for ghost in ghosts:
      if ghost not in scaredGhosts:
        activeGhosts.append(ghost)

    for food in currentFood:
      if food not in tunnels:
        freeRoamFood.append(food)

    for tFood in currentFood:
      if tFood in tunnels:
        tunnelFood.append(tFood)

    # 1
    if len(ghosts) == 0:
      self.capsule = None
      self.nextOpenFood = None
      self.nextTunnelFood = None

    # 2 
    if gameState.getAgentState(self.index).isPacman:
      self.changeEntrance = False

    # 3
    if nextPos in currentFood:
      self.carriedDot += 1
    if not gameState.getAgentState(self.index).isPacman:
      self.carriedDot = 0

    # 6
    if len(currentFood) < 3:
      features["return"] = self.getHomeDistance(successor)

    # 7
    if len(activeGhosts) > 0 and len(currentFood) >= 3:
      distances = []
      ghostPos = []
      succPos = []

      for aGhost in activeGhosts:
        distances.append(self.getMazeDistance(newPos, aGhost.getPosition()))

      minDist = min(distances)

      for acGhost in activeGhosts:
        ghostPos.append(acGhost.getPosition())

      features["ghostDist"] = minDist

      if nextPos in ghostPos:
        features["dead"] = 1
      
      for ghostP in ghostPos:
        succPos.append(getSuccsorsPos(ghostP, legalPositions))

      if nextPos in ghostPos[0]:
        features["dead"] = 1

      if len(freeRoamFood) > 0:
        freeRoamFoodFeatures = []

        for fRF in freeRoamFood:
          freeRoamFoodFeatures.append(self.getMazeDistance(nextPos, fRF))

        features["freeRoamFood"] = min(freeRoamFoodFeatures)

        if nextPos in freeRoamFood:
          features["freeRoamFood"] = -1
        
      elif len(freeRoamFood) == 0:
        features["return"] = self.getHomeDistance(successor)

    # 8
    if len(activeGhosts) > 0 and len(currentFood) >= 3:

      if len(freeRoamFood) > 0:
        
        safeFood = []
        nearGhostPos = []

        for fod in freeRoamFood:

          for actGhost in activeGhosts:
            nearGhostPos.append(self.getMazeDistance(actGhost.getPosition(), fod))

          if self.getMazeDistance(currentPos, fod) < min(nearGhostPos):
            safeFood.append(fod)

        if len(safeFood) != 0:

          closestFoodDist = []
          for foood in safeFood:
            closestFoodDist.append(self.getMazeDistance(currentPos, foood))

          for fd in safeFood:
            if self.getMazeDistance(currentPos, fd) == min(closestFoodDist):
              self.nextOpenFood = fd
              break

    # 9
    if len(activeGhosts) > 0 and len(tunnelFood) > 0 and len(scaredGhosts) == 0 and len(currentFood) > 2:
      safeTunnelFood = []
      for tFood in tunnelFood:
        tunnelEntry = getTunnelEntrance(tFood, tunnels, legalPositions)
        tunnelFoodDistance = self.getMazeDistance(currentPos, tFood) + self.getMazeDistance(tFood, tunnelEntry)
        for activeGho in activeGhosts:
          if tunnelFoodDistance < min(self.getMazeDistance(activeGho.getPosition(), tunnelEntry)):
            safeTunnelFood.append(tFood)
      if len(safeTunnelFood) > 0:
        closestTunnelFoodDist = []
        for sTF in safeTunnelFood:
          closestTunnelFoodDist.append(self.getMazeDistance(currentPos, sTF))
          if self.getMazeDistance(currentPos, sTF) == min(closestTunnelFoodDist):
            self.nextTunnelFood = sTF
            break

    # 10
    if self.nextOpenFood != None:
      features["goToSafeFood"] = self.getMazeDistance(nextPos, self.nextOpenFood)
      if nextPos == self.nextOpenFood:
        features["goToSafeFood"] = 0
        self.nextOpenFood = None

    # 11
    if features["goToSafeFood"] == 0 and self.nextTunnelFood != None:
      features["goToSafeFood"] = self.getMazeDistance(nextPos, self.nextTunnelFood)
      if nextPos == self.nextTunnelFood:
        features["goToSafeFood"] = 0
        self.nextTunnelFood = None

    # 12
    if len(activeGhosts) > 0 and len(capsules) != 0:
      for cap in capsules:
        actGhos = []
        for aG in activeGhosts:
          actGhos.append(self.getMazeDistance(cap, aG.getPosition()))
        if self.getMazeDistance(currentPos, cap) < min(actGhos):
          self.capsules = cap

    # 13
    if len(scaredGhosts) > 0 and len(capsules) != 0:
      for ca in capsules:
        scaGhosts = []
        for sG in scaredGhosts:
          scaGhosts.append(self.getMazeDistance(ca, sG.getPosition()))
        if self.getMazeDistance(currentPos, ca) >= scaredGhosts[0].scaredTimer and self.getMazeDistance(currentPos, ca) < min(scaGhosts):
          self.capsules = ca

    # 14
    if currentPos in tunnels:
      for c in capsules:
        if c in getCurrentPosTunnel(currentPos, tunnels):
          self.capsules = c

    # 15
    if self.capsules != None:
      features["capsuleDistance"] = self.getMazeDistance(nextPos, self.capsules)
      if nextPos == self.capsules:
        features["capsuleDistance"] = 0
        self.capsules = None

    # 16
    if len(activeGhosts) == 0 and nextPos in capsules:
      features["leaveCapsule"] = 0.1

    # 17
    if action == Directions.STOP:
      features["stop"] = 1

    # 18
    if successor.getAgentState(self.index).isPacman and currentPos not in tunnels and successor.getAgentState(self.index).getPosition() in tunnels and emptyTunnel == 0:
      features["noFoodInTunnel"] = -1

    # 19
    if len(activeGhosts) > 0:
      disAG = []
      for acG in activeGhosts:
        disAG.append(self.getMazeDistance(currentPos, acG.getPosition()))
      if emptyTunnel != 0 and emptyTunnel * 2 >= min(disAG) - 1:
        features["wasteAction"] = -1

    # 20
    if len(scaredGhosts) > 0:
      disSG = []
      for scG in scaredGhosts:
        disSG.append(self.getMazeDistance(currentPos, scG.getPosition()))
      if emptyTunnel != 0 and emptyTunnel * 2 >= scaredGhosts[0].scaredTimer -1:
        features["wasteAction"] = -1

    # 26
    if self.nextEntry != None and features["goToSafeFood"] == 0:
      features["goToNextEntrance"] = self.getMazeDistance(nextPos, self.nextEntrance)

    # 4
    if len(activeGhosts) == 0 and len(currentFood) >- 3:
      nearestFood = []
      for f in currentFood:
        nearestFood.append(self.getMazeDistance(nextPos, f))
      features["distToSafeFood"] = min(nearestFood)
      if nextPos in self.getFood(gameState).asList():
        features["distToSafeFood"] = -1

    return features

  def getWeights(self, gameState, action):
    return {"successorScore": 1,"return": -1, "ghostDist": -10, "dead": -1000, "freeRoamFood": -3, "goToSafeFood": -10, "distToSafeFood": -2,
    "capsuleDistance": -1000, "leaveCapsule": -1,"stop": -50,"noFoodInTunnel": 100,"wasteAction": 100,"goToNextEntrance": -1000}

  def getHomeDistance(self, gameState):
    curPos = gameState.getAgentState(self.index).getPosition()
    width = gameState.data.layout.width
    
    legalPositions = []
    legalRed = []
    legalBlue = []

    for noWall in gameState.getWalls().asList(False):
      legalPositions.append(noWall)

    for legalR in legalPositions:
      if legalR[0] == width / 2 - 1:
        legalRed.append(legalR)

    for legalB in legalPositions:
      if legalB[0] == width / 2:
        legalBlue.append(legalB)

    if self.red:
      distanceR = []
      for lRed in legalRed:
        distanceR.append(self.getMazeDistance(curPos, lRed))
      return min(distanceR)
    
    else:
      distanceB = []
      for lBlue in legalBlue:
        distanceB.append(self.getMazeDistance(curPos, lBlue))
      return min(distanceB)

class DefensiveChonk(reflexCaptureAgent):
  
  def getFeatures(self, gameState, action):

    features = util.Counter()

    successor = self.getSuccessor(gameState, action)
    currentState = gameState.getAgentState(self.index)
    currentPos = currentState.getPosition()
    successorState = successor.getAgentState(self.index)
    successorPos = successorState.getPosition()
    capsules = self.getCapsulesYouAreDefending(gameState)

    curEnemies = []
    nextEnemies = []
    curInvaders = []
    nextInvaders = []

    for opp in self.getOpponents(gameState):
      curEnemies.append(gameState.getAgentState(opp))

    for oppSucc in self.getOpponents(successor):
      nextEnemies.append(successor.getAgentState(oppSucc))

    for curInv in curEnemies:
      if curInv.isPacman and curInv.getPosition() != None:
        curInvaders.append(curInv)

    for nextInv in nextEnemies:
      if nextInv.isPacman and nextInv.getPosition() != None:
        nextInvaders.append(nextInv)

    features["defending"] = 100
    if successorState.isPacman: 
      features["defending"] = 0

    if self.goToEdge == None:
      features["goToEdge"] = self.getEdgeDistance(successor)

    if self.getEdgeDistance(successor) <= 2:
      self.goToEdge = 0

    if self.invaderGuess:
      self.enemyGuess.lookAround(self, gameState)
      enemyPos = self.enemyGuess.possiblePos(curInvaders[0])
      features["goToTunnel"] = self.getMazeDistance(enemyPos, successorPos)
      self.enemyGuess.guessEnemyPos()
    
    if self.blockTunnel(curInvaders, currentPos, capsules) and currentState.scaredTimer == 0:
      features["goToTunnel"] = self.getMazeDistance(getTunnelEntrance(curInvaders[0].getPosition(), tunnels, legalPositions), successorPos)
      return features

    if currentPos in defensiveTunnels and len(curInvaders) == 0:
      features["getOutOfTunnel"] = self.getMazeDistance(self.start, successorPos)

    features["invaders"] = len(nextInvaders)

    if len(curInvaders) == 0 and not successorState.isPacman and currentState.scaredTimer == 0:
      if currentPos not in defensiveTunnels and successorPos in defensiveTunnels:
        features["wastedAction"] = -1

    if len(nextInvaders) > 0 and currentState.scaredTimer != 0:
      dist = []
      for inv in nextInvaders:
        dist.append(self.getMazeDistance(successorPos, inv.getPosition()))
      features["chase"] = (min(dist) - 2) * (min(dist) - 2)
      if currentPos not in defensiveTunnels and successorPos in defensiveTunnels:
        features["wastedAction"] = -1

    if action == Directions.STOP: 
      features["stop"] = 1

    if self.getPreviousObservation() != None:
      if len(nextInvaders) == 0 and self.lostFood() != None:
        self.foodEatenByEnemy = self.lostFood()

      if self.foodEatenByEnemy != None and len(nextInvaders) == 0:
        features["murder"] = self.getMazeDistance(successorPos, self.foodEatenByEnemy)

      if successorPos == self.foodEatenByEnemy or len(nextInvaders) > 0:
        self.foodEatenByEnemy = None

    return features


  def getWeights(self, gameState, action):
    return {"defending": 10, "goToEdge": -2, "goToTunnel": -10, "getOutOfTunnel": -0.1,
    "Invaders": -100, "wastedAction": 200,  "chase": -100, "stop": -100, "murder": -1}

  def getEdgeDistance(self, gameState):

    curPos = gameState.getAgentState(self.index).getPosition()
    width = gameState.data.layout.width

    legalPositions = []
    legalRed = []
    legalBlue = []

    for noWall in gameState.getWalls().asList(False):
      legalPositions.append(noWall)

    for legalR in legalPositions:
      if legalR[0] == width / 2 - 1:
        legalRed.append(legalR)

    for legalB in legalPositions:
      if legalB[0] == width / 2:
        legalBlue.append(legalB)

    if self.red:
      distanceR = []
      for lRed in legalRed:
        distanceR.append(self.getMazeDistance(curPos, lRed))
      return min(distanceR)

    else:
      distanceB = []
      for lBlue in legalBlue:
        distanceB.append(self.getMazeDistance(curPos, lBlue))
      return min(distanceB)

  def blockTunnel(self, curInvaders, currentPos, curCapsule):
    if len(curInvaders) == 1:
      invaderPos = curInvaders[0].getPosition()
      if invaderPos in tunnels:
        tunnelEntrance = getTunnelEntrance(invaderPos, tunnels, legalPositions)
        if self.getMazeDistance(tunnelEntrance, currentPos) <= self.getMazeDistance(tunnelEntrance, invaderPos):
          if curCapsule not in getCurrentPosTunnel(invaderPos, tunnels):
            return None
    return False

  def lostFood(self):
    previousObservation = self.getPreviousObservation()
    currentObservation = self.getCurrentObservation()
    previousFood = self.getFoodYouAreDefending(previousObservation).asList()
    currentFood = self.getFoodYouAreDefending(currentObservation).asList()

    if len(currentFood) < len(previousFood):
      for lost in previousFood:
        if lost not in currentFood:
          return lost
    return None