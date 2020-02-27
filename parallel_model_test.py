from multiprocessing import Pool
from pprint import pprint
import time

j_values = {(0,): 5,
            (1,): 5,
            (2,): 6}

class Some_Container:

    def __init__(self, processor_pool, exogenous1, exogenous2):
        self.pool = processor_pool
        self.exo1 = exogenous1
        self.exo2 = exogenous2
        self.states = 5000

        self.cache = {(0, state,): 0 for state in range(self.states)}

    def j_func(self, args):
        t, x = args
        values = []
        for y in range(x, self.states):
            values.append(y**2 - self.exo1*y + self.exo2 + self.cache[(t-1, self.states-1-y)])
        return min(values)

    def calc_t(self, t):
        ret = Pool(self.pool).map(self.j_func, list((t, x) for x in range(self.states)))
        for x in range(self.states):
            self.cache[(t, x)] = ret[x]
        #print(ret)


if __name__ == "__main__":
    s = time.time()
    model = Some_Container(8, 10, 100)
    for t in range(1, 10):
        print(t)
        model.calc_t(t)
    e = time.time()
    print("Parallelized time:", e-s)
    s = e

    model = Some_Container(1, 10, 100)
    for t in range(1, 10):
        print(t)
        model.calc_t(t)
    e = time.time()
    print("Serial time:", e - s)





