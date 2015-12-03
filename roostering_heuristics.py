import json
import random
import math
import itertools
import copy
import matplotlib.pyplot as plt
import numpy as np
import cProfile

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""" Global Variables """""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def getData(filename):
    """
    Reads the json-file with the schedule data
    Returns a list of dictionaries
    """
    json_data=open(filename).read()
    return json.loads(json_data)
STUDENTS = 'students.json'
COURSES = 'coursesInf.json'
STUDENTDATA = getData(STUDENTS)
COURSEDATA = getData(COURSES)
ROOMS = {
    #Room name, room for nr students"
    "A1.04":41,
    "A1.06":22,
    "A1.08":20,
    "A1.10":56,
    "B0.201":48,
    "C0.110":117,
    "C1.112":60
    }

OVERBOOK = 1.2 # Rooms can be overbooked by this percentage
ITERATIONS = 1000

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""" Data Structure """""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

class Student(object):
    def __init__(self, firstName, lastName, studntNr, courses, courseList):
        self.firstName = firstName
        self.lastName = lastName
        self.nr = studntNr
        # self.courses is een lijst van course class-instanties
        self.courses = []
        for c in courses:
            for e in courseList:
                if c == e.getName():
                    self.courses.append(e)
                    e.addStudent(self)
                    break
            else: raise StandardError("Course " + c + " for student " +
                                      self.getName() + " does not exist")
        self.groups = []
    def getName(self):
        return self.firstName+' '+self.lastName
    def getNr(self):
        #python cant return int??
        return self.nr
    def getCourses(self):
        return self.courses
    def doesCourse(self, course):
        #check of course wel een class-instance is?
        return course in self.courses
    def addGroup(self, group):
        self.groups.append(group)
    def getGroups(self):
        return self.groups

class TimeTable(object):
    def __init__(self, parents):
        #include 4 empty time slots for every day of the week.
        l = []
        self.days = ['mo','tu','we','th','fr']
        for d in self.days:
            for t in range(4):
                l.append(TimeSlot(d,t))
        self.timeSlots = l
        self.students = []
        self.courses = []
        self.groups = []
        self.parents = parents
    def addStudent(self, student):
        self.students.append(student)
    def getStudents(self):
        return self.students
    def addCourse(self, course):
        self.courses.append(course)
    def getCourses(self):
        return self.courses
    def addGroup(self, group):
        self.groups.append(group)
    def getGroups(self):
        return self.groups
    def resetTimeSlots(self):
        self.timeSlots = []
        for d in self.days:
            for t in range(4):
                self.timeSlots.append(TimeSlot(d,t))
    def getTimeSlots(self):
        return self.timeSlots
    def getDayTimeSlots(self, day):
        for n, d in enumerate(self.days):
            if day==d:
                return self.timeSlots[(4*n):(4*n+4)]
    def getParents(self):
        return self.parents

class TimeSlot(object):
    # Each timeslot-instance contains 7 available rooms
    def __init__(self, day, time):
        # 'i' is a number in range 20.
        self.time = time
        self.day = day
        self.roomSlots = []
        for r in ROOMS:
            self.roomSlots.append(RoomSlot(r,ROOMS[r],self))
    def isFullyBooked(self):
        #Returns True if all rooms are booked. False otherwise
        return all([r.hasGroup for r in self.roomSlots])
    def getTime(self):
        return self.time
    def getDay(self):
        return self.day
    def printTime(self):
        return str(2*self.time+9)+"h till "+str(2*self.time+11)+"h."
    def getRoomSlots(self):
        return self.roomSlots
    
class RoomSlot(object):
    def __init__(self, room, size, timeSlot):
        self.room = room
        self.size = size
        self.timeSlot = timeSlot
        self.group = None
    def getRoom(self):
        return self.room
    def getTimeSlot(self):
        return self.timeSlot
    def getSize(self):
        return self.size
    def hasGroup(self):
        return self.group != None
    def appointGroup(self, group):
        self.group = group
    def reset(self):
        self.group = None
    def getGroup(self):
        return self.group
    def getStudents(self):
        if self.group == None:
            return None
        else: return self.group.getStudents()

