"""
This is a set of RPC calls using the ZeroRPC library. This is used by the
tonetrainer web project to call Pyrapt's RAPT functionality for use in showing
vocal pitch. See the tonetrainer github repo for more details:
https://github.com/dgaspari/tonetrainer
"""

import zerorpc
from pyrapt import pyrapt


class Pyrapt_RPC(object):
    def raptforfile(self, filename):
        print('running pyrapt.rapt...')
        freq_map = pyrapt.rapt(filename, transition_cost=0.5,
                               doubling_cost=30.0)
        print('finished running pyrapt.rapt...')
        return freq_map

    def testraptforfile(self, filename, tcost, dcost, addconst, vobias, lagwt,
                        freqwt, numcands, istwopass, isfilter):
        print('running TEST pyrapt.rapt...')
        results = pyrapt.rapt_with_nccf(filename, transition_cost=tcost,
                                        doubling_cost=dcost,
                                        additive_constant=addconst,
                                        voicing_bias=vobias, lag_weight=lagwt,
                                        freq_weight=freqwt,
                                        max_hypotheses_per_frame=numcands,
                                        is_two_pass_nccf=istwopass,
                                        is_run_filter=isfilter)
        print('finished running pyrapt.rapt...')
        return results

print('Using ZeroRPC to listen on port 4242 for pitch tracker requests...')
server = zerorpc.Server(Pyrapt_RPC())
# TODO: specify binding in config to control who talks to this server:
server.bind("tcp://0.0.0.0:4242")
server.run()
