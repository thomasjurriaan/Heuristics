"""***********************************************************************
* makeCourseInfJSON.py
*
* Heuristieken
* Daan van den Berg
*
* Converts course information saved in CSV format to JSON format. Outputs
* converted data into coursesInf.json found in the same directory as this
* file. 
*
***********************************************************************"""

import json
import itertools

FILE = 'courseInf.csv'
OUTPUTFILE = 'coursesInf.json'

def makeDatalist(filename):
    """
    Leest de csv-file met de rooster data
    Zet de data om in een lijst van dictionaries
    """
    with open(filename, 'r') as f:
        dataList = []
        # itertools open alleen de eerste 10 regels
        for row in f:
            e = row.split(',')
            if e[3]== "nvt": a = float('inf')
            else: a = int(e[3])
            if e[5]== "nvt": b = float('inf')
            else: b = int(e[5])
            # Verwijderen van lege inputs
            #if any(c.isalpha() for c in i)
            dataList.append({
                "courseName": e[0],
                "lectures": int(e[1]),
                "seminar":int(e[2]),
                "maxStudSeminar": a,
                "practica": int(e[4]),
                "maxStudPractica": b
                })
    return dataList

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
    print "Sorting course data..."
    dataList = makeDatalist(FILE)
    print "compiling JSON..."
    makeJSON(dataList, OUTPUTFILE)
