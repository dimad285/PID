import os
import statistics
import matplotlib.pyplot as plt
import math

dir = 'Log'
ls = os.listdir(dir)
ls.remove('backup')
r = 5
#print(ls)
p = list()
it = list()
U = list()
n = list()

inp = input('choose preashure   ')
if inp == '/':
    quit()
elif inp == 'all':
    for i in ls:
        p.append(i.rstrip('.txt'))
    inp = '/'

while inp != '/':
    p.append(inp)
    inp = input('choose preashure   ')

for i in range(len(p)):

    it.append([])
    U.append([])
    n.append([])

    with open(f'{dir}/{p[i]}.txt', 'r') as f:
        f.readline()
        while(True):
            l = f.readline()
            if l == '':
                break
            L = l.split('\t') 
            L = L[:3]
            
            L = [float(i) for i in L]
            it[i].append(L[0])
            U[i].append(L[1])
            n[i].append(L[2])


f, (ax1, ax2) = plt.subplots(2)
for i in range(len(p)):
    ax1.plot(it[i], U[i])
    ax1.grid(True, 'both', axis = 'both')
    ax2.plot(it[i], n[i])
    ax2.grid(True, 'both', axis = 'both')

ax1.legend(p)
ax2.legend(p)

plt.show() 

