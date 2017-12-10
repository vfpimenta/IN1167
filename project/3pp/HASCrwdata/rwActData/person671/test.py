import csv
import math
import matplotlib.pyplot as plt

def l2norm(*args):
  return math.sqrt(sum([float(a)**2 for a in args]))

series = list()
with open('hasc-111018-165936-acc.csv','r') as csvfile:
  spamreader = csv.reader(csvfile)
  for row in spamreader:
    series.append(l2norm(row[1], row[2], row[3]))

plt.plot(series)
plt.show()