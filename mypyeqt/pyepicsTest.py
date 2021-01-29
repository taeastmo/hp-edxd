from epics import PV

pv = PV('OPS:message1')

val = pv.get()

print(val)