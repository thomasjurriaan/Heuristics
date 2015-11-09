import json
import random

STUDENTS = 'students.json'
COURSES = 'coursesInf.json'
ROOMDICT = {
    #Room name, room for nr students"
    "A1.04":41,
    "A1.06":22,
    "A1.08":20,
    "A1.10":56,
    "B0.201":48,
    "C0.110":117,
    "C1.112":60
    }
ROOMS = []
for r in ROOMDICT:
    ROOMS.append({
        "name":r,
        "size":ROOMDICT[r],
        "course":False
        })

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
            else: raise StandardError("Course "+c+" for student "+self.getName()+" does not exist")
        self.activities = []
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
    def addActivity(self, activity):
        self.activities.append(activity)


class TimeTable(object):
    def __init__(self):
        #include 4 empty time slots for every day of the week.
        l = []
        self.days = ['mo','tu','we','th','fr']
        for d in self.days:
            for t in range(4):
                l.append(TimeSlot(d,t))
        self.timeSlots = l
    def resetTimeSlot(self,i):
        #When removing a booking from the schedual
        self.timeSlots[i] = TimeSlot(i)
    def getTimeSlots(self, day):
        for n, d in enumerate(self.days):
            if day==d:
                return self.timeSlots[(4*n):(4*n+4)]
    def getAllTimeSlots(self):
        return self.timeSlots


class TimeSlot(object):
    # Each timeslot-instance contains 7 available rooms
    def __init__(self, day, time):
        # 'i' is a number in range 20.
        self.time = time
        self.day = day
        self.roomSlots = ROOMS
    def isFullyBooked(self):
        #Returns True if all rooms are booked. False otherwise
        return all([r['course'] for r in self.roomSlots])
    def book(self, group, room):
        #Books a course in a specific room
        for r in self.roomSlots:
            if r['name'] == room:
                r['course'] = course
    def resetRoomSlot(self,room):
        #Resets a specific room in the timeslot
        for r in self.roomSlots:
            if r['name'] == room:
                r['course'] = False
    def getTime(self):
        return str(2*self.time+9)+"h till "+str(2*self.time+11)+"h."
    def getRoomSlots(self):
        return self.roomSlots

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
    def __init__(self, workType, course, maxStudents=None):
        # Worktype is 'lecture', 'seminar' or 'practicum'
        self.type = workType
        self.course = course
        self.maxStudents = maxStudents
    def getCourse(self):
        return self.course
    def getMaxStudents(self):
        return self.maxStudents
    def getType(self):
        return self.type
   # def split(self):


class Group(object):
    def __init__(self, activity, students, maxstudents, roomslot, timeslot):

    

def getData(filename):
    """
    Leest de json-file met de rooster data
    Returnt een lijst van dictionaries
    """
    json_data=open(filename).read()
    return json.loads(json_data)
 
if __name__ == '__main__':
    mainTimeTable = TimeTable()
    studentData = getData(STUDENTS)
    courseData = getData(COURSES)
    students = []
    courses = []
    groups = []
    for c in courseData:
        courses.append(Course(c['courseName'], c['lectures'], c['seminar'],
                              c['maxStudSeminar'], c['practica'], c['maxStudPractica']))


    for s in studentData[1:]:
        #Function that makes student-instances
        students.append(Student(s["firstName"],s["lastName"],s["nr"],s["courses"],courses))


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""" Poging tot recursieve functie om activiteiten in dagen in te delen """
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def getPoints(timeTable):
    # Calculates the points of the timeTable
    # Looks for bonus points(20 for each maximally spreaded course)
    # Looks for malus points(1 for each student-specific conflict,
    # 1 for each overbooked student, 10 for each double scedueled course on one day)
    return 1000
    

def bookRoom(timeTable,activity,day):
    # Tries to book a room. Is no room suits the needs of the specific
    # course and activity, an Error is raised
    l = timeTable.getTimeSlots(day)
    rooms = l.getRoomSlots()
    course = activity.getCourse()
    for t in l:
        for r in rooms:
            if {
                (not r['course']) &
                (r['size'] <= activity.getMaxStudents()) &
                (r['size'] >= len(course.getStudents()))
                 } :
                l.book(course,r) #book neemt nu group en timeslot als arguments
                break
        break
    else: raise StandardError("No room can be found for "
                              + activity.getCourse().getName()
                              +" on day " + day)

def bookRandomRoom(activity, timeslot):

    # Dit zijn de arguments van groups:(self, activity, students, maxstudents, roomslot, timeslot)
    rooms = timeslot.getRoomSlots()
    for r in rooms:
        if 
        {
            (not r['course']) &
            (r['size'] <= activity.getMaxStudents()) &
            (r['size'] >= len(course.getStudents()))
        }:
            groups.append(Group()
            l.book(group,r)
            break
    break


def generateAllChildren(parent, activity):
    # Returns a max of 5 timeTable indices
    days = ['mo','tu','we','th','fr']
    timeTables = []
    for d in days:
        try: timeTables.append(bookRoom(parent,activity,d))
        except: continue
    return timeTables

MAXPOINTS=0
def roosterVolgendeActiviteit(activities,parentTimeTable):
    # The recursive function
    timeTables = generateAllChildren(parentTimeTable,activities[0])
    for t in timeTables:
        if len(activities)==0:
            points = getPoints(t)
            if points > maxPoints:
                maxPoints = points
                bestTimeTable = t
        else: roosterVolgendeActiviteit(activities[1:],t)
    return bestTimeTable

def randomAlgorithm():
    # Make list of random activities
    random_activities = []
    for c in courses:
        random_activities.append(c.getActivities())

    random.shuffle(random_activities)

    # Make list of random timeslots
    random_timeslots = mainTimeTable.getAllTimeSlots()

    random.shuffle(random_timeslots)

    # Use bookRandomRoom to go from activities to groups and book those groups
    int i = 0
    while(i < len(random_activities)):
    {
        bookRandomRoom(random_activities[i], random_timeslots[i])
        i++
    }

    return timeTable


