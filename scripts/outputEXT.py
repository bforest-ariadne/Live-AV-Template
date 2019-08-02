op = op  # pylint:disable=invalid-name,used-before-assignment
root = root  # pylint:disable=invalid-name,used-before-assignment

from TDStoreTools import StorageManager # deeply dependable collections/storage
TDF = op.TDModules.mod.TDFunctions # utility functions

class OutputExtension():

    def __init__(self, my_op):
        self.Me = my_op
        #test5
        self.name = my_op.name
        self.print('init')
        self.onStop = { 'operator': None, 'method': None }
        self.onStart = { 'operator': None, 'method': None }
        self.onModeSet = { 'operator': None, 'method': None }
        self.createParameters()
        self.Modes = root.findChildren(depth=1, tags=['Mode'])
        self.ModeNames = []
        self.GetModeNames()

        return

    def Test(self):
        self.print('test extension')
        return

    def Setmodegoal(self, Modegoal=None, operator=None, method=None):
        # change Modegoal var
        if Modegoal is not None and Modegoal in self.ModeNames:
            self.Me.store( 'Setmodegoal', Modegoal )
        else:
            return False
        root.setVar( 'Modegoal', self.Me.fetch('Setmodegoal') )
        
        if root.var( 'Mode' ) != root.var( 'Modegoal' ):

            self.onModeSet = { 'operator': operator, 'method': method }

            # send stop to current mode with stop callback
            # self.OnModeStop()
            modeOp = op( '/' + root.var('Mode') )
            if modeOp.State() == 'Started':
                modeOp.Stop( self, 'OnModeStop')
            else:
                self.OnModeStop()
            return True
        return False

    def OnModeStop(self):
        self.print('OnModeStop')
        # in stop callback switch output display to modegoal
        self.Me.par.opviewer = root.var( 'Modegoal' )
        self.Me.par.selectpanel = root.var( 'Modegoal' )
        # send start to modegoal with start callback
        # self.OnModeStart()
        modeGoalOp =  op( '/' + root.var('Modegoal') )
        if modeGoalOp.State() == 'Stopped':
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
        return

    def createParameters(self):
        # self.Me.destroyCustomPars()
        # self.page = self.Me.appendCustomPage('Settings')
        # self.page.appendPulse( 'Test', label='Test', replace=True )
        # self.page.appendMenu( )
        # start = self.page.appendPulse( 'Start', label = 'Start')
        # stop = self.page.appendPulse( 'Stop', label = 'Stop')
        # Fadein = self.page.appendFloat( 'Fadein', label = 'Fadein')
        # Fadeout = self.page.appendFloat( 'Fadeout', label = 'Fadeout')
        return
    def GetModeNames(self):
        for mode in self.Modes:
            self.ModeNames.append( mode.name )
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