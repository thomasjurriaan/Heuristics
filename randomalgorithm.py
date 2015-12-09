from points import *
from datastructure import *

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
    course = activity.getCourse()
    if (
        not r.hasGroup()
        and r.getSize()*OVERBOOK >= students
        and not courseInTimeSlot(course, r)
        ): return True
    return False

def bookRandomRoom(activity, randomRoomSlots, students, timeTable):
    # Tries to book an activity in a room. If succeeded: returns the booked
    # group
    nrStudents = len(students)
    for r in randomRoomSlots:
        if roomIsValid(r, nrStudents, activity):
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

