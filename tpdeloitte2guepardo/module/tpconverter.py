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
# - IMPORT MODULES
###############################################################################
import mimetypes
import os.path

###############################################################################
# - GLOBAL VARIABLES
###############################################################################

# File to be converted
origin_file_path = ""

# Directory to write the converted files
target_path = ""


###############################################################################
# - FUNCTIONS DEFINITIONS
###############################################################################

def check_source_file_type(origin_file):
    """ Check if the source file is a text/file """

    return mimetypes.guess_type(origin_file)[0].find('text') >= 0


def convert_file(origin_file, target_folder):
    """ Starts the file conversion. Checks the existence of the file and
    target folder, and then starts the conversion """

    is_validated = True

    # Verify that source and target exists
    if not verify_source_exists(origin_file):
        is_validated = False
        print("Source file does not exist! Please check!")
    else:
        if not check_source_file_type(origin_file):
            is_validated = False
            print("Source file is not a text/plain file! Please check!")

    if not verify_target_exists(target_folder):
        is_validated = False
        print("Target folder  does not exist! Please check!")

    if not is_validated:
        print('There were errors during the execution. Please clear them and retry!')


def verify_source_exists(origin_file):
    """ Verify that source file exists """

    return os.path.exists(origin_file)


def verify_target_exists(target_folder):
    """ Verify that both target exist """

    return os.path.exists(target_folder)


###############################################################################
# - MAIN EXECUTION
###############################################################################

print("Enter the Deloitte's transfer pricing file path: ")
origin_file_path = input()
print("Enter the target folder [C:\\temp]: ")
target_path = input()
convert_file(origin_file_path, target_path)
