import pandas as pd
import matplotlib.pyplot as plt

#Read the dataset
##Make sure the dataset is in the same directory as the code
df = pd.read_csv('https://raw.githubusercontent.com/rarrazaan/TuProAI2/main/restoran.csv')
pelayanan = df['pelayanan']
makanan = df['makanan']

#Membership Function Formula
def trapezoidal(x, a, b, c , d):
    if a < x < b:
        return (x - a) / (b - a)
    if b <= x <= c:
        return 1
    if c < x <= d:
        return (d - x) / (d - c)
    return 0
    
def triangular(x, a, b, c):
    return trapezoidal(x, a, b, b, c)
    
def linear_up(x, a, b):
    return triangular(x, a, b, b)

def linear_down(x, a, b):
    return triangular(x, a, a, b)

#Fuzzification Pelayanan and Makanan
n = len(pelayanan)
arrSBuruk = [0]*n
arrBuruk = [0]*n
arrBaik = [0]*n
arrSBaik = [0]*n
for i in range(n):
    sBuruk = linear_down(pelayanan[i], 0, 33)
    buruk = triangular(pelayanan[i], 0, 33, 66)
    baik = triangular(pelayanan[i], 33, 66, 100)
    sBaik = linear_up(pelayanan[i], 66, 100)
    
    arrSBuruk[i] = sBuruk
    arrBuruk[i] = buruk
    arrBaik[i] = baik
    arrSBaik[i] = sBaik

m = len(makanan)
arrTEnak = [0]*m
arrNormal = [0]*m
arrEnak = [0]*m
for i in range(m):
    tEnak = linear_down(makanan[i], 0, 5)
    normal = triangular(makanan[i], 0, 5, 10)
    enak = linear_up(makanan[i], 5, 10)
    
    arrTEnak[i] = tEnak
    arrNormal[i] = normal
    arrEnak[i] = enak

#Inferences and Defuzzification
##Inference Function get the minimum value
def inference(l, serv, food):
    if serv != 0:
        if food != 0:
            result = min(serv, food)
            l.append(result)

###Inferences
disappointing = []
meh = []
soso = []
okay = []
lit = []

hasil = [0]*100

for i in range(len(df)):
    inference(disappointing, arrSBuruk[i], arrTEnak[i])
    inference(disappointing, arrSBuruk[i], arrNormal[i])
    inference(disappointing, arrBuruk[i], arrTEnak[i])
    
    inference(meh, arrSBuruk[i], arrEnak[i])
    inference(meh, arrBuruk[i], arrNormal[i])
    inference(meh, arrBaik[i], arrTEnak[i])
    
    inference(soso, arrSBaik[i], arrTEnak[i])
    inference(soso, arrBuruk[i], arrEnak[i])
    
    inference(okay, arrBaik[i], arrNormal[i])
    inference(okay, arrSBaik[i], arrNormal[i])
    inference(okay, arrBaik[i], arrEnak[i])
    
    inference(lit, arrSBaik[i], arrEnak[i])
    
    garisDis = max(disappointing) if len(disappointing) > 0 else 0
    garisMeh = max(meh) if len(meh) > 0 else 0
    garisSos = max(soso) if len(soso) > 0 else 0
    garisOka = max(okay) if len(okay) > 0 else 0
    garisLit = max(lit) if len(lit) > 0 else 0
    
    
    ###Defuzzification    
    pembilang = penyebut = 0
    j = 0
    while j < 100:
        tinggiDis = min(garisDis, linear_down(j, 0, 25))
        tinggiMeh = min(garisMeh, triangular(j, 0, 25, 50))
        tinggiSos = min(garisSos, triangular(j, 25, 50, 75))
        tinggiOka = min(garisOka, triangular(j, 50, 75, 100))
        tinggiLit = min(garisLit, linear_up(j, 75, 100))
        tinggiFusion = max(tinggiDis, tinggiMeh, tinggiSos, tinggiOka, tinggiLit)
        pembilang += j * tinggiFusion
        penyebut += tinggiFusion
        j += 0.01
    
    try:
        hasil[i] = pembilang / penyebut
    except ZeroDivisionError:
        hasil[i] = 0
      
    disappointing.clear()
    meh.clear()
    soso.clear()
    okay.clear()
    lit.clear()


#The Result
result = pd.DataFrame(hasil)
result.columns = ['hasil']
id = [i for i in range(1, len(result)+1)]
result['id'] = id

rank = pd.merge(df, result, how = 'inner', on = 'id')
rank.sort_values(['hasil'], ascending = False, inplace=True)

print(rank[:10])
# #Export Top10
# rank[:10].to_excel('D:\peringkat.xlsx')     #Export to drive D

# #Export Top100
# rank.to_excel('D:\peringkat_semua.xlsx')    #Export to drive D

#Scatter Plot checking the answer correctness
plt.figure(1)
plt.title('Grafik Peringkat')
plt.xlabel('Pelayanan')
plt.ylabel('Makanan')
for i in range(100): 
    data = rank.iloc[i]
    plt.scatter(data['pelayanan'], data['makanan'], color='r' if i < 10 else 'b' , label='TopTen' if i == 0 else ('Other' if i == 10 else None))
plt.legend()
plt.show()
