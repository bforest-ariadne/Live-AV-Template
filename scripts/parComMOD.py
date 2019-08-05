import json
# test
def page_to_dict(target_op, target_page, ignore_list):
    ''' 
        A reusable method for capturing parameters on a single page of a COMP
    
        Args
        ---------------
        target_op (TouchDesigner COMP):
        > a ToughDesigner COMP that has custom parameters you would like to convert
        > into a python dictionary.
        
        target_page (str):
        > the string name of the page whose parameters you would like to
        > convert into a python dictionary.
    
        o_name (str):
        > a name for the preset / cue.
        
        ignore_list (list):
        > a list of parameters you do not want to include.
                                
        Returns
        ---------------
        par_dict (dict)
        > a dictionary containing a preset name and dictionary of parameters.
    '''
 
    # create empty par_dict with input name as the preset_name value
    par_dict = {
        "op_name"   : target_op.name,
        "par_vals"   : {}
    }
 
    # loop through each parameter in the target_op and capture its name and
    # value only if its custom page matches the input string for target_page, 
    # and the pars are not on the ignore_list
    for each_par in target_op.pars():
        if each_par.isCustom and each_par.page == target_page and each_par.name not in ignore_list:
            par_dict["par_vals"][each_par.name] = each_par.val
 
    return par_dict

def write_dict_to_json(target_file, dict_to_save):
    ''' 
        A Helper function that writes JSON file to disk
    
        Args
        ---------------
        target_file (file path):
        > a path to a .json file on disk. This is where the file will
        > be written.
        
        dict_to_save (dict):
        > the dictionary to save as json.
                                
        Returns
        ---------------
        None
    '''
 
    # open the json file
    json_file               = open(target_file, 'w')
 
    # ensure the format for the json is human readable
    pretty_json             = json.dumps(dict_to_save, indent=4)
 
    # write the json to file
    json_file.write(pretty_json)
 
    # close the file
    json_file.close()

def load_pars(par_dict, target_op, readOnly=False):

    # safety to ensure we have a preset to use
    # try:
    #     par_vals         = par_dict[target_op.name]
    # except:
    #     print("This preset does not exist")

    # loop through all pars and set them based on the vals in storage
    targetName = target_op.name
    sourceName = par_dict['op_name']
    if targetName[:-1].find( sourceName ) != -1 or sourceName[:-1].find( targetName ) != -1:
        if targetName != sourceName:
            print( 'source:', par_dict['op_name'], 'target:', target_op.name )
            par_vals = par_dict['par_vals']
            for each_par, each_val in par_vals.items():
                targetPar = target_op.pars( each_par )
                if targetPar != []:
                    if not targetPar[0].readOnly or readOnly:
                        if targetPar[0].val != each_val:
                            # print('changed par: ', each_par, each_val, 'source:', par_dict[ 'op_name' ], 'target:', target_op.name, targetPar[0].val )
                            targetPar[0].val = each_val
                            if targetPar[0].isPulse:
                                targetPar[0].pulse()
