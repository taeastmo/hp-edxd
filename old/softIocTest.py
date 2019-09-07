from epics import PV

my_pv = PV('temperature:fname')

t = my_pv.get()

print(t)

my_pv.put('hello!')

t = my_pv.get()

print(t)
