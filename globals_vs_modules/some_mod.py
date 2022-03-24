from util import attach_to_globals

print('some_mod globals start:', list(globals().keys()))
attach_to_globals('some_mod_var', 'some_mod_value')
print('some_mod globals end:', list(globals().keys()))
