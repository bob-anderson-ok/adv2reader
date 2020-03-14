adv2reader
==========

This package provides a 'reader' for .adv (AstroDigitalVideo) files.

The specification for Astro Digital Video files can be 
found at: <http://www.astrodigitalvideoformat.org/spec.html>

To install this package on your system:

    pip install adv2reader

Then, sample usage is:

    from adv2reader import *
    from pathlib import Path
    
    rdr = None
    try:
        # Create a platform agnostic path to the test file (use forward slashes)
        file_path = str(Path('../ver2-test-file.adv'))  # Python will make Windows version as needed
        # Create a 'reader' for the given file
        rdr = Adv2reader(file_path)
    except AdvLibException as adverr:
        # The file could not be found or was not a version 2 .adv file
        print(repr(adverr))
        exit()

Now that the file has been opened and a 'reader' created for it, 
there are instance variables available that will be useful.
Here we print some of those out:

    print(f'Width: {rdr.Width}  Height: {rdr.Height}  NumMainFrames: {rdr.CountMainFrames}')

There is also an composite instance variable called `FileIno` which gives access to all
of the values defined in the structure `AdvFileInfo` (there are 20 of them).

For example:

    print(rdr.FileInfo.UtcTimestampAccuracyInNanoseconds)
    
The main thing that one will want to do is read image data and timestamps from image frames.
Continuing with the example:
  
    
    for frame in range(rdr.CountMainFrames):
        # frameInfo will contain the meta-data for the frame
        err, image, frameInfo = rdr.getMainImageData(frameNumber=frame)

        if not err:
            print(f'\nframe: {frame}')
            print(frameInfo.UtcMidExposureTimestampLo)
            print(frameInfo.UtcMidExposureTimestampHi)
            print(frameInfo.Exposure)

`err` is a string that will be empty if image bytes and metadata where successfully extracted.
In that case, `image` will contain a numpy array of uint16 values. If `err` is not empty, it will contain
a human-readle description of the error encountered.

The 'shape' of image will be `image[Height, Width]` for grayscale images. Color video
files are not yet supported.

Finally, the file should closed as in the example below:

    print(f'closeFile returned: {rdr.closeFile()}')
    rdr = None
    
The value returned will be the version number (2) of the file closed or 0, which indicates an attempt to close a file that was
already closed.
