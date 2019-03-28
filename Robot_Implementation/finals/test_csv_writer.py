import csv

with open("eYRC#AB#226.csv",'w') as file:
    writer = csv.writer(file)
    l = [['SIM 0','4'],['SIM 1','56'],['SIM 2','194'],['SIM 3','121']]
    writer.writerows(l)