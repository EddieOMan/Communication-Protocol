def eGCD(e, n):
    x, y, a, b = 1,0,0,1
    count = 0
    while n and count < 10000:
        q = e//n

        x, y = y, x - q*y
        #a, b = b, a - q*b

        e, n = n, e - q*n
        count+=1

    return(e,x,a)


for x in range(1,100,2):
    if eGCD(x, 336)[0]==1:
        if eGCD(x,336)[1] == abs(eGCD(x,336)[1]):
            print(x, eGCD(x,336)[1])
