import numpy as np
from randomalgorithm import *
from deterministic import *

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""  Genetic algorithm """""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def selectParents(children, acceptOutsider, chance):
    # The surving parents-to-be are randomly selected from all childs
    # It's possible to accept the introduction of an outsider every round
    
##    scoreList = [c.getPoints() for c in children]
##    minScore = min(scoreList)
##    mean = sum(scoreList)/float(len(children))
##    parents = []
##    for c in children:
##        factor = (c.getPoints() - minScore)/(mean - minScore)
##        if random.random() < factor*chance:
##            parents.append(c)
    children.sort(key = lambda x: x.getPoints())
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
                if not s.hasGroup() and (s.getSize()*OVERBOOK >= len(g.getStudents())):
                    g.newRoomSlot(s)
                    break
    return

def changeSlotMutation(timeTable, factor):
    # Every group had a change to swich places with other group
    for g1 in timeTable.getGroups():
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
    # Students can be made to swich workgroup with another student
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
                    g1.removeStudent(stud1)
                    g2.removeStudent(stud2)
                    g1.addStudent(stud2)
                    g2.addStudent(stud1)
                    stud1.switchGroups(g1,g2)
                    stud2.switchGroups(g2,g1)
    return
    
def mutate(parents, mutations):
    # Parents are mutated before coupling
    fsFactor = mutations[0]
    csFactor = mutations[1]
    sFactor = mutations[2]
    
    for p in parents:
        freeSlotMutation(p, fsFactor)
        changeSlotMutation(p, csFactor)
        studentMutation(p, sFactor)
    return parents

def incestCheck(p1, p2):
    if p1.getParents() == None or p2.getParents() == None:
        return False
    for gp1 in p1.getParents():
        for gp2 in p2.getParents():
            if gp1 == gp2 or gp1 == p2 or gp2 == p1:
                return True
    return False
    
def blindDate(p1, parents, incest):
    # Parents are coupled
    p2 = p1
    if incest == False:
        TO = 0
        while incestCheck(p1, p2) or p1 == p2:
            TO += 1
            p2 = random.choice(parents)
            if TO > 2* len(parents):
                print "Time Out..."
                break
    else:
        i = 0
        while p2 == p1:
            if i > 5* len(parents):
                break
            p2 = random.choice(parents)
            i += 1
    return p2

def freeRoomSlot(child, roomSlot, course):
    # Checking for free roomslots
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

def bedRoom(p1, p2):
    # Making children by recombining two parents. One child is returned

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
        parentC = random.choice([c1[i], c2[i]])
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
    if text == True:
        print "================================="
        print "Initiating genetic algorithm"
        print "================================="
    if initParents == None:
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
        offspring = makeLove(parents, nrChilds - len(parents), allowIncest)
        if text == True: print "Mutating offspring..."
        mutate(offspring, mutations)
        children = parents + offspring
        if text == True: print "Picking new parents..."
        parents = selectParents(children, acceptOutsider, survivorFactor)
        
        maxChild = max(children, key = lambda x: x.getPoints())
        if maxChild.getPoints() > bestChildScore:
            bestChild = maxChild
            bestChildScore = maxChild.getPoints()
            n = 0
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
        if i >= iterations and text == True and goToMax == False:
            q = ""
            print "\n======================"
            print "Evolution review!"
            print "======================"
            print "Total score: \n",evolution
            print "Overbookings: \n",overbookings
            print "Personal conflicts: \n",personal
            print "Spreadding points: \n",spread
            w = ("You want to do another "
                 +str(i)
                 +" iterations? (Y/N): ")
            q = raw_input(w)
            if q == "Y":
                iterations = i*2
                continue
            try: iterations += int(q)
            except: break
        
    return bestChild

scores = {}
def tuneGA(iterations):
    mutL = [
       (0.0, 0.005, 0.025),
       (0.01, 0.005, 0.025),
       (0.005, 0.005, 0.025),
       (0.015, 0.005, 0.025),
       (0.01, 0.000, 0.025),
       (0.01, 0.01, 0.025),
       (0.01, 0.015, 0.025),
       (0.01, 0.02, 0.025),
       (0.01, 0.005, 0.0),
       (0.01, 0.005, 0.02),
       (0.01, 0.005, 0.03),
       (0.01, 0.005, 0.04),
       (0.01, 0.005, 0.05)
       ]
    
    print "============================"
    print "Initiating tuning algorithm"
    print "============================"
##    for f in [0.10, 0.15, 0.2, 0.025]:
##        print "Starting survival factor ",f
##        print "Attempt ",
##        scores['SURVIVOR-'+str(f)] = []
##        for i in range(iterations):
##            print i,
##            schedule = geneticAlgorithm(survivorFactor = f, text = False)
##            schedule.setPoints(getPoints(schedule))
##            scores['SURVIVOR-'+str(f)].append(schedule.getPoints())
##        print "\n",scores['SURVIVOR-'+str(f)]
##    for m in mutL:
##        print "Starting mutation ",m
##        print "Attempt ",
##        scores['MUTATION-'+str(m)] = []
##        for i in range(iterations):
##            print i,
##            schedule = geneticAlgorithm(text = False, mutations = m)
##            schedule.setPoints(getPoints(schedule))
##            scores['MUTATION-'+str(m)].append(schedule.getPoints())
##        print "\n",scores['MUTATION-'+str(m)]
    for b in [False, True]:
        print "Starting genetic variations on ",b
        print "Attempt ",
        scores['INCEST-'+str(b)] = []
##        scores['OUTSIDER-'+str(b)] = []
        for i in range(iterations):
            print i,
            schedule1 = geneticAlgorithm(text = False, allowIncest = b, nrChilds=50)
##            schedule2 = geneticAlgorithm(text = False, acceptOutsider = b)
            schedule1.setPoints(getPoints(schedule1))
##            schedule2.setPoints(getPoints(schedule1))
            scores['INCEST-'+str(b)].append(schedule1.getPoints())
##            scores['OUTSIDER-'+str(b)].append(schedule2.getPoints())
##        print "\nOutsider: ",scores['OUTSIDER-'+str(b)]
        print "Incest: ",scores['INCEST-'+str(b)]
    return scores

def geneticPopulations(nrPop, iterations):
    children = []
    print "========================================"
    print "Initiating genetic populations programme"
    print "========================================"
    for i in range(nrPop):
        print "Evolving population ",i+1,"..."
        child = geneticAlgorithm(iterations, text = False)
        print "Fittest individual has ",child.getPoints()," points."
        children.append(child)
    print "\n================================"
    print "Merging fittest individuals..."
    print "================================"
    bestChild = geneticAlgorithm(
        iterations, initParents = children, mutations = (0.0,0.0,0.025)
        )
    return bestChild
