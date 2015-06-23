"""
Profiling script that runs client and server requests so we can capture
individual timings using the line_profiler library.
"""

# Import django settings.
import os, sys
sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'cryptoService.settings'

import argparse, json
from viewsprofiler import evalVpop, evalVprf, evalBls
from pyrelic import vprf, bls, vpop
from crypto import secureRandom
from settings import dp

w,t,m = secureRandom(), secureRandom(), secureRandom()


# Dummy request object
class dummyRequest(object):
    def __init__(self,w,t,x):
        self.GET = { 'w':w, 't':t, 'x':x }

@profile
def clientEval(prf, serverEval):
    """
    Runs a client-driven eval request using the provided @prf module and
    the @serverEval function.
    """
    # Make an eval request
    r,x = prf.blind(m)
    xWrap = prf.wrap(x)

    # Create a request object and query the server
    request = dummyRequest(w,t,x=xWrap)
    response = serverEval(request)

    # Check the response
    if response.status_code != 200:
        raise Exception("Server Error: HTTP response code {}".format(response.status_code))

    # Decode the JSON response into a dictionary
    r = json.loads(response.content)

    # Deserialize the items needed to verify the proof.
    y = prf.unwrapY(r["y"])
    p = prf.unwrapP(r["p"])

    # BLS proofs omit c,u
    if "c" in r and "u" in r:
        (c,u) = (prf.unwrapC(r["c"]), prf.unwrapU(r["u"]) )
    else:
        (c,u) = (None,None)

    pi = (p,c,u)

    # Test the proof
    prf.verify(x, t, y, pi, errorOnFail=True)


def repeat(func, n):
    for _ in range(n):
        func()

# A table mapping PRF names to prf modules
prfTable = { "vprf":vprf, "bls":bls, "vpop":vpop }
serverEvalTable = { "vprf":evalVprf, "bls":evalBls, "vpop":evalVpop}

def main():
    parser = argparse.ArgumentParser(description="Profiling tool for client-server eval queries.")
    parser.add_argument("N", help="iterations", type=int)
    parser.add_argument("prf", help="Name of the PRF to run eval() against", 
        choices=["vprf", "bls", "vpop"] )
    args = parser.parse_args()

    # Select the PRF module and the corresponding server function
    prf = prfTable[args.prf]
    serverEval = serverEvalTable[args.prf]
    funcUnderTest = lambda: clientEval(prf, serverEval)

    # Run the eval request repeatedly
    repeat(funcUnderTest, args.N)


# Run!
if __name__ == "__main__":
    main()


