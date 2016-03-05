import random
import math

def isPrime(n):
    if n == 2:
        return True
    if n%2!=0:
        for i in range(3,math.ceil(math.sqrt(n))+1,2):
            if n % i == 0:
                return False
        return True
    return False
x = 4
while not isPrime(x):
    x = random.randint(2**4,2**16)

print(x)
print()
y = 4
while not isPrime(y):
    y = random.randint(2**(len(str(x))-1), 2**len(str(x)))

semi = x*y
print(semi,len(str(semi)))
