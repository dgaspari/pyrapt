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
        freq_map = pyrapt.rapt(filename)
        print('finished running pyrapt.rapt...')
        return freq_map

    def raptforblob(self, blobdata):
        # this takes a blob from javascript (base 64 encoded?) - need
        # to convert to a file object temporarily, read as wav, then
        # return frequency data:
        print('received request for blob data:')
        print(blobdata)
        return [1, 2, 3, 4, 5]

server = zerorpc.Server(Pyrapt_RPC())
# TODO: specify binding in config to control who talks to this server:
server.bind("tcp://0.0.0.0:4242")
server.run()
