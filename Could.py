import time
import os
import sys
import requests
import numpy as np
from sklearn.linear_model import OrthogonalMatchingPursuit
import pymongo
import dns

broker_address = "192.168.43.246"

Y = 52
M = 129
N = 256
L = Y/N*100
Q = [[0], [0]]
pId = []
Bstart = False
sensor = 1
real = []
imag = []
realZ = []
imagZ = []
array = []
i = 0
urlSensor = ''
id_rompi: ""
id_sensor: ""
id_pasien: ""
data: ""
PPG = []
EKG = []
EMG = []
SUHU = []
AcceX = []
AcceY = []
AcceZ = []
start = time.time()

for x in range(Y-2):
    Q.append([0])
for x in range(Y):
    for y in range(M-1):
        Q[x].append(0)

Log = 0
Gaussian = np.loadtxt(fname="Gaussian52x129.txt")

for x in range(Y):
    for y in range(M):
        Q[x][y] = Gaussian[Log]
        Log += 1


def kirim_():
    response = requests.post(
        "https://bysonics-alpha001.herokuapp.com/recording/start")
    print(f"Request returned {response.status_code} : '{response.reason}'")
    payload = response.content
    import pprint
    pp = pprint.PrettyPrinter(indent=1)
    pp.pprint(payload)
    startAcc = time.time()
    data = {
        "id_rompi": "001",
        "id_sensor": "All01",
        "id_pasien": "000001",
        "dataAccelerometer_X": AcceX,
        "dataAccelerometer_Y": AcceY,
        "dataAccelerometer_Z": AcceZ,
        "dataSuhu": SUHU,
        "dataEKG": EKG,
        "dataPPG": PPG,
        "dataEMG": EMG
    }
    url_POST = (
        'https://bysonics-alpha001.herokuapp.com/dataAllSensor/save')
    response = requests.post(url_POST, None, data)
    print(
        f"Request returned {response.status_code} : '{response.reason}'")
    payload = response.content
    import pprint
    pp = pprint.PrettyPrinter(indent=1)
    pp.pprint(payload)
    x = collection.delete_many({})
    x.deleted_count
    end = time.time()
    runTime = end - startAcc
    print(f"Runtime of the program is {runTime} Second")


def CS_(real2, imag2):
    print(sensor)

    omp1 = OrthogonalMatchingPursuit(n_nonzero_coefs=M)
    omp1.fit(Q, real2)
    coefreal = omp1.coef_

    omp2 = OrthogonalMatchingPursuit(n_nonzero_coefs=M)
    omp2.fit(Q, imag2)
    coefimag = omp2.coef_

    realZ = []
    realQ = coefreal[0]
    realW = coefreal[M-1]
    realX = coefreal[1:M-1]
    realY = realX[::-1]
    realZ = np.append(realZ, realQ)
    realZ = np.append(realZ, realX)
    realZ = np.append(realZ, realW)
    realZ = np.append(realZ, realY)

    imagZ = []
    imagQ = coefimag[0]
    imagW = coefimag[M-1]
    imagX = coefimag[1:M-1]
    imagY = imagX[::-1]*-1
    imagZ = np.append(imagZ, imagQ)
    imagZ = np.append(imagZ, imagX)
    imagZ = np.append(imagZ, imagW)
    imagZ = np.append(imagZ, imagY)

    array = []
    for x in range(N):
        com = complex(realZ[x], imagZ[x])
        array = np.append(array, com)

    ftx = []
    ftx = np.fft.ifft(array)

    arr = []
    arr = np.array(ftx.real)
    arr2 = []
    arr2 = arr.tolist()
    myList = [int(x) for x in arr2]
    return myList


try:
    client = pymongo.MongoClient(
        "mongodb+srv://admin:admin@cluster0.eomgz.mongodb.net/Data_alpha001?retryWrites=true&w=majority")
    db = client.Data
    collection = db.Compressed
    x = collection.delete_many({})
    x.deleted_count
    print("connect to MongoDB")
except:
    print("Could not connect to MongoDB")
    exit()

if __name__ == '__main__':
    print("Program Ready")
    i = 0
    while True:
        try:
            data = collection.find().sort('_id', pymongo.DESCENDING).limit(1)
            Id = data[0]['_id']
            if pId != Id:
                start = time.time()
                print(f'Terdapat Data Baru, Id ={Id}')
                Hreal = []
                Himag = []
                try:
                    for X in data:
                        HrealPPG = (X['PPG']['real'])
                        HimagPPG = (X['PPG']['imag'])
                        HrealEKG = (X['EKG']['real'])
                        HimagEKG = (X['EKG']['imag'])
                        HrealACCX = (X['ACCX']['real'])
                        HimagACCX = (X['ACCX']['imag'])
                        HrealACCY = (X['ACCY']['real'])
                        HimagACCY = (X['ACCY']['imag'])
                        HrealACCZ = (X['ACCZ']['real'])
                        HimagACCZ = (X['ACCZ']['imag'])
                        HrealEMG = (X['EMG']['real'])
                        HimagEMG = (X['EMG']['imag'])
                        HrealSUHU = (X['SUHU']['real'])
                        HimagSUHU = (X['SUHU']['imag'])
                except:
                    print("Belum Ada Data PPG")
                PPG = CS_(HrealPPG, HimagPPG)
                EKG = CS_(HrealEKG, HimagEKG)
                AcceX = CS_(HrealACCX, HimagACCX)
                AcceY = CS_(HrealACCY, HimagACCY)
                AcceZ = CS_(HrealACCZ, HimagACCZ)
                EMG = CS_(HrealEMG, HimagEMG)
                SUHU = CS_(HrealSUHU, HimagSUHU)
                pId = Id
                print("Kirim")
                kirim_()
                end = time.time()
                runTime = end - start
                print(f"Runtime of the program is {runTime} Second")
            else:
                os.system('cls')
                print(f'Waiting for new data, Id = {Id}')
        except:
            # Id = []
            pId = []
