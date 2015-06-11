"""
Interface to the mongodb datastore
"""
from datetime import datetime
import mongoengine
from settings import *
from crypto import *

# Connect to mongoDB
mongoengine.connect(PYTHIA_PRF_DB)


class StateEntry(mongoengine.Document):
	"""
	The server's secure state table maps each client ID (w) to a randomly
	selected value that can be deleted, at the client's request, to ensure
	forward secrecy.
	"""
	# TODO: Add expiration, limit, contact info (email/SMS), and LastAccessTime.
	key = mongoengine.StringField(max_length=HASH_LENGTH)
	value = mongoengine.StringField(max_length=HASH_LENGTH)

	# An index on key makes lookups fast.
	meta = { "indexes": ["key"] }


def getStateEntry(w):
	"""
	Get the state table entry, z, for client ID @w. If no entry is found, a new
	entry will be generated randomly and stored in the table.
	"""
	w = str(w)[:HASH_LENGTH]

	# Check the table
	entry = StateEntry.objects(key=w).first()

	# If there's no state for this key, make a new entry.
	if not entry:
		z = secureRandom(HASH_LENGTH)
		entry = StateEntry(key=w, value=z).save()

	return entry.value


def checkStateEntry(w):
	"""
	Determines if entry @w exists in the state table.
	"""
	# Check the table for this value.
	w = str(w)[:HASH_LENGTH]
	entry = StateEntry.objects(key=w).first()
	return entry is not None


def dropStateEntry(w):
	"""
	Removes the state entry associated with @w.
	"""
	w = str(w)[:HASH_LENGTH]
	entry = StateEntry.objects(key=w).delete()


class QueryCount(mongoengine.Document):
	"""
	Tracks the number of unique queries on a parameter t (tweak). Permits 
	rate-limiting of queries which restricts guessing attacks.
	"""
	t = mongoengine.StringField(max_length=HASH_LENGTH)
	count = mongoengine.IntField()
	lastAccessTime = mongoengine.DateTimeField()

	# An index on t makes lookups fast.
	meta = { "indexes": [ 
			  # An index on t makes counting accesses fast.
			  "t", 

			  # An expiration index on time allows old information to 
			  # quietly disappear from the database once the period has past.
			  { 
			    'fields': ['lastAccessTime'],
		        'expireAfterSeconds': RATE_LIMIT_PERIOD_SECONDS
			 }
	 	] }


def noteQuery(t, threshold=RATE_LIMIT_THRESHOLD):
	"""
	Increments counters associated with query parameter @t (tweak) and 
	reports whether or not @threshold for @t has been exceeded.
	"""
	# NOTE: Using lastAccessTime for expiration time isn't quite right.
	# For hourly rate-limiting it's ok because we don't antictipate requests
	# coming once per hour for 10 hours in a row (which would erroneously 
	# trigger) the rate-limit. But for something like monthly or daily limits, 
	# this implementation fails and can trigger unintended rate-limiting.

	# Record this query in datastore
	QueryCount.objects(t=t).update_one(
		upsert = True, 
		inc__count = 1,
		set__lastAccessTime = datetime.now)

	# Check the count against the threshold
	if threshold is None:
		return True
	else:
		return QueryCount.objects.get(t=t).count <= threshold


class VerificationCode(mongoengine.Document):
	"""
	Stores short-term verification codes.
	"""
	# If we use vcodes more genererically, we can change this to just key/value
	w = mongoengine.StringField(max_length=HASH_LENGTH)
	vcode = mongoengine.StringField(max_length=HASH_LENGTH)
	creationTime = mongoengine.DateTimeField()

	meta = { "indexes": [ 
			  # Fast lookup
			  "w", 

			  # Expire old codes
			  { 
			    'fields': ['creationTime'],
		        'expireAfterSeconds': VERIFICATIION_CODE_EXPIRE_SECONDS
			 }
	 	] }


def dropVerificationCode(w):
	"""
	Removes any verification codes associated with @w.
	"""
	w = str(w)[:HASH_LENGTH]
	entry = VerificationCode.objects(w=w).delete()


def writeVerificationCode(w, v):
	"""
	Stores verification code @v associated with client ID @w.
	"""
	VerificationCode.objects(w=w).update_one(
		upsert = True,
		set__vcode = v,
		set__creationTime = datetime.now)


def getVerificationCode(w):
	"""
	Retrieves the verification code associated with client ID @w.
	"""
	entry = VerificationCode.objects(w=w).first()
	if entry:
		return entry.vcode
	else:
		return None

