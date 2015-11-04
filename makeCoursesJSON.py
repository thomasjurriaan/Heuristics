import json
#import matplotlib.pyplot as plt
#import numpy as np

FILE = 'students.json'
OUTPUTFILE = 'courses.json'
            
def makeCoursesDict(filename):
    """
    Leest de csv-file met de rooster data
    Zet de data om in een lijst van dictionaries
    """
    json_data=open(filename).read()
    f = json.loads(json_data)[1:]
    coursesDict = {}
    for student in f:
        for course in student["courses"]:
            if course not in coursesDict.keys():
                coursesDict[course]=[]
            for c in student["courses"]:
                if c != course: coursesDict[course].append(c)
    return coursesDict
    
def makeGraphData(filename):
    graphData = []
    for course in filename.keys():
        graphData.append({
            "name":course,
            "size":1,
            "imports":filename[course]
        })
    return graphData

def plotBar(L):
    hist, bins = np.histogram(L, bins=7)
    width = 0.7 * (bins[1] - bins[0])
    center = (bins[:-1] + bins[1:]) / 2
    plt.bar(center, hist, align='center', width=width)
    plt.show()

def makeJSON(dataList, filename):
    '''
    Slaat JSON bestand op met een dictionary voor elke student.

    Elke dictionary bevat de naam, het studentennummer en de
    vakken die de student volgt. De vakken staan in een lijst van
    strings. De andere keys verwijzen naar strings.

    De bijbehorende keys zijn "lastName","firstName","nr" en "courses"
    '''
    with open(filename, 'wb') as f:
        json.dump(dataList, f, indent=True, encoding='latin1')
        
if __name__ == '__main__':
    print "Sorting courses data..."
    coursesDict = makeCoursesDict(FILE)
    print "Resorting data for graph..."
    graphData = makeGraphData(coursesDict)
    courses = [course for course in coursesDict.keys()]
    barL = []
    for course in coursesDict.keys():
        L = []
        for e in courses:
            if e in coursesDict[course]:
                L.append(e)
        print course, "connected with courses: ",len(L)
#        barL.append(len(L))
#    plotBar(barL)
    print "Compiling JSON..."
    makeJSON(graphData, OUTPUTFILE)
