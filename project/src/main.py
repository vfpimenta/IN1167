import ga
import csv
import matplotlib.pyplot as plt

def read(n):
  series = list()
  with open('../data/series_{}.csv'.format(n)) as csvfile:
    spamreader = csv.reader(csvfile)
    for row in spamreader:
      series.append(float(row[0]))

  return series

def main():
  for ks in [5,9,11]:  
    print('> Running series ks = {}...\n\n'.format(ks))
    series = read(ks)

    model = ga.GeneticAlgorithm(series, ks=ks, verbose=1)
    model.run()

    fig, ax = plt.subplots( nrows=1, ncols=1 )
    ax.plot(model.fitseries)
    fig.savefig('fitseries_{}.png'.format(ks), bbox_inches='tight')
    plt.close(fig)

    fig, ax = plt.subplots( nrows=1, ncols=1 )
    model.fitness(model.Xbest, True, ax)
    fig.savefig('best_strand_{}.png'.format(ks), bbox_inches='tight')
    plt.close(fig)

if __name__ == '__main__':
  main()