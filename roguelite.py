import libtcodpy as libtcod
import textwrap
 
#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
 
#size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 43

#variables for GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1
 
FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = False  #light walls or not
TORCH_RADIUS = 10
 
LIMIT_FPS = 20  #20 frames-per-second maximum
 
 
color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)
 
 
class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        #all tiles start unexplored
        self.explored = False
        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

        
#class Combat:
    #a class containing logic necessary to run during the combat state
        
class Script:
    def __init__(self, name=None, data=None, scripts=None):
        self.name = name
        self.data = data
        self.scripts = scripts
        
    def __str__(self):
        return str(self.name)        

    def getChoice(self):
        self.choice = raw_input("=>")
        if not self.scripts.keys():
            return False
        if self.choice in self.scripts.keys():
            return True
        return False

    def run(self):
        while True:
            print
            print(self.data)
            print
            if self.scripts:
                for scr in self.scripts.values():
                    print(scr.name)
            if not self.getChoice():
                break
            if self.scripts:
                self = self.scripts.get(self.choice)
        

#class Encounter:
    #encounter has to be just data
    #
    #encounter has a collection of objects which can be carried between landmarks to make the text events more variable
    #
    #encounter will likely need a subset of it's objects to be defined as combatants, since these objects will trigger the combat state
    
class Object:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.fadedColor = color - libtcod.dark_gray
        self.lastX = self.x
        self.lastY = self.y
 
    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked
        if not map[self.x + dx][self.y + dy].blocked:
            self.x += dx
            self.y += dy
 
    def draw(self):
        #only show if it's visible to the player
        #if libtcod.map_is_in_fov(fov_map, self.x, self.y):
        #for y in range(MAP_HEIGHT):
            #for x in range(MAP_WIDTH):
                #set the color and then draw the character that represents this object at its position
        if map[self.x][self.y].explored and not (libtcod.map_is_in_fov(fov_map, self.x, self.y)):
            libtcod.console_set_default_foreground(con, color_light_ground * libtcod.dark_gray)
            libtcod.console_put_char(con, self.lastX, self.lastY, self.char, libtcod.BKGND_NONE)

        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
            self.lastX = self.x
            self.lastY = self.y

    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

    def collide(self, object):
        if self.y == object.y and self.x == object.x:
            return True
        else:
            return False
 
class Landmark(Object):
     
    #a location on the map that you can enter
    def __init__(self, x, y, char, color, name, objects, event):
        Object.__init__(self, x, y, char, color)
        self.name = name
        self.objects = objects
        self.event = event
        
    def update(self):
        for obj in self.objects:
            if Object.collide(self, obj):
                #run event if available
                self.event.run()
                                 
def make_map():
    global map
 
    #fill map with "unblocked" tiles
    map = [[ Tile(False)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]
 
    #place two pillars to test the map
    map[30][22].blocked = True
    map[30][22].block_sight = True
    map[50][22].blocked = True
    map[50][22].block_sight = True
    map[11][15].block_sight = True

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)
 
    #render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)
 
    #now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)
 
    #finally, some centered text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
        name + ': ' + str(value) + '/' + str(maximum))

def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute
 
    if fov_recompute:
        #recompute FOV if needed (the player moved or something)
        fov_recompute = False
        #check to see if player is inside a forest/trees, later will need to be able to check if player is in forest or on mountain and adjust FOV
        if map[player.x][player.y].block_sight == True:
            libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS/2, FOV_LIGHT_WALLS, FOV_ALGO)
        else:
            libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
 
        #go through all tiles, and set their background color according to the FOV
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = map[x][y].block_sight
                if not visible:
                    if map[x][y].explored:
                        if wall:
                            libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
                else:
                    #it's visible
                    if wall:
                        libtcod.console_set_char_background(con, x, y, color_light_wall, libtcod.BKGND_SET )
                    else:
                        libtcod.console_set_char_background(con, x, y, color_light_ground, libtcod.BKGND_SET )
                    map[x][y].explored = True
    
    #draw all objects in the list except for the player, who appears over other objects so is drawn last
    for object in objects:
        if object != player:
            object.draw()
    player.draw()

    #blit the contents of "con" to the root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    #print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1

    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

def message(new_msg, color = libtcod.white):
    #split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)
 
    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]
 
        #add the new line as a tuple, with the text and the color
        game_msgs.append( (line, color) )
 
def handle_keys():
    global fov_recompute
 
    #key = libtcod.console_check_for_keypress()  #real-time
    key = libtcod.console_wait_for_keypress(True)  #turn-based
 
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
 
    elif key.vk == libtcod.KEY_ESCAPE:
        return True  #exit game

    if game_state == 'playing':
        #movement keys
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            player.move(0, -1)
            fov_recompute = True
 
        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            player.move(0, 1)
            fov_recompute = True
 
        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            player.move(-1, 0)
            fov_recompute = True
 
        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            player.move(1, 0)
            fov_recompute = True
 
def player_death(player):
    global game_state
    message('You died!', libtcod.red)
    game_state = 'dead'
 
#############################################
# Initialization & Main Loop
#############################################
 
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'roguelite', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
 
#create object representing the player
player = Object(25, 23, '@', libtcod.white)

holeInMound = Script("a hole", "You reach inside the hole, you can't reach the end of the hole.")
discoverMound = Script("Atop the Mound", "on the plain, a two foot high vantage point can seem significant, until you view the hawk overhead.", {holeInMound.name:holeInMound})
holeInMound.scripts = {discoverMound.name:discoverMound}
mound = Landmark(SCREEN_WIDTH/2 + 10, SCREEN_HEIGHT/2 + 1, '^', libtcod.grey, "Mound", [player], discoverMound)

tree = Object(11, 15, 't', libtcod.green)

npc = Object(SCREEN_WIDTH/2 - 5, SCREEN_HEIGHT/2, '&', libtcod.red)
 
#the list of objects with those two
objects = [npc, player, mound, tree]
 
#generate map (at this point it's not drawn to the screen)
make_map()
 
#create the FOV map, according to the generated map
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)
        

 
fov_recompute = True
game_state = 'playing'

#create the list of game messages and their colors, starts empty
game_msgs = []
 
#a warm welcoming message!
message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', libtcod.red)
 
while not libtcod.console_is_window_closed():
 
    #render the screen
    render_all()
    libtcod.console_flush()
 
    #erase all objects at their old locations, before they move
    for object in objects:
        object.clear()
 
    objects[2].update()

    #handle keys and exit game if needed
    exit = handle_keys()
    if exit:
        break
