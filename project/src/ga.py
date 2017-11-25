import random
import string
import numpy as np

# =============================================================================

class GeneticAlgorithm:

  def __init__(self, series, M=50, ks=None, verbose=False):
    if ks == None:
      ks = random.randint(1,20)

    self.Xbest = Individual(series, ks)
    self.fitseries = list()
    self.series = series
    self.ks = ks

    self.pop = [Individual(series, ks) for i in range(M)]
    if 1 <= ks <= 6:
      self.alpha = random.uniform(.2, .3)
      self.pmu = random.uniform(.4, .5)
      self.popc = (1-self.pmu)/3
      self.puc = 2*self.popc
    elif ks > 6:
      self.alpha = .1
      self.pmu = .3
      self.popc = (1-self.pmu)/2
      self.puc = (1-self.pmu)/2

    self.pm = ks/len(series)
    self.pb = .6

    self.rounds = 20000
    self.max_stalls = 100
    self.verbose = verbose
  
  def fitness(self, X):
    return g(X) + self.alpha * p(X.k)

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
      if self.verbose:
        print('Running round {} out of {}...\nCurrent population:\n'.format(i+1,self.rounds))
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
        C = Individual(self.series, self.ks, Xi, method='m', pm=self.pm, pb=self.pb)
        if self.verbose:
          print('Selected operation is mutation.\n Mutated {} into {}'.format(Xi.id, C))

      Xmin = min(self.pop, key=lambda i: self.fitness(i))
      replace = self.fitness(C) / (self.fitness(C) + self.fitness(Xmin))
      keep = 1 - replace
      choice = np.random.choice(2, p=[replace, keep])

      if C.k == 0:
        if self.verbose:
          print('Bad strand generated! Aborting...')
        continue

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

    if exit_status == 1:
      print('\nStopped execution by reaching max generations {}'.format(self.rounds))
    else:
      print('\nStopped execution due to best fitness not being improved in the last {} generations'.format(self.max_stalls))
    print('\nFound best strand {} with fitness = {}'.format(self.Xbest, self.fitness(self.Xbest)))

# =============================================================================

class Individual:

  def __init__(self, series, ks, parentA=None, parentB=None, method=None, pm=None, pb=None):
    # ''.join(list(np.random.choice(list(string.ascii_uppercase),3)))
    self.id = np.random.randint(1000,9999)
    self.series = series
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
      choices = np.random.choice(3, len(parentA.B), p=[pm*pb, pm*pe, 1-pm])
      self.trace = '[{}->{}]'.format(parentA.id, self.id)
      self.B = [i if choices[i] == 0 else '*' if choices[i] == 1 else parentA.B[i] for i in range(len(parentA.B))]

    self._make_attr_()

  def __str__(self):
    return '<id:{}, trace:{}, B:{}, k:{}>'.format(self.id, self.trace, self.B, self.k)

  def _make_attr_(self):
    self.b = [i for i in self.B if i != '*']
    self.k = len(self.b)

  def y(self, i):
    return self.series[i]

# =============================================================================

def make_prob_list(l):
  return list(map(lambda el: el/sum(l), l))

def g(X):
  return (area(X) - sum([area(X, j) for j in range(0, X.k-1)])) / area(X)

def p(k):
  return 1/np.sqrt(k)

def area(X, j=None):
  if j == None:
    return (len(X.B)) * (max(X.series) - min(X.series))
  else:
    try:
      m0 = min(list(map(X.y, range(X.b[j],X.b[j+1]))))
      m1 = max(list(map(X.y, range(X.b[j],X.b[j+1]))))
      return (X.b[j+1] - X.b[j]) * (m1 - m0)
    except ValueError as e:
      print(X)
      raise e