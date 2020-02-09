import manager
import random
from win32api import GetSystemMetrics
import random
import noise

fullscreen = True
seed = 0



blocks = []
X=20
Z=X
def layer(blockid,y):
    for x in range(-X,X):
        for z in range(-Z,Z):
            blocks.append((x, y, z, blockid))

layer(1,0)
for n in range(1,64):
    layer(0,n)


shape = (2*X,2*Z)
scale = 100.0
octaves = 6
persistence = 0.5
lacunarity = 2.0

def get_perlin(x, z):
    return noise.pnoise2(x/scale, z/scale, octaves = octaves, persistence = persistence, lacunarity = lacunarity, repeatx = 2*X, repeaty = 2*Z, base=seed)

def tree(x, y, z):
    h=random.randint(1,4)
    for t in range(h):
        blocks.append((x, y+t, z, 6))
    for t in range(h,h+2):
        blocks.append((x, y+t, z, 6))
        for z_ in [-2,-1,1,2]:
            for x_ in range(-2,3):
                if not( abs(x_) == 2 and abs(z_) == 2):
                    blocks.append((x+x_, y+t, z+z_, 8))
        blocks.append((x+1, y+t, z, 8))
        blocks.append((x+2, y+t, z, 8))
        blocks.append((x-1, y+t, z, 8))
        blocks.append((x-2, y+t, z, 8))
    for t in range(h+2,h+4):
        for z_ in range(-1,2):
                for x_ in range(-1,2):
                    if not(abs(x_) == 1 and abs(z_) == 1):
                        blocks.append((x+x_, y+t, z+z_, 8))

#create terrian
#the terrain is geneated in the whole y per (x,z) so the ore is not in veins, but it will generate the same no matter what generates when
for x in range(-X,X):
    for z in range(-Z,Z):
        y = get_perlin(x, z)
        y *= 25
        y = int(y) + 24
        random.seed(int(get_perlin(x,z)*1000000))
        if random.randint(0,200) == 0:
            tree(x, y+1, z)
            blocks.append((x,y,z,3))
        else:
            blocks.append((x,y,z,4))
        for y_ in range(y-4,y):
            blocks.append((x,y_,z,3))
        for y_ in range(1,y-4):
            if random.randint(0,200) == 0: #coal
                blocks.append((x,y_,z,9))
            elif random.randint(0,200) == 0 and y_ < 24:#iron
                blocks.append((x,y_,z,10))
            elif random.randint(0,200) == 0 and y_ < 16:#gold
                blocks.append((x,y_,z,11))
            elif random.randint(0,200) == 0 and y_ < 8:#diamond
                blocks.append((x,y_,z,12))
            else:
                blocks.append((x,y_,z,2))


y = get_perlin(0, 0)
y *= 25
y = int(y) + 24 + 1
if fullscreen:
    r = manager.GameManager(1, GetSystemMetrics(0),GetSystemMetrics(1), y, 0.1, 0.007, 0.007, 0.007)
else:
    r = manager.GameManager(0, 400,300, y, 0.1, 0.007, 0.007, 0.007)

r.set_blocks(blocks)
r.mainloop()