class Course(object):
    def __init__(
        self, courseName, lectures, seminar, maxseminar, practica, maxPractica
        ):
        self.students = []
        self.lectures = [Activity("lecture"+str(i),self)
                         for i in range(lectures)]
        self.seminar = [Activity("seminar"+str(i), self, maxseminar)
                        for i in range(seminar)]
        self.practica = [Activity("practicum"+str(i), self, maxPractica)
                         for i in range(practica)]
        self.courseName = courseName
    def addStudent(self,student):
        self.students.append(student)
    def getActivities(self):
        return self.lectures+self.seminar+self.practica
    def getStudents(self):
        return self.students
    def getName(self):
        return self.courseName

class Activity(object):
    def __init__(self, workType, course, maxStudents = float('inf')):
        # Worktype is 'lecture', 'seminar' or 'practicum'
        self.type = workType
        self.course = course
        self.maxStudents = maxStudents
        self.groups = []
    def getCourse(self):
        return self.course
    def getMaxStudents(self):
        return self.maxStudents
    def getType(self):
        return self.type
    def addGroup(self,group):
        self.groups.append(group)
    def getGroups(self):
        return self.groups

class Group(object):
    def __init__(self, activity, students, maxStudents, roomSlot):
        self.activity = activity
        self.students = students
        self.maxStudents = maxStudents
        self.roomSlot = roomSlot
        roomSlot.appointGroup(self)
        for s in students:
            s.addGroup(self)
        activity.addGroup(self)
    def getActivity(self):
        return self.activity
    def getStudents(self):
        return self.students
    def getMaxStudents(self):
        return self.maxStudents
    def isValid(self):
        return len(self.students) <= self.maxStudents
    def getRoomSlot(self):
        return self.roomSlot
    def newRoomSlot(self, roomSlot):
        self.roomSlot.reset()
        self.roomSlot = roomSlot
        roomSlot.appointGroup(self)
    def removeStudent(self, student):
        self.students = [s for s in self.students if s != student]
    def addStudent(self, student):
        self.students.append(student)


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""  Counting points """""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def allCoursesScheduled(timeTable):
    if timeTable == None: return False
    
    students = timeTable.getStudents()
    for s in students:
        nrAct = 0
        for c in s.getCourses():
            nrAct += len(c.getActivities())
        nrGr = len(s.getGroups())
        if nrAct > nrGr:
            return False
    return True

def checkCount(dList, nrAct):
    L2 = [set(["mo", "th"]), set(["tu", "fr"])]
    L3 = set(["mo", "we", "fr"])
    L4 = set(["mo", "tu", "th", "fr"])
        
    for d in dList:
        if nrAct == 2 and set(d) in L2:
            return True
        if nrAct == 3 and set(d) == L3:
            return True
        if nrAct == 4 and set(d) == L4:
            return True
    return False

def spreadBonusPoints(c, r = None, group = None):
    nrAct = len(c.getActivities())
    if nrAct < 2 or nrAct > 4:
        return 0
    cDays = []
    for a in c.getActivities():
        aDays = []
        for g in a.getGroups():
            if g == group and r != None:
                d = r.getTimeSlot().getDay()
                print "hello"
            else:
                d = g.getRoomSlot().getTimeSlot().getDay()
            aDays.append(d)
        cDays.append(aDays)
    # Cartesian product
    aPoss = [list(v) for v in itertools.product(*cDays)]
    if checkCount(aPoss, nrAct):
        return 20
    return 0

def coursesMaximallySpread(timeTable):
    courses = timeTable.getCourses()
    bonus = 0
    for c in courses:
        bonus += spreadBonusPoints(c)            
    return bonus

def overbookMalusPoints(r):
    if (r.getStudents() != None):
        saldo = len(r.getStudents()) - r.getSize()
        if saldo > 0:
            return saldo
        else: return 0
    else: return 0

def overbooked(timeTable):
    malus = 0
    saldo = 0;
    ts = timeTable.getTimeSlots()
    rs = []
    for t in ts:
        rs += t.getRoomSlots()
    for r in rs:
        malus += overbookMalusPoints(r)
    return malus

def studentMalusPoints(s):
    individualMalus = 0
    cList = []
    for c in s.getGroups():
        if c.getRoomSlot().getTimeSlot() in cList:
            individualMalus += 1
        cList.append(c.getRoomSlot().getTimeSlot())
    return individualMalus

def personalScheduleConflict(timeTable):
    students = timeTable.getStudents()
    malus = 0
    # Loop over lijst met students heen
    for s in students:
        malus += studentMalusPoints(s)
    return malus

##def activityConflict(timeTable):
##    courses = timeTable.getCourses()
##    points = 0
##    for c in courses:
##        cList = []
##        for a in c.getActivities():
##            L = []
##            for g in a.getGroups():
##                day = g.getRoomSlot().getTimeSlot().getDay()
##                L.append(day)
##            cList.append(L)
##        print cList
##        for i, a in enumerate(cList):
##            for ii, aa in enumerate(cList):
##                if ii > i:
##                    l = [e for e in a if e not in aa]
##                    l += [e for e in aa if e not in a]
##                    if len(l) == 0: points += 10
##    return points

def spreadMalusPoints(c, r = None, group = None):
    malus = 0
    nrAct = 0
    days = []
    for a in c.getActivities():
        nrAct += 1
        for g in a.getGroups():
            if g == group and r != None:
                day = r.getTimeSlot().getDay()
                print "goodday"
            else:
                day = g.getRoomSlot().getTimeSlot().getDay()
            days.append(day)
    if nrAct > len(set(days)): malus += 10
    return malus

def activityConflict(timeTable):
    courses = timeTable.getCourses()
    malus = 0
    for c in courses:
        malus += spreadMalusPoints(c)
    return malus

def getPoints(timeTable):
    # Calculates the points of the timeTable
    # Looks for bonus points(20 for each maximally spreaded course)
    # Looks for malus points(1 for each student-specific conflict,
    # 1 for each overbooked student, 10 for each double scedueled course
    # on one day)
    if allCoursesScheduled(timeTable):
        points = 1000
        points += coursesMaximallySpread(timeTable)
        points -= activityConflict(timeTable)
        points -= overbooked(timeTable)
        points -= personalScheduleConflict(timeTable)
    else: points = None
    return points


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""  Random booking algorithm     """""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def courseInTimeSlot(course, roomSlot):
    timeSlot = roomSlot.getTimeSlot()
    for r in timeSlot.getRoomSlots():
        if r.hasGroup():
            group = r.getGroup()
            if course == group.getActivity().getCourse():
                return True
    return False

