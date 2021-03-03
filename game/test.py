import perlin
import random
import matplotlib.pyplot as plt

def show_perlin_noise():
    noise=perlin.Perlin(10)

    time=[i for i in range(200)]
    values=[noise.valueAt(i) for i in time]

    multiplied_list = [(element * 100) + 450 for element in values]

    plt.title("Perlin Noise")
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.plot(time, multiplied_list)
    plt.show()

show_perlin_noise()
