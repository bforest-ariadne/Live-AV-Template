TDJ = op.TDModules.mod.TDJSON

p = op.p

performSettings = TDJ.pageToJSONDict( p.customPages[0], ['val'] )

msgDict = {
    'messageType': 'Update',
    'messageData': {
        'opName': 'Perform_controls',
        'pageDict': performSettings
    }
}

TDJ.jsonToDat(msgDict, op('/json') )

children = op('/').findChildren( name = msgDict['messageData']['opName'], maxDepth = 1 )

p1 = None

if children != []:
    for child in children:
        if child.name != msgDict['messageData']['opName']:
            p1 = op('/').create(containerCOMP)
            p1.name = msgDict['messageData']['opName']
        else:
            p1 = child
else:
    p1 = op('/').create(containerCOMP)
    p1.name = msgDict['messageData']['opName']

    
TDJ.addParametersFromJSONDict(p1, msgDict['messageData']['pageDict'], replace=True, setValues=True, destroyOthers=True)
        



