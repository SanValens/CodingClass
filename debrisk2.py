#TEST MARIANA 
# Very important packages
from load_gmat import * # For the API to work from any directory, load_gmat.py has to be copied inside
from time import time

# Check usability and if not used, remove
import os
import numpy as np
from datetime import datetime
from dateutil import parser
import spiceypy as spy
import pandas as pd
import math as mt
import random
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

# For converting TLEs
from sgp4.earth_gravity import wgs84
from sgp4.io import twoline2rv
from sgp4.api import jday

# For plotting
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns

# Measure execution time
STATUS = time()

#Creates a string with the current time
current_time = datetime.now()
FORMATTED_TIME = current_time.strftime("%d %b %Y %H:%M:%S.%f")[:-3]


def elapsed_time():
    global STATUS
    end = time()
    print(f"{Fore.BLUE}Execution Time: {end - STATUS} s {Style.RESET_ALL}")
    #print(f"Execution time: {end - STATUS} s")
    STATUS = time()
    return end
#def coordinates(state_vector):

# Satellite class definition
"""
    TODO: allow Keplerian elements input
"""
class Satellite:
    def __init__(self, satName="Satellite",
                physical_prop=dict(DryMass=1,DragArea=1,Cr=2.2,Cd=2.2,SRPArea=1),
                epoch = FORMATTED_TIME,
                state_vector=[0,0,0,0,0,0]):
        
        self.satName = satName
        self.physical_prop = physical_prop
        self.epoch = epoch
        self.state_vector = state_vector

"""Describes the physical model used to simulate the dynamics in space
 * Is able to auto-name the force model if no name is provided"""
class ForceModel:
    counter = 1
    def __init__(self, fmName=None, potential=dict(Degree=2,Order=2),
                drag=dict(model=None),
                srp=dict(status='Off',Flux=1367,SRPModel='Spherical',NominalSun='149597870.691'),
                pm=dict(objects='') # {object1, object2, ..}
                ):
        if fmName:
            self.fmName = fmName
        else:
            self.fmName = f'DefaultProp_ForceModel{ForceModel.counter}'
            ForceModel.counter += 1
        self.potential = potential
        self.drag = drag
        self.srp = srp
        self.pm = pm


""" Propagates probes. You can change the method and just a few things more. Generally can be left in the default settings
    It can also autoname propagators to stop that annoying need 
"""
class Propagator:
    counter = 1
    def __init__(self, propName = None, forceModel = None, type = "RungeKutta89", initStep = 60, stopIfAccuracyIsViolated = True):
        if propName:
            self.propName = propName
        else:
            self.propName = f'DefaultProp{Propagator.counter}'
            ForceModel.counter += 1
        self.forceModel = forceModel if forceModel else ForceModel()
        self.initStep = initStep
        self.type = type
        self.stopIfAccuracyIsViolated = stopIfAccuracyIsViolated


"""
    * Enables you to create a report file but it is quite limited. It just let's you pull information about spacecrafts, no more.
    Variables must be written by hand in the 'variables' parameter
    It can also autoname reportfiles to stop that annoying need 
"""
class ReportFile:
    counter = 1
    def __init__(self, reportName = None, reportFileName = None, spacecrafts = [Satellite()], variables = ['UTCGregorian', 'EarthMJ2000Eq.X', 'EarthMJ2000Eq.Y', 'EarthMJ2000Eq.Z']):
        if reportName:
            self.reportName = reportName
        else:
            self.reportName = f'ReportFile{ReportFile.counter}'
            ForceModel.counter += 1
        self.spacecrafts = spacecrafts
        self.reportFileName = reportFileName if reportFileName else reportName
        self.variables = variables

"""
    * It is NOT a mission sequence but better a mission frame (just one step)
    * It needs a lot of work. So far the only available event is the Propagator and maybe 
    * TODO: Allow control logic or Manuver events
    * Obj: The object is the reference to accomplish the event, if the event is propagation, the object must
    * obviusly be a propagator. It depends on the need. And i insist on the fact that it needs a lot of work
    * paramters: sets what is affected by this event. For example...a satellite that is being propagated.
    * conditions: a matrix of conditions to stop the event or to characterize it further, it all depends on the application
    * (event), in the case of the propagation, its a list that contains the vector [satOfInteres, 'propertyOfInteres', 
    * 'valueReachedToStop'] in that order
"""
class MissionSequence:
    def __init__(self, event = 'Propagate', object = Propagator(), parameters = None, conditions = None):
        self.event = event
        self.object = object
        self.parameters = parameters if parameters else [Satellite()]
        self.conditions = conditions if conditions else [[self.parameters[0].satName, 'ElapsedSecs', 12000]]



