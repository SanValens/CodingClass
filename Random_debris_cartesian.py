from debrisk2 import *
from datetime import datetime
import random
import math
"""
SOURCE: https://spotthestation.nasa.gov/trajectory_data.cfm

Con debrisk:
Propagar 1 satélite en orbita LEO

Propagar X piezas de debris de diferentes tamaños, 
ángulos y excentricidades y con decaimiento. 

Todos los parámetros que sean aleatorios pero dentro de ciertos rangos
Plottear un histograma con frecuencias de 
acercamiento en un rango específico de tiempo
Plottear un histograma con energías de colisión

META_START
OBJECT_NAME          = ISS
OBJECT_ID            = 1998-067-A
CENTER_NAME          = Earth
REF_FRAME            = EME2000
TIME_SYSTEM          = UTC
START_TIME           = 2024-11-27T12:00:00.000
USEABLE_START_TIME   = 2024-11-27T12:00:00.000
USEABLE_STOP_TIME    = 2024-12-12T12:00:00.000
STOP_TIME            = 2024-12-12T12:00:00.000
META_STOP

COMMENT Source: This file was produced by the TOPO office within FOD at JSC.
COMMENT Units are in kg and m^2
COMMENT MASS=473264.00
COMMENT DRAG_AREA=1524.99
COMMENT DRAG_COEFF=2.00
COMMENT SOLAR_RAD_AREA=0.00
COMMENT SOLAR_RAD_COEFF=0.00

"""
current_time = datetime.now()
FORMATTED_TIME = current_time.strftime("%Y-%m-%d %H:%M:%S")
EPOCH_INIT = '01 Jan 2000 00:00:00.00'

#state vector de la iss
iss = Satellite(satName="ISS", 
                physical_prop=dict(DryMass=473264.00,DragArea=1524.99,Cr=0,Cd=2.00,SRPArea=0.00),
                state_vector=["c",-3803.111683270652,5637.422077446301,0.651103754965438,-3.940598689126699,-2.661915521602177,5.99985773278453])

#Función para generar escombros aleatorios cerca de la ISS
def generar_debris_orbitas_similares(n, iss):
    debris_list = []
    
    #Extraer la posición y velocidad de la ISS
    x_iss, y_iss, z_iss = iss.state_vector[1:4]  #Posición de la ISS (en km)
    vx_iss, vy_iss, vz_iss = iss.state_vector[4:7]  #Velocidad de la ISS (en m/s)
    
    for i in range(n):
        # Introducir pequeñas perturbaciones en las posiciones y velocidades
        # Mantener el orden de magnitud de las posiciones y velocidades de la ISS
        delta_pos = random.uniform(-50, 50)  #Separación aleatoria (en km)
        delta_vel = random.uniform(-0.05, 0.05)  #Perturbación aleatoria de velocidad (en km/s)

        #Generar posiciones similares pero separadas
        x = x_iss + delta_pos * random.uniform(0.8, 1.2)  # Variación en X
        y = y_iss + delta_pos * random.uniform(0.8, 1.2)  # Variación en Y
        z = z_iss + delta_pos * random.uniform(0.8, 1.2)  # Variación en Z

        #Generar velocidades similares pero con perturbaciones
        vx = vx_iss + delta_vel * random.uniform(0.8, 1.2)  # Velocidad en X
        vy = vy_iss + delta_vel * random.uniform(0.8, 1.2)  # Velocidad en Y
        vz = vz_iss + delta_vel * random.uniform(0.8, 1.2)  # Velocidad en Z

        #Crear el objeto de debris con características físicas aleatorias
        debris = Satellite(satName=f"debris_{i+1}",
                           physical_prop=dict(DryMass=random.uniform(0.1, 1000.0),
                                              DragArea=random.uniform(0.5, 10.0),
                                              Cr=0, Cd=2.0, SRPArea=0.0),
                           state_vector=["c", x, y, z, vx, vy, vz])
        
        debris_list.append(debris)
    
    return debris_list

#Generar 30 debris con órbitas similares pero no idénticas a la ISS
debris_aleatorios = generar_debris_orbitas_similares(30, iss)

#Agregar los escombros generados a la lista de satélites (incluyendo la ISS)
sat_list = [iss] + debris_aleatorios
#determinar el modelo de fuerza
fm1 = ForceModel(fmName = 'ForceModel1', potential=dict(Degree=4,Order=4),
                drag=dict(model=None),
                srp=dict(status='Off',Flux=1367,SRPModel='Spherical',NominalSun='149597870.691'),
                pm=dict(objects=""))
#Determinar un propagador
prop1 = Propagator(propName = 'Propagator1', forceModel = fm1)
#determinar un report file
rep1 = ReportFile(reportName = "Rep1", reportFileName = 'report', spacecrafts = sat_list)
#determinar una secuencia de misión 
seq1 = MissionSequence(event = 'Propagate', object = prop1, parameters = sat_list, conditions = [[iss.satName, 'ElapsedSecs', 40000]])

#generar el script
gen_script(sat_list, [fm1], [prop1], [rep1], [seq1], 'pleaseWork')
#correr el script
run_script('pleaseWork')