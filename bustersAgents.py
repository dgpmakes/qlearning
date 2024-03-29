from __future__ import print_function
from wekaI import Weka
import os
import numpy as np
# bustersAgents.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley.
# 
  # The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from builtins import range
from builtins import object
import util
from game import Agent
from game import Directions
from keyboardAgents import KeyboardAgent
import inference
import busters

class NullGraphics(object):
    "Placeholder for graphics"
    def initialize(self, state, isBlue = False):
        pass
    def update(self, state):
        pass
    def pause(self):
        pass
    def draw(self, state):
        pass
    def updateDistributions(self, dist):
        pass
    def finish(self):
        pass

class KeyboardInference(inference.InferenceModule):
    """
    Basic inference module for use with the keyboard.
    """
    def initializeUniformly(self, gameState):
        "Begin with a uniform distribution over ghost positions."
        self.beliefs = util.Counter()
        for p in self.legalPositions: self.beliefs[p] = 1.0
        self.beliefs.normalize()

    def observe(self, observation, gameState):
        noisyDistance = observation
        emissionModel = busters.getObservationDistribution(noisyDistance)
        pacmanPosition = gameState.getPacmanPosition()
        allPossible = util.Counter()
        for p in self.legalPositions:
            trueDistance = util.manhattanDistance(p, pacmanPosition)
            if emissionModel[trueDistance] > 0:
                allPossible[p] = 1.0
        allPossible.normalize()
        self.beliefs = allPossible

    def elapseTime(self, gameState):
        pass

    def getBeliefDistribution(self):
        return self.beliefs


class BustersAgent(object):
    "An agent that tracks and displays its beliefs about ghost positions."

    def __init__( self, index = 0, inference = "ExactInference", ghostAgents = None, observeEnable = True, elapseTimeEnable = True):
        self.weka = Weka()
        self.weka.start_jvm()
        inferenceType = util.lookup(inference, globals())
        self.inferenceModules = [inferenceType(a) for a in ghostAgents]
        self.observeEnable = observeEnable
        self.elapseTimeEnable = elapseTimeEnable
        self.reward = 0

    def registerInitialState(self, gameState):
        "Initializes beliefs and inference modules"
        import __main__
        self.display = __main__._display
        for inference in self.inferenceModules:
            inference.initialize(gameState)
        self.ghostBeliefs = [inf.getBeliefDistribution() for inf in self.inferenceModules]
        self.firstMove = True

    # def observationFunction(self, gameState):
    #     "Removes the ghost states from the gameState"
    #     agents = gameState.data.agentStates
    #     gameState.data.agentStates = [agents[0]] + [None for i in range(1, len(agents))]
    #     return gameState

    def getAction(self, gameState):
        "Updates beliefs, then chooses an action based on updated beliefs."
        #for index, inf in enumerate(self.inferenceModules):
        #    if not self.firstMove and self.elapseTimeEnable:
        #        inf.elapseTime(gameState)
        #    self.firstMove = False
        #    if self.observeEnable:
        #        inf.observeState(gameState)
        #    self.ghostBeliefs[index] = inf.getBeliefDistribution()
        #self.display.updateDistributions(self.ghostBeliefs)
        return self.chooseAction(gameState)

    def chooseAction(self, gameState):
        "By default, a BustersAgent just stops.  This should be overridden."
        return Directions.STOP 

