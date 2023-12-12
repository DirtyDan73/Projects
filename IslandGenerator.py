from tkinter import colorchooser
from PIL import Image
import opensimplex
from enum import Enum
import random
import math
import pygame.math as m


worldSize = 1600;
blobNum = 4;
coords = []
noiseAmp = .2
maxHeight = 1.2

class Biome:
	tempMin = 0
	tempMax = 0
	moistMin = 0
	moistMax = 0
	tempMid = 0
	moistMid = 0
	def __init__(self, tempMin, tempMax, moistMin, moistMax):
		self.tempMin = tempMin
		self.tempMax = tempMax
		self.moistMin = moistMin
		self.moistMax = moistMax
		self.tempMid = (tempMin+tempMax)/2
		self.moistMid = (moistMin+moistMax)/2
		
class _biomes(Enum):
	RIVER = 1
	OCEAN = 2
	DEEPOCEAN = 3
	BEACH = 4
	TROPICAL = 5
	WOODLAND = 6
	DESERT = 7
	TEMPERATE = 8
	SAVANNA = 9
	ROCK = 10
	SNOWY = 11
	ICY = 12
	NULL = 13
	
biomes = {
	_biomes.RIVER: Biome(-999,-999,-999,-999),
	_biomes.OCEAN: Biome(-999,-999,-999,-999),
	_biomes.DEEPOCEAN: Biome(-999,-999,-999,-999),
	_biomes.BEACH: Biome(-999,-999,-999,-999),
	_biomes.TROPICAL: Biome(20,30,250,400),
	_biomes.WOODLAND: Biome(20,30,100,250),
	_biomes.DESERT: Biome(0,30,0,30),
	_biomes.TEMPERATE: Biome(4,20,70,400),
	_biomes.SAVANNA: Biome(0,30,30,70),
	_biomes.ROCK: Biome(-.5,0,0,100),
	_biomes.SNOWY: Biome(-9.99,-.5,0,100),
	_biomes.ICY: Biome(-100,-9.99,0,100),
}

class Coord:
	pos = m.Vector2(0,0)
	height = 1
	moisture = 0
	temp = 0
	biome = None

def GenWorldData():
	genCoordData()
	assignBiomes(genRiverData())
	DrawWorld()

def genCoordData():
	blobs = []
	ang = random.randrange(.0,360.0)
	blobs.insert(0, m.Vector2(worldSize/2,worldSize/2)+m.Vector2((worldSize/4)*math.sin(ang), (worldSize/4)*math.cos(ang)))
	nextDir = m.Vector2(blobs[0] - (m.Vector2(worldSize/2,worldSize/2))).normalize
	for i in range(blobNum):
		print(nextDir)
		blobs.append(blobs[-1]+m.Vector2.dot((worldSize/random.randrange(4.0,12.0),worldSize/random.randrange(4.0,12.0)),(nextDir)))
		nextDir = m.Vector2(1,0).rotate_rad(math.atan2(nextDir.y, nextDir.x) + math.radians(random.randrange(-30.0,30.0)))
	isLine = []
	for i in range(random.randrange(1,blobNum)): 
		isLine.append(random.randrange(0,blobNum-1))
	highestPoint=0
	for x in range(worldSize):
		coords.append([])
		for y in range(worldSize):
			totalInf = 0
			closestLine = 0
			for i in range(blobs.size()-1):
				l2 = m.Vector2(blobs[i]).distance_squared_to(blobs[i+1])
				t = max(0, min(1, m.Vector2(m.Vector2(x,y) - blobs[i]).dot(blobs[i+1]-blobs[i])/ l2))
				distToLine = m.Vector2(x,y).distance_to(blobs[i] + t * (blobs[i+1]-blobs[i]))
				influence
				if isLine.has(i):
					influence = .8/pow(distToLine/(worldSize*.04)+1, .8)
				else:
					influence = .8/pow(m.Vector2(x,y).distance_to(blobs[i])/(worldSize*.04)+1, .8)
				infAdj = influence * (1 - m.Vector2(worldSize/2, worldSize/2).distance_to(blobs[i])/(worldSize/1.5))
				totalInf += infAdj
			if totalInf>highestPoint:
				highestPoint = totalInf
			#Actually creating the coords
			coords[x].append(Coord.new())
			coords[x][y].pos = m.Vector2(x,y)
			coords[x][y].height = totalInf
	for x in range(worldSize):
		for y in range(worldSize):
			coords[x][y].height = coords[x][y].height*2-1
			coords[x][y].height += ((opensimplex.noise2(x,y)*noiseAmp)+opensimplex.noise2(float(x)/5,float(y)/5)*.3)
			coords[x][y].temp = max(-10,min((30 - (coords[x][y].height*30) + (((float(y)/worldSize)*20)-10)), 30))
			coords[x][y].moisture = max(0, min(((opensimplex.noise2(float(x)/3,float(y)/3)*400)+200)*((coords[x][y].temp)/30),400))

