import json

STUDENTS = 'students.json'
COURSES = 'courses.json'
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

class Student(object):
    def __init__(self, firstName, lastName, studntNr, courses):
        self.firstName = firstName
        self.lastName = lastName
        self.nr = studntNr
        # self.courses is een lijst van course class-instanties
        self.courses = [Course(i,1,1) for i in courses]
        self.timeTable = TimeTable()
        
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

class TimeTable(object):
    def __init__(self):
        #include 4 empty time slots for every day of the week.
        l = []
        for d in ['mo','tu','we','th','fr']:
            for t in range(4):
                l.append(TimeSlot(d,t))
        self.timeSlots = l
    def resetTimeSlot(self,i):
        #When removing a booking from the schedual
        self.timeSlots[i] = TimeSlot(i)

class TimeSlot(object):
    # Each timeslot-instance contains 7 available rooms
    def __init__(self, i):
        rooms = ROOMS
        # 'i' is a number in range 20.
        self.time = i #te maken functie T(i)
        self.day = i #te maken functie D(i)
        self.roomSlots = []
        for r in rooms:
            self.roomSlots.append({
                "name":r,
                "size":rooms[r],
                "course":False
                })

    def isFullyBooked(self, room):
        #Returns True if all rooms are booked. False otherwise
        return all([r['course'] for r in self.roomSlots])
    def book(self, course, room):
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
        

class Course(object):
    def __init__(self, courseName,lectures,psp):
        self.timeTable = TimeTable()
        self.students = []
        self.lectures = [Activity("lecture",self) for i in range(lectures)]
        self.psp = [Activity("psp",self) for i in range(lectures)]
    def addStudent(self,student):
        self.students.append(student)
    def getActivities(self):
        return [i for i in self.lectures, self.psp]

class Activity(object):
    def __init__(self, workType, course):
        # Worktype is 'lecture' or 'psp'
        self.type = workType
        self.course = course
    


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
    for course in courseData:
        # Function that makes a list 'courses' with all the names,
        # number of lectures and number of PS-classes+praktica of every course
        #courses.append(Course(course))
        pass
    for s in studentData:
        #Function that makes student-instances
        students.append(Student(s["firstName"],s["lastName"],s["nr"],s["courses"]))
