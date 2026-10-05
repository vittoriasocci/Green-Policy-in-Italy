import random 
import math
from collections import deque
import numpy as np


#Percentage of the populations in each region
PIE = 7.21  #PIEMONTE = 7.21% of the total population
AOS = 0.21
LIG = 2.56
LOMB = 16.98
TREN = 1.84
VEN = 8.23
FRIU = 2.03
EMI = 7.55
TOSC = 6.21
UMB = 1.45
MAR = 2.51
LAZ = 9.69
ABR = 2.15
MOL = 0.49
CAMP = 9.49
PUGL = 6.60
BAS = 0.90
CAL = 3.12
SIC = 8.14
SAR = 2.66

# create an array of 20 numbers, one for each Italian region.
#Each number represents the number of seats allocated to a specific region, expressed per 1,000
#ES: seats_permille[0] = number of seats allocated to the PIE region out of a total of 1,000.
seats_permille = [57,39,35,89,78,57,54,56,46,23,35,57,35,23,57,56,23,35,78,67]

perc_com = [PIE,AOS,LIG,LOMB,TREN,VEN,FRIU,EMI,TOSC,UMB,MAR,LAZ,ABR,MOL,CAMP,PUGL,BAS,CAL,SIC,SAR]

name_com = ["PIE","AOS","LIG","LOMB","TREN","VEN","FRIU","EMI","TOSC","UMB","MAR","LAZ","ABR","MOL","CAMP","PUGL","BAS","CAL","SIC","SAR"]

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

#create a dictionary where the keys are the abbreviated names of the 20 regions
#and the values are lists of length 5 representing the percentage distribution
#of the population across income brackets in that region.
inc_com = {"PIE":[3.26,2.85,23.92,37.80,32.17],
           "AOS":[3.38,2.93,25.50,36.39,31.80],
           "LIG":[3.43,3.00,23.33,33.74,36.51],
           "LOMB":[4.42,3.63,24.84,36.31,30.80],
           "TREN":[3.84,3.19,26.45,34.10,32.42],
           "VEN":[3.24,2.77,22.64,38.86,32.49],
           "FRIU":[2.99,2.68,24.45,38.07,31.81],
           "EMI":[3.54,3.15,24.52,38.04,30.76],
           "TOSC":[3.17,2.76,21.79,37.80,34.47],
           "UMB":[2.49,2.11,19.63,36.91,38.85],
           "MAR":[2.56,2.22,19.29,39.55,36.39],
           "LAZ":[4.25,3.48,23.35,29.81,39.10],
           "ABR":[2.05,1.86,18.63,34.66,42.80],
           "MOL":[1.65,1.43,17.01,31.32,48.59],
           "CAMP":[2.07,1.75,17.72,29.77,48.69],
           "PUGL":[1.75,1.52,16.39,31.13,49.21],
           "BAS":[1.52,1.44,16.80,32.75,47.48],
           "CAL":[1.48,1.29,14.89,28.23,54.10],
           "SIC":[1.92,1.72,16.50,29.38,50.47],
           "SAR":[1.96,1.86,17.76,34.12,44.30]}


name_inc = ["H","HM","M","ML","L"] 

income_index = {"H":0,"HM":1,"M":2,"ML":3,"L":4}

# Macro-areas
NORD = {"PIE","AOS","LIG","LOMB","TREN","VEN","FRIU","EMI"}
CENTRO = {"TOSC","UMB","MAR","LAZ","ABR","MOL"}
SUD = {"CAMP","PUGL","BAS","CAL","SIC","SAR"}  # Sud + Isole

MACRO_OF_REGION = {}
for r in NORD:
    MACRO_OF_REGION[r] = "NORD"
for r in CENTRO:
    MACRO_OF_REGION[r] = "CENTRO"
for r in SUD:
    MACRO_OF_REGION[r] = "SUD"


#Class for citizens
class Citizen:
    
    def __init__(self,ID,income,gender,geo,position,size_com,income_class,alpha,beta,age=0):
    

        self.income = income   #income class: H, HM, M, ML or L

        self.gender = gender #gender: 0 (M) or 1 (F)

        self.geo = geo  #region

        self.position = position   

        self.age = age 

        self.neighbors = list([]) 

        self.alpha = alpha   #initial green propensity 

        self.beta = beta #self-efficacy
        
        self.size_com = size_com #region dimension of citizen

        self.income_class = income_class #income class dimension of citizen

        self.ID = ID  #citizen ID
        
    def add_neighbor(self,id2):
        l = self.neighbors 
        l.append(id2)
        self.neighbors = l 

#Class for political seats       
class Seat:
    def __init__(self, ID, geo, vote):
        self.ID = ID  #Seat ID: 0,1,2,..,199
        self.geo = geo  #Seat region
        self.vote = vote  #seat political orientation
                          #if vote = True --> GREEN seat; otherwise BROWN seat

def random_geo():   
    geo = random.random()
    if geo < 0.5:  
        return 1
    if geo < 0.8:  
        return 2
    return 3      

def exact_geo_seats(ID,N):     
          
    TOT = 0
    
    for i in range(len(seats_permille)): 
        
        TOT += seats_permille[i]
        
        if i==len(seats_permille)-1: 
            TOT=1000
        
        if 1000.0*ID/N <= TOT:
            
            return name_com[i]

def exact_geo(ID,N):    

    TOT = 0
    
    for i in range(len(perc_com)): 
        
        TOT += perc_com[i]  
        
        if i==len(perc_com)-1: 
            TOT=100
        
        if 100.0*ID/N <= TOT: 

            f_id = (TOT-perc_com[i])*N/100 
            l_id = TOT*N/100 
            position = (ID-f_id)/(float(l_id)-f_id) 
            LIST = [name_com[i]] 
            LIST.append(position)
            LIST.append(perc_com[i]*N/100) 
            return LIST
        

    
