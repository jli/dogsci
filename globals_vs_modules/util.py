def attach_to_globals(name, val):
    print('attaching', name, val)
    # `globals` is always local to the module. would need to pass in globals if
    # want to attach to the module of the caller
    globals()[name] = val
    print('globals now:', list(globals().keys()))
