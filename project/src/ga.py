import random
import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import util

# =============================================================================

class GeneticAlgorithm:

  def __init__(self, series, M=50, ks=None, verbose=False, halt=False, progress=False):
    if ks == None:
      ks = random.randint(1,20)
      self.kmax = None
    else:
      self.kmax = ks

    self.Xbest = Individual(series, ks)
    self.fitseries = list()
    self.series = series
    self.ks = ks

    self.pop = [Individual(series, ks) for i in range(M)]
    if 1 <= ks <= 6:
      self.alpha = random.uniform(.2, .3)
      self.pmu = random.uniform(.5, .6)
      self.popc = (1-self.pmu)/3
      self.puc = 2*self.popc
    elif ks > 6:
      self.alpha = .1
      self.pmu = .3
      self.popc = (1-self.pmu)/2
      self.puc = (1-self.pmu)/2

    self.pb = .6

    self.rounds = 20000
    self.max_stalls = 800
    self.verbose = verbose
    self.halt = halt
    self.progress = progress
  
  def fitness(self, X, plot=False, ax=None):
    if plot:
      ax.plot(self.series)
      return g(X,plot,ax) + self.alpha * p(X.k, self.kmax)

    if X.fitness:
      return X.fitness
    else:
      fitness = g(X,plot,ax) + self.alpha * p(X.k, self.kmax)
      X.fitness = fitness
      return fitness

  def get_individual(self, n):
    probabilities = list(map(lambda i: self.fitness(i), self.pop))
    choices = np.random.choice(len(self.pop), n, p=make_prob_list(probabilities), replace=False)
    if n > 1:
      return tuple([self.pop[i] for i in choices])
    elif n == 1:
      return self.pop[choices[0]]

  def valid(self, Individual):
    constraints = {
      'min k': lambda i: False if i.k == 0 else True,
      'chosen max k': lambda i: False if (self.kmax != None and i.k > self.kmax) else True,
      'series max k': lambda i: False if i.k > len(self.series)/100 else True,
      'repeated i': lambda i: False if any([x.B == i.B for x in self.pop]) else True
    }
    for key in constraints.keys():
      if not constraints[key](Individual):
        return False

    return True

  def run(self):
    stalls = 0
    exit_status = 0

    i = 0
    while i < self.rounds:
      if self.verbose:
        print('Running round {} out of {}...'.format(i+1,self.rounds))
        print('\nCurrent population:\n')
        for ind in self.pop:
          print('{} :: fitness={}'.format(ind,str(self.fitness(ind))))

      operation = np.random.choice(3, p=make_prob_list([self.popc, self.puc, self.pmu]))

      if operation == 0:
        Xi, Xj = self.get_individual(2)
        C = Individual(self.series, self.ks, Xi, Xj, method='uc')

        if self.verbose:
          print('Selected operation is uniform crossover.\nCreating new strand with parents {} and {}...\nObtained: {}'.format(Xi.id, Xj.id, C))
      elif operation == 1:
        Xi, Xj = self.get_individual(2)
        C = Individual(self.series, self.ks, Xi, Xj, method='opc')

        if self.verbose:
          print('Selected operation is one-point crossover.\nCreating new strand with parents {} and {}...\nObtained: {}'.format(Xi.id, Xj.id, C))
      else:
        Xi = self.get_individual(1)
        C = Individual(self.series, self.ks, Xi, method='m', pb=self.pb)

        if self.verbose:
          print('Selected operation is mutation.\n Mutated {} into {}'.format(Xi.id, C))

      if not self.valid(C):
        if self.verbose:
          print('Bad strand generated! Aborting...')
        continue

      Xmin = min(self.pop, key=lambda i: self.fitness(i))
      replace = self.fitness(C) / (self.fitness(C) + self.fitness(Xmin))
      keep = 1 - replace
      choice = np.random.choice(2, p=[replace, keep])

      if choice == 0:
        self.pop.remove(Xmin)
        self.pop.append(C)
        if self.verbose:
          print('Replaced minimum-fitness strand with {}'.format(C))

      Xmax = max(self.pop, key=lambda i: self.fitness(i))
      if self.fitness(Xmax) > self.fitness(self.Xbest):
        self.Xbest = Xmax
        stalls = 0
      else:
        stalls += 1

      self.fitseries.append(self.fitness(self.Xbest))
      if self.verbose:
        print('Best fitness so far: {}'.format(self.fitness(self.Xbest)))

      if stalls > self.max_stalls:
        exit_status = 1
        break

      if self.halt:
        input()

      i += 1
      if self.progress:
        util.printProgressBar(i, self.rounds, prefix='Running GA', suffix='Generations')

    if exit_status == 0:
      print('\nStopped execution by reaching max generations {}'.format(self.rounds))
    else:
      print('\nStopped execution due to best fitness not being improved in the last {} generations'.format(self.max_stalls))
    print('\nFound best strand {} with fitness = {}'.format(self.Xbest, self.fitness(self.Xbest)))

  def score(self):
    score = list()
    for i in range(len(self.series)):
      score.append(sum(b != '*' for b in [ind.B[i] for ind in self.pop])/len(self.pop))

    return score

