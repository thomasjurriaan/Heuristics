from hillclimber import *
from geneticalgorithm import *
from exportfunctions import *
import cProfile

if __name__ == '__main__':
    print "Welcome to Ultimate Scheduler 3000!"
    mainTimeTable = createTimeTableInstance()
    print "Creating random schedule, stored as 'mainTimeTable'."
    randomAlgorithm(mainTimeTable)
    print "This timetable has",getPoints(mainTimeTable)," points."

""" Thomas' chille functies """""
""""""""""""""""""""""""""""""""

''' print hillclimber '''
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