"""***********************************************************************
* hillclimber.py
*
* Heuristieken
* Daan van den Berg
*
* Contains the hillclimber and it's fellow brother: the simulated hillclimber
* The algorithme needs to be called in the roostering_heursticstics file
* in order to use the timetable and plot the results
*
***********************************************************************"""

import matplotlib.pyplot as plt
from deterministic import *
from randomalgorithm import *


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""" Hillclimbing algorithm """""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def checkChance(score, temp):
    """
    Computes the chance for a certain improvement to be accepted in simulated 
    annealing. If positive: chance > 1, else 0 < chance < 1. 
    There a constant to make minor decreases can happen after a lot of iterations
    """
    rawchance = math.exp(score / temp)
    if score < 0:
        chance = 0.02 / score + 0.98 * rawchance
    else:
        chance = rawchance
    return chance

def selectGroups(groups):
    """
    Randomly selects two groups out of a list .Gets called in checkGroupSwitch
    """
    groupOne = random.choice(groups)
    groupONE = random.choice(groups)
    while(groupOne != groupONE and
    groupOne.getRoomSlot().getSize() < OVERBOOK*len(groupONE.getStudents())
    and groupONE.getRoomSlot().getSize() < OVERBOOK*len(groupOne.getStudents())):
        groupOne = random.choice(groups)
        groupONE = random.choice(groups)
    return groupOne, groupONE

def hillOverbook(students, room):
    """
    Computes malus points for overbooked rooms in checkGroupsSwitch
    """
    saldo = len(students) - room.getSize()
    if saldo > 0:
        return saldo
    else: return 0

def groupPoints(group, students, course, room, newRoom):
    """
    Computes the score an individual groups has. Uses functions from getpoints
    except for hillOverbook, which is custom
    """
    studentMalus = 0
    for student in students:
        studentMalus += studentMalusPoints(student, room, newRoom)
    bonus = spreadBonusPoints(course, newRoom, group)
    spreadMalus = spreadMalusPoints(course, newRoom, group)
    overbookMalus = hillOverbook(students, newRoom)
    saldo = bonus - studentMalus - spreadMalus - overbookMalus
    return saldo

def pointsSaldo(group, newRoom):
    """
    Checks how many points a group wil gain (or lose) when given a new roomslot
    """
    students = group.getStudents()
    course = group.getActivity().getCourse()
    originalRoom = group.getRoomSlot()
    original = groupPoints(group, students, course, originalRoom, originalRoom)
    new = groupPoints(group, students, course, originalRoom, newRoom)
    return new - original

def switchGroups(groupOne, groupONE):
    """
    Switches the roomslots of two groups
    """
    roomSlotOne = groupOne.getRoomSlot()
    roomSlotONE = groupONE.getRoomSlot()
    groupOne.newRoomSlot(roomSlotONE)
    groupONE.newRoomSlot(roomSlotOne)
    roomSlotOne.appointGroup(groupONE)
    roomSlotONE.appointGroup(groupOne)
    return

def checkGroupSwitch(groups, sim = False, temp = None):
    """
    First mutation
    check if the switch of two groups increases the score of the timetable.
    Apply mutation if hillclimber, and apply according to chance when sim. anneal
    """.
    groupOne, groupONE = selectGroups(groups)
    roomOne = groupOne.getRoomSlot()
    roomONE = groupONE.getRoomSlot()
    pointsSaldo1 = pointsSaldo(groupOne, groupONE.getRoomSlot())
    pointsSaldo2 = pointsSaldo(groupONE, groupOne.getRoomSlot())
    score = pointsSaldo1 + pointsSaldo2
    if sim == True:
        if checkChance(score,temp) > random.random():
            switchGroups(groupOne, groupONE)
            return True
        return False
    if score > 0:
        switchGroups(groupOne, groupONE)
        return True
    return False

def switchStudents(stud1,g1,stud2,g2):
    """
    Switch the students from two groups
    """
    g1.removeStudent(stud1)
    g2.removeStudent(stud2)
    g1.addStudent(stud2)
    g2.addStudent(stud1)
    stud1.removeGroup(g1)
    stud2.removeGroup(g2)
    stud1.addGroup(g2)
    stud2.addGroup(g1)

