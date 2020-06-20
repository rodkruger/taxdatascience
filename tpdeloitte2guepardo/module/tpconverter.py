"""
tpconverter.py:
    Converts a Deloitte Transfer Pricing file format to Guepardo Transfer
    Pricing file format
"""

__author__ = "Rodrigo Krüger"
__copyright__ = "Copyright 2020, FH Guepardo"
__credits__ = ["Rodrigo Krüger"]
__version__ = "1.0.0"
__maintainer__ = "Rodrigo Krüger/FH Consulting"
__email__ = "rodrigo.kruger@fh.com.br"
__status__ = "Production"

###############################################################################
# --- IMPORT MODULES
###############################################################################
import mimetypes
import os.path


###############################################################################
# --- GLOBAL VARIABLES
###############################################################################


###############################################################################
# --- FUNCTIONS DEFINITIONS
###############################################################################

def check_source_file_type(origin_file):
    """ Check if the source file is a text/file """

    return mimetypes.guess_type(origin_file)[0].find('text') >= 0


def convert_file(origin_file, target_folder):
    """ Starts the file conversion. Checks the existence of the file and
    target folder, and then starts the conversion """

    is_validated = True

    # Verify if the source file exists, and is a text/plain file
    if not verify_source_exists(origin_file):
        is_validated = False
        print("Source file does not exist! Please check!")
    else:
        if not check_source_file_type(origin_file):
            is_validated = False
            print("Source file is not a text/plain file! Please check!")

    # Verify that the target folder exists
    if not verify_target_exists(target_folder):
        is_validated = False
        print("Target folder  does not exist! Please check!")

    # Check if all validations above were done successfully
    if not is_validated:
        print("There were errors during the execution. Please clear them and retry!")
        return

    # Everything ok! Let's do the conversion
    blocks = make_conversion(origin_file, target_folder)
    export_data_to_file(blocks, target_folder)


def export_data_to_file(blocks, target_folder):
    """ Export each block in the dictionary for a specific file  """

    # Iterate over all the block keys, and export the list with all lines for
    # a specific file
    for block_key in blocks:

        # Update a file, with the name equals to the Block Key
        file = open(target_folder + block_key + ".txt", "wt")

        # Read the data previously splitted
        block_data = blocks[block_key]

        # Write all the records in the list to the file
        for line_data in block_data:
            file.write("|".join(line_data))


def make_conversion(origin_file, target_folder):
    """
     Make the conversion to the final formats, considering that the original
     file is already synthatically checked
    """

    # Open the source file
    file = open(origin_file)

    # Initialize a dictionary, where the Key is the ECF Block Code
    blocks = {}

    # For each file, let's put the information into the corresponding block
    for line in file:

        # Read the raw line data
        line_data = line.split("|")

        # Get the Block Key (X200, X300, X310, etc)
        block_key = line_data[1]

        if not block_key:
            continue

        # Assume that there is no data into the corresponding line
        block_data = []

        # If the corresponding key is present in the dictionary, that means
        # there is information present there that needs to be appended. If no,
        # a blank list is already initialized in the previous statement
        if block_key in blocks:
            block_data = blocks[block_key]

        # Append the raw line data into the dictionary block
        block_data.append(line_data)

        # Update the dictionary with new data
        blocks[block_key] = block_data

    return blocks


def verify_source_exists(origin_file):
    """ Verify that source file exists """

    return os.path.exists(origin_file)


def verify_target_exists(target_folder):
    """ Verify that both target exist """

    return os.path.exists(target_folder)


###############################################################################
# - MAIN EXECUTION
###############################################################################

# print("Enter the Deloitte's transfer pricing file path: ")
# origin_file_path = input()
# print("Enter the target folder [C:\\temp]: ")
# target_path = input()

origin_file_path = "/home/rkruger/github.com/rodkruger/taxdatascience/tpdeloitte2guepardo/data/tpdeloitte.txt"
target_path = "/home/rkruger/github.com/rodkruger/taxdatascience/tpdeloitte2guepardo/data/target/"

convert_file(origin_file_path, target_path)
