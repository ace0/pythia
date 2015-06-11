"""
Settings for the Pythia PRF service.
"""
from crypto import *

##
# Datastore settings
##

# The name of our mongo db instance
PYTHIA_PRF_DB = 'pythiaPrf'


##
# Rate-limiting on query parameter t (tweak or user ID)
##

# Currently permitting 10 guesses per hour
RATE_LIMIT_THRESHOLD = 10
RATE_LIMIT_PERIOD_SECONDS = 3600

# DEBUG: Rate-limits disabled for performance testing
RATE_LIMIT_THRESHOLD = None

# Expire verification codes after 1 week
VERIFICATIION_CODE_EXPIRE_SECONDS = 3600*24*7

##
# Secret keys for Pythia PRF service
##

# TODO: Read these from S3
# Server secret keys, including previous secret keys.
keys = [ 
		 bytes("281fc58e9d22ad08cc17ad0d8f2688e4403440b03df3").encode('utf-8'), 
 		 bytes("0d8f2688e4403440b03df3281fc58e9d22ad08cc17ad").encode('utf-8'),
		]

SERVER_SECRET_KEY = keys[0]
SERVER_SKID = skid(keys[0])

# Put keys into a table mapping the secret key ID (skid) to the key value.
keyTable = buildTable(keys)


##
# Standardized error codes and messages
##

ERROR_CODE_GENERAL = "ERROR"
ERROR_CODE_QUERY_LIMIT = "QUERY-RATE-LIMIT-EXCEEDED"

# Error messages
ERROR_MISSING_PARAMS = "Your request is missing required parameters. "\
	"This request requires parameters: {}"

ERROR_EXCEEDED_QUERY_LIMIT = "The number of queries for this tweak t "\
	"has been exceeded. Only {0} queries are permitted every {1} seconds. "\
	"This parameter is locked for {1} seconds.".format(RATE_LIMIT_THRESHOLD, 
		RATE_LIMIT_PERIOD_SECONDS)


def dp(**kwargs):
	"""
	Debugging print. Prints a list of labels and values, each on their
	own line.
	"""
	for label,value in kwargs.iteritems():
		print "{0}\t{1}".format(label, value)


