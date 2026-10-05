import random 
import sys
import pandas as pd
import numpy as np
import csv
import matplotlib.pyplot as plt

random.seed(1000) # 10

sys.path.insert(1, '/path/to/application/app/folder')

from functions import * 

N_c = 100000 
N_s = 895 
STEPS = 5 

CITIZEN = []  
SEATS = []    

size_income = [0]*5   

size_gender = [0,0] 

income_index = {"H":0,"HM":1,"M":2,"ML":3,"L":4}  

community_index = {"PIE":0,
                   "AOS":1,
                   "LIG":2,
                   "LOMB":3,
                   "TREN":4,
                   "VEN":5,
                   "FRIU":6,
                   "EMI":7,
                   "TOSC":8,
                   "UMB":9,
                   "MAR":10,
                   "LAZ":11,
                   "ABR":12,
                   "MOL":13,
                   "CAMP":14,
                   "PUGL":15,
                   "BAS":16,
                   "CAL":17,
                   "SIC":18,
                   "SAR":19}   

min_beta = {"H":0.9,"HM":0.8, "M":0.7,"ML":0.6,"L":0.5}

df_dist = pd.read_csv(           
    'distanze_regioni_centroidi_km.csv',index_col=0)
#print(df_dist)

rename_map = {
    "Piemonte": "PIE",
    "Valle d'Aosta": "AOS",
    "Liguria": "LIG",
    "Lombardia": "LOMB",
    "Trentino-Alto Adige": "TREN",
    "Veneto": "VEN",
    "Friuli-Venezia Giulia": "FRIU",
    "Emilia-Romagna": "EMI",
    "Toscana": "TOSC",
    "Umbria": "UMB",
    "Marche": "MAR",
    "Lazio": "LAZ",
    "Abruzzo": "ABR",
    "Molise": "MOL",
    "Campania": "CAMP",
    "Puglia": "PUGL",
    "Basilicata": "BAS",
    "Calabria": "CAL",
    "Sicilia": "SIC",
    "Sardegna": "SAR",
}

df_dist = df_dist.rename(index=rename_map, columns=rename_map)

upper_mask = np.triu(np.ones(df_dist.shape, dtype=bool), k=0) # prendo solo triangolo superiore (inclusa la diagonale)
#print(upper_mask)

distances_geo = df_dist.where(upper_mask).stack().to_dict()
#print(distances_geo)

distance_inc = {('L','L') : 0, ('L','ML') : 15296.319777, ('L','M') : 30813.928794, ('L','HM') : 57076.452567, ('L','H'): 111250.662738,
                ('ML','ML') : 0, ('ML','M') : 15517.609016, ('ML','HM') : 41780.132790, ('ML','H') : 95954.342961,
                ('M','M') : 0, ('M','HM') : 26262.523774, ('M','H') : 80436.733945,
                ('HM','HM') : 0, ('HM','H') : 54174.210171,
                ('H','H') : 0}

max_d1 = max(distances_geo.values()) 
max_d2 = max(distance_inc.values()) 


#### CREATE CITIZENS
   
for i in range(N_c):              

    ID = i                        

    geo_list = exact_geo(i,N_c)   

#    print(geo_list)

    geo = geo_list[0]
    position = geo_list[1]
    size_com = geo_list[2] 
    income_list = exact_income(geo,position,size_com,size_income) 

#    print(geo,income_list)

    income = income_list[0]
    income_class = income_list[1]   

    alpha = random_alpha()          

    beta = 1 #random.random()        
    #beta = (1-min_beta[income]) * random.random() + min_beta[income]

    if random.random() < 0.49:       
        gender = 0 #sesso maschile   
    else:                            
        gender = 1 #sesso femminile  
    

    if gender == 0:          
        size_gender[0] += 1  
    else:                    
        size_gender[1] += 1
                               
    CITIZEN.append(Citizen(i,income,gender,geo,position,size_com,income_class,alpha,beta))

beta_H = 0
beta_HM = 0
beta_M = 0
beta_ML = 0
beta_L = 0
div = 0
for p in CITIZEN:
    if p.income == "H":
        beta_H += p.beta
        div += 1
print(beta_H / div)
div=0
for p in CITIZEN:
    if p.income == "HM":
        beta_HM += p.beta
        div += 1
print(beta_HM / div)
div=0
for p in CITIZEN:
    if p.income == "M":
        beta_M += p.beta
        div += 1
print(beta_M / div)
div=0
for p in CITIZEN:
    if p.income == "ML":
        beta_ML += p.beta
        div += 1
print(beta_ML / div)
div=0
for p in CITIZEN:
    if p.income == "L":
        beta_L += p.beta
        div += 1
print(beta_L / div)
    

f = open("income_class.txt", "w")     
for p in CITIZEN:
    f.write(str(p.geo)+"\t"+str(p.income)+"\t"+str(p.income_class)+"\n")                               
f.close()  


with open("node_attributes.csv", "w", newline="") as f_attr:
    writer = csv.writer(f_attr)
    writer.writerow(["nodo", "regione", "classe_reddito", "genere"])

    for cit in CITIZEN:
        gender_label = "M" if cit.gender == 0 else "F"
        writer.writerow([cit.ID, cit.geo, cit.income, gender_label])

    
#### CREATE SEATS

for i in range(N_s):              

    ID = i                        

    geo = exact_geo_seats(i,N_s) 

    vote = True # GREEN           
                      
    SEATS.append(Seat(i,geo,vote)) 



f = open("last_created_network_21.txt", "w") 
        
#### CREATE NETWORK (CITIZEN LAYER) STOCHASTIC BLOCK MODEL
        
for i in range(N_c-1): 
                
    if i%(N_c/20)==0:
        print(str(i/(N_c/20)*5)+"%"),
        
        
    for j in range(i+1,N_c):    

        citizen1 = CITIZEN[i]  
        citizen2 = CITIZEN[j] 

        prox = compute_proximity(citizen1,citizen2,N_c,distances_geo,
                                     distance_inc,max_d1,max_d2,teta=56,delta=40,g=0,k=1) 
        ## g corresponds to lambda in the paper; use g in {-8, -4, -2, 0, 2, 4, 8}
        ## to model gender heterophily (g < 0), neutral mixing (g = 0), or homophily (g > 0)
        

            
        if random.random()<prox: 
            citizen1.add_neighbor(j) 

            citizen2.add_neighbor(i) 
                          
            f.write(str(citizen1.ID) + "," + str(citizen2.ID)+"\n")
    
print("100%")   
f.close()   
