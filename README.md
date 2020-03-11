Adv2reader
==========

This package provides a 'reader' for .adv files.

The specification for the Astro Digital Video version 2 files can be found at: (TBD)

To install this package on your system:

    pip install Adv2reader

Then, sample usage is:

    from adv2reader import *
    
    rdr = None
    try:
        # Create a 'reader' for the given file
        rdr = Adv2reader(r'..\ver2-test-file.adv')
    except AdvLibException as adverr:
        # The file could not be found or was not a version 2 .adv file
        print(repr(adverr))
        exit()

Now that the file has been opened and a 'reader' created for it, 
there are instance variables available that will be useful.
Here we print some of those out:

    print(f'Width: {rdr.Width}  Height: {rdr.Height}  NumMainFrames: {rdr.CountMainFrames}')

There is an instance variable called `FileIno` which gives access to all
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
In that case, `image` will contain a numpy array of uint16 values.

The 'shape' of image will be `image[Height, Width]` for grayscale images
and `image[Height, Width, colorChannel]` (where colorChannel is 0, 1, or 2)
in the case of a color image.

Finally, the file should closed as in the example below:

    print(f'closeFile returned: {rdr.closeFile()}')
    
The value returned will be the version (2) of the file closed or 0, which indicates an attempt to close a file that was
already closed.
