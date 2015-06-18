#!/usr/bin/eval python
"""
Client-latency measurements for the Pythia service using the pyrelic 
implementation.
"""
from pyrelic import pbc, vpop, vprf, bls
from pyrelic.common import *
from httpJson import *
import argparse, sys
from timeit import timeit

warmupIterations = 100

w = "super_secret+client-id"
t = "super+secret_tweak"
m = "This is my next"


# A table mapping service name to the pyrelic module
serviceTable = {
    "vpop" : vpop, 
    "vprf" : vprf,
    "bls"  : bls
}

# A table mapping service name to url
urlTable = {
    "vpop" : "eval",
    "vprf" : "eval-unb",
    "bls"  : "eval-bls"
}


def eval(prf, url, w, t, m, keepalive, proof):
    """
    Request a PRF eval from the Pythia server
    """
    # Prepare the message
    r,x = prf.blind(m)
    xWrap = prf.wrap(x)

    # Put our query arguments into a dictionary.
    query = { "x":xWrap, "w":w, "t":t }

    # Append skipproof if proofs are disabled
    if not proof:
        query["skipproof"] = True

    # Submit the request and do a quick-check on the response
    response = fetch(url, query, keepalive=keepalive)

    # Extract fields from the response
    p,c,u = None,None,None
    y = prf.unwrapY(response["y"])

    if proof:
        verify(prf, x, t, y, response)

    # Compute the final result
    z = prf.deblind(r,y)


def verify(prf, x, t, y, response):
    """
    Verify proof from the response
    """
    p = prf.unwrapP(response["p"]) 

    # BLS service doesn't include c,u in the response
    if "c" in response and "u" in response:
        c,u = prf.unwrapC(response["c"]), prf.unwrapU(response["u"]) 
    else: 
        c,u = None,None

    # Verify the proof
    prf.verify(x, t, y, (p,c,u), errorOnFail=True)


def main():
    """
    Parse command-line options for clientlatency
    """
    parser = argparse.ArgumentParser(
        description='Time the latency for Pythia client eval requests')

    parser.add_argument('iterations', type=int,
                       help='Number of eval requests to issue')

    parser.add_argument('url', 
                       help='BaseURL to Pythia service. Example: https://remote-crypto.io/pythia')

    parser.add_argument('service', choices=['vpop', 'vprf', 'bls'],
                       help='Determines which PRF service is being used.')

    parser.add_argument('--cold', action='store_false', dest='keepalive',
                       help='Disable HTTP KeepAlive and make cold connections each time.')

    parser.add_argument('--noproof', action='store_false', dest='proof',
                       help='Disable HTTP KeepAlive and make cold connections each time.')

    parser.add_argument('--warmup', type=int,
                       help='Specify the number of warmup iterations')

    # Parse the arguments.
    args = parser.parse_args(sys.argv[1:])

    # Select the PRF and construct the URL
    prf = serviceTable[args.service]
    url = "{}/{}".format(args.url, urlTable[args.service])

    # Time requests and print the results.
    timetest(args.iterations, prf, url, args.keepalive, args.proof)


def timetest(iterations, prf, url, keepalive, proof):
    """
    Runs eval through timeit and reports the results.
    """
    evalFunc = lambda: eval(prf, url, w, t, m, keepalive, proof)

    # For a warmup, call the service a number of times before we start timing
    # latency.
    def warmup():
      for _ in range(warmupIterations): 
        evalFunc()

    # Print the options that we're testing
    print "{}x {} keepalive:{} proof:{}".format(iterations, url, keepalive, 
        proof)

    # Run eval and compute mean execution time
    latency = timeit(evalFunc, setup=warmup, number=iterations)
    meanMs = latency/iterations * 1000

    # Print the result
    print "{:4.3f} ms (mean)".format(meanMs)


# Run!
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print "Error:",e