import random
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# =============================================================================

class GeneticAlgorithm:

  def __init__(self, series, M=50, ks=None, verbose=0, halt=False):
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
  
  def fitness(self, X, plot=False, ax=None):
    if plot:
      ax.plot(self.series)
    return max(sys.float_info.min, g(X,plot,ax) - self.alpha * p(X.k, self.kmax))

  def get_individual(self, n):
    probabilities = list(map(lambda i: self.fitness(i), self.pop))
    choices = np.random.choice(len(self.pop), n, p=make_prob_list(probabilities), replace=False)
    if n > 1:
      return tuple([self.pop[i] for i in choices])
    elif n == 1:
      return self.pop[choices[0]]

  def run(self):
    stalls = 0
    exit_status = 0

    for i in range(self.rounds):
      if self.verbose >= 1:
        print('Running round {} out of {}...'.format(i+1,self.rounds))
      if self.verbose >= 2:
        print('\nCurrent population:\n')
        for ind in self.pop:
          print('{} :: fitness={}'.format(ind,str(self.fitness(ind))))

      operation = np.random.choice(3, p=make_prob_list([self.popc, self.puc, self.pmu]))

      if operation == 0:
        Xi, Xj = self.get_individual(2)
        C = Individual(self.series, self.ks, Xi, Xj, method='uc')
        if self.verbose >= 2:
          print('Selected operation is uniform crossover.\nCreating new strand with parents {} and {}...\nObtained: {}'.format(Xi.id, Xj.id, C))
      elif operation == 1:
        Xi, Xj = self.get_individual(2)
        C = Individual(self.series, self.ks, Xi, Xj, method='opc')

        if self.verbose >= 2:
          print('Selected operation is one-point crossover.\nCreating new strand with parents {} and {}...\nObtained: {}'.format(Xi.id, Xj.id, C))
      else:
        Xi = self.get_individual(1)
        C = Individual(self.series, self.ks, Xi, method='m', pb=self.pb)
        if self.verbose >= 2:
          print('Selected operation is mutation.\n Mutated {} into {}'.format(Xi.id, C))

      if C.k == 0:
        if self.verbose >= 2:
          print('Bad strand generated! Aborting...')
        continue

      Xmin = min(self.pop, key=lambda i: self.fitness(i))
      replace = self.fitness(C) / (self.fitness(C) + self.fitness(Xmin))
      keep = 1 - replace
      choice = np.random.choice(2, p=[replace, keep])
      

      if choice == 0:
        self.pop.remove(Xmin)
        self.pop.append(C)
        if self.verbose >= 2:
          print('Replaced minimum-fitness strand with {}'.format(C))

      Xmax = max(self.pop, key=lambda i: self.fitness(i))
      if self.fitness(Xmax) > self.fitness(self.Xbest):
        self.Xbest = Xmax
        stalls = 0
      else:
        stalls += 1

      self.fitseries.append(self.fitness(self.Xbest))
      if self.verbose >= 2:
        print('Best fitness so far: {}'.format(self.fitness(self.Xbest)))

      if stalls > self.max_stalls:
        exit_status = 1
        break

      if self.halt:
        input()

    if exit_status == 0:
      print('\nStopped execution by reaching max generations {}'.format(self.rounds))
    else:
      print('\nStopped execution due to best fitness not being improved in the last {} generations'.format(self.max_stalls))
    print('\nFound best strand {} with fitness = {}'.format(self.Xbest, self.fitness(self.Xbest)))

# =============================================================================

class Individual:

  def __init__(self, series, ks, parentA=None, parentB=None, method=None, pb=None):
    self.id = np.random.randint(1000,9999)
    self.series = series
    self.min_width = len(series)/10
    T = len(series)

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

def ziplist(X, padding=0):
  l = list()
  if X.b[0] > padding:
    l.append((0,X.b[0]-padding))
  if X.b[-1] < len(X.B)-1-padding:
    l.append((X.b[-1]+padding,len(X.B)-1))
  for i in range(X.k-1):
    l.append((X.b[i]+padding,X.b[i+1]-padding))
  return l

def g(X, plot, ax):
  return (area(X) - sum([area(X, j0, j1, plot, ax) for j0, j1 in ziplist(X)])) / area(X)

def p(k, kmax):
  if kmax == None: 
    return 1/np.sqrt(k)
  else:
    return np.abs((kmax-k+1)/kmax)

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