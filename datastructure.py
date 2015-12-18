"""***********************************************************************
* datastructure.py
*
* Heuristieken
* Daan van den Berg
*
* Contains the global structure: all classes, import of data and create
* timetable instance which will be used as init in roostering_heuristics.py
*
***********************************************************************"""

import json


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

# Rooms can be overbooked by this percentage
OVERBOOK = 1.2
ITERATIONS = 1000


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""" Data Structure """""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


class Student(object):
    def __init__(self, firstName, lastName, studntNr, courses, courseList):
        self.firstName = firstName
        self.lastName = lastName
        self.nr = studntNr
        # self.courses is a list of course class-instances
        self.courses = []
        for c in courses:
            courseObject = courseList[c]
            self.courses.append(courseObject)
            courseObject.addStudent(self)
        self.groups = []
    def getName(self):
        return self.firstName+' '+self.lastName
    def getNr(self):
        return self.nr
    def getCourses(self):
        return self.courses
    def doesCourse(self, course):
        #check if course is a class-instance
        return course in self.courses
    def addGroup(self, group):
        self.groups.append(group)
    def switchGroups(self, group1, group2):
        for n, g in enumerate(self.groups):
            if g == group1:
                self.groups[n] = group2
                break
        else: raise StandardError("No such group to switch for student")
    def removeGroup(self, group):
        self.groups = [g for g in self.groups if g != group]
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
        self.points = None
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
    def setPoints(self, points):
        self.points = points
    def getPoints(self):
        return self.points
    def addPointers(self, courses, students):
        self.studentPointers = students
        self.coursePointers = courses
    def getCoursePointers(self):
        return self.coursePointers
    def getStudentPointers(self):
        return self.studentPointers


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
            return []
        else: return self.group.getStudents()


class Course(object):
    def __init__(
        self, courseName, lectures, seminar, maxseminar, practica, maxPractica
        ):
        self.students = []
        self.actPointers = {}
        self.lectures = []
        self.seminar = []
        self.practica = []
        for i in range(lectures):
            name = "lecture"+str(i)
            act = Activity(name, self)
            self.lectures.append(act)
            self.actPointers[name] = act
        for i in range(seminar):
            name = "seminar"+str(i)
            act = Activity(name, self, maxseminar)
            self.seminar.append(act)
            self.actPointers[name] = act
        for i in range(practica):
            name = "practicum"+str(i)
            act = Activity(name, self, maxPractica)
            self.practica.append(act)
            self.actPointers[name] = act
        self.courseName = courseName
    def addStudent(self,student):
        self.students.append(student)
    def getActivities(self):
        return self.lectures+self.seminar+self.practica
    def getStudents(self):
        return self.students
    def getName(self):
        return self.courseName
    def getPointers(self):
        return self.actPointers
    def getNumberOfStudents(self):
        return len(self.students)


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
"""""""""""""""""""""  Initiate functions """""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    


def createTimeTableInstance(parents = None):
    """
    Converts data to class objects and saves it in the timetable instance
    """
    timeTable = TimeTable(parents)
    courses = {}
    students = {}
    for c in COURSEDATA:
        cName = c['courseName']
        course = Course(cName, c['lectures'], c['seminar'],
                        c['maxStudSeminar'], c['practica'],
                        c['maxStudPractica'])
        timeTable.addCourse(course)
        courses[cName] = course
    for s in STUDENTDATA[1:]:
        sName = s["firstName"]+' '+s["lastName"]
        student = Student(s["firstName"],s["lastName"],s["nr"],
                          s["courses"],courses)
        students[sName] = student
        timeTable.addStudent(student)
    timeTable.addPointers(courses, students)
        
    return timeTable
