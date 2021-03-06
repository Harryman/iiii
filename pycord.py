import Adafruit_BBIO.ADC as adc
import Adafruit_BBIO.GPIO as io
import time
import datetime
import os
import pymongo
from pymongo import MongoClient


mongo setup---------------
mongo = MongoClient('mongoURL')
db = mongo.bitHeat
collect = db.whProtoLog1


adc.setup()

rtable=[[-40,336479.00],[-39,314904.00],[-38,294848.00],[-37,276194.00],[-36,258838.00],[-35,242681.00],[-34,227632.00],[-33,213610.00],[-32,200539.00],[-31,188349.00],[-30,176974.00],[-29,166356.00],[-28,156441.00],[-27,147177.00],[-26,138518.00],[-25,130421.00],[-24,122847.00],[-23,115759.00],[-22,109122.00],[-21,102906.00],[-20,97081.00],[-19,91621.00],[-18,86501.00],[-17,81698.00],[-16,77190.00],[-15,72957.00],[-14,68982.00],[-13,65246.00],[-12,61736.00],[-11,58434.00],[-10,55329.00],[-9,52407.00],[-8,49656.00],[-7,47066.00],[-6,44626.00],[-5,42327.00],[-4,40159.00],[-3,38115.00],[-2,36187.00],[-1,34368.00],[0,32650.00],[1,31029.00],[2,29498.00],[3,28052.00],[4,26685.00],[5,25392.00],[6,24170.00],[7,23013.00],[8,21918.00],[9,20882.00],[10,19901.00],[11,18971.00],[12,18090.00],[13,17255.00],[14,16463.00],[15,15712.00],[16,14999.00],[17,14323.00],[18,13681.00],[19,13072.00],[20,12493.00],[21,11942.00],[22,11419.00],[23,10922.00],[24,10450.00],[25,10000.00],[26,9572.00],[27,9165.00],[28,8777.00],[29,8408.00],[30,8057.00],[31,7722.00],[32,7402.00],[33,7098.00],[34,6808.00],[35,6531.00],[36,6267.00],[37,6015.00],[38,5775.00],[39,5545.00],[40,5326.00],[41,5117.00],[42,4917.00],[43,4725.00],[44,4543.00],[45,4368.00],[46,4201.00],[47,4041.00],[48,3888.00],[49,3742.00],[50,3602.00],[51,3468.00],[52,3340.00],[53,3217.00],[54,3099.00],[55,2986.00],[56,2878.00],[57,2774.00],[58,2675.00],[59,2579.00],[60,2488.00],[61,2400.00],[62,2316.00],[63,2235.00],[64,2157.00],[65,2083.00],[66,2011.00],[67,1942.00],[68,1876.00],[69,1813.00],[70,1752.00],[71,1693.00],[72,1637.00],[73,1582.00],[74,1530.00],[75,1480.00],[76,1432.00],[77,1385.00],[78,1340.00],[79,1297.00],[80,1255.00],[81,1215.00],[82,1177.00],[83,1140.00],[84,1104.00],[85,1070.00],[86,1037.00],[87,1005.00],[88,973.80],[89,944.10],[90,915.50],[91,887.80],[92,861.20],[93,835.40],[94,810.60],[95,786.60],[96,763.50],[97,741.20],[98,719.60],[99,698.70],[100,678.60],[101,659.10],[102,640.30],[103,622.20],[104,604.60],[105,587.60]]

def C2F(c):
	return c*1.8+32
	

print "A0 = Hot Tank Tempurature"
print "A1 = Water Heater In temp"
print "A2 = Water Heater Out temp"
print "A3 = Water Heater Tank temp"
print "using 1k ohm lower leg V/D resistor"



#avcc = input('Measured ADC VCC Voltage:')
avcc=1.8


f = open((time.ctime()+".csv"),'w')
f.write("timeStamp,Hot Tank Temp, WH in Temp, WH out Temp,WH Tank Temp, ml Since last Timestamp\n")

pumpPin = "GPIO1_28"
io.setup(pumpPin, io.IN)
#io.cleanup()
io.add_event_detect(pumpPin,io.RISING)
last = time.time()
flow = 0

def mlConversion(val):
	return (val*60)/1000


def ain2c(adcVal):
	if(adcVal>0):
		res=(1000*(avcc-(adcVal*avcc)))/(adcVal*avcc)
		for i in range(len(rtable)):
			if( rtable[i][1]<res):
				preRes = rtable[i-1][1]
				preTemp = rtable[i-1][0]
				highRes = rtable[i][1]
				resRange = preRes - highRes;
				return ((preRes - res)/resRange)+preTemp 
		return "Conversion Not Found"
	else:
		return "NC"
a0 = 0
a1 = 0
a2 = 0
a3 = 0
aCount = 0

try:
	while True:
		a0 +=adc.read('AIN0')
		a1 +=adc.read('AIN1')
		a2 +=adc.read('AIN2')
		a3 +=adc.read('AIN3')	
		aCount += 1
		if io.event_detected("pumpPin"):
			flow += 91.667 

		if((time.time() - 1)> last): 
			a0 /= aCount
			a1 /= aCount
			a2 /= aCount
			a3 /= aCount		
			a0 = ain2c(a0)
			a1 = ain2c(a1)
			a2 = ain2c(a2)
			a3 = ain2c(a3)
			os.system('clear')
			#f.write(str(time.time())+","+str(a0)+","+str(a1)+","+str(a2)+","+str(a3)+","+str(flow)+"\n")
			log = {"timeStamp":datetime.datetime.now(),"hotTank":str(a0),"whIn":str(a1),"whOut":str(a2),"whTank":str(a3),"mL":str(flow)}
			collect.insert(log)
			print "A0 Hot Tank Temp:", 
			print a0
			print "A1 WH in  Temp:",
			print a1
			print "A2 WH out Temp:",
			print a2
			print "A3 WH Tank Temp:",
			print a3
			print "Flow ml/s",
			print flow
			a0 = 0
			a1 = 0
			a2 = 0
			a3 = 0
			aCount = 0
			flow = 0
			last = time.time()
		
except KeyboardInterrupt:
	f.close
	pass

