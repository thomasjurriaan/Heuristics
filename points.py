"""***********************************************************************
* points.py
*
* Heuristieken
* Daan van den Berg
*
* Contains all functions responsible for computing the value of a timetable
* instance. 
*
***********************************************************************"""

import random
import math
import itertools

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
"""""""""""""""  Counting points """""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def allCoursesScheduled(timeTable):
    """
    subfunction of getPoints()
    
    Checks whether the timetable is satisfying the hard constraint: fill
    out the timetable completely with all activities devided in groups if
    necessary. 
    """
    if timeTable == None: return False
    
    students = timeTable.getStudents()
    for s in students:
        nrAct = 0
        for c in s.getCourses():
            nrAct += len(c.getActivities())
        nrGr = len(s.getGroups())
        if nrAct > nrGr:
            print nrAct, nrGr
            return False
    return True

def checkCount(dList, nrAct):
    """
    subfunction of spreadBonusPoints()

    Checks it contains the right amount of days to give bonuspoints
    """
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
    """
    subfunction of coursesMaximallySpread()

    Calculates if a course has the right spread in order to
    get bonus points
    """
    nrAct = len(c.getActivities())
    if nrAct < 2 or nrAct > 4:
        return 0
    cDays = []
    for a in c.getActivities():
        aDays = []
        for g in a.getGroups():
            if g == group and r != None:
                d = r.getTimeSlot().getDay()
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
    """
    subfunction of getPoints()

    Calculates all bonuspoints of each course and returns total value
    of all courses in the timeTable. Yeyaa
    """
    courses = timeTable.getCourses()
    bonus = 0
    for c in courses:
        bonus += spreadBonusPoints(c)            
    return bonus

def overbookMalusPoints(r):
    """
    subfunction of overBookMalusPoints

    Checks for a room if it's overbooked and returns a int value
    which represents the maluspoints for the overbooking
    """
    if (r.getStudents() != None):
        saldo = len(r.getStudents()) - r.getSize()
        if saldo > 0:
            return saldo
        else: return 0
    else: return 0

def overbooked(timeTable):
    """
    subfunction of getPoints()

    Checks with function overBookMalusPoints() the maluspoints for
    each roomslot in the timeTable and returns the total value
    """
    malus = 0
    saldo = 0;
    ts = timeTable.getTimeSlots()
    rs = []
    for t in ts:
        rs += t.getRoomSlots()
    for r in rs:
        malus += overbookMalusPoints(r)
    return malus

def studentMalusPoints(s, originalRoom = None, newRoom = None):
    """
    subfunction of personalScheduleConflict()

    Checks per student whether he has a personal schedule conflict.
    A personal schedule conflict is when the student has two different
    activities as the same time. Returns the maluspoints per student
    """
    individualMalus = 0
    rList = []
    cList = []
    for g in s.getGroups():
        rList.append(g.getRoomSlot())
    for r in rList:
        if newRoom != None and r == originalRoom:
            r = newRoom
        if r.getTimeSlot() in cList:
            individualMalus += 1
        cList.append(r.getTimeSlot())
    return individualMalus

def personalScheduleConflict(timeTable):
    """
    subfunction of getPoints()

    Returns total value of all personal schedule conflicts in a
    timeTable
    """
    students = timeTable.getStudents()
    malus = 0
    # Loop over lijst met students heen
    for s in students:
        malus += studentMalusPoints(s)
    return malus
                    


def spreadMalusPoints(c, r = None, group = None):
    """
    subfunction of activityConflict()

    Check whether two groups are scheduled at the same time
    Returns value per conflict
    """
    malus = 0
    nrAct = 0
    days = []
    for a in c.getActivities():
        nrAct += 1
        for g in a.getGroups():
            if g == group and r != None:
                day = r.getTimeSlot().getDay()
            else:
                day = g.getRoomSlot().getTimeSlot().getDay()
            days.append(day)
    if nrAct > len(set(days)): malus += 10
    return malus

def activityConflict(timeTable):
    """
    Returns total value of all schedule conflicts of a timeTable
    """
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

def getPointsDeterministic(timeTable):
    """
    same as getPoints() but does not use the allCoursesScheduled() to check
    whether a timeTable is complete. 
    """
    points = 1000
    points += coursesMaximallySpread(timeTable)
    points -= activityConflict(timeTable)
    points -= overbooked(timeTable)
    points -= personalScheduleConflict(timeTable)
    return points

