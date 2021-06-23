from fastapi.testclient import TestClient
from main import app, Pool
import unittest
import random

class TestPool(unittest.TestCase):
	def setUp(self):
		self.pool = Pool()
	def test_insert_pool(self):
		self.pool.append([])
		self.assertEqual(self.pool.getLength(), 0)
		self.pool.append([1])
		self.assertEqual(self.pool.getLength(), 1)
		self.pool.append([2,3])
		self.assertEqual(self.pool.getLength(), 3)
		self.pool.append(list(range(4,100)))
		self.assertEqual(self.pool.getLength(), 99)
		self.assertFalse(self.pool.useTdigest)

		self.pool.append([100,101,102])
		self.assertEqual(self.pool.getLength(),102)
		self.assertTrue(self.pool.useTdigest)


class TestApi(unittest.TestCase):
	def setUp(self):
		self.client = TestClient(app)
		self.N = 10
		self.pool_counter = 0
		self.pool_id_range = list(range(self.N))
		random.shuffle(self.pool_id_range)

	def test_insert_pool(self):
		while self.pool_id_range:
			new_pool_id = self.pool_id_range.pop()
			json_file = {"poolId": new_pool_id, "poolValues": [1,2,3]}
			response = self.client.post(
				'/pools/addPool',
				json = json_file)
			self.assertEqual(response.status_code, 200)
			self.assertEqual(response.json(),"inserted")
			self.pool_counter += 1
		response = self.client.get('/DB')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(self.pool_counter, self.N)

	def test_append_pool(self):
		new_pool_id = self.N + 1
		tmp_pool_values = []
		new_value = random.randint(0,self.N)
		json_file = {"poolId": new_pool_id, "poolValues": [new_value]}
		response = self.client.post(
				'/pools/addPool',
				json = json_file)
		tmp_pool_values.append(new_value)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json(), "inserted")
		self.pool_counter+=1
		for _ in range(self.N):
			new_value = random.randint(0,self.N)
			json_file = {"poolId": new_pool_id, "poolValues": [new_value]}
			tmp_pool_values.append(new_value)
			response = self.client.post(
				'/pools/addPool',
				json = json_file)
			self.assertEqual(response.status_code, 200)
			self.assertEqual(response.json(), "appended")
		self.pool_counter+=1
		response = self.client.get('/DB')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.json()), 1)
		self.assertEqual(response.json()[0]['poolId'], self.N + 1)
		if len(tmp_pool_values) < 100:
			self.assertEqual(response.json()[0]['poolValues'], tmp_pool_values)
		else:
			self.assertTrue(response.json()[0]['useTdigest'])

	def test_bad_insert_pool(self):
		# bad pool id
		new_pool_id = 'a4'
		json_file = {"poolId":new_pool_id, "poolValues": [1,2,3]}
		response = self.client.post(
				'/pools/addPool',
				json = json_file)
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.json()['detail'][0]['msg'], "value is not a valid integer")

		#bad pool values
		new_pool_id = self.N+2
		json_file = {"poolId":new_pool_id, "poolValues": [1,'a',3]}
		response = self.client.post(
				'/pools/addPool',
				json = json_file)
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.json()['detail'][0]['msg'], "value is not a valid integer")

		#empty id
		json_file = {"poolId":"", "poolValues": [1,2,3]}
		response = self.client.post(
				'/pools/addPool',
				json = json_file)
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.json()['detail'][0]['msg'], "value is not a valid integer")

		#empty pool
		new_pool_id = self.N+3
		json_file = {"poolId":new_pool_id, "poolValues": []}
		response = self.client.post(
				'/pools/addPool',
				json = json_file)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json(), "inserted")

	def test_getPercentile(self):
		new_pool_id = self.N+4
		new_pool_values = list(range(10))
		input_percentile = 24.5

		json_file = {"poolId":new_pool_id, "poolValues":new_pool_values}
		response = self.client.post(
				'/pools/addPool',
				json = json_file)
	
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json(), "inserted")

		json_file = {"poolId":new_pool_id, "percentile":input_percentile}
		response = self.client.post(
				'/pools/getPercentile',
				# new_pool_id, input_percentile
				json= json_file)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json(), {
			'poolId': new_pool_id, 
			'poolLength': 10, 
			'percentile': 2.205
			})

	def test_getPercentileWithTDigest(self):
		new_pool_id = self.N+5
		new_pool_values = list(range(5000))
		input_percentile = 30.8

		json_file = {"poolId":new_pool_id, "poolValues":new_pool_values}
		response = self.client.post(
				'/pools/addPool',
				json = json_file)
	
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json(), "inserted")

		json_file = {"poolId":new_pool_id, "percentile":input_percentile}
		response = self.client.post(
				'/pools/getPercentile',
				json= json_file)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['poolId'], new_pool_id)
		self.assertEqual(response.json()['poolLength'], 5000)
		self.assertAlmostEqual(response.json()['percentile'], 1539.5)

	def test_badGetPercentile(self):
		new_pool_id = self.N + 6
		new_pool_values = list(range(10))


		json_file = {"poolId":new_pool_id, "poolValues":new_pool_values}
		response = self.client.post(
		'/pools/addPool',
		json = json_file)
	
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json(), "inserted")


		#empty pool_id
		input_percentile = "10"
		json_file = {"poolId": "a1", "percentile" : input_percentile}
		response = self.client.post(
				'/pools/getPercentile',
				json= json_file)
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.json()['detail'][0]['msg'], "value is not a valid integer")

		#not exist pool_id
		input_percentile = "10"
		json_file = {"pool_id": -1, "percentile" :input_percentile}
		response = self.client.post(
				'/pools/getPercentile',
				json= json_file)
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.json()['detail'][0]['loc'], ["body","poolId"])
		self.assertEqual(response.json()['detail'][0]['type'], "value_error.missing")

		#wrong input percentile
		input_percentile = "a10"
		json_file = {"poolId":new_pool_id, "percentile":input_percentile}
		response = self.client.post(
				'/pools/getPercentile',
				json= json_file)
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.json()['detail'][0]['msg'], "value is not a valid float")

		#empty input percentile
		input_percentile = ""
		json_file = {"poolId":new_pool_id, "percentile":input_percentile}
		response = self.client.post(
				'/pools/getPercentile',
				json= json_file)
		self.assertEqual(response.status_code, 422)
		self.assertEqual(response.json()['detail'][0]['msg'], "value is not a valid float")

		#percentile out of range
		input_percentile = 100.1
		json_file = {"poolId":new_pool_id, "percentile":input_percentile}
		response = self.client.post(
			'/pools/getPercentile',
			json= json_file)
		self.assertEqual(response.json(), "percentile must be in range (0 , 100)")