def random_income():  
    inc = random.random() 
    if inc < 0.5: 
        return 1
    if inc < 0.8: 
        return 2
    return 3 

def exact_income(geo, position, size_com, size_income):  
                        
    
    TOT = 0
#    print(size_com,inc_com[geo])
    
    for i in range(5): 
        
        TOT += inc_com[geo][i] 
#        print(position,TOT)
        
        if i==4:   
            TOT=100
            position = min(position, 1.0)  
        
        if position*100.0 <= TOT:   
            
            LIST = [name_inc[i]] 

            LIST.append(inc_com[geo][i]*size_com/100.0) 

            size_income[i] += 1  
            
            return LIST
        
    
    print("ERRORE geo:", geo, 
          "position:", position, 
          "size_com:", size_com, 
          "TOT finale:", TOT,
          "i (classe di reddito):", i )

def random_alpha():   
    return random.random()  

def exact_alpha(): 
    return 0.5

def compute_proximity(c1, c2,N,distances_geo,distance_inc,max_d1,max_d2,teta,delta,g,k):
    geo1 = c1.geo 
    geo2 = c2.geo 
    inc1 = c1.income 
    inc2 = c2.income 
    gen1 = c1.gender 
    gen2 = c2.gender 
    
    d1 = distances_geo.get((geo1, geo2), distances_geo.get((geo2, geo1), 0))

    d2 = distance_inc.get((inc1, inc2), distance_inc.get((inc2, inc1), 0)) 
    
    if gen1 == gen2:
        gender_factor = 2 / (1 + math.exp(-g))  
    else:
        gender_factor = 2 / (1 + math.exp(g))  

    d1_norm = d1 / max_d1
    d2_norm = d2 / max_d2

    if (geo1 == geo2) and (inc1 == inc2):
        p = (k / c1.income_class)*gender_factor
    else: 
        p = (math.exp(-teta * d1_norm) * math.exp(-delta * d2_norm))*gender_factor

    return p 
        
def count_green_seats(SEATS):
    
    tot = 0
    
    for seat in SEATS: 
        
        if seat.vote: 
            
            tot += 1
    
    return tot
        
              
def alpha_medio(CITIZEN):
    
    tot = 0.0
    
    for cit in CITIZEN: 
            
        tot += cit.alpha 
     
    return tot/len(CITIZEN) 
        

def load_edges(path):
    edges = []
    with open(path, "r") as f: 
        for line in f: 
            line = line.strip()
            if not line:
                continue
            a, b = line.split(",") 
            u = int(a); v = int(b) 
            if u == v: 
                continue
            if u > v: 
                u, v = v, u
            edges.append((u, v)) 
    return edges


#def rewire_edges(edges, N, p, rng, tries_per_edge=10):
def rewire_edges(edges, N, p, tries_per_edge=10):
    adj = [set() for _ in range(N)]
    for (u, v) in edges:
        adj[u].add(v)
        adj[v].add(u)

    nodes = list(range(N))
    new_edges = []
    edge_set = set()

    for (u, v) in edges:
        fixed = u
        old_neighbor = v

        a, b = (u, v) if u < v else (v, u)
        chosen = (a, b)

        #if rng.random() < p:
        if random.random() < p:
            for _ in range(tries_per_edge):
                #w = rng.choice(nodes)
                w = random.choice(nodes)
                if w == fixed or (w in adj[fixed]):
                    continue

                # rewiring
                adj[fixed].discard(old_neighbor)
                adj[old_neighbor].discard(fixed)

                adj[fixed].add(w)
                adj[w].add(fixed)

                a, b = (fixed, w) if fixed < w else (w, fixed)
                chosen = (a, b)
                break

        if chosen in edge_set:
            chosen = (u, v) if u < v else (v, u)

        edge_set.add(chosen)
        new_edges.append(chosen)

    return new_edges


def build_neighbors(citizens, edges):
    for c in citizens:
        c.neighbors = []
    for (u, v) in edges:
        citizens[u].add_neighbor(v)
        citizens[v].add_neighbor(u)


def giant_component(citizens):
    N = len(citizens)
    visited = [False] * N
    best = []

    for start in range(N):
        if visited[start]:
            continue
        visited[start] = True
        if len(citizens[start].neighbors) == 0:
            continue

        q = deque([start])
        comp = []

        while q:
            node = q.popleft()
            comp.append(node)
            for nb in citizens[node].neighbors:
                if not visited[nb]:
                    visited[nb] = True
                    q.append(nb)

        if len(comp) > len(best):
            best = comp

    return set(best)

def mean_std_se(values):
    n = len(values)
    if n == 0:
        return 0.0, 0.0, 0.0, 0
    mean = float(np.mean(values))
    std  = float(np.std(values, ddof=1)) if n > 1 else 0.0
    se   = std / np.sqrt(n) if n > 0 else 0.0
    return mean, std, se, n

def make_regional_policy(target_regions, high=0.9, low=0.3):
    pol = [0.0] * 20
    for reg, idx in community_index.items():
        pol[idx] = high if reg in target_regions else low
    return pol

def make_regional_income_policy(target_macro, vec_target, vec_other):
    pol = [[0.0]*5 for _ in range(20)]
    for reg, ridx in community_index.items():
        m = MACRO_OF_REGION[reg]              # "NORD"/"CENTRO"/"SUD"
        src = vec_target if m == target_macro else vec_other
        pol[ridx] = list(src)                 # 5 valori income
    return pol
