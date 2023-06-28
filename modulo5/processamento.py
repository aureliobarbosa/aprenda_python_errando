def processa_estados_leo(estados):
    n = len(estados)
    for i in range(n-1,-1,-1):
        print(i, estados[i])
        del estados[i]

    return len(estados)

def processa_estados_marco(estados):
    n = len(estados)    
    for i in range(n):
        estado = estados.pop()
        print(estado)

    return len(estados)

estados = ['GO','DF','MT','PR','PA']
processa_estados_leo(estados)

print()
estados = ['GO','DF','MT','PR','PA']
processa_estados_marco(estados)