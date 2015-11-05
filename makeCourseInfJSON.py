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
            # Verwijderen van lege inputs
            #if any(c.isalpha() for c in i)
            dataList.append({
                "courseName": e[0],
                "lectures": e[1],
                "PS":e[2],
                "maxStudPS":e[3],
                "practica": e[4],
                "MaxStudPractica": e[5]
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
    print "Sorting student data..."
    dataList = makeDatalist(FILE)
    print "compiling JSON..."
    makeJSON(dataList, OUTPUTFILE)
