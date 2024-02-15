import dump
import os
import time
import threading
import shutil
import csv
import math

# Constants
CYCLE = 100 #number of pic simulation cycles per PID iteration
TARGET_IONS = 5000  #target number of ions
COEF_P = 0.00005  # Proportional coefficient in PID controller
COEF_D = 0.0005  # Differential coefficient in PID controller

INPUT_PATH = 'Input/test'
LOG_PATH = 'Log'
DUMP_PATH = 'Input/dump'
DUMP_HISTORY_PATH = 'history'

DUMP_ITER = 1   #number of iterations between history dump; 0 - no dump

TIME_MULT = 1   #time multiplier
ECYCLE = 1000   #number of electron subcycles per oopicpro cycle
BASE_TIME = 1.0e-12  #base time for oopicpro


# Function to run oopicpro with h5 dump in cmd mode
def cmdH5(cycle: int, thread: int, path: str, dump: str) -> str:
    return f'oopicpro -i {path}{thread}.inp -nox -s {cycle} -h5 -or -d {dump}/bin/{thread} -sf {dump}/h5/{thread} -dp {cycle}' 
# Function to run oopicpro with bin dump in cmd mode
def cmdBin(cycle: int, thread: int, path: str, dump: str) -> str:
    return f'oopicpro -i {path}{thread}.inp -nox -s {cycle} -d {dump}/bin/{thread} -sf {dump}/bin/{thread} -dp {cycle}' 
# Function to start simulation with binary dump
def cmdStartBin(thread: int, path: str, dump: str) -> str:
    return f'oopicpro -i {path}{thread}.inp -nox -s 1 -sf {dump}/bin/{thread} -dp 1'

def cmdDump(thread: int, path: str, dump: str) -> str:
    return f'oopicpro -i {path}{thread}.inp -nox -s 1 -h5 -or -d Input/dump/bin/{thread} -sf {dump} -dp 1'

# Function to run the simulation
def cmdRun(cycle: int, thread: int, path: str, dump: str):
    os.system(cmdBin(cycle, thread, path, dump))
    time.sleep(0.1)
    os.system(cmdH5(1, thread, path, dump))
    time.sleep(0.1)
    
def modelInit(name:str):   
    global TIME_MULT
    global BASE_TIME
    global ECYCLE      
    with open(name, 'r') as inp:
        lines = inp.readlines()
        TIME_MULT = float(lines[26].strip('\ttime_mult = '))
        BASE_TIME = float(lines[27].strip('\tbaseTime = '))
        ECYCLE = int(lines[32].strip('\teCycle = '))

# Function to read input file
def inpRead(name: str) -> tuple:
    with open(name, 'r') as inp:
        lines = inp.readlines()
        d = float(lines[7].strip('\td = '))
        u = float(lines[8].strip('\tU = '))
        p = float(lines[9].strip('\tp = '))
    return u, p, d

# Function to change input file
def inpChange(name: str, u: float, p: float, d: float):
    with open(name, 'r') as inp:
        lines = inp.readlines()
    lines[7] = '\td = ' + str(d) + '\n'
    lines[8] = '\tU = ' + str(u) + '\n'
    lines[9] = '\tp = ' + str(p) + '\n'
    with open(name, 'w') as newinp:
        newinp.writelines(lines)

# Function to calculate new voltage using PID algorithm
def voltCalc(targetN, N2, N1, u):
    return u + (targetN - N2) * COEF_P - (N2 - N1) * COEF_D

# Function to write log to file
def logFile(name: str, *log):
    with open(name, 'w') as f:
        for i in range(len(log[0])):
            f.write('\t'.join(str(j[i]) for j in log) + '\n')

# Function to clear log folder
def clearLog(path: str):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        else:  # Assume it's a folder
            shutil.rmtree(item_path)
            
def dumpHistory(thread: int, path: str, dump: str):
    '''dumps history of a simulation in a form of binary dump file'''
    os.system(cmdDump(thread, path, dump))
      
def getTask(path:str):
    '''reads csv task file and returns lists of P, U, D'''  
    p = list()
    u = list()
    d = list()
    with open(path) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader)  # Skip header line in csv
        for row in reader:
            d.append(float(row[0]))
            p.append(float(row[1]))
            u.append(float(row[2]))      
    
    d_list = set(d)
    for i in d_list:
        os.mkdir(f'{LOG_PATH}/{i}')
    
    return d, p, u

