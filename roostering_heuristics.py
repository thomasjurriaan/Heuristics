from hillclimber import *
from geneticalgorithm import *
from exportfunctions import *
import cProfile

if __name__ == '__main__':
    print "Welcome to Ultimate Scheduler 3000!\n"

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
