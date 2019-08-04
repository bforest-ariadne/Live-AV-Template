op = op  # pylint:disable=invalid-name,used-before-assignment

class PerformExtension():

    def __init__(self, my_op):
        self.Me = my_op
        self.name = my_op.name
        print('name: ', self.name )
        #test
        self.input = op('../input')
        self.Me.store( 'Input', op('../input') )
        self.onStop = { 'operator': None, 'method': None }
        self.onStart = { 'operator': None, 'method': None }
        self.onSceneChange = { 'operator': None, 'method': None }
        self.nodes = []
        self.scenes = []
        self.States = [ 'Starting', 'Started', 'Stopping', 'Stopped' ]
        self.State = self.Me.fetch( 'State' )
        self.BlankScene = op('../blank')
        self.GetScenes()
        if self.CurrentScene() not in self.scenes:
            self.CurrentScene( op('../scene1') )
        self.print( 'current scene: ' + self.CurrentScene().name )
        self.PreviousScene = None
        if root.var('Mode') == 'Perform':
            if self.State == 'Started':
                self.StartCurrentScene()
                if self.Me.fetch( 'Nextsceneindex' ) == self.CurrentScene().Index:
                    self.Me.store( 'Nextsceneindex', self.CurrentScene().Index + 1 )
            else:
                self.Start()
        else:
            self.print('not perform mode')
            self.Stop()
        return


    def Test(self):
        self.print('test extension')
        return
    def Start(self, operator=None, method=None, index=None, name=None):
        if self.State == 'Stopped':
            self.State = 'Starting' 

            self.print('starting')
            self.onStarted = { 'operator': operator, 'method': method }

            if index is None and name is None:
                index = self.getNextIndex()
                if self.PreviousScene:
                    if self.PreviousScene.Index > -1:
                        index = self.PreviousScene.Index
            self.ChangeScene( index = index, operator = self, method = 'OnStart' )

        return

    def Stop(self, operator=None, method=None):
        if self.State == 'Started':
            self.State = 'Stopping' 

            self.print('stopping')
            self.onStopped = { 'operator': operator, 'method': method }

            self.ChangeScene( blank = True, operator = self, method = 'OnStop')
        
        return
    def getNextIndex(self):
        return self.Me.fetch( 'Nextsceneindex' )

    def Nextsceneindex(self):
        index = self.Me.fetch( 'Nextsceneindex' )
        nextScene = self.scenes[index]
        self.Me.par.Fadein.val = nextScene.par.Fadein.val
        self.Me.par.Fadeout.val = self.CurrentScene().par.Fadeout.val
    
    def Changetonextscene(self):
        return self.ChangeScene( self.getNextIndex() )

    def ChangeScene(self, index=None, name='scene1', blank=False, operator=None, method=None, fadein=None, fadeout=None):
        self.onSceneChange = { 'operator': None, 'method': None }
        self.onSceneChange = { 'operator': operator, 'method': method }
        fadeinArg = False
        fadeoutArg = False

        if fadein is not None:
            if type(fadein) == int:
                float(fadein)
            if type(fadein) == float:
                self.Fadein( fadein )
                fadeinArg = True
            else:
                self.print( 'wrong type for Fadein' )
        if fadeout is not None:
            if type(fadeout) == int:
                float(fadeout)
            if type(fadeout) == float:
                self.Fadeout( fadeout )
                fadeoutArg = True
            else:
                self.print( 'wrong type for Fadeout' )
        
        if blank:
            self.newScene = self.BlankScene
            return self.startSceneChange()

        self.newScene = False
        if type(index) == int:
            # self.print( self.scenes[index].name )
            if index >= len( self.scenes ):
                return False
            self.newScene = self.scenes[index]
        elif type( index ) == str and index.isnumeric():
            # self.print( self.scenes[ int(index) ].name )
            if int(index) >= len( self.scenes ):
                return False
            self.newScene = self.scenes[ int(index) ]
        elif type(name) == str:
            for scene in self.scenes:
                if scene.name == name:
                    # self.print( scene.name )
                    self.newScene = scene
        if self.newScene:
            if self.Fades() or fadeinArg:
                if not self.newScene.par.Lockfades.eval():
                    self.newScene.par.Fadein = self.Me.fetch('Fadein')
            if self.Fades() or fadeoutArg:
                if not self.CurrentScene().par.Lockfades.eval():
                    self.CurrentScene().par.Fadeout = self.Me.fetch('Fadeout')

            return self.startSceneChange()
        return False
    
    def startSceneChange(self):
        # stop current scene -
        self.print( 'stopping current scene ' + self.CurrentScene().name )
        if self.CurrentScene().State != 'Stopped':
            self.CurrentScene().Stop( self, 'ContinueSceneChange' )
        else:
            self.print( self.CurrentScene().name + ' was not Stopped ')
            self.ContinueSceneChange()
        return True

    def StartCurrentScene(self):
        # self.GetScenes()
        self.print( 'StartCurrentScene init' )

        startedCount = 0
        startedScenes = []
        for scene in self.scenes:
            if scene.State == 'Started':
                startedScenes.append( scene )
        startedCount = len( startedScenes )
        self.print('startedCount: ' + str(startedCount) )
        if startedCount == 1 and startedScenes[0] == self.CurrentScene():
            if self.CurrentScene().Start() == "Started":
                return True
        else:
            self.stopAllScenes()
            self.disconnectAllScenes()
            # self.CurrentScene( self.scenes[0] )
            self.CurrentScene().outputConnectors[0].connect( self.input )
            self.Me.par.Currentsceneindex = self.CurrentScene().Index
            if self.CurrentScene().State == 'Stopped':
                self.CurrentScene().Start( self, 'OnCurrentSceneStart' )
            # elif self.CurrentScene().State == 'Stopping':
            #     self.CurrentScene().onStopped = { 'operator': self.CurrentScene(), 'method': 'Start' }
            return 
        return

    def ContinueSceneChange(self):
        self.print( 'continueSceneChange' )
        self.Me.store('SceneStart', False )
        # disconnect on stop
        self.CurrentScene().outputConnectors[0].disconnect()
        # change current scene to previous scene
        self.PreviousScene = self.CurrentScene()
        # set new scene to current scene
        self.CurrentScene( self.newScene )
        self.Me.par.Currentsceneindex = self.newScene.Index
        # connect current scene to input
        self.CurrentScene().outputConnectors[0].connect( self.input )
        # start current scene
        # update current scene started on start
        if self.CurrentScene().State != 'Started':
            self.CurrentScene().Start( self, 'OnCurrentSceneStart' )
        else:
            self.OnCurrentSceneStart()
        return

    def OnCurrentSceneStart(self):
        self.Me.store('SceneStart', True )
        self.callback( self.onSceneChange )
        return
    
    def OnStart(self):
        self.print('OnStart')
        # - update started state in storage
        self.State = 'Started'
        # - run a 'started' callback
        self.callback( self.onStarted )
        return

    def OnStop(self):
        self.State = 'Stopped' 
        # - run stopped callback
        self.callback( self.onStopped )
        return

    def stopAllScenes(self):
        print('stop all except', self.CurrentScene().name )
        for scene in self.scenes:
            if scene != self.CurrentScene():
                if scene.State == 'Started':
                    print( scene.name, scene.State )
                    scene.Stop()
        return
    def disconnectAllScenes(self):
        print('dissconnect all except', self.CurrentScene().name )
        for scene in self.scenes:
            if scene != self.CurrentScene():
                scene.outputConnectors[0].disconnect()
        return

    def disableNodes(self):
        for node in self.nodes:
            node.bypass = True
        return

    def enableNodes(self):
        for node in self.nodes:
            node.bypass = False
        return

    def GetScenes(self):
        findScene = op('opfind_scene')
        scenePaths = findScene.cells('scene*', 'path')
        self.scenes = []
        i = 0
        for paths in scenePaths:
            scene = op( paths )
            scene.Index = i
            self.scenes.append( scene )
            i += 1
        self.Me.store( "Scenes", self.scenes )
        self.Me.par.Nextsceneindex.normMax = len(self.scenes) - 1
        self.Me.par.Currentsceneindex.normMax = len(self.scenes) -1
        return

    def CurrentScene(self, value = None):
        if value is None:
            return self.Me.fetch('CurrentScene')
        else:
            self.Me.store( 'CurrentScene', value )
            self.Me.par.Currentsceneindex.val = value.Index
        return value
    
    @property
    def State(self):
        return self.Me.fetch('State')
    
    @State.setter
    def State(self, val):
        if val in self.States:
            self.Me.store( 'State', val )
            self.Me.par.State.val = val

    def Fades(self, value = None):
        
        if value is None:
            value = self.Me.fetch('Fades')
        else:
            self.Me.store( 'Fades', value )
        self.print('fades: ' + str(value) )
        self.Me.par.Fadein.readOnly = not value
        self.Me.par.Fadeout.readOnly = not value
        return value
    
    def Fadein(self, value = None):
        if value is None:
            return self.Me.fetch('Fadein')
        else:
            self.Me.store( 'Fadein', value )
            self.Me.par.Fadein.val = value
        return

    def Fadeout(self, value = None):
        if value is None:
            return self.Me.fetch('Fadeout')
        else:
            self.Me.store( 'Fadeout', value )
            self.Me.par.Fadeout.val = value
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