import psycopg2

con = psycopg2.connect(
    host = "localhost",
    database = "yachtCharter",
    user = "postgres",
    password = "DataBase01"
)



boat_name = 'Flavia'
print(boat_name)
cur = con.cursor()
cur.execute("SELECT boat_hull_number,model_name FROM Boat WHERE boat_name = %s", (boat_name,))
print(cur.fetchall())
con.commit()
cur.close()



''' SQL DUMP
create table Boat (
boat_hull_number integer primary key,
boat_name varchar(20) not null,
boat_sail_number integer not null,
boat_maker varchar(30) not null,
boat_construction_year integer not null,
boat_launching integer not null,
located_seaport_ID varchar(20) not null,
model_name varchar(30) not null
);

create table Boat (
boat_hull_number integer primary key,
boat_name varchar(20) not null,
boat_sail_number integer not null,
boat_maker varchar(30) not null,
boat_construction_year integer not null,
boat_launching integer not null,
located_seaport_ID varchar(20) not null,
model_name varchar(30) not null
);





'''