class BustersKeyboardAgent(BustersAgent, KeyboardAgent):
    "An agent controlled by the keyboard that displays beliefs about ghost positions."

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):
        q = KeyboardAgent.getAction(self, gameState)
        return q

    def printLineData(self, gameState, mode=1):

        # Skip initial frames with the Stop direction
        if gameState.data.agentStates[0].getDirection() == "Stop": 
            return ""

        # Direccion al fantasma mas cercano
        is_at_north = False
        is_at_south = False
        is_at_east = False
        is_at_west = False

        nearest_ghost_index = gameState.data.ghostDistances.index(min(i for i in gameState.data.ghostDistances if i is not None))

        nearest_ghost_x_position = gameState.getGhostPositions()[nearest_ghost_index][0]
        nearest_ghost_y_position = gameState.getGhostPositions()[nearest_ghost_index][1]

        #print("x -> " + str(nearest_ghost_x_position))
        #print("y -> " + str(nearest_ghost_y_position))


        pacman_x_pos = gameState.getPacmanPosition()[0]
        pacman_y_pos = gameState.getPacmanPosition()[1]

        relative_x_pos = nearest_ghost_x_position - pacman_x_pos
        relative_y_pos = nearest_ghost_y_position - pacman_y_pos

        if relative_y_pos > 0:
            is_at_north = True
        if relative_y_pos < 0:
            is_at_south = True
        if relative_x_pos > 0:
            is_at_east = True
        if relative_x_pos < 0:
            is_at_west = True

        #print("N -> " + str(is_at_north))
        #print("S -> " + str(is_at_south))
        #print("E -> " + str(is_at_east))
        #print("W -> " + str(is_at_west))

        if mode == 1:

            return (

                str("North" in gameState.getLegalPacmanActions()) + # Can go North
                "," + str("South" in gameState.getLegalPacmanActions()) + # Can go South
                "," + str("East" in gameState.getLegalPacmanActions()) + # Can go East
                "," + str("West" in gameState.getLegalPacmanActions()) + # Can go West


                "," + str(is_at_north) + # Is at the north
                "," + str(is_at_south) + # Is at the south
                "," + str(is_at_east) + # Is at the east
                "," + str(is_at_west) + # Is at the west
        
                "," + str(gameState.data.agentStates[0].getDirection()) + # Actions by PacMan
                "\n" 

            )

        elif mode == 2:

            is_any_ghost_within_reach = (abs(relative_y_pos) == 1 and abs(relative_x_pos) == 0) or (abs(relative_y_pos) == 0 and abs(relative_x_pos) == 1)
            is_any_food_nearby = gameState.getDistanceNearestFood() == 1

            return (

                str(gameState.getScore()) + "\n" + # score

                str(is_any_ghost_within_reach) + # if there is a ghost nearby
                "," + str(is_any_food_nearby) + # if there is a dot to eat nearby

                "," + str(gameState.getScore()) + "," # scoreSiguiente

            )





from distanceCalculator import Distancer
from game import Actions
from game import Directions
import random, sys