def roomIsValid(roomSlot, students, activity):
    r = roomSlot
    if (
        not r.hasGroup() and
        r.getSize()*OVERBOOK >= len(students) and
        not courseInTimeSlot(activity.getCourse(), r)
        ): return True
    return False

def bookRandomRoom(activity, randomRoomSlots, students, timeTable):
    # Tries to book an activity in a room. If succeeded: returns the booked
    # group
    for r in randomRoomSlots:
        if roomIsValid(r, students, activity):
            group = Group(activity, students, activity.getMaxStudents(), r)
            timeTable.addGroup(group)
            return
    else: raise StandardError("No room can be found for " +
                              activity.getCourse().getName())

    
def split(activity):
    # Takes an activity with more students than allowed per group and returns
    #lists of valid student groups
    numberOfGroups = math.ceil(len(activity.getCourse().getStudents())
                               /float(activity.getMaxStudents()))
    activityStudents = activity.getCourse().getStudents()
    random.shuffle(activityStudents)
    numberStud = len(activityStudents)/numberOfGroups
    studentGroups = []
    for i in range(int(numberOfGroups)):
        newStudentGroup = activityStudents[
            int(i*numberStud):int((i+1)*numberStud)
            ]
        studentGroups.append(newStudentGroup)
    return studentGroups


