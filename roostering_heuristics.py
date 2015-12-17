from hillclimber import *
from geneticalgorithm import *
from exportfunctions import *
import cProfile

if __name__ == '__main__':
    print "Welcome to Ultimate Scheduler 3000!\n"

def r():
	hendrik = createTimeTableInstance()
	randomAlgorithm(hendrik)
	print "Dit rooster heeft", getPoints(hendrik), "punten."
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

def printhillclimber(iterations = 50, hilliterations = 25000):
	randomscores = []
	scores = []
	highscores = []
	for i in range(iterations):
		h = createTimeTableInstance()
		randomAlgorithm(h)
		randomscores.append(getPoints(h))
		scores.append(hillclimbAlgorithm(h, hilliterations, doPlot = False))
	return randomscores, scores, highscores
