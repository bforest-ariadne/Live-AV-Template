op = op  # pylint:disable=invalid-name,used-before-assignment
root = root  # pylint:disable=invalid-name,used-before-assignment

TDF = op.TDModules.mod.TDFunctions  # utility functions
TDJ = op.TDModules.mod.TDJSON
parComMod = mod('/scripts/parComMOD')
ParSendModeExtension = mod('parSendModeEXT').ParSendModeExtension


class OutputExtension( ParSendModeExtension ):

    """ A class used to control the final output switchCOMP

    Attributes
    ----------
    Me : td.COMP
        a reference to the output Op
    name : str
        the name of the Op
    onModeSet : dict
        a callback that is fired when the Mod has set
        keys: 'operator', 'method'
    States : list
        strings representing the possible states of the op
    Modes : list
        a list of Mode tagged ops in the root dir
    ModeNames : list
        a list of names of the Modes in Modes
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

    Setmodegoal(self, Modegoal=None, operator=None, method=None)
        Starts the process of setting the new mode (Modegoal)

    OnModeStop()
        a callback method fired when the current mode has stopped

    OnModeStart()
        a callback method fired when the new mode has started

    OnRootVarsChange(dat, rows)
        updates paramater status - called by a datexecDAT when any root vars change.

    OnRootVarsChange()
        updates paramater Mode menus and Modes list. called by a datexecDAT callback


    """

    def __init__(self, my_op):
        self.Me = my_op
        self.name = my_op.name
        self.onModeSet = {'operator': None, 'method': None}
        self.States = ['Set', 'Setting']
        self.Modes = root.findChildren(depth=1, tags=['Mode'])
        self.Me.store('Modes', self.Modes)
        self.Me.store('States', self.States)
        self.State = self.Me.fetch('State')
        # self.com = op('/IO/base_com')
        ParSendModeExtension.__init__(self, my_op)
        self.ModeNames = []
        self.status('init')
        self.getModeNames()
        self.Setmodegoal()
        return

    def Test(self):
        self.print('test extension')
        return

    def Setmodegoal(self, Modegoal=None, operator=None, method=None):

        # Only start modeChange if not already setting
        if self.State == 'Set':
            self.State = 'Setting'

            # change Modegoal var
            # check Modegoal argument
            if Modegoal is not None and Modegoal in self.ModeNames:
                self.Me.store('Setmodegoal', Modegoal)
            elif Modegoal is None:
                root.setVar('Modegoal', self.Me.fetch('Setmodegoal'))

            # make sure Modegoal is not Mode
            if root.var('Mode') != root.var('Modegoal'):

                # set onModeSet callback
                self.onModeSet = {'operator': operator, 'method': method}

                # send stop to current mode with stop callback
                self.status('mode change start: ' + root.var('Modegoal'))
                modeOp = op('/' + root.var('Mode'))

                # stop current mode, if already stopped continue with mode change
                if modeOp.State == 'Started':
                    modeOp.Stop(self, 'OnModeStop')
                else:
                    self.OnModeStop()
                return True
            # reset Modegoal and state since Mode is not changing
            root.setVar('Modegoal', 'None')
            self.State = 'Set'
            return False
        self.State = 'Set'
        return False

    def OnModeStop(self):
        self.status(root.var('Mode') +
                    ' Mode stopped. Starting ' + root.var('Modegoal'))

        # in stop callback switch output display to modegoal
        self.Me.par.opviewer = root.var('Modegoal')
        self.Me.par.selectpanel = root.var('Modegoal')

        # send start to modegoal with start callback
        modeGoalOp = op('/' + root.var('Modegoal'))
        if modeGoalOp.State == 'Stopped':
            modeGoalOp.Start(self, 'OnModeStart')
        else:
            self.OnModeStart()
        return

    def OnModeStart(self):
        self.status(root.var('Mode') + ' Starting')

        # change mode to modegoal
        newMode = root.var('Modegoal')
        if newMode == 'None':
            debug('tried to switch Mode to None')
        else:
            root.setVar('Mode', root.var('Modegoal'))

        # change modegoal to None
        root.setVar('Modegoal', 'None')

        # reset State and launch on set callback
        self.State = 'Set'
        self.callback(self.onModeSet)
        return

    def getModeNames(self):
        self.ModeNames = []
        for mode in self.Modes:
            self.ModeNames.append(mode.name)
        self.Me.store('ModeNames', self.ModeNames)
        return

    def OnRootVarsChange(self, dat, rows):
        self.refreshVarPars()
        for row in rows:
            cells = dat.row(row)
            varName = cells[0]
            varVal = cells[1]
            customPars = self.Me.customPars
            for par in customPars:
                if par.name == varName:
                    par.val = varVal

    def refreshVarPars(self):
        self.Me.par.Mode = root.var('Mode')
        self.Me.par.Modegoal = root.var('Modegoal')
        return

    @property
    def State(self):
        return self.Me.fetch('State')

    @State.setter
    def State(self, val):
        if val in self.States:
            self.Me.store('State', val)
            self.Me.par.State.val = val
            if val == 'Setting':
                self.Me.par.Setmodegoal.readOnly = True
            else:
                self.Me.par.Setmodegoal.readOnly = False

    def OnModesChange(self):
        self.print('modes change')
        self.Modes = root.findChildren(depth=1, tags=['Mode'])
        self.getModeNames()
        menuPars = ['Mode', 'Modegoal', 'Setmodegoal']
        for menuName in menuPars:
            menu = self.Me.pars(menuName)[0]
            names = self.ModeNames
            if menuName == 'Modegoal':
                names.append('None')
            menu.menuNames = names
            menu.menuLabels = names
        pass

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
        self.sendApplyParVals()
        return

    def print(self, message):
        print(self.name + ': ', message)
        return

    def status(self, message):
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
