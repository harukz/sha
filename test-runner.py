import subprocess
import argparse
import csv

parser = argparse.ArgumentParser()
parser.add_argument('--debug', help='デバッグ用フラグ', action='store_true')
args = parser.parse_args()

# prompt and take input for start and end
# start = input("最小値を入力してください: ")
# end = input("最大値はを入力してください: ")

if (args.debug):
  print("デバッグは有効です。")

ns = []; cpus = []
with open('test_data.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader) 
    for row in reader:
        ns.append(row[0])
        cpus.append(row[1])


cpus = [float(cpu) for cpu in cpus]

left = 0
right = 99 
tgt = 0.8
# resolution = .5
# cnt = 0

def binary_search(left, right, data, value):
    while left <= right:
        # deicision of next pramater
        next = (left + right) // 2

        # run gatling with next
        # nwmw ..
        # process = subprocess.Popen(cmd, stdout=subprocess.PIPE,shell=True).communicate()[0]


        # get cpu utilization from result
        # data = query(...)
        result_cpu = data[next]

        if result_cpu < value:
            left = next + 1
            # left = next + resolution 
        else:
            right = next - 1
            # right = next - resolution 
    return right 


# influx query --raw 'from(bucket:"tochigi") |> range(start:-12h)'

r = binary_search(left, right, cpus, tgt)
print(ns[r], cpus[r])
