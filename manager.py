import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import math
import operator

class Player:
    def __init__(self, x, y, z, manager):
        self.x = x
        self.y = y
        self.z = z
##        self.vx = 0
##        self.vz = 0
##        self.terminal_v = 1
##        self.terminal_v_sprint = 2
##        self.vy = 0
##        self.ay = 1
##        self.terminal_v_y = -5
        self.manager = manager
    def update(self,keypress,ticks):
##        const=100
##        self.x += self.vx*(ticks/const)
##        self.z += self.vz*(ticks/const)
##        self.y += self.vy*(ticks/const)
##        if self.manager.blocks[int(self.x)][int(self.y)][int(self.z)].blockid == 0:
##            self.vy += self.ay*(ticks/const)
##            if self.vy > self.terminal_v_y:
##                self.vy = sellf.terminal_v_y
##        if self.manager.blocks[int(self.x)][int(self.y-1)][int(self.z)].blockid > 0:
##            self.y+=1
        if keypress[pygame.K_w]:
            glTranslatef(0,0,0.007*ticks)
        if keypress[pygame.K_s]:
            glTranslatef(0,0,-0.007*ticks)
        if keypress[pygame.K_d]:
            glTranslatef(-0.007*ticks,0,0)
        if keypress[pygame.K_a]:
            glTranslatef(0.007*ticks,0,0)
        if keypress[pygame.K_SPACE]: ##fix this to jump
            glTranslatef(0,-0.007*ticks,0)
        if keypress[pygame.K_LSHIFT]:
            glTranslatef(0,0.007*ticks,0)
        
            
        
    
        

class Block:
    
    def __init__(self, x,y,z, blockid, man, strength=1):
        self.x, self.y, self.z = x, y, z
        self.blockid = blockid
        self.manager = man
        self.face_coords=[
            [
                (0,0,0),
                (0,0,1),
                (0,1,1),
                (0,1,0),
             ],
            [
                (1,0,1),
                (1,0,0),
                (1,1,0),
                (1,1,1),
             ],
            [
                (0,0,0), #not sure about rotation
                (1,0,0),
                (1,0,1),
                (0,0,1),
             ],
            [
                (1,1,1), #not sure about rotation
                (1,1,0),
                (0,1,0),
                (0,1,1),
             ],
            [
                (1,0,0),
                (0,0,0),
                (0,1,0),
                (1,1,0),
             ],
            [
                (0,0,1),
                (1,0,1),
                (1,1,1),
                (0,1,1),
             ],
            ]
        self.lookup_coords=[
            (-1,0,0),
            (1,0,0),
            (0,-1,0),
            (0,1,0),
            (0,0,-1),
            (0,0,1),
            ]
        self.strength = strength

    def render_face(self, i):
        glTexCoord2f(0, 0)
        glVertex3f(self.x+self.face_coords[i][0][0], self.y+self.face_coords[i][0][1], self.z+self.face_coords[i][0][2])
        glTexCoord2f(1, 0)
        glVertex3f(self.x+self.face_coords[i][1][0], self.y+self.face_coords[i][1][1], self.z+self.face_coords[i][1][2])
        glTexCoord2f(1, 1)
        glVertex3f(self.x+self.face_coords[i][2][0], self.y+self.face_coords[i][2][1], self.z+self.face_coords[i][2][2])
        glTexCoord2f(0, 1)
        glVertex3f(self.x+self.face_coords[i][3][0], self.y+self.face_coords[i][3][1], self.z+self.face_coords[i][3][2])

    def draw(self):
        if self.blockid > 0: #so not air
            glBegin(GL_QUADS)
            for i in range(6):
                if self.manager.textures[self.blockid][i] != self.manager.last: ## TODO make more friendly to newer drawing system
                    glEnd()
                    self.manager.select_texture(self.blockid, i)
                    glBegin(GL_QUADS)
                self.manager.last = self.manager.textures[self.blockid][i]
                self.render_face(i)
            glEnd()

    def draw_face(self, f):
        if self.blockid > 0: #so not air
            if self.manager.textures[self.blockid][f] != self.manager.last: ## TODO make more friendly to newer drawing system
                glEnd()
                self.manager.select_texture(self.blockid, f)
                glBegin(GL_QUADS)
            self.manager.last = self.manager.textures[self.blockid][f]
            self.render_face(f)
            
    def get_sides_to_draw(self):
        sides=[]
        if self.blockid != 0: #so not air; if air then will never render anything
            for i in range(6):
                x = self.x + self.lookup_coords[i][0]
                y = self.y + self.lookup_coords[i][1]
                z = self.z + self.lookup_coords[i][2]
                try: # to get around if there is no block there
                    if self.manager.blocks[x][y][z].blockid == 0:
                        sides.append((self.x, self.y, self.z, i))
                except:
                    pass
        return sides
    def break_block(self):
        self.blockid = 0
        self.call_block_update()
        
    def place_block(self,newblockid): # only return true if block was air and so placed
        if self.blockid == 0:
            self.blockid = newblockid
            self.call_block_update()
            return True
        else:
            return False
        
    def call_block_update(self):
        translated_coords = []
        for x, y, z in self.lookup_coords:
            x += self.x
            y += self.y
            z += self.z
            translated_coords.append((x, y, z))
        self.manager.remove_draw_list_coords(translated_coords)
        self.manager.add_draw_list_coords(translated_coords)
            


