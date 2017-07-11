#!python3.6
# Sean Leeka
# UA Dev Test
# 3 July 2017
### REQUIREMENTS: pip install flask_restplus
import requests
from flask_restplus import Api
from random import choice, shuffle
from itertools import permutations
from time import time
from json import loads
# from numba import jit
from multiprocessing import Pool

# Test texts per second and user load; Must be greater than 10
# Usually 100-150
class user_load_tests():

	def __init__(self):
		# WEB SERVER
		self.url = 'http://127.0.0.1:8080/chat'
		# UNIQUE USERNAME SOURCE
		with open('top_2000_baby_names.txt','r') as f:
			self.usernames = f.read().split(',')

		# MUST use an even user_count
		# POST/GET are paired evenly in test_texts_per_second()
		test_param = [
			{'user_count' : 100},
			{'user_count' : 500},
			{'user_count' : 1000},
			{'user_count' : 2000},
			# {'user_count' : 100000},
			# {'user_count' : 1000000},
			# {'user_count' : 10000000},
			# {'user_count' : 100000000},
		]

		for test in test_param:
			self.test_texts_per_second(**test)


	def req(self, x):
			requests.post(self.url, {'username':x[0], 'message':x[1]})
			requests.get(self.url, {'username':x[2]})

	# @jit
	def test_texts_per_second(self, user_count):
		# DROP ALL COLLECTIONS FROM DATABASE 'text_messages'
		requests.delete(self.url)

		# CREATE PAYLOAD:
		payload = self.create_payload(user_count)

		print(f'\n{user_count:,} shuffled users;\tPOST/GET = 1 text; 2 iterations:')
		
		pool = Pool(4)

		### START ###
		start = time()

		for _ in range(2):
			pool.map(self.req,payload)

		elapsed = time()-start
		### STOP ###
		print(f'User count: {user_count:,}\tTPS: {user_count*2/elapsed:,.1f}')

	def create_payload(self, user_count):
		# CREATE PAYLOADS FOR UP TO 2K USERS
		post_data, get_data = [], []
		for name in self.usernames:
			post_data.append([name, self.rand_message_gen()])
			get_data.append(name)
			user_count -= 1
			if not user_count:		# a.k.a.: if user_count == 0:
				break 

		if user_count > 0:
			# HERE, user_count = 2,000
			# PERMUTE USERNAMES FOR UP TO 2,001,000 USERS
			for name in permutations(self.usernames,2):
				post_data.append([f'{name[0]}{name[1]}','Do not waste RAM'])
				get_data.append(f'{name[0]}{name[1]}')
				user_count -= 1
				if not user_count:	# a.k.a.: if user_count == 0:
					break

		# if user_count > 0:
		# 	# HERE, user_count = 2,001,000
		# 	# PERMUTE USERNAMES FOR UP TO 1,333,335,000 USERS
		# 	for name in permutations(self.usernames,3):
		# 		post_data.append([f'{name[0]}{name[1]}{name[2]}', 'Do not waste RAM'])
		# 		get_data.append('{name[0]}{name[1]}{name[2]}')
		# 		user_count -= 1
		# 		if not user_count:	# a.k.a.: if user_count == 0:
		# 			break


		# ARRANGE DATA TO EXECUTE POST/GET REQUESTS SEQUENTIALLY
		shuffle(post_data)
		shuffle(get_data)		# shuffling slows down TPS ;)
		payload = []
		for count in range(len(get_data)):
			post_data[count].append(get_data[count])
			# p = f'requests.post(\"{self.url}\", {{\"username\":\"{post_data[count][0]}\", \"message\":\"{post_data[count][1]}\"}})'
			payload.append(post_data[count])
			# g = f'requests.get(\"{self.url}\", {{\"username\":\"{get_data[count]}\"}})'
			# payload.append(get_data[count])
		return payload

	def rand_message_gen(self):
		s_nouns = ["A dude", "Bob Dole", "My mom", "The king", "Bob Barker", "Francis Bacon", "Some guy", "A cat with rabies", "A sloth", "Your homie", "This cool guy my gardener met yesterday", "Superman"]
		p_nouns = ["These dudes", "These drivers", "Both of my aunts", "All the kings of the world", "Some guys", "All of a cattery's cats", "The multitude of sloths living under your bed", "Your homies", "Like, these, like, all these people", "Supermen"]
		s_verbs = ["eats", "kicks", "gives", "treats", "meets with", "creates", "hacks", "configures", "spies on", "encourages", "meows on", "flees from", "tries to automate", "explodes"]
		p_verbs = ["eat", "kick", "give", "treat", "meet with", "create", "hack", "configure", "spy on", "encourages", "meow on", "flee from", "try to automate", "explode"]
		infinitives = ["to make a pie.", "because of nausia.", "for no apparent reason.", "because the sky is green.", "for a disease.", "to be able to make toast explode.", "to know more about archeology."]
		
		string = ""
		string += choice(s_nouns) + " "
		string += choice(s_verbs) + " "
		string += choice(s_nouns).lower() + " " or choice(p_nouns).lower() + " "
		string += choice(infinitives)
		return string