'''Random PacMan Agent'''
class RandomPAgent(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        ##print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table
        
    def chooseAction(self, gameState):
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman
        move_random = random.randint(0, 3)
        if   ( move_random == 0 ) and Directions.WEST in legal:  move = Directions.WEST
        if   ( move_random == 1 ) and Directions.EAST in legal: move = Directions.EAST
        if   ( move_random == 2 ) and Directions.NORTH in legal:   move = Directions.NORTH
        if   ( move_random == 3 ) and Directions.SOUTH in legal: move = Directions.SOUTH
        return move


class WekaAgent(BustersAgent, KeyboardAgent):

    def __init__(self, index = 0, inference = "KeyboardInference", ghostAgents = None):
        KeyboardAgent.__init__(self, index)
        BustersAgent.__init__(self, index, inference, ghostAgents)

    def getAction(self, gameState):
        return BustersAgent.getAction(self, gameState)

    def chooseAction(self, gameState):  

        # Direccion al fantasma mas cercano
        is_at_north = False
        is_at_south = False
        is_at_east = False
        is_at_west = False

        nearest_ghost_index = gameState.data.ghostDistances.index(min(i for i in gameState.data.ghostDistances if i is not None))

        nearest_ghost_x_position = gameState.getGhostPositions()[nearest_ghost_index][0]
        nearest_ghost_y_position = gameState.getGhostPositions()[nearest_ghost_index][1]

        pacman_x_pos = gameState.getPacmanPosition()[0]
        pacman_y_pos = gameState.getPacmanPosition()[1]

        relative_x_pos = nearest_ghost_x_position - pacman_x_pos
        relative_y_pos = nearest_ghost_y_position - pacman_y_pos

        if relative_y_pos > 0:
            is_at_north = True
        if relative_y_pos < 0:
            is_at_south = True
        if relative_x_pos > 0:
            is_at_east = True
        if relative_x_pos < 0:
            is_at_west = True


        x = [
        str("North" in gameState.getLegalPacmanActions()),
        str("South" in gameState.getLegalPacmanActions()),
        str("East" in gameState.getLegalPacmanActions()),
        str("West" in gameState.getLegalPacmanActions()),
        str(is_at_north),
        str(is_at_south),
        str(is_at_east),
        str(is_at_west)
        ]
        print(x)
        import os
        wekapath = os.environ['WEKAPATH']
        move = self.weka.predict(wekapath + "/model.model", x, wekapath + "/data.arff", debug=False)
        print(move)
        return move


class GreedyBustersAgent(BustersAgent):
    "An agent that charges the closest ghost."

    def registerInitialState(self, gameState):
        "Pre-computes the distance between every two points."
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)

    def chooseAction(self, gameState):
        """
        First computes the most likely position of each ghost that has
        not yet been captured, then chooses an action that brings
        Pacman closer to the closest ghost (according to mazeDistance!).

        To find the mazeDistance between any two positions, use:
          self.distancer.getDistance(pos1, pos2)

        To find the successor position of a position after an action:
          successorPosition = Actions.getSuccessor(position, action)

        livingGhostPositionDistributions, defined below, is a list of
        util.Counter objects equal to the position belief
        distributions for each of the ghosts that are still alive.  It
        is defined based on (these are implementation details about
        which you need not be concerned):

          1) gameState.getLivingGhosts(), a list of booleans, one for each
             agent, indicating whether or not the agent is alive.  Note
             that pacman is always agent 0, so the ghosts are agents 1,
             onwards (just as before).

          2) self.ghostBeliefs, the list of belief distributions for each
             of the ghosts (including ghosts that are not alive).  The
             indices into this list should be 1 less than indices into the
             gameState.getLivingGhosts() list.
        """
        pacmanPosition = gameState.getPacmanPosition()
        legal = [a for a in gameState.getLegalPacmanActions()]
        livingGhosts = gameState.getLivingGhosts()
        livingGhostPositionDistributions = \
            [beliefs for i, beliefs in enumerate(self.ghostBeliefs)
             if livingGhosts[i+1]]
        return Directions.EAST