def bookActivity(activity, randomRoomSlots, timeTable):
    # Splits activities in valid groups and tries to book them
    if activity.getMaxStudents() < len(activity.getCourse().getStudents()):
        studentGroups = split(activity)
    else: studentGroups = [activity.getCourse().getStudents()]

    for g in studentGroups:
        try: bookRandomRoom(activity, randomRoomSlots, g, timeTable)
        except: break
    return
        
def randomAlgorithm(timeTable):
    # Make list of random activities
    courses = timeTable.getCourses()
    randomActivities = []
    for c in courses:
        randomActivities += c.getActivities()
    random.shuffle(randomActivities)
    
    # Make list of random timeslots
    randomRoomSlots = []
    for t in timeTable.getTimeSlots():
        randomRoomSlots += t.getRoomSlots()
    random.shuffle(randomRoomSlots)
    
    # Use bookRandomRoom to go from activities to groups and book those groups
    for activity in randomActivities:
        bookActivity(activity, randomRoomSlots, timeTable)

    # The timeTable is updated and doesn't have to be returned explicitly
    return


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""  Deterministic booking algorithm"""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def determisticSchnizlle(timeTable):
    # Make list of random activities
    courses = timeTable.getCourses()
    randomActivities = []
    for c in courses:
        randomActivities += c.getActivities()
    random.shuffle(randomActivities)
    
    # Make list of random timeslots
    randomRoomSlots = []
    for t in timeTable.getTimeSlots():
        randomRoomSlots += t.getRoomSlots()
    random.shuffle(randomRoomSlots)
    
    # Use bookRandomRoom to go from activities to groups and book those groups
    for activity in randomActivities:
        bookActivity(activity, randomRoomSlots, timeTable)

    # The timeTable is updated and doesn't have to be returned explicitly
    return

def determisticSchnizlle(timeTable):
    # Make list of random activities
    courses = timeTable.getCourses()

    for c in courses:
        pass
    return
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""" Hillclimbing algorithm """""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
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

def groupPoints(group, students, course, room):
    saldo = 0
    for student in students:
        saldo -= studentMalusPoints(student)
    saldo += spreadBonusPoints(course, room, group)
    saldo -= spreadMalusPoints(course, room, group)
    saldo -= hillOverbook(students, room)
    return saldo

def pointsSaldo(group, newRoom):
    students = group.getStudents()
    course = group.getActivity().getCourse()
    originalRoom = group.getRoomSlot()
    original = groupPoints(group, students, course, originalRoom)
    new = groupPoints(group, students, course, newRoom)
    return new - original

def switch(groupOne, groupTwo, groups):
    roomSlotOne = groupOne.getRoomSlot()
    groupTwo.getRoomSlot().appointGroup(groupOne)
    roomSlotOne.appointGroup(groupTwo)
    groupOne.newRoomSlot(groupTwo.getRoomSlot())
    groupTwo.newRoomSlot(roomSlotOne)

def hillclimbAlgorithm(timeTable, score, iterations):
    print "\n\n\n\n\n......................................................."
    # switch random groups and run getPoints()
    highscore = score
    scores = []
    groups = timeTable.getGroups()
    for i in range(iterations):
        groupOne, groupTwo = selectGroups(groups)
        switch(groupOne, groupTwo, groups)
        #score = pointsSaldo(groupOne, groupTwo.getRoomSlot()) + pointsSaldo(groupTwo, groupOne.getRoomSlot())
        score = getPoints(timeTable)
        if((score > highscore)):
            highscore = score
        else: 
            switch(groupTwo, groupOne, groups)
        scores.append(highscore)
        if(i % 10 == 0):
            print "Current iteration: "
            print i 
    return scores

'''def hillclimbAlgorithm(timeTable, score, iterations):
    print "\n\n\n\n\n......................................................."
    # switch random groups and run getPoints()
    scores = []
    groups = timeTable.getGroups()
    for i in range(iterations):
        groupOne, groupTwo = selectGroups(groups)
        score = pointsSaldo(groupOne, groupTwo.getRoomSlot()) + pointsSaldo(groupTwo, groupOne.getRoomSlot())
        print "score:  ",score
        if score > 0:
            print "current score is higher than the highest score"
            highscore = getPoints(timeTable)
            scores.append(highscore)
            switch(timeTable, groupOne, groupTwo, groups)
        if(i % 50 == 0):
            print "Current iteration: "
            print i 
    print scores
    print max(scores)'''

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""  Simulated annealing   """""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def simulatedAnnealing(timeTable, score, temperature = 20.0, coolingRate = 0.999):
    highscore = score
    scores = []
    chances = []
    groups = timeTable.getGroups()
    i = 0
    while(temperature > 3):
        if(i % 10 == 0):
            print "                 Current iteration: ", i
        oldscore = score
        groupOne, groupTwo = selectGroups(groups)
        switch(groupOne, groupTwo, groups)
        #score = pointsSaldo(groupOne, groupTwo.getRoomSlot()) + pointsSaldo(groupTwo, groupOne.getRoomSlot())
        score = getPoints(timeTable)
        print oldscore," ", score, " ", "temp: ", temperature
        print "=", (oldscore - score) / temperature
        rawchance = (math.exp((score - oldscore) / temperature))
        if score - oldscore < 0:
            chance = ((0.02 / ((oldscore - score))) + 0.98 * rawchance)
        else:
            chance = rawchance
        print "chance: ", chance
        if chance < 1:
            chances.append(chance)
        if(chance > random.random()):
            highscore = score
            #scores.append(highscore)
        else: 
            switch(groupTwo, groupOne, groups)
            score = oldscore
            print "switched back"
        i += 1
        scores.append(highscore)
        temperature *= coolingRate
    plt.plot(chances)
    plt.ylabel('chance')
    plt.xlabel('iterations')
    plt.show()
    plt.plot(scores)
    plt.ylabel('points')
    plt.xlabel('iterations')
    plt.show()
    while(True):
        s = raw_input("would you like to run a hillclimber for 300 times? (y/n)")
        if s == "n":
            break
        if s == "y":
            print "initialize hillclimber..."
            scores.append(hillclimbAlgorithm(timeTable, getPoints(timeTable), 300))
    return scores

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""  Genetic algorithm """""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def selectParents(children, acceptOutsider):
    # The surving parents-to-be are randomly selected from all childs
    # It's possible to accept the introduction of an outsider every round
    chance = 0.3
    
    print "Picking parents..."
    scoreList = [getPoints(c) for c in children]
    minScore = min(scoreList)
    mean = np.mean(scoreList)
    parents = []
    for c in children:
        factor = (getPoints(c) - minScore)/(mean - minScore)
        if random.random() < factor*chance:
            parents.append(c)
    
    if acceptOutsider == True:
        child = None
        while not allCoursesScheduled(child):
            child = createTimeTableInstance()
            randomAlgorithm(child)
        parents.append(child)
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
                if not s.hasGroup():
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
                if (roomIsValid(room2, g1.getStudents(),
                                g1.getActivity()) and
                    roomIsValid(room1, g2.getStudents(),
                                g2.getActivity())):
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
    return
    
def mutate(parents):
    # Parents are mutated before coupling
    fsFactor = 0.01
    csFactor = 0.01
    sFactor = 0.05
    
    print "Mutating offspring..."
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
        while p2 == p1:
            p2 = random.choice(parents)
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
    # Making children with two parents. One child is returned

    child = createTimeTableInstance([p1, p2])
    if len(p1.getCourses()) != len(p2.getCourses()):
        raise StandardError("TimeTables are of different species")
    badGroups = []
    c1 = p1.getCourses()
    c2 = p2.getCourses()

    courseNr = range(len(c1))
    random.shuffle(courseNr)
    for i in courseNr:
        parentC = random.choice([c1[i], c2[i]])
        for c in child.getCourses():
            if c.getName() == parentC.getName():
                course = c
                break
        groups = sum([a.getGroups() for a in parentC.getActivities()],[])
        for parentG in groups:
            activityName = parentG.getActivity().getType()
            for a in course.getActivities():
                if a.getType() == activityName:
                    activity = a
                    break
            studentNames = [s.getName() for s in parentG.getStudents()]
            students = [s for s in child.getStudents()
                        if s.getName() in studentNames]
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
        except:
            print "Miscarriage..."
            return None
    return child

def makeLove(parents, n, incest):
    print "\nMaking new children..."
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

def geneticAlgorithm(iterations = 1, acceptOutsider = True, allowIncest = True):
    nrChilds = 20

    print "================================="
    print "Initiating genetic algorithm"
    print "================================="
    children = []
    for i in range(nrChilds):
        table = None
        while not allCoursesScheduled(table):
            table = createTimeTableInstance()
            randomAlgorithm(table)
        children.append(table)

    evolution = []
    overbookings = []
    spread = []
    personal = []
    bestChildScore = 0
    i = 0
    while i < iterations:
        i += 1
        print "\n========================"
        print "Starting iteration ",i
        print "========================"
        print "Amount of children ",len(children)
        parents = selectParents(children, acceptOutsider)
        print "Parent points this generation: "
        for p in parents:
            print getPoints(p),
        offspring = makeLove(parents, nrChilds - len(parents), allowIncest)
        mutate(offspring)
        children = parents + offspring
        
        maxChild = max(children, key = lambda x: getPoints(x))
        if getPoints(maxChild) > bestChildScore:
            bestChild = maxChild
            bestChildScore = getPoints(maxChild)
        evolution.append(int(np.mean([getPoints(c) for c in children])))
        overbookings.append(int(np.mean([overbooked(c) for c in children])))
        spread.append(int(np.mean([
            coursesMaximallySpread(c) - activityConflict(c) for c in children
            ])))
        personal.append(int(np.mean([
            personalScheduleConflict(c) for c in children
            ])))
        if i == iterations:
            q = ""
            print "\n======================"
            print "Evolution review!"
            print "======================"
            print "Total score: \n",evolution
            print "Overbookings: \n",overbookings
            print "Personal conflicts: \n",personal
            print "Spreadding points: \n",spread
            w = ("You want to do another "
                 +str(iterations)
                 +" iterations? (Y/N)")
            q = raw_input(w)
            if q == "Y":
                iterations *= 2
                continue
            try: i += int(q)
            except: break
        
    return bestChild
    

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""  Initial functions """""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    

