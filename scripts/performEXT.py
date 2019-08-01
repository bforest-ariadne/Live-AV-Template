op = op  # pylint:disable=invalid-name,used-before-assignment

class PerformExtension():

    def __init__(self, my_op):
        self.Me = my_op
        self.name = my_op.name
        print('name: ', self.name )
        #test9
        self.input = op('../input')
        self.Me.store( 'Input', op('../input') )
        self.onStop = { 'operator': None, 'method': None }
        self.onStart = { 'operator': None, 'method': None }
        self.nodes = []
        self.scenes = []
        # self.GetScenes()
        self.CurrentScene( op('../scene1') )
        self.PreviousScene = None
        self.StartCurrentScene()
        if self.Me.fetch( 'Nextsceneindex' ) == self.CurrentScene().digits - 1:
            self.Me.store( 'Nextsceneindex', self.CurrentScene().digits )
        return


    def Test(self):
        self.print('test extension')
        return
    def Start(self, operator=None, method=None):
        return

    def Stop(self, operator=None, method=None):
        return
    def getNextIndex(self):
        return self.Me.fetch( 'Nextsceneindex' )
    
    def Changetonextscene(self):
        return self.ChangeScene( self.getNextIndex() )

    def ChangeScene(self, index = None, name = 'scene1'):
        self.newScene = False
        if type(index) == int:
            # self.print( self.scenes[index].name )
            self.newScene = self.scenes[index]
        elif type( index ) == str and index.isnumeric():
            # self.print( self.scenes[ int(index) ].name )
            self.newScene = self.scenes[ int(index) ]
        elif type(name) == str:
            for scene in self.scenes:
                if scene.name == name:
                    # self.print( scene.name )
                    self.newScene = scene
        if self.newScene:
            if not self.newScene.par.Lockfades.eval():
                self.newScene.par.Fadein = self.Me.fetch('Fadein')
            if not self.CurrentScene().par.Lockfades.eval():
                self.CurrentScene().par.Fadeout = self.Me.fetch('Fadeout')
            return self.startSceneChange()
        return False
    
    def startSceneChange(self):
        # stop current scene -
        self.print( 'stopping current scene' + self.CurrentScene().name )
        return self.CurrentScene().Stop( self, 'ContinueSceneChange' )

    def StartCurrentScene(self):
        self.GetScenes()
        startedCount = 0
        for scene in self.scenes:
            if scene != self.CurrentScene() and scene.State() == 'Started':
                startedCount += 1
        self.print('startedCount: ' + str(startedCount) )
        if startedCount == 1 and self.CurrentScene().Start() == "Started":
            return True
        else:
            self.stopAllScenes()
            self.disconnectAllScenes()
            # self.CurrentScene( self.scenes[0] )
            self.CurrentScene().outputConnectors[0].connect( self.input )
            self.Me.par.Currentsceneindex = self.CurrentScene().digits - 1
            if self.CurrentScene().State() == 'Stopped':
                self.CurrentScene().Start( self, 'OnCurrentSceneStart' )
            # elif self.CurrentScene().State() == 'Stopping':
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
        self.Me.par.Currentsceneindex = self.newScene.digits - 1
        # connect current scene to input
        self.CurrentScene().outputConnectors[0].connect( self.input )
        # start current scene
        # update current scene started on start
        self.CurrentScene().Start( self, 'OnCurrentSceneStart' )
        return

    def OnCurrentSceneStart(self):
        self.Me.store('SceneStart', True )
        return
    

    def stopAllScenes(self):
        print('stop all except', self.CurrentScene().name )
        for scene in self.scenes:
            if scene != self.CurrentScene():
                if scene.State() == 'Started':
                    print( scene.name, scene.State() )
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
        for paths in scenePaths:    
            self.scenes.append( op( paths ))
        self.Me.store( "Scenes", self.scenes )
        self.Me.par.Nextsceneindex.normMax = len(self.scenes) - 1
        self.Me.par.Currentsceneindex.normMax = len(self.scenes) -1
        return

    def CurrentScene(self, value = None):
        if value is None:
            return self.Me.fetch('CurrentScene')
        else:
            self.Me.store( 'CurrentScene', value )
            self.Me.par.Currentsceneindex.val = value.digits - 1
        return value
        
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