# Utilities Sub-Class Definition
""" Create a class where elapsed time of execution is calculated, the data from the TLE can be read, transform to a CSV file,
 Numpy Array, and plotting data for further analysis
"""
class Utility:

    def __init__(self):
        self.Satellite = Satellite
        
    # Read CSV TLE File, convert it to a Pandas Dataframe and get timelapse between TLEs
    def read_csv_tle(self, state_source):
        sv_final = pd.read_csv(state_source,index_col=0)
        elapsed_time()
        sv_final['diff']=sv_final['datetime'].diff()*86400
        sv_final['diff']=sv_final['diff'].fillna(0)
        sv_final.to_csv("state_vector_time_diff.csv")
        return sv_final

    # Read CSV TLE File, convert it to a Pandas Dataframe and get timelapse between TLEs
    def read_csv_tle_diff(self, csv_time_diff_file):
        sv_diff=pd.read_csv(csv_time_diff_file)
        elapsed_time()
        sv_diff_last50=sv_diff['diff'].tail(50)
        sum_prop_time=sv_diff_last50['diff'].sum()
        # sv_diff_last50['diff'].apply()
        print(sum_prop_time)
        #sv_final.to_csv("state_vector_time_diff.csv")
        return sum_prop_time

        
    # Read TLEs and convert it/them
    def read_convert_TLE(self, tle_file):
        # Read TLE text file from object
        # spy.furnsh('latest_leapseconds.tls')
        sv_final=np.empty((0,8))
        #tle_file=f"tle_Envisat.txt"
        #lines=[]
        with open(tle_file, 'r') as f:
            lines=f.readlines()
        for i in range(0,len(lines),2):
            line1=lines[i].strip()
            line2=lines[i+1].strip()
            satellite=twoline2rv(line1,line2,wgs84)
            epoch=satellite.epoch
            year=epoch.year
            month=epoch.month
            day=epoch.day
            hours=epoch.hour
            minutes=epoch.minute
            seconds=epoch.second+round(epoch.microsecond/1e6,3)
            position,velocity=satellite.propagate(year, month, day, hours, minutes, seconds)
            jd, fr = jday(year, month, day, hours, minutes, seconds)
            julian_day = jd+fr
            """julday=367*year-mt.trunc(((7*(year+mt.trunc((month+9)/12)))/4))+mt.trunc(275*month/9)+day+1721013.5
            poday=(((((seconds/60)+minutes)/60)+hours)/24)
            utc_mdj=(julday-2430000.0)+poday # Modified Julian Date TT in GMAT"""
            utc_gmat=epoch.strftime('%d %b %Y %H:%M:%S.%f')[:-3] # string use .%f for more precision and [:-3] for 3 digit
            sv=np.array(position+velocity)#+sec_epoch)
            sv_sec_sv=np.append((julian_day),sv)#.astype(object)) # it was sec_epoch
            sv_utc_sec_sv=np.append(utc_gmat,sv_sec_sv.astype(object))
            sv_final=np.append(sv_final,sv_utc_sec_sv)
        
        sv_final = sv_final.reshape(-1,8)
        statevec_csv = pd.DataFrame(sv_final, columns=['datetime_str','datetime','x', 'y','z', 'vx', 'vy', 'vz'])
        statevec_csv.to_csv("state_vector.csv")
        # spy.unload('latest_leapseconds.tls')
        return statevec_csv

    def plot_time_diff(self, report_txt,csv_time_diff_file):
        # Plotting time difference and propagated orbits
        sv_diff=pd.read_csv(csv_time_diff_file)
        fig=px.scatter(sv_diff, x='datetime',y='y', title='Scatter Plot')
        fig.show()

    
    def plot_Scatter_GEO(self, txt_report_file):

        # Read the TXT report file data

        orbit_data = pd.read_fwf(txt_report_file)
        orbit_loc=orbit_data[[f"Envisat.Earth.RMAG",f"Envisat.Earth.Latitude",f"Envisat.Earth.Longitude"]]
        locations=np.array(orbit_loc[[f"Envisat.Earth.RMAG",f"Envisat.Earth.Latitude",f"Envisat.Earth.Longitude"]])
        #print(orbit_data,orbit_loc,locations)

        # Create a scattergeo plot
        Scatter_RA_DEC=go.Scattergeo(
            lat=locations[:,1],
            lon=locations[:,2],
            mode='markers',
            marker=dict(
                size=10,
                color=locations[:,0],   #'blue', # RMag
                symbol='circle',
                opacity=0.7
            )
        )

        Layout_SGeo=go.Layout(
            title='Object Positions',
            geo=dict(
                scope='world',
                projection_type='orthographic',
                #projection_type='equirectangular',
                showland=True,
                landcolor='rgb(217, 217, 217)',
                showcountries=True,
                countrycolor='rgb(255, 255, 255)'
            )
        )

        fig1=go.Figure(data=[Scatter_RA_DEC],layout=Layout_SGeo)
        fig1.show()