# =============================================================================

class Individual:

  def __init__(self, series, ks, parentA=None, parentB=None, method=None, pb=None):
    self.id = np.random.randint(1000,9999)
    self.series = series
    self.min_width = len(series)/10
    T = len(series)

    self.fitness = None

    if method == None:
      bs = random.sample(range(T), ks)
      self.trace = '[]'
      self.B = [i if i in bs else '*' for i in range(T)]
    elif method == 'uc':
      choices = np.random.choice(2, T)
      self.trace = '[{}+{}]'.format(parentA.id, parentB.id)
      self.B = [parentA.B[i] if choices[i] == 0 else parentB.B[i] for i in range(T)]
    elif method == 'opc':
      point = random.choice(range(T))
      self.trace = '[{}+{}]'.format(parentA.id, parentB.id)
      self.B = [parentA.B[i] if i < point else parentB.B[i] for i in range(T)]
    elif method == 'm':
      pe = 1-pb
      pm = 2*parentA.k/T
      choices = np.random.choice(3, len(parentA.B), p=[pm*pb, pm*pe, 1-pm])
      self.trace = '[{}->{}]'.format(parentA.id, self.id)
      self.B = [i if choices[i] == 0 else '*' if choices[i] == 1 else parentA.B[i] for i in range(len(parentA.B))]

    self._make_attr_()

  def __str__(self):
    return '<id:{}, trace:{}, b:{}, k:{}>'.format(self.id, self.trace, self.b, self.k)

  def _make_attr_(self):
    self.b = [i for i in self.B if i != '*']
    self.k = len(self.b)

  def y(self, i):
    return self.series[i]

# =============================================================================

def make_prob_list(l):
  return list(map(lambda el: el/sum(l), l))

def ziplist(X, padding=2):
  l = list()
  if X.b[0] > padding:
    l.append((0,X.b[0]-padding))
  if X.b[-1] < len(X.B)-1-padding:
    l.append((X.b[-1]+padding,len(X.B)-1))
  for i in range(X.k-1):
    if X.b[i]+padding < X.b[i+1]-padding:
      l.append((X.b[i]+padding,X.b[i+1]-padding))
    else:
      l.append((X.b[i],X.b[i+1]))
  return l

def g(X, plot, ax):
  return (area(X) - sum([area(X, j0, j1, plot, ax) for j0, j1 in ziplist(X)])) / area(X)

def p(k, kmax):
  if kmax == None: 
    return 1/np.sqrt(k)
  else:
    return max(0, (kmax-k+1)/kmax)

def area(X, j0=None, j1=None, plot=False, ax=None):
  if j0 == None:
    return (len(X.B)) * (max(X.series) - min(X.series))
  else:
    try:
      m0 = min(list(map(X.y, range(j0, j1))))
      m1 = max(list(map(X.y, range(j0, j1))))
      if plot:
        ax.add_patch(patches.Rectangle(
          (j0, m0),
          j1 - j0,
          m1-m0,
          fill=False
        ))
      return (j1 - j0) * (m1 - m0)
    except ValueError as e:
      print(X)
      raise e