def historyFolder(path: str, distance: list, pressure: list[list]):
    
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        else:  # Assume it's a folder
            shutil.rmtree(item_path)
            
    for dist, pres in zip(distance, pressure):
        dist_path = os.path.join(path, f'{dist}')
        if not os.path.exists(dist_path):
            os.makedirs(dist_path)
        
        pres_path = os.path.join(dist_path, f'{pres}')
        if not os.path.exists(pres_path):
            os.makedirs(pres_path)    
    
def copyInputFiles(tc: int, input_path: str):
    for i in range(tc):
        shutil.copyfile(f'{input_path}.inp', f'{input_path}{i+1}.inp')
        
        
def run(p:float, uStart:float, d:float, iter:int, thread:int, inter_dump: int):
    '''runs oopicpro with PID controler'''
    
    ############################
            #SETUP#
    tStart = time.time()
    print(f'\033[0;34mThread {thread} started {p} Torr\033[0;0m')
    logU = [uStart]
    logI = [TARGET_IONS]
    logT = [-1]
    k = 0
    inpChange(f'{INPUT_PATH}{thread}.inp',uStart, p, d)
    os.system(cmdStartBin(thread, INPUT_PATH, DUMP_PATH))
    time.sleep(0.1)
    ############################   

    for i in range(iter):   #main loop
        
        cmdRun(CYCLE, thread, INPUT_PATH, DUMP_PATH)
        n = dump.read(f'{DUMP_PATH}/h5/{thread}.h5')
        u = inpRead(f'{INPUT_PATH}{thread}.inp')[0]
        logU.append(u); logI.append(n); logT.append(i)
        
        if n == 0:
            logFile(f'{LOG_PATH}/{d}/{p}.txt', logT, logU, logI)
            print(f'\033[0;31mThread {thread} finished {p} torr with 0 ions\033[0;0m')
            return
        
        inpChange(f'{INPUT_PATH}{thread}.inp',voltCalc(TARGET_IONS,logI[i-1],logI[i-2],u), p, d)
        logFile(f'{LOG_PATH}/{d}/{p}.txt', logT, logU, logI)
        print(f'Thread {thread}\t{p} Torr Iteration {i}: U = {"%.2f" % u} {n} Ions')
        
        
        if inter_dump != 0 and (k+1) == inter_dump:
            name:str = DUMP_HISTORY_PATH + f'/{d}_{p}_{i*ECYCLE*BASE_TIME*TIME_MULT/math.sqrt(p)}'
            dumpHistory(thread, INPUT_PATH, name)
            k = 0
        
    tEnd = time.time()
    print(f'\033[0;32mThread {thread} finished {p} torr in {tEnd - tStart} seconds\033[0;0m')
    logFile(f'{LOG_PATH}/{d}/{p}.txt', logT, logU, logI)
        

def runThread(P:float, U:float, d:float, iter, thread, inter_dump):
    '''runs thread with PID controler''' 
    run(P, U, d, iter, thread, inter_dump)
    freeThreads.append(thread)
    
    
if __name__ == '__main__':
    # SETUP
    tc = int(input('Number of threads '))   #number of threads
    it = int(input('Number of iterations '))   #number of iterations
    freeThreads = [i+1 for i in range(tc)]    #list of free threads
    n = 1   #number of active threads
    clearLog(LOG_PATH)    #clears log folder
    clearLog(DUMP_HISTORY_PATH)    #clears history folder
    modelInit('Input/test.inp') #reads model parameters
    copyInputFiles(tc, INPUT_PATH) #copies input file for each thread    
    d_task, p_task, u_task = getTask('task.csv')    #reads task file
    
    # MAIN LOOP
    tStart = time.time()    #time counter
    while True: #main loop
        if len(p_task)>0:
            if n < tc+1:
                t = threading.Thread(target=runThread, args=(p_task[0], u_task[0], d_task[0], it, freeThreads[0], DUMP_ITER)) #creates new thread
                t.start()    #starts thread
                p_task.pop(0)    #deletes first element from list
                u_task.pop(0)    #deletes first element from list
                d_task.pop(0)    #deletes first element from list
                freeThreads.pop(0)    #deletes first element from list
        n = threading.active_count()    #number of active threads
        time.sleep(1)    #waits for 1 second who knows why
        if n == 1:    #if there is only main thread
            print('\033[1;32mDONE\033[0;0m')    #prints DONE
            break    #breaks the loop

    tEnd = time.time()    #time counter
    print(f'time {tEnd-tStart} seconds')    #prints time

   