class GameManager: #manages rendering and storing all game information
    def __init__(self, fullscreen, ScreenWidth, ScreenHeight, starty, mouseSpeed, strafeSpeed, forwardSpeed, backSpeed):
        self.player = Player(0,starty,0, self)
        pygame.init()
        self.display = (ScreenWidth, ScreenHeight)
        if fullscreen:
            self.screen = pygame.display.set_mode((ScreenWidth, ScreenHeight), DOUBLEBUF | OPENGL | pygame.OPENGLBLIT | pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((ScreenWidth, ScreenHeight), DOUBLEBUF | OPENGL | pygame.OPENGLBLIT)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (ScreenWidth/ScreenHeight), 0.1, 100.0)

        glMatrixMode(GL_MODELVIEW)
        gluLookAt(self.player.x, self.player.y, self.player.y, self.player.x+1, self.player.y, self.player.x, 0, 1, 0)
        self.viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
        glLoadIdentity()

        self.blocks = {}

        self.mouseSpeed = mouseSpeed
        self.strafeSpeed = strafeSpeed
        self.backSpeed = backSpeed
        self.forwardSpeed = forwardSpeed

        glEnable(GL_TEXTURE_2D)#from load textures

        self.last="" # used by the cube renderer to know what the last drawn texture was to save on the effort of reloading an already loaded texture (takes time!)
        
        self.sides_to_draw = []
        
