from hillclimber import *
from geneticalgorithm import *
from exportfunctions import *
import cProfile

if __name__ == '__main__':
    print "Welcome to Ultimate Scheduler 3000!\n"
##    mainTimeTable = createTimeTableInstance()
##    print "Creating random schedule, stored as 'mainTimeTable'."
##    randomAlgorithm(mainTimeTable)
##    print "This timetable has",getPoints(mainTimeTable)," points."
    print "========================="
    print "Testing genetic algorithm"
    print "========================="
    n = 1
    roosters = []
    while n < 11:
        print "Creating schedule ",n
        try:
            r = geneticAlgorithm(150, text=False, goToMax=True, nrChilds=50)
            print "Schedule ",n," has ",r.getPoints()," points."
            n+=1
            roosters.append(r)
        except:
            print "Memory error?.."
        print "\n"
