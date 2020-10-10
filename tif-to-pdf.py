import os
import sys
import argparse
from PIL import Image, ImageSequence


def isTif(path):
    """
    Test whether a path is a valid tif file or not.
    :param path: the path of the file to be checked
    :returns: True if path is found to be a valid tif file, False otherwise
    """
    return (path.lower().endswith('.tif') or path.lower().endswith('.tiff')) and os.path.isfile(path)


def saveAsPDF(img, opfile):
    """
    Save a specified PIL image as PDF.
    :param img: PIL image to be saved as PDF
    :param dir: output directory for the PDF
    """
    # Get the frames in the .tif file
    pages = [imPage.convert('RGB') for imPage in ImageSequence.Iterator(img)]
    for i, page in enumerate(pages):
        try:
            if(i == 0):
                page.save(opfile, append=False, resolution = page.size[0]/9.0)
            else:
                page.save(opfile, append=True, resolution = page.size[0]/9.0)
        except PermissionError:
            print('Error: Permission to write file denied.', file=sys.stderr)
            exit(1)


def update_progress(progress):
    barLength = 20 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), int(progress*1000)/10.0, status)
    print(text, end='\r')


if __name__ == '__main__':
    # Setup argument parser.
    parser = argparse.ArgumentParser(
        description = 'Convert multipage .tif files to .pdf files.')
    parser.add_argument("input", 
        help = "The directory containing .tif files to be converted.")
    parser.add_argument("-o", "--output", type = str,
        help = "The directory to which to write converted .pdf files.")
    args = parser.parse_args()
    
    # Open input directory and get .tif filepaths. Exit if directory is
    # not found.
    ipdir = str(os.path.abspath(args.input))
    print('Input directory: ' + ipdir)
    try:
        files = [os.path.join(ipdir, fp) for fp in os.listdir(ipdir)]
        print(str(len(files))+' files/folders in ' + ipdir)
    except FileNotFoundError:
        print ('Fatal error: Input directory not found.', file=sys.stderr)
        exit(1)
    tifs = [f for f in files if(isTif(f))]
    print(str(len(tifs))+' .tif files in ' + ipdir)
    
    # Set output directory according to arguments. Create the directory
    # if it does not exist.
    if(args.output == None):
        opdir = os.path.join(ipdir, 'pdfs')
    else:
        opdir = args.output
    if(not os.path.exists(opdir)):
        os.makedirs(opdir)
    
    # Open each .tif image using PIL and save it as .pdf in the output
    # directory 
    for i, tif in enumerate(tifs):

        img = Image.open(tif)
        filename = os.path.splitext(os.path.split(tif)[1])[0] + '.pdf'
        saveAsPDF(img, os.path.join(opdir, filename))
        update_progress((float(i)+1)/len(tifs))