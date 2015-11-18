import json
import random
import math
import itertools

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""" Global Variables """""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


STUDENTS = 'students.json'
COURSES = 'coursesInf.json'
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
            else: raise StandardError("Course " + c + " for student " + self.getName() + " does not exist")
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
    def __init__(self):
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
    def __init__(self, courseName, lectures, seminar, maxseminar, practica, maxPractica):
        self.students = []
        self.lectures = [Activity("lecture",self) for i in range(lectures)]
        self.seminar = [Activity("seminar", self, maxseminar) for i in range(seminar)]
        self.practica = [Activity("practicum", self, maxPractica) for i in range(practica)]
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
    def __init__(self, workType, course, maxStudents=float('inf')):
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
        for s in students:
            s.addGroup(self)
        activity.addGroup(self)
    def getActivity(self):
        return self.activity
    def getStudents(self):
        return self.students
    def isValid(self):
        return len(self.students) <= self.maxStudents
    def getRoomSlot(self):
        return self.roomSlot



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


def checkCount(aPoss, numberOfActivities):
    for c in aPoss:
        if numberOfActivities == 2:
            if "mo" and "thu" or "tu" and "fri" or "mo" and "fri" in c:
                return True
        elif numberOfActivities == 3:
            if "mo" and "we" and "fri" in c:
                return True
        elif numberOfActivities == 4:
            if "mo" and "tu" and "th" and "fr" in c:
                return True
        return False

def coursesMaximallySpread(timeTable):
    courses = timeTable.getCourses()
    bonus = 0
    for c in courses:
        cDays = []
        for a in c.getActivities():
            aDays = []
            for g in a.getGroups():
                d = g.getRoomSlot().getTimeSlot().day
                aDays.append(d)
            cDays.append(aDays)
        # Cartesian product
        aPoss = [list(v) for v in itertools.product(*cDays)]
        numberOfActivities = len(cDays)
        if checkCount(aPoss, numberOfActivities):
            bonus += 20
    return bonus
        
    
def overbooked(timeTable):
    malus = 0
    saldo = 0;
    ts = timeTable.getTimeSlots()
    rs = []
    for t in ts:
            rs += t.getRoomSlots()
    for r in rs:
        if r.getStudents() != None:
            saldo = len(r.getStudents()) - r.getSize()
        if saldo > 0:
            malus += saldo
    return malus


def personalScheduleConflict(timeTable):
    students = timeTable.getStudents()
    malus = 0
    # Loop over lijst met students heen
    for s in students:
        cList = []
        for c in s.getGroups():
            if c.getRoomSlot().getTimeSlot() in cList:
                malus += 1
            cList.append(c.getRoomSlot().getTimeSlot())
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

def activityConflict(timeTable):
    courses = timeTable.getCourses()
    points = 0
    for c in courses:
        nrAct = 0
        days = []
        for a in c.getActivities():
            nrAct += 1
            for g in a.getGroups():
                day = g.getRoomSlot().getTimeSlot().getDay()
                days.append(day)
        if nrAct > len(set(days)): points += 10
    return points