class BasicAgentAA(BustersAgent):

    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self, gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.countActions = 0
        
    ''' Example of counting something'''
    def countFood(self, gameState):
        food = 0
        for width in gameState.data.food:
            for height in width:
                if(height == True):
                    food = food + 1
        return food
    
    ''' Print the layout'''  
    def printGrid(self, gameState):
        table = ""
        #print(gameState.data.layout) ## Print by terminal
        for x in range(gameState.data.layout.width):
            for y in range(gameState.data.layout.height):
                food, walls = gameState.data.food, gameState.data.layout.walls
                table = table + gameState.data._foodWallStr(food[x][y], walls[x][y]) + ","
        table = table[:-1]
        return table

    def printInfo(self, gameState):
        print("---------------- TICK ", self.countActions, " --------------------------")
        # Map size
        width, height = gameState.data.layout.width, gameState.data.layout.height
        print("Width: ", width, " Height: ", height)
        # Pacman position
        print("Pacman position: ", gameState.getPacmanPosition())
        # Legal actions for Pacman in current position
        print("Legal actions: ", gameState.getLegalPacmanActions())
        # Pacman direction
        print("Pacman direction: ", gameState.data.agentStates[0].getDirection())
        # Number of ghosts
        print("Number of ghosts: ", gameState.getNumAgents() - 1)
        # Alive ghosts (index 0 corresponds to Pacman and is always false)
        print("Living ghosts: ", gameState.getLivingGhosts())
        # Ghosts positions
        print("Ghosts positions: ", gameState.getGhostPositions())
        # Ghosts directions
        print("Ghosts directions: ", [gameState.getGhostDirections().get(i) for i in range(0, gameState.getNumAgents() - 1)])
        # Manhattan distance to ghosts
        print("Ghosts distances: ", gameState.data.ghostDistances)
        # Pending pac dots
        print("Pac dots: ", gameState.getNumFood())
        # Manhattan distance to the closest pac dot
        print("Distance nearest pac dots: ", gameState.getDistanceNearestFood())
        # Map walls
        print("Map:")
        print( gameState.getWalls())
        # Score
        print("Score: ", gameState.getScore())
        
    def printLineData(self, gameState, mode=1):

        # Skip initial frames with the Stop direction
        if gameState.data.agentStates[0].getDirection() == "Stop": 
            return ""

        # Direccion al fantasma mas cercano
        is_at_north = False
        is_at_south = False
        is_at_east = False
        is_at_west = False

        nearest_ghost_index = gameState.data.ghostDistances.index(min(i for i in gameState.data.ghostDistances if i is not None))

        nearest_ghost_x_position = gameState.getGhostPositions()[nearest_ghost_index][0]
        nearest_ghost_y_position = gameState.getGhostPositions()[nearest_ghost_index][1]

        #print("x -> " + str(nearest_ghost_x_position))
        #print("y -> " + str(nearest_ghost_y_position))


        pacman_x_pos = gameState.getPacmanPosition()[0]
        pacman_y_pos = gameState.getPacmanPosition()[1]

        relative_x_pos = nearest_ghost_x_position - pacman_x_pos
        relative_y_pos = nearest_ghost_y_position - pacman_y_pos

        if relative_y_pos > 0:
            is_at_north = True
        if relative_y_pos < 0:
            is_at_south = True
        if relative_x_pos > 0:
            is_at_east = True
        if relative_x_pos < 0:
            is_at_west = True

        #print("N -> " + str(is_at_north))
        #print("S -> " + str(is_at_south))
        #print("E -> " + str(is_at_east))
        #print("W -> " + str(is_at_west))

        if mode == 1:

            return (

                str("North" in gameState.getLegalPacmanActions()) + # Can go North
                "," + str("South" in gameState.getLegalPacmanActions()) + # Can go South
                "," + str("East" in gameState.getLegalPacmanActions()) + # Can go East
                "," + str("West" in gameState.getLegalPacmanActions()) + # Can go West


                "," + str(is_at_north) + # Is at the north
                "," + str(is_at_south) + # Is at the south
                "," + str(is_at_east) + # Is at the east
                "," + str(is_at_west) + # Is at the west
        
                "," + str(gameState.data.agentStates[0].getDirection()) + # Actions by PacMan
                "\n" 

            )

        elif mode == 2:

            is_any_ghost_within_reach = (abs(relative_y_pos) == 1 and abs(relative_x_pos) == 0) or (abs(relative_y_pos) == 0 and abs(relative_x_pos) == 1)
            is_any_food_nearby = gameState.getDistanceNearestFood() == 1

            return (

                str(gameState.getScore()) + "\n" + # score

                str(is_any_ghost_within_reach) + # if there is a ghost nearby
                "," + str(is_any_food_nearby) + # if there is a dot to eat nearby

                "," + str(gameState.getScore()) + "," # scoreSiguiente

            )

    def chooseAction(self, gameState):
        self.countActions = self.countActions + 1
        self.printInfo(gameState)
        move = Directions.STOP
        legal = gameState.getLegalActions(0) ##Legal position from the pacman

        distancer = Distancer(gameState.data.layout)


        # Move towards the nearest ghost

        pos_pacman = gameState.getPacmanPosition()
        ghost_to_follow = 0
        nearest_distance = 999999999999999

        # Look which ghost is closer
        for i in range(0, len(gameState.getGhostPositions())):
            distance_to_analyze = distancer.getDistance((pos_pacman[0], pos_pacman[1]),(gameState.getGhostPositions()[i][0], gameState.getGhostPositions()[i][1]))
            if gameState.getLivingGhosts()[i+1] and distance_to_analyze < nearest_distance:
                ghost_to_follow = i
                nearest_distance = distance_to_analyze

        # Look how to approach the ghost
        valid_directions = legal
        if "Stop" in valid_directions:
            valid_directions.remove("Stop")
        
        # Analyze which direction is better
        current_best_distance = 99999999999999
        current_direction = None

        for direction in valid_directions:
            pacman_position = (pos_pacman[0], pos_pacman[1])

            if direction is Directions.NORTH:
                pacman_position = (pos_pacman[0], pos_pacman[1] + 1)
            elif direction is Directions.SOUTH:
                pacman_position = (pos_pacman[0], pos_pacman[1] - 1)   
            elif direction is Directions.WEST:
                pacman_position = (pos_pacman[0] - 1, pos_pacman[1])               
            elif direction is Directions.EAST:
                pacman_position = (pos_pacman[0] + 1, pos_pacman[1])   
            
            resulting_distance = distancer.getDistance(pacman_position,
                (gameState.getGhostPositions()[ghost_to_follow][0], gameState.getGhostPositions()[ghost_to_follow][1]))

            if resulting_distance < current_best_distance:
                current_direction = direction
                current_best_distance = resulting_distance

        return current_direction

