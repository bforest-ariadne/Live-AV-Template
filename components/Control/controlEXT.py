import json
import socket
op = op  # pylint:disable=invalid-name,used-before-assignment
root = root  # pylint:disable=invalid-name,used-before-assignment
# parComMOD = mod('/scripts/parComMOD')
import parComMOD
TDJ = op.TDModules.mod.TDJSON


class ControlExtension():

    def __init__(self, my_op):
        self.Me = my_op
        self.name = my_op.name
        self.Children = self.Me.findChildren(type=containerCOMP, maxDepth=2)
        self.widgets = self.Me.findChildren(type=widgetCOMP)
        self.Msg = {}
        self.readOnlyFontColor = [0.913725, 1, 0, 1]
        self.fontColor = [0.65, 0.65, 0.65, 1]
        self.com = op('/Control/base_com_control')
        self.pageDicts = {}

        self.print('init')
        self.adjustWidgets()
        return

    def updateChildren(self):
        self.Children = self.Me.findChildren(type=containerCOMP, maxDepth=2)
        return

    def ApplyParVals(self, message, comsParent):

        self.updateChildren()

        # init method arguments
        target = message.get('value').get('target')
        msg = message.get('value').get('parDict')
        rootOp = self.Me if comsParent.name == 'Control' else root

        # find targetOp
        targetOps = rootOp.findChildren(name=target)
        if targetOps == []:
            return
        try:
            assert(len(targetOps) <= 1)
        except AssertionError as error:
            print(error)
            self.print('there should be only one potential targetOp')
        targetOp = targetOps[0]
        if targetOp:
            # update readonly parameters if target is in the Control op
            readOnly = targetOp in self.Children
            # update targetOp with new par vals
            parComMOD.applyControlPars(msg, targetOp, readOnly=readOnly)
        return

    def ApplyPars(self, message):

        # init method vars
        target = message.get('value').get('target')
        msg = message.get('value').get('pageDict')
        parOrder = message.get('value').get('parOrder')

        # init pageDicts if needed
        if self.pageDicts.get(target) is None:
            self.pageDicts[target] = {'pageDict': msg}

        if self.pageDicts[target].get('pastDict') is None:
            self.pageDicts[target]['pastDict'] = msg

        self.pageDicts[target]['pastDict'] = self.pageDicts[target]['pageDict']
        self.pageDicts[target]['pageDict'] = msg

        # check past with current parameter numbers
        # to see if UI needs update
        uiNeedsUpdate = len(self.pageDicts[target]['pastDict']) != len(
            self.pageDicts[target]['pageDict'])

        children = self.Me.op('ui').findChildren(name=target, maxDepth=1)
        targetOp = None
        created = False
        # if the target does not exist, create it
        if children != []:
            for child in children:
                if child.name != target:
                    targetOp = self.Me.op('ui').copy(self.Me.op('template'))
                    created = True
                else:
                    targetOp = child
        else:
            targetOp = self.Me.op('ui').copy(self.Me.op('template'))
            targetOp.name = target
            created = True

        # update target op with new pars
        TDJ.addParametersFromJSONDict(
            targetOp, msg, replace=True, setValues=True, destroyOthers=True)

        # sort parameters for correct order
        try:
            targetOp.customPages[0].sort(*parOrder)
        except:
            self.print('parameter sorting error')
        
        self.print('after except')
        # if just created, load audoUI tox into target
        autoUI = None
        if created:
            autoUI = targetOp.loadTox(
                root.var('TOUCH') + '/components/autoUI.tox')
        autoUI = targetOp.op('autoUI')

        # update UI if different number of pars
        # or if target was just created
        if created or uiNeedsUpdate:
            self.print('autoUI pulsed. created: ' +
                       str(created) + ' uiNeedsUpdate: ' + str(uiNeedsUpdate))
            autoUI.par.Generateui.pulse()

        # update par colors for readOnly and update children
        self.adjustWidgets()
        self.updateChildren()

        return

    def OnChildParChange(self, par):

        parDict = parComMOD.pageToDict(par.owner, 'Settings', [])
        target = parDict['op_name'][:-1]
        msg = {
            'messagekind'	: "ApplyParVals",
            'target'		: op.Com.Hostname,
            'sender'		: op.Com.Hostname,
            'output'		: None,
            'parameter'		: None,
            'value'			: {
                            "parDict"	: parDict,
                            "target": target,
            }
        }
        self.com.Send_msg(msg)
        return

    def adjustWidgets(self):
        self.widgets = self.Me.findChildren(type=widgetCOMP)
        for widget in self.widgets:
            if hasattr(widget.par, 'Value0'):
                if widget.par.Value0.bindMaster.readOnly:
                    self.changeFontColor(widget, self.readOnlyFontColor)
                else:
                    self.changeFontColor(widget, self.fontColor)
        return

    def changeFontColor(self, widget, color):
        fontColorParNames = ['*fontcolor*', '*fontoffcolor*']
        for fontColorParName in fontColorParNames:
            fontColorPars = widget.pars(fontColorParName)
            if fontColorPars != []:
                fontColors = ['*fontcolorr', '*fontcolorg',
                              '*fontcolorb', '*fontcolora']
                for i in range(len(fontColors)):
                    fontColorSingle = widget.pars(fontColors[i])
                    for fontPar in fontColorSingle:
                        fontPar.val = color[i]
        return

    def OnReceive(self, dat, rowIndex, message, bytes, peer):
        self.print('OnReceive')
        json_msg = json.loads(message)

        if json_msg.get('op_name', None):
            self.handleOpNameMsg(json_msg)

        return

    def handleOpNameMsg(self, msg):
        for child in self.Children:
            if child.name.find(msg.get('op_name', None)) != -1:
                self.Msg = msg
                readOnly = child.digits is not None
                parComMOD.applyControlPars(msg, child, readOnly=readOnly)

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
                self.print('FADEIO: callback no fire')
                self.print('operator: ' + config['operator'])
                self.print('method: ' + config['method'])
        return
