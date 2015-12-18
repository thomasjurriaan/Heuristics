"""***********************************************************************
* roostering_heuristics.py
*
* Heuristieken
* Daan van den Berg
*
* Mainfile in which you can call the algorithms to optimize the
* timetable produced by the init function or find the best timetable
* the deterministic way
*
***********************************************************************"""

from hillclimber import *
from geneticalgorithm import *
from exportfunctions import *
import cProfile

if __name__ == '__main__':
    print "Welcome to Ultimate Scheduler 3000!\n"

def r():
	hendrik = createTimeTableInstance()
	randomAlgorithm(hendrik)
	return hendrik

def testGeneticAlgorithm(schedules = 20):
    print "========================="
    print "Testing genetic algorithm"
    print "========================="
    n = 0
    roosters = []
    while n < schedules:
        print "Creating schedule ",n+1
        r = geneticAlgorithm(100, text=False, goToMax=True, nrChilds=60, allowIncest=True)
        print "Schedule ",n," has ",r.getPoints()," points."
        n+=1
        roosters.append(r.getPoints())
        print "\n"
    return roosters

def hillandsimresults():
    hillscores = []
    maxhill = []
    simscores = []
    maxsim = []
    for i in range(50):
        main = r()
        while getPoints(main) == None:
            main = r()
        hillscore = hillclimbAlgorithm(main, 0.7, doPlot=False)
        hillscores.append(hillscore)
        while getPoints(main) == None:
            main = r()
        simscores.append(hillclimbAlgorithm(main, sim = True, doPlot = False))
        print "iteration:", i
    for s in hillscores:
        maxhill.append(max(s))
    for s in simscores:
        maxsim.append(max(s))
    return hillscores, simscores, maxhill, maxsim

def runDeterministic():
    timeTable = createTimeTableInstance()
    deterministic(timeTable)
    
def randomresults(iterations = 1000):
    scores = []
    for i in range(iterations):
        main = r()
        score = getPoints(main)
        while score == None:
            main = r()
            score = getPoints(main)
        scores += score
    return score

