# Test script for yasper.py

from yasper import Yasper

def ycdi(data):
    return yc() + di()

def yc():
    return "You can "

def di():
    return "do it!"

yasper = Yasper()
yasper.registerFunction("add", lambda data: sum([int(x) for x in data]), -1)
yasper.registerFunction("addn", lambda data: "n", -1)
yasper.registerFunction("subtract", lambda data: int(data[0]) - int(data[1]), 2)
yasper.registerFunction("encourage", ycdi, 0)
yasper.initialize()
# Note that errors in the following statements will print "None" to the console
# in addition to the errors, because we're not checking for None before printing
# the results
print(str(yasper.execute("add 2 4 6 8")))       # 20
print(str(yasper.execute("addqwerty 2 4 6 8"))) # 20 [overcompletion]
print(str(yasper.execute("addn 2 4 6 8")))      # n
print(str(yasper.execute("addnfwef 2 4")))      # n [overcompletion]
print(str(yasper.execute("ad 2 4 6 8")))        # Error [ambiguous]
print(str(yasper.execute("subtract 20 3")))     # 17
print(str(yasper.execute("s 20 3")))            # 17 [undercompletion]
print(str(yasper.execute("subtract 20 3 5")))   # 17 [extra arguments are ignored]
print(str(yasper.execute("subtract 20")))       # Error [too few arguments]
print(str(yasper.execute("encourage")))         # You can do it!
print(str(yasper.execute("yabusa")))            # Error [unexpected command]