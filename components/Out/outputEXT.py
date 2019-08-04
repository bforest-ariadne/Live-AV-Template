op = op  # pylint:disable=invalid-name,used-before-assignment
root = root  # pylint:disable=invalid-name,used-before-assignment

from TDStoreTools import StorageManager # deeply dependable collections/storage
TDF = op.TDModules.mod.TDFunctions # utility functions

class OutputExtension():

    def __init__(self, my_op):
        self.Me = my_op
        #test4
        self.name = my_op.name
        self.print('init')
        self.onStop = { 'operator': None, 'method': None }
        self.onStart = { 'operator': None, 'method': None }
        self.onModeSet = { 'operator': None, 'method': None }
        self.States = [ 'Set', 'Setting' ]
        self.State = self.Me.fetch( 'State' )
        self.Modes = root.findChildren(depth=1, tags=['Mode'])
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
        root.setVar( 'Mode', root.var( 'Modegoal' ) )
        # change modegoal to None
        root.setVar( 'Modegoal', 'None' )
        self.State = 'Set' 
        self.callback( self.onModeSet )
        return

    def GetModeNames(self):
        for mode in self.Modes:
            self.ModeNames.append( mode.name )
        return
    
    def OnRowChange(self, dat, rows):
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