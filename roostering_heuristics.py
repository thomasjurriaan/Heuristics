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

def testGeneticAlgorithm():
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

