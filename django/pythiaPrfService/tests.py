from django.test import SimpleTestCase
import json
from settings import dp
from pyrelic import vpop


class VpopEvalTest(SimpleTestCase):
    """
    Tests the eval API.
    """
    urlTemplate = "/pythia/eval?w={}&t={}&x={}"

    # Dummy balues that can be used for testing
    w = "abcdefg0987654321"
    t = "123456789poiuytrewq"
    pw = "super secret pw"


    def checkErrorResponse(self, response):
        """
        Checks that a response with an expected error, gives HTTP 200,
        valid JSON with errorCode and errorMessage fields.
        """
        self.assertEqual(response.status_code, 200)
        r = json.loads(response.content)
        self.assertTrue("errorCode" in r and "errorMessage" in r )


    def check(self, response):
        """
        Basic validation that a response contains the expected fields.
        """
        self.assertEqual(response.status_code, 200)
        r = json.loads(response.content)
        self.assertTrue("y" in r)
        return r


    def testNoParams(self):
        """
        Ensure eval responds with an HTTP 200 and valid JSON repsonse.
        """
        response = self.client.get('/pythia/eval')
        self.checkErrorResponse(response)


    def testWrongParams(self):
        """
        Test a variety of bad params for the eval function.
        """
        response = self.client.get('/pythia/eval?w')
        self.checkErrorResponse(response)

        response = self.client.get('/pythia/eval?w=2341234')
        self.checkErrorResponse(response)

        response = self.client.get('/pythia/eval?w=10987314&t=lkjasdf')
        self.checkErrorResponse(response)

        response = self.client.get('/pythia/eval?w=10987314&x=adsfasdf')
        self.checkErrorResponse(response)

        response = self.client.get('/pythia/eval?t=10987314&x=adsfasdf')
        self.checkErrorResponse(response)



    def testEvalSimple(self):
        """
        Simple test of the eval function
        """
        r,x = vpop.blind(VpopEvalTest.pw)
        x = vpop.wrap(x)

        response = self.client.get(VpopEvalTest.urlTemplate.format(VpopEvalTest.w,VpopEvalTest.t,x))
        d = self.check(response)

        y = vpop.unwrapGt(str(d["y"]))
        z = vpop.deblind(r,y)


    def testEvalStable(self):
        """
        Runs eval a number of times and verifies thatL intermediate results
        differ (because blinding is randomized), and final result is always
        the same.
        """
        y1,z1 = self.runClientEval(VpopEvalTest.w, VpopEvalTest.t, VpopEvalTest.pw)
        y2,z2 = self.runClientEval(VpopEvalTest.w, VpopEvalTest.t, VpopEvalTest.pw)

        # Verify that the intermediate results differ
        self.assertNotEqual(y1,y2)

        # But final results are the same
        self.assertTrue(z1 == z2 )


    def runClientEval(self,w,t,m):
        """
        Runs the client-side eval() and returns the resulting y and z values.
        """
        # Prepare the message
        r,x = vpop.blind(m)
        x = vpop.wrap(x)

        # Submit the request and do a quick-check on the response
        response = self.client.get(VpopEvalTest.urlTemplate.format(w,t,x))
        d = self.check(response)

        # Compute the final result
        y = vpop.unwrapGt(str(d["y"]))
        z = vpop.deblind(r,y)

        return y,z


    def testProofOmmitted(self):
        """
        Requests eval with proof omitted.
        """
        # Request eval with no proof
        _, url = self.getUrl()
        response = self.client.get(url + "&skipproof=true")

        # Check the response and ensure there is no proof included.
        r = json.loads(response.content)
        self.assertTrue( "p" not in r and "c" not in r and "u" not in r)


    def parseResponse(self, response):
        """
        Verifies the response code is HTTP 200 and parses the JSON response.
        @returns a dictionary of the response contents.
        """
        self.assertEqual(response.status_code, 200)
        return json.loads(response.content)


    def testProofRandomized(self):
        """
        Checks to ensure that the same request gets a different proof each time
        """
        # Make two requests with the same URL.
        _, url = self.getUrl()
        r1 = self.parseResponse(self.client.get(url))
        r2 = self.parseResponse(self.client.get(url))

        # Test that the pubkey p is the same, but c,u are different.
        self.assertEqual(r1["p"], r2["p"])
        self.assertNotEqual(r1["c"], r2["u"])
        self.assertNotEqual(r1["u"], r2["u"])


    def testProof(self):
        """
        Ensures the proof is valid.
        """
        # Make an eval request
        r,x = vpop.blind(VpopEvalTest.pw)
        xWrap = vpop.wrap(x)
        url = VpopEvalTest.urlTemplate.format(VpopEvalTest.w,VpopEvalTest.t,xWrap)
        r = self.parseResponse(self.client.get(url))

        # Deserialize the items needed to verify the proof.
        y = vpop.unwrapY(r["y"])
        pi = (vpop.unwrapP(r["p"]), vpop.unwrapC(r["c"]), vpop.unwrapU(r["u"]) )

        # Test the proof
        self.assertTrue( vpop.verify(x, VpopEvalTest.t, y, pi) )


    def getUrl(self):
        """
        Helper function: gets a URL using the standard VpopEvalTest w,t,pw 
        parameters with a freshly blinded value x.
        @returns r, url  where r is the value required for deblinding.
        """
        r,x = vpop.blind(VpopEvalTest.pw)
        x = vpop.wrap(x)
        return r, VpopEvalTest.urlTemplate.format(VpopEvalTest.w,VpopEvalTest.t,x)

