import h5py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pygame



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
    size = [1920, 1000]
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

    #print(XY)

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
    #plt.scatter(X,Y,th)
    #plt.plot([0, 0.128, 0.128, 0, 0], [0.028, 0.028, 0.033, 0.033, 0.028],'r')
    #plt.plot([0.02, 0.02, 0.045, 0.045, 0.02], [0, 0.006, 0.006, 0, 0],'r')
    #plt.plot([0.108, 0.108, 0.083, 0.083, 0.108], [0, 0.006, 0.006, 0, 0],'r')
    #plt.show()


def readFull(path:str):
    f = h5py.File(path, 'r')
    print(list(f.keys()))
    print(list(f['ions'])) # type: ignore
    print(f['electrons']['pGrp1']['ptcls'][0][0]) # type: ignore
    l = len(list(f['electrons']['pGrp1']['ptcls'])) # type: ignore
    print(l)
    f.close()


if __name__ == 'main':
    pygame.init()
    #readFull('dump/h5/1.h5')
    draw('dump/h5/1.h5',part = 'ions')
