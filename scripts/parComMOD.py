import json

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

def dict_to_storage(target_op, storage_dict_key, op_name, dict_to_store):
    ''' 
        A reusable method for capturing parameters on a single page of a COMP
    
        Args
        ---------------
        target_op (TouchDesigner COMP):
        > a ToughDesigner COMP that has custom parameters you would like to convert
        > into a python dictionary.
        
        storage_dict_key (str):
        > the string name of the storage dictionary you'd like to add
        > your preset / cue to.
    
        op_name (str):
        > a name for the preset / cue.
        
        dict_to_store (dict):
        > a python dictionary to put into storage.
                                
        Returns
        ---------------
        None
    '''
    # grab the dictionary from storage
    all_presets                 = target_op.fetch(storage_dict_key)
 
    # create a new entry
    all_presets[op_name]    = dict_to_store
 
    # put dictionary back into storage
    target_op.store(storage_dict_key, all_presets)

def load_store_json(target_file, storage_op, target_key, storage_name):
    ''' 
        A Helper function that reads JSON from disk
    
        Args
        ---------------
        target_file (file path):
        > a path to a .json file on disk. This is where the file will
        > be read from.
        
        storage_op (TouchDesigner operator):
        > the target operator where we will store the dictionary.
 
        target_key (str):
        > the string key we want to pull from our JSON file.
 
        storage_name (str):
        > the string name we want to use for storage.
                                
        Returns
        ---------------
        None
    '''
 
    # open the json file
    json_file               = open(target_file, 'r')
 
    # create a dictionary out of our json file
    json_dict               = json.load(json_file).get(target_key)
 
    # store our dictionary in the target op
    storage_op.store(storage_name, json_dict)
 
    # close the file
    json_file.close()

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

def load_preset(op_name, storage_op, target_op):

    # safety to ensure we have a preset to use
    try:
        par_vals         = storage_op.fetch("presets")[op_name]
    except:
        print("This preset does not exist")

    # loop through all pars and set them based on the vals in storage
    for each_par, each_val in par_vals.items():
        target_op.pars(each_par)[0].val = each_val

    target_op.par.Presetname = op_name

def load_pars(par_dict, target_op, readOnly=False):

    # safety to ensure we have a preset to use
    # try:
    #     par_vals         = par_dict[target_op.name]
    # except:
    #     print("This preset does not exist")

    # loop through all pars and set them based on the vals in storage
    # if par_dict['op_name'] == target_op.name:
    if target_op.name.find( par_dict[ 'op_name' ] ) != -1:
        par_vals = par_dict['par_vals']
        for each_par, each_val in par_vals.items():
            targetPar = target_op.pars( each_par )
            # print('targetPar: ', targetPar )
            if targetPar != []:
                if not targetPar[0].readOnly or readOnly:
                    if targetPar[0].val != each_val:
                        targetPar[0].val = each_val
                    
                    # target_op.pars(each_par)[0].val = each_val

        # target_op.par.Presetname = op_name