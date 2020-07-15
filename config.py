import configparser

name = 'dupa'
lh = 123
hh = 213
ls = 4214
hs = 213
lv = 231
hv = 324
la = 344
ha = 4000


def saveConfig(name, lh, hh, ls, hs, lv, hv, la, ha):
    config = configparser.ConfigParser()
    config[name] = {'Low Hue': lh,
                    'High Hue': hh,
                    'Low Sat': ls,
                    'High Sat': hs,
                    'Low Val': lv,
                    'High Val': hv,
                    'Low Area': la,
                    'High Area': ha}
    config['polygon'] = [[361, 134], [602, 133], [603, 318], [371, 320]]

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def loadConfig():
    config = configparser.ConfigParser()
    config.read('config.ini')
    for key in config[name]:
        print(config[name][key])



saveConfig(name, lh, hh, ls, hs, lv, hv, la, ha)

loadConfig()
