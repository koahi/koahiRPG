import os

classDictionary={}
for module in os.listdir(os.path.dirname(__file__)):
        if module.endswith(".py") and module!="__init__.py":
                print module[:-3]
                exec("from "+module[:-3]+" import "+module[:-3])
                classDictionary[module[:-3]]=eval(module[:-3])
del module

