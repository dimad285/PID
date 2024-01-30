import dump
import os
import argparse
import time
import matplotlib.pyplot as plt
import threading
import shutil
import csv

cycl = 100
target = 5000

coefP = 0.00005
coefD = 0.0005
#Ustart = 450

P = [0.15, 0.2, 0.3, 0.5, 0.8, 1, 1.15, 1.2, 1.3, 1.5, 1.8, 2]
U = [1100, 700, 625, 400, 360, 360, 400, 400, 400, 440, 470, 500]
D = []
#coefD = []
#coefP = []
#P = [0.12]
#U = [500]
#L = []

grphFlag = True

inputPath = 'Input/test'
logPath = 'Log'

def cmdStartH5(cycl, thread):
    cmd = f'oopicpro -i {inputPath}{thread}.inp -nox -s {cycl} -h5 -or -d dump/bin/{thread} -sf dump/h5/{thread} -dp {cycl}' 
    return cmd

def cmdStartBin(cycl, thread):
    cmd = f'oopicpro -i {inputPath}{thread}.inp -nox -s {cycl} -sf dump/bin/{thread} -dp {cycl}' 
    return cmd

def cmdH5(cycl, thread):
    cmd = f'oopicpro -i {inputPath}{thread}.inp -nox -s {cycl} -h5 -or -d dump/bin/{thread} -sf dump/h5/{thread} -dp {cycl}' 
    return cmd

def cmdBin(cycl, thread):
    cmd = f'oopicpro -i {inputPath}{thread}.inp -nox -s {cycl} -d dump/bin/{thread} -sf dump/bin/{thread} -dp {cycl}' 
    return cmd


def inpRead(name, *arg):
    u = 0
    p = 0
    d = 0
    with open(name,'r') as inp:
        i = 0
        for lines in inp:
            if i == 7:
                d = float(lines.lstrip('\td = '))
            if i == 8:
                u = float(lines.lstrip('\tU = '))
            if i == 9:
                p = float(lines.lstrip('\tp = '))
                break
            i = i+1

    return u, p, d


def inpChange(name, u, p, d, *arg):
    new = ''
    with open(name,'r') as inp:
        i = 0
        for lines in inp:
            if i == 7:
                new = new + '\td = ' + str(d) + '\n'
            elif i == 8:
                new = new + '\tU = ' + str(u) + '\n'
            elif i == 9:
                new = new + '\tp = ' + str(p) + '\n'
            else:
                new = new + lines
            i = i+1

    with open(name,'w') as newinp:
        newinp.write(new)


def voltCalc(targetN, N2, N1, u, coefP, coefD):
    newU = u + (targetN - N2)*coefP - (N2 - N1)*coefD
    if N2 < targetN/5:
        newU = newU + 500/N2
    #elif N2 > target*2:
    #    newU = newU - N2/1000
    return newU


def logFile(name, *log):
    
    with open(name, 'w') as f:
        for i in range(len(log[0])):
            f.write('\n')
            for j in log:
                f.write(str(j[i])+'\t')

def clearLog(path):
    
    ls = os.listdir(path)
    if 'backup' in ls:
        ls.remove('backup')
        for i in ls:
            shutil.copyfile(f'{path}/{i}', f'{path}/backup/{i}')
            os.remove(f'{path}/{i}')
    else:
        for i in ls:
            print(i)
            os.remove(f'{path}/{i}')


def drawParticles():
    pass



