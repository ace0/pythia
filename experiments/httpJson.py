"""
Routines for interacting with a remote service via HTTP/HTTPS and parsing the 
response as JSON.
"""
import httplib2, json
from urllib import urlencode

httpClient = httplib2.Http()


def getUrl(base, params):
	"""
	Appends @params from a dictionary to the end of a @base URL.
	"""
	# No params are easy
	if not params:
		return base

	# Format the parameters into a query string and return the combined URL.
	paramString = urlencode(params, doseq=True)
	return "{}?{}".format(base, paramString)


def fetch(url, params=None, keepalive=False, requireValidCert=False, 
		debug=False):
	"""
	Fetches the desired @url using an HTTP GET request and appending and 
	@params provided in a dictionary.

	If @keepalive is False, a fresh connection will be made for this request.
	If @requireValidCert is True, then an exception is thrown if the remote 
	server cannot provide a valid TLS certificate.

	If @keepalive is False, connections are closed and so subsequent connections
	must make fresh (cold) HTTPS connections.

	@returns the result as a dictionary, decoded from server-provided JSON.

	@raises an exception if there are any problems connecting to the remote 
	server, receiving a valiud HTTP status 200 response, or decoding the 
	resulting JSON response.
	"""
	# Set the certificate verification flag
	httpClient.disable_ssl_certificate_validation = not requireValidCert

	# Assemble the URL
	url = getUrl(url, params)

	if debug:
		print "Fetching " + url

	# Fetch the URL with a GET request.
	response, content = httpClient.request(url, "GET")

	# Check the status code.
	if response.status != 200:
		m = "Remote service reported an error (status:{} {}) for "\
			"URL {}".format(response.status, response.reason, url)
		raise Exception(m)

	# Close the connection if requested.
	if not keepalive:
		map(lambda (k,v): v.close(), httpClient.connections.iteritems())

	# Parse the response
	return json.loads(content)
