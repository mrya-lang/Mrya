import math
import random

def absfn(x):
    return abs(x)

def roundfn(x):
    return round(x)

def up(x):
    return math.ceil(x)

def down(x):
    return math.floor(x)

def root(x):
    if x < 0: 
        raise RuntimeError("sqrt() domain error: input must be noon-negative.")
    return math.sqrt(x)

def randomf():
    return random.random()

def randint(low, high):
    return random.randint(int(low), int(high))
