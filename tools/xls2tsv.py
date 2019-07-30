# Name: xls2tsv.py
# Since: July 30th, 2019
# Author: Christen Ford
# Description: Converts XLS/XLSM documents to TSV format. I have explicitly chosen to TSV over CSV as there are certain well-known programs and libraries that actively choose not to support CSV files (such as SQL Server). Whereas TSV files seem more universally supported.

# Import standard libraries
import csv, sys, os

# Import click for CLI
import click

# Import openpyxl and its utility library
import openpyxl as pyxl
import openpyxl_utilities as utils


def get_outfile(filepath, worksheet):
    '''
    Helper function used to generate output filenames.
    Mandatory Arguments:
        filepath: The path to the XLS/XLSM document.
        worksheet: The name of the worksheet.
    '''
    # Get the workbooks name
    parts = filepath.split(os.pathsep)
    filename = parts[-1]
    # Strip off the file extension, throw an error if unsupported filetype
    if filename.endswith('.xls'):
        filename = filename.rstrip('.xls')
    elif filename.endswith('.xlsm'):
        filename = filename.rstrip('.xlsm')
    else:
        raise ValueError('Unsupported filetype detected!')
    # Construct the outfile name to return
    outfile = '{}_{}.tsv'.format(filename, worksheet)
    # return the outfile name
    return outfile


def write_outfile(ws_handle, outfile):
    '''
    Helper function that dumps the contents of a worksheet to a Tab separated
    value file.
    Arguments:
        ws_handle: The handle for a worksheet.
        outfile: The filepath to dump to.
    '''
    try:
        #TODO: Open a tsv file using the csv lib and write out to it
        pass
    except BaseException as e:
        raise e


@click.command()
@click.argument('infile')
@click.option('-of', '--outfile', default=None, help='The file to write the converted tsv to.')
@click.option('-ws', '--worksheet', default=None, help='The worksheet to convert.')
@click.option('-v', '--verbose', default=False, is_flag=True, help='Will print additional information if set.')
def convert_command(infile, outfile, worksheet, verbose):
    '''
    Attempts to convert the XLS/XLSM file pointed to by filename to a TSV file. If there is more than one worksheet in the book, then each worksheet will produce an additional tsv file with the filename: '[workbook]_[worsheet].tsv'.
    Mandatory Arguments:
        filename: The path to the XLS/XLSM document.
    Optional Arguments:
        -of/--outfile: The path to write the converted tsv file to.
        -ws/--worksheet: The worksheet to convert. If there is more than one worksheet in the workbook and this option is specified, only this worksheet will be converted to a tsv.
        -v/--verbose: Prints more information during runtime if set.
    '''
    try:
        # Attempt to open the workbook
        wb_handle = pyxl.load_workbook(filename=infile, read_only=True))

        # Start writing a single file if necessary
        if worksheet and worksheet in wb_handle:
            if not outfile:
                outfile = get_outfile()
        # Otherwise, write all sheets in the book
        else:
            for ws_name in wb.keys():
                ws_handle = workbook[ws_name]




    except OSError as e:
        click.secho('An OSError occurred during processing!', fg='red')
        if verbose:
            click.secho(str(e). fg='red')
        sys.exit(-1)
    except IOError as e:
        click.secho('An IOError occurred during processing!', fg='red')
        if verbose:
            click.secho(str(e), fg='red')
        sys.exit(-1)
    except BaseException as e:
        click.secho('An error occurred during processing!', fg='red')
        if verbose:
            click.secho(str(e), fg='red')
        sys.exit(-1)


if __name__ == '__main__':
    convert_command()