def genRiverData():
	riverHeads = []
	riverNext = []
	riverCoords = []
	snowline = 1
	riverNum = 3
	#find the riverheads
	for x in coords:
		for coord in x:
			if coord.height > 1 & coord.height < 1.1:
				riverHeads.append(m.Vector3(coord.pos.x, coord.pos.y, coord.height))
	for r in range(riverNum):
		riverNext.append(riverHeads.pick_random())
		while riverNext.is_empty() == False:
			for i in riverNext:
				if i == None:
					riverNext.clear()
					break
				riverCoords.append(i)
				if i.z < -.1:
					riverNext.clear()
					break
				coords[i.x][i.y].biome = _biomes.RIVER
				#these are the 4 tiles we check for height
				checking = [
					coords[i.x-1][i.y], coords[i.x+1][i.y], coords[i.x][i.y-1], coords[i.x][i.y+1]
				]
				checking.shuffle()
				fails = 0
				lowest = m.Vector3(0,0,10000)
				for j in checking:
					if j.height < lowest.z & j.biome != _biomes.RIVER:
						lowest = m.Vector3(j.pos.x,j.pos.y,j.height)
					if j.height > i.z | j.biome == _biomes.RIVER:
						fails += 1
				if fails >= 4:
					for j in checking:
						riverNext.append(m.Vector3(j.pos.x, j.pos.y, j.height))
				else:
					riverNext.clear()
					riverNext.append(lowest)
				riverNext.erase(i)
	for i in riverCoords:
		neighbors = [
					coords[i.x-1][i.y], coords[i.x+1][i.y], coords[i.x][i.y-1], coords[i.x][i.y+1]
				]
		for x in neighbors:
			x.biome = _biomes.RIVER
	return(riverCoords)
	
def assignBiomes(riverCoords):
	for r in riverCoords:
		radius = 7
		for x in range(r.x-radius,r.x+radius):
			for y in range(r.y-radius,r.y+radius):
				coords[x][y].moisture = max(0, min(coords[x][y].moisture + (1-(m.Vector2(r.x,r.y).distance_to(m.Vector2(x,y))/radius))*(20/radius), 400))
	for x in coords:
		for coord in x:
			if coord.biome == _biomes.RIVER:
				continue
			if coord.height <= 0:
				if coord.height >= -.01:
					coord.biome = _biomes.BEACH
				elif coord.height >= -.1:
					coord.biome = _biomes.OCEAN
				else:
					coord.biome = _biomes.DEEPOCEAN
				continue
			possibleBiomes = []
			for biome in biomes:
				if coord.temp >= biomes[biome].tempMin & coord.temp <= biomes[biome].tempMax & coord.moisture >= biomes[biome].moistMin & coord.moisture <= biomes[biome].moistMax:
					possibleBiomes.append(biome)
				if possibleBiomes.size() > 1:
					closestBiome = m.Vector2(-1, 1000000000)
					for poss in possibleBiomes:
						if m.Vector2(biomes[poss].moistMid, biomes[poss].moistMid).distance_to(m.Vector2(coord.moisture, coord.temp)) < closestBiome.y:
							closestBiome.y = m.Vector2(biomes[poss].moistMid, biomes[poss].moistMid).distance_to(m.Vector2(coord.moisture, coord.temp))
							closestBiome.x = poss
					coord.biome = closestBiome.x
				elif possibleBiomes.size() == 0:
					closestBiome = m.Vector2(-1, 1000000000)
					for poss in biomes:
						if m.Vector2(biomes[poss].moistMid, biomes[poss].moistMid).distance_to(m.Vector2(coord.moisture, coord.temp)) < closestBiome.y:
							closestBiome.y = m.Vector2(biomes[poss].moistMid, biomes[poss].moistMid).distance_to(m.Vector2(coord.moisture, coord.temp))
							closestBiome.x = poss
					coord.biome = closestBiome.x
				else:
					coord.biome = possibleBiomes[-1]

def DrawWorld():
	im = Image.new()
	for x in range(worldSize):
		for y in range(worldSize):
			if coords[x][y].biome == _biomes.ICY:
				im.putpixel((x,y), (255,255,255)) #ice
			elif coords[x][y].biome == _biomes.SNOWY:
				im.putpixel((x,y), (1,1,1))#snow
			elif coords[x][y].biome == _biomes.SAVANNA:
				im.putpixel((x,y), (1,1,1))#drygrass
			elif coords[x][y].biome == _biomes.TEMPERATE:
				im.putpixel((x,y), (1,1,1))#grass
			elif coords[x][y].biome == _biomes.WOODLAND:
				im.putpixel((x,y), (1,1,1))#darkgrass
			elif coords[x][y].biome == _biomes.TROPICAL:
				im.putpixel((x,y), (1,1,1))#wetgrass
			elif coords[x][y].biome == _biomes.BEACH:
				im.putpixel((x,y), (1,1,1))#sand
			elif coords[x][y].biome == _biomes.OCEAN | coords[x][y].biome == _biomes.RIVER:
				im.putpixel((x,y), (1,1,1))#water
			elif coords[x][y].biome == _biomes.DEEPOCEAN:
				im.putpixel((x,y), (1,1,1))#darkwater
			elif coords[x][y].biome == _biomes.DESERT:
				im.putpixel((x,y), (1,1,1))#desert
			elif coords[x][y].biome == _biomes.ROCK:
				im.putpixel((x,y), (1,1,1))#rock
	im.load()
	

GenWorldData()