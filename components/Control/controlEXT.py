op = op  # pylint:disable=invalid-name,used-before-assignment
root = root  # pylint:disable=invalid-name,used-before-assignment
parComMod = mod('/IO/base_com/parComMOD')
import socket
import json

class ControlExtension():

    def __init__(self, my_op):
        self.Me = my_op
        # test
        self.name = my_op.name
        print('name: ', self.name )
        self.com = op('/IO/base_com')
        self.children = self.Me.findChildren(type=containerCOMP, maxDepth=2)
        # self.print(self.children)
        self.Msg = {}
        return
    
    def OnReceive(self, dat, rowIndex, message, bytes, peer):
        json_msg = json.loads(message)
		
        if json_msg.get( 'op_name', None ):
            self.handleOpNameMsg(json_msg)

        return
    def handleOpNameMsg(self, msg):
        for child in self.children:
            if child.name.find( msg.get( 'op_name', None ) ) != -1:
                self.Msg = msg

        return

    def OnPulse(self, par):
        if hasattr( self.Me, par.name ):
            function = getattr( self.Me, par.name )
            if callable( function ):
                function()
            # else:
            #     self.print( 'attr is not callable' )
        return

    def OnValueChange(self, par):
        self.Me.store( par.name, par.eval() )
        if hasattr( self.Me, par.name ):
            function = getattr( self.Me, par.name )
            if callable( function ):
                function()
            # else:
            #     self.print( 'attr is not callable' )
        return

    def print(self, message):
        print( self.name + ': ', message )
        return

    # method to call callbacks
    def callback(self, config):
        if config['operator'] and config['method']:
            if hasattr( config['operator'], config['method'] ):
                function = getattr(config['operator'], config['method'])
                if callable( function ):
                    function()
            else:
                self.print('FADEIO: callback no fire')
                self.print('operator: ' + config['operator'])
                self.print('method: ' + config['method'])
        return