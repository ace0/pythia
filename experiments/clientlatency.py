#!/usr/bin/eval python
"""
Client-latency measurements for the Pythia service using the pyrelic 
implementation.
"""
from pyrelic import vpop
from pyrelic import pbc
from pyrelic.common import *
from httpJson import *

server = "http://localhost:8000"
evalUrl = server + "/pythia/eval"

m = "This is my next"
t = "super+secret_tweak"
w = "super_secret+client-id"


def eval():
    """
    Request a PRF eval from the Pythia server
    """
    # Prepare the message
    r,x = vpop.blind(m)
    xWrap = vpop.wrap(x)

    params = { "x":xWrap, "w":w, "t":t }

    # Submit the request and do a quick-check on the response
    response = fetch(evalUrl, params)

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

eval()