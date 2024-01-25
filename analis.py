import os
import statistics
import matplotlib.pyplot as plt
import math

dir = 'Log'
ls = os.listdir(dir)
ls.remove('backup')
#print(ls)
u_mean = list()
u_er = list()
u_last = list()
p = list()

r = 5

for i in ls:
    time = list()
    U = list()
    I = list()

    with open(f'{dir}/{i}', 'r') as f:
        f.readline()
        while(True):
            l = f.readline()
            L = l.split('\t') 
            L = L[:3]
            if l == '':
                break
            L = [float(i) for i in L]
            time.append(L[0])
            U.append(L[1])
            I.append(L[2])
            
    MN = statistics.mean(U[len(U)-r:])
    u_last.append(U[-1])
    u_mean.append(MN)

    SD = 0
    for j in U[len(U)-r:]:
        SD += (j - MN)**2
    SD = math.sqrt(SD/(r-1))
    u_er.append(SD)
    p.append(float(i.rstrip('.txt')))


for j in range(len(p)):  
    for i in range(len(p)- j -1):
        if p[i+1]>p[i]:
            continue
        else:
            tmpP = p[i]
            tmpU = u_mean[i]
            tmpErr = u_er[i]

            p[i] = p[i+1]
            p[i+1] = tmpP

            u_mean[i] = u_mean[i+1]
            u_mean[i+1] = tmpU

            u_er[i] = u_er[i+1]
            u_er[i+1] = tmpErr

#print(u_mean)
#print(u_er)
#print(p)

with open('line.txt', 'w') as f:
    for i in range(len(u_mean)):
        f.write(f'{p[i]}\t{u_mean[i]}\n')

f, ax = plt.subplots()
#ax.errorbar(p,u_mean, yerr=u_er)
ax.plot(p, u_mean)
#ax.plot(p, u_last)
#ax.legend(["mean", "last"])
#ax.set_ylim(250, 1000)
#ax.set_xlim(0.01, 10)
ax.set_yscale('log')
ax.set_xscale('log')
ax.grid(True, 'both', axis = 'both')
plt.show() 

