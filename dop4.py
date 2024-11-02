import main as m
import dop1 as d1
import dop2 as d2
import time


t = time.time()
for _ in range(100):
    m.run()
print(time.time() - t)
t = time.time()
for _ in range(100):
    d1.run()
print(time.time() - t)
t = time.time()
for _ in range(100):
    d2.run()
print(time.time() - t)