class test_chat_api():
	def __init__(self):
		self.api_url = 'http://localhost:8080/chat'
		requests.delete(self.api_url)
		self.test_post()
		self.test_get()
		self.test_delete()


	def test_post(self):
		# Valid POSTs
		val_params = [
		{'message':'Learning never exhausts the mind.', 'username': "Leonardo da Vinci", 'timeout':600},
		{'message':'I love.', 'username': "Leonardo da Vinci"},
		{'username':'Al Pacino', 'message':"It's easy to fool the eye but it's hard to fool the heart."},
		{'username':'Aldous Huxley',
		'message':"There is only one corner of the universe you can be certain of improving, and that's your own self.",
		'timeout':36000}
		]
		for params in val_params:
			response = requests.post(self.api_url, params)
			assert response.status_code == 201

			response = loads(response.content.strip())
			assert 'id' in response.keys()
			assert isinstance(response['id'], int)

		# Invalid POSTs
		inv_params = [
		{'username':'James Bond'},	# No message
		{'message':'Being entirely honest with oneself is a good exercise. -Sigmund Freud'},	# No username
		{'username': 'Thomas Jefferson','timeout': 60},	# No message, with timeout
		{'message': 'The best preparation for tomorrow is doing your best today.','timeout': 60}, # No username, with timeout
		{'timeout':346}
		] # could try every char encoding, or funky objects sent
		
		for invalid in inv_params:		
			response = requests.post(self.api_url, invalid)
			assert response.status_code == 400
		print('\t** /chat POST successfully tested **')


	def test_get(self):
		# Valid GETs
		response = requests.get(self.api_url, {'username':'Leonardo da Vinci'})

		# We added two messages to Leo in POST
		text = ['Learning never exhausts the mind.', 'I love.']		# Order is kept

		assert response.status_code == 200
		response = loads(response.content.strip())

		for r in response:
			assert 'id' in r.keys()
			assert 'text' in r.keys()
			assert r['text'] in text
			text.remove(r['text'])
			assert isinstance(r['id'], int)

		# Invalid GETs
		# No username key
		response = requests.get(self.api_url, "Leonardo da Vinci")
		assert response.status_code == 400

		# User has not been added
		response = requests.get(self.api_url, {'username':"Francis Bacon"})
		assert loads(response.content.strip()) == 'Username not found'
		assert response.status_code == 404

		# No user requested
		response = requests.get(self.api_url)
		assert response.status_code, 400		
		print('\t** /chat GET successfully tested **')

	# These are run out of order, and often delete the data I'm verifying via GET

	def test_delete(self):

		# Valid DELETE
		response = requests.delete(self.api_url)
		assert response.status_code == 200

		# Invalid DELETE
		response = requests.delete('http://127.0.0.1:8080')
		assert response.status_code == 405
		print('\t** /chat DELETE successfully tested **')

if __name__=="__main__":
	test_chat_api()
	user_load_tests()
