op = op  # pylint:disable=invalid-name,used-before-assignment
ParMode = ParMode  # pylint:disable=invalid-name,used-before-assignment
TDF = op.TDModules.mod.TDFunctions # utility functions

class FadeIOExtension():

    def __init__(self, my_op):
        self.Me = my_op
        self.onFadeOut = { 'operator': None, 'method': None }
        self.onFadeIn = { 'operator': None, 'method': None }
        self.fadeInTimer = op( 'timer_fadein' )
        self.fadeOutTimer = op( 'timer_fadeout' )

        fadeInPar = self.Me.par.Fadeintime
        fadeOutPar = self.Me.par.Fadeouttime
        if TDF.getParInfo( self.Me.parent(), pattern='Fadein*', includeNonCustom=False ) != {}:
            print( 'has pars' )
            fadeInPar.bindExpr = 'parent().par.Fadein'
            fadeInPar.mode = ParMode.BIND
            self.Me.store( fadeInPar.name, fadeInPar.eval() )
            
            fadeOutPar.bindExpr = 'parent().par.Fadeout'
            fadeOutPar.mode = ParMode.BIND
            self.Me.store( fadeOutPar.name, fadeOutPar.eval() )
        else:
            fadeInPar.mode = ParMode.CONSTANT
            fadeOutPar.mode = ParMode.CONSTANT
        return
    
    def ImmediateOut(self):
        self.fadeOutTimer.par.gotodone.pulse()
        return

    def ImmediateIn(self):
        self.fadeInTimer.par.gotodone.pulse()
        return


    def Fadein(self, operator=None, method=None, time=None):
        ''' Fade in function
        Sets the fade in time and pulses the fadein timer

        Arguments: operator and method to callback on complete

        Returns if the function was able to execute
        '''
        self.onFadeIn = { 'operator': operator, 'method': method }

        seg = op('fadeInSeg')
        seg[1,'length'] = self.Me.fetch('Fadeintime')
        if time is not None:
            seg[1,'length'] = time
        btn = op('btn_fadeIn')
        btn.click()
        return self.Me.fetch('state') == False

    def Fadeout(self, operator=None, method=None, time=None):
        ''' Fade out function
        Sets the fade out time and pulses the fadein timer

        Arguments: operator and method to callback on complete

        Returns if the function was able to execute
        '''
        self.onFadeOut = { 'operator': operator, 'method': method }

        seg = op('fadeOutSeg')
        seg[1,'length'] = self.Me.fetch('Fadeouttime')
        if time is not None:
            seg[1,'length'] = time
        btn = op('btn_fadeOut')
        btn.click()
        return self.Me.fetch('state') == True

    # Methods for timer callbacks
    def FadeInOnDone(self, timerOp):
        ''' Fade in Done timer callback function
        - inits the fade out timer
        - sets the component state variable
        - fires callback if exists

        Arguments: timer op
        '''
        fadeOut = op( 'timer_fadeout' )
        if fadeOut['done']:
            fadeOut.par.initialize.pulse()
            
        self.Me.store('state', True)
        self.callback( self.onFadeIn )
        return

    def FadeOutOnDone(self, timerOp):
        ''' Fade out Done timer callback function
        - inits the fade in timer
        - sets the component state variable
        - fires callback if exists

        Arguments: timer op
        '''
        fadeIn = op( 'timer_fadein' )
        if fadeIn['done']:
            fadeIn.par.initialize.pulse()
            
        self.Me.store('state', False)
        self.callback( self.onFadeOut )
        return

    # method to call callbacks
    def callback(self, config):
        if config['operator'] and config['method']:
            if hasattr( config['operator'], config['method'] ):
                function = getattr(config['operator'], config['method'])
                if callable( function ):
                    function()
            else:
                print('FADEIO: callback no fire')
                print('operator: ', config['operator'])
                print('method: ', config['method'])
        return

    def OnPulse(self, par):
        if hasattr( self.Me, par.name ):
            function = getattr( self.Me, par.name )
            function()
        return

    def OnValueChange(self, par):
        self.Me.store( par.name, par.eval() )
        return