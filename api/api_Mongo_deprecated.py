# Sean Leeka
# UA Dev Test
# 3 July 2017
from flask import Flask
from flask_restplus import Api, Resource, reqparse, fields
from datetime import datetime, timedelta
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

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

#Set up database connection.
client = MongoClient('mongodb://mongo:27017')
db = client['text_messages']

@api.route('/chat')
class chat(Resource):

	# def __init__(self, *args):
	# 	global message_id
	# 	message_id = 0

	# POST
	@api.expect(post_parser)
	def post(self):
	    args = post_parser.parse_args()
	    # We've passed parameter validation.

	    global message_id
	    message_id += 1
	    # Data to add to the database 'text_messages'
	    data = {
	        '_id': message_id,
	    	'message': args.message,
	    	'timeout': datetime.utcnow() + timedelta(0,args.timeout) # (hours, seconds)
	    }
	    # Insert into the database
	    db[args.username].save(data)

	    response = {"id": message_id}
	    return response, 201 #status.HTTP_201_CREATED

	# GET
	@api.expect(get_parser)
	def get(self):
		args = get_parser.parse_args()
		# We've passed parameter validation.

		if args.username not in db.collection_names():
			return 'Username not found', 404  # NOT FOUND

		current_time = datetime.utcnow()
		query = {"timeout" : { "$gte" : current_time}}
		# Response from the Mongo database
		db_response = list(db[args.username].find(query))

		if len(db_response) == 0:
		# No valid text messages for user args.username
			return 'No text messages', 404  # NOT FOUND
		# Create an array		
		api_response = [{'id' : r['_id'], 'text' : r['message']} for r in db_response]
		# These are now expired
		db[args.username].remove({"_id" : {"$in" : [r['id'] for r in api_response]}})
		# I want to try searching and removing expired entries every 5min
		return api_response, 200
		

	def delete(self):
		# Clear all collections in the database 'text_messages'
		clearDatabase()
		return 200

def clearDatabase():
	# Iterate through all collections in the database 'text_messages'
	for collection in db.collection_names():
		db[collection].drop()
	global message_id
	message_id = 0

# if __name__ == "__main__":
def initialize(app):
	global message_id
	# DELETE all collections in the 'text_messages' database
	# This prevents duplicate primary keys!
	clearDatabase()
	# Static message ID, increments +1 per message
	# This will get large with millions of users @ 1,000 tps,
	#	but Python handles large numbers well
	#	We could reset this depending on a max timeout
	message_id = 0

	# To persist data, comment the above two lines and uncomment the line below
	# message_id = sum([db[collection].count() for collection in db.collection_names()])

	# Does not run threaded 
	# app.run(host='0.0.0.0', debug=True)
initialize(app)
