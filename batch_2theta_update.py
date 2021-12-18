from hpm.models.mcaModel import MCA
from os import listdir
from os.path import isfile, join


##  WARNING do not run this unless you are sure

folder = '/Users/ross/Desktop/Cell2-HT'
new_two_theta = 7.956717 

def update_2theta(folder, files, two_theta):



    mca = MCA()


    for f in files:
        file = join(folder, f) 
        [file, ok] = mca.read_file(file)
        calibration = mca.get_calibration()[0]
        calibration.two_theta = two_theta
        mca.set_calibration([calibration])
        mca.write_file(file)
        print(file)


files = [f for f in listdir(folder) if isfile(join(folder, f))]

update_2theta(folder, files, new_two_theta)