import ga
import csv
import matplotlib.pyplot as plt

def main():
  series = list()
  with open('../data/series.csv') as csvfile:
    spamreader = csv.reader(csvfile)
    for row in spamreader:
      series.append(float(row[0]))

  model = ga.GeneticAlgorithm(series)
  model.run()

  plt.plot(model.fitseries)
  plt.show()

if __name__ == '__main__':
  main()