from pyrelic import vprf
from pyrelic.pbc import G1Element
from crypto import *

class UnbEvalTest(SimpleTestCase):
    """
    Tests the eval API for unblinded PRF implementation.
    """

    def setUp(self):        
        self.urlTemplate = "/pythia/eval-unb?w={}&t={}&x={}"
    
        # Dummy values that can be used for testing
        self.w = "abcdefg0987654321"
        self.t = "123456789poiuytrewq"
        self.pw = "super secret pw"
        self.salt = secureRandom()
        self.x = sha(self.salt, self.pw)
        self.standardUrl = self.urlTemplate.format(self.w, self.t, self.x)


    def parse(self, response):
        """
        Verify that the response is HTTP status 200 and parse the response
        as JSON.
        """
        self.assertEqual(response.status_code, 200)
        d = json.loads(response.content)

        # Convert unicode keys into strings.
        return dict({ (str(k), v) for k,v in d.iteritems() })


    def testEvalSimple(self):
        """
        Simple test of the eval function
        """
        # Query the eval function
        response = self.client.get(self.standardUrl)
        d = self.parse(response)

        # Verify that we got a response of the correct type
        self.assertTrue( "y" in d )
        y = vprf.unwrapY(d["y"])
        self.assertTrue(isinstance(y, G1Element))


    def testEvalStable(self):
        """
        Runs eval a number of times and verifies thatL intermediate results
        differ (because blinding is randomized), and final result is always
        the same.
        """
        y1, p1, c1, u1 = self.runClientEval()
        y2, p2, c2, u2 = self.runClientEval()

        # Verify that result and pubkey are the same
        self.assertEqual(y1, y2)
        self.assertEqual(p1, p2)

        # But the proof is randomized
        self.assertNotEqual(c1, c2)
        self.assertNotEqual(u1, u2)


    def runClientEval(self):
        """
        Runs the client-side eval() and returns the resulting values
        after they've been unwrapped.
        """
        # Query the eval function
        response = self.client.get(self.standardUrl)
        d = self.parse(response)

        # Unwrap the results.
        return (vprf.unwrapY(d["y"]), vprf.unwrapP(d["p"]), 
                vprf.unwrapC(d["c"]), vprf.unwrapU(d["u"]) )


    def testProofOmmitted(self):
        """
        Requests eval with proof omitted.
        """
        # Request eval with no proof
        response = self.client.get(self.standardUrl + "&skipproof=true")

        # Check the response and ensure there is no proof included.
        r = json.loads(response.content)
        self.assertTrue( "p" not in r and "c" not in r and "u" not in r)


    def parseResponse(self, response):
        """
        Verifies the response code is HTTP 200 and parses the JSON response.
        @returns a dictionary of the response contents.
        """
        self.assertEqual(response.status_code, 200)
        return json.loads(response.content)


    def testProof(self):
        """
        Ensures the proof is valid.
        """
        # Query eval function
        y,p,c,u = self.runClientEval()

        # Test the proof
        self.assertTrue( vprf.verify(self.x, self.t, y, (p,c,u), 
                errorOnFail=False) )