def checkStudentSwitch(groups, sim = False, temp = None):
    """
    Second mutation
    Check if a switch of students from two different groups of the same activity
    increases the score of the timetable and applies mutation according to
    the algorithm in which it's called (sim or hill)
    """
    score = 0
    group = None
    while(True):
        group = random.choice(groups)
        actGroups = group.getActivity().getGroups()
        if len(actGroups) > 1:
            break
    random.shuffle(actGroups)
    stud1 = random.choice(actGroups[0].getStudents())
    room1 = actGroups[0].getRoomSlot()
    stud2 = random.choice(actGroups[1].getStudents())
    room2 = actGroups[1].getRoomSlot()
    score += (studentMalusPoints(stud1) 
        - studentMalusPoints(stud1, room1, room2))
    score += (studentMalusPoints(stud2)
        - studentMalusPoints(stud2, room2, room1))
    if sim == True:
        if checkChance(score,temp) > random.random():
            switchStudents(stud1,actGroups[0],stud2, actGroups[1])
            return True
        return False
    if score > 0:
        switchStudents(stud1,actGroups[0],stud2, actGroups[1])
        return True
    return False

def freeSlotChange(timeTable):
    """
    Third mutation
    Check if a random groups can change to a random free roomslot
    """
    freeSlots = []
    # Free roomslots are listed
    for t in timeTable.getTimeSlots():
        for r in t.getRoomSlots():
            if not r.hasGroup():
                freeSlots.append(r)
    random.shuffle(freeSlots)
    
    for g in timeTable.getGroups():
        for s in freeSlots:
            if not s.hasGroup() and (s.getSize()*OVERBOOK >= len(g.getStudents())):
                if pointsSaldo(g,s) > 0:
                    g.newRoomSlot(s)
                    return True
                else: return False
        

def hillclimbAlgorithm(timeTable, perc_of_iter = 0.7, perc_of_score = 0.01, \
                       sim = False, temperature = 15,minTemp = 0.1, \
                       coolingRate = 0.9995, doPlot = True):
    """
    Main function in hillclimber and simulated annealing that calls the 
    functions above. Simulated annealing is executed when 'sim = True' argument is
    placed. 
    Both the algorithms use the same three mutations: switching two students from 
    different groups of the same activity,switching the roomslots of two random 
    groups and placing a group in a empty roomslot.
    """
    # switch random groups and run getPoints()
    initialScore = getPoints(timeTable)
    highscore = initialScore
    scores = []
    groups = timeTable.getGroups()
    i = 0
    if sim == True:
        while temperature > minTemp:
            if checkStudentSwitch(groups, True, temperature):
                highscore = getPoints(timeTable)
            if checkGroupSwitch(groups, True, temperature):
                highscore = getPoints(timeTable)
            if freeSlotChange(timeTable):
                highscore = getPoints(timeTable)
            scores.append(highscore)
            if(i % 1000 == 0):
                print "Current iteration: ",
                print i
            temperature *= coolingRate
            i += 1
    else:
        growth = 1
        while growth > perc_of_score:
            if checkStudentSwitch(groups):
                highscore = getPoints(timeTable)
            if checkGroupSwitch(groups):
                highscore = getPoints(timeTable)
            if freeSlotChange(timeTable):
                highscore = getPoints(timeTable)
            scores.append(highscore)
            i += 1
            if i % 100 == 0:
                growth = float(highscore - scores[int(i * perc_of_iter)]) \
                         / float(highscore - initialScore)
                if i % 1000 == 0:
                    print "Current iteration: ", i

    timeTable.setPoints(getPoints(timeTable))
    if doPlot == True:
        plt.plot(scores)
        plt.ylabel('points')
        plt.xlabel('iterations')
        plt.show()
    return scores


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""  Simulated annealing   """""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def simulatedAnnealing(timeTable, temperature = 15.0, coolingRate = 0.9995, \
                       doPlot = True):
    """
    Extra function for users who are not familiar with the code and want to use a 
    simulated annealing
    """
    # switch random groups and run getPoints()
    score = getPoints(timeTable)
    highscore = score
    scores = []
    groups = timeTable.getGroups()
    i = 0
    while(temperature > endTemp):
        if(i % 100 == 0):
            print "Current iteration:", i, "current temperature:",temperature
        if checkStudentSwitch(groups, True, temperature):
            highscore = getPoints(timeTable)
        if(checkGroupSwitch(groups, True, temperature)):
            highscore = getPoints(timeTable)
        scores.append(highscore)
        i+=1
        temperature *= coolingRate
    timeTable.setPoints(getPoints(timeTable))
    if doPlot == True:
        plt.plot(scores)
        plt.ylabel('points')
        plt.xlabel('iterations')
        plt.show()
    return
