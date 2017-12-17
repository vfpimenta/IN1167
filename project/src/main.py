import ga
import csv
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-k', '--kmax', dest='ks', type='int',
    help='Number of break points.', metavar='NUMBER')
parser.add_option('-s', '--series', dest='series', type='str',
    help='Target series [cf|jm|sv|3pp].', metavar='CHARACTER')

(options, args) = parser.parse_args()

def ROC(score):
  target = [1 if i%100==0 else 0 for i in range(len(read(options.series)))]

  fpr, tpr, _ = roc_curve(target, score)
  roc_auc = auc(fpr, tpr)

  return fpr, tpr, roc_auc

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
    fname = options.series
  elif not options.ks == None:
    print('Running series ks = {}...\n\n'.format(options.ks))
    series = read(options.ks)
    fname = options.ks
  else:
    raise Exception('Unknown arguments!')

  model = ga.GeneticAlgorithm(series, ks=options.ks, progress=True)
  model.run()

  # Basic info
  fig, ax = plt.subplots( nrows=1, ncols=1 )
  ax.plot(model.fitseries)
  fig.savefig('../tests/fitness/fitseries_{}.png'.format(fname), bbox_inches='tight')
  plt.close(fig)

  fig, ax = plt.subplots( nrows=1, ncols=1 )
  model.fitness(model.Xbest, True, ax)
  fig.savefig('../tests/best/best_strand_{}.png'.format(fname), bbox_inches='tight')
  plt.close(fig)

  # Analysis
  score = model.score()
  fig, ax = plt.subplots( nrows=1, ncols=1 )
  ax.plot(score, color='red')
  fig.savefig('../tests/ROC/score_{}.png'.format(fname), bbox_inches='tight')
  plt.close(fig)

  tpr, fpr, roc_auc = ROC(score)
  fig, ax = plt.subplots( nrows=1, ncols=1 )
  ax.plot(fpr, tpr, color='darkorange', label='ROC curve (area = {})'.format(roc_auc))
  ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
  plt.xlim([0.0, 1.0])
  plt.ylim([0.0, 1.05])
  plt.xlabel('False Positive Rate')
  plt.ylabel('True Positive Rate')
  plt.legend(loc="lower right")
  fig.savefig('../tests/ROC/roc_{}.png'.format(fname), bbox_inches='tight')
  plt.close(fig)
  

if __name__ == '__main__':
  main()