from schedulerlib.input import make_input_generators, NameGenerator, input_int, input_str
from schedulerlib.write import write_to_ifile, write_to_peramfile
from schedulerlib.parser import parse_data,parse_groupings,search_data,reorder_tree
from pprint import pprint
import pickle
import sys
from pathlib import Path

#***NOTICE:: Run through project "PLSim 1.2" as the set relative location within the entire project. 
#            Accordingly if this is run in a new project each input and output file may need to have 
#            a modified file path corresponding to this new file structure ***

# input files
#INPUT_XML = "simulationfiles/devicedatabases/xmls/PLSim2Format.xml" #This is the input power usage "database" format
INPUT_XML = "simulationfiles/devicedatabases/xmls/DeviceList_xml.xml"

# output files
OUTPUT_PICKLE = 'simulationfiles/scheduleobjects/run_params' #this is the pickled object file passed with the selected device list onto the calculation engine
OUTPUT_CONFIG = 'simulationfiles/scheduleobjects/csvs/run_perams.cfg' #This is the list of parameters for the scheduler run, similar in content to the PICKLE file.
OUTPUT_CSV = 'simulationfiles/scheduleobjects/csvs/test_group.csv' #This is the generated schedule for device operation

MENU_STR = '''Simulation Builder/Scheduler Main Menu:
a: Add a device to simulation
d: Delete a from simulation
p: Print current devices in simulation
r: Run scheduler on selected devices, display output, Quit
q: Quit simulation
'''

def check_idm_readfile(inp_list:list):
    print("Whole input list: ", end = "")
    print(inp_list)
    reprompt = 1
    if(len(inp_list) == 0):
        print("Input file is empty")
        remprompt = 1
    else:
        inp = inp_list[0]
#         print("inp: " + inp)
        if inp == 'a':
            if (len(inp_list[1:]) != 4):
                print("Invalid input for 'a', length of input after a should be 4 but got {}.".format(str(len(inp_list[1:])))) 
                return reprompt
        elif inp == 'd':
            if (len(inp_list[1:]) != 1):
                print("Invalid input for 'd', length of input after d should be 1 but got {}.".format(len(inp_list[1:])))
                return reprompt
        elif inp == 'p':
            if (len(inp_list[1:]) != 0):
                print("Invalid input for 'p', length of input after p should be 0 but got {}.".format(len(inp_list[1:])))
                return reprompt
        elif inp == 'r':
            if (len(inp_list[1:]) != 1):
                print("Invalid input for 'r', length of input after p should be 1 but got {}.".format(len(inp_list[1:])))
                return reprompt
            elif (str(inp_list[1]).isdigit() == False):
                print("Invalid input for 'r', the second element should be an integer.")
                return reprompt
        elif inp == 'q':
            if (len(inp_list[1:]) != 0):
                print("Invalid input for 'q', length of input after q should be 0 but got {}.".format(len(inp_list[1:])))
                return reprompt
#     print("reprompt = " + str(reprompt))
    reprompt = 0
    return reprompt

INPUT_OPT_STR = "Do you want to manually enter the data or use commands from files? Type m(manually) / f(file): ";
#input
#[a,1,1,1]
#[1,1,1]
def input_device_model_readfile(devices_data: {dict}, p_string: str, inputList:list)->list:
    if type(devices_data) == set:
        z = zip(range(1, len(devices_data)+1), sorted(devices_data))
        str_range = set(str(x) for x in range(1, len(devices_data)+1))
        inp = inputList[0]
        input_dict = dict(zip(range(1, len(devices_data)+1), sorted(devices_data)))
        
        if not inp in devices_data:
            inp = input_dict[int(inp)]
            
        print('selected: {}'.format(inp))
        return [inp]
    else:
        keys_set = set(devices_data.keys())
        z = zip(range(1, len(keys_set)+1), sorted(keys_set))
        str_range = set(str(x) for x in range(1, len(devices_data)+1))
        #This is the input that the program will prompt the use to input
        inp = inputList[0]
        #print("ELSE: input: ")
        #print(inp)
        input_dict = dict(zip(range(1, len(keys_set)+1), sorted(keys_set)))
        
        if not inp in keys_set:
            inp = input_dict[int(inp)]
            
        p_string += '{}:'.format(inp)
        to_return = [inp]
        print('selected: {}'.format(inp))
        to_return.extend(input_device_model_readfile(devices_data[inp], p_string,inputList[1:]))
            
        return to_return


