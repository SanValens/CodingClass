from debrisk2 import *
from datetime import datetime
import random
import math

#Función para generar órbitas keplerianas perturbadas
def generar_debris_keplerianos(n, iss_keplerian):
    debris_list = []

    # Extraer los elementos keplerianos de la ISS
    a_iss, e_iss, i_iss, raan_iss, argp_iss, nu_iss = iss_keplerian

    for j in range(n):
        # Perturbaciones controladas para cada elemento kepleriano
        a = a_iss + random.uniform(0, 10)  # Semieje mayor perturbado (en km)
        e = max(0, e_iss + random.uniform(0, 0.001))  # Excentricidad perturbada (asegurar que sea >= 0)
        i = i_iss + random.uniform(0, 0.5) * math.pi / 180  # Inclinación perturbada (en radianes)
        raan = raan_iss + random.uniform(0, 0.5) * math.pi / 180  # Nodo ascendente perturbado (en radianes)
        argp = argp_iss + random.uniform(0, 0.5) * math.pi / 180  # Argumento del perigeo perturbado (en radianes)
        nu = random.uniform(0, 360) * math.pi / 180  # Anomalía verdadera aleatoria (en radianes)

        # Crear un objeto Satellite con los parámetros keplerianos
        debris = Satellite(
            satName=f"debris_{j+1}",
            physical_prop=dict(DryMass=random.uniform(0.001,1000),  # Masa aleatoria (en kg)
                               DragArea=random.uniform(0.001,10),  # Área de arrastre aleatoria (en m²)
                               Cr=0, Cd=2.0, SRPArea=0.0),
            state_vector=["k", a, e, i, raan, argp, nu]  # Coordenadas Keplerianas
        )

        debris_list.append(debris)

    return debris_list

#Coordenadas keplerianas iniciales de la ISS
#a: Semieje mayor (en km)
#e: Excentricidad
#i: Inclinación (en radianes)
#raan: Nodo ascendente (en radianes)
#argp: Argumento del perigeo (en radianes)
#nu: Anomalía verdadera (en radianes)
iss_keplerian = (
    6771,  # Semieje mayor (400 km sobre el nivel del mar)
    0.001,  # Excentricidad
    math.radians(51.64),  # Inclinación
    math.radians(0),  # Nodo ascendente
    math.radians(0),  # Argumento del perigeo
    math.radians(0)  # Anomalía verdadera
)

# Generar 30 escombros con coordenadas keplerianas similares a la ISS
debris_aleatorios = generar_debris_keplerianos(30, iss_keplerian)

# Agregar los escombros generados a la lista de satélites (incluyendo la ISS)
iss = Satellite(
    satName="ISS",
    physical_prop=dict(DryMass=473264.00, DragArea=1524.99, Cr=0, Cd=2.00, SRPArea=0.00),
    state_vector=["k"] + list(iss_keplerian)
)

sat_list = [iss] + debris_aleatorios

# Configurar el modelo de fuerza
fm1 = ForceModel(fmName='ForceModel1', potential=dict(Degree=4, Order=4),
                 drag=dict(model=None),
                 srp=dict(status='Off', Flux=1367, SRPModel='Spherical', NominalSun='149597870.691'),
                 pm=dict(objects=""))

# Configurar un propagador
prop1 = Propagator(propName='Propagator1', forceModel=fm1)

# Configurar un archivo de reporte
rep1 = ReportFile(reportName="Rep1", reportFileName='report', spacecrafts=sat_list)

# Configurar una secuencia de misión
seq1 = MissionSequence(event='Propagate', object=prop1, parameters=sat_list,
                       conditions=[[iss.satName, 'ElapsedSecs', 40000]])

# Generar el script
gen_script(sat_list, [fm1], [prop1], [rep1], [seq1], 'pleaseWork')

# Correr el script
run_script('pleaseWork')

