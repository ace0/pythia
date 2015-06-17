"""
Contains cryptographic functions like hashing.
"""
import hashlib
import hmac as HMAC
import base64
import os
from base64 import urlsafe_b64encode as b64encode

HASH_ALG = hashlib.sha256
HASH_LENGTH = 32

# Tags for domain separation of hash functions.
TAG_SKID = "TAG_PYTHIA_SKID"


def skid(k):
	return hmac(TAG_SKID, "MESSAGE", k)


def buildTable(keys):
	"""
	Builds a dictionary mapping skid-to-keys.
	"""
	return dict([ (skid(k), k) for k in keys])


def sha(*args):
	"""
	Runs @args through the current hash algorithm (SHA256) and returns the 
	result as a (URL-safe) base64 string.
	"""
	i = ''.join(str(x) for x in args)
	return base64.urlsafe_b64encode( HASH_ALG(i).digest() )


def hmac(key, message, tag=None, alg=HASH_ALG, encode=base64.urlsafe_b64encode):
	"""
	Generates a hashed message authentication code (HMAC).
	"""
	return encode(HMAC.new(key, tag + message, digestmod=alg).digest())


def secureRandom(n=HASH_LENGTH):
	"""
	Gets a secure random string (base64 encoded) of @n bytes.
	"""
	return str(b64encode(os.urandom(n))[:n])
