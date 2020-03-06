from src.AdvGetFileVersion import AdvGetFileVersion
from src.AdvErrors import ResolveCoreCodeMessage

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

# Exercise ResolveCoreCodeMessage()
assert ResolveCoreCodeMessage(0x81001014).startswith('The requested frame cannot')
print('\nResolveCoreCodeMessage test 1 passed')

assert ResolveCoreCodeMessage(0x81001014, kind='enum').startswith('E_ADV_FRAME_MISSING')
print('ResolveCoreCodeMessage test 2 passed')

assert ResolveCoreCodeMessage(0x91001014).startswith('0x91001014 is not')
print('ResolveCoreCodeMessage test 3 passed')

