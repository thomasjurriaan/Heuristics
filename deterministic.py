"""***********************************************************************
* deterministic.py
*
* Heuristieken
* Daan van den Berg
*
* Contains all contents needed for the deterministic algorithm
*
***********************************************************************"""

from points import *
from datastructure import *
from exportfunctions import *
from randomalgorithm import *
import operator


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""  Deterministic booking algorithm"""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def deterministic(timeTable):
    """
    Deterministische algoritme. Hieronder staan een aantal lijsten die als
    input kunnen worden gebruikt voor de while loop. 
    """
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
                # Maak children van parent
                try:
                    children = generateAllChildren(parent[1], activityList)
                    stack.append(children)
                except:
                    # Calculeer maxpoints en vergelijk timetable met eerder resultaat
                    currentScore = getPointsDeterministic(timeTable)
                    count += 1
                    lBookedActivity = bookedActivities.pop()
                    if currentScore > bestScore: bestScore = currentScore
                    if count > 1000:
                        count = 0
                        print bestScore
                    deleteActivity(lBookedActivity[1], timeTable)


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