def input_device_model(devices_data: {dict}, p_string: str)->list:
    if type(devices_data) == set:
        z = zip(range(1, len(devices_data)+1), sorted(devices_data))
        str_range = set(str(x) for x in range(1, len(devices_data)+1))
        inp = input_str('Which type of {} device do you want to choose? {}: '.format(p_string,
                        sorted(z)), valid=devices_data.union(str_range))
#         print("Input_device_model: INPUT: ")
#         print(inp)
        input_dict = dict(zip(range(1, len(devices_data)+1), sorted(devices_data)))
        
        if not inp in devices_data:
            inp = input_dict[int(inp)]
            
        print('selected: {}'.format(inp))
        return [inp]
    else:
        keys_set = set(devices_data.keys())
        z = zip(range(1, len(keys_set)+1), sorted(keys_set))
        str_range = set(str(x) for x in range(1, len(devices_data)+1))
        #This is the input that the program will prompt the use to input
        inp = input_str('Which type of {} device do you want to choose? {}: '.format(p_string,
                        sorted(z)), valid=keys_set.union(str_range))
#         print("ELSE: input: ")
#         print(inp)
        input_dict = dict(zip(range(1, len(keys_set)+1), sorted(keys_set)))
        
        if not inp in keys_set:
            inp = input_dict[int(inp)]
            
        p_string += '{}:'.format(inp)
        to_return = [inp]
        print('selected: {}'.format(inp))
#         print("ELSE: about to call input_device_model again")
        to_return.extend(input_device_model(devices_data[inp], p_string))
            
        return to_return

def input_at_interval(ig_list: ['InputGenerator'], time_interval: int):
    '''helper function for running the simulation'''
    for inp_gen in ig_list:
        rlen = range(1, len(inp_gen.states())+1)
        str_rlen = set(str(x) for x in rlen)
        state = input_str('Which of the following states is \"{}\" in {}: '.format(inp_gen.dev_name,\
                          sorted(zip(rlen, sorted(inp_gen.states())))), valid=inp_gen.states().union(str_rlen))

        input_dict = dict(zip(rlen, sorted(inp_gen.states())))
        if not state in sorted(inp_gen.states()):
            state = input_dict[int(state)]

        inp_gen.write_on_state(state, time_interval)

def run_sim(integration_period: int, input_generators: list):
    '''runs the simulation that creates the input csv'''

    while True:
        print()
        time_interval = input_int('How long is this time interval (in minutes)[enter 0 to end the simulation]: ')
        if time_interval == 0:
            return
        num_periods_interval = int(60 / integration_period * time_interval)
        input_at_interval(input_generators, num_periods_interval)
        
def _process_inputList_readfile(inp_list:list)->list:
    new_list = []
    for old_item in inp_list:
        new_list.append(old_item.strip())
    return new_list        

def run_sim_state(integration_period: int, input_generators: list):
    while True:
        for inp_gen in input_generators:
            rlen = range(1, len(inp_gen.states())+1)
            str_rlen = set(str(x) for x in rlen)
            state = input_str('Which of the following states is \"{}\" in {}[enter 0 to end the simulation]: '.format(inp_gen.dev_name,\
                                sorted(zip(rlen, sorted(inp_gen.states())))), valid=inp_gen.states().union(str_rlen))
            if state == '0':
                return
            input_dict = dict(zip(rlen, sorted(inp_gen.states())))
            if not state in sorted(inp_gen.states()):
                state = input_dict[int(state)]
            time_interval = input_int('How long is this time interval (in minutes)[enter 0 to end the simulation]: ')
            if time_interval == 0:
                return
            num_periods_interval = int(60 / integration_period * time_interval)
            inp_gen.write_on_state(state, num_periods_interval)



