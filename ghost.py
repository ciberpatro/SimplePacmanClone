from bge import logic
from random import random

scene = logic.getCurrentScene()

scared_speed=1
killed_speed=10

#This function defines the movement of the ghost it uses properties to change dynamically the target and speed 

def movement(cont):
	ghost = cont.owner
	
	target = ghost['target']
	speed = ghost['speed']
	
	steering = cont.actuators['Steering']
	if target in scene.objects:
		steering.target = scene.objects[target]
		steering.velocity = speed
	
		cont.activate(steering)

#The ghost start the normal behaviour (follow the player)
def following(cont):
	ghost = cont.owner
	normal_ghost(ghost)
	
	cont.activate(ghost.actuators['Follower_Ghost'])

#The Ghost is killed and it move to the jail or spawn
def killed(cont):
	ghost = cont.owner
	ghost['speed']=killed_speed
	ghost['spawn']=False
	ghost['target']='Ghost_spawn'
	ghost['killed']=True
	
	ghost.collisionGroup=4
	ghost.collisionMask=3
	
	cont.activate(ghost.actuators['Ghost2Spawn'])

#The ghost is scared and start to follow the Player_Ghost
def scared(cont):
	ghost = cont.owner
	status = cont.sensors['Scared_Ghost'].status
	if status == logic.KX_SENSOR_JUST_ACTIVATED:

		ghost['speed']= scared_speed
		ghost['target']='Player_Ghost'
		ghost['killable']=True
		ghost['blink']="NO"
		ghost.replaceMesh('Ghost_scared')
		
		if ghost.state != 9:
			cont.activate(ghost.actuators['Ghost_Scared'])

#The ghost go back to the normal behaviour
def unscared(cont):
	ghost = cont.owner
	status = cont.sensors['Unscared_Ghost'].status

	if not ghost['killed'] and status == logic.KX_SENSOR_JUST_ACTIVATED:
		normal_ghost(ghost)
		cont.activate(ghost.actuators['Follower_Ghost'])

#The ghost blink until ghost['blink']="NO"
def blink(cont):
	ghost = cont.owner
	status = cont.sensors['BlinkBool'].status
	if status == logic.KX_SENSOR_JUST_ACTIVATED or status == logic.KX_SENSOR_ACTIVE:
		if ghost['blink'] == 'BLINK':
			ghost.replaceMesh('Ghost_blinking')
			ghost['blink'] = 'SCARED'
		elif ghost['blink'] == 'SCARED':
			ghost.replaceMesh('Ghost_scared')
			ghost['blink'] = 'BLINK'

#When a ghost is killed it have a chance of 10 % to go back to the normal behaviour
def in_spawn(cont):
	ghost = cont.owner
	ghost.replaceMesh(ghost.name)
	if random() > 0.9:
		normal_ghost(ghost)
		cont.activate(ghost.actuators['Follower_Ghost'])

#Function that define the behaviour of a follower ghost
def normal_ghost(ghost):
	ghost['speed']=ghost['default_speed']
	ghost['killable']=False
	ghost['target']='Player'
	ghost['blink']='NO'
	ghost['killed']=False
	
	ghost.collisionGroup=2
	ghost.collisionMask=1
	
	ghost.replaceMesh(ghost.name)