"""***********************************************************************
* randomalgorithm.py
*
* Heuristieken
* Daan van den Berg
*
* This file contains the functions and the algorithme responsible for creating
* a timetable randomly a.k.a. the random algorithm. 
*
***********************************************************************"""


from points import *
from datastructure import *


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""  Random booking algorithm     """""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


def courseInTimeSlot(course, roomSlot):
    """
    Subfunction of roomIsValid()

    Checks if another activity of the same course is allready in this timeslot.
    Courses shouldn't be able to book multiple activities in the same timeslot.
    Returns a boolean
    """
    timeSlot = roomSlot.getTimeSlot()
    for r in timeSlot.getRoomSlots():
        if r.hasGroup():
            group = r.getGroup()
            if course == group.getActivity().getCourse():
                return True
    return False


def roomIsValid(roomSlot, students, activity):
    """
    Subfunction of bookRandomRoom()

    Checks if a room is suited for an activity.
    Returns a boolean
    """
    r = roomSlot
    course = activity.getCourse()
    if (
        not r.hasGroup()
        and r.getSize()*OVERBOOK >= students
        and not courseInTimeSlot(course, r)
        ): return True
    return False


def bookRandomRoom(activity, randomRoomSlots, students, timeTable):
    """
    Subfunction of bookActivity()

    Tries to book an activity in a room. If this fails an error is raised.
    """
    nrStudents = len(students)
    for r in randomRoomSlots:
        if roomIsValid(r, nrStudents, activity):
            group = Group(activity, students, activity.getMaxStudents(), r)
            timeTable.addGroup(group)
            return
    else: raise StandardError("No room can be found for " +
                              activity.getCourse().getName())

    
def split(activity):
    """
    Subfunction of bookActivity()

    Takes an activity with more students than allowed per group and returns
    lists of valid student groups.
    Returns multiple lists of student-instances.
    """
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
    """
    Subfunction of randomAlgorithm()
    
    It takes in an random activity and a shuffled list of roomslots, then
    tries to book the activity in the first suiting roomslot.
    """
    if activity.getMaxStudents() < len(activity.getCourse().getStudents()):
        studentGroups = split(activity)
    else: studentGroups = [activity.getCourse().getStudents()]

    for g in studentGroups:
        try: bookRandomRoom(activity, randomRoomSlots, g, timeTable)
        except: break
    return

        
def randomAlgorithm(timeTable):
    """
    The actual algoritm. It takes in an empty timetable-instance and fills it
    with groups, depending on the demands of the activities in the schedule.
    """
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