if "__main__" == __name__:

    # DUPLICATION CHECKS
    name_gen = NameGenerator()
    # key -> name of device "type brand model", value -> its data
    device_map = {}
    
    #Error Handling: File Exist
    file_location = INPUT_XML
    exist_flag = Path(file_location)
    if exist_flag.exists() == False :
        print("Error: XML file does not exist")
        print("Program Quit")
        sys.exit(1)
    
    #Error Handling: File Parsing
    try:
        # Parse xml
        tree = parse_data(file_location)
    except:
        print("Error: Unable to parse XML file")
        print("Program Quit")
        sys.exit(1);
    
    # All labels {class,type,brand,model} without any data
    devices_data = parse_groupings(tree)
    # devices_data = reorder_tree(devices_data)
    

    while True:
        #Ask user if they want to manually input or read from a file.
        inputOption = input_str(INPUT_OPT_STR, valid = {'m', 'f'}).lower()
        
        if inputOption == 'm': #User choose to input data manually
            inp = input_str(MENU_STR, valid={'a', 'd', 'p', 'r', 'q'}).lower()
            print()
            '''
            a = add. 
            a -> add devices. there are data inside the devices. After adding devices, we are pulling data of those devices from
            csv files.
            '''
            if inp == 'a':
                # dev_key[list of choice by steps]
                dev_key = input_device_model(devices_data, '')
                # key -> "type+brand+model", value -> power and etc
                key,value = search_data(tree, dev_key)
                # name_gen.generate_name checks DUPLICATES and add a number at the end if DUPLICATED
                device_map[name_gen.generate_name(key)] = value
            elif inp == 'd':
                valid = set(device_map.keys())
                if len(valid) > 0:
                    to_delete = input_str('Which device do you want to delete? {}: '.format(valid), valid)
                    del device_map[to_delete]
                else:
                    print('There are no devices to delete\n')
            elif inp == 'p':
                pprint(device_map)
            elif inp == 'r':
                input_generators = make_input_generators(device_map)
                # Get Integration Period
                integration_period = input_int('Enter integration period for simulation calculation framework (whole seconds): ')
                # Get Periods
                run_sim_state(integration_period, input_generators)
                # run_sim(integration_period, input_generators)
    
                # pickle run_perams
                with open(OUTPUT_PICKLE,'wb') as fd:
                    pickle.dump({'integeration_period':integration_period,'device_map':device_map}, fd)
    
                # write info file
                write_to_ifile(OUTPUT_CSV, integration_period, input_generators)
                # write copy of the pickle file
                write_to_peramfile(OUTPUT_CONFIG, integration_period, device_map)
                
                print ("CSV File Input Gen:")
                print(input_generators)
                print ("Integration Period:")
                print(integration_period)
                print ("Device Map:")
                print(device_map)
    
                # Quit the Program after Simulation
                exit(0)
    
            elif inp == 'q':
                exit(0)
    
            print()
        #From here, the user wants to get input from a file instead of manually typing them above.
        else:
            print("Read from file: ElectricDeviceInput.txt to get input")
            try:
                inputFile = open("ElectricDeviceInput.txt", "r")
                for line in inputFile:
                    raw_list = line.strip().strip(',').split(',')
                    inp_list = _process_inputList_readfile(raw_list)
                    inp = inp_list[0] #comment up to here out later after check input
                    flag = check_idm_readfile(inp_list) #check for invalid input by length of list from file input
                    if(flag == 1):
                        print("Re-prompt\n\n")
                        
                    else:
                        if inp == 'a':
                            print("Adding a device to simulation: \n")
                            # dev_key[list of choice by steps]
                            dev_key = input_device_model_readfile(devices_data, '', inp_list[1:])
                            # key -> "type+brand+model", value -> power and etc
                            key,value = search_data(tree, dev_key)
                            # name_gen.generate_name checks DUPLICATES and add a number at the end if DUPLICATED
                            device_map[name_gen.generate_name(key)] = value
                            print("\nFinish adding.\n")
                        elif inp == 'd':
                            print("Deleting a device from simulation: \n")
                            valid = set(device_map.keys())
                            if len(valid) > 0:
                                to_delete = inp_list[1]
                                del device_map[to_delete]
                                print("Deleted " + str(inp_list[1]))
                            else:
                                print('There are no devices such as "{}" to delete\n'.format(inp_list[1]))
                        elif inp == 'p':
                            print("Printing current devices in simulation: \n")
                            pprint(device_map)
                        elif inp == 'r':
                            print("Running scheduler on selected devices, display output, Quit\n")
                            input_generators = make_input_generators(device_map)
                            # Get Integration Period
                            integration_period = inp_list[1]
                            # Get Periods
                            run_sim_state(integration_period, input_generators)
                            # run_sim(integration_period, input_generators)
                 
                            # pickle run_perams
                            with open(OUTPUT_PICKLE,'wb') as fd:
                                pickle.dump({'integeration_period':integration_period,'device_map':device_map}, fd)
                 
                            # write info file
                            write_to_ifile(OUTPUT_CSV, integration_period, input_generators)
                            # write copy of the pickle file
                            write_to_peramfile(OUTPUT_CONFIG, integration_period, device_map)
                             
                            print ("CSV File Input Gen:")
                            print(input_generators)
                            print ("Integration Period:")
                            print(integration_period)
                            print ("Device Map:")
                            print(device_map)
                 
                            # Quit the Program after Simulation
                            exit(0)
                 
                        elif inp == 'q':
                            print("Quit.\n")
                            exit(0)
                 
                        print()
                    #From here, the user wants to get input from a file instead of manually typing them above.
                                        
            except FileNotFoundError:
                print("The file does not exist")
                    
                    
        
    
        
            
            
            
            
