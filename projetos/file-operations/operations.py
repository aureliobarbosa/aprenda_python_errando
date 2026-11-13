# simple writing 
filename = 'blablebli.txt'
file = open(filename,'w')
print('bla\nble\nbli', file=file)
file.close()



# simple reading
filename = 'numbers.dat'
file = open(filename,'r')
numbers = []
for line in file:
    numbers.append(int(line))

print(numbers)
file.close()

