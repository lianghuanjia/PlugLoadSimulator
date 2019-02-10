def write_to_ifile(file_name: str, integration_period: int, input_generators: list):
    '''writes the strings generated by the string generators onto the input csv'''
    with open(file_name, 'w') as outfile:
        to_write = 'sample_rate:{}\n'.format(integration_period)
        for input_generator in input_generators:
            to_write += input_generator.generate_str()
        outfile.write(to_write)

def write_to_peramfile(file_name: str, integration_period: int, device_map: dict):
    '''writes the strings generated by the string generators onto the input csv'''
    with open(file_name, 'w') as outfile:
        to_write = 'sample_rate:{}\n'.format(integration_period)
        to_write += str(device_map)
        outfile.write(to_write)
