op = op  # pylint:disable=invalid-name,used-before-assignment
root = root  # pylint:disable=invalid-name,used-before-assignment
parComMod = mod('/Control/base_com/parComMOD')
TDJ = op.TDModules.mod.TDJSON
import socket
import json

class ControlExtension():

    def __init__(self, my_op):
        self.Me = my_op
        # test
        self.name = my_op.name
        print('name: ', self.name )
        self.com = op('/IO/base_com')
        self.children = self.Me.findChildren(type=containerCOMP, maxDepth=2)
        self.Children = self.children
        self.widgets = self.Me.findChildren(type=widgetCOMP)
        self.Widgets = self.widgets
        self.WriteableWidgets = []
        self.Msg = {}
        self.fontColor = [0.913725, 1, 0, 1]
        self.com = op('/Control/base_com')
        self.adjustWidgets()
        self.AdjustWidgets = self.adjustWidgets

        return
    
    def updateChildren(self):
        self.children = self.Me.findChildren(type=containerCOMP, maxDepth=2)
        return

    def ApplyParVals(self, message):
        target = message.get('value').get('target')
        msg = message.get('value').get('parDict')

        if msg.get( 'op_name', None ):
            targetOp = root.findChildren(name=target)[0]
            if targetOp:
                parComMod.load_pars(msg, targetOp, readOnly=False)
        return

    def ApplyPars(self, message):
        self.print('ApplyPars')

        target = message.get('value').get('target')
        msg = message.get('value').get('pageDict')
        parOrder = message.get('value').get('parOrder')

        children = self.Me.op('ui').findChildren( name = target, maxDepth = 1 )
        targetOp = None
        created = False
        if children != []:
            for child in children:
                if child.name != target:
                    targetOp = self.Me.op('ui').copy( self.Me.op('template') )
                    # targetOp.name = target
                    created = True
                else:
                    targetOp = child
        else:
            targetOp = self.Me.op('ui').copy( self.Me.op('template') )
            targetOp.name = target
            created = True
        
        # self.print('targetOp: ' + targetOp)
        TDJ.addParametersFromJSONDict(targetOp, msg, replace=True, setValues=True, destroyOthers=True)
        targetOp.customPages[0].sort(*parOrder)
        
        if created:
            autoUI = targetOp.loadTox(root.var('TOUCH') +'/components/autoUI.tox' ) 
        autoUI = targetOp.op('autoUI')
        autoUI.par.Generateui.pulse()        
        # targetOp.op('ui').par.reinitnet.pulse()
        self.adjustWidgets()
        self.updateChildren()

        return

    def OnChildParChange(self, par):
        # self.print('child par change')
        parDict = parComMod.page_to_dict( par.owner, 'Settings', [] )
        target = parDict['op_name'][:-1]
        msg = {
			'messagekind'	: "ApplyParVals",
			'target'		: op.Com.Hostname,
			'sender'		: op.Com.Hostname,
			'output'		: None,
			'parameter'		: None,
			'value'			: {
				"parDict"	: parDict,
                "target"    : target
			}
		}
        self.com.Send_msg( msg )
        return

    def adjustWidgets(self):
        self.WriteableWidgets = []
        for widget in self.widgets:
            # self.print('widget: ' + widget.name )
            if widget.pars('Value0') != []:
                # print( widget.par.Value0 )
                if True:
                    if widget.par.Value0.bindMaster.readOnly:
                        # self.print('readOnly par: ' + widget.name)
                        fontColorParNames = ['*fontcolor*', '*fontoffcolor*']
                        for fontColorParName in fontColorParNames:
                            fontColorPars = widget.pars(fontColorParName)
                            # self.print(fontColorPars)
                            if fontColorPars != []:
                                fontColors = ['*fontcolorr', '*fontcolorg', '*fontcolorb', '*fontcolora']
                                for i in range(len(fontColors)):
                                    fontColorSingle = widget.pars( fontColors[i] )
                                    for fontPar in fontColorSingle:
                                        fontPar.val = self.fontColor[i]
                else:
                    self.WriteableWidgets.append( widget )
        return    

    def OnReceive(self, dat, rowIndex, message, bytes, peer):
        json_msg = json.loads(message)
		
        if json_msg.get( 'op_name', None ):
            self.handleOpNameMsg(json_msg)

        return
    def handleOpNameMsg(self, msg):
        for child in self.children:
            if child.name.find( msg.get( 'op_name', None ) ) != -1:
                self.Msg = msg
                readOnly = child.digits is not None
                # self.print( 'readOnly: ' + str(readOnly))
                parComMod.load_pars( msg, child, readOnly=readOnly )

        return

    def OnPulse(self, par):
        if hasattr( self.Me, par.name ):
            function = getattr( self.Me, par.name )
            if callable( function ):
                function()
            # else:
            #     self.print( 'attr is not callable' )
        return

    def OnValueChange(self, par):
        self.Me.store( par.name, par.eval() )
        if hasattr( self.Me, par.name ):
            function = getattr( self.Me, par.name )
            if callable( function ):
                function()
            # else:
            #     self.print( 'attr is not callable' )
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