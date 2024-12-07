from debrisk2 import *
from datetime import datetime

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

iss = Satellite(satName="ISS", 
                physical_prop=dict(DryMass=473264.00,DragArea=1524.99,Cr=0,Cd=2.00,SRPArea=0.00),
                state_vector=["k",-3803.111683270652,5637.422077446301,0.651103754965438,-3.940598689126699,-2.661915521602177,5.99985773278453])

debris = Satellite(satName="debris", 
                physical_prop=dict(DryMass=2.00,DragArea=1.1,Cr=0,Cd=2.00,SRPArea=0.00),
                state_vector=["c",-4500.111683270652,6000.422077446301,8.651103754965438,-3.940598689126699,-1.661915521602177,5.99985773278453])
debris2 = Satellite(satName="debris2", 
                physical_prop=dict(DryMass=8.00,DragArea=1.1,Cr=0,Cd=2.00,SRPArea=0.00),
                state_vector=["k",-5000.111683270652,6200,5.651103754965438,-4.940598689126699,-2.661915521602177,5.99985773278453])

sat_list = [iss, debris, debris2]

fm1 = ForceModel(fmName = 'ForceModel1', potential=dict(Degree=4,Order=4),
                drag=dict(model=None),
                srp=dict(status='Off',Flux=1367,SRPModel='Spherical',NominalSun='149597870.691'),
                pm=dict(objects=""))

prop1 = Propagator(propName = 'Propagator1', forceModel = fm1)

rep1 = ReportFile(reportName = "Rep1", reportFileName = 'report1', spacecrafts = sat_list)

seq1 = MissionSequence(event = 'Propagate', object = prop1, parameters = sat_list, conditions = [[iss.satName, 'ElapsedSecs', 12000]])


gen_script(sat_list, [fm1], [prop1], [rep1], [seq1], 'pleaseWork')

run_script('pleaseWork')