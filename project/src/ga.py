import numpy as np

# =============================================================================

class GeneticAlgorithm:

  def __init__(self, pop_size, sol_size):
    self.pop = [Individual(sol_size)] * pop_size
    self.alpha = np.random.rand()
  
  def fitness(X):
    return g(X) + self.alpha * p(X.k)

  def next_gen():


# =============================================================================

class Individual:

  def __init__(self, size):
    self.series = readcsv('../data/series.csv')
    self.k = 0
    self.B = list()

  def y(self, i):
    return self.series[i]

# =============================================================================

def g(X):
  return (area(X) - [area(X, j) for j in range(0, X.k-1)]) / area(X)

def p(k):
  return 1/np.sqrt(k)

def area(X, j=None):
  if j == None:
    return (X.B[0] - X.B[len(X.B)-1]) * (max(X.series) - min(X.series))
  else:
    m0 = min(list(map(X.y, range(X.B[j],X.B[j+1]))))
    m1 = max(list(map(X.y, range(X.B[j],X.B[j+1]))))
    return (X.B[j+1] - X.B[j]) * (m1 - m0)