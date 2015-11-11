import json
import random


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
            else: raise StandardError("Course "+c+" for student "+self.getName()+" does not exist")
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
    def getTimeSlots(self):
        return self.timeSlots
    def getAllTimeSlots(self):
        return self.timeSlots

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
    def __init__(self, workType, course, maxStudents=None):
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
"""""""""""""""  Scheduling algorithms """""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

# This function uses the Boolean allCoursesScheduled. 
# It is instantiated as 'True' and set to 'False' when 
# an activity cannot be scheduled in randomAlgorithm(). 

def coursesMaximallySpread():
    pass

def getPoints(timeTable, allCoursesScheduled):
    # Calculates the points of the timeTable
    # Looks for bonus points(20 for each maximally spreaded course)
    # Looks for malus points(1 for each student-specific conflict,
    # 1 for each overbooked student, 10 for each double scedueled course on one day)
    if AllCoursesScheduled:
        points = 1000
        points += coursesMaximallySpread()
        points -= activityConflict()
        points -= overbooked()
        points -= personalScheduleConflict()
    else: points = None

    # or: points = allCoursesSchudeled() + CoursesMaximallySpreaded() - (activityConflict() + overbooked() + personalScheduleConflict())
    return points

def bookRandomRoom(activity, randomRoomSlots):
    # Dit zijn de arguments van groups:(self, activity, students, maxStudents, roomSlot, timeSlot)
    for r in randomRoomSlots:
        if not r.hasGroup():
            if r.getSize()*OVERBOOK >= len(activity.getCourse().getStudents()):
                group = Group(activity, activity.getCourse().getStudents(),
                              activity.getMaxStudents(), r)
                groups.append(group)
                r.appointGroup(group)
                return groups
    else: raise StandardError("No room can be found for " +
                              activity.getCourse().getName())


def randomAlgorithm(courses, timeTable):
    # Make list of random activities
    randomActivities = []
    for c in courses:
        randomActivities += c.getActivities()
    random.shuffle(randomActivities)

    # Make list of random timeslots
    randomRoomSlots = []
    for t in timeTable.getAllTimeSlots():
        randomRoomSlots += t.getRoomSlots()
    random.shuffle(randomRoomSlots)
    
    # Use bookRandomRoom to go from activities to groups and book those groups
    allCoursesScheduled = True
    for activity in randomActivities:
        try: groups = bookRandomRoom(activity, randomRoomSlots)
        except: allCoursesScheduled = False

    # The timeTable is updated and doesn't have to be returned explicitly
    # allCoursesScheduled only returns False when bookRandomRoom returned an error
    return allCoursesScheduled 


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""  Initial functions """""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    

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

    allCoursesScheduled = randomAlgorithm(courses, mainTimeTable)
    #getPoints(mainTimeTable, allCoursesScheduled)

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""""""""  Initial functions """""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def exportTimeTable(timeTable):
    pass
    
    
##def generateAllChildren(parent, activity):
##    # Returns a max of 5 timeTable indices
##    days = ['mo','tu','we','th','fr']
##    timeTables = []
##    for d in days:
##        try: timeTables.append(bookRoom(parent,activity,d))
##        except: continue
##    return timeTables
##
##MAXPOINTS=0
##def roosterVolgendeActiviteit(activities,parentTimeTable):
##    # The recursive function
##    timeTables = generateAllChildren(parentTimeTable,activities[0])
##    for t in timeTables:
##        if len(activities)==0:
##            points = getPoints(t)
##            if points > maxPoints:
##                maxPoints = points
##                bestTimeTable = t
##        else: roosterVolgendeActiviteit(activities[1:],t)
##    return bestTimeTable
##
##def bookRoom(timeTable,activity,day):
##    # Tries to book a room. Is no room suits the needs of the specific
##    # course and activity, an Error is raised
##    l = timeTable.getTimeSlots(day)
##    rooms = l.getRoomSlots()
##    course = activity.getCourse()
##    for t in l:
##        for r in rooms:
##            if {
##                (not r['course']) &
##                (r['size'] <= activity.getMaxStudents()) &
##                (r['size'] >= len(course.getStudents()))
##                 } :
##                l.book(course,r) #book neemt nu group en timeslot als arguments
##                break
##        break
##    else: raise StandardError("No room can be found for "
##                              + activity.getCourse().getName()
##                              +" on day " + day)
##
##
