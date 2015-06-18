"""
Server implementation of the Pythia PRF service.
"""
from response import *
from datastore import *
from settings import *
from datetime import datetime
from pyrelic import vpop, vprf, bls

# Entry points for each PRF variant.
evalVpop = lambda request: eval(request, vpop) 
evalVprf = lambda request: eval(request, vprf) 
evalBls = lambda request: eval(request, bls) 


def eval(request, prf):
    """
    Process eval @request using @prf. This is a common routine for evalVpop, 
    evalVprf (also called eval-unb), and evalBls.
    """
    required = ["w", "t", "x"]
    optional = ["skid", "skipproof"]

    # Parse and validate parameters from the request.
    try:
        w,t,x,skid,skipproof = \
            getParams(request, required, optional)

    except ServiceException as e:
        return e.errorResponse

    # Include a proof unless there's a specific request to omit it.
    proof = not skipproof

    # Check rate-limits
    if not noteQuery(t):
        return ErrorResponse(ERROR_EXCEEDED_QUERY_LIMIT, ERROR_CODE_QUERY_LIMIT)

    # Run eval and send the response as JSON
    return JsonResponse(runEval(prf,w,t,x,proof))


def runEval(prf,w,t,x,proof):
    """
    Runs the Pythia eval function using @prf.
    """
    # Deserialize parameter x
    x = prf.unwrapX(x)

    # Get the (secret) state table entry assigned to this w
    s = getStateEntry(w)
    y,kw,tTilde = prf.eval(w,t,x,SERVER_SECRET_KEY,s)

    # Package our results into a dictionary d
    d = { "y" : prf.wrap(y),
          "message" : "Thank you for using the Pythia PRF service for all your password hardening needs", 
        }

    # Generate a proof, if requested. Note that BLS eval queries don't have any
    # proof beyond
    if proof:
        p,c,u = prf.prove(x,tTilde,kw,y)
        d.update( { "p": prf.wrap(p) } )

        # The BLS protocol doesn't have items c,u
        if c and u:
            d.update( 
                { "c": prf.wrap(c),
                  "u": prf.wrap(u)
                 } )

    return d


# def updateRequest(request):
#     """
#     A client can request to update their ID w to a new ID wPrime.
#     """
#     try:
#         w = getParams(request, ["w"])
#     except ServiceException as e:
#         return e.errorResponse

#     # Generate and store a verification code.
#     vcode = secureRandom()
#     writeVerificationCode(w, vcode)

#     # TODO: email verification code. For now, emit the vcode and we can 
#     # copy/paste it into the client for testing.
#     print "w: {}\tverification code: {}".format(w, vcode)

#     d = { "status" : "OK", 
#           "message": "Verification code sent to email address associated "\
#            "with this client ID w" }
#     return JsonResponse(d)


# def updateBegin(request, checkWprime=False):
#     """
#     Initiates a client ID w update. Client provides a new client ID, 
#     wPrime, and a verification code as proof-of-ownership of the client ID. 
#     Sends an update value delta that permits the client to transition existing
#     values to the new ID wPrime.
#     """
#     # TODO: Permit updates for other groups. For now, assume ECC.
#     prf = prfEcc

#     # Grab parameters
#     try:
#         w,wPrime,vcode = getParams(request, ["w", "wprime", "v"])
#     except ServiceException as e:
#         return e.errorResponse

#     # Check the verification code.
#     if not checkVcode(w, vcode):
#         return ErrorResponse("Verification code is invalid.")

#     # Verify wPrime not in use
#     # NOTE: this is necessary to prevent a DoS attack by an adversary that 
#     #       has stolen a client ID wPrime and is trying to use the update 
#     #       process (on a new w that she owns) to invalidate an existing wPrime.
#     if checkWprime and checkStateEntry(wPrime):
#         return ErrorResponse("wPrime value is not valid.")

#     # Generate delta
#     z = getStateEntry(w)
#     zPrime = getStateEntry(wPrime)
#     delta, pPrime = prf.deltaSlow(w=w, sk=SERVER_SECRET_KEY, z=z, 
#         wPrime=wPrime, skPrime=SERVER_SECRET_KEY, zPrime=zPrime)

#     # Send the results
#     d = { "delta": delta, "pPrime": pPrime }
#     return JsonResponse(d)


# def updateComplete(request, finalize=False):
#     """
#     Finalizes a client ID update by erasing the state entry for @w. 
#     """
#     try:
#         w,vcode = getParams(request, ["w", "v"])
#     except ServiceException as e:
#         return e.errorResponse

#     # Check the verification code
#     if not checkVcode(w, vcode):
#         return ErrorResponse("Verification code is invalid.")

#     # Remove existing state and verification code.
#     dropStateEntry(w)
#     dropVerificationCode(w)

#     d = { "status" : "OK", "message": "Operation complete" }
#     return JsonResponse(d)


# def checkVcode(w, vcodeClient, skipCheck=True):
#     """
#     Checks a verification code @vcodeClient for @w unless @skipCheck is set for 
#     debugging.
#     """
#     # If debugging
#     if skipCheck:
#         return True

#     # Grab the verification code and validate the client-provided code.
#     vcodeServer = getVerificationCode(w)
#     return (not vcodeServer or vcodeServer != vcodeClient)


def getParams(request, required, optional=None):
    """
    Retrieves named parameters from the HTTP request. @required is a list of
    the named required parameters and @optional is a list of the named
    optional parameters.

    Raises a ServiceException if any required parameters are missing.
    @returns: the parameters as a tuple in the order provided.
    """
    # Grab required items.
    try:
        params = [request.GET[x] for x in required]

    # Complain if any required params are missing.
    except (KeyError):
        e = ERROR_MISSING_PARAMS.format(','.join(required))
        raise ServiceException(e)

    # Grab optional items.
    if optional:
        params.extend([request.GET.get(x, None) for x in optional])

    # Convert any unicode elements to strings and handle None values correctly.
    def toStr(x):
        if x is not None:
            return str(x)
        else:
            return None

    params = [toStr(x) for x in params]

    # Create a tuple if we have one or more parameters.
    if len(params) == 1:
        return params[0]
    else:
        return tuple(params)
