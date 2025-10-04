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

def sin(x):
    return math.sin(x)

def cos(x):
    return math.cos(x)

def tan(x):
    return math.tan(x)

def log(x):
    if x <= 0:
        raise RuntimeError("log() domain error: input must be positive.")
    return math.log(x)

def exp(x):
    return math.exp(x)

def pow(base, exponent):
    return math.pow(base, exponent)