def getPoints(timeTable):
    # Calculates the points of the timeTable
    # Looks for bonus points(20 for each maximally spreaded course)
    # Looks for malus points(1 for each student-specific conflict,
    # 1 for each overbooked student, 10 for each double scedueled course on one day)
    if allCoursesScheduled(timeTable):
        points = 1000
        points += coursesMaximallySpread(timeTable)
        points -= activityConflict(timeTable)
        points -= overbooked(timeTable)
        points -= personalScheduleConflict(timeTable)
    else: points = None
    return points


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""  Random booking algorithm """""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def bookRandomRoom(activity, randomRoomSlots, students, timeTable):
    # Tries to book an activity in a room. If succeeded: returns the booked group
    for r in randomRoomSlots:
        if ((not r.hasGroup()) and
            r.getSize()*OVERBOOK >= len(students)
            ):
                group = Group(activity, students, activity.getMaxStudents(), r)
                r.appointGroup(group)
                timeTable.addGroup(group)
                return
    else: raise StandardError("No room can be found for " +
                              activity.getCourse().getName())

    
def split(activity):
    # Takes an activity with more students than alowed per group and returns lists of valid student groups
    numberOfGroups = math.ceil(len(activity.getCourse().getStudents())
                               /float(activity.getMaxStudents()))
    activityStudents = activity.getCourse().getStudents()
    numberStud = len(activityStudents)/numberOfGroups
    studentGroups = []
    for i in range(int(numberOfGroups)):
        newStudentGroup = activityStudents[int(i*numberStud):int((i+1)*numberStud)]
        studentGroups.append(newStudentGroup)
    return studentGroups


def bookActivity(activity, randomRoomSlots, timeTable):
    # Splits activities in valid groups and tries to book them
    if activity.getMaxStudents() < len(activity.getCourse().getStudents()):
        studentGroups = split(activity)
    else: studentGroups = [activity.getCourse().getStudents()]

    for g in studentGroups:
        try: bookRandomRoom(activity, randomRoomSlots, g, timeTable)
        except: pass
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
"""""""""""""""  Deterministic booking algorithm"""""""""""""""""""""""""""""""""""""""
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
"""""""""""""""  Hillclimbing algorithm """""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# SUCCES THOMAS :)

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""  Genetic algorithm """""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def selectParents(children):
    bestP = 0.2
    randomP = 0.05
    
    print "Picking parents..."
    n = len(children)
    children.sort(key=lambda x: getPoints(x))
    
    bestChildren = children[int(-bestP*n):]
    restChildren = children[:int(-bestP*n)]
    randomChildren = [
        random.choice(restChildren) for i in range(int(randomP*n))
        ]
    return bestChildren + randomChildren

def mutate(parents):
    return parents

def makeLove(parents):
    print "Making new children..."
    return parents

def geneticAlgorithm(iterations = 1):
    nrChilds = 100

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

    for i in range(iterations):
        print "Starting iteration ",i+1
        parents = selectParents(children)
        mutate(parents)
        children = makeLove(parents)
    
    return max(children, key = lambda x: getPoints(x))
    

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""  In
itial functions """""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    

def getData(filename):
    """
    Reads the json-file with the schedule data
    Returns a list of dictionaries
    """
    json_data=open(filename).read()
    return json.loads(json_data)

def createTimeTableInstance():
    print "Creating empty timetable structure..."
    studentData = getData(STUDENTS)
    courseData = getData(COURSES)
    timeTable = TimeTable()
    students = []
    courses = []
    for c in courseData:
        course = Course(c['courseName'], c['lectures'], c['seminar'],
                        c['maxStudSeminar'], c['practica'],
                        c['maxStudPractica'])
        courses.append(course)
        timeTable.addCourse(course)
    for s in studentData[1:]:
        student = Student(s["firstName"],s["lastName"],s["nr"],
                          s["courses"],courses)
        students.append(student)
        timeTable.addStudent(student)
        
    return timeTable
 
if __name__ == '__main__':
    print "Welcome to Ultimate Scheduler 3000!"
    mainTimeTable = createTimeTableInstance()
    print "Creating random schedule, stored as 'mainTimeTable'."
    randomAlgorithm(mainTimeTable)
    getPoints(mainTimeTable)

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""" Exporting function """""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def tableToList(timeTable):
    data = []
    for t in timeTable.getTimeSlots():
        for r in t.getRoomSlots():
            if r.hasGroup():
                group = r.getGroup()
                students = [(s.getName(),s.getNr()) for s in group.getStudents()]
                data.append({
                    "startTime": 2*t.getTime(), #int of number of houres after 9 
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
    with open("Visualisatie/Data/main.json", 'wb') as f:
        json.dump(data, f, encoding='latin1')
    print "Saving timetables of "+str(len(students))+" students..."
    students = timeTable.getStudents()
    for i, s in enumerate(students):
        data = studentToList(s)
        filename = "student"+str(i)+".json"
        with open("Visualisatie/Data/"+filename, 'wb') as f:
            json.dump(data, f, encoding='latin1')
    print "Saving timetables of "+str(len(courses))+" courses..."
    courses = timeTable.getCourses()
    for i, c in enumerate(courses):
        data = courseToList(c)
        filename = "course"+str(i)+".json"
        with open("Visualisatie/Data/"+filename, 'wb') as f:
            json.dump(data, f, encoding='latin1')
                
    return

def saveTimeTable(timeTable):
    filename = raw_input("Name your timetable json: ")+".json"
    print "Data is stored in .../visualisation/Data/"+filename+"..."
    data = tableToList()
    with open("Visualisatie/Data/"+filename, 'wb') as f:
        json.dump(data, f, indent=True, encoding='latin1')
    return
    
    
