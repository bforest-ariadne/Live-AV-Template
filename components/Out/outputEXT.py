op = op  # pylint:disable=invalid-name,used-before-assignment
root = root  # pylint:disable=invalid-name,used-before-assignment

TDF = op.TDModules.mod.TDFunctions # utility functions
TDJ = op.TDModules.mod.TDJSON
parComMod = mod('/IO/base_com/parComMOD')
# test

class OutputExtension():

    def __init__(self, my_op):
        self.Me = my_op
        #test4
        self.name = my_op.name
        self.print('init')

        self.onModeSet = { 'operator': None, 'method': None }
        self.States = [ 'Set', 'Setting' ]
        self.Modes = root.findChildren(depth=1, tags=['Mode'])
        self.Me.store( 'Modes', self.Modes )
        self.Me.store( 'States', self.States )
        self.State = self.Me.fetch( 'State' )
        self.com = op('/IO/base_com')

        self.fadeInProg = op('./fadeInProg')
        self.fadeOutProg = op('./fadeOutProg')
        TDF.createProperty( self, 
            'FadeInProgSel', 
            value=op('/' + root.var('Modegoal') ).FadeInProg if root.var('Modegoal') != 'None' else op('constant1'), 
            dependable=True)
        TDF.createProperty( self, 
            'FadeOutProgSel', 
            value=op('/' + root.var('Mode') ).FadeOutProg, 
            dependable=True)
        self.ModeNames = []
        self.GetModeNames()
        self.Setmodegoal()
        return

    def Test(self):
        self.print('test extension')
        return

    def Setmodegoal(self, Modegoal=None, operator=None, method=None):
        if self.State == 'Set':
            self.State = 'Setting' 

            # change Modegoal var
            if Modegoal is not None and Modegoal in self.ModeNames:
                self.Me.store( 'Setmodegoal', Modegoal )
            elif Modegoal is None:
                root.setVar( 'Modegoal', self.Me.fetch('Setmodegoal') )
            
            if root.var( 'Mode' ) != root.var( 'Modegoal' ):

                self.onModeSet = { 'operator': operator, 'method': method }

                # send stop to current mode with stop callback
                # self.OnModeStop()
                self.print('mode change start: ' + root.var('Modegoal') )
                modeOp = op( '/' + root.var('Mode') )
                if modeOp.State == 'Started':
                    modeOp.Stop( self, 'OnModeStop')
                else:
                    self.OnModeStop()
                return True
            root.setVar( 'Modegoal', 'None' )
            self.State = 'Set'
            return False
        self.State = 'Set'
        return False


    def OnModeStop(self):
        self.print('OnModeStop')
        # in stop callback switch output display to modegoal
        self.Me.par.opviewer = root.var( 'Modegoal' )
        self.Me.par.selectpanel = root.var( 'Modegoal' )
        # send start to modegoal with start callback
        # self.OnModeStart()
        modeGoalOp =  op( '/' + root.var('Modegoal') )
        if modeGoalOp.State == 'Stopped':
            modeGoalOp.Start( self, 'OnModeStart')
        else:
            self.OnModeStart()
        return
    
    def OnModeStart(self):
        self.print('OnModeStart')
        # change mode to modegoal
        newMode = root.var('Modegoal')
        if newMode == 'None':
            debug( 'tried to switch Mode to None')
        else:
            root.setVar( 'Mode', root.var( 'Modegoal' ) )
        # change modegoal to None
        root.setVar( 'Modegoal', 'None' )
        self.State = 'Set' 
        self.callback( self.onModeSet )
        return

    def GetModeNames(self):
        self.ModeNames = []
        for mode in self.Modes:
            self.ModeNames.append( mode.name )
        self.Me.store( 'ModeNames', self.ModeNames )
        return
    
    def OnRowChange(self, dat, rows):
        self.print('rowChange')
        self.refreshVarPars()
        for row in rows:
            cells = dat.row( row )
            varName = cells[0]
            varVal = cells[1]
            # print( 'var: ', varName, ' val: ', varVal )
            customPars = self.Me.customPars
            for par in customPars:
                if par.name == varName:
                    par.val = varVal
                    self.updateProgressSelect()

    def refreshVarPars(self):
        self.Me.par.Mode = root.var('Mode')
        self.Me.par.Modegoal = root.var('Modegoal')
        return
                    
    
    def updateProgressSelect(self):
        if root.var('Modegoal') != 'None':
            self.FadeInProgSel = op('/' + root.var('Modegoal') ).FadeInProg
        else:
            self.FadeInProgSel = op('constant1')
        self.FadeOutProgSel = op('/' + root.var('Mode') ).FadeOutProg
        return

    @property
    def State(self):
        return self.Me.fetch('State')
    
    @State.setter
    def State(self, val):
        if val in self.States:
            self.Me.store( 'State', val )
            self.Me.par.State.val = val
            if val == 'Setting':
                self.Me.par.Setmodegoal.readOnly = True
            else:
                self.Me.par.Setmodegoal.readOnly = False

    def OnModesChange(self):
        self.print('modes change')
        self.Modes = root.findChildren(depth=1, tags=['Mode'])
        self.GetModeNames()
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
        if hasattr( self.Me, par.name ):
            function = getattr( self.Me, par.name )
            if callable( function ):
                function()
            # else:
                # self.print( 'attr is not callable: ' + par.name  )
        return

    def OnValueChange(self, par):
        self.Me.store( par.name, par.eval() )
        if hasattr( self.Me, par.name ):
            function = getattr( self.Me, par.name )
            if callable( function ):
                function()
            # else:
                # self.print( 'attr is not callable: ' + par.name )
        self.SendApplyParVals()
        return

    def SendApplyParVals(self):
        parDict = parComMod.page_to_dict( self.Me, 'Settings', [] )
        # TDJ.jsonToDat( op.Out.op('text1'), parDict )
        msg = {
			'messagekind'	: "ApplyParVals",
			'target'		: op.Com.Hostname,
			'sender'		: op.Com.Hostname,
			'output'		: None,
			'parameter'		: None,
			'value'			: {
				"parDict"	: parDict,
                "target"    : self.name+'1'
			}
		}
        if self.Me.fetch('Uipars'):
            # self.print('send applyParVals')
            self.com.Send_msg( msg )
        return

    def OnParsChange(self):
        self.SendApplyPars()
        self.SendApplyParVals()
        return

    def SendApplyPars(self):
        pageDict = TDJ.pageToJSONDict( self.Me.customPages[0], ['val', 'order'] )
        pars = self.Me.customPages[0].pars
        parOrder = []
        for par in pars:
            parOrder.append( par.name )

        # print( 'Out parsDict', pageDict )
        
        msg = {
			'messagekind'	: "ApplyPars",
			'target'		: op.Com.Hostname,
			'sender'		: op.Com.Hostname,
			'output'		: None,
			'parameter'		: None,
			'value'			: {
				'pageDict'  : pageDict,
                "target"    : self.name+'1',
                'parOrder'     : parOrder,
			}
		}
        if self.Me.fetch('Ui'):
            # self.print('SentApplyPars')
            self.com.Send_msg( msg )
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