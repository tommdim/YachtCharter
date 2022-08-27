from curses.ascii import isalpha
from turtle import circle
import numpy as np
import random
from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
import psycopg2
            

app = Flask(__name__)

logged = False
user = ''
ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:DataBase01@localhost/tommasodimario'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
try:
    con = psycopg2.connect(
        host = 'localhost',
        database = 'tommasodimario',
        user = 'postgres',
        password = 'DataBase01',
    )

    con.autocommit(True)
except:
    print("ISSUES")


"""Prima cosa generiamo le barche"""
def genera_barche(dic1, dic2):
    #Attributi (boat_hull_number, boat_name, boat_maker, boat_construction_year, located_seaport_id, model_name, boat_cost)
    boat_hull_number = int(np.random.random() * 100000000)
    cur = con.cursor()
    cur.execute('SELECT boat_hull_number from public."Boat"')
    hull_nums = cur.fetchall()
    while boat_hull_number in hull_nums:
        boat_hull_number = int(np.random.random() * 100000000)
    
    boat_name = dic1[int(np.random.random() * len(dic1))]
    boat_maker = dic2[int(np.random.random() * len(dic2))]
    boat_construction_year = str(int(random.randrange(1970, 2022))) + "-" + str(int(random.randrange(1, 12))) + "-" + str(int(random.randrange(1, 30)))
    cur.execute('SELECT seaport_id FROM public."Seaport";')
    porti = cur.fetchall()
    located_seaport_id = porti[int(np.random.random() * len(porti))]
    print(located_seaport_id)
    piedi = int(random.randrange(40,350))
    cur.execute('SELECT model_name FROM public."Model_boat"')
    modelli = cur.fetchall()
    model_name = modelli[int(np.random.random() * len(modelli))]
    print(model_name)
    cur.execute('SELECT length FROM public."Model_boat" where (model_name = %s);', (model_name))
    length = cur.fetchall()
    
    boat_cost = length[0][0] * int(random.randrange(75000, 175000))
    
    print(boat_hull_number)
    cur = con.cursor()
    cur.execute('INSERT INTO public."Boat" (boat_hull_number, boat_name, boat_maker, boat_construction_year, located_seaport_ID, model_name, boat_cost) values (%s,%s,%s,%s,%s,%s,%s)', (boat_hull_number, boat_name, boat_maker ,boat_construction_year,located_seaport_id ,model_name , boat_cost))
    with open("queries.txt", mode="a") as f:
        f.write(f'INSERT INTO public."Boat" (boat_hull_number, boat_name, boat_maker, boat_construction_year, located_seaport_ID, model_name, boat_cost) values ({boat_hull_number}, {boat_name}, {boat_maker} ,{boat_construction_year},{located_seaport_id} ,{model_name} , {boat_cost})' )
    con.commit()
    cur.close()
    
