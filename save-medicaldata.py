#!/usr/bin/python3

import urllib.parse
import json
import subprocess

OK = {'success':'true','message':'The Command Completed Successfully'};

# Testing Only!
# myjson = {
#    "Patient_Number": "2020-v1",
#    "Services_Performed": "Immunization Screening_Testing Treatment Education Referral_To_Hospital",
#    "Immunizations_Performed": "DTwPHibHepB Yellow_Fever Meningococcal_A",
#    "Screening_Testing": "Eyes Hearing Skin_Check",
#    "Treatments_Performed": "HIV Wound_Care",
#    "Treatment_Notes": "Left Knee Cut",    
#    "Education_Discussed": "General_Hygiene Gender_Health Childcare",
#    "General_Notes": "200 unichars = 퉉ͮݼȘ򡯛X𡩇𓷯wh񴡚ڝȎ䦫񘎦ԛຯꙋ̿ѝp괂򱉂💩,쪮ǳ򙤇軮Ɉ/ާuՊ偊&έ𘔦՚훂K󋆨tɹ*ה຋ஷγ=عF턨㎡领$Ǉ떘𕧜𠍻Ҁ?ۇ7Ɓ𕚟񾋒󀃣S与񚣰Ӛ]&Оߴ䙱yG򔷧@촏།󷍈톥񂋄<𯍆߯L٬݄񾋬.x¤ڽch󓐾꒹Û򊛙裎󛴅Żԇ赊Yz񨗒ɒ򮏹򚽹℥bҶѶ谗جW胲K֎򲍟򥕌׿܎ޚ󦚉됱5󁸘{ᶊ餿ػ󷅠E󖓑킈2袁=эg̈́񹩌vȽזw@>䯦v򻣇d뒴끁򣝱񺩙񏍪󜗶ꂞʞ޲ٹ�򤂵ĺ񗆌Ԭ[=ۙ鳪"
#}

myjson = json.load(sys.stdin)

endpt = "https://docs.google.com/forms/d/e/1FAIpQLSfUwugrsJl2_eEnz7rV_E3QEsX1YCNbpAHFPV17oyg66y47wA/formResponse?usp=pp_url&" 
parms = {'entry.4151265': str(myjson['Patient_Number']).replace(" ",", "), 
         'entry.1319736686': str(myjson['Immunizations_Performed']).replace(" ",", "), 
         'entry.236690816': str(myjson['Screening_Testing']).replace(" ",", "), 
         'entry.1381571885': str(myjson['Treatments_Performed']).replace(" ",", "),
         'entry.1937888729': str(myjson['Treatment_Notes']),         
         'entry.1751984836': str(myjson['Education_Discussed']).replace(" ",", "), 
         'entry.2056706490': str(myjson['General_Notes'])} 
 
sp = subprocess.run(["/usr/bin/curl","-s","-o","/dev/null","-w","%{http_code}", endpt + urllib.parse.urlencode(parms)], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

print('Content-Type: application/json\n\n')
if (sp.stdout == "200"):
    print(json.dumps(OK))   
else:
    print(json.dump(myjson, sys.stdout))
