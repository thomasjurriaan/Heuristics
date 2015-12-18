from points import *
from datastructure import *
from exportfunctions import *
from randomalgorithm import *
import operator

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""  Deterministic booking algorithm"""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""
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
"""

def deterministic(timeTable):
    # dictionary voor roomslots
    sortedRoomSlotsDict = {
        'mo' :[],
        'tu' :[],
        'we' :[],
        'th' :[],
        'fr' :[],
        }
    sortedRoomSlotsList = []
    
    #fill courses from max students to min students
    courses = timeTable.getCourses()
    lectureList = []
    seminarList = []
    practicumList = []
    sortCourses = []

    # Sort courses list
    for c in courses:
        sortCourses.append(c)
    sortCourses.sort(key=operator.attrgetter('getNumberOfStudents'))

    # sortCourses --> activitiesMaxMin Dictionary
    for c in sortCourses:
        act = c.getActivities()
        for a in act:
            aType = a.getType()
            if "lecture" in aType:
                lectureList.append(a)
            if "seminar" in aType:
                seminarList.append(a)
            if "practicum" in aType:
                practicumList.append(a)
    activitiesMaxMin = {'lecture':lectureList, 'seminar':seminarList, 'practicum':practicumList}

    # Activities MaxMin List
    activityList = []
    for c in sortCourses:
        act = c.getActivities()
        for a in act:
            activityList.append(a)
            
    # maak dictionary met roomslots per dag. 'mo': [roomslotsValues]      
    for t in timeTable.timeSlots:
        roomSlots = t.getRoomSlots()
        for s in roomSlots:
            sortedRoomSlotsDict[t.getDay()].append(s)
                   
    # sorteert roomslots op size
    for key in sortedRoomSlotsDict:
        sortedRoomSlotsDict[key].sort(key=operator.attrgetter('size'))
        
    # gesorteerde lijst met roomslots
    for key in sortedRoomSlotsDict:
        for roomslots in sortedRoomSlotsDict[key]:
            sortedRoomSlotsList.append(roomslots)
    sortedRoomSlotsList.sort(key=operator.attrgetter('size'))

    # Courselist gesorteerd op aantal activities
    sortCourses.sort(key = lambda x: len(x.getActivities()), reverse=True)

    # dict
    pointDict = {
        5 : ['mo', 'tu', 'we', 'th', 'fr'],
        4 : ['mo', 'tu', 'th', 'fr'],
        3 : ['mo', 'we', 'fr'],
        2 : ['th', 'mo'],
        }

    # random room slots
    randomRoomSlots = []
    for t in timeTable.getTimeSlots():
        randomRoomSlots += t.getRoomSlots()
    random.shuffle(randomRoomSlots)

    """
    # booking
    for course in sortCourses:
        activities = course.getActivities()
        for amount in pointDict:
            if amount == len(course.getActivities()):
                count = 0
                for activity in activities:
                    day = pointDict[amount][count]
                    count += 1
                    print activity
                    try: bookActivity(activity, randomRoomSlots, timeTable)
                    except: break
    print getPoints(timeTable)

    return
    """


    # Stack
    #
    #random.shuffle(activityList)
    bestScore = 0
    count = 0
    stack = [[["mo", activityList[0]]]]
    bookedActivities = []
    while stack != []:
        for child in stack:
            try: parent = stack[-1].pop()
            except:
                
                #lijst van children is leeg
                stack.pop()
                lBookedActivity = bookedActivities.pop()
                deleteActivity(lBookedActivity[1], timeTable)
                continue
            
            # Book Parent
            if depthBookActivity(parent[1], sortedRoomSlotsDict[parent[0]], sortedRoomSlotsList, timeTable) != False:
                bookedActivities.append(parent)
                #print "***** BOOKED *****"
                # Maak children van parent
                try:
                    children = generateAllChildren(parent[1], activityList)
                    stack.append(children)
                    #print "made children"
                except:
                    #print "made no children"
                    # TODO: Calculeer maxpoints en vergelijk timetable met eerder resultaat
                    currentScore = getPointsDeterministic(timeTable)
                    count += 1
                    #print currentScore
                    lBookedActivity = bookedActivities.pop()
                    if currentScore > bestScore: bestScore = currentScore
                    if count > 1000:
                        count = 0
                        print bestScore
                    deleteActivity(lBookedActivity[1], timeTable)

    # Poging 3
"""
    stack = sortCourses
    while stack != []:
        c = stack.pop()
        activities = p.getActivities()
        for activity in activities:
            if len(activities) = 2:
                depthBookActivity(activity, sortedRoomSlots)
            if len(activities) = 3:
                #
            if len(activities) = 4:
                #
            if len(activities) = 5:
                #
        
"""

def deleteActivity(activity, timeTable):
    for group in activity.getGroups():
        timeTable.groups.remove(group)
        group.roomSlot.reset()
        for student in group.students:
            student.removeGroup(group)
    activity.groups = []
        
def generateAllChildren(parent, activityList):
    days = ['mo', 'tu', 'we', 'th', 'fr']
    children = []
    indexSperm = activityList.index(parent) + 1
    for day in days:
        kid = [day, activityList[indexSperm]]
        children.append(kid)
    return children

def depthBookActivity(activity, sortedRoomSlots, roomSlots, timeTable):
    # Splits activities in valid groups and tries to book them
    if activity.getMaxStudents() < len(activity.getCourse().getStudents()):
        studentGroups = split(activity)
    else:
        studentGroups = [activity.getCourse().getStudents()]

    count = 0
    for students in studentGroups:
        try:
            bookRoom(activity, sortedRoomSlots, students, timeTable)
            count += 1
        except:
            if count != 0:
                deleteActivity(activity, timeTable)
    return

def bookOrDeleteGroup(activity, roomSlots, students, timeTable, randomRoomSlots):
    try:
        bookRoom(activity, roomSlots, students, timeTable)
    except:
        deleteActivity(activity, timeTable)
        raise StandardError("hi")
    
def bookRoom(activity, roomSlots, students, timeTable):
    # Tries to book  
    for r in roomSlots:
        if roomIsValid(r, students, activity):
            group = Group(activity, students, activity.getMaxStudents(), r)
            timeTable.addGroup(group)
            return
    raise StandardError("No room can be found for " +
                              activity.getCourse().getName())
