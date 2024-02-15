import h5py
import pygame
import struct
import os
import matplotlib.pyplot as plt
import numpy as np

def read(path:str):
    N = 0
    f = h5py.File(path, 'r')
    #print(list(f.keys()))
    l = len(list(f['ions'])) # type: ignore
    for i in range(l):
        N = N + len(list(f['ions'][f'pGrp{i}']['ptcls'])) # type: ignore
    f.close()
    return N

def draw(path:str, part = 'ions', fig = None, th = 1):

    done = False
    BLACK = (  0,   0,   0)
    WHITE = (255, 255, 255)
    size = [1280, 720]
    screen = pygame.display.set_mode(size)

    if fig != None:
        ax = fig.add_axes()

    X = list()
    Y = list()
    XY = list()

    f = h5py.File(path, 'r')
    for i in list(f[part]): # type: ignore
        for j in list(f[part][i]['ptcls']): # type: ignore
            X.append(j[0])
            Y.append(j[1])
            XY.append((int(j[0]/0.128*size[0]), size[1] - int(j[1]/0.064*size[1])))

    while not done:     
        for event in pygame.event.get(): # User did something
            if event.type == pygame.QUIT: # If user clicked close
                done=True # Flag that we are done so we exit this loop
                
        screen.fill(BLACK)
        for i in XY:
            screen.set_at(i,WHITE)

        pygame.draw.rect(screen, WHITE, [0, 0.028/0.064*size[1], 0.128/0.128*size[0], 0.005/0.064*size[1]])
        pygame.display.flip()

    pygame.quit()

def readFull(path:str):
    f = h5py.File(path, 'r')
    print(list(f.keys()))
    print(list(f['ions'])) # type: ignore
    print(f['electrons']['pGrp1']['ptcls'][0][0]) # type: ignore
    l = len(list(f['electrons']['pGrp1']['ptcls'])) # type: ignore
    print(l)
    f.close()


def readBin(path:str):
    with open(path, 'rb') as f:
        #simLen = int.from_bytes(f.read(4).encode(), "little")
        #simTime = struct.unpack('f', f.read(4).encode())
        f.read(8)
        name = int.from_bytes(f.read(4), "little")
        print(name)
        print('name =', f.read(name+1).decode())
        tmp = f.read(4)
        #print(tmp)
        simTime = struct.unpack('<f', tmp)
        print(simTime)
        dims = struct.unpack('<4f', f.read(16))
        print(dims)
        nbound = int.from_bytes(f.read(4), "little")
        print(nbound)
        print(f.read(30))
        
def readCharge(path:str, plotFlag, printFlag, bound:int = 3):
    Q = []
    file_list = os.listdir(path)
    for i in file_list:
        f = h5py.File(f'{path}/{i}', 'r')
        Q.append(list(f['Boundaries'][f'boundary{bound}']['Q'])) # type: ignore
        f.close()
    
    if plotFlag:
        X = np.arange(0, len(Q[0]), 1, dtype=np.int32)
        Y = np.arange(0, len(Q), 1, dtype=np.int32)
        X, Y = np.meshgrid(X, Y)
        Q = np.array(Q)
        fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
        surf = ax.plot_surface(X, Y, Q, cmap='viridis',
                       linewidth=0, antialiased=False)
        plt.show()
    
    if printFlag:
        with open('charge.txt', 'w') as f:
            x = 0
            y = 0
            f.write('x\tt\tQ\n')
            f.write('m\ts\tk\n')
            f.write('coord\ttime\tcharge\n')
            for i in Q:
                y = y + 1
                x = 0
                for j in i:
                    f.write(f'{x}\t{y}\t{j}\n')
                    x = x + 1
    

if __name__ == '__main__':
    readCharge('history', True, False)