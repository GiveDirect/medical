#!/usr/bin/python3

import sys
import urllib.parse
import json
import subprocess
import re

OK = {'success':'true','message':'The Command Completed Successfully'};

# Testing Only!

myjson = json.load(sys.stdin)

# json cleanup
myjson = json.dumps(myjson, indent=4, sort_keys=False)

# Delete these!
myjson = re.sub(r'\"[A-Z].*/', '"', myjson)
myjson = re.sub(r'\"Services_.*([\n]+)', '', myjson)
myjson = re.sub(r'.*false\",?([\n]+)', '', myjson)
myjson = re.sub(r'.*gathered.*([\n])+', '', myjson)
myjson = re.sub(r'",', '', myjson)

# Start gathering values!
patientNum = re.findall('.*Patient_Number.*', myjson)
patientNum = re.sub(r'\s+"Patient_Number.*: "', '', str(patientNum))

imm = re.findall('.*Immunizations.*', myjson)
imm = re.sub(r'\s+"Immunizations.*: "', '', str(imm))
imm = re.sub(r' ', ', ', str(imm))

check = re.findall('.*_Check.*', myjson)
check = re.sub(r'((\s+)?\'(\s+)?)', '', str(check))
check = re.sub(r'((\s+)?\")', '', str(check))
check = re.sub(r':true', '', str(check))
check = re.sub(r'(\[)|(\])', '', str(check))
check = re.sub(r'(General_)|(Illness_)|(STDs_)', '', str(check))

check = list(check.split(','))

treat = re.findall('.*_Treated.*', myjson)
treat = re.sub(r'((\s+)?\'(\s+)?)', '', str(treat))
treat = re.sub(r'((\s+)?\")', '', str(treat))
treat = re.sub(r':true', '', str(treat))
treat = re.sub(r'(\[)|(\])', '', str(treat))
treat = re.sub(r'(General_)|(Illness_)|(STDs_)', '', str(treat))

treat = list(treat.split(','))

refer = re.findall('.*_Referral.*', myjson)
refer = re.sub(r'((\s+)?\'(\s+)?)', '', str(refer))
refer = re.sub(r'((\s+)?\")', '', str(refer))
refer = re.sub(r':true', '', str(refer))
refer = re.sub(r'(\[)|(\])', '', str(refer))
refer = re.sub(r'(General_)|(Illness_)|(STDs_)', '', str(refer))

refer = list(refer.split(','))

myCTR = check + treat + refer
myCTR.sort()

value = re.findall('.*_value.*', myjson)
value = re.sub(r'((\s+)?\'(\s+)?)', '', str(value))
value = re.sub(r'((\s+)?\")', '', str(value))
value = re.sub(r':', '=', str(value))
value = re.sub(r'(Vitals_)|(_value)', '', str(value))
value = re.sub(r'(\[)|(\])', '', str(value))

value = list(value.split(','))
value.sort()

notes = re.findall('.*_Notes.*', myjson)
notes = re.sub(r'\s+"', '', str(notes))
notes = re.sub(r'"', '', str(notes))

# for x in range(len(myCTR)): 
#    print(myCTR[x]);
    
endpt = "https://docs.google.com/forms/d/e/1FAIpQLSfUwugrsJl2_eEnz7rV_E3QEsX1YCNbpAHFPV17oyg66y47wA/formResponse?usp=pp_url&" 
parms = {'entry.4151265': str(patientNum), 
         'entry.1319736686': str(imm), 
         'entry.236690816': str(myCTR), 
         'entry.1937888729': str(notes),         
         'entry.2056706490': str(value)
} 
 
sp = subprocess.run(["/usr/bin/curl","-s","-o","/dev/null","-w","%{http_code}", endpt + urllib.parse.urlencode(parms)], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

print('Content-Type: application/json\n\n')
if (sp.stdout == "200"):
    print(json.dumps(OK))   
else:
    print(json.dump(myjson, sys.stdout))
