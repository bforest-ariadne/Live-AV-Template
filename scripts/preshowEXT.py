op = op  # pylint:disable=invalid-name,used-before-assignment
root = root  # pylint:disable=invalid-name,used-before-assignment


class PreShowExtension():

    def __init__(self, my_op):
        self.Me = my_op
        # test
        self.name = my_op.name
        self.onStopped = {'operator': None, 'method': None}
        self.onStarted = {'operator': None, 'method': None}
        self.States = ['Starting', 'Started', 'Stopping', 'Stopped']
        self.fadeIO = op('../fadeIO')
        # fade in and out progress refs for outputEXT progress
        self.FadeInProg = op('../fadeIO/fadeInProg')
        self.FadeOutProg = op('../fadeIO/fadeOutProg')
        self.State = self.Me.fetch('State')

        self.print('init')
        if self.State == 'Started':
            self.fadeIO.ImmediateIn()
        elif self.State == 'Stopped':
            self.fadeIO.ImmediateOut()

        if root.var('Mode') == self.name:
            if self.State != 'Started':
                self.Start()
        else:
            if self.State != 'Stopped':
                self.Stop()
        return

    def Test(self):
        self.print('test extension')
        return

    def Start(self, operator=None, method=None):
        if self.State == 'Stopped':
            self.State = 'Starting'

            self.print('starting')
            self.onStarted = {'operator': operator, 'method': method}

            fadeIO = self.fadeIO
            fadeInSuccess = fadeIO.Fadein(self, 'OnFadeIn')
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
            self.onStopped = {'operator': operator, 'method': method}
            # - fade out scene from black
            fadeIO = self.fadeIO
            fadeOutSuccess = fadeIO.Fadeout(self, 'OnFadeOut')
            if fadeOutSuccess == False:
                self.OnFadeOut()

            return True
        else:
            return False

        return

    def OnFadeIn(self):
        self.print('onfadein')
        # - update started state in storage
        self.State = 'Started'
        # - run a 'started' callback
        self.callback(self.onStarted)
        return

    def OnFadeOut(self):
        self.print('onfadeout')
        self.finishStopping()
        return

    def finishStopping(self):
        self.State = 'Stopped'
        # - run stopped callback
        self.callback(self.onStopped)
        return

    # to replace self.State('val') with self.State = val with find/replace:
    #   input: self.State\((.*)(\))
    #   output: self.State = $1

    @property
    def State(self):
        return self.Me.fetch('State')

    @State.setter
    def State(self, val):
        if val in self.States:
            self.Me.store('State', val)
            self.Me.par.State.val = val

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

        return

    def print(self, message):
        print(self.name + ': ', message)
        return

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
