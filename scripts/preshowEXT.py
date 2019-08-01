op = op  # pylint:disable=invalid-name,used-before-assignment

class PreShowExtension():

    def __init__(self, my_op):
        self.Me = my_op
        # test6
        self.name = my_op.name
        print('name: ', self.name )
        self.onStop = { 'operator': None, 'method': None }
        self.onStart = { 'operator': None, 'method': None }
        self.createParameters()
        return

    def Test(self):
        self.print('test extension')
        return
    def Start(self, operator=None, method=None):
        fadeIO = op('../fadeIO')
        fadeInSuccess = fadeIO.Fadein()
        return


    def Stop(self, operator=None, method=None):
        fadeIO = op('../fadeIO')
        fadeOutSuccess = fadeIO.Fadeout()
        return

    def createParameters(self):
        self.Me.destroyCustomPars()
        self.page = self.Me.appendCustomPage('Settings')
        start = self.page.appendPulse( 'Start', label = 'Start')
        stop = self.page.appendPulse( 'Stop', label = 'Stop')
        # Fadein = self.page.appendFloat( 'Fadein', label = 'Fadein')
        # Fadeout = self.page.appendFloat( 'Fadeout', label = 'Fadeout')
        return
        
    def OnPulse(self, par):
        if hasattr( self.Me, par.name ):
            function = getattr( self.Me, par.name )
            if callable( function ):
                function()
            else:
                self.print( 'attr is not callable' )
        return

    def OnValueChange(self, par):
        self.Me.store( par.name, par.eval() )
        if hasattr( self.Me, par.name ):
            function = getattr( self.Me, par.name )
            if callable( function ):
                function()
            else:
                self.print( 'attr is not callable' )
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