# Sean Leeka
# UA Dev Test
# 3 July 2017
from flask import Flask
from flask_restplus import Api, Resource, reqparse, fields
from datetime import datetime, timedelta
from redis import ConnectionPool, StrictRedis
import sys

app = Flask(__name__)
api = Api(app)
# Set up Redis connection
# redis_store = FlaskRedis(app, strict=False)
pool = ConnectionPool(host='redis', port=6379)

# POST parameters;  post_parser.parse_args() verifies
post_parser = reqparse.RequestParser()
post_parser.add_argument(
	'username', required=True, type=str, help='The user\'s username')
post_parser.add_argument(
	'message', type=str, required=True, help='The text message')
post_parser.add_argument(
	'timeout', required=False, type=int, default=60,
	help='Time (seconds) to consider a message as expired')

# GET parameters;  get_parser.parse_args() verifies
get_parser = reqparse.RequestParser()
get_parser.add_argument(
	'username', required=True, type=str, help='The user\'s username')

@api.route('/chat')
class chat(Resource):

	# POST
	@api.expect(post_parser)
	def post(self):
		args = post_parser.parse_args()
		# Do not allow usernames as integers
		if (args.username).isdigit():
			return 400
		# We've passed parameter validation.
		
		# Get redis connection pool
		redis_conn = StrictRedis(connection_pool=pool)
		
		# Insert into the database, using global message id as key
		_id = redis_conn.get('global_message_id')
		redis_conn.set(_id, args.message)

		# Incriment global message id
		redis_conn.incr('global_message_id')

		# Expire at timeout
		redis_conn.expire(_id, int(args.timeout))
		
		# Keep a list of message id's with username as the key
		redis_conn.lpush(args.username, _id)

		response = {"id": int(_id)}
		return response, 201 #status.HTTP_201_CREATED

	# GET
	@api.expect(get_parser)
	def get(self):
		args = get_parser.parse_args()
		# We've passed parameter validation.
		redis_conn = StrictRedis(connection_pool=pool)

		if not redis_conn.exists(args.username):
			return 'Username not found', 404  # NOT FOUND

		# Get all id's linked to username
		username_ids = redis_conn.lrange(args.username, 0, -1)

		# Delete username key
		redis_conn.delete(args.username)

		# Response from redis (messages)
		db_response = redis_conn.mget(*username_ids)
		# print(f'HERER {db_response}', file=sys.stderr)
		
		if not db_response:
		# No valid text messages for user args.username
			return 'No text messages', 404  # NOT FOUND
		# Create a JSON array		
		api_response = [{'id' : int(_id), 'text' : text.decode('utf-8')} for _id, text in zip(username_ids, db_response)]
		# I want to try searching and removing expired entries every 5min
		# print(f'HERER {api_response}', file=sys.stderr)
		return api_response, 200

	def delete(self):
		# Clear all collections in the database 'text_messages'
		clear_database()
		return 200

def clear_database():
	counter_db = StrictRedis(connection_pool=pool)
	counter_db.flushall()
	counter_db.set('global_message_id', 0)