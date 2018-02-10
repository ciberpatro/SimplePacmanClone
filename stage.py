from bge import logic

CONSTANT_COORDINATES=1.21874
POINTS_DOT=50
POINTS_GHOST=1000

scene = logic.getCurrentScene()

class Entity:
	def __init__(self, name, spawn):
		self.name=name
		self.spawn=spawn
	def getName(self):
		return self.name
	def getSpawn(self):
		return self.spawn

#Init script, put all the entities in the a fixed stage.
#dot_table: First dimension store the row, second dimension the column of the stage
def init(cont):
	coordinates=scene.objects['Dot_spawner'].worldPosition
	parent = scene.objects['Stage']
	dot_table = [[],
	[Entity('Dot',x) for x in range(1,15)],
	[Entity('Dot',1),Entity('Dot',6),Entity('Dot',9),Entity('Dot',14)],
	[Entity('SpecialDot',1)]+[Entity('Dot',x) for x in range(2,14)]+[Entity('SpecialDot',14)],
	[Entity('Dot',2),Entity('Dot',6),Entity('Dot',9),Entity('Dot',13)],
	[Entity('Dot',2)]+[Entity('Dot',x) for x in range(4,12)]+[Entity('Dot',13)],
	[Entity('Dot',2),Entity('Dot',4),Entity('Dot',11),Entity('Dot',13)],
	[Entity('Dot',2),Entity('Dot',4),Entity('Ghost_LightBlue',7),Entity('Ghost_Red',8),Entity('Dot',11),Entity('Dot',13)],
	[Entity('Dot',2),Entity('Dot',4),Entity('Ghost_Orange',7),Entity('Ghost_Pink',8),Entity('Dot',11),Entity('Dot',13)],
	[Entity('Dot',2),Entity('Dot',4),Entity('Dot',11),Entity('Dot',13)],
	[Entity('Dot',x) for x in range(2,7)]+[Entity('Player',7)]+[Entity('Dot',x) for x in range(9,14)],
	[Entity('Dot',3),Entity('Dot',12)],
	[Entity('SpecialDot',1)]+[Entity('Dot',x) for x in range(2,7)]+[Entity('Dot',x) for x in range(9,14)]+[Entity('SpecialDot',14)],
	[Entity('Dot',1),Entity('Dot',6),Entity('Dot',9),Entity('Dot',14)],
	[Entity('Dot',x) for x in range(1,15)],
	[]]
	
	#Debug table
	"""dot_table = [[],[],[],[],[],[],[],
	[Entity('Ghost_LightBlue',7),Entity('Ghost_Red',8)],
	[],[],[],
	[Entity('Player',7)],[Entity('SpecialDot',6),Entity('Dot',7)],
	[],[],[]]"""
	
	for line_number, line in enumerate(dot_table):
		for dot in line:
			d=scene.objectsInactive[dot.getName()]
			d.worldPosition.y=(dot.getSpawn()*CONSTANT_COORDINATES)+coordinates.y
			
			d.worldPosition.x=(line_number*CONSTANT_COORDINATES)+coordinates.x
			
			a=scene.addObject(d, d, 0)
			if dot.getName() == 'Dot' or dot.getName() == 'SpecialDot':
				a.setParent(parent,True,True)

#Pacman death. It stop the music and change the state of the stage
def pacman_death(cont):
	stage = cont.owner
	status = stage.sensors['Message_Death'].status
	if status == logic.KX_SENSOR_JUST_ACTIVATED:
		stage.actuators['BM'].stopSound()
		cont.activate(stage.actuators['End_Game_Death'])

#Pacman eat a dot, giving points and also check if all dots are eaten. 
#All the dots are children of the stage so when children of stage == 0, the player win and change to the next stage
def dot(cont):
	stage = cont.owner
	sensor = cont.sensors['Dot']
	status = sensor.status
	if status == logic.KX_SENSOR_JUST_ACTIVATED and sensor.subject == 'dot':
		stage['points']+=POINTS_DOT
		cont.activate(stage.actuators['GUI_Points'])
		cont.activate(stage.actuators['DotSound'])
		if len(stage.children) == 0:
			stage.actuators['BM'].stopSound()
			stage['blink'] = 'Stage'
			cont.activate(stage.actuators['End_Game'])
		stage['dots']+=1
#It send a message to make all the ghost scared
def scare_timer(cont):
	stage = cont.owner
	stage['scared_timer']=stage['scared_time']
	sensor = stage.sensors['BigDot']
	status = sensor.status
	if status ==logic.KX_SENSOR_JUST_ACTIVATED:
		mg = stage.actuators['ScareGhosts']
		cont.activate(mg)

#It send a message to make the ghost blink until its deactivated.
#If stage['scared_time'] == stage['scared_timer'] means that they start blinking but the player ate a fat dot so
# the ghost will still be scared
def blinking_ghost(cont):
	status = cont.sensors['ScareTimeBlink'].status
	stage = cont.owner
	mg = None
	if status == logic.KX_SENSOR_JUST_ACTIVATED:
		mg = stage.actuators['StartBlink']
	elif status == logic.KX_SENSOR_JUST_DEACTIVATED and stage['scared_time'] != stage['scared_timer']:
		mg = stage.actuators['StopScared']
	if mg != None: cont.activate(mg)

#Change the pitch of the background music when the ghost are scared or not
def scary_music(cont):
	stage = cont.owner
	bm_start= stage.sensors['BM_Start']
	bdot_sens = stage.sensors['BigDot']
	sound = stage.actuators['BM']
	stop_pitch = cont.sensors['ScareTimeBlink'].status
	if bm_start.status == logic.KX_SENSOR_JUST_ACTIVATED:
		cont.activate(sound)
		sound.pitch=1
	if bdot_sens.status == logic.KX_SENSOR_JUST_ACTIVATED:
		sound.pitch=2
	if stop_pitch == logic.KX_SENSOR_JUST_DEACTIVATED and stage['scared_time'] != stage['scared_timer']:
		sound.pitch=1

#Blink when pacman win the game
def blink(cont):
	stage = cont.owner
	status = cont.sensors['BlinkBool_Stage'].status
	if status == logic.KX_SENSOR_JUST_ACTIVATED or status == logic.KX_SENSOR_ACTIVE:
		if stage['blink'] == 'Stage_White':
			stage.replaceMesh('Stage')
			stage['blink'] = 'Stage'
		
		elif stage['blink'] == 'Stage':
			stage.replaceMesh('Stage_White')
			stage['blink'] = 'Stage_White'

#Pacman eats a ghost giving points
def ghost_killed(cont):
	stage = cont.owner
	status = stage.sensors['Ghost_Killed'].status
	if status == logic.KX_SENSOR_JUST_ACTIVATED:
		stage['points']+=POINTS_GHOST
		cont.activate(stage.actuators['GUI_Points'])

#The gui appear in the game
def gui(cont):
	gui = cont.owner
	sensor = gui.sensors['Message']
	if sensor.status == logic.KX_SENSOR_JUST_ACTIVATED:
		gui['Text']="Points: %d" % int(sensor.bodies[0])