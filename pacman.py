from bge import logic
from bge import events

import mathutils

speed=0.1

scene=logic.getCurrentScene()

UP=mathutils.Quaternion((0.7071,0,0,0.7071))
DOWN=mathutils.Quaternion((0.7071,0,0,-0.7071))
RIGHT=mathutils.Quaternion((1,0,0,0))
LEFT=mathutils.Quaternion((0,0,0,-1))

#Movement of pacman, when the player go up Pacman rotate to up, when the player go down Pacman rotate to down, etc
def direction(cont):
	keyboard = cont.sensors["Keyboard"]
	player = cont.owner
	
	for key, status in keyboard.events:
		
		if status == logic.KX_INPUT_ACTIVE:
			if key == events.UPARROWKEY:
				if player["orientation"]!="UP": player.localOrientation=UP; player['orientation']="UP"
				player.applyMovement((-speed,0,0),False)
			if key == events.DOWNARROWKEY:
				if player["orientation"]!="DOWN": player.localOrientation=DOWN; player['orientation']="DOWN";
				player.applyMovement((speed,0,0),False)
			if key == events.LEFTARROWKEY:
				if player["orientation"]!="LEFT": player.localOrientation=LEFT; player['orientation']="LEFT";
				player.applyMovement((0,-speed,0),False)
			if key == events.RIGHTARROWKEY:
				if player["orientation"]!="RIGHT": player.localOrientation=RIGHT; player['orientation']="RIGHT" 
				player.applyMovement((0,speed,0),False)

#Make the player teleport to the other side of the stage
def tp(cont):
	player = cont.owner
	
	status = cont.sensors["TP"].status
	
	if status == logic.KX_SENSOR_JUST_ACTIVATED:
		message=cont.sensors["TP"].bodies[0]
		if message == "RIGHT_2_LEFT":
			spawn = scene.objects["Left_spawn"]
		elif message == "LEFT_2_RIGHT":
			spawn = scene.objects["Right_spawn"]
		player.worldPosition=spawn.worldPosition

#Copy of pacman to be followed by the ghost when they are scared
def ghost(cont):
	ghost_player = cont.owner
	if "Player" in scene.objects:
		player = scene.objects['Player']
		pos = player.worldPosition
		ghost_player.worldPosition = [-pos.x,-pos.y,pos.z]

#Detect collsion with the ghosts. If ghost is killable the ghost go back to the jail else pacman die and game over.
def ghost_collision(cont):
	player = cont.owner
	sensor = cont.sensors['Collision']
	ghost = sensor.hitObject
	if ghost != None:
		if ghost['killable']:
			logic.sendMessage("ghost_killed","",ghost.name,"")
			cont.activate(player.actuators['EatGhost'])
			cont.activate(player.actuators['Ghost_Killed'])
		else:
			cont.activate(player.actuators['PacmanDeath'])
			player.endObject()