def run_script(scriptName):
    scriptName += ".script"
    elapsed_time()
    gmat.LoadScript(scriptName)
    gmat.RunScript()
    gmat.Help(scriptName) #Check Help object
    elapsed_time()


""" This is the heart of the code. It generates a .script file to be ran by GMAT
Structure:
    * Header: general info
    * Spacecraft: by each spacecraft. It's missing a looot of arguments
    * Forcemodel: decently equipped to change the dynamic properties. 
    * Propagator: Always references a forcemodel and adds some mathematical characteristics to solve de ODEs
    * Subscribers: Default settings for report file and default settings for visual view using GMAT (for debbuging if needed)
    * Mission sequence: I insist on the fact that it is a little hard-coded. The .script commands might vary too much
        by each type of event that it becomes impractical to code somthing like this. Insist again that more research is needed
"""
def gen_script(spacecrafts, forceModels,propagators, reportFiles, missseqs, fileName):
    global FORMATTED_TIME

    #As there me multiple spacecrafts/propagators etc we save each info's on a list element. Then just add them all together
    script_spacecrafts = []
    script_forces = [] 
    script_propagators = []
    script_reportFiles = []
    script_missionsequences = []



    script_header = f"""%General Mission Analysis Tool(GMAT) Script
%Created: {FORMATTED_TIME}
%This script was python generated using the Debrisk library
    """
    #Just making sure that even single elements are treated as arrays to avoid compiling errors
    if not isinstance(spacecrafts, list):
        spacecrafts = [spacecrafts]
    for spft in spacecrafts:
        #Creates a random RGB color
        random_rgb = [random.randint(0, 255) for _ in range(3)]
        if spft.state_vector[0] == "c":
            script_spacecrafts.append(f"""
%----------------------------------------
%---------- Spacecraft
%----------------------------------------
                                
Create Spacecraft {spft.satName};
GMAT {spft.satName}.DateFormat = UTCGregorian;
GMAT {spft.satName}.Epoch = '{spft.epoch}';
GMAT {spft.satName}.CoordinateSystem = EarthMJ2000Eq;

GMAT {spft.satName}.DisplayStateType = Cartesian;
GMAT {spft.satName}.X = {spft.state_vector[1]:.13f};
GMAT {spft.satName}.Y = {spft.state_vector[2]:.13f};
GMAT {spft.satName}.Z = {spft.state_vector[3]:.13f};
GMAT {spft.satName}.VX = {spft.state_vector[4]:.13f};
GMAT {spft.satName}.VY = {spft.state_vector[5]:.13f};
GMAT {spft.satName}.VZ = {spft.state_vector[6]:.13f};

% Additional
GMAT {spft.satName}.AtmosDensityScaleFactor = 1;
GMAT {spft.satName}.ExtendedMassPropertiesModel = 'None';
GMAT {spft.satName}.NAIFId = -10000001;
GMAT {spft.satName}.NAIFIdReferenceFrame = -9000001;
GMAT {spft.satName}.OrbitColor = [{random_rgb[0]} {random_rgb[1]} {random_rgb[2]}];
GMAT {spft.satName}.TargetColor = Teal;
GMAT {spft.satName}.OrbitErrorCovariance = [ 1e+70 0 0 0 0 0 ; 0 1e+70 0 0 0 0 ; 0 0 1e+70 0 0 0 ; 0 0 0 1e+70 0 0 ; 0 0 0 0 1e+70 0 ; 0 0 0 0 0 1e+70 ];
GMAT {spft.satName}.CdSigma = 1e+70;
GMAT {spft.satName}.CrSigma = 1e+70;
GMAT {spft.satName}.Id = 'SatId';
      
%----------------------------------------
%---------- Physical properties
%----------------------------------------
GMAT {spft.satName}.DryMass = {spft.physical_prop['DryMass']};
GMAT {spft.satName}.DragArea = {spft.physical_prop['DragArea']};
GMAT {spft.satName}.Cd = {spft.physical_prop["Cd"]};
GMAT {spft.satName}.Cr = {spft.physical_prop["Cr"]};
GMAT {spft.satName}.SRPArea = {spft.physical_prop["SRPArea"]};
        """)
        elif spft.state_vector[0] == "k":
            script_spacecrafts.append(f"""
%----------------------------------------
%---------- Spacecraft
%----------------------------------------
                                
Create Spacecraft {spft.satName};
GMAT {spft.satName}.DateFormat = UTCGregorian;
GMAT {spft.satName}.Epoch = '{spft.epoch}';
GMAT {spft.satName}.CoordinateSystem = EarthMJ2000Eq;

GMAT {spft.satName}.DisplayStateType = Keplerian;
GMAT {spft.satName}.SMA= {spft.state_vector[1]:.13f};
GMAT {spft.satName}.ECC = {spft.state_vector[2]:.13f};
GMAT {spft.satName}.INC = {spft.state_vector[3]:.13f};
GMAT {spft.satName}.RAAN = {spft.state_vector[4]:.13f};
GMAT {spft.satName}.AOP = {spft.state_vector[5]:.13f};
GMAT {spft.satName}.TA= {spft.state_vector[6]:.13f};

% Additional
GMAT {spft.satName}.AtmosDensityScaleFactor = 1;
GMAT {spft.satName}.ExtendedMassPropertiesModel = 'None';
GMAT {spft.satName}.NAIFId = -10000001;
GMAT {spft.satName}.NAIFIdReferenceFrame = -9000001;
GMAT {spft.satName}.OrbitColor = [{random_rgb[0]} {random_rgb[1]} {random_rgb[2]}];
GMAT {spft.satName}.TargetColor = Teal;
GMAT {spft.satName}.OrbitErrorCovariance = [ 1e+70 0 0 0 0 0 ; 0 1e+70 0 0 0 0 ; 0 0 1e+70 0 0 0 ; 0 0 0 1e+70 0 0 ; 0 0 0 0 1e+70 0 ; 0 0 0 0 0 1e+70 ];
GMAT {spft.satName}.CdSigma = 1e+70;
GMAT {spft.satName}.CrSigma = 1e+70;
GMAT {spft.satName}.Id = 'SatId';
      
%----------------------------------------
%---------- Physical properties
%----------------------------------------
GMAT {spft.satName}.DryMass = {spft.physical_prop['DryMass']};
GMAT {spft.satName}.DragArea = {spft.physical_prop['DragArea']};
GMAT {spft.satName}.Cd = {spft.physical_prop["Cd"]};
GMAT {spft.satName}.Cr = {spft.physical_prop["Cr"]};
GMAT {spft.satName}.SRPArea = {spft.physical_prop["SRPArea"]};
        """)
            

    if not isinstance(forceModels, list):
        forceModels = [forceModels]
    for fm in forceModels:
        forces = f"""
%----------------------------------------
%---------- ForceModels
%----------------------------------------
Create ForceModel {fm.fmName};
GMAT {fm.fmName}.CentralBody = Earth;
GMAT {fm.fmName}.PrimaryBodies = {{Earth}};
GMAT {fm.fmName}.RelativisticCorrection = Off;
"""
        #If there is no pointmasses that line of code can't even be written
        if fm.pm['objects']:
            forces += f"""
GMAT DefaultProp_ForceModel.PointMasses = {fm.pm['objects']};
"""
        else:
            forces += f""
        forces += f"""
GMAT {fm.fmName}.ErrorControl = RSSStep;
GMAT {fm.fmName}.GravityField.Earth.Degree = {fm.potential["Degree"]};
GMAT {fm.fmName}.GravityField.Earth.Order = {fm.potential["Order"]};
GMAT {fm.fmName}.GravityField.Earth.StmLimit = 100;
GMAT {fm.fmName}.GravityField.Earth.PotentialFile = 'JGM2.cof';
GMAT {fm.fmName}.GravityField.Earth.TideModel = 'None';"""
        
        #If there is no drag model this lines of code can't even be written
        if fm.drag['model']:
            forces += f"""GMAT DefaultProp_ForceModel.Drag.AtmosphereModel = {fm.drag['model']};
GMAT {fm.fmName}.Drag.HistoricWeatherSource = 'ConstantFluxAndGeoMag';
GMAT {fm.fmName}.Drag.PredictedWeatherSource = 'ConstantFluxAndGeoMag';
GMAT {fm.fmName}.Drag.CSSISpaceWeatherFile = 'SpaceWeather-All-v1.2.txt';
GMAT {fm.fmName}.Drag.SchattenFile = 'SchattenPredict.txt';
GMAT {fm.fmName}.Drag.F107 = 150;
GMAT {fm.fmName}.Drag.F107A = 150;
GMAT {fm.fmName}.Drag.MagneticIndex = 3;
GMAT {fm.fmName}.Drag.SchattenErrorModel = 'Nominal';
GMAT {fm.fmName}.Drag.SchattenTimingModel = 'NominalCycle';
GMAT {fm.fmName}.Drag.DragModel = 'Spherical';
            """
        else:
            forces += f"""
GMAT {fm.fmName}.Drag = None;
            """
        #If SRP is not enabled these lines of code can't even be written
        if fm.srp['status'] == 'On':
            forces += f"""
GMAT {fm.fmName}.SRP = On;
GMAT {fm.fmName}.SRP.Flux = {fm.srp["Flux"]};
GMAT {fm.fmName}.SRP.SRPModel = {fm.srp["SRPModel"]};
GMAT {fm.fmName}.SRP.Nominal_Sun = {fm.srp["NominalSun"]};
            """
        else: 
            forces += f"""
GMAT {fm.fmName}.SRP = Off;
"""

        script_forces.append(forces)
    if not isinstance(propagators, list):
        propagators = [propagators]
    for prop in propagators:
        script_propagators.append(f"""
%----------------------------------------
%---------- Propagators
%----------------------------------------
Create Propagator {prop.propName};
GMAT {prop.propName}.FM = {prop.forceModel.fmName};
GMAT {prop.propName}.Type = {prop.type};
GMAT {prop.propName}.InitialStepSize = {prop.initStep};
GMAT {prop.propName}.Accuracy = 9.999999999999999e-12;
GMAT {prop.propName}.MinStep = 0.001;
GMAT {prop.propName}.MaxStep = 2700;
GMAT {prop.propName}.MaxStepAttempts = 50;
GMAT {prop.propName}.StopIfAccuracyIsViolated = {prop.stopIfAccuracyIsViolated};
        """)

    if not isinstance(reportFiles, list):
        reportFiles = [reportFiles]
    for rpF in reportFiles:
        if not isinstance(rpF.variables, list):
            rpF.variables = [rpF.variables]
        if not isinstance(rpF.spacecrafts, list):
            rpF.spacecrafts = [rpF.spacecrafts]
        cuFolder = os.getcwd()
        reportFilePath = f"{cuFolder}\{rpF.reportFileName}.txt"
        print(reportFilePath)
        #Creating lists for variables to report and satellites to include in the OrbitView
        rAdd = ''
        vAdd = ''
        for sat in rpF.spacecrafts:
            vAdd += f'{sat.satName}, '
            for val in rpF.variables:
                rAdd += f'{sat.satName}.{val}, '
        rAdd = rAdd.rstrip(", ") #Remove the last comma and space
        vAdd = vAdd.rstrip(", ") #Remove the last comma and space

        script_reportFiles.append(f"""
%----------------------------------------
%---------- Subscribers
%----------------------------------------
Create ReportFile {rpF.reportName};
GMAT {rpF.reportName}.SolverIterations = Current;
GMAT {rpF.reportName}.UpperLeft = [ 0.02950819672131148 0.05714285714285714 ];
GMAT {rpF.reportName}.Size = [ 0.5975409836065574 0.7957142857142857 ];
GMAT {rpF.reportName}.RelativeZOrder = 138;
GMAT {rpF.reportName}.Maximized = false; 
GMAT {rpF.reportName}.Filename = '{reportFilePath}'
GMAT {rpF.reportName}.Add = {{{rAdd}}}
GMAT {rpF.reportName}.WriteHeaders = true;
GMAT {rpF.reportName}.LeftJustify = On;
GMAT {rpF.reportName}.ZeroFill = Off;
GMAT {rpF.reportName}.FixedWidth = true;
GMAT {rpF.reportName}.Delimiter = ' ';
GMAT {rpF.reportName}.ColumnWidth = 23;
GMAT {rpF.reportName}.WriteReport = true;

Create OrbitView DefaultOrbitView;
GMAT DefaultOrbitView.SolverIterations = Current;
GMAT DefaultOrbitView.UpperLeft = [ 0.002225189141076991 0 ];
GMAT DefaultOrbitView.Size = [ 0.5002225189141077 0.4497950819672131 ];
GMAT DefaultOrbitView.RelativeZOrder = 63;
GMAT DefaultOrbitView.Maximized = false;
GMAT DefaultOrbitView.Add = {{{vAdd}, Earth}};
GMAT DefaultOrbitView.CoordinateSystem = EarthMJ2000Eq;
GMAT DefaultOrbitView.DrawObject = [ true true ];
GMAT DefaultOrbitView.DataCollectFrequency = 1;
GMAT DefaultOrbitView.UpdatePlotFrequency = 50;
GMAT DefaultOrbitView.NumPointsToRedraw = 0;
GMAT DefaultOrbitView.ShowPlot = true;
GMAT DefaultOrbitView.MaxPlotPoints = 20000;
GMAT DefaultOrbitView.ShowLabels = true;
GMAT DefaultOrbitView.ViewPointReference = Earth;
GMAT DefaultOrbitView.ViewPointVector = [ 30000 0 0 ];
GMAT DefaultOrbitView.ViewDirection = Earth;
GMAT DefaultOrbitView.ViewScaleFactor = 1;
GMAT DefaultOrbitView.ViewUpCoordinateSystem = EarthMJ2000Eq;
GMAT DefaultOrbitView.ViewUpAxis = Z;
GMAT DefaultOrbitView.EclipticPlane = Off;
GMAT DefaultOrbitView.XYPlane = On;
GMAT DefaultOrbitView.WireFrame = Off;
GMAT DefaultOrbitView.Axes = On;
GMAT DefaultOrbitView.Grid = Off;
GMAT DefaultOrbitView.SunLine = Off;
GMAT DefaultOrbitView.UseInitialView = On;
GMAT DefaultOrbitView.StarCount = 7000;
GMAT DefaultOrbitView.EnableStars = On;
GMAT DefaultOrbitView.EnableConstellations = On;        
        """)
    script_missionsequences.append(f"""
%----------------------------------------
%---------- Mission Sequence
%----------------------------------------
BeginMissionSequence;""")
    
    i = 0
    if not isinstance(missseqs, list):
        missseqs = [missseqs]
    for miss in missseqs:
        if not isinstance(miss.parameters, list):
            miss.parameters = [miss.parameters]
        if not isinstance(miss.conditions, list):
            miss.conditions = [miss.conditions]
        if(miss.event == 'Propagate'):
            #Hard coded commands for the propagation situation
            param = ''
            cond = ''
            
            for p in miss.parameters:
                param += f'{p.satName}, '
            for c in miss.conditions:
                cond += f'{c[0]}.{c[1]} = {c[2]}, '

            param = param.rstrip(", ") #Remove the last comma and space
            cond = cond.rstrip(", ") #Remove the last comma and space
            
            
            script_missionsequences.append(f"""
{miss.event} {miss.object.propName}({param}) {{{cond}}};
            """)
        elif(miss.event == 'Other thing'):
            #ADD MORE EVENTS HERE
            pass

    script_final = script_header
    for scr in script_spacecrafts:
        script_final += scr
    
    for scr in script_forces:
        script_final += scr

    for scr in script_propagators:
        script_final += scr

    for scr in script_reportFiles:
        script_final += scr

    for scr in script_missionsequences:
        script_final += scr

    fileName += '.script'
    
    print(f"{Fore.LIGHTRED_EX}Saving script: {fileName} {Style.RESET_ALL}")
    f=open(fileName,"w")
    f.write(script_final)
    f.close()