##        clone minecraft block ids: //different to actual blockids
##            0   air
##            1   bedrock
##            2   stone
##            3   dirt
##            4   grass block
##            5   cobblestone
##            6   log
##            7   planks
##            8   leves
##            9   coal ore
##            10  iron ore
##            11  gold ore
##            12  diamond ore

        self.textures = [
            None, #air
            ['bedrock.png','bedrock.png','bedrock.png','bedrock.png','bedrock.png','bedrock.png',],
            ['stone.png', 'stone.png', 'stone.png', 'stone.png', 'stone.png', 'stone.png'],
            ['dirt.png','dirt.png','dirt.png','dirt.png','dirt.png','dirt.png',],
            ['grass_side.png','grass_side.png','dirt.png','grass_top.png','grass_side.png','grass_side.png',],
            ['cobblestone.png','cobblestone.png','cobblestone.png','cobblestone.png','cobblestone.png','cobblestone.png',],
            ['log_oak.png','log_oak.png','log_oak_top.png','log_oak_top.png','log_oak.png','log_oak.png',],
            ['planks_oak.png','planks_oak.png','planks_oak.png','planks_oak.png','planks_oak.png','planks_oak.png',],
            ['leaves_oak.png','leaves_oak.png','leaves_oak.png','leaves_oak.png','leaves_oak.png','leaves_oak.png',],
            ['coal_ore.png','coal_ore.png','coal_ore.png','coal_ore.png','coal_ore.png','coal_ore.png',],
            ['iron_ore.png','iron_ore.png','iron_ore.png','iron_ore.png','iron_ore.png','iron_ore.png',],
            ['gold_ore.png','gold_ore.png','gold_ore.png','gold_ore.png','gold_ore.png','gold_ore.png',],
            ['diamond_ore.png','diamond_ore.png','diamond_ore.png','diamond_ore.png','diamond_ore.png','diamond_ore.png',],
            #['grass.png',],
            
            ]
        
        texid = 1
        glGenTextures((len(self.textures)-1)*6) #for each texture to be loaded, -1 to account for air
        for tex_group in self.textures[1:]:
            for tex in tex_group:
                textureSurface = pygame.image.load("1.6 textures/" + tex)
                textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
                width = textureSurface.get_width()
                height = textureSurface.get_height()
                glBindTexture(GL_TEXTURE_2D, texid)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height,
                             0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
                texid+=1

        #for rendering outline
        self.verticies = (
            (1, -1, -1),
            (1, 1, -1),
            (-1, 1, -1),
            (-1, -1, -1),
            (1, -1, 1),
            (1, 1, 1),
            (-1, -1, 1),
            (-1, 1, 1)
            )

        self.edges = (
            (0,1),
            (0,3),
            (0,4),
            (2,1),
            (2,3),
            (2,7),
            (6,3),
            (6,4),
            (6,7),
            (5,1),
            (5,4),
            (5,7)
            )


    def select_texture(self, blockid, faceid):
        texid = (blockid-1)*6
        texid += faceid + 1
        glBindTexture(GL_TEXTURE_2D, texid)
        #ONLY IF NOT WORKING WITHOUT SHALL ENABLE; CAUSES LAG
