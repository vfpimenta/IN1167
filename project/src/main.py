import ga
import csv
import matplotlib.pyplot as plt
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-k', '--kmax', dest='ks', type='int',
    help='Number of break points.', metavar='NUMBER')
parser.add_option('-s', '--series', dest='series', type='str',
    help='Target series \{cf,jm,sv\}.', metavar='CHARACTER')

(options, args) = parser.parse_args()

def read(n):
  series = list()
  with open('../data/series/series_{}.csv'.format(n)) as csvfile:
    spamreader = csv.reader(csvfile)
    for row in spamreader:
      series.append(float(row[0]))

  return series

def main():
  if not options.series == None:
    series = read(options.series)

    model = ga.GeneticAlgorithm(series, ks=options.ks, halt=True)
    model.run()

    fig, ax = plt.subplots( nrows=1, ncols=1 )
    ax.plot(model.fitseries)
    fig.savefig('../tests/fitseries_{}.png'.format(options.series), bbox_inches='tight')
    plt.close(fig)

    fig, ax = plt.subplots( nrows=1, ncols=1 )
    model.fitness(model.Xbest, True, ax)
    fig.savefig('../tests/best_strand_{}.png'.format(options.series), bbox_inches='tight')
    plt.close(fig)
  elif not options.ks == None:
    print('Running series ks = {}...\n\n'.format(options.ks))
    series = read(options.ks)

    model = ga.GeneticAlgorithm(series, ks=options.ks, halt=True)
    model.run()

    fig, ax = plt.subplots( nrows=1, ncols=1 )
    ax.plot(model.fitseries)
    fig.savefig('../tests/fitseries_{}.png'.format(options.ks), bbox_inches='tight')
    plt.close(fig)

    fig, ax = plt.subplots( nrows=1, ncols=1 )
    model.fitness(model.Xbest, True, ax)
    fig.savefig('../tests/best_strand_{}.png'.format(options.ks), bbox_inches='tight')
    plt.close(fig)
  else:
    raise Exception('Unknown arguments!')

if __name__ == '__main__':
  main()