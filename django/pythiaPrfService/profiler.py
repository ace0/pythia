# Import project settings to appease Django
import os, sys
sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'cryptoService.settings'
from viewsProfiler import *

ITERATIONS=10000

class dummyRequest(object):
    def __init__(self,w,t,m):
        self.GET = { 'w':w, 't':t, 'm':m }


blsMessage = "2:XVQ3420DnzidW_Dnveda9yPHvUvGzmsuPwlR3Ey0GI4wF2xO-tdQ5qiS4aqCif72k7Fv1HWRFayFurLHC%5CUuqaBPbP-xogLFiu0S0Aye0syTCtS3RXBTWLkQzHHJOuAFwXPzUDgbrVBYH16W5JfaN2HBEy_9LnMl7b1In-08BjbfjxrpVOkBIjtx_S%5CcIlOLHovQvTRUVxYXjV-HBv2a7zri1ENkHOD_jj"
message = "lkjasdf;lkjas;dlfkj;alskdf;lkamsd;lfkjopaif;asdnf"

serviceTable = { "query-ecc":  queryEcc, 
                 "oquery-ecc": oqueryEcc, 
                 "query-bls":  queryBls, 
                 "oquery-bls": oqueryBls
             }

@profile
def runTopLevel(queryFunc, request, n):
    for _ in range(n):
        queryFunc(request)

def main():
    # Parse cmd line args
    n, service = int(sys.argv[1]), sys.argv[2]

    # Grab the query function
    queryFunc = serviceTable[service]

    # Select the message and build the request object.
    if queryFunc == oqueryBls:
        msg = blsMessage
    else:
        msg = message
    
    request = dummyRequest("12341234", "lkjasldkfj", msg)

    # Run and profile!
    runTopLevel(queryFunc, request, n)


# Run!
if __name__ == "__main__":
    main()
