op = op  # pylint:disable=invalid-name,used-before-assignment
root = root  # pylint:disable=invalid-name,used-before-assignment


class PresetEXT():

    def __init__(self, my_op):
        self.Me = my_op
        self.name = my_op.name
        self.parent = self.Me.parent()
        self.SceneName = self.parent.name
        self.Me.par.Scenename = self.SceneName

        self.print('init')
        self.Dev()
        return

    def createMidiConstant(self):
        children = self.parent.findChildren(name='midi', type=constantCHOP)
        if children == []:
            print('create midi')
            self.Midi = self.parent.create(constantCHOP, 'midi')
            self.Midi.nodeX = self.Me.nodeX
            self.Midi.nodeY = self.Me.nodeY - self.Me.nodeHeight - 20
            self.parent.par.iopshortcut2 = 'midi'
            self.parent.par.iop2 = self.Midi.path
        elif len(children) == 1:
            self.Midi = children[0]
        return

    def Dev(self):
        if self.Me.fetch('Dev'):
            self.print('dev mode on')
            self.CreateMidiConstant = self.createMidiConstant
        else:
            self.print('dev mode off')
        

    def Test(self):
        self.print('test extension')
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
                self.print('callback no fire')
                self.print('operator: ' + config['operator'])
                self.print('method: ' + config['method'])
        return
