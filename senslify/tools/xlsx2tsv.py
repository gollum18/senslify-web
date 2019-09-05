# THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
# APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
# HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT
# WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
# PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE
# DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR
# CORRECTION.

# Name: xls2tsv.py
# Since: July 30th, 2019
# Author: Christen Ford
# Description: Converts XLS/XLSM documents to TSV format. I have explicitly 
#   chosen TSV over CSV as there are certain well-known programs and 
#   libraries that actively choose not to support CSV files (such as SQL Server). 
#   Whereas TSV files seem more universally supported.
# This converter *should* work with indiscrimately large files without penalty.

# Import standard libraries
import csv, sys, os

# Import click for CLI
import click

# Import openpyxl and its utility library
import openpyxl as pyxl
import openpyxl_utilities as utils


def get_outfile(filepath, worksheet=None):
    """Helper function used to generate output filenames.
    
    Args:
        filepath (str): The path to the XLS/XLSM document.
        worksheet (str): The name of the worksheet.
    """
    # Get the workbooks name
    parts = filepath.split(os.pathsep)
    filename = parts[-1]
    # Strip off the file extension, throw an error if unsupported filetype
    if filename.endswith('.xlsx'):
        filename = filename.rstrip('.xlsx')
    elif filename.endswith('.xlsm'):
        filename = filename.rstrip('.xlsm')
    else:
        raise ValueError('Unsupported filetype detected!')
    # Construct the outfile name to return
    if worksheet:
        outfile = '{}_{}.tsv'.format(filename, worksheet)
    else:
        outfile = '{}.tsv'.format(filename)
    # return the outfile name
    return outfile


def write_outfile(ws_handle, outfile):
    """Helper function that dumps the contents of a worksheet to a Tab 
    separated value file.
    
    Args:
        ws_handle (openpyxl.worksheet.worksheet): The handle for a worksheet.
        outfile (str): The filepath to dump to.
    """
    with open(outfile, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t', 
            quotechar="\"", quoting=csv.QUOTE_MINIMAL)
        for raw_row in ws_handle.rows:
            row = []
            for cell in raw_row:
                row.append(cell.value)
            writer.writerow(row)


@click.command()
@click.argument('infile')
@click.option('-of', '--outfile', default=None, help='The file to write the converted tsv to.')
@click.option('-ws', '--worksheet', default=None, help='The worksheet to convert.')
@click.option('-v', '--verbose', default=False, is_flag=True, help='Will print additional information if set.')
def main(infile, outfile, worksheet, verbose):
    """Attempts to convert the XLS/XLSM file pointed to by INFILE to a TSV 
    file. If there is more than one worksheet in the book, then each worksheet 
    will produce an additional tsv file with the filename: 
    '[workbook]_[worsheet].tsv'.
    
    Args:
        infile (str): Path to the input file.
        outfilke (str): Path to the output file.
        worksheet (str): The name of the worksheet to convert.
        verbose (boolean): Whether to verbosely output information or not.
    """
    try:
        # Attempt to open the workbook
        wb_handle = pyxl.load_workbook(filename=infile, read_only=True)

        # Check if the user specified a sheet
        if worksheet and worksheet in wb_handle:
            if not outfile:
                outfile = get_outfile(infile, worksheet)
        # Otherwise write a single sheet if the book has one page or all pages
        #   othwerise
        elif not worksheet:
            if len(wb_handle.sheetnames) == 1:
                # get the handle, and file name
                ws_handle = wb_handle.active
                outfile = get_outfile(infile)
                # write the outfile
                write_outfile(ws_handle, outfile)
            else:
                for ws_name in wb.keys():
                    # get a handle to the current sheet, build its outfile name
                    ws_handle = wb_handle[ws_name]
                    outfile = get_outfile(infile, ws_name)
                    # write the outfile
                    write_outfile(ws_handle, outfile)

    except OSError as e:
        click.secho('An OSError occurred during processing!', fg='red')
        if verbose:
            click.secho('{}'.format(e), fg='red')
        sys.exit(-1)
    except IOError as e:
        click.secho('An IOError occurred during processing!', fg='red')
        if verbose:
            click.secho('{}'.format(e), fg='red')
        sys.exit(-1)


if __name__ == '__main__':
    main()
