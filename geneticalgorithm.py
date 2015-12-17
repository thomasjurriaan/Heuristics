import numpy as np
from randomalgorithm import *
from deterministic import *
import matplotlib.pyplot as plt

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""  Genetic algorithm """""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def selectParents(children, acceptOutsider, chance):
    """
    Subfunction of geneticAlgorithm()
    
    The surving parents-to-be are selected from the best childs
    It's possible to accept the introduction of an outsider every round
    """

####    # Function to choose parents with chance proportional to their points
####    # This function had a negative effect on the evolution of the population
##    scoreList = [c.getPoints() for c in children]
##    mean = sum(scoreList)/float(len(children))
##    smoothness = 18.0
##    parents = []
##    for c in children:
##        # This function is used in Fermi-Dirac statistic. The function behaves
##        # like a step function from 0 to 100% for a smoothness near 0
##        factor = 2/(math.exp((mean - c.getPoints())/smoothness) + 1)
##        if random.random() < factor*chance:
##            parents.append(c)

    children.sort(key = lambda x: x.getPoints()) #Children are sorted on points
    nr = int(chance*len(children))
    parents = children[-nr:]
    while(len(parents) < 3): parents.append(random.choice(children))
    
    if acceptOutsider == True:
        child = None
        while not allCoursesScheduled(child):
            child = createTimeTableInstance()
            randomAlgorithm(child)
        parents.append(child)
        child.setPoints(getPoints(child))
    random.shuffle(parents)
    
    return parents

def freeSlotMutation(timeTable, factor):
    """
    Subfunction of mutate()
    
    Moves groups to new, free roomslots
    """
    freeSlots = []
    # Free roomslots are listed
    for t in timeTable.getTimeSlots():
        for r in t.getRoomSlots():
            if not r.hasGroup():
                freeSlots.append(r)
    random.shuffle(freeSlots)
    
    for g in timeTable.getGroups():
        # Every group has a chance to change roomslots
        if random.random() <= factor:
            for s in freeSlots:
                if (not s.hasGroup()
                    and (s.getSize()*OVERBOOK >= len(g.getStudents()))
                         ):
                    g.newRoomSlot(s)
                    break
    return

def changeSlotMutation(timeTable, factor):
    """
    Subfunction of mutate()
    
    Switches groups with each others timeslots
    """

    for g1 in timeTable.getGroups():
        # Every group had a change to swich places with other groups
        if random.random() <= factor:
            groups2 = timeTable.getGroups()
            random.shuffle(groups2)
            for g2 in groups2:
                room1 = g1.getRoomSlot()
                room2 = g2.getRoomSlot()
                if (room1.getSize()*OVERBOOK >= len(g2.getStudents())
                    and room2.getSize()*OVERBOOK >= len(g1.getStudents())):
                    g1.newRoomSlot(room2)
                    g2.newRoomSlot(room1)
                    break
    return

def studentMutation(timeTable, factor):
    """
    Subfunction of mutate()
    
    Switches students from one group to another
    """
    activities = []
    for g in timeTable.getGroups():
        if len(g.getActivity().getGroups()) > 1:
            activities.append(g.getActivity())
    for a in activities:
        if random.random() <= math.sqrt(factor):
            for g1 in a.getGroups():
                if random.random() <= math.sqrt(factor):
                    g2 = g1
                    while g2 == g1:
                        g2 = random.choice(a.getGroups())
                    stud1 = random.choice(g1.getStudents())
                    stud2 = random.choice(g2.getStudents())
                    # The data structure is updated
                    g1.removeStudent(stud1)
                    g2.removeStudent(stud2)
                    g1.addStudent(stud2)
                    g2.addStudent(stud1)
                    stud1.removeGroup(g1)
                    stud2.removeGroup(g2)
                    stud1.addGroup(g2)
                    stud2.addGroup(g1)
    return
    
def mutate(parents, mutations):
    """
    Subfunction of geneticAlgorithm()
    
    Function that mutates an existing timetable
    There are three mutations:
        - move groups to free roomslot
        - switch the roomslot of two groups
        - switch two students of the same activity

    The variable 'mutations' is a tuple of three floats
    """
    fsFactor = mutations[0]
    csFactor = mutations[1]
    sFactor = mutations[2]
    
    for p in parents:
        freeSlotMutation(p, fsFactor)
        changeSlotMutation(p, csFactor)
        studentMutation(p, sFactor)
    return

def incestCheck(p1, p2):
    """
    Subfunction of blindDate()
    
    The user can request to make sure there are nog parent-parent matches
    where the parents are (half)brothers/-sisters or parent-child related
    """
    if p1.getParents() == None or p2.getParents() == None:
        return False
    for gp1 in p1.getParents():
        for gp2 in p2.getParents():
            if gp1 == gp2 or gp1 == p2 or gp2 == p1:
                return True
    return False
    
def blindDate(p1, parents, incest):
    """
    Subfunction of makeLove()
    
    A match for a parent is returned
    Incest can be forbidden
    """
    p2 = p1
    if len(parents) == 1:
        # There must be another parent
        return p2
    if incest == False:
        TO = 0
        while incestCheck(p1, p2) or p1 == p2:
            TO += 1
            p2 = random.choice(parents)
            if TO > 2* len(parents):
                #Sometimes the entire population is related
                print "Time Out..."
                break
    else:
        while p2 == p1:
            p2 = random.choice(parents)
    return p2

def freeRoomSlot(child, roomSlot, course):
    """
    Subfunction of geneticAlgorithm()
    
    Checks is roomslot is free to use for a course
    """
    roomName = roomSlot.getRoom()
    time = roomSlot.getTimeSlot().getTime()
    day = roomSlot.getTimeSlot().getDay()
    for t in child.getTimeSlots():
        if t.getDay() == day and t.getTime() == time:
            for r in t.getRoomSlots():
                if r.getRoom() == roomName:
                    if not r.hasGroup():
                        if not courseInTimeSlot(course, r):
                            return r
                        else: return False
                    else: return False

def groupPoints(group):
    """
    Subfunction of coursePoints()
    
    Counts the malus points of the student and overbook points of a group
    """
    students = group.getStudents()
    room = group.getRoomSlot()
    studentMalus = 0
    for student in students:
        studentMalus += studentMalusPoints(student)
    overbookMalus = overbookMalusPoints(room)
    return studentMalus + overbookMalus

def coursePoints(course):
    """
    Subfunction of chooseCourse()
    
    Counts all the fitness-points of a group
    """
    groups = sum([a.getGroups() for a in course.getActivities()],[])
    groupMalusPoints = 0
    for g in groups:
        groupMalusPoints += groupPoints(g)
    bonusPoints = spreadBonusPoints(course)
    malusPoints = spreadMalusPoints(course)
    points = bonusPoints - malusPoints - groupMalusPoints
    return points

def chooseCourse(c1, c2):
    """
    Subfunction of bedroom()
    
    On the basis of the total points of two courses, some courses have a
    higher chance to be picked for recombination. This is a heuristic addition.
    c1 and c2 are the two parent courses. The chosen course is returned
    """
    smoothness = 5.0
    points1 = coursePoints(c1)
    points2 = coursePoints(c2)
    mean = (points1 + points2)/2.0
    course = c1
    low = points1
    if points2 < points1:
        course = c2
        low = points2
    # The following function is known from Fermi-Dirac statistics. The function
    # behaves like a step function from 0 to 100% for a smoothness near 0
    chance = 1/(math.exp(abs(mean - low)/smoothness) + 1)
    if random.random() > chance:
        if course == c1:
            course = c2
        else: course = c1    
    return course

def bedRoom(p1, p2):
    """
    Subfunction of makeLove()
    
    You know what's going on here...
    Two parents take some time and return a child
    """

    # Empty timetable instance is created
    child = createTimeTableInstance([p1, p2])
    if len(p1.getCourses()) != len(p2.getCourses()):
        raise StandardError("TimeTables are of different species")
    badGroups = []
    c1 = p1.getCourses()
    c2 = p2.getCourses()
    coursePointers = child.getCoursePointers()
    studentPointers = child.getStudentPointers()

    courseNr = range(len(c1))
    random.shuffle(courseNr)
    for i in courseNr:
        # The timetables are recombined by choosing courses of both timetables
        # The courses are a 29th part of the genes of each timetable and are
        # chosen because the Building Block Hypothesis requests large building
        # blocks, large sections of genes
        parentC = chooseCourse(c1[i], c2[i])
        course = coursePointers[parentC.getName()]
        groups = sum([a.getGroups() for a in parentC.getActivities()],[])
        for parentG in groups:
            activityName = parentG.getActivity().getType()
            actPointers = course.getPointers()
            activity = actPointers[activityName]
            students = [
                studentPointers[s.getName()] for s in parentG.getStudents()
                ]
            room = freeRoomSlot(child, parentG.getRoomSlot(), course)
            if  room != False:
                group = Group(
                    activity, students, parentG.getMaxStudents(), room
                    )
                child.addGroup(group)
            else:
                badGroups.append([activity, students])

    # The algorithm tries to schedule the groups that didn't fit in their
    # original roomslot
    roomSlots = sum([t.getRoomSlots() for t in child.getTimeSlots()],[])
    freeRoomSlots = [r for r in roomSlots if not r.hasGroup()]
    random.shuffle(freeRoomSlots)
    for g in badGroups:
        try: bookRandomRoom(g[0], freeRoomSlots, g[1], child)
        except: return None
    child.setPoints(getPoints(child))
    return child

def makeLove(parents, n, incest):
    """
    Subfunction of geneticAlgorithm()
    
    Matches parents and sends them to the bedroom(), returns children
    """
    
    cpp = int(n/float(len(parents)))
    children = []
    for p1 in parents:
        for i in range(cpp):
            p2 = blindDate(p1, parents, incest)
            newChild = bedRoom(p1, p2)
            if newChild != None: children.append(newChild)
    while len(children) < n:
        p1 = random.choice(parents)
        p2 = blindDate(p1, parents, incest)
        newChild = bedRoom(p1, p2)
        if newChild != None: children.append(newChild)
    return children

def geneticAlgorithm(
    iterations = 25, acceptOutsider = False, text = True, allowIncest = True, 
    survivorFactor = 0.15, mutations = (0.01, 0.005, 0.025), nrChilds = 30,
    initParents = None, goToMax = False
    ):
    """
    The actual algorithm
        - An outsider can be added to the parents each generation
        - The output of text can be blocked
        - Incest can be forbidden
        - Initial parents can be presented to evolve, instead of random parents
        - goToMax will make the evolution continue until no improvements are
            found for 20 generations

    The algorithm returns the best child. This does not have to be the last
    generation.
    """
        
    if text == True:
        print "================================="
        print "Initiating genetic algorithm"
        print "================================="
    if initParents == None:
        # A number of random parents is created and the best are selected
        tryChildren = []
        for i in range(nrChilds*5):
            if i % nrChilds == 0 and text == True:
                print i," timetables created..."
            table = None
            while not allCoursesScheduled(table):
                table = createTimeTableInstance()
                randomAlgorithm(table)
            tryChildren.append(table)
            table.setPoints(getPoints(table))
        tryChildren.sort(key = lambda x: x.getPoints()) 
        children = tryChildren[-nrChilds:]
        if text == True: print "Picking parents..."
        parents = selectParents(children, acceptOutsider, survivorFactor)
    else: parents = initParents

    bestEvolution = []
    evolution = []
    overbookings = []
    spread = []
    personal = []
    bestChildScore = 0
    i = 0
    n = 0
    while i < iterations or goToMax:
        i += 1
        n += 1
        if text == True:
            print "\n========================"
            print "Starting iteration ",i
            print "========================"

            print "Parent points this generation: "
            for p in parents:
                print p.getPoints(),
            print "\nMaking new children..."
        # The offspring of the parents is created, mutated and new parents are
        # selected
        offspring = makeLove(parents, nrChilds - len(parents), allowIncest)
        if text == True: print "Mutating offspring..."
        mutate(offspring, mutations)
        children = parents + offspring
        if text == True: print "Picking new parents..."
        parents = selectParents(children, acceptOutsider, survivorFactor)

        # The children are sorted on fitness. The evolution of all fitness
        # parameters is monitored
        maxChild = max(children, key = lambda x: x.getPoints())
        if maxChild.getPoints() > bestChildScore:
            bestChild = maxChild
            bestChildScore = maxChild.getPoints()
            n = 0
        bestEvolution.append(int(bestChildScore))
        evolution.append(int(np.mean([c.getPoints() for c in children])))
        overbookings.append(int(np.mean([overbooked(c) for c in children])))
        spread.append(int(np.mean([
            coursesMaximallySpread(c) - activityConflict(c) for c in children
            ])))
        personal.append(int(np.mean([
            personalScheduleConflict(c) for c in children
            ])))
        if n > 20:
            goToMax = False
        # The evolution is displayed and more iterations can be done
        if i >= iterations and text == True and goToMax == False:
            q = ""
            print "\n======================"
            print "Evolution review!"
            print "======================"
            print "Total score: \n",evolution
            print "Overbookings: \n",overbookings
            print "Personal conflicts: \n",personal
            print "Spreadding points: \n",spread
            w = ("You want to do another " + str(i) + " iterations? (Y/N): ")
            q = raw_input(w)
            if q == "Y":
                iterations = i*2
                continue
            try: iterations += int(q)
            except: break

    return bestChild
