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

#######################################################################################################################
# --- IMPORT MODULES
#######################################################################################################################
import mimetypes
import os.path

import pandas as pd

#######################################################################################################################
# --- CONSTANTS
#######################################################################################################################

DATA_EXCEL_EXTENSION = '.xlsx'
SEPARATOR = '|'
TEMPLATE_EXCEL_EXTENSION = '.xlsx'
TEMPLATE_EXCEL_SHEET_NAME = 'Planilha1'


#######################################################################################################################
# --- GLOBAL VARIABLES
#######################################################################################################################


#######################################################################################################################
# --- FUNCTIONS DEFINITIONS
#######################################################################################################################

def check_source_file_type(origin_file):
    """
    Check if the source file is a text/file

    :param origin_file: origin file, where contains the data
    :return: True - if the file is text/plain; False - if the file is not text/plain
    """

    return mimetypes.guess_type(origin_file)[0].find('text') >= 0


def convert_file(origin_file, target_folder, template_path):
    """
    Starts the file conversion. Checks the existence of the file and target folder, and then starts the conversion

    :param origin_file: origin file, where contains the data
    :param target_folder: the folder where the target files will be written
    :param template_path: the path for the excel templates
    :return: None
    """

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
    blocks = make_conversion(origin_file)

    # Export the data to .csv file
    export_data_to_file(blocks, target_folder)

    # Read the headers from the templates
    template_headers = read_excel_header_templates(blocks, template_path)

    # Export the data to Excel File
    export_data_to_excel(blocks, target_folder, template_headers)


def export_data_to_file(blocks, target_folder):
    """
    Export each block in the dictionary for a specific file

    :param blocks: a dictionary, where the key is the ECF block key
    :param target_folder: the folder where the target files will be written
    :return:
    """

    # Iterate over all the block keys, and export the list with all lines for
    # a specific file
    for block_key in blocks:

        # Generate the target file name
        file_name = target_folder + block_key + ".txt"

        # Update a file, with the name equals to the Block Key
        file = open(file_name, "wt")

        # Read the data previously splitted
        block_data = blocks[block_key]

        # Write all the records in the list to the file
        for line_data in block_data:
            file.write(SEPARATOR.join(line_data))


def export_data_to_excel(blocks, target_folder, template_headers):
    """
    Export each block in the dictionary for a specific Excel Spreadsheet

    :param blocks: a dictionary, where the key is the ECF block key
    :param target_folder: the folder where the target files will be written
    :return:
    """

    # Iterate over all the block keys, and export the list with all lines for
    # a specific file
    for block_key in blocks:

        # Read the data previously splitted
        block_data = blocks[block_key]

        # Create a Pandas Dataframe with the data
        df = pd.DataFrame(block_data)

        # Verify it there is template header name
        if block_key in template_headers:

            # Get the template header names
            template_header = template_headers[block_key]

            # Let the template_header and colums with the same size. Pandas throws an exception if they are different
            while len(template_header) < len(df.columns):
                template_header.append("No_name")

            while len(template_header) > len(df.columns):
                del template_header[-1]

            # Put the new names into the DataFrame
            df.columns = template_header

        # Generate the target file name
        file_name = target_folder + block_key + DATA_EXCEL_EXTENSION

        # Create a Writer to export the data to an Excel Spreadsheet
        writer = pd.ExcelWriter(file_name, engine="xlsxwriter")

        # Export the data to the spreadsheet
        df.to_excel(writer, sheet_name='Data', index=False)

        # Save the data to the file
        writer.save()


def make_conversion(origin_file):
    """
    Make the conversion to the final formats, considering that the original
    file is already syntactically checked

    :param origin_file: origin file, where contains the data
    :return: a dictionary, where the key is the ECF block key
    """

    # Open the source file
    file = open(origin_file)

    # Initialize a dictionary, where the Key is the ECF Block Code
    blocks = {}

    # For each file, let's put the information into the corresponding block
    for line in file:

        # Read the raw line data
        line_data = line.split(SEPARATOR)

        # Get the Block Key (X200, X300, X310, etc)
        block_key = line_data[1]

        # If there is no block key, there is nothing to do. Continue!
        if not block_key:
            continue

        # Assume that there is no data into the corresponding line
        block_data = []

        # If the corresponding key is present in the dictionary, that means there is information present there that
        # needs to be appended. If no, a blank list is already initialized in the previous statement
        if block_key in blocks:
            block_data = blocks[block_key]

        # A particular situation in Block X300 and X320. It is need to propagate into its sequentially down child the
        # X300 index. So, we keep the value here, to propagate the same index into the immediatelly down childs
        if block_key == "X300" or block_key == "X320":
            x300_index = line_data[2]

        # In the blocks X310 and 330, we propagate the X300 / 320 index in the childs
        if block_key == "X310" or block_key == "X330":
            line_data.insert(2, x300_index)

        # Remove the first field, that is the block identifier. This is not necessary in the final file
        del line_data[0:2]

        # Append the raw line data into the dictionary block
        block_data.append(line_data)

        # Update the dictionary with new data
        blocks[block_key] = block_data

        # Keep the last Block Key, to control the indexes of the Block X300
        # and X310
        previous_block_key = block_key

    return blocks


def read_excel_header_templates(blocks, template_path):
    """
    Read the Excel file header and returns a dictionary indexed by the block key, in order to use the same column
    names as used in the templates

    :param blocks: a dictionary, where the key is the ECF block key
    :param template_path: the path where there is the templates to read some information
    :return:
    """

    # Initialize a dictionary, where the Key is the ECF Block Code
    template_headers = {}

    # Iterate over all the block keys, and export the list with all lines for
    # a specific file
    for block_key in blocks:
        # Generate the target file name
        file_name = template_path + block_key + TEMPLATE_EXCEL_EXTENSION

        try:
            # Read the excel file template
            excel_df = pd.read_excel(file_name, sheet_name=TEMPLATE_EXCEL_SHEET_NAME)

            # Get the column names from the template, and put them in a list
            header_data = excel_df.columns.tolist()

            # Put the list in the specific ECF key block
            template_headers[block_key] = header_data
        except FileNotFoundError:
            print("File {0} not found. Skipping it! Please check!".format(file_name))

    return template_headers


def verify_source_exists(origin_file):
    """
    Verify if the source file exists

    :param origin_file: origin file, where contains the data
    :return: True - if the file exists ; False - if the file does not exist
    """

    return os.path.exists(origin_file)


def verify_target_exists(target_folder):
    """
    Verify if the target folder exist

    :param target_folder: there folder to put the target files
    :return: True - if the folder exists ; False - if the folder does not exist
    """

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
template_path = "/home/rkruger/github.com/rodkruger/taxdatascience/tpdeloitte2guepardo/template/"

convert_file(origin_file_path, target_path, template_path)
