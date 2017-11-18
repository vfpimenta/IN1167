import ga
import csv

def main():
  series = list()
  with open('../data/series.csv') as csvfile:
    spamreader = csv.reader(csvfile)
    for row in spamreader:
      series.append(float(row[0]))

  model = ga.GeneticAlgorithm(series, 100, 3)
  model.run()

  print(model.Xbest)

if __name__ == '__main__':
  main()