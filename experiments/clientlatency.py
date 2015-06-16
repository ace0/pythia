#!/usr/bin/eval python
"""
Client-latency measurements for the Pythia service using the pyrelic 
implementation.
"""
from pyrelic import vpop
from pyrelic import pbc
from pyrelic.common import *
from httpJson import *
import argparse, sys
from timeit import timeit

warmupIterations = 100

m = "This is my next"
t = "super+secret_tweak"
w = "super_secret+client-id"


def eval(url, m, t, w, keepalive):
    """
    Request a PRF eval from the Pythia server
    """
    # Prepare the message
    r,x = vpop.blind(m)
    xWrap = vpop.wrap(x)

    # Submit the request and do a quick-check on the response
    response = fetch(url, { "x":xWrap, "w":w, "t":t }, keepalive=keepalive)

    # Extract fields from the response
    y,p,c,u = [ response[name] for name in ["y","p","c","u" ] ]
    y = vpop.unwrapY(y)
    p = vpop.unwrapP(p)
    c = vpop.unwrapC(c)
    u = vpop.unwrapU(u)

    # Verify the proof
    vpop.verify(x, t, y, (p,c,u), errorOnFail=True)

    # Compute the final result
    z = vpop.deblind(r,y)


def main():
    """
    Parse command-line options for clientlatency
    """
    parser = argparse.ArgumentParser(
        description='Time the latency for Pythia client eval requests')

    parser.add_argument('iterations', type=int,
                       help='Number of eval requests to issue')

    parser.add_argument('url', 
                       help='URL to Pythia eval service. Example: https://remote-crypto.io/pythia/eval')

    parser.add_argument('--cold', action='store_false', dest='keepalive',
                       help='Disable HTTP KeepAlive and make cold connections each time.')


    args = parser.parse_args(sys.argv[1:])

    timetest(args.iterations, args.url, args.keepalive)


def timetest(iterations, url, keepalive):
    """
    Runs eval through timeit and reports the results.
    """
    def warmup():
      for _ in range(warmupIterations): 
        eval(url, m, t, w, keepalive)

    # Indicate that we're starting
    print "{}x {} keepalive:{}".format(iterations, url, keepalive)

    # Run eval and compute mean execution time
    latency = timeit(lambda: eval(url, m, t, w, keepalive), 
            setup=warmup, number=iterations)
    meanMs = latency/iterations * 1000

    # Print the result
    print "{:4.3f} ms (mean)".format(meanMs)


# Run!
if __name__ == "__main__":
    main()