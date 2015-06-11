"""
Custom HTTP responses in JSON and standardized exceptions.
"""
from settings import *
from django.shortcuts import render
from django.http import HttpResponse
import json


class JsonResponse(HttpResponse):
	"""
	A JSON response converts a dictionary @d into JavaScript
	Object Notation (JSON) and uses the "application/json"
	content type.
	"""
	def __init__(self, d):
		super(JsonResponse, self).__init__(json.dumps(d), 
			content_type="application/json")

		# Generates HTTP 500: Internal Server Error
		#super(JsonResponse, self).__init__("This is not the JSON you're looking for"), content_type="application/text")

		# Generates JSON parse errors in the client.
		#super(JsonResponse, self).__init__("This is not the JSON you're looking for")


class ErrorResponse(JsonResponse):
	"""
	Generates a JsonResponse with the specified @error message.
	"""
	def __init__(self, message, code=ERROR_CODE_GENERAL):
		d = { "errorMessage": message, 
			  "errorCode": code,
			}
		super(ErrorResponse, self).__init__(d)


class ServiceException(Exception):
	"""
	Indicates that a critical error has occurred and that the request can no
	longer be processed. Includes an appropriate ErrorReponse to send to the 
	client.
	"""
	def __init__(self, message, code=ERROR_CODE_GENERAL):
		self.errorResponse = ErrorResponse(message, code)