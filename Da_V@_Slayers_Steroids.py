# To run the file:
# python .\capture.py -r Da_V@_Slayers_Steroids.py -b {insert other team}
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
  cornered in. This means that when we are on the offence we want to avoid these places when 
  other pacman are nearby and on defence we want to corner the other pacman. 
  """

  # Make a variable tunnels to save all the found tunnels
  tunnels = []

  # Loop as long as there are no more tunnels
  while len(tunnels) != len(moreTunnels(legalPositions, tunnels)):
    tunnels = moreTunnels(legalPositions, tunnels)

  # Return a list of all found tunnels
  return tunnels

def moreTunnels(legalPositions, tunnels):
  """
  This function loops over all the valid positions a pacman can be in. It looks at the board and
  looks for all the places where the only way to go is back. It returns a list of the previous 
  tunnels with a new found one. 
  """
  
  # Save the already found tunnels
  newTunnels = tunnels

  # Loop over all the valid positions a pacman can be in
  for legal in legalPositions:

    # Set up variables to save how many directions a pacman can go to
    num1 = 0
    num2 = 0

    # Read the coordinates of the legal move
    x, y = legal

    # Check how many directions a pacman can go to in a found tunnels
    if (x + 1, y) in tunnels:
      num1 += 1
    if (x + 1, y) in tunnels:
      num1 += 1
    if (x + 1, y) in tunnels:
      num1 += 1
    if (x + 1, y) in tunnels:
      num1 += 1
    
    # Check how many directions a pacman can go to in the legalmoves 
    x, y = legal
    if (x + 1, y) in legalPositions:
      num2 += 1
    if (x + 1, y) in legalPositions:
      num2 += 1
    if (x + 1, y) in legalPositions:
      num2 += 1
    if (x + 1, y) in legalPositions:
      num2 += 1

    # If there is only 1 move (backwards) a dead end is found
    # Make sure the tunnel wasn't already found
    if num2 - num1 == 1 and legal not in tunnels:
      newTunnels.append(legal)

    # Reset the variables 
    num1 = 0
    num2 = 0

  # Return the list with the newly added tunnel
  return newTunnels

def nextPosition(pos, action):
  """
  This function checks the all the possible next positions a pacman can take
  """

  # Read the coordinates of the legal move 
  x, y = pos

  # Return the coordinates based on the direction
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
  """
  This function will return the tunnel a pacman is currently in, if any
  """
  
  # Return none if pacman is not currently in a tunnel
  if pos not in tunnels:
    return None

  # Set up a queue to save the position to look at
  queue = util.Queue()
  queue.push(pos)

  # List variable to save the position of the pacman in
  empty = []

  # Loop until there are no more positions a pacman can go in
  while not queue.isEmpty():

    # Get the position from the queue
    currentPos = queue.pop()

    # Make sure the position is not already visited
    if currentPos not in empty:

      # Save the current position
      empty.append(currentPos)

      # Calculate the successor position
      successorPos = getSuccessorPos(currentPos, tunnels)

      # Loop over the successor positions
      for succPos in successorPos:

        # Make sure the location is not already visited
        if succPos not in empty:

          # Save the successor position
          queue.push(succPos)

  # Return the list of the positions used to get to the end of the tunnel
  return empty

def getSuccessorPos(pos, legalPositions):
  """
  This function will find all the possible positions a successor can be in
  """

  # Create an empty list that can hold the successor's positions
  successorpos = []

  # Read the coordinates of the legal move
  x, y = pos

  # Find all the legal positions a pacman can take from the position it's standing
  if (x + 1, y) in legalPositions:
    successorpos.append((x + 1, y))
  if (x + 1, y) in legalPositions:
    successorpos.append((x - 1, y))
  if (x + 1, y) in legalPositions:
    successorpos.append((x, y + 1))
  if (x + 1, y) in legalPositions:
    successorpos.append((x, y - 1))
  return successorpos

def getTunnelEntrance(pos, tunnels, legalPositions):
  """
  This function finds the entrance to a tunnel
  """

  # Do nothing if the position is not in the tunnels list
  if pos not in tunnels:
    return None

  # Get the list of position of the current tunnel
  currentTunnel = getCurrentPosTunnel(pos, tunnels)

  # Loop over the positions
  for tnl in currentTunnel:

    # Return the entrance if the tunnel is found
    entrance = getCurrentPosTunnel(tnl, tunnels, legalPositions)
    if entrance != None:
      return entrance

class Guessing:
  """
  This Guessing class guesses the position of opponents 
  """

  def __init__(self, agent, gameState):
    """
    This is the class initializer
    """

    # Set up the start state and save the enemies, agent and middle of the board
    self.start = gameState.getInitialAgentPosition(agent.index)
    self.agent = agent
    self.middle = gameState.data.layout.width / 2
    self.enemies = self.agent.getOpponents(gameState)

    # Define a list for the legalpositions and a dictionary for the guesses
    self.legalPositions = []
    self.guesses = {}

    # Get all the legal positions in the whole game
    for noWall in gameState.getWalls().asList(False):
      self.legalPositions.append(noWall)

    # Loop over the enemies
    for enemy in self.enemies:

      # Build a counter for each enemy and start with a generic number to save data
      self.guesses[enemy] = util.Counter()
      self.guesses[enemy][gameState.getInitialAgentPosition(enemy)] = 1.0
      self.guesses[enemy].normalize()

  def guessEnemyPos(self):
    """
    This function guesses where the enemy will go or has already gone
    """

    # Loop over the enemies and build a counter for the distance for each
    for enemy in self.enemies:
      distance = util.Counter()

      # Loop over all the legal positions on the board
      for legal in self.legalPositions:

        # Build a counter for the new distance to the enemies
        newDistance = util.Counter()

        # This line saves all possible positions a pacman sees, legal or not
        allPos = [(legal[0] + i, legal[1] + j) for i in [-1,0,1] for j in [-1,0,1] if not (abs(i) == 1 and abs(j) == 1)]

        # Loop over the legalpositions
        for legalPos in self.legalPositions:

          # Check which of the legal positions are in all the positions the pacman can go
          if legalPos in allPos:

            # Save the distance 
            newDistance[legalPos] = 1.0

        # Save the average distance
        newDistance.normalize()

        # Loop over the position and probability
        for pos, probability in newDistance.items():

          # Update the distance prediction
          distance[pos] = distance[pos] + self.guesses[self.enemy][pos] * probability

      # Calculate the average distance and update the guess
      distance.normalize()
      self.guesses[enemy] = distance

  def lookAround(self, agent, gameState):
    """
    This function uses manhattan and noisy distances to try and guess where the 
    enemies are currently
    """

    # Get own position and distance to enemy
    myPos = gameState.getAgentPosition(agent.index)
    noisyDistance = gameState.getAgentDistances()

    # Set up a counter for the distance
    distance = util.Counter()

    # Loop over the enemies
    for enemy in self.enemies:

      # Loop over all the legal positions
      for legal in self.legalPositions:

        # Calculate the manhattan distance and probability 
        manhattan = util.manhattanDistance(myPos, legal)
        probability = gameState.getDistanceProb(manhattan, noisyDistance)

        # Save the distance to the middle from the first position a pacman is in
        if agent.red:
          ifPacman = legal[0] < self.middle
        else:
          ifPacman = legal[0] > self.middle

        # Run away when close to enemy ghost 
        if manhattan <= 6 or ifPacman != gameState.getAgentState(enemy).isPacman:
          distance[legal] = 0.0
        else:
          distance[legal] = self.guesses[enemy][legal] * probability

      # Get the average distnaces 
      distance.normalize()
      self.guesses[enemy] = distance

  def possiblePos(self, enemy):
    """
    This function returns the max value of the guess 
    """

    return self.guesses[enemy].argMax()

#  -=-=-=- Agents -=-=-=-
class ReflexChonk(CaptureAgent):

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

    self.enemyGuess = Guessing(self, gameState)

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
          successorPos = getSuccessorPos((x, y), tunnels)
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
        successorPos = getSuccessorPos((x, y), tunnels)

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

class OffensiveChock(ReflexChonk):
  """
    Here we made the offensive agent, its a subclass of the reflex agent
    And has specific functions and behaviour related to good offensive actions
  """
  
  def getFeatures(self, gameState, action):
    """
      This function extracts all needed features from other functions like getFood or getCapsules.
      It also init lists for the features that aren't given in the right format. And append them to a list.
    """
    
    # init lists for features
    enemies = []
    ghosts = []
    scaredGhosts = []
    activeGhosts = []
    freeRoamFood = []
    tunnelFood = []
    
    # call functions for more features and puts them in a variable
    successor = self.getSuccessor(gameState, action)
    currentPos = gameState.getAgentState(self.index).getPosition()
    newPos = successor.getAgentState(self.index).getPosition()
    nextPos = nextPosition(currentPos, action)
    currentFood = self.getFood(gameState).asList()
    capsules = self.getCapsules(gameState)
    emptyTunnel = self.checkIfTunnelEmpty(gameState, successor)

    # init dict named "features" for saving data
    features = util.Counter()
    features["successorScore"] = self.getScore(successor)


    # append all the features to there corresponding list
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

    # Checks if the len of ghost = 0. And sets the variables accordingly
    if len(ghosts) == 0:
      self.capsule = None
      self.nextOpenFood = None
      self.nextTunnelFood = None

    # Checks if getAgentState = pacman. And changes the variable changeEntrance accordingly
    if gameState.getAgentState(self.index).isPacman:
      self.changeEntrance = False

    # Checks if the nextPosition will be a position with food, and adds 1 to carrying dots
    if nextPos in currentFood:
      self.carriedDot += 1
    if not gameState.getAgentState(self.index).isPacman:
      self.carriedDot = 0

    # Checks if the length of currentfood < 3, and goes home (Because 2 or less on the playing field is anough to win)
    if len(currentFood) < 3:
      features["return"] = self.getHomeDistance(successor)

    # When the length of activeghost > 0 and the length of currentfood >= 3. init lists for the positions
    if len(activeGhosts) > 0 and len(currentFood) >= 3:
      distances = []
      ghostPos = []
      succPos = []

      # append to the lists the variables
      for aGhost in activeGhosts:
        distances.append(self.getMazeDistance(newPos, aGhost.getPosition()))

      minDist = min(distances)

      for acGhost in activeGhosts:
        ghostPos.append(acGhost.getPosition())

      features["ghostDist"] = minDist

      # if your nextposition = a ghost position, your dead.
      if nextPos in ghostPos:
        features["dead"] = 1
      
      for ghostP in ghostPos:
        succPos.append(getSuccessorPos(ghostP, legalPositions))

      if nextPos in ghostPos[0]:
        features["dead"] = 1

      # if the length of freeRoamFood > 0, make another list
      if len(freeRoamFood) > 0:
        freeRoamFoodFeatures = []

        for fRF in freeRoamFood:
          freeRoamFoodFeatures.append(self.getMazeDistance(nextPos, fRF))

        features["freeRoamFood"] = min(freeRoamFoodFeatures)

        if nextPos in freeRoamFood:
          features["freeRoamFood"] = -1
        
      elif len(freeRoamFood) == 0:
        features["return"] = self.getHomeDistance(successor)

    # When the length of activeghost > 0 and the length of currentfood >= 3. init the freeroamfood lists
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

    # These are functions for edge cases. 
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

    # Checks of nextOpenFood = 0. And then try to go home
    if self.nextOpenFood != None:
      features["goToSafeFood"] = self.getMazeDistance(nextPos, self.nextOpenFood)
      if nextPos == self.nextOpenFood:
        features["goToSafeFood"] = 0
        self.nextOpenFood = None

    # Makes sure that while going to "SafeFood". it doesn't die too ghosts
    if features["goToSafeFood"] == 0 and self.nextTunnelFood != None:
      features["goToSafeFood"] = self.getMazeDistance(nextPos, self.nextTunnelFood)
      if nextPos == self.nextTunnelFood:
        features["goToSafeFood"] = 0
        self.nextTunnelFood = None

    # if there are ghosts active and there are still capsules in the game, act accordingly
    if len(activeGhosts) > 0 and len(capsules) != 0:
      for cap in capsules:
        actGhos = []
        for aG in activeGhosts:
          actGhos.append(self.getMazeDistance(cap, aG.getPosition()))
        if self.getMazeDistance(currentPos, cap) < min(actGhos):
          self.capsules = cap

    # if there are ghosts active and there are still capsules in the game, act accordingly
    if len(scaredGhosts) > 0 and len(capsules) != 0:
      for ca in capsules:
        scaGhosts = []
        for sG in scaredGhosts:
          scaGhosts.append(self.getMazeDistance(ca, sG.getPosition()))
        if self.getMazeDistance(currentPos, ca) >= scaredGhosts[0].scaredTimer and self.getMazeDistance(currentPos, ca) < min(scaGhosts):
          self.capsules = ca

    # if the current position is in a tunnel, search if there are capsules in the tunnel
    if currentPos in tunnels:
      for c in capsules:
        if c in getCurrentPosTunnel(currentPos, tunnels):
          self.capsules = c

    # if there are capsules in the game, get the distances to the capsules
    if self.capsules != None:
      features["capsuleDistance"] = self.getMazeDistance(nextPos, self.capsules)
      if nextPos == self.capsules:
        features["capsuleDistance"] = 0
        self.capsules = None

    # If there are no activeghosts, make sure the agent doesn't get the capsule
    if len(activeGhosts) == 0 and nextPos in capsules:
      features["leaveCapsule"] = 0.1

    # if the action is stop, set the feature to stop
    if action == Directions.STOP:
      features["stop"] = 1

    # This is a function to let the agent decide if he needs to go for food in a tunnel
    if successor.getAgentState(self.index).isPacman and currentPos not in tunnels and successor.getAgentState(self.index).getPosition() in tunnels and emptyTunnel == 0:
      features["noFoodInTunnel"] = -1

    # When there are active ghosts, find the mazedinstance.
    if len(activeGhosts) > 0:
      disActiveGhost = []
      for activeGhost in activeGhosts:
        disActiveGhost.append(self.getMazeDistance(currentPos, activeGhost.getPosition()))
      if emptyTunnel != 0 and emptyTunnel * 2 >= min(disActiveGhost) - 1:
        features["wasteAction"] = -1

    # When there are scared ghosts, find there mazedinstance.
    if len(scaredGhosts) > 0:
      disScaredGhost = []
      for ScaredGhost in scaredGhosts:
        disScaredGhost.append(self.getMazeDistance(currentPos, ScaredGhost.getPosition()))
      if emptyTunnel != 0 and emptyTunnel * 2 >= scaredGhosts[0].scaredTimer -1:
        features["wasteAction"] = -1

    # if the agent can't go the safe food, find the best next entrance.
    if self.nextEntry != None and features["goToSafeFood"] == 0:
      features["goToNextEntrance"] = self.getMazeDistance(nextPos, self.nextEntrance)

    # Checks of there are no active ghosts and if there is food, then only aims to get food most efficient
    if len(activeGhosts) == 0 and len(currentFood) >- 3:
      nearestFood = []
      for f in currentFood:
        nearestFood.append(self.getMazeDistance(nextPos, f))
      features["distToSafeFood"] = min(nearestFood)
      if nextPos in self.getFood(gameState).asList():
        features["distToSafeFood"] = -1

    return features

  # this is a functions that returns the weights
  def getWeights(self, gameState, action):
    return {"successorScore": 1,"return": -1, "ghostDist": -10, "dead": -1000, "freeRoamFood": -3, "goToSafeFood": -10, "distToSafeFood": -2,
    "capsuleDistance": -1000, "leaveCapsule": -1,"stop": -50,"noFoodInTunnel": 100,"wasteAction": 100,"goToNextEntrance": -1000}

  # This is a functions that returns the distance to Home
  def getHomeDistance(self, gameState):
    
    # Get current position and the width of the layout
    curPos = gameState.getAgentState(self.index).getPosition()
    width = gameState.data.layout.width
    
    # Init lists
    legalPositions = []
    legalRed = []
    legalBlue = []

    # appends all the places where there are no walls.
    for noWall in gameState.getWalls().asList(False):
      legalPositions.append(noWall)
    
    # Get the Red half of the screen
    for legalR in legalPositions:
      if legalR[0] == width / 2 - 1:
        legalRed.append(legalR)

    # Get the Blue half of the screen
    for legalB in legalPositions:
      if legalB[0] == width / 2:
        legalBlue.append(legalB)

    # If we are team red, get the distance to the middle
    if self.red:
      distanceR = []
      for lRed in legalRed:
        distanceR.append(self.getMazeDistance(curPos, lRed))
      return min(distanceR)
    
    # Else return distance to the middle from blue
    else:
      distanceB = []
      for lBlue in legalBlue:
        distanceB.append(self.getMazeDistance(curPos, lBlue))
      return min(distanceB)

class DefensiveChonk(ReflexChonk):
  """
    This is the defensive agent, it has custom weights and policy's for defensive actions
  """
  
  def getFeatures(self, gameState, action):
    """
      This function extracts all needed features from other functions like getFood or getCapsules.
      It also init lists for the features that aren't given in the right format. And append them to a list.
    """
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

    # Append all the features relevant to the defensive agent
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

    # Here we hardcoded the defending feature
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

  # Return the weights for the agent
  def getWeights(self, gameState, action):
    return {"defending": 10, "goToEdge": -2, "goToTunnel": -10, "getOutOfTunnel": -0.1,
    "Invaders": -100, "wastedAction": 200,  "chase": -100, "stop": -100, "murder": -1}

  # Get the distance from you to the middle of the matrix
  def getEdgeDistance(self, gameState):

    curPos = gameState.getAgentState(self.index).getPosition()
    width = gameState.data.layout.width

    # Makes a list for information we need
    legalPositions = []
    legalRed = []
    legalBlue = []

    # Append the legal positions to the list.
    for noWall in gameState.getWalls().asList(False):
      legalPositions.append(noWall)

    # Append the legal actions for red
    for legalR in legalPositions:
      if legalR[0] == width / 2 - 1:
        legalRed.append(legalR)

    # Append the legal actions for blue
    for legalB in legalPositions:
      if legalB[0] == width / 2:
        legalBlue.append(legalB)

    # If we are red, calculate the distance till the first red space
    if self.red:
      distanceR = []
      for lRed in legalRed:
        distanceR.append(self.getMazeDistance(curPos, lRed))
      return min(distanceR)

    # Else we are blue, calculate the distance till the first blue space
    else:
      distanceB = []
      for lBlue in legalBlue:
        distanceB.append(self.getMazeDistance(curPos, lBlue))
      return min(distanceB)

  # With this function we can check if an Agent is better just blocking an enemy then eating it. 
  # By blocking a tunnel instead of eating the pacman
  def blockTunnel(self, curInvaders, currentPos, curCapsule):
    if len(curInvaders) == 1:
      invaderPos = curInvaders[0].getPosition()
      if invaderPos in tunnels:
        tunnelEntrance = getTunnelEntrance(invaderPos, tunnels, legalPositions)
        if self.getMazeDistance(tunnelEntrance, currentPos) <= self.getMazeDistance(tunnelEntrance, invaderPos):
          if curCapsule not in getCurrentPosTunnel(invaderPos, tunnels):
            return None
    return False

  # returns the food we lost. By observation
  def lostFood(self):
    previousObservation = self.getPreviousObservation()
    currentObservation = self.getCurrentObservation()
    previousFood = self.getFoodYouAreDefending(previousObservation).asList()
    currentFood = self.getFoodYouAreDefending(currentObservation).asList()

    # If the length of currentFood < then previousFood, return the lost food
    if len(currentFood) < len(previousFood):
      for lost in previousFood:
        if lost not in currentFood:
          return lost
    return None