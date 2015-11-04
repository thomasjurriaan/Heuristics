import json

FILE = 'studenten_roostering.csv'
OUTPUTFILE = 'students.json'
            
def makeDatalist(filename):
    """
    Leest de csv-file met de rooster data
    Zet de data om in een lijst van dictionaries
    """
    with open(filename, 'r') as f:
        dataList = []
        for row in f:
            e = row.split(',')
            # Verwijderen van lege inputs
            d = [i.rstrip().decode('utf8','ignore') for i in e if any(c.isalpha() for c in i)]
            for n, i in enumerate(d):
                if i == "Zoeken":
                    s = d[n]+d[n+1]
                    d = d[:n]+[s]+d[(n+2):]
                    break
            dataList.append({
                "lastName": e[0],
                "firstName": e[1],
                "nr":e[2],
                "courses":[i for i in d[2:]]
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
    print "Compiling JSON..."
    makeJSON(dataList, OUTPUTFILE)