##        self.loadTexture("1.6 textures/" + self.textures[blockid][faceid])

    def loadTexture(self, filepath): #horrible legacy code for compatability with broken computers (CL6,CL3)
        textureSurface = pygame.image.load(filepath)
        textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
        width = textureSurface.get_width()
        height = textureSurface.get_height()

        
        texid = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, texid)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height,
                     0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        return texid
   
    def set_blocks(self, blocks, reset=False):
        if reset:
            self.blocks={}
        for data in blocks:
            x, y, z, blockid = data
            try:
                bool(self.blocks[x])
            except:
                self.blocks[x] = {}
            try:
                bool(self.blocks[x][y])
            except:
                self.blocks[x][y] = {}
            self.blocks[x][y][z]=Block(x, y, z, blockid, self)
        self.update_draw_list()
            
    def update_draw_list(self):
        self.sides_to_draw = []
        for x, xitems in self.blocks.items():
            for y, yitems in xitems.items():
                for z, zitem in yitems.items():
                    self.sides_to_draw += zitem.get_sides_to_draw()
        self.sides_to_draw.sort(key=lambda side:self.textures[self.blocks[side[0]][side[1]][side[2]].blockid])#TODO when placing and breakign blocks: does this actually make it any more efficient??
        
    def remove_draw_list_coords(self, coords):
        for x, y, z, f in self.sides_to_draw: # TODO make more efficient?
            for X, Y, Z in coords:
                if x == X:
                    if y == Y:
                        if z == Z:
                            self.sides_to_draw.remove((x, y, z, f))
                            
    def add_draw_list_coords(self, coords):
        for x,y,z in coords:
            self.sides_to_draw += self.blocks[x][y][z].get_sides_to_draw()
    
    def mainloop(self):
        # init mouse movement and center mouse on screen
        self.displayCenter = [self.screen.get_size()[i] // 2 for i in range(2)]
        self.mouseMove = [0, 0]
        pygame.mouse.set_pos(self.displayCenter)

        self.up_down_angle = 0.0
        self.paused = False
        self.run = True
        self.controller = True

        clock = pygame.time.Clock()
        pygame.joystick.init()

        highlighted = (0,32,0)

##        
##        for y in range(64):
##            for x in range(12):
##                for z in range(12):
##                    if self.blocks[x][y][z].blockid == 2:
##                        self.blocks[x][y][z] = Block(x, y, z, 0, self)
##        self.update_draw_list()

        
        while self.run:
            ticks=clock.get_time()
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        self.run = False
                    if event.key == pygame.K_PAUSE or event.key == pygame.K_p:
                        self.paused = not self.paused
                        pygame.mouse.set_pos(self.displayCenter)
                if not self.paused:
                    if not self.controller:
                        if event.type == pygame.MOUSEMOTION:
                            self.mouseMove = [event.pos[i] - self.displayCenter[i] for i in range(2)]
                        pygame.mouse.set_pos(self.displayCenter)
                    else:
                        try:
                            j = pygame.joystick.Joystick(0)
                            j.init()
                            tx = j.get_axis(4)
                            ty = j.get_axis(3)
                            self.mouseMove = [tx*2*ticks, ty*2*ticks]
                        except:
                            self.controller=False # if contoller not found then exit from controller mode, back to keyboard

            if not self.paused:
                # get keys
                keypress = pygame.key.get_pressed()

                # init model view matrix
                glLoadIdentity()

                # apply the look up and down
                self.up_down_angle += self.mouseMove[1]*self.mouseSpeed
                glRotatef(self.up_down_angle, 1, 0, 0)

                # init the view matrix
                glPushMatrix()
                glLoadIdentity()

                # apply the movment
                if not self.controller:
                    self.player.update(keypress,ticks) #will only work for keyboard and mouse atm
                    
                else:
                    j = pygame.joystick.Joystick(0)
                    j.init()
                    tx = j.get_axis(0)
                    ty = j.get_axis(1)
                    glTranslatef(-tx*ticks*0.01,0,0) # this is ony line because x scales in both directions when usign controler input (value as -1 to 1)
                    glTranslatef(0,0,-ty*ticks*0.01)
                    if j.get_button(4): ##fix this to jump 
                        glTranslatef(0,-0.007*ticks,0)
                    if j.get_button(5):
                        glTranslatef(0,0.007*ticks,0)
                    if j.get_button(6) and j.get_button(7):
                        self.run=False

                # apply the left and right rotation
                glRotatef(self.mouseMove[0]*self.mouseSpeed, 0, 1, 0)

                # multiply the current matrix by the get the new view matrix and store the final vie matrix 
                glMultMatrixf(self.viewMatrix)
                self.viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)

                # apply view matrix
                glPopMatrix()
                glMultMatrixf(self.viewMatrix)

                glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

                glPushMatrix()

                #TODO get coords of block looking at


                
                #render all faces in sides_to_draw list
                glBegin(GL_QUADS)
                for  x, y, z, f in self.sides_to_draw:
                    self.blocks[x][y][z].draw_face(f)
                glEnd()
                #render highlighted block's outline in black
##                glBegin(GL_LINES)
##                glColor3f(0.0, 0.0, 0.0)
##                for edge in self.edges:
##                    for vertex in edge:
##                        glVertex3fv(tuple(map(operator.add,self.verticies[vertex],highlighted))) # draw cube translated to highglighted block
##                        #TODO test if actually woirks
##                glEnd()
                
                
                glPopMatrix()
                glFlush()
                pygame.display.flip()
        pygame.quit()



