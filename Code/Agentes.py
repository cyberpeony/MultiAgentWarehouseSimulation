"""
Robots:
        Atributos:
            - id
            - state (0 - chasing, 1 - carrying, 2 - idle)
            - position
            - rotation
            - partner
            - color
            - utility

            // CARGA
            - objectType

            // ESTADISTICA (UTILIDAD)
            - recorded_objects_handled
            - recorded_movements_made
            - recorded_steps_idle
            - recorded_avoided_collisions

            // SENSORES
            - adyacentTiles
            - collision (true/false)
            - stackHeight

            // PLANNING
            - path
            - goal_tile
        Actions:
            - search
            - find_path
            - grab_object
            - stack_object
            - idle (si va a haber collision) (si ya terminó sus objetos)
            - thinking
Objetos:
    0. Cubo
    1. Warrior
    2. Pelota
    3. Dino
    4. Carro

Variables de ambiente:
    1. 
"""

# Equipo Wizards
""" 
Fernanda Diaz Gutierrez |  A01639572
Miguel Angel Barrientos Ballesteros | A01637150
Carlos Iván Armenta Naranjo | A01643070
Jorge Javier Blazquez Gonzalez | A01637706
Gabriel Alvarez Arzate | A01642991
"""
#
import random

# Ontologia
from owlready2 import *
onto = get_ontology("file://ontology.owl")


# Model design
import agentpy as ap
import numpy as np 

# Visualization
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt



with onto: 
    class Agent(Thing):
        pass
    class RobotCuboOnto(Agent):
        pass
    class RobotWarriorOnto(Agent):
        pass
    class RobotPelotaOnto(Agent):
        pass
    class RobotDinoOnto(Agent):
        pass
    class RobotCarroOnto(Agent):
        pass
    class State(Thing):
        pass
    class Stack(Thing):
        pass
    class Object(Thing):
        pass
    class Target(Thing):
        pass
    class ObjectCubo(Object):
        pass
    class ObjectWarrior(Object):    
        pass
    class ObjectPelota(Object):
        pass
    class ObjectDino(Object):
        pass
    class ObjectCarro(Object):
        pass
    class Tile(Thing):
        pass
    class Almacen(Thing):
        pass   
    class Color(Thing):
        pass
    class has_target(FunctionalProperty, ObjectProperty):
        domain = [Agent]
        range = [Tile]
    class has_stack(FunctionalProperty, ObjectProperty):
        domain = [Agent]
        range = [Stack]
    class stack_value(FunctionalProperty, DataProperty):
        domain = [Stack]
        range = [int]
    class contains_object(FunctionalProperty, ObjectProperty):
        domain = [Stack]
        range = [Object]
    class stackTile(FunctionalProperty, ObjectProperty):
        domain = [Stack]
        range = [Tile]
    class has_Position(FunctionalProperty, ObjectProperty):
        domain = [Agent]
        range = [Tile]
    class has_id(FunctionalProperty, DataProperty):
        domain = [Agent]
        range = [int]
    class has_color(FunctionalProperty, ObjectProperty):
        domain = [Agent]
        range = [Color]
    class color_value(FunctionalProperty, DataProperty):
        domain = [Color]
        range = [str]    
    class has_state(FunctionalProperty, ObjectProperty):
        domain = [Agent]
        range = [State]
    class state_value(FunctionalProperty, DataProperty):
        domain = [State]
        range = [int]
    class is_carrying(FunctionalProperty, ObjectProperty):
        domain = [Agent]
        range = [Object]
    class object_in_tile(ObjectProperty):
        domain = [Tile]
        range = [Object] 
    class robot_in_tile(ObjectProperty):
        domain = [Tile]
        range = [Agent]
    class has_tiles(ObjectProperty):
        domain = [Almacen]
        range = [Tile]

    # Now we save the ontology into the file
    onto.save()

'''Ejemplos de instancias
# Crear instancias de objetos y tiles
object1 = onto.ObjectOso("object1")
tile1 = onto.Tile("tile1")
tile1.tileCoordinate = (2, 3)  # Coordenada del tile

# Crear un stack
stack1 = onto.Stack("stack1")
stack1.contains_object = object1  # Asignar objeto al stack
stack1.located_on_tile = tile1    # Asignar tile al stack

# Verificar las relaciones
print(f"El stack {stack1} contiene el objeto: {stack1.contains_object}")
print(f"El stack {stack1} está ubicado en el tile: {stack1.located_on_tile.tileCoordinate}")
'''

