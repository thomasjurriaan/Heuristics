import matplotlib.pyplot as plt
from deterministic import *
from randomalgorithm import *

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""" Hillclimbing algorithm """""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def checkChance(score, temp):
    rawchance = math.exp(score / temp)
    if score < 0:
        chance = 0.02 / score + 0.98 * rawchance
    else:
        chance = rawchance
    return chance

def selectGroups(groups):
    groupOne = random.choice(groups)
    groupTwo = random.choice(groups)
    while(groupOne != groupTwo and
    groupOne.getRoomSlot().getSize() < OVERBOOK*len(groupTwo.getStudents())
    and groupTwo.getRoomSlot().getSize() < OVERBOOK*len(groupOne.getStudents())):
        groupOne = random.choice(groups)
        groupTwo = random.choice(groups)
    return groupOne, groupTwo

def hillOverbook(students, room):
    saldo = len(students) - room.getSize()
    if saldo > 0:
        return saldo
    else: return 0

def groupPoints(group, students, course, room, newRoom):
    studentMalus = 0
    for student in students:
        studentMalus += studentMalusPoints(student, room, newRoom)
    bonus = spreadBonusPoints(course, newRoom, group)
    spreadMalus = spreadMalusPoints(course, newRoom, group)
    overbookMalus = hillOverbook(students, newRoom)
    saldo = bonus - studentMalus - spreadMalus - overbookMalus
    return saldo

def pointsSaldo(group, newRoom):
    students = group.getStudents()
    course = group.getActivity().getCourse()
    originalRoom = group.getRoomSlot()
    original = groupPoints(group, students, course, originalRoom, originalRoom)
    new = groupPoints(group, students, course, originalRoom, newRoom)
    return new - original

def switchGroups(groupOne, groupTwo):
    roomSlotOne = groupOne.getRoomSlot()
    roomSlotTwo = groupTwo.getRoomSlot()
    groupOne.newRoomSlot(roomSlotTwo)
    groupTwo.newRoomSlot(roomSlotOne)
    roomSlotOne.appointGroup(groupTwo)
    roomSlotTwo.appointGroup(groupOne)
    return

def checkGroupSwitch(groups, sim = False, temp = None):
    groupOne, groupTwo = selectGroups(groups)
    roomOne = groupOne.getRoomSlot()
    roomTwo = groupTwo.getRoomSlot()
    pointsSaldo1 = pointsSaldo(groupOne, groupTwo.getRoomSlot())
    pointsSaldo2 = pointsSaldo(groupTwo, groupOne.getRoomSlot())
    score = pointsSaldo1 + pointsSaldo2
    if sim == True:
        if checkChance(score,temp) > random.random():
            switchGroups(groupOne, groupTwo)
            return True
        return False
    if score > 0:
        switchGroups(groupOne, groupTwo)
        return True
    return False

def switchStudents(stud1,g1,stud2,g2):
    g1.removeStudent(stud1)
    g2.removeStudent(stud2)
    g1.addStudent(stud2)
    g2.addStudent(stud1)
    stud1.removeGroup(g1)
    stud2.removeGroup(g2)
    stud1.addGroup(g2)
    stud2.addGroup(g1)

def checkStudentSwitch(groups, sim = False, temp = None):
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

def freeSlotChange():
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
        

def hillclimbAlgorithm(timeTable, iterations = 1000, sim = False, temperature = 15, coolingRate = 0.9995, doPlot = True):
    # switch random groups and run getPoints()
    highscore = getPoints(timeTable)
    scores = []
    groups = timeTable.getGroups()
    for i in range(iterations):
        if sim == True:
            if checkStudentSwitch(groups, True, temperature):
                highscore = getPoints(timeTable)
            if checkGroupSwitch(groups, True, temperature):
                highscore = getPoints(timeTable)
            if freeSlotChange():
                highscore = getPoints(timeTable)
        else:
            if checkStudentSwitch(groups):
                highscore = getPoints(timeTable)
            if checkGroupSwitch(groups):
                highscore = getPoints(timeTable)
            if freeSlotChange():
                highscore = getPoints(timeTable)
        scores.append(highscore)
        if(i % 250 == 0):
            print "Current iteration: ",
            print i
    timeTable.setPoints(getPoints(timeTable))
    if doPlot == True:
        plt.plot(scores)
        plt.ylabel('points')
        plt.xlabel('iterations')
        plt.show()
    return

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""  Simulated annealing   """""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def simulatedAnnealing(timeTable, temperature = 15.0, coolingRate = 0.9995, doPlot = True):
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