def createTimeTableInstance(parents = None):
    print "Creating new timetable structure..."
    timeTable = TimeTable(parents)
    courses = []
    for c in COURSEDATA:
        course = Course(c['courseName'], c['lectures'], c['seminar'],
                        c['maxStudSeminar'], c['practica'],
                        c['maxStudPractica'])
        timeTable.addCourse(course)
        courses.append(course)
    for s in STUDENTDATA[1:]:
        student = Student(s["firstName"],s["lastName"],s["nr"],
                          s["courses"],courses)
        timeTable.addStudent(student)
        
    return timeTable
 
if __name__ == '__main__':
    print "Welcome to Ultimate Scheduler 3000!"
    mainTimeTable = createTimeTableInstance()
    print "Creating random schedule, stored as 'mainTimeTable'."
    randomAlgorithm(mainTimeTable)
    print "This timetable has",getPoints(mainTimeTable)," points."


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def t():
    henk = createTimeTableInstance()
    randomAlgorithm(henk)
    scores = hillclimbAlgorithm(henk, getPoints(henk), ITERATIONS * 3)
    plt.plot(scores)
    plt.ylabel('points')
    plt.xlabel('iterations')
    plt.show()
    return henk, scores

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def r():
    scores = []
    timetables = []
    for i in range(100):
        henk = createTimeTableInstance()
        randomAlgorithm(henk)
        scores.append((getPoints(henk)))
        timetables.append(henk)
        if i % 10 == 0:
            print "iterations: ", i
    return timetables[scores.index(max(scores))]
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def h():
    h = createTimeTableInstance()
    randomAlgorithm(h)
    print "eerste score: ",getPoints(h)
    g = h.getGroups()
    g1,g2 = selectGroups(g)
    switch(g1,g2,g)
    print "tweede score: ",getPoints(h)
    print "naam groep 1: ",g1.getActivity().getCourse().getName()
    print "naam groep 2: ",g2.getActivity().getCourse().getName()
    return h, g1,g2,g
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def s():
    h = createTimeTableInstance()
    randomAlgorithm(h)
    scores = simulatedAnnealing(h,getPoints(h))
    return h, scores

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def p():
    timetable = r()
    scores = simulatedAnnealing(timetable, getPoints(timetable))
    return timetable, scores

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""" Exporting function """""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def tableToList(timeTable):
    data = []
    for t in timeTable.getTimeSlots():
        for r in t.getRoomSlots():
            if r.hasGroup():
                group = r.getGroup()
                students = [
                    (s.getName(),s.getNr()) for s in group.getStudents()
                    ]
                data.append({
                    "startTime": 2*t.getTime(),
                    #int of number of houres after 9 
                    "day": t.getDay(),
                    #"students": students, #Erg lange dictionary met dit erbij..
                    "course": group.getActivity().getCourse().getName(),
                    "workType": group.getActivity().getType(),
                    "validity": str(group.isValid()),
                    "roomName": r.getRoom(),
                    "roomSize": r.getSize()
                    })
    return data

