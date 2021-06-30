from fastapi import FastAPI
from pydantic import BaseModel
import math
from typing import List
from tdigest import TDigest

app = FastAPI()
db = {}

class Pool:
	def __init__(self, poolId: int = 0):
		self.poolId = poolId
		self.poolValues = []
		self.useTdigest = False
	
	def getLength(self):
		return self.poolValues.to_dict()['n'] if self.useTdigest else len(self.poolValues)  

	def append(self, newValues):
		if len(newValues) + len(self.poolValues) >= 100:
			self.useTdigest = True
		
		if self.useTdigest:
			return self.appendTDigest(newValues)
		else:
			self.poolValues += newValues

	def appendTDigest(self, newValues):
		if type(self.poolValues) == list:
			tmp = self.poolValues
			self.poolValues = TDigest()
			for i in tmp:
				self.poolValues.update(i)
			self.useTdigest = True

		for i in newValues:
			self.poolValues.update(i)

	def getPercentile(self, percentile):

		if self.useTdigest:
			return self.poolValues.percentile(percentile)

		#credit: https://stackoverflow.com/questions/2374640/how-do-i-calculate-percentiles-with-python-numpy
		key = lambda x:x
		N = self.poolValues
		k = (len(N)-1) * percentile/100
		f = math.floor(k)
		c = math.ceil(k)
		if f == c:
			return key(N[int(k)])
		d0 = key(N[int(f)]) * (c-k)
		d1 = key(N[int(c)]) * (k-f)
		return d0+d1

class _Pool(BaseModel):
	poolId : int
	poolValues : List[int]

class _Percentile(BaseModel):
	poolId : int
	percentile : float

@app.get('/')
def index():
	return {'msg','Api Alive'}

@app.post('/pools/addPool')
def addPool(pool: _Pool)->str:
	poolId = pool.poolId
	poolValues = pool.poolValues
	if poolId not in db.keys():
		newPool = Pool(poolId = poolId)
		newPool.append(poolValues)
		db[poolId] = newPool
		return "inserted"
	else:
		curPool = db[poolId]
		curPool.append(poolValues)
		return "appended"

@app.post('/pools/getPercentile')
def getPercentile(percentileBM: _Percentile)->dict:
	poolId = percentileBM.poolId
	percentile = percentileBM.percentile
	if 0 > percentile or percentile > 100:
		return "percentile must be in range (0 , 100)"
	curPool = db.get(poolId)
	if curPool.getLength() == 0:
		return "Unable to calculate percentile on empty pool"
	return {
		'poolId': poolId,
		'poolLength': curPool.getLength(),
		'percentile': curPool.getPercentile(percentile)
		}

@app.get('/DB')
def getDB():
	return [db[key] for key in db.keys()]
	