class RobotCubo(ap.Agent):
    def see(self,e):
        self.board = e

    def next(self):
        """
        The next function contains the decision making process, where the
        general algorithm of deductive reasoning is executed.
        """
        # For every action in the action list
        for act in self.actions:
        # For every rule in the rule list
            for rule in self.rules:
            # If the action (act) is valid by using the rule (rule)
                if rule(act):
            # return validated action
                    return act
                
    def action(self,act):
        """
        The action function will execute the chosen action (act).
        """
        # If the action exists
        if act is not None:
            act() 
            
    def step(self):
        """
        The agent's step function
        """
        self.see(self.model.boardTiles) # Perception function

        a = self.next() # next function (return chosen action (a))
        self.action(a) # action function (executes action (a))
                        # statistics recordings

    def setup(self):
        self.done = False
        self.robotID = 0
        self.recorded_objects_handled = 0 # stack
        self.recorded_movements_made = 0 # move
        self.recorded_steps_idle = 0 # idle
        self.recorded_avoided_collisions = 0 # move rule
        self.recorded_utility = 0 # pick up
        self.board = [] #not used

        self.lastGoAround = None
        self.currentIdles = 0

        self.path = [0,0] #not set

        self.myself = onto.RobotCuboOnto(has_id = self.id)
        self.myself.has_state = onto.State(state_value = 2) # idle
        #print("state: " + str(self.myself.has_state.state_value))
        self.position = self.model.robotList[self.robotID] # Initialize with robot coordinate from unity


        #print("Initial position: " + str(self.position[0]) + ", " + str(self.position[1]))
        #self.myself.has_color = onto.Color(color_value = "Blue")
        self.targetObjectType = None
        self.pathEnd = None # Must be set before moving
        self.nextTile = None

        self.myAvailableObjectsCoords = list(self.model.objCoorList)
        self.myAvailableObjectsType = list(self.model.objTypeList)
        
        # stack
        self.currentStack = None
        self.stackAmount = None

        self.actions = [self.setTarget, self.pickUp, self.stack, self.setNextHorTile, self.setNextVerticalTile, self.goAroundHorizontal, self.goAroundVertical, self.moveTo, self.idle] # The action list 
        self.rules = [self.rule_canSetTarget, self.rule_canPick, self.rule_canStack, self.rule_nextHor,
        self.rule_nextVer, self.rule_goAroundHorizontal, self.rule_goAroundVertical, self.rule_canMove, self.rule_idle] # The rule list 

    def rule_canStack(self,act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If the state is carrying, if path is (0,0), if the pathEnd is adyacent to my position, then i must stack my object”.
        """
        if self.pathEnd is None:
            return False

        rule_validation = [False, False, False]
        
        if self.myself.has_state.state_value == 1: # Im carrying
            rule_validation[0] = True 
        if abs(self.position[0] - self.pathEnd[0]) + abs(self.position[1] - self.pathEnd[1]) == 1:
            rule_validation[1] = True
        if act == self.stack:
            rule_validation[2] = True 
        return all(rule_validation)

    def rule_canPick(self,act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If state is chasing, If path is (0,0), if pathEnd is adyacet to my position tile, , then I must pick it up”.
        """ 
        if self.pathEnd is None:
            return False

        rule_validation = [False,False,False]
        if self.myself.has_state.state_value == 0:
            rule_validation[0] = True 
        if abs(self.position[0] - self.pathEnd[0]) + abs(self.position[1] - self.pathEnd[1]) == 1:
            rule_validation[1] = True
        if act == self.pickUp:
            rule_validation[2] = True 
        return all(rule_validation)


    def rule_canMove(self, act): 
        if self.done:
            return False

        rule_validation = [False, False, False]
        #print(f"Checking rule_canMove: nextTile={self.nextTile}, robotList={self.model.robotList}")

        if self.nextTile is not None:
            rule_validation[0] = True 
        if self.nextTile not in self.model.robotList:
            rule_validation[1] = True
        else:
            #print("Collision detected with another robot!")
            self.recorded_avoided_collisions += 1
        if act == self.moveTo:
            rule_validation[2] = True 

        #print(f"rule_canMove validation: {rule_validation}")
        return all(rule_validation)

    def rule_canSetTarget(self,act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If objCoorList is not empty, if pathEndd is None”.
        """
        if self.done:
            return False

        rule_validation = [False,False,False]
        if len(self.myAvailableObjectsCoords) != 0 or self.currentStack != None:
            rule_validation[0] = True 
        if self.pathEnd == None:
            rule_validation[1] = True
        if act == self.setTarget:
            rule_validation[2] = True 
        return all(rule_validation)
        
    def rule_idle(self,act):  
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        If there i
        “”.
        """
        rule_validation = [False]
        if act == self.idle:
            rule_validation[0] = True
        return all(rule_validation)

    def rule_nextHor(self, act): 
        rule_validation = [False, False, False, False, False]
        peekTile = (self.position[0] - 1, self.position[1]) if self.path[0] < 0 else (self.position[0] + 1, self.position[1])
        #print(f"rule_nextHor: path={self.path}, nextTile={self.nextTile}, position={self.position}, peekTile={peekTile}")
        if self.lastGoAround != "X":
            rule_validation[0] = True 
        if self.path[0] != 0:
            rule_validation[1] = True 
        if self.nextTile is None: 
            rule_validation[2] = True
        if peekTile not in self.model.objCoorList and peekTile not in self.model.robotList:
            rule_validation[3] = True
        if act == self.setNextHorTile:
            rule_validation[4] = True 
        #if(all(rule_validation)):
            #print(f"rule_nextHor validation: {rule_validation}")
        return all(rule_validation)


    def rule_nextVer(self, act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If rule_nextHor isn't accomplished (due to collision), this assures the robot moves 1 step vertically”.
        If path.x is not 0, if nextTile is None, if the next tile in x is not occupied
        """
        rule_validation = [False, False, False, False, False]
        peekTile = (self.position[0], self.position[1] - 1) if self.path[1] < 0 else (self.position[0], self.position[1] + 1)
        #print(f"rule_nextVer: path={self.path}, nextTile={self.nextTile}, position={self.position}, peekTile={peekTile}")
        if self.lastGoAround != "Y":
            rule_validation[0] = True
        if self.path[1] != 0:
            rule_validation[1] = True 
        if self.nextTile is None: 
            rule_validation[2] = True
        if peekTile not in self.model.objCoorList and peekTile not in self.model.robotList:
            rule_validation[3] = True
        if act == self.setNextVerticalTile:
            rule_validation[4] = True 
        #
            #print(f"rule_nextVer validation: {rule_validation}")
        return all(rule_validation)
    
    def rule_goAroundHorizontal(self, act):
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If rule_nextHor nor rule_verTile (due to collision or path 0), this assures the robot moves 1 step vertically”.
        If path.y is 0, if nextTile is None, if the next tile in x is not occupied
        """
        rule_validation = [False, False, False, False]
        up_tile = (self.position[0], self.position[1] + 1)
        down_tile = (self.position[0], self.position[1] - 1)
        #print(f"rule_goAroundHorizontal: path={self.path}, nextTile={self.nextTile}, position={self.position}, up_tile={up_tile}, down_tile={down_tile}")
        if self.path[1] == 0:
            rule_validation[0] = True 
        if self.nextTile is None: 
            rule_validation[1] = True
        if (up_tile not in self.model.objCoorList and up_tile not in self.model.robotList) or (down_tile not in self.model.objCoorList and down_tile not in self.model.robotList):
            rule_validation[2] = True
        if act == self.goAroundHorizontal:
            rule_validation[3] = True 
        #if all(rule_validation):
            #print(f"rule_goAroundHorizontal: {rule_validation}")
        return all(rule_validation)
    
    def rule_goAroundVertical(self, act):
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If rule_nextHor nor rule_verTile (due to collision or path 0), this assures the robot moves 1 step vertically”.
        If path.x is 0, if nextTile is None, if the next tile in x is not occupied
        """
        rule_validation = [False, False, False, False]
        left_tile = (self.position[0] - 1, self.position[1])
        right_tile = (self.position[0] + 1, self.position[1])
        #print(f"pathEnd: pathEnd={self.pathEnd}, rule_goAroundHorizontal: path={self.path}, nextTile={self.nextTile}, position={self.position}, left_tile={left_tile}, right_tile={right_tile}")
        
        if self.path[0] == 0:
            rule_validation[0] = True 
        if self.nextTile is None: 
            rule_validation[1] = True
        if (left_tile not in self.model.objCoorList and left_tile not in self.model.robotList) or (right_tile not in self.model.objCoorList and right_tile not in self.model.robotList):
            rule_validation[2] = True
        if act == self.goAroundVertical:
            rule_validation[3] = True 
        #if all(rule_validation):
            #print(f"rule_goAroundVertical: {rule_validation}")
        return all(rule_validation)

    def setTarget(self):
        #print("setTarget")
        """
        Set pathEnd
        which the next target coordinate before moving (Stack or Object) 
        Remove the target from the available obj list
        """
        self.model.robotCuboActions.append("thinking")
        self.model.robotCuboActCoords.append(self.position)

        if self.myself.has_state.state_value == 1: # if Im currently carrying
            if self.currentStack == None:
                random_index = random.choice(range(len(self.model.stackList)))
                print("\n\nsetTarget: Going to Stack")
                print("rand Index: " + str(random_index))
                self.currentStack = self.model.stackList[random_index]
                self.model.stackList.remove(self.currentStack)
                self.stackAmount = 0
                self.pathEnd = self.currentStack
                
            else:
                self.pathEnd = self.currentStack
        
        elif self.myself.has_state.state_value == 2: # if Im currently idle
            self.myself.has_state = onto.State(state_value = 0) # set state to chasing
            random_index = random.choice(range(len(self.myAvailableObjectsCoords)))
            
            print("\n\nsetTarget: Going for object")
            print("Available objects left: " + str(len(self.myAvailableObjectsCoords)))
            print("Available objects type left: " + str(len(self.myAvailableObjectsType)))
            print("rand Index: " + str(random_index))
            self.pathEnd = self.myAvailableObjectsCoords[random_index]
            self.targetObjectType = self.myAvailableObjectsType[random_index]
            
            del self.myAvailableObjectsType[random_index]
            self.myAvailableObjectsCoords.remove(self.pathEnd)

            """ 
            #print("(" + str(self.model.objCoorList[random_index][0]) + ", " + str(self.model.objCoorList[random_index][1]) + "), ")
            #print("\n")
            
            #print("myAvailableObjectsCoords: ")
            for elem in self.myAvailableObjectsCoords:
                #print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")

            #print("\n")
            #print("myAvailableObjectsType: ")
            for elem in self.myAvailableObjectsType:
                #print(str(elem) + ", ", end=" ")
            """

        print("RobotID: " + str(self.robotID))
        print("pathEnd: (" + str(self.pathEnd[0]) + ", " + str(self.pathEnd[1]) + ")")
        print("targetObjectType: " + str(self.targetObjectType)) 
        print("Current Position: (" + str(self.position[0]) + ", " + str(self.position[1]) + ")")

        
        self.findPath()

    def goAroundHorizontal(self):
        """
        Ignoring path
        Sets nextTile to +1 or -1 in y coor. 
        """
        self.model.robotCuboActions.append("thinking")
        self.model.robotCuboActCoords.append(self.position)

        #print("goAroundHor")
        if (self.position[1] < 18):
            self.nextTile = (self.position[0], self.position[1] + 1)
        else:
            self.nextTile = (self.position[0], self.position[1] - 1)
        self.lastGoAround = "Y"
        
    def goAroundVertical(self):
        """
        Sets nextTile to +1 or -1 in x coor. 
        """
        self.model.robotCuboActions.append("thinking")
        self.model.robotCuboActCoords.append(self.position)
        #print("goAroundVer")
        if (self.position[0] < 18):
            self.nextTile = (self.position[0] + 1, self.position[1])
        else:
            self.nextTile = (self.position[0] - 1, self.position[1])
        self.lastGoAround = "X"
        

    def setNextHorTile(self):
        #print("setNextHorTile")
        self.model.robotCuboActions.append("thinking")
        self.model.robotCuboActCoords.append(self.position)
        if self.path[0] < 0:
            self.nextTile = (self.position[0] - 1, self.position[1])
            #self.path[0] += 1  
        elif self.path[0] > 0: 
            self.nextTile = (self.position[0] + 1, self.position[1])
            #self.path[0] -= 1
        #print(f"setNextHorTile: nextTile={self.nextTile}, path={self.path}")
        self.lastGoAround = None
        

    def setNextVerticalTile(self):
        # #print("setNextVerticalTile")
        self.model.robotCuboActions.append("thinking")
        self.model.robotCuboActCoords.append(self.position)
        if self.path[1] < 0:
            self.nextTile = (self.position[0], self.position[1] - 1)
            #self.path[1] += 1
        elif self.path[1] > 0: 
            self.nextTile = (self.position[0], self.position[1] + 1)
            #self.path[1] -= 1
        #print(f"setNextVerticalTile: nextTile={self.nextTile}, path={self.path}")
        self.lastGoAround = None
        

    def findPath(self):
        self.path[0] = self.pathEnd[0] - self.position[0]
        self.path[1] = self.pathEnd[1] - self.position[1]
        #print(f"findPath: position={self.position}, pathEnd={self.pathEnd}, path={self.path}")

        
    def moveTo(self):
        print(f"Moving to: {self.nextTile}")
        self.model.robotCuboActions.append("move")
        self.position = self.nextTile
        self.model.robotCuboActCoords.append(self.position)
        self.model.robotList[self.robotID] = self.position
        self.recorded_movements_made += 1
        self.nextTile = None
        self.findPath() # Recalculate path from my new position Robot 0: Cubo
        self.currentIdles = 0


    def pickUp(self):
        #print("\nPICK UP: ")
        """
        Try To pick up 
        If the robot cant, return the target to the available objList
        """
        #print("targetObjectType: " + str(self.targetObjectType) + ", robotID: " + str(self.robotID))
        if self.targetObjectType == self.robotID:
        
        # si puedo pick up (si es mi tipo de obj) 
            self.myself.has_state = onto.State(state_value = 1) # State 1. Carrying
            self.model.robotCuboActions.append("pickup")
            self.model.robotCuboActCoords.append(self.pathEnd)

            objIndex = self.model.objCoorList.index(self.pathEnd) 

            self.model.objCoorList.remove(self.pathEnd) 
            del self.model.objTypeList[objIndex]

            self.targetObjectType = None
            self.pathEnd = None
            self.recorded_utility += 1
            self.nextTile = None

            
        else:
        # No puedo agarrarlo
            self.myself.has_state = onto.State(state_value = 2) # State 2. Idle
            self.targetObjectType = None
            self.pathEnd = None
            self.nextTile = None
      
    def stack(self):
        """
        Set currentStack a None si stackAmount es 5
        """
        self.stackAmount += 1
        self.myself.has_state = onto.State(state_value = 2) # State 2. Idle
        self.model.robotCuboActions.append("stack")
        self.model.robotCuboActCoords.append(self.pathEnd)
        self.targetObjectType = None
        self.pathEnd = None
        self.recorded_objects_handled += 1

        if self.stackAmount == 5:
            self.stackAmount = None
            self.currentStack = None

        if self.recorded_objects_handled == 5:
            self.myAvailableObjectsCoords = []
            self.myAvailableObjectsType = []
            print("RobotID " + str(self.robotID) + ": Done with my 5 objects")
            self.done = True

    def idle(self):
        """
        """
        self.model.robotCuboActions.append("idle")
        self.model.robotCuboActCoords.append(self.position)
        self.recorded_steps_idle += 1
        self.currentIdles +=1
        print("Idle: " + str(self.currentIdles))
        if self.currentIdles > 50 and self.myself.has_state.state_value != 1: #not carrying
            self.myself.has_state = onto.State(state_value = 2)
            self.myAvailableObjectsCoords.append(self.pathEnd) # regresarlo para intentarlo despues
            self.myAvailableObjectsType.append(self.targetObjectType)
            self.pathEnd = None
            self.targetObjectType = None
            self.nextTile = None
            print("\n\nSTOP IDLE PLEASE\n")
            self.currentIdles = 0
            
            

class RobotWarrior(ap.Agent):
    def see(self,e):
        self.board = e

    def next(self):
        """
        The next function contains the decision making process, where the
        general algorithm of deductive reasoning is executed.
        """
        # For every action in the action list
        for act in self.actions:
        # For every rule in the rule list
            for rule in self.rules:
            # If the action (act) is valid by using the rule (rule)
                if rule(act):
            # return validated action
                    return act
                
    def action(self,act):
        """
        The action function will execute the chosen action (act).
        """
        # If the action exists
        if act is not None:
            act() 
            
    def step(self):
        """
        The agent's step function
        """
        self.see(self.model.boardTiles) # Perception function

        a = self.next() # next function (return chosen action (a))
        self.action(a) # action function (executes action (a))
                        # statistics recordings

    def setup(self):
        self.done = False
        self.robotID = 1
        self.recorded_objects_handled = 0 # stack
        self.recorded_movements_made = 0 # move
        self.recorded_steps_idle = 0 # idle
        self.recorded_avoided_collisions = 0 # move rule
        self.recorded_utility = 0 # pick up
        self.board = [] #not used

        self.lastGoAround = None
        self.currentIdles = 0

        

        self.path = [0,0] #not set

        self.myself = onto.RobotWarriorOnto(has_id = self.id)
        self.myself.has_state = onto.State(state_value = 2) # idle
        #print("state: " + str(self.myself.has_state.state_value))
        self.position = self.model.robotList[self.robotID] # Initialize with robot coordinate from unity


        #print("Initial position: " + str(self.position[0]) + ", " + str(self.position[1]))
        #self.myself.has_color = onto.Color(color_value = "Blue")
        self.targetObjectType = None
        self.pathEnd = None # Must be set before moving
        self.nextTile = None

        self.myAvailableObjectsCoords = list(self.model.objCoorList)
        self.myAvailableObjectsType = list(self.model.objTypeList)
        
        # stack
        self.currentStack = None
        self.stackAmount = None

        self.actions = [self.setTarget, self.pickUp, self.stack, self.setNextHorTile, self.setNextVerticalTile, self.goAroundHorizontal, self.goAroundVertical, self.moveTo, self.idle] # The action list 
        self.rules = [self.rule_canSetTarget, self.rule_canPick, self.rule_canStack, self.rule_nextHor,
        self.rule_nextVer, self.rule_goAroundHorizontal, self.rule_goAroundVertical, self.rule_canMove, self.rule_idle] # The rule list 

    def rule_canStack(self,act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If the state is carrying, if path is (0,0), if the pathEnd is adyacent to my position, then i must stack my object”.
        """
        if self.pathEnd is None:
            return False

        rule_validation = [False, False, False]
        
        if self.myself.has_state.state_value == 1: # Im carrying
            rule_validation[0] = True 
        if abs(self.position[0] - self.pathEnd[0]) + abs(self.position[1] - self.pathEnd[1]) == 1:
            rule_validation[1] = True
        if act == self.stack:
            rule_validation[2] = True 
        return all(rule_validation)

    def rule_canPick(self,act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If state is chasing, If path is (0,0), if pathEnd is adyacet to my position tile, , then I must pick it up”.
        """ 
        if self.pathEnd is None:
            return False

        rule_validation = [False,False,False]
        if self.myself.has_state.state_value == 0:
            rule_validation[0] = True 
        if abs(self.position[0] - self.pathEnd[0]) + abs(self.position[1] - self.pathEnd[1]) == 1:
            rule_validation[1] = True
        if act == self.pickUp:
            rule_validation[2] = True 
        return all(rule_validation)


    def rule_canMove(self, act): 
        if self.done:
            return False

        rule_validation = [False, False, False]
        #print(f"Checking rule_canMove: nextTile={self.nextTile}, robotList={self.model.robotList}")

        if self.nextTile is not None:
            rule_validation[0] = True 
        if self.nextTile not in self.model.robotList:
            rule_validation[1] = True
        else:
            #print("Collision detected with another robot!")
            self.recorded_avoided_collisions += 1
        if act == self.moveTo:
            rule_validation[2] = True 

        #print(f"rule_canMove validation: {rule_validation}")
        return all(rule_validation)

    def rule_canSetTarget(self,act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If objCoorList is not empty, if pathEndd is None”.
        """
        if self.done:
            return False

        rule_validation = [False,False,False]
        if len(self.myAvailableObjectsCoords) != 0 or self.currentStack != None:
            rule_validation[0] = True 
        if self.pathEnd == None:
            rule_validation[1] = True
        if act == self.setTarget:
            rule_validation[2] = True 
        return all(rule_validation)
        
    def rule_idle(self,act):  
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        If there i
        “”.
        """
        rule_validation = [False]
        if act == self.idle:
            rule_validation[0] = True
        return all(rule_validation)

    def rule_nextHor(self, act): 
        rule_validation = [False, False, False, False, False]
        peekTile = (self.position[0] - 1, self.position[1]) if self.path[0] < 0 else (self.position[0] + 1, self.position[1])
        #print(f"rule_nextHor: path={self.path}, nextTile={self.nextTile}, position={self.position}, peekTile={peekTile}")
        if self.lastGoAround != "X":
            rule_validation[0] = True 
        if self.path[0] != 0:
            rule_validation[1] = True 
        if self.nextTile is None: 
            rule_validation[2] = True
        if peekTile not in self.model.objCoorList and peekTile not in self.model.robotList:
            rule_validation[3] = True
        if act == self.setNextHorTile:
            rule_validation[4] = True 
        #if(all(rule_validation)):
            #print(f"rule_nextHor validation: {rule_validation}")
        return all(rule_validation)


    def rule_nextVer(self, act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If rule_nextHor isn't accomplished (due to collision), this assures the robot moves 1 step vertically”.
        If path.x is not 0, if nextTile is None, if the next tile in x is not occupied
        """
        rule_validation = [False, False, False, False, False]
        peekTile = (self.position[0], self.position[1] - 1) if self.path[1] < 0 else (self.position[0], self.position[1] + 1)
        #print(f"rule_nextVer: path={self.path}, nextTile={self.nextTile}, position={self.position}, peekTile={peekTile}")
        if self.lastGoAround != "Y":
            rule_validation[0] = True
        if self.path[1] != 0:
            rule_validation[1] = True 
        if self.nextTile is None: 
            rule_validation[2] = True
        if peekTile not in self.model.objCoorList and peekTile not in self.model.robotList:
            rule_validation[3] = True
        if act == self.setNextVerticalTile:
            rule_validation[4] = True 
        #
            #print(f"rule_nextVer validation: {rule_validation}")
        return all(rule_validation)
    
    def rule_goAroundHorizontal(self, act):
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If rule_nextHor nor rule_verTile (due to collision or path 0), this assures the robot moves 1 step vertically”.
        If path.y is 0, if nextTile is None, if the next tile in x is not occupied
        """
        rule_validation = [False, False, False, False]
        up_tile = (self.position[0], self.position[1] + 1)
        down_tile = (self.position[0], self.position[1] - 1)
        #print(f"rule_goAroundHorizontal: path={self.path}, nextTile={self.nextTile}, position={self.position}, up_tile={up_tile}, down_tile={down_tile}")
        if self.path[1] == 0:
            rule_validation[0] = True 
        if self.nextTile is None: 
            rule_validation[1] = True
        if (up_tile not in self.model.objCoorList and up_tile not in self.model.robotList) or (down_tile not in self.model.objCoorList and down_tile not in self.model.robotList):
            rule_validation[2] = True
        if act == self.goAroundHorizontal:
            rule_validation[3] = True 
        #if all(rule_validation):
            #print(f"rule_goAroundHorizontal: {rule_validation}")
        return all(rule_validation)
    
    def rule_goAroundVertical(self, act):
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If rule_nextHor nor rule_verTile (due to collision or path 0), this assures the robot moves 1 step vertically”.
        If path.x is 0, if nextTile is None, if the next tile in x is not occupied
        """
        rule_validation = [False, False, False, False]
        left_tile = (self.position[0] - 1, self.position[1])
        right_tile = (self.position[0] + 1, self.position[1])
        #print(f"pathEnd: pathEnd={self.pathEnd}, rule_goAroundHorizontal: path={self.path}, nextTile={self.nextTile}, position={self.position}, left_tile={left_tile}, right_tile={right_tile}")
        
        if self.path[0] == 0:
            rule_validation[0] = True 
        if self.nextTile is None: 
            rule_validation[1] = True
        if (left_tile not in self.model.objCoorList and left_tile not in self.model.robotList) or (right_tile not in self.model.objCoorList and right_tile not in self.model.robotList):
            rule_validation[2] = True
        if act == self.goAroundVertical:
            rule_validation[3] = True 
        #if all(rule_validation):
            #print(f"rule_goAroundVertical: {rule_validation}")
        return all(rule_validation)

    def setTarget(self):
        #print("setTarget")
        """
        Set pathEnd
        which the next target coordinate before moving (Stack or Object) 
        Remove the target from the available obj list
        """
        self.model.robotWarriorActions.append("thinking")
        self.model.robotWarriorActCoords.append(self.position)
        if self.myself.has_state.state_value == 1: # if Im currently carrying
            if self.currentStack == None:
                random_index = random.choice(range(len(self.model.stackList)))
                print("\n\nsetTarget: Going to Stack")
                print("rand Index: " + str(random_index))
                self.currentStack = self.model.stackList[random_index]
                self.model.stackList.remove(self.currentStack)
                self.stackAmount = 0
                self.pathEnd = self.currentStack
            else:
                self.pathEnd = self.currentStack

        elif self.myself.has_state.state_value == 2: # if Im currently idle
            self.myself.has_state = onto.State(state_value = 0) # set state to chasing
            random_index = random.choice(range(len(self.myAvailableObjectsCoords)))
            
            print("\n\nsetTarget: Going for object")
            print("Available objects left: " + str(len(self.myAvailableObjectsCoords)))
            print("Available objects type left: " + str(len(self.myAvailableObjectsType)))
            print("rand Index: " + str(random_index))
            self.pathEnd = self.myAvailableObjectsCoords[random_index]
            self.targetObjectType = self.myAvailableObjectsType[random_index]
            
            del self.myAvailableObjectsType[random_index]
            self.myAvailableObjectsCoords.remove(self.pathEnd)

            """ 
            #print("(" + str(self.model.objCoorList[random_index][0]) + ", " + str(self.model.objCoorList[random_index][1]) + "), ")
            #print("\n")
            
            #print("myAvailableObjectsCoords: ")
            for elem in self.myAvailableObjectsCoords:
                #print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")

            #print("\n")
            #print("myAvailableObjectsType: ")
            for elem in self.myAvailableObjectsType:
                #print(str(elem) + ", ", end=" ")
            """

        print("RobotID: " + str(self.robotID))
        print("pathEnd: (" + str(self.pathEnd[0]) + ", " + str(self.pathEnd[1]) + ")")
        print("targetObjectType: " + str(self.targetObjectType)) 
        print("Current Position: (" + str(self.position[0]) + ", " + str(self.position[1]) + ")")

        
        self.findPath()

    def goAroundHorizontal(self):
        """
        Ignoring path
        Sets nextTile to +1 or -1 in y coor. 
        """
        self.model.robotWarriorActions.append("thinking")
        self.model.robotWarriorActCoords.append(self.position)
        #print("goAroundHor")
        if (self.position[1] < 18):
            self.nextTile = (self.position[0], self.position[1] + 1)
        else:
            self.nextTile = (self.position[0], self.position[1] - 1)
        self.lastGoAround = "Y"
        
    def goAroundVertical(self):
        """
        Sets nextTile to +1 or -1 in x coor. 
        """
        self.model.robotWarriorActions.append("thinking")
        self.model.robotWarriorActCoords.append(self.position)
        #print("goAroundVer")
        if (self.position[0] < 18):
            self.nextTile = (self.position[0] + 1, self.position[1])
        else:
            self.nextTile = (self.position[0] - 1, self.position[1])
        self.lastGoAround = "X"
        

    def setNextHorTile(self):
        #print("setNextHorTile")
        self.model.robotWarriorActions.append("thinking")
        self.model.robotWarriorActCoords.append(self.position)
        if self.path[0] < 0:
            self.nextTile = (self.position[0] - 1, self.position[1])
            #self.path[0] += 1  
        elif self.path[0] > 0: 
            self.nextTile = (self.position[0] + 1, self.position[1])
            #self.path[0] -= 1
        #print(f"setNextHorTile: nextTile={self.nextTile}, path={self.path}")
        self.lastGoAround = None
        

    def setNextVerticalTile(self):
        # #print("setNextVerticalTile")
        self.model.robotWarriorActions.append("thinking")
        self.model.robotWarriorActCoords.append(self.position)
        if self.path[1] < 0:
            self.nextTile = (self.position[0], self.position[1] - 1)
            #self.path[1] += 1
        elif self.path[1] > 0: 
            self.nextTile = (self.position[0], self.position[1] + 1)
            #self.path[1] -= 1
        #print(f"setNextVerticalTile: nextTile={self.nextTile}, path={self.path}")
        self.lastGoAround = None
        

    def findPath(self):
        self.path[0] = self.pathEnd[0] - self.position[0]
        self.path[1] = self.pathEnd[1] - self.position[1]
        #print(f"findPath: position={self.position}, pathEnd={self.pathEnd}, path={self.path}")

        
    def moveTo(self):
        print(f"Moving to: {self.nextTile}")
        self.model.robotWarriorActions.append("move")
        self.position = self.nextTile
        self.model.robotWarriorActCoords.append(self.position)
        self.model.robotList[self.robotID] = self.position
        self.recorded_movements_made += 1
        self.nextTile = None
        self.findPath() # Recalculate path from my new position Robot 1: Warrior
        self.currentIdles = 0


    def pickUp(self):
        #print("\nPICK UP: ")
        """
        Try To pick up 
        If the robot cant, return the target to the available objList
        """
        #print("targetObjectType: " + str(self.targetObjectType) + ", robotID: " + str(self.robotID))
        if self.targetObjectType == self.robotID:
        
        # si puedo pick up (si es mi tipo de obj) 
            self.myself.has_state = onto.State(state_value = 1) # State 1. Carrying
            self.model.robotWarriorActions.append("pickup")
            self.model.robotWarriorActCoords.append(self.pathEnd)

            objIndex = self.model.objCoorList.index(self.pathEnd) 

            self.model.objCoorList.remove(self.pathEnd) 
            del self.model.objTypeList[objIndex]

            self.targetObjectType = None
            self.pathEnd = None
            self.recorded_utility += 1
            self.nextTile = None

            
        else:
        # No puedo agarrarlo
            self.myself.has_state = onto.State(state_value = 2) # State 2. Idle
            self.targetObjectType = None
            self.pathEnd = None
            self.nextTile = None
      
    def stack(self):
        """
        Set currentStack a None si stackAmount es 5
        """
        self.stackAmount += 1
        self.myself.has_state = onto.State(state_value = 2) # State 2. Idle
        self.model.robotWarriorActions.append("stack")
        self.model.robotWarriorActCoords.append(self.pathEnd)
        self.targetObjectType = None
        self.pathEnd = None
        self.recorded_objects_handled += 1

        if self.stackAmount == 5:
            self.stackAmount = None
            self.currentStack = None

        if self.recorded_objects_handled == 5:
            self.myAvailableObjectsCoords = []
            self.myAvailableObjectsType = []
            print("RobotID " + str(self.robotID) + "Done with my 5 objects")
            self.done = True

    def idle(self):
        """
        """
        self.model.robotWarriorActions.append("idle")
        self.model.robotWarriorActCoords.append(self.position)
        self.recorded_steps_idle += 1
        self.currentIdles +=1
        print("Idle: " + str(self.currentIdles))
        if self.currentIdles > 50 and self.myself.has_state.state_value != 1: #not carrying
            self.myself.has_state = onto.State(state_value = 2)
            self.myAvailableObjectsCoords.append(self.pathEnd) # regresarlo para intentarlo despues
            self.myAvailableObjectsType.append(self.targetObjectType)
            self.pathEnd = None
            self.targetObjectType = None
            self.nextTile = None
            print("\n\nSTOP IDLE PLEASE\n")
            self.currentIdles = 0
            
            


class RobotPelota(ap.Agent):
    def see(self,e):
        self.board = e

    def next(self):
        """
        The next function contains the decision making process, where the
        general algorithm of deductive reasoning is executed.
        """
        # For every action in the action list
        for act in self.actions:
        # For every rule in the rule list
            for rule in self.rules:
            # If the action (act) is valid by using the rule (rule)
                if rule(act):
            # return validated action
                    return act
                
    def action(self,act):
        """
        The action function will execute the chosen action (act).
        """
        # If the action exists
        if act is not None:
            act() 
            
    def step(self):
        """
        The agent's step function
        """
        self.see(self.model.boardTiles) # Perception function

        a = self.next() # next function (return chosen action (a))
        self.action(a) # action function (executes action (a))
                        # statistics recordings

    def setup(self):
        self.done = False
        self.robotID = 2
        self.recorded_objects_handled = 0 # stack
        self.recorded_movements_made = 0 # move
        self.recorded_steps_idle = 0 # idle
        self.recorded_avoided_collisions = 0 # move rule
        self.recorded_utility = 0 # pick up
        self.board = [] #not used

        self.lastGoAround = None
        self.currentIdles = 0

        

        self.path = [0,0] #not set

        self.myself = onto.RobotPelotaOnto(has_id = self.id)
        self.myself.has_state = onto.State(state_value = 2) # idle
        #print("state: " + str(self.myself.has_state.state_value))
        self.position = self.model.robotList[self.robotID] # Initialize with robot coordinate from unity


        #print("Initial position: " + str(self.position[0]) + ", " + str(self.position[1]))
        #self.myself.has_color = onto.Color(color_value = "Blue")
        self.targetObjectType = None
        self.pathEnd = None # Must be set before moving
        self.nextTile = None

        self.myAvailableObjectsCoords = list(self.model.objCoorList)
        self.myAvailableObjectsType = list(self.model.objTypeList)
        
        # stack
        self.currentStack = None
        self.stackAmount = None

        self.actions = [self.setTarget, self.pickUp, self.stack, self.setNextHorTile, self.setNextVerticalTile, self.goAroundHorizontal, self.goAroundVertical, self.moveTo, self.idle] # The action list 
        self.rules = [self.rule_canSetTarget, self.rule_canPick, self.rule_canStack, self.rule_nextHor,
        self.rule_nextVer, self.rule_goAroundHorizontal, self.rule_goAroundVertical, self.rule_canMove, self.rule_idle] # The rule list 

    def rule_canStack(self,act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If the state is carrying, if path is (0,0), if the pathEnd is adyacent to my position, then i must stack my object”.
        """
        if self.pathEnd is None:
            return False

        rule_validation = [False, False, False]
        
        if self.myself.has_state.state_value == 1: # Im carrying
            rule_validation[0] = True 
        if abs(self.position[0] - self.pathEnd[0]) + abs(self.position[1] - self.pathEnd[1]) == 1:
            rule_validation[1] = True
        if act == self.stack:
            rule_validation[2] = True 
        return all(rule_validation)

    def rule_canPick(self,act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If state is chasing, If path is (0,0), if pathEnd is adyacet to my position tile, , then I must pick it up”.
        """ 
        if self.pathEnd is None:
            return False

        rule_validation = [False,False,False]
        if self.myself.has_state.state_value == 0:
            rule_validation[0] = True 
        if abs(self.position[0] - self.pathEnd[0]) + abs(self.position[1] - self.pathEnd[1]) == 1:
            rule_validation[1] = True
        if act == self.pickUp:
            rule_validation[2] = True 
        return all(rule_validation)


    def rule_canMove(self, act): 
        if self.done:
            return False

        rule_validation = [False, False, False]
        #print(f"Checking rule_canMove: nextTile={self.nextTile}, robotList={self.model.robotList}")

        if self.nextTile is not None:
            rule_validation[0] = True 
        if self.nextTile not in self.model.robotList:
            rule_validation[1] = True
        else:
            #print("Collision detected with another robot!")
            self.recorded_avoided_collisions += 1
        if act == self.moveTo:
            rule_validation[2] = True 

        #print(f"rule_canMove validation: {rule_validation}")
        return all(rule_validation)

    def rule_canSetTarget(self,act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If objCoorList is not empty, if pathEndd is None”.
        """
        if self.done:
            return False


        rule_validation = [False,False,False]
        if len(self.myAvailableObjectsCoords) != 0 or self.currentStack != None:
            rule_validation[0] = True 
        if self.pathEnd == None:
            rule_validation[1] = True
        if act == self.setTarget:
            rule_validation[2] = True 
        return all(rule_validation)
        
    def rule_idle(self,act):  
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        If there i
        “”.
        """
        rule_validation = [False]
        if act == self.idle:
            rule_validation[0] = True
        return all(rule_validation)

    def rule_nextHor(self, act): 
        rule_validation = [False, False, False, False, False]
        peekTile = (self.position[0] - 1, self.position[1]) if self.path[0] < 0 else (self.position[0] + 1, self.position[1])
        #print(f"rule_nextHor: path={self.path}, nextTile={self.nextTile}, position={self.position}, peekTile={peekTile}")
        if self.lastGoAround != "X":
            rule_validation[0] = True 
        if self.path[0] != 0:
            rule_validation[1] = True 
        if self.nextTile is None: 
            rule_validation[2] = True
        if peekTile not in self.model.objCoorList and peekTile not in self.model.robotList:
            rule_validation[3] = True
        if act == self.setNextHorTile:
            rule_validation[4] = True 
        #if(all(rule_validation)):
            #print(f"rule_nextHor validation: {rule_validation}")
        return all(rule_validation)


    def rule_nextVer(self, act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If rule_nextHor isn't accomplished (due to collision), this assures the robot moves 1 step vertically”.
        If path.x is not 0, if nextTile is None, if the next tile in x is not occupied
        """
        rule_validation = [False, False, False, False, False]
        peekTile = (self.position[0], self.position[1] - 1) if self.path[1] < 0 else (self.position[0], self.position[1] + 1)
        #print(f"rule_nextVer: path={self.path}, nextTile={self.nextTile}, position={self.position}, peekTile={peekTile}")
        if self.lastGoAround != "Y":
            rule_validation[0] = True
        if self.path[1] != 0:
            rule_validation[1] = True 
        if self.nextTile is None: 
            rule_validation[2] = True
        if peekTile not in self.model.objCoorList and peekTile not in self.model.robotList:
            rule_validation[3] = True
        if act == self.setNextVerticalTile:
            rule_validation[4] = True 
        #
            #print(f"rule_nextVer validation: {rule_validation}")
        return all(rule_validation)
    
    def rule_goAroundHorizontal(self, act):
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If rule_nextHor nor rule_verTile (due to collision or path 0), this assures the robot moves 1 step vertically”.
        If path.y is 0, if nextTile is None, if the next tile in x is not occupied
        """
        rule_validation = [False, False, False, False]
        up_tile = (self.position[0], self.position[1] + 1)
        down_tile = (self.position[0], self.position[1] - 1)
        #print(f"rule_goAroundHorizontal: path={self.path}, nextTile={self.nextTile}, position={self.position}, up_tile={up_tile}, down_tile={down_tile}")
        if self.path[1] == 0:
            rule_validation[0] = True 
        if self.nextTile is None: 
            rule_validation[1] = True
        if (up_tile not in self.model.objCoorList and up_tile not in self.model.robotList) or (down_tile not in self.model.objCoorList and down_tile not in self.model.robotList):
            rule_validation[2] = True
        if act == self.goAroundHorizontal:
            rule_validation[3] = True 
        #if all(rule_validation):
            #print(f"rule_goAroundHorizontal: {rule_validation}")
        return all(rule_validation)
    
    def rule_goAroundVertical(self, act):
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If rule_nextHor nor rule_verTile (due to collision or path 0), this assures the robot moves 1 step vertically”.
        If path.x is 0, if nextTile is None, if the next tile in x is not occupied
        """
        rule_validation = [False, False, False, False]
        left_tile = (self.position[0] - 1, self.position[1])
        right_tile = (self.position[0] + 1, self.position[1])
        #print(f"pathEnd: pathEnd={self.pathEnd}, rule_goAroundHorizontal: path={self.path}, nextTile={self.nextTile}, position={self.position}, left_tile={left_tile}, right_tile={right_tile}")
        
        if self.path[0] == 0:
            rule_validation[0] = True 
        if self.nextTile is None: 
            rule_validation[1] = True
        if (left_tile not in self.model.objCoorList and left_tile not in self.model.robotList) or (right_tile not in self.model.objCoorList and right_tile not in self.model.robotList):
            rule_validation[2] = True
        if act == self.goAroundVertical:
            rule_validation[3] = True 
        #if all(rule_validation):
            #print(f"rule_goAroundVertical: {rule_validation}")
        return all(rule_validation)

    def setTarget(self):
        #print("setTarget")
        """
        Set pathEnd
        which the next target coordinate before moving (Stack or Object) 
        Remove the target from the available obj list
        """
        self.model.robotPelotaActions.append("thinking")
        self.model.robotPelotaActCoords.append(self.position)
        if self.myself.has_state.state_value == 1: # if Im currently carrying
            if self.currentStack == None:
                random_index = random.choice(range(len(self.model.stackList)))
                print("\n\nsetTarget: Going to Stack")
                print("rand Index: " + str(random_index))
                self.currentStack = self.model.stackList[random_index]
                self.model.stackList.remove(self.currentStack)
                self.stackAmount = 0
                self.pathEnd = self.currentStack
            else:
                self.pathEnd = self.currentStack

        elif self.myself.has_state.state_value == 2: # if Im currently idle
            self.myself.has_state = onto.State(state_value = 0) # set state to chasing
            random_index = random.choice(range(len(self.myAvailableObjectsCoords)))
            
            print("\n\nsetTarget: Going for object")
            print("Available objects left: " + str(len(self.myAvailableObjectsCoords)))
            print("Available objects type left: " + str(len(self.myAvailableObjectsType)))
            print("rand Index: " + str(random_index))
            self.pathEnd = self.myAvailableObjectsCoords[random_index]
            self.targetObjectType = self.myAvailableObjectsType[random_index]
            
            del self.myAvailableObjectsType[random_index]
            self.myAvailableObjectsCoords.remove(self.pathEnd)

            """ 
            #print("(" + str(self.model.objCoorList[random_index][0]) + ", " + str(self.model.objCoorList[random_index][1]) + "), ")
            #print("\n")
            
            #print("myAvailableObjectsCoords: ")
            for elem in self.myAvailableObjectsCoords:
                #print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")

            #print("\n")
            #print("myAvailableObjectsType: ")
            for elem in self.myAvailableObjectsType:
                #print(str(elem) + ", ", end=" ")
            """

        print("RobotID: " + str(self.robotID))
        print("pathEnd: (" + str(self.pathEnd[0]) + ", " + str(self.pathEnd[1]) + ")")
        print("targetObjectType: " + str(self.targetObjectType)) 
        print("Current Position: (" + str(self.position[0]) + ", " + str(self.position[1]) + ")")

        
        self.findPath()

    def goAroundHorizontal(self):
        """
        Ignoring path
        Sets nextTile to +1 or -1 in y coor. 
        """
        self.model.robotPelotaActions.append("thinking")
        self.model.robotPelotaActCoords.append(self.position)
        #print("goAroundHor")
        if (self.position[1] < 18):
            self.nextTile = (self.position[0], self.position[1] + 1)
        else:
            self.nextTile = (self.position[0], self.position[1] - 1)
        self.lastGoAround = "Y"
        
    def goAroundVertical(self):
        """
        Sets nextTile to +1 or -1 in x coor. 
        """
        self.model.robotPelotaActions.append("thinking")
        self.model.robotPelotaActCoords.append(self.position)
        #print("goAroundVer")
        if (self.position[0] < 18):
            self.nextTile = (self.position[0] + 1, self.position[1])
        else:
            self.nextTile = (self.position[0] - 1, self.position[1])
        self.lastGoAround = "X"
        

    def setNextHorTile(self):
        self.model.robotPelotaActions.append("thinking")
        self.model.robotPelotaActCoords.append(self.position)
        #print("setNextHorTile")
        if self.path[0] < 0:
            self.nextTile = (self.position[0] - 1, self.position[1])
            #self.path[0] += 1  
        elif self.path[0] > 0: 
            self.nextTile = (self.position[0] + 1, self.position[1])
            #self.path[0] -= 1
        #print(f"setNextHorTile: nextTile={self.nextTile}, path={self.path}")
        self.lastGoAround = None
        

    def setNextVerticalTile(self):
        self.model.robotPelotaActions.append("thinking")
        self.model.robotPelotaActCoords.append(self.position)
        # #print("setNextVerticalTile")
        if self.path[1] < 0:
            self.nextTile = (self.position[0], self.position[1] - 1)
            #self.path[1] += 1
        elif self.path[1] > 0: 
            self.nextTile = (self.position[0], self.position[1] + 1)
            #self.path[1] -= 1
        #print(f"setNextVerticalTile: nextTile={self.nextTile}, path={self.path}")
        self.lastGoAround = None
        

    def findPath(self):
        self.path[0] = self.pathEnd[0] - self.position[0]
        self.path[1] = self.pathEnd[1] - self.position[1]
        #print(f"findPath: position={self.position}, pathEnd={self.pathEnd}, path={self.path}")

        
    def moveTo(self):
        print(f"Moving to: {self.nextTile}")
        self.model.robotPelotaActions.append("move")
        self.position = self.nextTile
        self.model.robotPelotaActCoords.append(self.position)
        self.model.robotList[self.robotID] = self.position
        self.recorded_movements_made += 1
        self.nextTile = None
        self.findPath() # Recalculate path from my new position Robot 2: Pelota
        self.currentIdles = 0


    def pickUp(self):
        #print("\nPICK UP: ")
        """
        Try To pick up 
        If the robot cant, return the target to the available objList
        """
        #print("targetObjectType: " + str(self.targetObjectType) + ", robotID: " + str(self.robotID))
        if self.targetObjectType == self.robotID:
        
        # si puedo pick up (si es mi tipo de obj) 
            self.myself.has_state = onto.State(state_value = 1) # State 1. Carrying
            self.model.robotPelotaActions.append("pickup")
            self.model.robotPelotaActCoords.append(self.pathEnd)

            objIndex = self.model.objCoorList.index(self.pathEnd) 

            self.model.objCoorList.remove(self.pathEnd) 
            del self.model.objTypeList[objIndex]

            self.targetObjectType = None
            self.pathEnd = None
            self.recorded_utility += 1
            self.nextTile = None

            
        else:
        # No puedo agarrarlo
            self.myself.has_state = onto.State(state_value = 2) # State 2. Idle
            self.targetObjectType = None
            self.pathEnd = None
            self.nextTile = None
      
    def stack(self):
        """
        Set currentStack a None si stackAmount es 5
        """
        self.stackAmount += 1
        self.myself.has_state = onto.State(state_value = 2) # State 2. Idle
        self.model.robotPelotaActions.append("stack")
        self.model.robotPelotaActCoords.append(self.pathEnd)
        self.targetObjectType = None
        self.pathEnd = None
        self.recorded_objects_handled += 1

        if self.stackAmount == 5:
            self.stackAmount = None
            self.currentStack = None

        if self.recorded_objects_handled == 5:
            self.myAvailableObjectsCoords = []
            self.myAvailableObjectsType = []
            print("RobotID " + str(self.robotID) + "Done with my 5 objects")
            self.done = True

    def idle(self):
        """
        """
        self.model.robotPelotaActions.append("idle")
        self.model.robotPelotaActCoords.append(self.position)
        self.recorded_steps_idle += 1
        self.currentIdles +=1
        print("Idle: " + str(self.currentIdles))
        if self.currentIdles > 50 and self.myself.has_state.state_value != 1: #not carrying
            self.myself.has_state = onto.State(state_value = 2)
            self.myAvailableObjectsCoords.append(self.pathEnd) # regresarlo para intentarlo despues
            self.myAvailableObjectsType.append(self.targetObjectType)
            self.pathEnd = None
            self.targetObjectType = None
            self.nextTile = None
            print("\n\nSTOP IDLE PLEASE\n")
            self.currentIdles = 0
            
            


class RobotDino(ap.Agent):
    def see(self,e):
        self.board = e

    def next(self):
        """
        The next function contains the decision making process, where the
        general algorithm of deductive reasoning is executed.
        """
        # For every action in the action list
        for act in self.actions:
        # For every rule in the rule list
            for rule in self.rules:
            # If the action (act) is valid by using the rule (rule)
                if rule(act):
            # return validated action
                    return act
                
    def action(self,act):
        """
        The action function will execute the chosen action (act).
        """
        # If the action exists
        if act is not None:
            act() 
            
    def step(self):
        """
        The agent's step function
        """
        self.see(self.model.boardTiles) # Perception function

        a = self.next() # next function (return chosen action (a))
        self.action(a) # action function (executes action (a))
                        # statistics recordings

    def setup(self):
        self.done = False
        self.robotID = 3
        self.recorded_objects_handled = 0 # stack
        self.recorded_movements_made = 0 # move
        self.recorded_steps_idle = 0 # idle
        self.recorded_avoided_collisions = 0 # move rule
        self.recorded_utility = 0 # pick up
        self.board = [] #not used

        self.lastGoAround = None
        self.currentIdles = 0

        

        self.path = [0,0] #not set

        self.myself = onto.RobotDinoOnto(has_id = self.id)
        self.myself.has_state = onto.State(state_value = 2) # idle
        #print("state: " + str(self.myself.has_state.state_value))
        self.position = self.model.robotList[self.robotID] # Initialize with robot coordinate from unity


        #print("Initial position: " + str(self.position[0]) + ", " + str(self.position[1]))
        #self.myself.has_color = onto.Color(color_value = "Blue")
        self.targetObjectType = None
        self.pathEnd = None # Must be set before moving
        self.nextTile = None

        self.myAvailableObjectsCoords = list(self.model.objCoorList)
        self.myAvailableObjectsType = list(self.model.objTypeList)
        
        # stack
        self.currentStack = None
        self.stackAmount = None

        self.actions = [self.setTarget, self.pickUp, self.stack, self.setNextHorTile, self.setNextVerticalTile, self.goAroundHorizontal, self.goAroundVertical, self.moveTo, self.idle] # The action list 
        self.rules = [self.rule_canSetTarget, self.rule_canPick, self.rule_canStack, self.rule_nextHor,
        self.rule_nextVer, self.rule_goAroundHorizontal, self.rule_goAroundVertical, self.rule_canMove, self.rule_idle] # The rule list 

    def rule_canStack(self,act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If the state is carrying, if path is (0,0), if the pathEnd is adyacent to my position, then i must stack my object”.
        """
        if self.pathEnd is None:
            return False

        rule_validation = [False, False, False]
        
        if self.myself.has_state.state_value == 1: # Im carrying
            rule_validation[0] = True 
        if abs(self.position[0] - self.pathEnd[0]) + abs(self.position[1] - self.pathEnd[1]) == 1:
            rule_validation[1] = True
        if act == self.stack:
            rule_validation[2] = True 
        return all(rule_validation)

    def rule_canPick(self,act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If state is chasing, If path is (0,0), if pathEnd is adyacet to my position tile, , then I must pick it up”.
        """ 
        if self.pathEnd is None:
            return False

        rule_validation = [False,False,False]
        if self.myself.has_state.state_value == 0:
            rule_validation[0] = True 
        if abs(self.position[0] - self.pathEnd[0]) + abs(self.position[1] - self.pathEnd[1]) == 1:
            rule_validation[1] = True
        if act == self.pickUp:
            rule_validation[2] = True 
        return all(rule_validation)


    def rule_canMove(self, act):
        if self.done:
            return False

        rule_validation = [False, False, False]
        #print(f"Checking rule_canMove: nextTile={self.nextTile}, robotList={self.model.robotList}")

        if self.nextTile is not None:
            rule_validation[0] = True 
        if self.nextTile not in self.model.robotList:
            rule_validation[1] = True
        else:
            #print("Collision detected with another robot!")
            self.recorded_avoided_collisions += 1
        if act == self.moveTo:
            rule_validation[2] = True 

        #print(f"rule_canMove validation: {rule_validation}")
        return all(rule_validation)

    def rule_canSetTarget(self,act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If objCoorList is not empty, if pathEndd is None”.
        """
        if self.done:
            return False


        rule_validation = [False,False,False]
        if len(self.myAvailableObjectsCoords) != 0 or self.currentStack != None:
            rule_validation[0] = True 
        if self.pathEnd == None:
            rule_validation[1] = True
        if act == self.setTarget:
            rule_validation[2] = True 
        return all(rule_validation)
        
    def rule_idle(self,act):  
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        If there i
        “”.
        """
        rule_validation = [False]
        if act == self.idle:
            rule_validation[0] = True
        return all(rule_validation)

    def rule_nextHor(self, act): 
        rule_validation = [False, False, False, False, False]
        peekTile = (self.position[0] - 1, self.position[1]) if self.path[0] < 0 else (self.position[0] + 1, self.position[1])
        #print(f"rule_nextHor: path={self.path}, nextTile={self.nextTile}, position={self.position}, peekTile={peekTile}")
        if self.lastGoAround != "X":
            rule_validation[0] = True 
        if self.path[0] != 0:
            rule_validation[1] = True 
        if self.nextTile is None: 
            rule_validation[2] = True
        if peekTile not in self.model.objCoorList and peekTile not in self.model.robotList:
            rule_validation[3] = True
        if act == self.setNextHorTile:
            rule_validation[4] = True 
        #if(all(rule_validation)):
            #print(f"rule_nextHor validation: {rule_validation}")
        return all(rule_validation)


    def rule_nextVer(self, act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If rule_nextHor isn't accomplished (due to collision), this assures the robot moves 1 step vertically”.
        If path.x is not 0, if nextTile is None, if the next tile in x is not occupied
        """
        rule_validation = [False, False, False, False, False]
        peekTile = (self.position[0], self.position[1] - 1) if self.path[1] < 0 else (self.position[0], self.position[1] + 1)
        #print(f"rule_nextVer: path={self.path}, nextTile={self.nextTile}, position={self.position}, peekTile={peekTile}")
        if self.lastGoAround != "Y":
            rule_validation[0] = True
        if self.path[1] != 0:
            rule_validation[1] = True 
        if self.nextTile is None: 
            rule_validation[2] = True
        if peekTile not in self.model.objCoorList and peekTile not in self.model.robotList:
            rule_validation[3] = True
        if act == self.setNextVerticalTile:
            rule_validation[4] = True 
        #
            #print(f"rule_nextVer validation: {rule_validation}")
        return all(rule_validation)
    
    def rule_goAroundHorizontal(self, act):
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If rule_nextHor nor rule_verTile (due to collision or path 0), this assures the robot moves 1 step vertically”.
        If path.y is 0, if nextTile is None, if the next tile in x is not occupied
        """
        rule_validation = [False, False, False, False]
        up_tile = (self.position[0], self.position[1] + 1)
        down_tile = (self.position[0], self.position[1] - 1)
        #print(f"rule_goAroundHorizontal: path={self.path}, nextTile={self.nextTile}, position={self.position}, up_tile={up_tile}, down_tile={down_tile}")
        if self.path[1] == 0:
            rule_validation[0] = True 
        if self.nextTile is None: 
            rule_validation[1] = True
        if (up_tile not in self.model.objCoorList and up_tile not in self.model.robotList) or (down_tile not in self.model.objCoorList and down_tile not in self.model.robotList):
            rule_validation[2] = True
        if act == self.goAroundHorizontal:
            rule_validation[3] = True 
        #if all(rule_validation):
            #print(f"rule_goAroundHorizontal: {rule_validation}")
        return all(rule_validation)
    
    def rule_goAroundVertical(self, act):
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If rule_nextHor nor rule_verTile (due to collision or path 0), this assures the robot moves 1 step vertically”.
        If path.x is 0, if nextTile is None, if the next tile in x is not occupied
        """
        rule_validation = [False, False, False, False]
        left_tile = (self.position[0] - 1, self.position[1])
        right_tile = (self.position[0] + 1, self.position[1])
        #print(f"pathEnd: pathEnd={self.pathEnd}, rule_goAroundHorizontal: path={self.path}, nextTile={self.nextTile}, position={self.position}, left_tile={left_tile}, right_tile={right_tile}")
        
        if self.path[0] == 0:
            rule_validation[0] = True 
        if self.nextTile is None: 
            rule_validation[1] = True
        if (left_tile not in self.model.objCoorList and left_tile not in self.model.robotList) or (right_tile not in self.model.objCoorList and right_tile not in self.model.robotList):
            rule_validation[2] = True
        if act == self.goAroundVertical:
            rule_validation[3] = True 
        #if all(rule_validation):
            #print(f"rule_goAroundVertical: {rule_validation}")
        return all(rule_validation)

    def setTarget(self):
        #print("setTarget")
        """
        Set pathEnd
        which the next target coordinate before moving (Stack or Object) 
        Remove the target from the available obj list
        """
        self.model.robotDinoActions.append("thinking")
        self.model.robotDinoActCoords.append(self.position)
        if self.myself.has_state.state_value == 1: # if Im currently carrying
            if self.currentStack == None:
                random_index = random.choice(range(len(self.model.stackList)))
                print("\n\nsetTarget: Going to Stack")
                print("rand Index: " + str(random_index))
                self.currentStack = self.model.stackList[random_index]
                self.model.stackList.remove(self.currentStack)
                self.stackAmount = 0
                self.pathEnd = self.currentStack
            else:
                self.pathEnd = self.currentStack

        elif self.myself.has_state.state_value == 2: # if Im currently idle
            self.myself.has_state = onto.State(state_value = 0) # set state to chasing
            random_index = random.choice(range(len(self.myAvailableObjectsCoords)))
            
            print("\n\nsetTarget: Going for object")
            print("Available objects left: " + str(len(self.myAvailableObjectsCoords)))
            print("Available objects type left: " + str(len(self.myAvailableObjectsType)))
            print("rand Index: " + str(random_index))
            self.pathEnd = self.myAvailableObjectsCoords[random_index]
            self.targetObjectType = self.myAvailableObjectsType[random_index]
            
            del self.myAvailableObjectsType[random_index]
            self.myAvailableObjectsCoords.remove(self.pathEnd)

            """ 
            #print("(" + str(self.model.objCoorList[random_index][0]) + ", " + str(self.model.objCoorList[random_index][1]) + "), ")
            #print("\n")
            
            #print("myAvailableObjectsCoords: ")
            for elem in self.myAvailableObjectsCoords:
                #print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")

            #print("\n")
            #print("myAvailableObjectsType: ")
            for elem in self.myAvailableObjectsType:
                #print(str(elem) + ", ", end=" ")
            """

        print("RobotID: " + str(self.robotID))
        print("pathEnd: (" + str(self.pathEnd[0]) + ", " + str(self.pathEnd[1]) + ")")
        print("targetObjectType: " + str(self.targetObjectType)) 
        print("Current Position: (" + str(self.position[0]) + ", " + str(self.position[1]) + ")")

        
        self.findPath()

    def goAroundHorizontal(self):
        """
        Ignoring path
        Sets nextTile to +1 or -1 in y coor. 
        """
        self.model.robotDinoActions.append("thinking")
        self.model.robotDinoActCoords.append(self.position)
        #print("goAroundHor")
        if (self.position[1] < 18):
            self.nextTile = (self.position[0], self.position[1] + 1)
        else:
            self.nextTile = (self.position[0], self.position[1] - 1)
        self.lastGoAround = "Y"
        
    def goAroundVertical(self):
        """
        Sets nextTile to +1 or -1 in x coor. 
        """
        self.model.robotDinoActions.append("thinking")
        self.model.robotDinoActCoords.append(self.position)
        #print("goAroundVer")
        if (self.position[0] < 18):
            self.nextTile = (self.position[0] + 1, self.position[1])
        else:
            self.nextTile = (self.position[0] - 1, self.position[1])
        self.lastGoAround = "X"
        

    def setNextHorTile(self):
        self.model.robotDinoActions.append("thinking")
        self.model.robotDinoActCoords.append(self.position)
        #print("setNextHorTile")
        if self.path[0] < 0:
            self.nextTile = (self.position[0] - 1, self.position[1])
            #self.path[0] += 1  
        elif self.path[0] > 0: 
            self.nextTile = (self.position[0] + 1, self.position[1])
            #self.path[0] -= 1
        #print(f"setNextHorTile: nextTile={self.nextTile}, path={self.path}")
        self.lastGoAround = None
        

    def setNextVerticalTile(self):
        self.model.robotDinoActions.append("thinking")
        self.model.robotDinoActCoords.append(self.position)
        # #print("setNextVerticalTile")
        if self.path[1] < 0:
            self.nextTile = (self.position[0], self.position[1] - 1)
            #self.path[1] += 1
        elif self.path[1] > 0: 
            self.nextTile = (self.position[0], self.position[1] + 1)
            #self.path[1] -= 1
        #print(f"setNextVerticalTile: nextTile={self.nextTile}, path={self.path}")
        self.lastGoAround = None
        

    def findPath(self):
        self.path[0] = self.pathEnd[0] - self.position[0]
        self.path[1] = self.pathEnd[1] - self.position[1]
        #print(f"findPath: position={self.position}, pathEnd={self.pathEnd}, path={self.path}")

        
    def moveTo(self):
        print(f"Moving to: {self.nextTile}")
        self.model.robotDinoActions.append("move")
        self.position = self.nextTile
        self.model.robotDinoActCoords.append(self.position)
        self.model.robotList[self.robotID] = self.position
        self.recorded_movements_made += 1
        self.nextTile = None
        self.findPath() # Recalculate path from my new position Robot 3: Dino
        self.currentIdles = 0


    def pickUp(self):
        #print("\nPICK UP: ")
        """
        Try To pick up 
        If the robot cant, return the target to the available objList
        """
        #print("targetObjectType: " + str(self.targetObjectType) + ", robotID: " + str(self.robotID))
        if self.targetObjectType == self.robotID:
        
        # si puedo pick up (si es mi tipo de obj) 
            self.myself.has_state = onto.State(state_value = 1) # State 1. Carrying
            self.model.robotDinoActions.append("pickup")
            self.model.robotDinoActCoords.append(self.pathEnd)

            objIndex = self.model.objCoorList.index(self.pathEnd) 

            self.model.objCoorList.remove(self.pathEnd) 
            del self.model.objTypeList[objIndex]

            self.targetObjectType = None
            self.pathEnd = None
            self.recorded_utility += 1
            self.nextTile = None

            
        else:
        # No puedo agarrarlo
            self.myself.has_state = onto.State(state_value = 2) # State 2. Idle
            self.targetObjectType = None
            self.pathEnd = None
            self.nextTile = None
      
    def stack(self):
        """
        Set currentStack a None si stackAmount es 5
        """
        self.stackAmount += 1
        self.myself.has_state = onto.State(state_value = 2) # State 2. Idle
        self.model.robotDinoActions.append("stack")
        self.model.robotDinoActCoords.append(self.pathEnd)
        self.targetObjectType = None
        self.pathEnd = None
        self.recorded_objects_handled += 1

        if self.stackAmount == 5:
            self.stackAmount = None
            self.currentStack = None

        if self.recorded_objects_handled == 5:
            self.myAvailableObjectsCoords = []
            self.myAvailableObjectsType = []
            print("RobotID " + str(self.robotID) + "Done with my 5 objects")
            self.done = True

    def idle(self):
        """
        """
        self.model.robotDinoActions.append("idle")
        self.model.robotDinoActCoords.append(self.position)
        self.recorded_steps_idle += 1
        self.currentIdles +=1
        print("Idle: " + str(self.currentIdles))
        if self.currentIdles > 50 and self.myself.has_state.state_value != 1: #not carrying
            self.myself.has_state = onto.State(state_value = 2)
            self.myAvailableObjectsCoords.append(self.pathEnd) # regresarlo para intentarlo despues
            self.myAvailableObjectsType.append(self.targetObjectType)
            self.pathEnd = None
            self.targetObjectType = None
            self.nextTile = None
            print("\n\nSTOP IDLE PLEASE\n")
            self.currentIdles = 0
            
            


class RobotCarro(ap.Agent):
    def see(self,e):
        self.board = e

    def next(self):
        """
        The next function contains the decision making process, where the
        general algorithm of deductive reasoning is executed.
        """
        # For every action in the action list
        for act in self.actions:
        # For every rule in the rule list
            for rule in self.rules:
            # If the action (act) is valid by using the rule (rule)
                if rule(act):
            # return validated action
                    return act
                
    def action(self,act):
        """
        The action function will execute the chosen action (act).
        """
        # If the action exists
        if act is not None:
            act() 
            
    def step(self):
        """
        The agent's step function
        """
        self.see(self.model.boardTiles) # Perception function

        a = self.next() # next function (return chosen action (a))
        self.action(a) # action function (executes action (a))
                        # statistics recordings

    def setup(self):
        self.done = False
        self.robotID = 4
        self.recorded_objects_handled = 0 # stack
        self.recorded_movements_made = 0 # move
        self.recorded_steps_idle = 0 # idle
        self.recorded_avoided_collisions = 0 # move rule
        self.recorded_utility = 0 # pick up
        self.board = [] #not used

        self.lastGoAround = None
        self.currentIdles = 0

        

        self.path = [0,0] #not set

        self.myself = onto.RobotCarroOnto(has_id = self.id)
        self.myself.has_state = onto.State(state_value = 2) # idle
        #print("state: " + str(self.myself.has_state.state_value))
        self.position = self.model.robotList[self.robotID] # Initialize with robot coordinate from unity


        #print("Initial position: " + str(self.position[0]) + ", " + str(self.position[1]))
        #self.myself.has_color = onto.Color(color_value = "Blue")
        self.targetObjectType = None
        self.pathEnd = None # Must be set before moving
        self.nextTile = None

        self.myAvailableObjectsCoords = list(self.model.objCoorList)
        self.myAvailableObjectsType = list(self.model.objTypeList)
        
        # stack
        self.currentStack = None
        self.stackAmount = None

        self.actions = [self.setTarget, self.pickUp, self.stack, self.setNextHorTile, self.setNextVerticalTile, self.goAroundHorizontal, self.goAroundVertical, self.moveTo, self.idle] # The action list 
        self.rules = [self.rule_canSetTarget, self.rule_canPick, self.rule_canStack, self.rule_nextHor,
        self.rule_nextVer, self.rule_goAroundHorizontal, self.rule_goAroundVertical, self.rule_canMove, self.rule_idle] # The rule list 

    def rule_canStack(self,act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If the state is carrying, if path is (0,0), if the pathEnd is adyacent to my position, then i must stack my object”.
        """
        if self.pathEnd is None:
            return False

        rule_validation = [False, False, False]
        
        if self.myself.has_state.state_value == 1: # Im carrying
            rule_validation[0] = True 
        if abs(self.position[0] - self.pathEnd[0]) + abs(self.position[1] - self.pathEnd[1]) == 1:
            rule_validation[1] = True
        if act == self.stack:
            rule_validation[2] = True 
        return all(rule_validation)

    def rule_canPick(self,act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If state is chasing, If path is (0,0), if pathEnd is adyacet to my position tile, , then I must pick it up”.
        """ 
        if self.pathEnd is None:
            return False

        rule_validation = [False,False,False]
        if self.myself.has_state.state_value == 0:
            rule_validation[0] = True 
        if abs(self.position[0] - self.pathEnd[0]) + abs(self.position[1] - self.pathEnd[1]) == 1:
            rule_validation[1] = True
        if act == self.pickUp:
            rule_validation[2] = True 
        return all(rule_validation)


    def rule_canMove(self, act): 
        if self.done:
            return False
        
        rule_validation = [False, False, False]
        #print(f"Checking rule_canMove: nextTile={self.nextTile}, robotList={self.model.robotList}")

        if self.nextTile is not None:
            rule_validation[0] = True 
        if self.nextTile not in self.model.robotList:
            rule_validation[1] = True
        else:
            #print("Collision detected with another robot!")
            self.recorded_avoided_collisions += 1
        if act == self.moveTo:
            rule_validation[2] = True 

        #print(f"rule_canMove validation: {rule_validation}")
        return all(rule_validation)

    def rule_canSetTarget(self,act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If objCoorList is not empty, if pathEndd is None”.
        """
        if self.done:
            return False

        rule_validation = [False,False,False]
        if len(self.myAvailableObjectsCoords) != 0 or self.currentStack != None:
            rule_validation[0] = True 
        if self.pathEnd == None:
            rule_validation[1] = True
        if act == self.setTarget:
            rule_validation[2] = True 
        return all(rule_validation)
        
    def rule_idle(self,act):  
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        If there i
        “”.
        """
        rule_validation = [False]
        if act == self.idle:
            rule_validation[0] = True
        return all(rule_validation)

    def rule_nextHor(self, act): 
        rule_validation = [False, False, False, False, False]
        peekTile = (self.position[0] - 1, self.position[1]) if self.path[0] < 0 else (self.position[0] + 1, self.position[1])
        #print(f"rule_nextHor: path={self.path}, nextTile={self.nextTile}, position={self.position}, peekTile={peekTile}")
        if self.lastGoAround != "X":
            rule_validation[0] = True 
        if self.path[0] != 0:
            rule_validation[1] = True 
        if self.nextTile is None: 
            rule_validation[2] = True
        if peekTile not in self.model.objCoorList and peekTile not in self.model.robotList:
            rule_validation[3] = True
        if act == self.setNextHorTile:
            rule_validation[4] = True 
        #if(all(rule_validation)):
            #print(f"rule_nextHor validation: {rule_validation}")
        return all(rule_validation)


    def rule_nextVer(self, act): 
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If rule_nextHor isn't accomplished (due to collision), this assures the robot moves 1 step vertically”.
        If path.x is not 0, if nextTile is None, if the next tile in x is not occupied
        """
        rule_validation = [False, False, False, False, False]
        peekTile = (self.position[0], self.position[1] - 1) if self.path[1] < 0 else (self.position[0], self.position[1] + 1)
        #print(f"rule_nextVer: path={self.path}, nextTile={self.nextTile}, position={self.position}, peekTile={peekTile}")
        if self.lastGoAround != "Y":
            rule_validation[0] = True
        if self.path[1] != 0:
            rule_validation[1] = True 
        if self.nextTile is None: 
            rule_validation[2] = True
        if peekTile not in self.model.objCoorList and peekTile not in self.model.robotList:
            rule_validation[3] = True
        if act == self.setNextVerticalTile:
            rule_validation[4] = True 
        #
            #print(f"rule_nextVer validation: {rule_validation}")
        return all(rule_validation)
    
    def rule_goAroundHorizontal(self, act):
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If rule_nextHor nor rule_verTile (due to collision or path 0), this assures the robot moves 1 step vertically”.
        If path.y is 0, if nextTile is None, if the next tile in x is not occupied
        """
        rule_validation = [False, False, False, False]
        up_tile = (self.position[0], self.position[1] + 1)
        down_tile = (self.position[0], self.position[1] - 1)
        #print(f"rule_goAroundHorizontal: path={self.path}, nextTile={self.nextTile}, position={self.position}, up_tile={up_tile}, down_tile={down_tile}")
        if self.path[1] == 0:
            rule_validation[0] = True 
        if self.nextTile is None: 
            rule_validation[1] = True
        if (up_tile not in self.model.objCoorList and up_tile not in self.model.robotList) or (down_tile not in self.model.objCoorList and down_tile not in self.model.robotList):
            rule_validation[2] = True
        if act == self.goAroundHorizontal:
            rule_validation[3] = True 
        #if all(rule_validation):
            #print(f"rule_goAroundHorizontal: {rule_validation}")
        return all(rule_validation)
    
    def rule_goAroundVertical(self, act):
        """
        A deduction rule of the type “If A and B then C”. The rule is:
        “If rule_nextHor nor rule_verTile (due to collision or path 0), this assures the robot moves 1 step vertically”.
        If path.x is 0, if nextTile is None, if the next tile in x is not occupied
        """
        rule_validation = [False, False, False, False]
        left_tile = (self.position[0] - 1, self.position[1])
        right_tile = (self.position[0] + 1, self.position[1])
        #print(f"pathEnd: pathEnd={self.pathEnd}, rule_goAroundHorizontal: path={self.path}, nextTile={self.nextTile}, position={self.position}, left_tile={left_tile}, right_tile={right_tile}")
        
        if self.path[0] == 0:
            rule_validation[0] = True 
        if self.nextTile is None: 
            rule_validation[1] = True
        if (left_tile not in self.model.objCoorList and left_tile not in self.model.robotList) or (right_tile not in self.model.objCoorList and right_tile not in self.model.robotList):
            rule_validation[2] = True
        if act == self.goAroundVertical:
            rule_validation[3] = True 
        #if all(rule_validation):
            #print(f"rule_goAroundVertical: {rule_validation}")
        return all(rule_validation)

    def setTarget(self):
        #print("setTarget")
        """
        Set pathEnd
        which the next target coordinate before moving (Stack or Object) 
        Remove the target from the available obj list
        """
        self.model.robotCarroActions.append("thinking")
        self.model.robotCarroActCoords.append(self.position)
        if self.myself.has_state.state_value == 1: # if Im currently carrying
            if self.currentStack == None:
                random_index = random.choice(range(len(self.model.stackList)))
                print("\n\nsetTarget: Going to Stack")
                print("rand Index: " + str(random_index))
                self.currentStack = self.model.stackList[random_index]
                self.model.stackList.remove(self.currentStack)
                self.stackAmount = 0
                self.pathEnd = self.currentStack
            else:
                self.pathEnd = self.currentStack

        elif self.myself.has_state.state_value == 2: # if Im currently idle
            self.myself.has_state = onto.State(state_value = 0) # set state to chasing
            random_index = random.choice(range(len(self.myAvailableObjectsCoords)))
            
            print("\n\nsetTarget: Going for object")
            print("Available objects left: " + str(len(self.myAvailableObjectsCoords)))
            print("Available objects type left: " + str(len(self.myAvailableObjectsType)))
            print("rand Index: " + str(random_index))
            self.pathEnd = self.myAvailableObjectsCoords[random_index]
            self.targetObjectType = self.myAvailableObjectsType[random_index]
            
            del self.myAvailableObjectsType[random_index]
            self.myAvailableObjectsCoords.remove(self.pathEnd)

            """ 
            #print("(" + str(self.model.objCoorList[random_index][0]) + ", " + str(self.model.objCoorList[random_index][1]) + "), ")
            #print("\n")
            
            #print("myAvailableObjectsCoords: ")
            for elem in self.myAvailableObjectsCoords:
                #print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")

            #print("\n")
            #print("myAvailableObjectsType: ")
            for elem in self.myAvailableObjectsType:
                #print(str(elem) + ", ", end=" ")
            """

        print("RobotID: " + str(self.robotID))
        print("pathEnd: (" + str(self.pathEnd[0]) + ", " + str(self.pathEnd[1]) + ")")
        print("targetObjectType: " + str(self.targetObjectType)) 
        print("Current Position: (" + str(self.position[0]) + ", " + str(self.position[1]) + ")")

        
        self.findPath()

    def goAroundHorizontal(self):
        """
        Ignoring path
        Sets nextTile to +1 or -1 in y coor. 
        """
        self.model.robotCarroActions.append("thinking")
        self.model.robotCarroActCoords.append(self.position)
        #print("goAroundHor")
        if (self.position[1] < 18):
            self.nextTile = (self.position[0], self.position[1] + 1)
        else:
            self.nextTile = (self.position[0], self.position[1] - 1)
        self.lastGoAround = "Y"
        
    def goAroundVertical(self):
        """
        Sets nextTile to +1 or -1 in x coor. 
        """
        self.model.robotCarroActions.append("thinking")
        self.model.robotCarroActCoords.append(self.position)
        #print("goAroundVer")
        if (self.position[0] < 18):
            self.nextTile = (self.position[0] + 1, self.position[1])
        else:
            self.nextTile = (self.position[0] - 1, self.position[1])
        self.lastGoAround = "X"
        

    def setNextHorTile(self):
        #print("setNextHorTile")
        self.model.robotCarroActions.append("thinking")
        self.model.robotCarroActCoords.append(self.position)
        if self.path[0] < 0:
            self.nextTile = (self.position[0] - 1, self.position[1])
            #self.path[0] += 1  
        elif self.path[0] > 0: 
            self.nextTile = (self.position[0] + 1, self.position[1])
            #self.path[0] -= 1
        #print(f"setNextHorTile: nextTile={self.nextTile}, path={self.path}")
        self.lastGoAround = None
        

    def setNextVerticalTile(self):
        # #print("setNextVerticalTile")
        self.model.robotCarroActions.append("thinking")
        self.model.robotCarroActCoords.append(self.position)
        if self.path[1] < 0:
            self.nextTile = (self.position[0], self.position[1] - 1)
            #self.path[1] += 1
        elif self.path[1] > 0: 
            self.nextTile = (self.position[0], self.position[1] + 1)
            #self.path[1] -= 1
        #print(f"setNextVerticalTile: nextTile={self.nextTile}, path={self.path}")
        self.lastGoAround = None
        

    def findPath(self):
        self.path[0] = self.pathEnd[0] - self.position[0]
        self.path[1] = self.pathEnd[1] - self.position[1]
        #print(f"findPath: position={self.position}, pathEnd={self.pathEnd}, path={self.path}")

        
    def moveTo(self):
        print(f"Moving to: {self.nextTile}")
        self.model.robotCarroActions.append("move")
        self.position = self.nextTile
        self.model.robotCarroActCoords.append(self.position)
        self.model.robotList[self.robotID] = self.position
        self.recorded_movements_made += 1
        self.nextTile = None
        self.findPath() # Recalculate path from my new position Robot 4: Carro
        self.currentIdles = 0


    def pickUp(self):
        #print("\nPICK UP: ")
        """
        Try To pick up 
        If the robot cant, return the target to the available objList
        """
        #print("targetObjectType: " + str(self.targetObjectType) + ", robotID: " + str(self.robotID))
        if self.targetObjectType == self.robotID:
        
        # si puedo pick up (si es mi tipo de obj) 
            self.myself.has_state = onto.State(state_value = 1) # State 1. Carrying
            self.model.robotCarroActions.append("pickup")
            self.model.robotCarroActCoords.append(self.pathEnd)

            objIndex = self.model.objCoorList.index(self.pathEnd) 

            self.model.objCoorList.remove(self.pathEnd) 
            del self.model.objTypeList[objIndex]

            self.targetObjectType = None
            self.pathEnd = None
            self.recorded_utility += 1
            self.nextTile = None

            
        else:
        # No puedo agarrarlo
            self.myself.has_state = onto.State(state_value = 2) # State 2. Idle
            self.targetObjectType = None
            self.pathEnd = None
            self.nextTile = None
      
    def stack(self):
        """
        Set currentStack a None si stackAmount es 5
        """
        self.stackAmount += 1
        self.myself.has_state = onto.State(state_value = 2) # State 2. Idle
        self.model.robotCarroActions.append("stack")
        self.model.robotCarroActCoords.append(self.pathEnd)
        self.targetObjectType = None
        self.pathEnd = None
        self.recorded_objects_handled += 1

        if self.stackAmount == 5:
            self.stackAmount = None
            self.currentStack = None

        if self.recorded_objects_handled == 5:
            self.myAvailableObjectsCoords = []
            self.myAvailableObjectsType = []
            print("RobotID " + str(self.robotID) + "Done with my 5 objects")
            self.done = True
            
            

    def idle(self):
        """
        """
        self.model.robotCarroActions.append("idle")
        self.model.robotCarroActCoords.append(self.position)
        self.recorded_steps_idle += 1
        self.currentIdles +=1
        print("Idle: " + str(self.currentIdles))
        if self.currentIdles > 50 and self.myself.has_state.state_value != 1: #not carrying
            self.myself.has_state = onto.State(state_value = 2)
            self.myAvailableObjectsCoords.append(self.pathEnd) # regresarlo para intentarlo despues
            self.myAvailableObjectsType.append(self.targetObjectType)
            self.pathEnd = None
            self.targetObjectType = None
            self.nextTile = None
            print("\n\nSTOP IDLE PLEASE\n")
            self.currentIdles = 0
            
class WealthModel(ap.Model):
    def setup(self):


        self.objTypeList = [0] * 5 + [1] * 5 + [2] * 5 + [3] * 5 + [4] * 5
        random.shuffle(self.objTypeList)

        # Generate the 20x20 grid for boardTiles
        self.boardTiles = [[(x, y) for y in range(20)] for x in range(20)]

        # Generate a list of inner board tiles (18x18 grid excluding borders)
        innerBoardTiles = [(x, y) for x in range(1, 19) for y in range(1, 19)]

        # Sample 50 coordinates from the inner board for objCoorList
        self.objCoorList = random.sample(innerBoardTiles, 25)
        for coor in self.objCoorList:
            self.boardTiles[coor[0]][coor[1]] = None  # Mark these as occupied in boardTiles
            innerBoardTiles.remove(coor)

        # Sample 5 coordinates from the inner board for robotList, avoiding the border
        self.robotList = random.sample(innerBoardTiles, 5)

        self.stackList = [(0, y) for y in range(20)] + [(19, y) for y in range(20)]
        
        self.robotCuboActions = []      
        self.robotWarriorActions = []
        self.robotPelotaActions = []
        self.robotDinoActions = []
        self.robotCarroActions = [] 


        self.robotCuboActCoords = []        
        self.robotWarriorActCoords = []
        self.robotPelotaActCoords = []
        self.robotDinoActCoords = []
        self.robotCarroActCoords = [] 

        print("\nobjTypeList:")
        for elem in self.objTypeList:
            
            print(str(elem) + ", ", end=" ")
        print("\nobjCoorList:")
        for elem in self.objCoorList:
            
            print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")

        print("\nrobotList:")
        for elem in self.robotList:
            
            print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")
        
        #print("\nboardtiles")
        #for i in range(0,20,1):
        #    for j in range(0,20,1):
        #        if self.boardTiles[i][j] is not None:
        #            print("(" + str(self.boardTiles[i][j][0]) + ", " + str(self.boardTiles[i][j][1]) + "), ", end=" ")
        #        else:
        #            print("None, ", end=" ")

        """ print("\ninnerBoardTiles")
        for elem in innerBoardTiles:
            print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")
        """
        print("\nstackList")
        for elem in self.stackList:
            
            print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")
                
        for elem in self.robotCuboActions:
            print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")   

        for elem in self.robotCuboActCoords:
            print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")

        # Instantiate all agents
        self.robotCubo_agents = ap.AgentList(self, self.p.robotCubo_agents, RobotCubo)
        self.robotWarrior_agents = ap.AgentList(self,self.p.robotWarrior_agents,RobotWarrior)
        self.robotPelota_agents = ap.AgentList(self,self.p.robotPelota_agents,RobotPelota)
        self.robotDino_agents = ap.AgentList(self,self.p.robotDino_agents,RobotDino)
        self.robotCarro_agents = ap.AgentList(self,self.p.robotCarro_agents,RobotCarro)
        
    def step(self):

        # Call agents' step()
        self.robotCubo_agents.step()
                
        self.robotWarrior_agents.step()
        self.robotPelota_agents.step()
        self.robotDino_agents.step()
        self.robotCarro_agents.step()


    def update(self):

        # Record agents' Gini Coefficient
        #self.record('Gini Coefficient', gini(self.robotCubo_agents.recorded_utility))
        self.record('ObJ Handled over states (robotCubo Agent)', list(self.robotCubo_agents.recorded_objects_handled))
        self.record('Movements Made over states (robotCubo Agent)', list(self.robotCubo_agents.recorded_movements_made))

        # If the simulation has reached max steps then stop simulation
        #if self.t >= self._steps:
        #    self.stop()


    def end(self):

        # Reccord final wealth of all agents
        self.robotCubo_agents.record('recorded_objects_handled')
        self.robotCubo_agents.record('recorded_movements_made')
        # End of simulation message
        #print(f"\nModel ended on step {self.t}\n")
        print("\nRobotCubo ActionsList::")
        for elem in self.robotCuboActions:
            print(str(elem) + ", ", end=" ")

        print("\nRobotCubo CoordsList::")
        for elem in self.robotCuboActCoords:
            if elem is not None:
                print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")
            else:
                print("None, ", end=" ")

        """print("\nRobotWarrior ActionsList::")
        for elem in self.robotWarriorActions:
            print(str(elem) + ", ", end=" ")"""

        print("\nRobotWarrior CoordsList::")
        for elem in self.robotWarriorActCoords:
            if elem is not None:
                print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")
            else:
                print("None, ", end=" ")
                
        """print("\nRobotPelota ActionsList::")
        for elem in self.robotPelotaActions:
            print(str(elem) + ", ", end=" ")"""

        print("\nRobotPelotaCoordsList::")
        for elem in self.robotPelotaActCoords:
            if elem is not None:
                print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")
            else:
                print("None, ", end=" ")

        """print("\nRobotDino ActionsList::")
        for elem in self.robotDinoActions:
            print(str(elem) + ", ", end=" ")"""

        print("\nRobotDino CoordsList::")
        for elem in self.robotDinoActCoords:
            if elem is not None:
                print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")
            else:
                print("None, ", end=" ")
        
        """print("\nRobotCarro ActionsList::")
        for elem in self.robotCarroActions:
            print(str(elem) + ", ", end=" ")"""

        print("\nRobotCarroCoordsList::")
        for elem in self.robotCarroActCoords:
            if elem is not None:
                print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")
            else:
                print("None, ", end=" ")

        print("\nAmount of stacked objects (cubo): " + str(self.robotCubo_agents[0].recorded_objects_handled))
        print("\nAmount of stacked objects (warrior): " + str(self.robotWarrior_agents[0].recorded_objects_handled))
        print("\nAmount of stacked objects (pelota): " + str(self.robotPelota_agents[0].recorded_objects_handled))
        print("\nAmount of stacked objects (dino): " + str(self.robotDino_agents[0].recorded_objects_handled))
        print("\nAmount of stacked objects (carro): " + str(self.robotCarro_agents[0].recorded_objects_handled))

        print("\nobjCoorList:")
        for elem in self.objCoorList:
            
            print("(" + str(elem[0]) + ", " + str(elem[1]) + "), ", end=" ")

model = None

def create_model():
    """
    Initializes and returns the WealthModel.
    """
    global model
    parameters = {
        'robotCubo_agents': 1,
        'robotWarrior_agents': 1,
        'robotPelota_agents': 1,
        'robotDino_agents': 1,
        'robotCarro_agents': 1,
        'steps': 1500,
    }
    model = WealthModel(parameters)
    return model

def plot_results(data):
    """
    Generates all relevant plots using simulation data.
    """
    # Utility values of 5 robots
    utility_keys = [
        "Utility over states (RobotCubo Agent)",
        "Utility over states (RobotWarrior Agent)",
        "Utility over states (RobotPelota Agent)",
        "Utility over states (RobotDino Agent)",
        "Utility over states (RobotCarro Agent)"
    ]
    robot_labels = ["RobotCubo", "RobotWarrior", "RobotPelota", "RobotDino", "RobotCarro"]
    markers = ["o", "s", "^", "d", "*"]
    
    # Plot Utilities
    x = range(len(data[utility_keys[0]]))
    for key, label, marker in zip(utility_keys, robot_labels, markers):
        plt.plot(x, list(data[key]), label=label, marker=marker)
    plt.title('Utility of 5 Robots over steps')
    plt.xlabel('Steps')
    plt.ylabel('Utility')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # Movements Made
    movement_keys = [
        "Movements Made over states (RobotCubo Agent)",
        "Movements Made over states (RobotWarrior Agent)",
        "Movements Made over states (RobotPelota Agent)",
        "Movements Made over states (RobotDino Agent)",
        "Movements Made over states (RobotCarro Agent)"
    ]
    x = range(len(data[movement_keys[0]]))
    for key, label, marker in zip(movement_keys, robot_labels, markers):
        plt.plot(x, list(data[key]), label=label, marker=marker)
    plt.title('Movements made by 5 Robots over steps')
    plt.xlabel('Steps')
    plt.ylabel('Moves')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # Stacks Made
    stack_keys = [
        "Objects Stacked over states (RobotCubo Agent)",
        "Objects Stacked over states (RobotWarrior Agent)",
        "Objects Stacked over states (RobotPelota Agent)",
        "Objects Stacked over states (RobotDino Agent)",
        "Objects Stacked over states (RobotCarro Agent)"
    ]
    x = range(len(data[stack_keys[0]]))
    for key, label, marker in zip(stack_keys, robot_labels, markers):
        plt.plot(x, list(data[key]), label=label, marker=marker)
    plt.title('Stacks made by 5 Robots over steps')
    plt.xlabel('Steps')
    plt.ylabel('Stacks')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Amount of Idle
    idle_keys = [
        "Amount of Idle over states (RobotCubo Agent)",
        "Amount of Idle over states (RobotWarrior Agent)",
        "Amount of Idle over states (RobotPelota Agent)",
        "Amount of Idle over states (RobotDino Agent)",
        "Amount of Idle over states (RobotCarro Agent)"
    ]
    x = range(len(data[idle_keys[0]]))
    for key, label, marker in zip(idle_keys, robot_labels, markers):
        plt.plot(x, list(data[key]), label=label, marker=marker)
    plt.title('Amount of idles by 5 Robots over steps')
    plt.xlabel('Steps')
    plt.ylabel('Idles')
    plt.legend()
    plt.grid(True)
    plt.show()

def run_simulation():
    """
    Runs the simulation and plots results.
    """
    create_model()  
    results = model.run()
    data = results.variables

    print("Simulation finished!")

    # Call the plot_results function to generate plots
    plot_results(data)

__all__ = ["WealthModel", "create_model", "model", "plot_results", "run_simulation"]

