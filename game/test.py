
import math

points = [[-20,0]]
for x in range(200):
    points.append([(x-1)*20,20*math.sin(x/30)+470])



print(points[-1][1])
