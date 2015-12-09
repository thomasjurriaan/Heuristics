import json

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""" Exporting function """""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def tableToList(timeTable):
    data = []
    for t in timeTable.getTimeSlots():
        for r in t.getRoomSlots():
            if r.hasGroup():
                group = r.getGroup()
                students = [
                    (s.getName(),s.getNr()) for s in group.getStudents()
                    ]
                data.append({
                    "startTime": 2*t.getTime(),
                    #int of number of houres after 9 
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
##    with open("Visualisatie/Data/main.json", 'wb') as f:
##        json.dump(data, f, encoding='latin1')
    students = timeTable.getStudents()
    print "Saving timetables of "+str(len(students))+" students..."
    for i, s in enumerate(students):
        data = studentToList(s)
        filename = "student"+str(i)+".json"
        with open("Visualisatie/Data/"+filename, 'wb') as f:
            json.dump(data, f, encoding='latin1')
    courses = timeTable.getCourses()
    print "Saving timetables of "+str(len(courses))+" courses..."
    for i, c in enumerate(courses):
        data = courseToList(c)
        filename = "course"+str(i)+".json"
        with open("Visualisatie/Data/"+filename, 'wb') as f:
            json.dump(data, f, encoding='latin1')
                
    return

def saveTimeTable(timeTable):
    filename = raw_input("Name your timetable json: ")+".json"
    print "Data is stored in .../visualisation/Data/"+filename+"..."
    data = tableToList(timeTable)
    with open("Visualisatie/Data/"+filename, 'wb') as f:
        json.dump(data, f, indent=True, encoding='latin1')
    return
