from curses.ascii import isalpha
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
    nomi_f = [nome.strip().title() for nome in femmine.split() if len(nome) > 1 and nome.isalpha()]
    
    
    cantieri = [nome.strip().title() for nome in cantieri.splitlines() if len(nome) > 1 if all(x.isalpha() or x.isspace() for x in nome)]
    
    barche = [nome.title().strip() for nome in barche.splitlines() if len(nome) > 1 and nome.isalpha()]
    
    marche = [nome.strip().title() for nome in marche.splitlines() if len(nome) > 1 if all(x.isalpha() or x.isspace() for x in nome)]
    
    # for i in range(30):
    #     genera_barche(nomi_f, cantieri)
    generaMotori(marche)
    # for i in range(10):
    #     generaModelli(dicb, dicc)
    # cur = con.cursor()
    # cur.execute(""" SELECT * from public."Model_boat" """)
    # print(cur.fetchall())
    # con.commit()
    # cur.close()
    
    
    