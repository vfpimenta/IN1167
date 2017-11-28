import ga
import csv
import matplotlib.pyplot as plt

def read():
  series = list()
  with open('../data/series.csv') as csvfile:
    spamreader = csv.reader(csvfile)
    for row in spamreader:
      series.append(float(row[0]))

  return series

def main():
  series = read()

  model = ga.GeneticAlgorithm(series, ks=4, verbose=True, halt=True)
  model.run()

  plt.plot(model.fitseries)
  plt.show()

if __name__ == '__main__':
  main()