def studentToList(student):
    data = []
    for g in student.getGroups():
        r = g.getRoomSlot()
        t = r.getTimeSlot()
        data.append({
            "startTime": 2*t.getTime(), #int of number of houres after 9 
            "day": t.getDay(),
            "students": [student.getName()],
            "course": g.getActivity().getCourse().getName(),
            "workType": g.getActivity().getType(),
            "validity": str(g.isValid()),
            "roomName": r.getRoom(),
            "roomSize": r.getSize()
            })
    return data
      
def courseToList(course):
    data = []
    for a in course.getActivities():
        for g in a.getGroups():
            r = g.getRoomSlot()
            t = r.getTimeSlot()
            students = [(s.getName(),s.getNr()) for s in g.getStudents()]
            data.append({
                "startTime": 2*t.getTime(), #int of number of houres after 9 
                "day": t.getDay(),
                "students": students,
                "course": course.getName(),
                "workType": a.getType(),
                "validity": str(g.isValid()),
                "roomName": r.getRoom(),
                "roomSize": r.getSize()
                })
    return data


def exportData(timeTable):
    print "Data is stored in .../visualisation/Data/."
    print "Saving main timetable..."
    data = tableToList(timeTable)
##    with open("Visualisatie/Data/main.json", 'wb') as f:
##        json.dump(data, f, encoding='latin1')
    students = timeTable.getStudents()
    print "Saving timetables of "+str(len(students))+" students..."
    for i, s in enumerate(students):
        data = studentToList(s)
        filename = "student"+str(i)+".json"
        with open("Visualisatie/Data/"+filename, 'wb') as f:
            json.dump(data, f, encoding='latin1')
    courses = timeTable.getCourses()
    print "Saving timetables of "+str(len(courses))+" courses..."
    for i, c in enumerate(courses):
        data = courseToList(c)
        filename = "course"+str(i)+".json"
        with open("Visualisatie/Data/"+filename, 'wb') as f:
            json.dump(data, f, encoding='latin1')
                
    return

def saveTimeTable(timeTable):
    filename = raw_input("Name your timetable json: ")+".json"
    print "Data is stored in .../visualisation/Data/"+filename+"..."
    data = tableToList(timeTable)
    with open("Visualisatie/Data/"+filename, 'wb') as f:
        json.dump(data, f, indent=True, encoding='latin1')
    return
    
    
