# deeply dependable collections/storage
from TDStoreTools import StorageManager
op = op  # pylint:disable=invalid-name,used-before-assignment
root = root  # pylint:disable=invalid-name,used-before-assignment

TDF = op.TDModules.mod.TDFunctions  # utility functions
TDJ = op.TDModules.mod.TDJSON
# parComMOD = mod('/IO/base_com/parComMOD')
ParSendModeExtension = mod('parSendModeEXT').ParSendModeExtension



class PerformExtension(ParSendModeExtension):

    """ A class used to control the final output switchCOMP

    Attributes
    ----------
    Me : td.COMP
        a reference to the output Op
    name : str
        the name of the Op
    States : list
        strings representing the possible states of the op
    State : str
        a string representing the current state of the op
    com : td.COMP
        the base_com tox that will be used for comunication

    Methods
    -------
    Test()
        prints a test message

    print(str)
        prints name + message

    status(str)
        prints name + message

    Start(operator=None, method=None, index=None, name=None)
        Starts the perform mode, transitioning from blank scene to current scene. Called by "Start" custom parameter.

    Stop(operator=None, method=None)
        Stops the perform mode, transitioning from the current scene to the blank scene. Called by "Stop" custom parameter.

    Nextsceneindex()
        Called by the "Next Scene" custom parameter. Sets the next scene index and updates Fade in and Fadeout custom parameters

    Changetonextscene()
        Startes scene change to scene selected by "Next Scene" index custom parameter

    ChangeScene( index=None, name='scene1', blank=False, operator=None, method=None, fadein=None, fadeout=None)
        Called by "Change Scene" custom parameter. This is the main method to start a scene transition. 

    ContinueSceneChange()
        a callback method fired when the current scene has stopped

    OnCurrentSceneStart()
        a callback method fired when the new scene has started

    OnStart()
        a callback method fired when the Perform mode has started

    OnStop()
        a callback method fired when the Perform mode has started

    """

    def __init__(self, my_op):
        
        self.Me = my_op
        self.name = my_op.name
        self.onStopped = {'operator': None, 'method': None}
        self.onStarted = {'operator': None, 'method': None}
        self.onSceneChange = {'operator': None, 'method': None}
        self.Debug = False
        # self.com = op('/IO/base_com')
        super().__init__(my_op)
        self.States = ['Starting', 'Started', 'Stopping', 'Stopped']
        self.State = self.Me.fetch('State')
        self.CurrentScene = self.Me.fetch('CurrentScene')
        self.BlankScene = self.Me.op('blank')
        self.input = op('../input')
        self.scenes = []
        self.FadeInProg = op('../fadeInProg')
        self.FadeOutProg = op('../fadeOutProg')

        self.print('init')
        #  get list of scenes
        self.GetScenes()
        #  default to scene1 if CurrentScene from storage not available
        if self.CurrentScene not in self.scenes:
            self.CurrentScene = self.scenes[0]
        self.print('init current scene: ' + self.CurrentScene.name)

        # init previous scene as blank scene
        TDF.createProperty(self,
                           'PreviousScene',
                           value=self.BlankScene,
                           dependable=True)
        # init next scene from Nextsceneindex par in storage
        TDF.createProperty(self,
                           'NewScene',
                           value=self.Me.fetch('Scenes')[
                               self.Me.fetch('Nextsceneindex')],
                           dependable=True)
        # init Changing state to False
        TDF.createProperty(self,
                           'Changing',
                           value=False,
                           dependable=True)

        # init the Current scene if Mode == Perform and if State is Started
        if root.var('Mode') == 'Perform':
            if self.State == 'Started':
                self.initCurrentScene()
                # init Nextsceneindex to not the CurrentScene index
                if self.Me.fetch('Nextsceneindex') == self.CurrentScene.Index:
                    self.Me.store('Nextsceneindex',
                                  self.CurrentScene.Index + 1)
            else:
                # Start Perform if Mode = Perform and not State is not Started
                self.Start()
        else:
            # if Mode is not Perform, stop Perform
            self.print('not perform mode')
            self.Stop()
        return

    def Start(self, operator=None, method=None, index=None, name=None):
        if self.State == 'Stopped':
            self.State = 'Starting'

            self.print('starting')
            self.onStarted = {'operator': operator, 'method': method}

            if index is None and name is None:
                index = self.getNextIndex()
                if self.PreviousScene:
                    if self.PreviousScene.Index > -1:
                        index = self.PreviousScene.Index
            self.ChangeScene(index=index, operator=self, method='OnStart')

        return

    def Stop(self, operator=None, method=None):
        if self.State == 'Started':
            self.State = 'Stopping'

            self.print('stopping')
            self.onStopped = {'operator': operator, 'method': method}

            self.ChangeScene(blank=True, operator=self, method='OnStop')
        return

    def getNextIndex(self):
        return self.Me.fetch('Nextsceneindex')

    def Nextsceneindex(self):
        index = self.Me.fetch('Nextsceneindex')
        nextScene = self.scenes[index]
        self.Me.par.Fadein.val = nextScene.par.Fadein.val
        self.Me.par.Fadeout.val = self.CurrentScene.par.Fadeout.val
        return

    def Changetonextscene(self):
        return self.ChangeScene(self.getNextIndex())

    def ChangeScene(self, index=None, name='scene1', blank=False, operator=None, method=None, fadein=None, fadeout=None):
        # init and set onSceneChange callbacks
        self.onSceneChange = {'operator': None, 'method': None}
        self.onSceneChange = {'operator': operator, 'method': method}

        # fadeinArg is a temporary solution to mode based fades which is not implemented yet
        # TODO implement mode based fades
        fadeinArg = False
        fadeoutArg = False
        # this logic is type checking the fadein and fadeout arguments
        if fadein is not None:
            if type(fadein) == int:
                float(fadein)
            if type(fadein) == float:
                self.Fadein(fadein)
                fadeinArg = True
            else:
                self.print('wrong type for Fadein')
        if fadeout is not None:
            if type(fadeout) == int:
                float(fadeout)
            if type(fadeout) == float:
                self.Fadeout(fadeout)
                fadeoutArg = True
            else:
                self.print('wrong type for Fadeout')

        # starts change to blank scene if blang arg
        if blank:
            self.NewScene = self.BlankScene
            return self.startSceneChange()

        # initialize new scene
        self.NewScene = False
        # type check new scene int arg
        if type(index) == int:
            # make sure index is within range of available scenes
            if index >= len(self.scenes):
                return False
            # set new scene from index
            self.NewScene = self.scenes[index]
        # type check for index as string
        elif type(index) == str and index.isnumeric():
            # make sure index is within range of available scenes
            if int(index) >= len(self.scenes):
                return False
            # set new scene from index
            self.NewScene = self.scenes[int(index)]
        # type check name arg
        elif type(name) == str:
            # check if scene arg is in available scenes
            for scene in self.scenes:
                if scene.name == name:
                    # set new scene from scene name
                    self.NewScene = scene

        # checks that NewScene has been set
        if self.NewScene:
            # check that new scene is different than current scene
            if self.NewScene == self.CurrentScene:
                self.print('new scene is same as current scene')
                return False

            # check if we should set the new scene fade in time
            if self.Fades() or fadeinArg:
                if not self.NewScene.par.Lockfades.eval():
                    # set the fadein time for our new scene
                    self.NewScene.par.Fadein = self.Me.fetch('Fadein')
            # check if we should set the new scene fade out time
            if self.Fades() or fadeoutArg:
                if not self.CurrentScene.par.Lockfades.eval():
                    # set the fadeout time for our new scene
                    self.CurrentScene.par.Fadeout = self.Me.fetch('Fadeout')

            return self.startSceneChange()
        return False

    def startSceneChange(self):
        # check changing state - no change start if already changing
        if not self.Changing:
            # set changing state property
            self.Changing = True
            self.print('stopping current scene ' + self.CurrentScene.name)
            # check if CurrentScene is playing
            if self.CurrentScene.State != 'Stopped':
                # stop Current Scene
                self.CurrentScene.Stop(self, 'ContinueSceneChange')
            else:
                # if stopped, continue scene change from scene.OnStopped callback
                self.print(self.CurrentScene.name + ' was not Stopped ')
                self.ContinueSceneChange()
            return True
        else:
            self.print('scene is already changing')

    def initCurrentScene(self):
        self.print('StartCurrentScene init')

        startedCount = 0
        startedScenes = []
        for scene in self.scenes:
            if scene.State == 'Started':
                startedScenes.append(scene)
        startedCount = len(startedScenes)
        self.print('startedCount: ' + str(startedCount))
        if startedCount == 1 and startedScenes[0] == self.CurrentScene:
            if self.CurrentScene.Start() == "Started":
                return True
        else:
            self.stopAllScenes()
            self.disconnectAllScenes()
            # self.CurrentScene = self.scenes[0]
            self.CurrentScene.outputConnectors[0].connect(self.input)
            self.Me.par.Currentsceneindex = self.CurrentScene.Index
            if self.CurrentScene.State == 'Stopped':
                self.CurrentScene.Start(self, 'OnCurrentSceneStart')
            # elif self.CurrentScene.State == 'Stopping':
            #     self.CurrentScene.onStopped = { 'operator': self.CurrentScene, 'method': 'Start' }
            return
        return

    def ContinueSceneChange(self):
        self.print('continueSceneChange')
        self.Me.store('SceneStart', False)
        # disconnect on stop
        self.CurrentScene.outputConnectors[0].disconnect()
        # change current scene to previous scene
        self.PreviousScene = self.CurrentScene
        # set new scene to current scene
        self.CurrentScene = self.NewScene
        self.Me.par.Currentsceneindex = self.NewScene.Index
        # connect current scene to input
        self.CurrentScene.outputConnectors[0].connect(self.input)
        # start current scene
        # update current scene started on start
        if self.CurrentScene.State != 'Started':
            self.CurrentScene.Start(self, 'OnCurrentSceneStart')
        else:
            self.OnCurrentSceneStart()
        return

    def OnCurrentSceneStart(self):
        self.Me.store('SceneStart', True)
        self.Changing = False
        self.callback(self.onSceneChange)
        return

    def OnStart(self):
        self.print('OnStart')
        # - update started state in storage
        self.State = 'Started'
        # - run a 'started' callback
        self.callback(self.onStarted)
        return

    def OnStop(self):
        self.State = 'Stopped'
        # - run stopped callback
        self.callback(self.onStopped)
        return

    def stopAllScenes(self):
        print('stop all except', self.CurrentScene.name)
        for scene in self.scenes:
            if scene != self.CurrentScene:
                if scene.State == 'Started':
                    print(scene.name, scene.State)
                    scene.Stop()
        return

    def disconnectAllScenes(self):
        print('dissconnect all except', self.CurrentScene.name)
        for scene in self.scenes:
            if scene != self.CurrentScene:
                scene.outputConnectors[0].disconnect()
        return

    def GetScenes(self):
        findScene = op('opfind_scene')
        scenePaths = findScene.cells('scene*', 'path')
        self.scenes = []
        i = 0
        for paths in scenePaths:
            scene = op(paths)
            scene.Index = i
            self.scenes.append(scene)
            i += 1
        self.Me.store("Scenes", self.scenes)
        self.Me.par.Nextsceneindex.normMax = len(self.scenes) - 1
        self.Me.par.Currentsceneindex.normMax = len(self.scenes) - 1
        return

    @property
    def CurrentScene(self):
        return self.Me.fetch('CurrentScene')

    @CurrentScene.setter
    def CurrentScene(self, val):
        self.Me.store('CurrentScene', val)
        self.Me.par.Currentsceneindex.val = val.Index

    @property
    def State(self):
        return self.Me.fetch('State')

    @State.setter
    def State(self, val):
        if val in self.States:
            self.Me.store('State', val)
            self.Me.par.State.val = val

    @property
    def Debug(self):
        return self.Me.fetch('Debug')

    @Debug.setter
    def Debug(self, val):
        if type(val) == bool:
            self.Me.store('Debug', val)
            self.Me.par.Debug.val = val

    # TODO turn Fades, Fadein, and Fadeout into properties

    def Fades(self, value=None):

        if value is None:
            value = self.Me.fetch('Fades')
        else:
            self.Me.store('Fades', value)
        self.print('fades: ' + str(value))
        self.Me.par.Fadein.readOnly = not value
        self.Me.par.Fadeout.readOnly = not value
        return value

    def Fadein(self, value=None):
        if value is None:
            return self.Me.fetch('Fadein')
        else:
            self.Me.store('Fadein', value)
            self.Me.par.Fadein.val = value
        return

    def Fadeout(self, value=None):
        if value is None:
            return self.Me.fetch('Fadeout')
        else:
            self.Me.store('Fadeout', value)
            self.Me.par.Fadeout.val = value
        return

    def OnPulse(self, par):
        if hasattr(self.Me, par.name):
            function = getattr(self.Me, par.name)
            if callable(function):
                function()
        return

    def OnValueChange(self, par):
        self.Me.store(par.name, par.eval())
        if hasattr(self.Me, par.name):
            function = getattr(self.Me, par.name)
            if callable(function):
                function()
        self.sendApplyParVals()
        return

    def OnParsChange(self):
        self.sendApplyPars()
        return

    def print(self, message):
        if self.Debug == True:
            print(self.name + ': ', message)
        return

    # method to call callbacks
    def callback(self, config):
        if config['operator'] and config['method']:
            if hasattr(config['operator'], config['method']):
                function = getattr(config['operator'], config['method'])
                if callable(function):
                    function()
            else:
                self.print('FADEIO: callback no fire')
                self.print('operator: ' + config['operator'])
                self.print('method: ' + config['method'])
        return

    def Test(self):
        self.print('test extension')
        return
