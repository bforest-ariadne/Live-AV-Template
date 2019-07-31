class SceneExtension():

    def __init__(self, my_op):
        self.Me = my_op
        # test4
        self.onStop = { 'operator': None, 'method': None }
        self.onStart = { 'operator': None, 'method': None }
        self.Me.store( 'Output', op('../out1') )
        self.springs = []
        self.GetSprings()
        self.name = my_op.name

        self.selInputs = []
        self.GetSelInputs()
        return

    def Test(self):
        self.print('test scene extension')
        return
    def Start(self, operator=None, method=None):
        # method that starts the scene
        if not self.Me.fetch( 'Starting' ) and not self.Me.fetch( 'Started' ):
            self.Me.store( 'Stopped', False )
            self.Me.store( 'Starting', True )
            self.print('starting')
            # - reset physics
            self.enableNodes()
            # - reinit the scene in any other ways
            # - update inited state in storage
            # - fade in scene from black
            fadeIO = op('../fadeIO')
            fadeIO.Fadein(self, 'OnFadeIn')
            # - update started state in storage
            # - run a 'started' callback
        return

    def Stop(self, operator=None, method=None):
        if not self.Me.fetch( 'Stopping' ) and not self.Me.fetch( 'Stopped' ):
            self.Me.store( 'Stopping', True )
            self.Me.store( 'Started', False )

            self.print('stopping')
            # method that starts the scene
            # - fade out scene from black
            fadeIO = op('../fadeIO')
            fadeIO.Fadeout(self, 'OnFadeOut')
            # - stop any other processing
            # - update states in storage

            # - run stopped callback

        return

    def OnFadeIn(self):
        self.Me.store( 'Started', True )
        self.Me.store( 'Starting', False )
        self.Me.store( 'Stopped', False )
        return

    def OnFadeOut(self):
        self.finishStopping()
        return
    
    def finishStopping(self):
        self.disableNodes()
        self.Me.store( 'Stopping', False )
        self.Me.store( 'Stopped', True )
        return

    def disableNodes(self):
        for node in self.springs:
            node.bypass = True
        for node in self.selInputs:
            node.bypass = True
        return

    def enableNodes(self):
        for node in self.springs:
            node.bypass = False
        for node in self.selInputs:
            node.bypass = False
        return

    def GetSprings(self):
        findSpring = op('opfind_spring')
        springPaths = findSpring.cells('spring*', 'path')
        self.springs = []
        for paths in springPaths:    
            self.springs.append( op( paths ))
        return
    
    def GetSelInputs(self):
        findSelInput = op('opfind_selInput')
        selInputPaths = findSelInput.cells('select*', 'path')
        self.selInputs = []
        for paths in selInputPaths:    
            self.selInputs.append( op( paths ))
        return
        
    def OnPulse(self, par):
        if hasattr( self.Me, par.name ):
            function = getattr( self.Me, par.name )
            function()
        return

    def OnValueChange(self, par):
        self.Me.store( par.name, par.eval() )
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
                self.print('operator: ', config['operator'])
                self.print('method: ', config['method'])
        return