def generaModelli(dic3, dic2):
    """model_name, model_brand, model_sleeping_places, num_sails, num_engines, model_type, length, draft, width, weight"""
    length = int(random.randrange(40,350))
    model_name = dic3[int(np.random.random() * len(dic3))] + " " + str(length)
    model_brand = dic2[int(np.random.random() * len(dic2))]
    model_sleeping_places = int(random.randrange(5,25))
    num_sails = 0 if random.randrange(0,2) > 0.5 else random.randint(3,6)
    num_engines = 1 if num_sails >= 3 else random.randint(2,6)
    model_type = "Yacht" if num_sails == 0 else "Sailboat"
    draft = int(random.randrange(10,50))
    width = int(random.randrange(length//5, length//2))
    weight = int(random.randrange(1000,5000))
    cur = con.cursor()
    cur.execute("""INSERT INTO "Model of the boat"( model_name, model_brand, model_sleeping_places, num_sails, num_engines, model_type, length, draft, width, weight) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(model_name, model_brand, model_sleeping_places, num_sails, num_engines, model_type, length, draft, width, weight))
    with open("queries.txt", mode="a") as f:
        f.write("\n")
        f.write(f"""INSERT INTO "Model of the boat" (model_name, model_brand, model_sleeping_places, num_sails, num_engines, model_type, length, draft, width, weight) VALUES ({model_name}, {model_brand}, {model_sleeping_places}, {num_sails}, {num_engines}, {model_type}, {length}, {draft}, {width}, {weight})""")
    con.commit()
    cur.close()
    
def generaMotori(marche):
    cur = con.cursor()
    cur.execute(""" select boat_hull_number, num_engines, boat_construction_year from public."Model_boat", public."Boat" where (public."Boat".model_name = public."Model_boat".model_name) """)
    ret = cur.fetchall()
    cur.execute(""" select engine_serial_number from public."Engine" """)
    motori = [el for lista in cur.fetchall() for el in lista]
    
    
    for boat in ret:
        anno = random.randint(boat[2].year,2022)
        boat_hull_number = boat[0]
        engine_purchase_date = f"{anno}-{random.randint(1,12)}-{random.randint(1,28)}"
        engine_brand = marche[random.randint(0,len(marche)-1)]
        engine_displacement = [600,700,800,1000,1500,2000,2500,3000][random.randint(0,7)]
        engine_consumes = engine_displacement / 20
        engine_cost = engine_displacement * 30
        for i in range(boat[1]): 
            engine_serial_number = boat[0] / 3 + i
            if str(engine_serial_number) in motori:
                continue
            else:
                cur.execute(""" INSERT INTO public."Engine"(
                            engine_serial_number, engine_brand, engine_cost, engine_purchase_date, engine_consumes, engine_displacement, boat_hull_number)
                            VALUES (%s, %s, %s, %s, %s, %s, %s); """, (engine_serial_number,engine_brand, engine_cost, engine_purchase_date, engine_consumes, engine_displacement, boat_hull_number))
                with open("queries.txt", "a") as f:
                    f.write("\n")
                    f.write(f""" INSERT INTO public."Engine"(
                            engine_serial_number, engine_brand, engine_cost, engine_purchase_date, engine_consumes, engine_displacement, boat_hull_number)
                            VALUES ({engine_serial_number},{engine_brand}, {engine_cost}, {engine_purchase_date}, {engine_consumes}, {engine_displacement}, {boat_hull_number}); """)
                con.commit()
    cur.close()        
    
def generaPersone(strade, nomi, cognomi):
    lettere = "abcdefghijklmnopqrstuvxywz".upper()
    numeri = "0123456789"
    cur = con.cursor()
    cur.execute(""" select person_id_num from public."Person" """)
    ids = [el for lista in cur.fetchall() for el in lista]
    person_id_num = f"{lettere[random.randint(0,25)]}{lettere[random.randint(0,25)]}{numeri[random.randint(0,9)]}{numeri[random.randint(0,9)]}{numeri[random.randint(0,9)]}{lettere[random.randint(0,25)]}{lettere[random.randint(0,25)]}"
    while person_id_num in ids:
        person_id_num = f"{lettere[random.randint(0,25)]}{lettere[random.randint(0,25)]}{numeri[random.randint(0,9)]}{numeri[random.randint(0,9)]}{numeri[random.randint(0,9)]}{lettere[random.randint(0,25)]}{lettere[random.randint(0,25)]}"
    person_nat = random.randint(0,3)
    civico = random.randint(1,250)
    person_birth_date = f"{random.randint(1965,2002)}-{random.randint(1,12)}-{random.randint(1,28)}"
    if person_nat == 0:
        #italia
        person_city = "Roma"
        #genera via italiana + civico 
        person_address = strade[person_nat][random.randint(0,len(strade[person_nat]) - 1)] +  ", " + str(civico)
        person_name = nomi[person_nat][random.randint(0,len(nomi[person_nat]) - 1)]
        person_surname = cognomi[person_nat][random.randint(0,len(cognomi[person_nat]) - 1)]
        email = f"{person_surname.lower()}{person_name.lower()}@gmail.com"
    elif person_nat == 1:
        #germania
        person_city = "Berlin"
        person_address = strade[person_nat][random.randint(0,len(strade[person_nat]) - 1)] + ", " + str(civico)
        person_name = nomi[person_nat][random.randint(0,len(nomi[person_nat]) - 1)]
        person_surname = cognomi[person_nat][random.randint(0,len(cognomi[person_nat]) - 1)]
        email = f"{person_surname.lower()}{person_name.lower()}@gmail.com"
    
    elif person_nat == 2:
        #inghilterra
        person_city = "London"
        person_address = strade[person_nat][random.randint(0,len(strade[person_nat]) - 1)] + ", " + str(civico)
        person_name = nomi[person_nat][random.randint(0,len(nomi[person_nat]) - 1)]
        person_surname = cognomi[person_nat][random.randint(0,len(cognomi[person_nat]) - 1)]
        email = f"{person_surname.lower()}{person_name.lower()}@gmail.com"
    else:
        person_city = "Paris"
        person_address = strade[person_nat][random.randint(0,len(strade[person_nat]) - 1)] + ", " + str(civico)
        person_name = nomi[person_nat][random.randint(0,len(nomi[person_nat]) - 1)]
        person_surname = cognomi[person_nat][random.randint(0,len(cognomi[person_nat]) - 1)]
        email = f"{person_surname.lower()}{person_name.lower()}@gmail.com"
    
    cur.execute(
    """INSERT INTO public."Person"
    (person_id_num, person_name, person_surname, person_birth_date, person_address, person_email, person_city)
	VALUES (%s, %s, %s,%s,%s,%s,%s);""",(person_id_num, person_name, person_surname, person_birth_date, person_address, email, person_city)
    )
    con.commit()
    cur.close()

def generaEmployee():
    # cose da mettere su emp che non sono in persona:
    
    cur = con.cursor()
    cur.execute(""" select * from public."Person" """)
    persone = cur.fetchall()
    persona = persone[random.randint(0,len(persone)-1)]
    person_id_num = persona[0]
    city = persona[6]
    emp_mail = f"{persona[2]}{city}@yachtcharter.com".lower()
    cur.execute(""" select emp_mail from public."Employee" """)
    mails = [str(el) for lista in cur.fetchall() for el in lista]
    if str(emp_mail) in mails:
        return
    
    emp_start_date = f"{random.randint(2018,2021)}-{random.randint(1,12)}-{random.randint(1,28)}"
    emp_end_date = f"{random.randint(2018,2022)}-{random.randint(1,12)}-{random.randint(1,28)}"
    while int(emp_end_date[:4]) <= int(emp_start_date[:4]):
        emp_end_date = f"{random.randint(2018,2022)}-{random.randint(1,12)}-{random.randint(1,28)}"           
    emp_id = int(int("".join([str(ord(c)) for c in persona[1]+persona[2]])) % 1e9)
    #TODO controlla se il codice non va
    emp_role = ["OfficeWorker", "Broker", "Crew", "Repair"][random.randint(0,3)]
    
    
    
    login_username = f"{persona[2]}{city}".lower()
    user_password = f"{nomi_tedeschi[random.randint(0,len(nomi_tedeschi) -1)].title()}01"
    emp_phone = int(emp_id) * 23 % 1e10
    if city == "Roma":
        phone_country_code = "+39" 
        off_code = f"5010{random.randint(1,2)}"
    elif city == "Paris":
        phone_country_code = "+33" 
        off_code = f"7500{random.randint(1,2)}"
    elif city == "London":
        phone_country_code = "+44" 
        off_code = f"8500{random.randint(1,2)}"
    else:
        phone_country_code = "+49" 
        off_code = f"9500{random.randint(1,2)}"

    # cur.execute(""" select distinct "Employee".off_code from public."Employee" where "Employee".emp_role='Director' """)
    # lista = [str(el) for lista in cur.fetchall() for el in lista]
    # print(off_code)
    # print(lista)
    # if str(off_code) in lista:
    #     print("non sono down")
    #     return
    contract_number = int(emp_id) * 61 % 1e10
    
    cur.execute("""select emp_id from public."Employee" """)
    ids = [str(el) for lista in cur.fetchall() for el in lista]
    if str(emp_id) in ids:
        return
    
    cur.execute(
        """
        INSERT INTO public."Login credentials"(
	login_username, user_password)
	VALUES (%s, %s);
        """, (login_username,user_password)
    )
    cur.execute(
    """
    INSERT INTO public."Contract"(
	contract_number, contract_name, contract_surname, contract_type, contract_expiration_date, contract_starting_date, contract_salary)
	VALUES (%s, %s, %s, %s, %s, %s, %s);""",(contract_number, persona[1], persona[2], "Employee", emp_end_date, emp_start_date, ["20000","30000","40000","50000","60000","70000"][random.randint(0,5)])
    )
    cur.execute(
        """INSERT INTO public."Phone"(
	phone_country_code, phone_number, person_id_num)
	VALUES (%s, %s, %s);""", (phone_country_code, emp_phone, person_id_num)
    )
    cur.execute(
    """INSERT INTO public."Employee"(
	emp_id, emp_start_date, emp_end_date, emp_role, emp_mail, person_id_num, emp_phone, phone_country_code, login_username, contract_number, off_code)
	VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""",(emp_id, emp_start_date, emp_end_date, emp_role, emp_mail, person_id_num, int(emp_phone), phone_country_code, login_username, contract_number, int(off_code))
    )
    con.commit()
    cur.close()
    
if __name__ == "__main__":
    #genera_barche()
    
    femmine = """
AALINA
ABIGAIL
ACHIROPITA
ADA
ADALGISA
ADDOLORATA
ADELA
ADELAIDE
ADELE
ADELIA
ADELINA
ADIMA
ADRIANA
AFRA
AGATA
AGNESE
AGOSTINA
.
AGRIPPINA
AIDA
AIKO
AISHA
ALBA
ALBERTA
ALBINA
ALCESTE
ALDA
ALEANDRA
ALEIDA
ALENA
ALESSANDRA
ALESSIA
ALEXANDRA
ALEXIS
ALGISA
ALIANA
ALICE
ALICIA
ALIDA
ALISEA
ALISEE
ALISSA
ALLEGRA
ALMA
ALTEA
ALICYA
ALLYSON
ALMERINDA
ALYSSA
AMABILE
AMALIA
AMANDA
AMARILLI
AMBA
AMBRA
AMBROSIA
AMELIA
AMELIE
AMINA
AMIRA
ANAGAIA
ANASTASIA
ANCILLA
ANDREINA
ANGELA
ANGELICA
ANGIOLINA
ANIKA
ANITA
ANNA
ANNABELLA
ANNACHIARA
ANNALAURA
ANNALISA
ANNALUNA
ANNAMARIA
ANNARELLA
ANNARITA
ANNAROSA
ANNASOFIA
ANNAVERA
ANNIKA
ANNUNZIATA
ANTEA
ANTIDA
ANTINISKA
ANTONELLA
ANTONIA
ANTONICCA
ANTONIETTA
ANTONINA
ANUSCA
AQUILINA
ARCANGELA
ARIA
ARGENIDE
ARIANNA
ARIANNE
ARIEL
ARIELA
ARIELE
ARLENA
ARMIDA
ARTEMIA
ARTEMIDE
ARTEMISIA
ASCENZA
ASHASA
ASIA
ASMARA
ASSIA
ASSUNTA
ASSUNTA MARIA
ASTRID
AUGUSTA
AURA
AUREA
AURELIA
AURORA
AZUE
AZZURRA
.	.	.	.
B
BARBARA
BEATA
BEATRICE
BELINDA
BELLA
BENEDETTA
BERENICE
BERNADETTE
BERTA
BERTILLA
BETTA
BETTY
BIANCA
BIBIANA
BICE
BONARIA
BONELLA
BRENDA
BRIGIDA
BRIGITTA
BRUNA
BRUNELLA
BRUNETTA
BRUNILDE
C
CAIDE
CAMILLA
CANDIDA
CARLA
CARLOTTA
CARMELA
CARMEN
CAROLA
CAROLINA
CARTISIA
CASSANDRA
CASSIOPEA
CATERINA
CATIA
CECILIA
CELESTE
CELESTINA
CESIDIA
CESIRA
CHANTAL
CHELSEA
CHIARA
CHIARALUNA
CHRISTINE
CINZIA
CIRA
CLAIRE
CLARA
CLARETTA
CLARITA
CLARISSA
CLAUDIA
CLEA
CLEIDE
CLELIA
CLEMENTINA
CLENEIDE
CLEO
CLEOPATRA
CLEOFE
CLEZIANA
CLEONICE
CLIO
CLODOVEA
CLOE
CLOIDE
CLORINDA
CLOTILDE
COLOMBA
CONCETTA
CONNY
CONNIE
CONSOLATA
CONSUELO
CORINNE
CORNELIA
COSETTA
COSTANZA
CRETA
CRISTEL
CORA
CRISTIANA
CRISTINA
CRISTYN
.	.
D
DAFNE
DAISY
DALIA
DALILA
DAMARIS
DAMIANA
DANA
DANIA
DANIELA
DANILA
DANUSKA
DANUTA
DANZIA
DARIA
DARIELLA
DEA
DEBORA
DEBORAH
DELIA
DELFINA
DELINDA
DEMETRA
DEMETRIA
DEMI
DENISE
DESDEMONA
DESIREE
DESIDERIA
DHARMA
DIAMANTE
DIAMARA
DIANA
DILETTA
DINA
DIOMIRA
DIVA
DOLORES
DOMENICA
DOMEZIA
DOMINIC
DOMITILLA
DOMIZIANA
DONATELLA
DONNA
DORA
DORALICE
DORELLA
DORIS
DORIANA
DORINA
DOROTEA
DOROTY
DRUSIANA
DRUSILLA
E
EBE
EDDA
EDGARDA
EDI
EDITH
EDNA
EDVIGE
EFREM
EGIZIA
EGLE
ELA
ELAINE
ELBA
ELDA
ELENA
ELENIA
ELEONORA
ELEKTRA
ELETTRA
ELGA
ELIANA
ELIDE
ELISA
ELISABETTA
ELOISA
ELSA
ELTI
ELVA
ELVI
ELVIRA
EMANUELA
EMERENZIANA
EMI
EMILIA
EMMA
EMILY
ENILA
ENOLA
ENORE
ERMELINDA
ENRICHETTA
ERALDA
ERGENIDE
ERICA
ERIKA
ERMELINDA
ERMINIA
ERNESTA
ERSILIA
ERSILDE
ESMERALDA
ESTER
EUFEMIA
EUFRASIA
EUGENIA
EVA
EVELINA
EVELYNE
EVITA
.
F
FABIA
FABIANA
FABIOLA
FABRIZIA
FANNY
FATIMA
FAUSTA
FEBE
FEDERICA
FEDORA
FEDRA
FELICIA
FERNANDA
FEMKE
FIAMMA
FIAMMETTA
FILIPPA
FILOMENA
FIONA
FIORDALISA
FIORENZA
FLAMINIA
FLAVIA
FLAVIANA
FLORA
FLORIANA
FLORINDA
FIORELLA
FORTUNA
FORTUNATA
FOSCA
FRANCA
FRANCESCA
FRIDA
FULVIA
FUTURA
G
GABRIELLA
GAETANA
GAIA
GAVINA
GEA
GELSOMINA
GEMMA
GENESIA
GENEVIEVE
GENNY
GENOVEFFA
GENZIANA
GEORGIANA
GERALDINA
GERARDA
GERMANA
GERTRUD
GERTRUDE
GIACINTA
GIADA
GIAMILA
GIANNA
GIANNINA
GIGLIOLA
GILDA
GINA
GINEVRA
GIOIA
GIORDANA
GIORGIA
GIOVANNA
GIOVITA
GISELLA
GIUDITTA
GIULIA
GIULIANA
GIULIETTA
GIUSEPPINA
GIUSTINA
GIUSY
GLENDA
GLORIA
GRAZIA
GRAZIANA
GRAZIELLA
GRETA
GRISELDA
GUADALUPE
GUENDALINA
GUIA
.	.	.	.
H
HALENEY
HEATHER
HEIDE
HELEN
HELENA
HELGA
HELENE
HILARY
HOARA
.
.
.
I
IAELE
IARA
IDA
IFIGENIA
ILARIA
ILDA
ILEANA
ILENE
ILENIA
IMMACOLATA
INDIA
INES
INGRID
IOLANDA
IOLE
IONIA
IPPOLITA
IRA
IRENE
IRIDEA
IRINA
IRIS
IRMA
ISA
ISABEL
ISABELLA
ISADORA
ISAURA
ISELLA
ISIDE
ISIDORA
ISIRA
ISOTTA
ITALIA
IVA
IVANA
IVANIA
IVONNE
.	.	.	.
J
JAMILA
JANA
JANE
JANIRA
JASMINE
JELENA
JENISHA
JENNIFER
JENNY
JESSICA
JILLIAN
JOANNA
JOLE
JOLANDA
JOSEPHINE
JOVANA
JUDITH
JULIA
JUNIA
JUSTINE
.	.	.	.
K
KARIN
KATE
KATIA
KATIUSCIA
KATUSCA
KAYLA
KENAN
KENDRA
KETTY
KIRA
KISHA
KRISTEL
KRIZIA
.	.	.	.	.
L
LAIDE
LAILA
LALLA
LARA
LARISSA
LAURA
LAVINIA
LAYLA
LEA
LEDA
LEILA
LELA
LELLA
LEONDINA
LEONILDA
LENA
LETIZIA
LIA
LIANA
LIALA
LIBERA
LICIA
LIDA
LIDIA
LIGEIA
LILIA
LILIANA
LINA
LINDA
LISA
LIVIA
LIVIANA
LJUBA
LOLA
LORA
LOREDANA
LORELAYNE
LORELEY
LORELLA
LORENA
LORENZA
LORETTA
LORIANA
LORITA
LORITY
LORYAN
LUANA
LUCE
LUCETTA
LUCIA
LUCINA
LUCILLA
LUCIANA
LUCREZIA
LUDOVICA
LUIGIA
LUIGINA
LUISA
LUISELLA
LUNA
M
MADDALENA
MAELA
MAFALDA
MAGDA
MAIA
MAIKA
MAILA
MAIRA
MALVINA
MANILA
MANUELA
MARA
MARCELLA
MAREA
MARELLA
MARETA
MARGARET
MARGHERITA
MARIA
MARIA ADELE
MARIANGELA
MARIA ANTONIETTA
MARIACHIARA
MARIA ASSUNTA
MARIA CARLA
MARIA CLAUDIA
MARIA CONCETTA
MARIACRISTINA
MARIA ELENA
MARIA FLAVIA
MARIAFRANCESCA
MARIAGIORGIA
MARIAGIULIA
MARIAGIOVANNA
MARIAGRAZIA
MARIAITALIA
MARIALAURA
MARIALOURDES
MARIALUCE
MARIALUISA
MARIANEVE
MARIANITA
MARIANELLA
MARIA MADDALENA
MARIANNA
MARIA PAOLA
MARIAPIA
MARIA RITA
MARIAROSA
MARIA SARA
MARIASOLE
MARIATERESA
MARICA
MARIA VITTORIA
MARIELE
MARIELLA
MARIEVA
MARIKA
MARILENA
MARILINA
MARILISA
MARILU'
MARINA
MARINELLA
MARIOLINA
MARISA
MARISEL
MARISOL
MARISSA
MARISTELLA
MARY
MARY KATE
MARYLIN
MARTA
MARTINA
MARUSKA
MARZIA
MASCHA
MASSIMILIANA
MATILDA
MATILDE
MATTEA
MAUDIA
MAURA
MAURICA
MAYA
MECREN
MELANIA
MELISSA
MELITA
MELITTA
MEGAN
MERCEDES
MIA
MICHELA
MICAELA
MICHELLE
MICOL
MIKOL
MIETTA
MILA
MILENA
MILLY
MILVA
MILVIA
MIRIANA
MINA
MIRANDA
MIRKA
MIREA
MIRELLA
MIRIAM
MIRNA
MIRTA
MIRZIA
MOANA
MOIRA
MONIA
MONIC
MONICA
MOREA
MORENA
MURIELLE
MORGANA
.	.	.	.	.
N
NABILA
NADA
NADIA
NAIKE
NANCY
NAOMI
NARA
NATALIA
NATALINA
NATASCIA
NAUSICA
NAYADE
NEIDE
NELIDA
NELLA
NEREIDE
NERINA
NICHE
NICLA
NICOLE
NICOLETTA
NILDE
NILLA
NINA
NINFA
NIVA
NIVEA
NIVES
NOA
NOELA
NOEMI
NORA
NORIKO
NORMA
NORUENA
NUCCIA
NUMA
NUNZIA
NUVOLETTA
.	.	.
O
OAKEYSI
ODESSA
OFELIA
OLETTA
OLGA
OLIMPIA
OLIVIA
OMBRETTA
ONESTA
ONORATA
ONORINA
ORETTA
ORIANA
ORIELLA
ORIETTA
ORNELLA
ORSOLA
ORTENSIA
OTTAVIA
.	.	.	.	.
P
PAMELA
PALMA
PALMIRA
PAOLA
PATRIZIA
PENELOPE
PERLA
PERNILLA
PETRA
PHOEBE
PIA
PICCARDA
PIERA
PIERANGELA
PINA
PINUCCIA
PORZIA
PRISCA
PRISCILLA
PROVVIDENZA
PULCHERIA
.
.
.
Q
QUINTINA
QUINZIA
.
.
.
.
R
RACHELE
RAFFAELLA
RAIKA
RAISSA
RAMONA
REBECCA
REDENTA
REDIA
REGINA
RENATA
RENZA
RINA
RITA
ROBERTA
ROCCA
ROLITA
ROMANA
ROMINA
ROSA
ROSALBA
ROSALIA
ROSALINDA
ROSAMARIA
ROSANGELA
ROSANNA
ROSARIA
ROSELDA
ROSELINA
ROSELLA
ROSETTA
ROSINA
ROSITA
ROSMARA
ROSMUNDA
ROSSANA
ROSSELLA
ROSY
RUTH
.	.	.	.
S
SABINA
SABRINA
SALOME'
SAMANTA
SAMIA
SAMIRA
SAMOA
SANDRA
SANDY
SANTA
SARA
SARAH
SARITA
SASHA
SAVIANA
SEBASTIANA
SEFORA
SELENE
SELVAGGIA
SENIA
SERAFINA
SERENA
SERENELLA
SEVERINA
SHAIRA
SHALABA
SHANA
SHARON
SHEILA
SHIRLEY
SIBILLA
SILVANA
SILVIA
SIMONA
SIRIA
SMERALDA
SMILLA
SOAVE
SOFIA
SOILI
SOLEDAD
SONDRA
SONIA
SORIANA
SOPHIE
SOVIANA
SPERANZA
STEFANIA
STELLA
SUE ELLEN
SUSANNA
SVEVA
SWAMI
SUELO
T
TAIDE
TAMARA
TANIA
TARA
TATIANA
TECLA
TEODORA
TERENZIA
TERESA
TERSILLA
TESSA
THEA
TILDE
TINA
TISBE
TIZIANA
TOMMASINA
TONIA
TOSCA
TRISTANA
TULLIA
.
.
.
U
UBALDA
ULDERICA
ULRICA
UMA
UMBERTA
URSULA
V
VALENIA
VALENTINA
VALERIA
VANDA
VANESSA
VANIA
VANNA
VELIA
VENERA
VENERE
VENERITA
VERA
VERENA
VERIDIANA
VERONICA
VERUSKA
VESNA
VIENNA
VILIA
VILMA
VINCENZA
VIOLA
VIOLAINE
VIOLANTE
VIOLANTINA
VIOLETTA
VIRGINIA
VIRNA
VITA
VITALBA
VITALIA
VITTORIA
VIVIANA
.
.
.
W
WANDA
WENDY
WILMA
WINONA
.
.
X
XENA
XENIA
.
.
.
.
Y
YASMINE
YARA
YLENIA
YOYCE
YVONNE
.
Z
ZABRY
ZAIRA
ZARA
ZELDA
ZELIA
ZELIDA
ZELINDA
ZEUDI
ZITA
ZOE
ZOIA
ZULEJKA
"""

    cantieri = """Alalunga 
Alfamarine 
Apreamare 
Azimut Yachts 
B
Baia 
Bavaria 
Beneteau 
Benetti 
Bertram 
Boston whaler 
Bruno abbate 
C
Canados 
Cantiere del pardo 
Cantieri di pisa 
Cantieri di sarnico 
Cantieri Estensi 
Cayman Yachts 
Comar Yachts 
Conam 
Cranchi 
D

Dufour 
Fairline 
Ferretti Yachts 
Fiart 
Fipa Yachts 
Fratelli Aprea 
G
Gianetti Yacht 
H
Hanse 
I
Ilver 
Innovazioni Progetti 
Itama 
J
Jeanneau 
L
M
Mano' Marine 
Menorquin 
Mochi Craft 
N
Nautors Swan 
O
Overmarine 
P
Pershing 
Posillipo 
Pursuit 
R
Riva 
Riviera 
Rizzardi 
S
Salpa 
Sanlorenzo 
Sciallino 
Sessa Marine 
Sunseeker 
"""
    
    barche = """
    Titanic II
Seasick
Jawesome
Sick and Tide
Ship-faced
Dock-topus
Shelly
New Kid on the Dock
Eat Cray Love
Lady Kriller
American Buoy
In Too Deep
Riptide
Nausea
Serendipity
Imagination
Liberty
Wanderlust
Gale
Zephyr
Sapphire
Amazonite
Atlantis
Leviathan
Noah
Neptune
Wayfarer
Coral
Go with the Flow
Great White
Shark Bait
Unsinkable
The Kraken
Hammerhead
Long Weekend
Aquamarine
The Antarctic
Flying Dutchman
Megalodon
The Dark Zone
Cthulhu
Carpe Diem
Beauty
Marquise
Sunny Days
Siren
20,000 Leagues
Pura Vida
Blue Blood
Contessa
Amethyst
Cleopatra
The Lady of the Lake
Titan
SS Opportunity
Fantasea
Easea on the Eyes
Seas the Day
Mishell
Krill-minal
Sea-battical
Aquaholic
Shore Thing
Vitamin Sea
Old Buoy
Forget-Me-Knot
Ex-squid-sit
Fin and Tonic
Resplendent
Oceania
Flo
Alexandrite
Ashray
Beowulf
Icarus
Eurydice
Isolde
Odysseus
Scylla
Steadfast
Nessie
Reel Love
The Codfather
Yellowtail
Night Trawler
Fishing for Compliments
Lady Kriller
Fishy Business
Fish Tank
Misty
All Aboard
Pearl
Fishin Impossible
Dreamboat
Poseidon
Wave Runner
Big Blue
Avalon
Fortuna
Capricorn
Venus
Full Throttle
Castaway
Seaduction
Dreamweaver
Expedition
Sweet Caroline
The Great Gatsea
The Old Man
Ariel
Jenny
The Inferno
Frank Ocean
Nemo
Usain Boat
Boaty McBoatface
Gilligan
Float On
Baits Motel
The Orca
    """
    
    marche = """
    A
AEG
AGCO
Ailsa Craig Engines
American Locomotive Company
Andrée & Rosenqvist
Anglo Belgian Corporation
Anzani
Atlas-Imperial
B
Barclay Curle
Bergen Engines
BMW Marine
Bolinder-Munktell
Boulton and Watt
British Polar Engines
British Seagull
Brodosplit
John Brown & Company
Bryansk Machine-Building Plant
Burmeister & Wain
C
Cammell Laird
Caterpillar Inc.
Charles Ward Engineering Works
Chrysler
George Clark & NEM
Cooper Industries
Crossley
Cummins
Cummins-Wärtsilä
D
DESA company
Detroit Diesel
Deutz AG
William Doxford & Sons
E
ELTO
Evinrude Outboard Motors
F
Fairbanks-Morse
Fairfield Shipbuilding and Engineering Company
Fincantieri
Firth Brown Steels
Fleming and Ferguson
Foos Gas Engine Company
FPT Industrial
G
Gale Products
Garden Reach Shipbuilders & Engineers
L. Gardner and Sons
Gas Turbine Research Establishment
GE Transportation
General Electric
General Motors
Gourlay Brothers
Gray Marine Motor Company
H
Hall-Scott
Hitachi Zosen Corporation
Honda
Honda Marine
Hyundai Heavy Industries
Hyundai Heavy Industries Group
I
IHI Corporation
Anthony Inglis (shipbuilder)
Isotta Fraschini
Isuzu
J
J. Tylor and Sons
Jarvis Walker
John Inglis and Company
Johnson Outboards
JSC Kuznetsov
K
Kaluga Turbine Plant
Kawasaki Heavy Industries
Kelvin Diesels
John G. Kincaid & Company
Kolomna Locomotive Works
Komatsu Limited
Kubota
Kuznetsov Design Bureau
L
Lamborghini
M
MAN Diesel
MAN Energy Solutions
Marinediesel AB
McCulloch Motors Corporation
Mercury Marine
Mitsubishi Heavy Industries
Moteurs Baudouin
MTU Friedrichshafen
N
Robert Napier and Sons
Nissan Marine
Nissan Outboard Motors
Norman Engineering Co
O
Oceanvolt
Outboard Marine Corporation
P
Palmers Shipbuilding and Iron Company
Parsons Engineering
C. A. Parsons and Company
Charles Algernon Parsons
Penzadieselmash
Perkins Engines
Pythagoras Mechanical Workshop Museum
R
R A Lister and Company
Rolls-Royce Holdings
Rolls-Royce Submarines
RUMO Plant
S
Salyut Machine-Building Association
Samuel F. Hodge & Company
Scania AB
Seatek SPa diesels
SEMT Pielstick
Shaanxi Diesel Engine Heavy Industry
Shanghai Diesel Engine
Siemens
Sintz Gas Engine Company
Sulzer (manufacturer)
Suzuki
T
Rolls-Royce Power Systems
Tohatsu
Toyota
Turner Manufacturing Company
U
UEC Saturn
UEC-Perm Engines
Uljanik
Union Iron Works
United Engine Corporation
V
Vericor Power Systems
Vickers
Victoria Machinery Depot
VM Motori
Volvo
Volvo Penta
Voronezh Mechanical Plant
Vosper & Company
W
Wallsend Slipway & Engineering Company
Wärtsilä
West Bend Company
Westinghouse Electric Corporation
Wichmann Diesel
Peter William Willans
Y
Yamaha Motor Company
Yanmar
Yarrow Shipbuilders
Z
Zavolzhye Engine Factory
    """
    
    strade_parigi = """
    !
Boulevard di Parigi
A
Rue Agar
Avenue Montaigne
B
Boulevard Beaumarchais
Boulevard de Bonne-Nouvelle
Boulevard de Rochechouart
C
Rue du Calvaire
Boulevard des Capucines
Avenue des Champs-Élysées
Rue de la Chaussée-d'Antin
Boulevard de Clichy
Rue Clovis
D
Dictionnaire historique des rues de Paris
F
Rue du Faubourg-Saint-Martin
Boulevard des Filles-du-Calvaire
Avenue Foch
G
Avenue George V
Rue de Grenelle
H
Boulevard Haussmann
I
Avenue d'Iéna
Boulevard des Invalides
Avenue d'Italie
Boulevard des Italiens
L
Rue de Lappe
Rue Lepic
M
Boulevard de la Madeleine
Rue de Madrid
Boulevard de Magenta
Avenue de Malakoff
Rue Mallet-Stevens
Avenue Marceau
Rue des Mathurins
Quai de Montebello
Boulevard Montmartre
Rue Montorgueil
Rue Mouffetard
N
Rue Neuve-Notre-Dame
O
Boulevard Ornano
Rue Oudinot
P
Rue de la Paix
Passage de la Duée
Rue de Phalsbourg
Boulevard Poissonnière
Q
Quai Anatole-France
Quai d'Orsay
Quai Voltaire
R
Boulevard Raspail
Rue de l'Estrapade
Rue de Rennes
Rue de Rivoli
Rue de Sèvres
Rue du Bac 
S
Boulevard Saint-Denis
Boulevard Saint-Germain
Boulevard Saint-Martin
Rue Saint-Martin
Boulevard Saint-Michel
Rue Saint-Nicaise
Boulevard de Strasbourg 
T
Boulevard du Temple
Rue du Temple
Rue de Tolbiac
V
Rue de Varenne
Rue de Vaugirard
Rue de la Victoire
W
Avenue du Président-Wilson"""
    
    strade_roma = """
    A
Via Alessandrina
Via Anagnina
Via Appia Nuova
Via Ardeatina
Via Aurelia
Autostrada A90
Viale Aventino
B
Via del Babuino
Via Baldo degli Ubaldi
Via dei Banchi Vecchi
Borgo Angelico
Borgo Pio
Borgo Sant'Angelo
Borgo Santo Spirito
Borgo Vittorio
Via Borgognona
Via delle Botteghe Oscure
C
Via Casilina
Via Cassia
Via Cavour
Via dei Cessati Spiriti
Circonvallazione Casilina
Circonvallazione Ostiense
Via Collatina
Via Cristoforo Colombo
Via della Conciliazione
Via dei Condotti
Via dei Coronari
Via del Corso
E
Viale Europa
F
Via Flaminia
Via dei Fori Imperiali
Corso di Francia
Via Frattina
G
Galleria Giovanni XXIII
Galleria Pasa
Gay street di Roma
Circonvallazione Gianicolense
Via Giulia
Via Gregoriana
I
Corso d'Italia
L
Via Labicana
Via Latina
Via Laurentina
Via della Lungara
M
Strada statale 8 Via del Mare
Via Margutta
Via Merulana
N
Via del Nazareno
Via Nazionale
Via Nomentana
O
Via Ostiense
P
Via Portuense
Via Prenestina
Q
Via delle Quattro Fontane
Via Quattro Novembre
R
Viale Regina Margherita
Corso del Rinascimento
Via di Ripetta
S
Via Sacra
Via Salaria
Via San Giovanni in Laterano
Via delle Sette Chiese
Via Sistina
T
Tangenziale Est dello Sdo di Roma
Tangenziale Est di Roma
Via Tiburtina Valeria
Viale Palmiro Togliatti
Viale di Trastevere
Tridente
Corso Trieste
Via Trionfale
Via del Tritone
Via Tuscolana
V
Via Veientana
Via Venti Settembre
Via Ventiquattro Maggio
Viale Ventuno Aprile
Via del Teatro di Marcello
Vicolo delle Vacche
Corso Vittorio Emanuele II
Via Vittorio Veneto
    """
    
    strade_londra = """
    A
Avenue of Stars
B
Brick Lane
Broadwick Street
C
Cambridge Circus
Cannon Street
Charing Cross Road
Cheapside
Chelsea Embankment
Cornhill
D
Denmark Street
E
Elephant and Castle
Exhibition Road
F
Fenchurch Street
Finsbury Circus
Fleet Street
Flood Street
Fulham Road
G
Gillespie Road
Gloucester Road
Golborne Road
Gray's Inn Road
Green Street
Grosvenor Place
H
Harley Street
High Holborn
J
Jermyn Street
K
King William Street
King's Road
Kingsway
L
Lime Street
Lombard Street
Ludgate Circus
Ludgate Hill
O
Old Street
P
Park Lane
Portobello Road
Q
Queen Victoria Street
S
Sloane Street
T
Thames Embankment
Thames Street
The Cut
Tottenham Court Road
Turnpike Lane
V
Victoria Road"""
    
    strade_berlino = """
    A
Ackerstraße 
Adlergestell
Albertstraße 
Albrechtstraße 
Alfred-Kowalke-Straße
Allee der Kosmonauten 
Almstadtstraße
Alt-Biesdorf
Alt-Blankenburg
Alt-Friedrichsfelde
Alt-Kaulsdorf
Alt-Köpenick
Alt-Mahlsdorf
Alt-Mariendorf
Alt-Marzahn
Alt-Moabit
Altonaer Straße 
Am Berlin Museum
Am Großen Wannsee
Am Kupfergraben
Am Sandwerder
Am Treptower Park
Am Zirkus
Amalienstraße 
An der Stechbahn
Andreasstraße 
Anna-Louisa-Karsch-Straße
Arnimallee
Augsburger Straße 
Auguststraße 
AVUS
Axel-Springer-Straße
B
Badstraße 
Baumschulenstraße 
Beatrice-Zweig-Straße
Behrenstraße
Bergmannstraße 
Berlin-Potsdamer Chaussee
Berliner Allee 
Berliner Straße 
Bernauer Straße
Bismarckstraße 
Bleibtreustraße
Blumberger Damm
Blumenstraße 
Bölschestraße
Bornholmer Straße
Boxhagener Straße
Breite Straße 
Brüderstraße 
Brunnenstraße 
Budapester Straße 
Bülowstraße
Bundesallee 
Burgstraße 
Buschallee 
Buttmannstraße
C
Ceciliengärten
Charlottenburger Straße 
Chausseestraße
Clayallee
Columbiadamm
D
Danckelmannstraße
Danziger Straße
Dieffenbachstraße
Dominicusstraße
Dorfstraße 
Dorotheenstraße 
Dörpfeldstraße
Drakestraße 
E
Eberswalder Straße
Ebertstraße 
Eislebener Straße 
Elsa-Brändström-Straße 
Elsenstraße 
Enckestraße
Entlastungsstraße
Eschengraben
F
Falkenberger Chaussee
Falkoniergasse
Fasanenstraße 
Fasanerieallee 
Flatowallee
Fontanepromenade
Frankfurter Allee
Französische Straße 
Friedenstraße 
Friedrichsgracht
Friedrichstraße
Friesenstraße 
Friesickestraße
G
Gartenstraße 
General-Pape-Straße
Generalszug
Gerichtstraße 
Gertraudenstraße
Giesebrechtstraße
Glienicker Weg
Glinkastraße
Gneisenaustraße
Gneiststraße
Gottlieb-Dunkel-Straße
Graefestraße
Grazer Damm
Greenwichpromenade
Greifswalder Straße
Griebenowstraße
Groß-Berliner Damm
Große Hamburger Straße
Große Sternallee
Grünauer Straße
Grunerstraße 
Grunewaldstraße 
H
Hallesches Ufer
Hansastraße 
Hardenbergstraße
Hasenheide (Straße)
Hasensprung
Hauptstraße 
Hauptstraße 
Havelchaussee
Havelschanze
Heerstraße 
Heinrich-Heine-Straße 
Helenenhof 
Herbert-von-Karajan-Straße 
Hermannstraße 
Hertzallee
Herzbergstraße
Heynstraße
Hiroshimastraße
Hofjägerallee
Hohenzollerndamm
Hoher Wallgraben
Holzmarktstraße 
Hönower Straße
Hornstraße
Hortensienstraße 
Hufelandstraße
Hultschiner Damm
Husemannstraße 
I
In den Zelten
Indira-Gandhi-Straße
Innenstadtring 
Invalidenstraße 
J
Jägerstraße 
Jerusalemer Straße 
Joachimsthaler Straße
John-Foster-Dulles-Allee
Judengasse 
Jüdenstraße 
Jüdenstraße 
K
Kadiner Straße
Kaiserdamm
Kantstraße
Kapelle-Ufer
Karl-Marx-Allee
Karl-Liebknecht-Straße 
Karl-Marx-Straße 
Kastanienallee 
Kietz 
Kirchgasse 
Klemkestraße
Klosterstraße 
Kniprodestraße 
Knorrpromenade
Koenigsallee
Kolk (Spandau)
Koloniestraße 
Königin-Luise-Straße
Königstraße 
Königsweg 
Königsweg 
Königsweg 
Konrad-Wolf-Straße
Kopenhagener Straße
Köpenicker Straße
Kopernikusstraße 
Körtestraße
Kösliner Straße
Köthener Straße
Kottbusser Damm
Krausnickstraße
Kochstraße 
Am Krögel
Kulmer Straße
Kurfürstendamm
Kurfürstenstraße 
L
Landsberger Allee
Langhansstraße 
Lasdehner Straße
Lehrter Straße
Leipziger Straße 
Liesenstraße
Lietzenburger Straße
Lindenstraße 
Linienstraße 
Littenstraße
    """
    
    nomi_italiani = """
    Adele
Alessia
Alice
Anita
Anna
Arianna
Asia
Aurora
Azzurra
Beatrice
Benedetta
Bianca
Camilla
Carlotta
Caterina
Cecilia
Chiara
Chloe
Elena
Eleonora
Elisa
Emily
Emma
Eva
Francesca
Gaia
Giada
Ginerva
Gioia
Giorgia
Giulia
Greta
Irene
Isabel
Ludovica
Margherita
Maria
Marta
Martina
Matilde
Melissa
Mia
Miriam
Nicole
Noemi
Rebecca
Sara
Sofia
Viola
Vittoria
Abramo
Alessandro
Alessio
Andrea
Antonio
Brando
Christian
Daniel
Davide
Diego
Domenico
Edoardo
Elia
Emanuele
Enea
Federico
Filippo
Francesco
Franco
Gabriel
Giacomo
Gioele
Giorgio
Giovanni
Giulio
Giuseppe
Jacopo
Leonardo
Lorenzo
Luca
Luigi
Manuel
Marco
Matteo
Mattia
Michele
Nathan
Nicola
Nicolo
Pietro
Raffaele
Riccardo
Salvatore
Samuel
Simone
Stefano
Thomas
Tommaso
Valerius
Vincenzo
"""
    cognomi_italiani = """
    Rossi
Ferrari
Russo
Bianchi
Romano
Gallo
Costa
Fontana
Conti
Esposito
Ricci
Bruno
De Luca
Moretti
Marino
Greco
Barbieri
Lombardi
Giordano
Cassano
Colombo
Mancini
Longo
Leone
Martinelli
Marchetti
Martini
Galli
Gatti
Mariani
Ferrara
Santoro
Marini
Bianco
Conte
Serra
Farina
Gentile
Caruso
Morelli
Ferri
Testa
Ferraro
Pellegrini
Grassi
Rossetti
D'Angelo
Bernardi
Mazza
Rizzi
Natale"""
    nomi_tedeschi =  """
    Tobias
Jonas
Ben
Elias
Ben
Paolo
Leon
Finn
Elias
Jonas
Luis
Noè
Felix
Lukas
Jürgen
Karl
Stefan
Walter
Uwe
Hans
Klaus
Günter
Adalia
Erica
Ernestina
Federica
Greta
Heidi
Jenell
Kerstin
Leyn
Mallory
Marlene
Viveka
Wanda
Zelinda
Abigail
Adalheid
Adelheid
Agathe
Agnes
Agnethe
Albertina
Aleit
Alexandra
Alexia
Alfreda
Alina
Aloisia
Amalia
Andrea

Anelie
Angela
Angelika
Anke
Anna
Annelie
Anneliese
Annemarie
Anselma
Antje
Antonia
Barbara
Beata
    """
    cognomi_tedeschi = """
Müller
Schmidt
Schneider
Fischer
Weber
Meyer
Wagner
Becker
Schulz
Hoffmann
Schäfer
Koch
Bauer
Richter
Klein
Wolf
Schröder
Neumann
Schwarz
Zimmermann
Braun
Krüger
Hofmann
Hartmann
Lange
Schmitt
Werner
Schmitz
Krause
Meier
Lehmann
Schmid
Schulze
Maier
Köhler
Herrmann
Körtig
Walter
Mayer
Huber
Kaiser
Fuchs
Peters
Lang
Scholz
Möller
Weiß
Jung
Hahn
Schubert
Vogel
Friedrich
Keller
Günther
Frank
Berger
Winkler
Roth
Beck
Lorenz
Baumann
Franke
Albrecht
Schuster
Simon
Ludwig
Böhm
Winter
Kraus
Martin
Schumacher
Krämer
Vogt
Stein
Jäger
Otto
Sommer
Groß
Seidel
Heinrich
Brandt
Haas
Schreiber
Graf
Schulte
Dietrich
Ziegler
Kuhn
Kühn
Pohl
Engel
Horn
Busch
Bergmann
Thomas
Voigt
Sauer
Arnold
Wolff
Pfeiffer"""
    nomi_francesi = """
    Jean  
Marie  
Michel  
Claude  
Dominique  
Philippe  
Francis  
Pierre  
Alain  
Nathalie  
Bernard  
Isabelle  
Andre  
Patrick  
Catherine  
Daniel  
Jacques  
Sylvie  
Christian  
Eric  
Thierry  
Christophe  
Laurent  
Pascal  
Rene  
Monique  
Christine  
Joseph  
Olivier  
Anne  
Nicolas  
Robert  
Sandrine  
Valerie  
David  
Jacqueline  
Roger  
Sophie  
Guy  
Didier  
Bruno  
Nicole  
Marcel  
Marc  
Yves  
Georges  
Serge  
Laurence  
Julien  
Patricia  
Paul  
Henri  
Brigitte  
Vincent  
Christiane  
Stephane  
Corinne  
Maurice  
Annie  
Louis  
Stephanie  
Christelle  
Franck  
Chantal  
Frederic  
Celine  
Sebastien  
Denis  
Raymond  
Aurelie  
Gilles  
Caroline  
Veronique  
Guillaume  
Karine  
Denise  
Maria  
Jeanne  
Gerard  
Delphine  
Emilie  
Claudine  
Julie  
Colette  
Claire  
Yvette  
Sylvain  
Pascale  
Thomas  
Florence  
Roland  
Madeleine  
Charles  
Alexandre  
Sandra  
Annick  
Antoine  
Mireille  
Bernadette  
Helene  
    """
    cognomi_francesi = """
    Martin
Bernard
Robert
Richard
Durand
Dubois
Moreau
Simon
Laurent
Michel
Garcia
Thomas
Leroy
David
Morel
Roux
Girard
Fournier
Lambert
Lefebvre
Mercier
Blanc
Dupont
Faure
Bertrand
Morin
Garnier
Nicolas
Marie
Rousseau
Bonnet
Vincent
Henry
Masson
Robin
Martinez
Boyer
Muller
Chevalier
Denis
Meyer
Blanchard
Lemaire
Dufour
Gauthier
Vidal
Perez
Perrin
Fontaine
Joly
Jean
da Silva
Gautier
Roche
Roy
Pereira
Mathieu
Roussel
Duval
Guerin
Lopez
Rodriguez
Colin
Aubert
Lefevre
Marchand
Schmitt
Picard
Caron
Sanchez
Meunier
Gaillard
Louis
Nguyen
Lucas
Dumont
dos Santos
Brunet
Clement
Brun
Arnaud
Giraud
Barbier
Rolland
Charles
Hubert
Fernandes
Fabre
Moulin
Leroux
Dupuis
Guillaume
Roger
Paris
Guillot
Dupuy
Fernandez
Carpentier
Payet
Ferreira"""
    nomi_inglesi = """Adie
Ethelburg 
Angie 
Ashleigh
Ashton 
Aubrey
B
Barnes 
Barry 
Basil 
Bernadine
Bethany 
Betty
Braden 
Bradley
Brent 
Bret 
Brett
Burdine
C
Caden 
Cadence 
Carrington
Charlene 
Charles
Charlton 
Chay 
Chet
Christopher
Clinton
Corinna 
Cowden 
D
Daris
Darleen
Darlene 
Darnell
Deb 
Demi
Dennis
Diamond 
Doreen 
Dorothy 
Dustin 
E
Earlene
Elaine 
Elfriede
Eli 
Emery 
Emory 
Evan
G
Gabriel 
Georgiana
Gladys 
Greenbury
Gregory 
Greig 
Gwen 
H
Harley 
Hastings 
Hazel 
Heather 
Helton 
Henrietta 
Heston 
Holly 
Hulda 
I
Increase 
India 
Irene 
J
Jackie 
Jade 
January 
Jean 
Jemma 
Jenny 
Jerald
Jerrold
Jerry 
Jessie 
Jethro
Jigar 
Jill
Jocelyn
Jodie
Joey 
Justine
K
Kate 
Kathryn
Keaton 
Kendra
Kerr 
Kimball 
Kitty 
Kristy
Kylie 
L
Laren
Lawrence 
Lawson 
Leanne
Lianne
Louise 
Luci
M
Maddox 
Malford
Marlene 
Maud
Melinda
Melville 
Miley 
Millicent
Mindi 
Mindy
Molly 
Mort 
N
Nancy 
Nelson 
Nigel
O
Osbert
Ottilie
P
Pamela 
Pascoe
Percy
Pippa 
Poppy 
R
Rebecca 
Reynold
Rhoda 
Riley 
Roland 
Rosaleen
Rosalie 
Rosie 
Ruby 
Rupert 
Ruth 
S
Savannah 
Scarlett 
Sharon
Sheridan 
Shiloh 
Sidney 
Stacy 
Sydney 
T
Tammy 
Tim 
Timmy
Timothy 
Tracy 
Travis 
Trent 
Trudie
Tucker 
V
Velma
Vicary
Violet 
W
Walker 
Warren 
Whitney 
Wilfried
Woodrow """
    cognomi_inglesi = """
    Smith
Jones
Williams
Taylor
Brown
Davies
Evans
Wilson
Thomas
Johnson
Roberts
Robinson
Thompson
Wright
Walker
White
Edwards
Hughes
Green
Hall
Lewis
Harris
Clarke
Patel
Jackson
Wood
Turner
Martin
Cooper
Hill
Ward
Morris
Moore
Clark
Lee
King
Baker
Harrison
Morgan
Allen
James
Scott
Phillips
Watson
Davis
Parker
Price
Bennett
Young
Griffiths
Mitchell
Kelly
Cook
Carter
Richardson
Bailey
Collins
Bell
Shaw
Murphy
Miller
Cox
Richards
Khan
Marshall
Anderson
Simpson
Ellis
Adams
Singh
Begum
Wilkinson
Foster
Chapman
Powell
Webb
Rogers
Gray
Mason
Ali
Hunt
Hussain
Campbell
Matthews
Owen
Palmer
Holmes
Mills
Barnes
Knight
Lloyd
Butler
Russell
Barker
Fisher
Stevens
Jenkins
Murray
Dixon
Harvey"""
    
    strade_roma = [strada.strip().title() for strada in strade_roma.splitlines() if len(strada.strip()) > 1]
    strade_berlino = [strada.strip().title() for strada in strade_berlino.splitlines() if len(strada.strip()) > 1]
    strade_londra = [strada.strip().title() for strada in strade_londra.splitlines() if len(strada.strip()) > 1]
    strade_parigi = [strada.strip().title() for strada in strade_parigi.splitlines() if len(strada.strip()) > 1]
    
    strade = [strade_roma,  strade_berlino ,strade_londra, strade_parigi]
    
    cognomi_inglesi = [nome.strip().title() for nome in cognomi_inglesi.splitlines() if len(nome.strip()) > 1 if all(x.isalpha() or x.isspace() for x in nome)]
    cognomi_italiani = [nome.strip().title() for nome in cognomi_italiani.splitlines() if len(nome.strip()) > 1 if all(x.isalpha() or x.isspace() for x in nome)]
    cognomi_francesi = [nome.strip().title() for nome in cognomi_francesi.splitlines() if len(nome.strip()) > 1 if all(x.isalpha() or x.isspace() for x in nome)]
    cognomi_tedeschi = [nome.strip().title() for nome in cognomi_tedeschi.splitlines() if len(nome.strip()) > 1 if all(x.isalpha() or x.isspace() for x in nome)]
    
    cognomi = [cognomi_italiani, cognomi_tedeschi, cognomi_inglesi,cognomi_francesi]
    nomi_inglesi = [nome.strip().title() for nome in nomi_inglesi.splitlines() if len(nome.strip()) > 1 if all(x.isalpha() or x.isspace() for x in nome)]
    nomi_italiani = [nome.strip().title() for nome in nomi_italiani.splitlines() if len(nome.strip()) > 1 if all(x.isalpha() or x.isspace() for x in nome)]
    nomi_francesi = [nome.strip().title() for nome in nomi_francesi.splitlines() if len(nome.strip()) > 1 if all(x.isalpha() or x.isspace() for x in nome)]
    nomi_tedeschi = [nome.strip().title() for nome in nomi_tedeschi.splitlines() if len(nome.strip()) > 1 if all(x.isalpha() or x.isspace() for x in nome)]
    nomi = [nomi_italiani, nomi_tedeschi, nomi_inglesi, nomi_francesi ]
    
    nomi_f = [nome.strip().title() for nome in femmine.split() if len(nome) > 1 and nome.isalpha()]
    
    cantieri = [nome.strip().title() for nome in cantieri.splitlines() if len(nome) > 1 if all(x.isalpha() or x.isspace() for x in nome)]
    
    barche = [nome.title().strip() for nome in barche.splitlines() if len(nome) > 1 and nome.isalpha()]
    
    marche = [nome.strip().title() for nome in marche.splitlines() if len(nome) > 1 if all(x.isalpha() or x.isspace() for x in nome)]
    
    # for i in range(30):
    #     genera_barche(nomi_f, cantieri)
    #generaMotori(marche)
    # for i in range(10):
    #     generaModelli(dicb, dicc)
    # cur = con.cursor()
    # cur.execute(""" SELECT * from public."Model_boat" """)
    # print(cur.fetchall())
    # con.commit()
    # cur.close()
    for i in range(20):
        print(generaEmployee())
    
    