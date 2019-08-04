op = op  # pylint:disable=invalid-name,used-before-assignment
root = root  # pylint:disable=invalid-name,used-before-assignment

class SceneExtension():

    def __init__(self, my_op):
        self.Me = my_op
        # test
        
        self.onStop = { 'operator': None, 'method': None }
        self.onStart = { 'operator': None, 'method': None }
        self.Me.store( 'Output', op('../out1') )
        self.springs = []
        self.GetSprings()
        self.name = my_op.name
        self.print('init')
        # self.Page = self.Me.customPages[0]
        self.States = [ 'Starting', 'Started', 'Stopping', 'Stopped' ]
        self.State = self.Me.fetch( 'State' )
        self.Me.par.State.menuLabels = self.States
        self.Me.par.State.menuNames = self.States
        self.onStopped = { 'operator': None, 'method': None }
        self.onStarted = { 'operator': None, 'method': None }
        self.fadeIO = op('../fadeIO')

        self.Index = -1
        self.perform = op('/Perform')
        if len( self.perform.fetch('Scenes') ) > 0:
            if self.name != 'blank':
                self.Index = self.perform.fetch('Scenes').index(self.Me)
            else:
                self.Index = -1
        self.Me.par.Index.readOnly = True

        self.selInputs = []
        self.GetSelInputs()
        self.print('init')

        if self.name == 'blank' and root.var('Mode') != 'Perform':
            self.fadeIO.ImmediateIn()
            self.OnFadeIn()
        elif root.var('Mode') == 'Perform' and self.perform.fetch('CurrentScene') == self.Me:
            self.fadeIO.ImmediateIn()
            self.OnFadeIn()
        else:
            self.fadeIO.ImmediateOut()
            self.finishStopping()
        return

    def Test(self):
        self.print('test scene extension')
        return
    def Start(self, operator=None, method=None, inTime=None, outTime=None):
        # method that starts the scene
        if self.State == 'Stopped':
            self.State = 'Starting' 
        # if not self.Me.fetch( 'Starting' ) and not self.Me.fetch( 'Started' ):
        #     self.Me.store( 'Stopped', False )
        #     self.Me.store( 'Starting', True )
            self.print('starting')
            self.onStarted = { 'operator': operator, 'method': method }
            # - reset physics
            self.enableNodes()
            # - reinit the scene in any other ways
            # - update inited state in storage
            # - fade in scene from black
            fadeIO = self.fadeIO
            fadeInSuccess = fadeIO.Fadein(self, 'OnFadeIn', self.Me.par.Fadein)
            if fadeInSuccess == False:
                self.OnFadeIn()
            return True
        else:
            return False
        return

    def Stop(self, operator=None, method=None):
        if self.State == 'Started':
            self.State = 'Stopping' 

            self.print('stopping')
            self.onStopped = { 'operator': operator, 'method': method }
            # method that starts the scene
            # - fade out scene from black
            fadeIO = self.fadeIO
            fadeOutSuccess = fadeIO.Fadeout(self, 'OnFadeOut', self.Me.par.Fadeout)
            if fadeOutSuccess == False:
                self.OnFadeOut()

            return True
        else:
            return False

        return

    def OnFadeIn(self):
        self.print('onfadein')
        # - update started state in storage
        # self.Me.store( 'Started', True )
        # self.Me.store( 'Starting', False )
        # self.Me.store( 'Stopped', False )
        self.State = 'Started'
        # - run a 'started' callback
        self.callback( self.onStarted )
        return

    def OnFadeOut(self):
        self.print('onfadeout')
        self.finishStopping()
        return
    
    def finishStopping(self):
        # - stop any other processing
        self.disableNodes()
        # - update states in storage
        # self.Me.store( 'Stopping', False )
        # self.Me.store( 'Stopped', True )
        self.State = 'Stopped' 
        # - run stopped callback
        self.callback( self.onStopped )
        return


    def disableNodes(self):
        op('../post').par.Bypass = True
        for node in self.springs:
            node.bypass = True
        for node in self.selInputs:
            node.bypass = True
        return

    def enableNodes(self):
        op('../post').par.Bypass = False
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
        
    def Lockfades(self):
        self.Me.par.Fadein.readOnly = self.Me.par.Lockfades.val
        self.Me.par.Fadeout.readOnly = self.Me.par.Lockfades.val
        return

    # def State(self, value = None):
    #     if value is None:
    #         return self.Me.fetch('State')
    #     else:
    #         self.Me.store( 'State', value )
    #         self.Me.par.State.val = value
    #     return

    @property
    def State(self):
        return self.Me.fetch('State')
    
    @State.setter
    def State(self, val):
        if val in self.States:
            self.Me.store( 'State', val )
            self.Me.par.State.val = val

    @property
    def Index(self):
        return self.Me.fetch( 'Index' )
    
    @Index.setter
    def Index(self, val):
        self.Me.store( 'Index', val )
        self.Me.par.Index.val = val
        
    def OnPulse(self, par):
        if hasattr( self.Me, par.name ):
            function = getattr( self.Me, par.name )
            function()
        return

    def OnValueChange(self, par):
        self.Me.store( par.name, par.eval() )
        if hasattr( self.Me, par.name ):
            function = getattr( self.Me, par.name )
            if callable( function ):
                function()
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