class QLearningAgent(BustersAgent):
    
    def registerInitialState(self, gameState):
        BustersAgent.registerInitialState(self,gameState)
        self.distancer = Distancer(gameState.data.layout, False)
        self.epsilon = 0.3
        self.alpha = 0.3
        self.discount = 0.8

        self.actions = {"North":0, "East":1, "South":2, "West":3}
        if os.path.exists("qtable.txt"):
            self.table_file = open("qtable.txt", "r+")
            self.q_table = self.readQtable()
        else:
            self.table_file = open("qtable.txt","w+")
            width = gameState.data.layout.width
            height = gameState.data.layout.height
            print(width*height)
            self.initializeQtable(8) #argumento indica cuantos estados hay
            #self.initializeQtable(32) #argumento indica cuantos estados hay

    
    def initializeQtable(self, nrows):
        self.q_table = np.zeros((nrows,len(self.actions)))

    def readQtable(self):
        "Read qtable from disc"
        table = self.table_file.readlines()
        q_table = []

        for i, line in enumerate(table):
            row = line.split()
            row = [float(x) for x in row]
            q_table.append(row)

        return q_table

    def writeQtable(self):
        "Write qtable to disc"
        self.table_file.seek(0)
        self.table_file.truncate()
        for line in self.q_table:
            for item in line:
                self.table_file.write(str(item)+" ")
            self.table_file.write("\n")
            
    def printQtable(self):
        "Print qtable"
        for line in self.q_table:
            print(line)
        print("\n")    
            
    def __del__(self):
        "Destructor. Invokation at the end of each episode"
        self.writeQtable()
        print("__del__ ha sido llamado")
        self.table_file.close()

    def computePosition(self, gameState):

        # p0 = gameState.getPacmanPosition()[0]
        # p1 = gameState.getPacmanPosition()[1]
        # width = gameState.data.layout.width
        # height = gameState.data.layout.height

        # return p1*width + p0

        is_at_north = False
        is_at_south = False
        is_at_east = False
        is_at_west = False

        nearest_ghost_index = gameState.data.ghostDistances.index(min(i for i in gameState.data.ghostDistances if i is not None))

        nearest_ghost_x_position = gameState.getGhostPositions()[nearest_ghost_index][0]
        nearest_ghost_y_position = gameState.getGhostPositions()[nearest_ghost_index][1]

        #print("x -> " + str(nearest_ghost_x_position))
        #print("y -> " + str(nearest_ghost_y_position))


        pacman_x_pos = gameState.getPacmanPosition()[0]
        pacman_y_pos = gameState.getPacmanPosition()[1]

        relative_x_pos = nearest_ghost_x_position - pacman_x_pos
        relative_y_pos = nearest_ghost_y_position - pacman_y_pos

        if relative_y_pos > 0:
            is_at_north = True
        if relative_y_pos < 0:
            is_at_south = True
        if relative_x_pos > 0:
            is_at_east = True
        if relative_x_pos < 0:
            is_at_west = True

        result = 0
        action_mapper = {"North":0, "East":1, "South":2, "West":3}

        if is_at_north:
            if is_at_east: #NORESTE
                print("state -> 0")
                result = 0
            elif is_at_west: #NOROESTE
                print("state -> 1")
                result = 1
            else: #NORTE
                print("state -> 2")
                result = 2
        elif is_at_south:
            if is_at_east:
                print("state -> 3")
                result = 3
            elif is_at_west:
                print("state -> 4")
                result = 4
            else:
                print("state -> 5")
                result = 5
        elif is_at_west:
            print("state -> 6")
            result = 6
        elif is_at_east:
            print("state -> 7")
            result = 7

        return result
        if self.previous_action != None:
            return result + 8 * action_mapper[self.previous_action]
        else:
            return result


    def getQValue(self, state, action):

        """
          Returns Q(state,action)
          Should return 0.0 if we have never seen a state
          or the Q node value otherwise
        """
        position = self.computePosition(state)
        action_column = self.actions[action]
        print(position,action_column)
        return self.q_table[position][action_column]


    def computeValueFromQValues(self, state):
        """
          Returns max_action Q(state,action)
          where the max is over legal actions.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return a value of 0.0.
        """
        legalActions = state.getLegalActions()
        if 'Stop' in legalActions: legalActions.remove("Stop")
        if len(legalActions)==0:
          return 0
        return max(self.q_table[self.computePosition(state)])

    def computeActionFromQValues(self, state):
        print("computeAction()")

        """
          Compute the best action to take in a state.  Note that if there
          are no legal actions, which is the case at the terminal state,
          you should return None.
        """
        legalActions = state.getLegalPacmanActions()
        if 'Stop' in legalActions: legalActions.remove("Stop")
        if len(legalActions) == 0:
          return None

        best_actions = [legalActions[0]]
        best_value = self.getQValue(state, legalActions[0])
        print("\n\nChoosing the best actiion...")
        for action in legalActions:
            value = self.getQValue(state, action)
            print(str(action) + " -> " + str(value))
            if value == best_value:
                best_actions.append(action)
            if value > best_value:
                best_actions = [action]
                best_value = value
        
        print("The best action is -> " + str(best_actions))
        return random.choice(best_actions)

    def getAction(self, currentState):
        """
          Compute the action to take in the current state.  With
          probability self.epsilon, we should take a random action and
          take the best policy action otherwise.  Note that if there are
          no legal actions, which is the case at the terminal state, you
          should choose None as the action.
        """
        
        # Pick Action
        legalActions = currentState.getLegalActions()
        if 'Stop' in legalActions: legalActions.remove("Stop")
        action = None

        #Se decide el valor de epsilon para elegir acción aleatoria o decidida
        flip = util.flipCoin(self.epsilon)

        if flip:
            action = random.choice(legalActions)
        else:
            action = self.getPolicy(currentState)

        # Una vez tenemos la mejor acción, generamos el estado sucesor
        nextState = currentState.generateSuccessor(0, action)
        reward = self.getReward(currentState, action, nextState)

        #if self.previous_state != None and self.previous_action != None:
        self.update(currentState, action, nextState, reward)
        
        return action


    # def chooseAction(self, gameState):
    #     actionToPerform = self.getAction(gameState)
    #     nextState = self.generateSuccessor(self, actionToPerform)

    #     reward = self.getReward(gameState, actionToPerform, nextState)
    #     self.update(self, actionToPerform, nextState, reward)


    def update(self, previousState, action, nextState, reward):
        """
        The parent class calls this to observe a
        state = action => nextState and reward transition.
        You should do your Q-Value update here

        Good Terminal state -> reward 1
        Bad Terminal state -> reward -1
        Otherwise -> reward 0

        Q-Learning update:

        if terminal_state:
        Q(state,action) <- (1-self.alpha) Q(state,action) + self.alpha * (r + 0)
        else:
        Q(state,action) <- (1-self.alpha) Q(state,action) + self.alpha * (r + self.discount * max a' Q(nextState, a'))

        """
        # TRACE for transition and position to update. Comment the following lines if you do not want to see that trace
