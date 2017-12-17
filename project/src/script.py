import ga
import csv
import main
series = main.read()
model = ga.GeneticAlgorithm(series, ks=4, verbose=1)
model.run()
model.fitness(model.Xbest, True)
B = ['*'] * len(series)
B[42] = 42
B[270] = 270
B[676] = 676
B[821] = 821
i = ga.Individual(series,4)
i.B = B
i._make_attr_()
model.fitness(i,True)