def run(p, uStart, d, iter, thread, failFlag = False, graphFlag = False, stopFlag = False):

    ############################
            #SETUP#
    tStart = time.time()
    print(f'\033[0;34mThread {thread} started {p} Torr\033[0;0m')
    global freeThreads
    logU = []
    logI = []
    logT = []

    if graphFlag == True:
        fig, (ax1, ax2) = plt.subplots(2)
        fig.set_size_inches((12,8))
        ax1.set_xlabel('Iteration')
        ax1.set_ylabel('U')
        ax2.set_xlabel('Iteration')
        ax2.set_ylabel('Ions')
        plt.ion()
    elif graphFlag != False:
            print('Error, wrong graph input')


    inpChange(f'{inputPath}{thread}.inp',uStart, p, d)
    ############################

    u = inpRead(f'{inputPath}{thread}.inp')[0]
    
    os.system(cmdStartBin(cycl,thread))
    time.sleep(0.1)

    os.system(cmdStartH5(1, thread))
    time.sleep(0.1)
    
    n = dump.read(f'dump/h5/{thread}.h5')
    if n == 0:
        logFile(f'{logPath}/{p}.txt', logT, logU, logI)
        print(f'\033[0;31mThread {thread} finished {p} torr with 0 ions\033[0;0m')
        return
    
    logU.append(u); logI.append(n); logT.append(1)
    print(f'Thread {thread}\t{p} Torr Iteration {1}: U = {"%.2f" % u} {n} Ions')

    if graphFlag == True:
        ax1.plot(logT, logU)
        ax2.plot(logT, logI)
        plt.show(block = False)
        plt.pause(0.5)
    elif graphFlag != False:
            print('Error, wrong graph input')


    inpChange(f'{inputPath}{thread}.inp',voltCalc(target,logI[0],logI[0],u,coefP,coefD), p, d)
    

    for i in range(2, iter+1, 1):

        if stopFlag:
            break
        logFile(f'{logPath}/{d}/{p}.txt', logT, logU, logI)
        u = inpRead(f'{inputPath}{thread}.inp')[0]
        
        os.system(cmdBin(cycl,thread))
        time.sleep(0.1)

        os.system(cmdH5(1, thread))
        time.sleep(0.1)
        
        n = dump.read(f'dump/h5/{thread}.h5')
        if n == 0:
            logFile(f'{logPath}/{d}/{p}.txt', logT, logU, logI)
            print(f'\033[0;31mThread {thread} finished {p} torr with 0 ions\033[0;0m')
            if failFlag:
                P.append(p)
                U.append(uStart)
            return
        
        logU.append(u); logI.append(n); logT.append(i)
        
        print(f'Thread {thread}\t{p} Torr Iteration {i}: U = {"%.2f" % u} {n} Ions')

        if graphFlag == True:
            ax1.cla()
            ax2.cla()
            ax1.plot(logT, logU)
            ax2.plot(logT, logI)
            plt.draw()
            plt.pause(0.5)
        elif graphFlag != False:
            print('Error, wrong graph input')

        inpChange(f'{inputPath}{thread}.inp',voltCalc(target,logI[i-1],logI[i-2],u,coefP,coefD), p=p, d=d)

    tEnd = time.time()
    print(f'\033[0;32mThread {thread} finished {p} torr in {tEnd - tStart} seconds\033[0;0m')
    logFile(f'{logPath}/{d}/{p}.txt', logT, logU, logI)
    if graphFlag == True:
        plt.savefig(f'graphs/{p}.png')
        

def run_thread(P:float, U:float, d:float, iter, thread):

    run(P, U, d, iter = iter, thread = thread, graphFlag = False)
    freeThreads.append(thread)


def getTask(path:str):
    
    p = list()
    u = list()
    d = list()
    
    with open(path) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            d.append(float(row[0]))
            p.append(float(row[1]))
            u.append(float(row[2]))      
    
    d_list = set(d)
    for i in d_list:
        os.mkdir(f'{logPath}/{i}')
    
    return d, p, u
    
    
    
if __name__ == '__main__':

    tc = int(input('Number of threads '))
    it = int(input('Number of iterations '))
    subL = int(len(P)/tc)
    threadList = list()

    for i in range(tc):
        shutil.copyfile(f'{inputPath}.inp', f'{inputPath}{i+1}.inp')

    clearLog(logPath)

    d_task, p_task, u_task = getTask('task.csv')
    freeThreads = [i+1 for i in range(tc)]
    n = 1
    tStart = time.time()

    while True:
        if len(p_task)>0:
            if n < tc+1:
                t = threading.Thread(target=run_thread, args=(p_task[0], u_task[0], d_task[0], it, freeThreads[0]))
                p_task.pop(0)
                u_task.pop(0)
                d_task.pop(0)
                t.start()
                freeThreads.pop(0)
        n = threading.active_count()
        time.sleep(1)
        if n == 1:
            print('\033[1;32mDONE\033[0;0m')
            break

    tEnd = time.time()
    print(f'time {tEnd-tStart} seconds')

   