#        print("Update Q-table with transition: ", state, action, nextState, reward)
#         position = self.computePosition(state)
#         action_column = self.actions[action]
#         print("Corresponding Q-table cell to update:", position, action_column)

        currentValue = self.getQValue(previousState, action)
        nextValue = self.getValue(nextState)
        discount = self.discount
        alpha = self.alpha

        reward = self.getReward(previousState, action, nextState)
        print("REWARD OBTENIDO = " + str(reward))
        result = (1 - alpha) * currentValue + alpha * (reward + discount*nextValue)
        print("almacenar -> " + str(result))
        self.q_table[self.computePosition(previousState)][self.actions[action]] = result
        
        
        # TRACE for updated q-table. Comment the following lines if you do not want to see that trace
#         print("Q-table:")
#         self.printQtable()

    def getPolicy(self, state):
        "Return the best action in the qtable for a given state"
        return self.computeActionFromQValues(state)

    def getValue(self, state):
        "Return the highest q value for a given state"
        return self.computeValueFromQValues(state)

    def getReward(self, state, action, nextState):
        "Return the obtained reward"
        # diferencia_score = abs(state.getScore()) - abs(nextState.getScore())
        # if diferencia_score == -1:
        #     if self.getNearestGhostDistance(state) - self.getNearestGhostDistance(nextState) <= 0:
        #         print("reward -> -1")
        #         return -1
        #     else:
        #         print("reward -> 10")
        #         return 10
        # else:
        #     #return 0
        #     print("reward -> " + str(diferencia_score))
        #     return diferencia_score

        

        if (self.getNearestGhostDistance(state) - self.getNearestGhostDistance(nextState) > 0 and self.getNearestGhostDistance(nextState) is not 0):
            #print("reward -> 10")
            return 10

        #print("reward -> " + str(nextState.getScore() - state.getScore()))
        return (nextState.getScore() - state.getScore())


    def getNearestGhostDistance(self, gameState):

        pos_pacman = gameState.getPacmanPosition()
        ghost_to_follow = 0
        nearest_distance = 999999999999999

        # Look which ghost is closer
        for i in range(0, len(gameState.getGhostPositions())):
            distance_to_analyze = self.distancer.getDistance((pos_pacman[0], pos_pacman[1]),(gameState.getGhostPositions()[i][0], gameState.getGhostPositions()[i][1]))
            if gameState.getLivingGhosts()[i+1] and distance_to_analyze < nearest_distance:
                ghost_to_follow = i
                #print("se sigue al fantasma numero "+str(i))
                nearest_distance = distance_to_analyze

        #print(self.q_table)
        nearest_distance = gameState.data.ghostDistances[ghost_to_follow]
        print("distancia a fantasma más cercano ->" + str(nearest_distance))

        to_return = nearest_distance

        return 0 if to_return == None else to_return


        


