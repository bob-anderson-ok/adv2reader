from AdvLib import *
from AdvError import ResolveErrorMessage

# Exercise AdvGetVersion()
err_msg, version_number1 = AdvGetFileVersion('non-existent_file.adv')
assert err_msg.startswith('Error - cannot find file')
print('\nAdvGetFileVersion test 1 passed')

err_msg, version_number2 = AdvGetFileVersion(r'..\ver2-test-file.adv')
assert err_msg == '' and version_number2 == 2
print('AdvGetFileVersion test 2 passed')

err_msg, version_number3 = AdvGetFileVersion(r'adv2_tests.py')
assert err_msg.startswith('Error - not an FSTF') and version_number3 == 0
print('AdvGetFileVersion test 3 passed')

# Exercise ResolveErrorMessage()
assert ResolveErrorMessage(0x81001014).startswith('The requested frame cannot')
print('\nResolveCoreCodeMessage test 1 passed')

assert ResolveErrorMessage(0x81001014, kind='enum').startswith('E_ADV_FRAME_MISSING')
print('ResolveCoreCodeMessage test 2 passed')

assert ResolveErrorMessage(0x91001014).startswith('0x91001014 is not')
print('ResolveCoreCodeMessage test 3 passed')

# Exercise AdvOpenFile
info_from_file = AdvFileInfo()  # Create struct to hold returned data

# Use an r'' (raw string) to specify the filepath so that the \ is
# not interpreted as an escape character
ret_value = AdvOpenFile(r'..\ver2-test-file.adv', info_from_file)

assert ret_value == 2
assert info_from_file.Width == 960
assert info_from_file.Height == 600
assert info_from_file.CountMainFrames == 102
assert info_from_file.CountCalibrationFrames == 0
assert info_from_file.DataBpp == 16
assert info_from_file.MaxPixelValue == 65535
assert info_from_file.MainClockFrequency == 1000
assert info_from_file.MainStreamAccuracy == 1
assert info_from_file.CalibrationClockFrequency == 1000
assert info_from_file.CalibrationStreamAccuracy == 1
assert info_from_file.MainStreamTagsCount == 0
assert info_from_file.CalibrationStreamTagsCount == 0
assert info_from_file.SystemMetadataTagsCount == 21
assert info_from_file.UserMetadataTagsCount == 0
assert info_from_file.UtcTimestampAccuracyInNanoseconds == 1000000
assert info_from_file.IsColourImage is False
assert info_from_file.ImageLayoutsCount == 1
assert info_from_file.StatusTagsCount == 5
assert info_from_file.ImageSectionTagsCount == 3
assert info_from_file.ErrorStatusTagId == -1
print('\nAdvOpenFile test 1 passed')