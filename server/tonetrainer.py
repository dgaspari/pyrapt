"""
This is a set of RPC calls using the ZeroRPC library. This is used by the
tonetrainer web project to call Pyrapt's RAPT functionality for use in showing
vocal pitch. See the tonetrainer github repo for more details:
https://github.com/dgaspari/tonetrainer
"""

import zerorpc
# from pyrapt import pyrapt


class Pyrapt_RPC(object):
    def hello(self, name):
        print('hello method invoked')
        return "Hello, %s" % name


server = zerorpc.Server(Pyrapt_RPC())
# TODO: specify binding in config to control who talks to this server:
server.bind("tcp://0.0.0.0:4242")
server.run()
