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

# @profile
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

@profile
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
