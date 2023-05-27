import sys

def mdc(a,b):
    if b == 0:
        return a
    return mdc(b,a%b)

def mdc_while(a,b):

    while b > 0:
        resto = a % b
        a = b
        b = resto
    
    return a

def mdc_for(a,b):
    menor = min(a,b)
    maior = max(a,b)

    for i in range(menor-1,0,-1):
        if (maior % i) == 0 and (menor % i) == 0:
            return i


if __name__ == '__main__':
    a = int(sys.argv[1])
    b = int(sys.argv[2])
    v_mdc = mdc_for(a,b)
    print(v_mdc)
    v_mdc = mdc_while(a,b)
    print(v_mdc)
