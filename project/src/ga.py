import random
import numpy as np

# =============================================================================

class GeneticAlgorithm:

  def __init__(self, series, M, ks):
    self.Xbest = Individual(series, ks)
    self.series = series
    self.ks = ks

    self.pop = [Individual(series, ks) for i in range(M)]
    self.alpha = random.random()
    self.puc = random.random()
    self.popc = random.random()
    self.pmu = random.random()
    self.pm = random.random()
    self.pb = random.random()

    self.rounds = 1000
    self.max_stalls = 100
  
  def fitness(self, X):
    return g(X) + self.alpha * p(X.k)

  def get_individual(self, n):
    probabilities = list(map(lambda i: self.fitness(i), self.pop))
    choices = np.random.choice(len(self.pop), n, p=make_prob_list(probabilities))
    if n > 1:
      return tuple([self.pop[i] for i in choices])
    elif n == 1:
      return self.pop[choices[0]]

  def run(self):
    stalls = 0
    for i in range(self.rounds):
      operation = np.random.choice(3, p=make_prob_list([self.popc, self.puc, self.pmu]))
      if operation == 0:
        Xi, Xj = self.get_individual(2)
        C = Individual(self.series, self.ks, Xi, Xj, crossover='uniform')
      elif operation == 1:
        Xi, Xj = self.get_individual(2)
        C = Individual(self.series, self.ks, Xi, Xj, crossover='one-point')
      else:
        C = self.get_individual(1).mutation(self.pm, self.pb)

      Xmin = min(self.pop, key=lambda i: self.fitness(i))
      replace = self.fitness(C) / (self.fitness(C) + self.fitness(Xmin))
      keep = 1 - replace
      choice = np.random.choice(2, p=[replace, keep])

      if choice == 0:
        Xmin = C

      Xmax = max(self.pop, key=lambda i: self.fitness(i))
      if self.fitness(Xmax) > self.fitness(self.Xbest):
        self.Xbest = Xmax
        stalls = 0
      else:
        stalls += 1

      if stalls > self.max_stalls:
        break

# =============================================================================

class Individual:

  def __init__(self, series, ks, parentA=None, parentB=None, crossover=None):
    self.series = series
    T = len(series)

    if crossover == None:
      bs = random.sample(range(T), ks)
      self.B = [i if i in bs else '*' for i in range(T)]
    elif crossover == 'uniform':
      choices = np.random.choice(2, T, p=[0.5, 0.5])
      self.B = [parentA.B[i] if choices[i] == 0 else parentB.B[i] for i in choices]
    elif crossover == 'one-point':
      point = random.choice(range(T))
      self.B = [parentA.B[i] if i < point else parentB.B[i] for i in range(T)]

    self._make_attr_()

  def __str__(self):
    return '<B:{}, b:{}, k:{}>'.format(self.B, self.b, self.k)

  def _make_attr_(self):
    self.b = [i for i in self.B if i != '*']
    self.k = len(self.b)

  def mutation(self, pm, pb):
    pe = 1-pb
    choices = np.random.choice(3, len(self.B), p=[pm*pb, pm*pe, 1-pm])
    self.B = [i if choices[i] == 0 else '*' if choices[i] == 1 else self.B[i] for i in choices]
    self._make_attr_()

    return self

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
    return (X.b[0] - X.b[X.k-1]) * (max(X.series) - min(X.series))
  else:
    m0 = min(list(map(X.y, range(X.b[j],X.b[j+1]))))
    m1 = max(list(map(X.y, range(X.b[j],X.b[j+1]))))
    return (X.b[j+1] - X.b[j]) * (m1 - m0)