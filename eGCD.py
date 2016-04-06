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

