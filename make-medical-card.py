#!/usr/bin/python3

import csv
import cgi
import codecs
import time
import os
import re
import urllib.request
from datetime import datetime

# CSV Mappings
###############

TEMPLATE_FILE="card.template.html"

CHECK_IN_CSV_URL="https://docs.google.com/spreadsheets/d/e/2PACX-1vTdGrYYysLlD4lLaIUhhroiw4kDtNWjbpiF5NximTtBK6OAq8OJYJ5ulcPks0_BWDo9PZw7aFc9-37s/pub?gid=535824425&single=true&output=csv&range="
CHECK_IN_END_COL='D'
CHECK_IN_COL_CNT=4

VIT_CSV_URL="https://docs.google.com/spreadsheets/d/e/2PACX-1vTdGrYYysLlD4lLaIUhhroiw4kDtNWjbpiF5NximTtBK6OAq8OJYJ5ulcPks0_BWDo9PZw7aFc9-37s/pub?gid=79449362&single=true&output=csv&range="
VIT_END_COL='CG'
VIT_COL_CNT=85

IMM_CSV_URL="https://docs.google.com/spreadsheets/d/e/2PACX-1vTdGrYYysLlD4lLaIUhhroiw4kDtNWjbpiF5NximTtBK6OAq8OJYJ5ulcPks0_BWDo9PZw7aFc9-37s/pub?gid=1308664369&single=true&output=csv&range="
IMM_END_COL='Y'
IMM_COL_CNT=25

CTR_CSV_URL="https://docs.google.com/spreadsheets/d/e/2PACX-1vTdGrYYysLlD4lLaIUhhroiw4kDtNWjbpiF5NximTtBK6OAq8OJYJ5ulcPks0_BWDo9PZw7aFc9-37s/pub?gid=862169354&single=true&output=csv&range="
CTR_END_COL='GB'
CTR_COL_CNT=184

NOTES_CSV_URL="https://docs.google.com/spreadsheets/d/e/2PACX-1vTdGrYYysLlD4lLaIUhhroiw4kDtNWjbpiF5NximTtBK6OAq8OJYJ5ulcPks0_BWDo9PZw7aFc9-37s/pub?gid=99678788&single=true&output=csv&range="
NOTES_END_COL='C'
NOTES_COL_CNT=3

PAS_URL="https://ee.humanitarianresponse.info/x/NxuQSXxW"
IMM_REF_URL="http://www.vacfa.uct.ac.za/sites/default/files/image_tool/images/210/Immunization_Schedules/Ghana.pdf"

cur = time.time()
os.environ["TZ"] = "GMT"
time.tzset()

def isTrue(v):
  return v.lower() in ("TRUE", "True", "true", "1")

def valiDate(date_text):
    try:
        if (re.search('^[0-9][0-9]-[A-Z][a-z][a-z]-[0-9][0-9][0-9][0-9]$',str(date_text))):
            return True
        else:
            raise ValueError
    except ValueError:
        return False

def add_Footer(patientNum, row):
    return "Data from row (<b>" + row + "</b>) in the Google Spreadsheet as of : <b>" + time.strftime("%T %Z", time.localtime(cur)) + "</b><br><hr><p>Please remember to take the Patient Action Survey (PAS) for this patient, linked <a href='" + PAS_URL + '/?&d[Patient_Number]=' + patientNum + "' target='_blank'>here</a>.\n"

def labelBP(BPs,BPd):
  # BPs (<89) || BPd (<59) = low
  # BPs (90-119) && BPd (60-79) = normal
  # BPs (120-129) && BPd (60-79) = pre-hypertension
  # BPs (130-139) || BPd (80-89) = hypertension-1
  # BPs (140-179) || BPd (90-119) = hypertension-2
  # BPs (>=180) = hypertension-3
  # BPd (>=120) = hypertension-3
  out = "<td>n/a</td>" 
  if (BPs.isnumeric() or BPd.isnumeric()):
      BPs = int(BPs)
      BPd = int(BPd)
      if ((BPs>=180 and BPs<=300) or (BPd>=120 and BPd<=300)):
          out = "<td style='color: white; background-color:#be272c'>HTN-3</td>"
      elif ((BPs>=140 and BPs<=179) or (BPd>=90 and BPd<=119)): 
          out = "<td style='background-color:#e0656a'>HTN-2</td>"
      elif ((BPs>=130 and BPs<=139) or (BPd>=80 and BPd<=89)):
          out = "<td style='background-color:#f1c564'>HTN-1</td>"
      elif ((BPs>=120 and BPs<=129) and (BPd>=60 and BPd<=79)):
          out = "<td style='background-color:#fce74c'>Pre-HTN</td>"
      elif ((BPs>=90 and BPs<=119) and (BPd>=60 and BPd<=79)):
          out = "<td style='background-color:#7cc580'>Normal</td>"
      elif (BPs<=89 or BPd<=59):
          out = "<td style='background-color:#80d6f9'>Low</td>"
  return out

def add_VitLine(date,age,weight,height,SBP,DBP,PulseR,FBS,RBS,Resp,Temp,PulseO,BMI,BPCat):
    out = str("<tr><td>" + date + "</td><td>" + age + "</td><td>" + weight + "</td><td>" + height + "</td><td>" + BMI + "</td><td>" + SBP + "</td><td>" + DBP + "</td>" + labelBP(SBP,DBP) + "<td>" + PulseR + "</td><td>" + FBS + "</td><td>" + RBS + "</td><td>" + Resp + "</td><td>" + Temp + "</td><td>" + PulseO + "</td></tr>") 
    return out

def add_Vit(date1,age1,weight1,height1,SBP1,DBP1,PulseR1,FBS1,RBS1,Resp1,Temp1,PulseO1,BMI1,BPCat1,date2,age2,weight2,height2,SBP2,DBP2,PulseR2,FBS2,RBS2,Resp2,Temp2,PulseO2,BMI2,BPCat2,date3,age3,weight3,height3,SBP3,DBP3,PulseR3,FBS3,RBS3,Resp3,Temp3,PulseO3,BMI3,BPCat3,date4,age4,weight4,height4,SBP4,DBP4,PulseR4,FBS4,RBS4,Resp4,Temp4,PulseO4,BMI4,BPCat4,date5,age5,weight5,height5,SBP5,DBP5,PulseR5,FBS5,RBS5,Resp5,Temp5,PulseO5,BMI5,BPCat5,date6,age6,weight6,height6,SBP6,DBP6,PulseR6,FBS6,RBS6,Resp6,Temp6,PulseO6,BMI6,BPCat6):

    out = "<table><tr><th class='vitals'>Visit<br>Date</th><th class='vitals'>Age</th><th class='vitals'>Weight<br>(kg)</th><th class='vitals'>Height<br>(cm)</th><th class='vitals'>BMI</th><th class='vitals'>BP<br>(SYS)</th><th class='vitals'>BP<br>(DIA)</th><th class='vitals'>BP Cat</th><th class='vitals'>Pulse<br>Rate</th><th class='vitals'>FBS</th><th class='vitals'>RBS</th><th class='vitals'>Resp</th><th class='vitals'>Temp<br>(c)</th><th class='vitals'>Pulse<br>Ox</th></tr>" + add_VitLine(date1,age1,weight1,height1,SBP1,DBP1,PulseR1,FBS1,RBS1,Resp1,Temp1,PulseO1,BMI1,BPCat1) + "\n"
    out = out + add_VitLine(date2,age2,weight2,height2,SBP2,DBP2,PulseR2,FBS2,RBS2,Resp2,Temp2,PulseO2,BMI2,BPCat2) + "\n"
    out = out + add_VitLine(date3,age3,weight3,height3,SBP3,DBP3,PulseR3,FBS3,RBS3,Resp3,Temp3,PulseO3,BMI3,BPCat3) + "\n"
    out = out + add_VitLine(date4,age4,weight4,height4,SBP4,DBP4,PulseR4,FBS4,RBS4,Resp4,Temp4,PulseO4,BMI4,BPCat4) + "\n"
    out = out + add_VitLine(date5,age5,weight5,height5,SBP5,DBP5,PulseR5,FBS5,RBS5,Resp5,Temp5,PulseO5,BMI5,BPCat5) + "\n"
    out = out + add_VitLine(date6,age6,weight6,height6,SBP6,DBP6,PulseR6,FBS6,RBS6,Resp6,Temp6,PulseO6,BMI6,BPCat6) + "</table>\n"
    return str(out)

def add_Imm(BGC1,OPV1,OPV2,OPV3,OPV4,R1,R2,Hep1,Hep2,Hep3,Pn1,Pn2,Pn3,IPV1,YF1,MR1,MR2,M1,MenA1,Td1,Td2,Td3,Td4,COVID1):
    out = "<table><tr><th class='imm'>Immunization</th><th class='imm'></th><th class='imm'></th><th class='imm'></th><th class='imm'></th></tr><tr><td>BGC</td><td>" + BGC1 + "</td></tr>\n"
    out = out + "<tr><td>OPV</td><td>" + OPV1 + "</td><td>" + OPV2 + "</td><td>" + OPV3 + "</td><td>" + OPV4 + "</td></tr>\n"
    out = out + "<tr><td>Rotavirus</td><td>" + R1 + "</td><td>" + R2 + "</td></tr>\n"
    out = out + "<tr><td>DTwPHibHepB</td><td>" + Hep1 + "</td><td>" + Hep2 + "</td><td>" + Hep3 + "</td></tr>\n"
    out = out + "<tr><td>Pneumo_conj</td><td>" + Pn1 + "</td><td>" + Pn2 + "</td><td>" + Pn3 + "</td></tr>\n"
    out = out + "<tr><td>IPV (from Sept-2017)</td><td>" + IPV1 + "</td></tr>\n"
    out = out + "<tr><td>YF</td><td>" + YF1 + "</td></tr>\n"
    out = out + "<tr><td>MR</td><td>" + MR1 + "</td><td>" + MR2 + "</td></tr>\n"
    out = out + "<tr><td>Measles</td><td>" + M1 + "</td></tr>\n"
    out = out + "<tr><td>MenA</td><td>" + MenA1 + "</td></tr>\n"
    out = out + "<tr><td>Td</td><td>" + Td1 + "</td><td>" + Td2 + "</td><td>" + Td3 + "</td><td>" + Td4 + "</td></tr>\n"
    out = out + "<tr><td>COVID19</td><td>" + COVID1 + "</td></tr></table>\n"    
    out = out + "<p><i><a href='" + IMM_REF_URL + "' target='_blank'>National  Immunization Schedule - Ghana</a></i><br></div>\n"    
    return str(out)

def processCTR(label,dateArr,fieldArr,outArr):
    # outArr = [rout,tout,cout,iout]
    # dateAdd - newest first
    # print(label + " -> " + str(dateArr) + " = " + str(fieldArr) + "<br>\n")

    if (valiDate(dateArr[0]) and isTrue(fieldArr[0][2])):
        # Referrals first (pos 2) -> rout
        outArr[0] = outArr[0] + "<tr><td>" + label + "</td><td>" + dateArr[0] + "</td>\n"
        if (valiDate(dateArr[1]) and isTrue(fieldArr[1][2])):
            outArr[0] = outArr[0] + "<td>" + dateArr[1] + "</td>\n"
            if (valiDate(dateArr[2]) and isTrue(fieldArr[2][2])):
                outArr[0] = outArr[0] + "<td>" + dateArr[2] + "</td>\n"
            else:
                outArr[0] = outArr[0] + "</tr>\n"
        else:
            outArr[0] = outArr[0] + "</tr>\n"
    elif (valiDate(dateArr[0]) and isTrue(fieldArr[0][1])):
        # Treatments next (pos 1) -> tout
        outArr[1] = outArr[1] + "<tr><td>" + label + "</td><td>" + dateArr[0] + "</td>\n"
        if (valiDate(dateArr[1]) and isTrue(fieldArr[1][1])):
            outArr[1] = outArr[1] + "<td>" + dateArr[1] + "</td>\n"
            if (valiDate(dateArr[2]) and isTrue(fieldArr[2][1])):
                outArr[1] = outArr[1] + "<td>" + dateArr[2] + "</td>\n"
            else:
                outArr[1] = outArr[1] + "</tr>\n"
        else:
            outArr[1] = outArr[1] + "</tr>\n"
    elif (valiDate(dateArr[0]) and isTrue(fieldArr[0][0])):
        # Checks next (pos 0) -> tout
        outArr[2] = outArr[2] + "<tr><td>" + label + "</td><td>" + dateArr[0] + "</td>\n"
        if (valiDate(dateArr[1]) and isTrue(fieldArr[1][0])):
            outArr[2] = outArr[2] + "<td>" + dateArr[1] + "</td>\n"
            if (valiDate(dateArr[2]) and isTrue(fieldArr[2][0])):
                outArr[2] = outArr[2] + "<td>" + dateArr[2] + "</td>\n"
            else:
                outArr[2] = outArr[2] + "</tr>\n"
        else:
            outArr[2] = outArr[2] + "</tr>\n"
    else:
        outArr[3] = outArr[3] + "<tr><td>" + label + "</td></tr>\n"
    return(outArr)

def add_CTRTables(date1,eyes1,hearing1,mouth1,skin1,preg1,snake1,other1,hyper1,malaria1,asthma1,sugar1,hepb1,hepc1,herps1,syph1,chlam1,candi1,gono1,warts1,hiv1,date2,eyes2,hearing2,mouth2,skin2,preg2,snake2,other2,hyper2,malaria2,asthma2,sugar2,hepb2,hepc2,herps2,syph2,chlam2,candi2,gono2,warts2,hiv2,date3,eyes3,hearing3,mouth3,skin3,preg3,snake3,other3,hyper3,malaria3,asthma3,sugar3,hepb3,hepc3,herps3,syph3,chlam3,candi3,gono3,warts3,hiv3):
    rout = "<table><tr><th class='ctrh'>Recent Referrals</th><th class='ctr1'>Visit 1</th><th class='ctr1'>Visit 2</th><th class='ctr1'>Visit 3</th></tr>"
    tout = "<table><tr><th class='ctrh'>Recent Treatments</th><th class='ctr1'>Visit 1</th><th class='ctr1'>Visit 2</th><th class='ctr1'>Visit 3</th></tr>"
    cout = "<table><tr><th class='ctrh'>Recent Testing / Screening</th><th class='ctr1'>Visit 1</th><th class='ctr1'>Visit 2</th><th class='ctr1'>Visit 3</th></tr>"
    iout = "<table><tr><th class='ctrh'>Ideas </th></tr>"
    
    dateArr = [date1,date2,date3]
    outArr = [rout,tout,cout,iout]

    fieldArr = [eyes1,eyes2,eyes3]
    outArr = processCTR("Eyes",dateArr,fieldArr,outArr)
    fieldArr = [hearing1,hearing2,hearing3]
    outArr = processCTR("Hearling",dateArr,fieldArr,outArr)
    fieldArr = [mouth1,mouth2,mouth3]
    outArr = processCTR("Mouth",dateArr,fieldArr,outArr)
    fieldArr = [skin1,skin2,skin3]
    outArr = processCTR("Skin Check",dateArr,fieldArr,outArr)
    fieldArr = [preg1,preg2,preg3]
    outArr = processCTR("Pregnancy",dateArr,fieldArr,outArr)
    fieldArr = [snake1,snake2,snake3]
    outArr = processCTR("Wound Care<br>(snake)",dateArr,fieldArr,outArr)
    fieldArr = [other1,other2,other3]
    outArr = processCTR("Wound Care<br>(other)",dateArr,fieldArr,outArr)
    fieldArr = [hyper1,hyper2,hyper3]
    outArr = processCTR("Hypertension",dateArr,fieldArr,outArr)
    fieldArr = [malaria1,malaria2,malaria3]
    outArr = processCTR("Malaria",dateArr,fieldArr,outArr)
    fieldArr = [asthma1,asthma2,asthma3]
    outArr = processCTR("Asthma",dateArr,fieldArr,outArr)
    fieldArr = [sugar1,sugar2,sugar3]
    outArr = processCTR("Blood Sugar",dateArr,fieldArr,outArr)
    fieldArr = [hepb1,hepb2,hepb3]
    outArr = processCTR("Hepatitis B",dateArr,fieldArr,outArr)
    fieldArr = [hepc1,hepc2,hepc3]
    outArr = processCTR("Hepatitis C",dateArr,fieldArr,outArr)
    fieldArr = [herps1,herps2,herps3]
    outArr = processCTR("Herpes",dateArr,fieldArr,outArr)
    fieldArr = [syph1,syph2,syph3]
    outArr = processCTR("Syphilis",dateArr,fieldArr,outArr)
    fieldArr = [chlam1,chlam2,chlam3]
    outArr = processCTR("Chlamydia",dateArr,fieldArr,outArr)
    fieldArr = [candi1,candi2,candi3]
    outArr = processCTR("Candidiasis",dateArr,fieldArr,outArr)
    fieldArr = [gono1,gono2,gono3]
    outArr = processCTR("Gonorrhea",dateArr,fieldArr,outArr)
    fieldArr = [warts1,warts2,warts3]
    outArr = processCTR("Warts",dateArr,fieldArr,outArr)
    fieldArr = [hiv1,hiv2,hiv3]
    outArr = processCTR("HIV / AIDS",dateArr,fieldArr,outArr)

    out = outArr[0] + "</table>" + outArr[1] + "</table>" + outArr[2] + "</table>" + outArr[3] + "</table>"
    return str(out)

def make_CTR(CTRRow0,CTRRow1,CTRRow2,CTRRow3,CTRRow4,CTRRow5,CTRRow6,CTRRow7,CTRRow8,CTRRow9,CTRRow10,CTRRow11,CTRRow12,CTRRow13,CTRRow14,CTRRow15,CTRRow16,CTRRow17,CTRRow18,CTRRow19,CTRRow20,CTRRow21,CTRRow22,CTRRow23,CTRRow24,CTRRow25,CTRRow26,CTRRow27,CTRRow28,CTRRow29,CTRRow30,CTRRow31,CTRRow32,CTRRow33,CTRRow34,CTRRow35,CTRRow36,CTRRow37,CTRRow38,CTRRow39,CTRRow40,CTRRow41,CTRRow42,CTRRow43,CTRRow44,CTRRow45,CTRRow46,CTRRow47,CTRRow48,CTRRow49,CTRRow50,CTRRow51,CTRRow52,CTRRow53,CTRRow54,CTRRow55,CTRRow56,CTRRow57,CTRRow58,CTRRow59,CTRRow60,CTRRow61,CTRRow62,CTRRow63,CTRRow64,CTRRow65,CTRRow66,CTRRow67,CTRRow68,CTRRow69,CTRRow70,CTRRow71,CTRRow72,CTRRow73,CTRRow74,CTRRow75,CTRRow76,CTRRow77,CTRRow78,CTRRow79,CTRRow80,CTRRow81,CTRRow82,CTRRow83,CTRRow84,CTRRow85,CTRRow86,CTRRow87,CTRRow88,CTRRow89,CTRRow90,CTRRow91,CTRRow92,CTRRow93,CTRRow94,CTRRow95,CTRRow96,CTRRow97,CTRRow98,CTRRow99,CTRRow100,CTRRow101,CTRRow102,CTRRow103,CTRRow104,CTRRow105,CTRRow106,CTRRow107,CTRRow108,CTRRow109,CTRRow110,CTRRow111,CTRRow112,CTRRow113,CTRRow114,CTRRow115,CTRRow116,CTRRow117,CTRRow118,CTRRow119,CTRRow120,CTRRow121,CTRRow122,CTRRow123,CTRRow124,CTRRow125,CTRRow126,CTRRow127,CTRRow128,CTRRow129,CTRRow130,CTRRow131,CTRRow132,CTRRow133,CTRRow134,CTRRow135,CTRRow136,CTRRow137,CTRRow138,CTRRow139,CTRRow140,CTRRow141,CTRRow142,CTRRow143,CTRRow144,CTRRow145,CTRRow146,CTRRow147,CTRRow148,CTRRow149,CTRRow150,CTRRow151,CTRRow152,CTRRow153,CTRRow154,CTRRow155,CTRRow156,CTRRow157,CTRRow158,CTRRow159,CTRRow160,CTRRow161,CTRRow162,CTRRow163,CTRRow164,CTRRow165,CTRRow166,CTRRow167,CTRRow168,CTRRow169,CTRRow170,CTRRow171,CTRRow172,CTRRow173,CTRRow174,CTRRow175,CTRRow176,CTRRow177,CTRRow178,CTRRow179,CTRRow180,CTRRow181,CTRRow182):
    date1 = CTRRow0
    eyes1 = [CTRRow1,CTRRow2,CTRRow3]
    hearing1 = [CTRRow4,CTRRow5,CTRRow6]
    mouth1 = [CTRRow7,CTRRow8,CTRRow9]
    skin1 = [CTRRow10,CTRRow11,CTRRow12]
    preg1 = [CTRRow13,CTRRow14,CTRRow15]
    snake1 = [CTRRow16,CTRRow17,CTRRow18]
    other1 = [CTRRow19,CTRRow20,CTRRow21]
    hyper1 = [CTRRow22,CTRRow23,CTRRow24]
    malaria1 = [CTRRow25,CTRRow26,CTRRow27]
    asthma1 = [CTRRow28,CTRRow29,CTRRow30]
    sugar1 = [CTRRow31,CTRRow32,CTRRow33]
    hepb1 = [CTRRow34,CTRRow35,CTRRow36]
    hepc1 = [CTRRow37,CTRRow38,CTRRow39]
    herps1 = [CTRRow40,CTRRow41,CTRRow42]
    syph1 = [CTRRow43,CTRRow44,CTRRow45]
    chlam1 = [CTRRow46,CTRRow47,CTRRow48]
    candi1 = [CTRRow49,CTRRow50,CTRRow51]
    gono1 = [CTRRow52,CTRRow53,CTRRow54]
    warts1 = [CTRRow55,CTRRow56,CTRRow57]
    hiv1 = [CTRRow58,CTRRow59,CTRRow60]
    date2 = CTRRow61
    eyes2 = [CTRRow62,CTRRow63,CTRRow64]
    hearing2 = [CTRRow65,CTRRow66,CTRRow67]
    mouth2 = [CTRRow68,CTRRow69,CTRRow70]
    skin2 = [CTRRow71,CTRRow72,CTRRow73]
    preg2 = [CTRRow74,CTRRow75,CTRRow76]
    snake2 = [CTRRow77,CTRRow78,CTRRow79]
    other2 = [CTRRow80,CTRRow81,CTRRow82]
    hyper2 = [CTRRow83,CTRRow84,CTRRow85]
    malaria2 = [CTRRow86,CTRRow87,CTRRow88]
    asthma2 = [CTRRow89,CTRRow90,CTRRow91]
    sugar2 = [CTRRow92,CTRRow93,CTRRow94]
    hepb2 = [CTRRow95,CTRRow96,CTRRow97]
    hepc2 = [CTRRow98,CTRRow99,CTRRow100]
    herps2 = [CTRRow101,CTRRow102,CTRRow103]
    syph2 = [CTRRow104,CTRRow105,CTRRow106]
    chlam2 = [CTRRow107,CTRRow108,CTRRow109]
    candi2 = [CTRRow110,CTRRow111,CTRRow112]
    gono2 = [CTRRow113,CTRRow114,CTRRow115]
    warts2 = [CTRRow116,CTRRow117,CTRRow118]
    hiv2 = [CTRRow119,CTRRow120,CTRRow121]
    date3 = CTRRow122
    eyes3 = [CTRRow123,CTRRow124,CTRRow125]
    hearing3 = [CTRRow126,CTRRow127,CTRRow128]
    mouth3 = [CTRRow129,CTRRow130,CTRRow131]
    skin3 = [CTRRow132,CTRRow133,CTRRow134]
    preg3 = [CTRRow135,CTRRow136,CTRRow137]
    snake3 = [CTRRow138,CTRRow139,CTRRow140]
    other3 = [CTRRow141,CTRRow142,CTRRow143]
    hyper3 = [CTRRow144,CTRRow145,CTRRow146]
    malaria3 = [CTRRow147,CTRRow148,CTRRow149]
    asthma3 = [CTRRow150,CTRRow151,CTRRow152]
    sugar3 = [CTRRow153,CTRRow154,CTRRow155]
    hepb3 = [CTRRow156,CTRRow157,CTRRow158]
    hepc3 = [CTRRow159,CTRRow160,CTRRow161]
    herps3 = [CTRRow162,CTRRow163,CTRRow164]
    syph3 = [CTRRow165,CTRRow166,CTRRow167]
    chlam3 = [CTRRow168,CTRRow169,CTRRow170]
    candi3 = [CTRRow171,CTRRow172,CTRRow173]
    gono3 = [CTRRow174,CTRRow175,CTRRow176]
    warts3 = [CTRRow177,CTRRow178,CTRRow179]
    hiv3 = [CTRRow180,CTRRow181,CTRRow182]
    
    out = add_CTRTables(date1,eyes1,hearing1,mouth1,skin1,preg1,snake1,other1,hyper1,malaria1,asthma1,sugar1,hepb1,hepc1,herps1,syph1,chlam1,candi1,gono1,warts1,hiv1,date2,eyes2,hearing2,mouth2,skin2,preg2,snake2,other2,hyper2,malaria2,asthma2,sugar2,hepb2,hepc2,herps2,syph2,chlam2,candi2,gono2,warts2,hiv2,date3,eyes3,hearing3,mouth3,skin3,preg3,snake3,other3,hyper3,malaria3,asthma3,sugar3,hepb3,hepc3,herps3,syph3,chlam3,candi3,gono3,warts3,hiv3)
    return(out)

def add_Notes(tnotes,gnotes):
    out = "<table><tr><th class='noteh'>Treatment Notes</th></tr>"
    out = out + "<tr><td>" + tnotes + "</td></tr></table><p>\n"
    out = out + "<table><tr><th class='noteh'>General Notes</th></tr>"
    out = out + "<tr><td>" + gnotes + "</td></tr></table>\n"
    return str(out)        

def get_Row(url,rowNum,endCol,colCnt):
    fullUrl = url + "A" + rowNum + ":" + endCol + rowNum
    response = urllib.request.urlopen(fullUrl)
    text = response.read().decode('utf-8')
    row = text.split(",")
    # print(str(row))    
    # print("*****" + str(len(row)))    
    if (len(row) != colCnt):
        print("<H1>GiveDirect Error</H1>")
        print("Valid record not found in Google Sheet at row (" + str(row) + "), try a different row...")
    else: 
        return row

if __name__ == "__main__":
    try:
        print("Content-Type: text/html")    # HTML is following
        print()                             # blank line, end of headers
        form = cgi.FieldStorage()
        if "row" not in form:
         print("<H1>GiveDirect Error</H1>")
         print("<h3>You must send a 'row' as a GET argument.</h3><br><hr>")
        
        rowNum = form["row"].value
        # rowNum="6"

        templateStr=codecs.open(TEMPLATE_FILE, 'r').read()
        
        # csvFile = open("data.csv")
        # csvFile = open("sample.csv")        
        # readCSV = csv.reader(csvFile)
        
        # readCSV = csv.reader(text)
        # for row in readCSV:
       
        checkInRow = get_Row(CHECK_IN_CSV_URL,rowNum,CHECK_IN_END_COL, CHECK_IN_COL_CNT)
        vitRow = get_Row(VIT_CSV_URL,rowNum,VIT_END_COL,VIT_COL_CNT)
        immRow = get_Row(IMM_CSV_URL,rowNum,IMM_END_COL,IMM_COL_CNT)
        CTRRow = get_Row(CTR_CSV_URL,rowNum,CTR_END_COL,CTR_COL_CNT)
        notesRow = get_Row(NOTES_CSV_URL,rowNum,NOTES_END_COL,NOTES_COL_CNT)
        
        templateStr = templateStr.replace("MC_PATIENT_NUM",checkInRow[0])

        templateStr = templateStr.replace("MC_PATIENT_PHONE",checkInRow[3])
        templateStr = templateStr.replace("MC_VITALS",add_Vit(vitRow[1],vitRow[2],vitRow[3],vitRow[4],vitRow[5],vitRow[6],vitRow[7],vitRow[8],vitRow[9],vitRow[10],vitRow[11],vitRow[12],vitRow[13],vitRow[14],vitRow[15],vitRow[16],vitRow[17],vitRow[18],vitRow[19],vitRow[20],vitRow[21],vitRow[22],vitRow[23],vitRow[24],vitRow[25],vitRow[26],vitRow[27],vitRow[28],vitRow[29],vitRow[30],vitRow[31],vitRow[32],vitRow[33],vitRow[34],vitRow[35],vitRow[36],vitRow[37],vitRow[38],vitRow[39],vitRow[40],vitRow[41],vitRow[42],vitRow[43],vitRow[44],vitRow[45],vitRow[46],vitRow[47],vitRow[48],vitRow[49],vitRow[50],vitRow[51],vitRow[52],vitRow[53],vitRow[54],vitRow[55],vitRow[56],vitRow[57],vitRow[58],vitRow[59],vitRow[60],vitRow[61],vitRow[62],vitRow[63],vitRow[64],vitRow[65],vitRow[66],vitRow[67],vitRow[68],vitRow[69],vitRow[70],vitRow[71],vitRow[72],vitRow[73],vitRow[74],vitRow[75],vitRow[76],vitRow[77],vitRow[78],vitRow[79],vitRow[80],vitRow[81],vitRow[82],vitRow[83],vitRow[84]))
        templateStr = templateStr.replace("MC_IMMUNIZATION",add_Imm(immRow[1],immRow[2],immRow[3],immRow[4],immRow[5],immRow[6],immRow[7],immRow[8],immRow[9],immRow[10],immRow[11],immRow[12],immRow[13],immRow[14],immRow[15],immRow[16],immRow[17],immRow[18],immRow[19],immRow[20],immRow[21],immRow[22],immRow[23],immRow[24]))


        templateStr = templateStr.replace("MC_CTR",make_CTR(CTRRow[1],CTRRow[2],CTRRow[3],CTRRow[4],CTRRow[5],CTRRow[6],CTRRow[7],CTRRow[8],CTRRow[9],CTRRow[10],CTRRow[11],CTRRow[12],CTRRow[13],CTRRow[14],CTRRow[15],CTRRow[16],CTRRow[17],CTRRow[18],CTRRow[19],CTRRow[20],CTRRow[21],CTRRow[22],CTRRow[23],CTRRow[24],CTRRow[25],CTRRow[26],CTRRow[27],CTRRow[28],CTRRow[29],CTRRow[30],CTRRow[31],CTRRow[32],CTRRow[33],CTRRow[34],CTRRow[35],CTRRow[36],CTRRow[37],CTRRow[38],CTRRow[39],CTRRow[40],CTRRow[41],CTRRow[42],CTRRow[43],CTRRow[44],CTRRow[45],CTRRow[46],CTRRow[47],CTRRow[48],CTRRow[49],CTRRow[50],CTRRow[51],CTRRow[52],CTRRow[53],CTRRow[54],CTRRow[55],CTRRow[56],CTRRow[57],CTRRow[58],CTRRow[59],CTRRow[60],CTRRow[61],CTRRow[62],CTRRow[63],CTRRow[64],CTRRow[65],CTRRow[66],CTRRow[67],CTRRow[68],CTRRow[69],CTRRow[70],CTRRow[71],CTRRow[72],CTRRow[73],CTRRow[74],CTRRow[75],CTRRow[76],CTRRow[77],CTRRow[78],CTRRow[79],CTRRow[80],CTRRow[81],CTRRow[82],CTRRow[83],CTRRow[84],CTRRow[85],CTRRow[86],CTRRow[87],CTRRow[88],CTRRow[89],CTRRow[90],CTRRow[91],CTRRow[92],CTRRow[93],CTRRow[94],CTRRow[95],CTRRow[96],CTRRow[97],CTRRow[98],CTRRow[99],CTRRow[100],CTRRow[101],CTRRow[102],CTRRow[103],CTRRow[104],CTRRow[105],CTRRow[106],CTRRow[107],CTRRow[108],CTRRow[109],CTRRow[110],CTRRow[111],CTRRow[112],CTRRow[113],CTRRow[114],CTRRow[115],CTRRow[116],CTRRow[117],CTRRow[118],CTRRow[119],CTRRow[120],CTRRow[121],CTRRow[122],CTRRow[123],CTRRow[124],CTRRow[125],CTRRow[126],CTRRow[127],CTRRow[128],CTRRow[129],CTRRow[130],CTRRow[131],CTRRow[132],CTRRow[133],CTRRow[134],CTRRow[135],CTRRow[136],CTRRow[137],CTRRow[138],CTRRow[139],CTRRow[140],CTRRow[141],CTRRow[142],CTRRow[143],CTRRow[144],CTRRow[145],CTRRow[146],CTRRow[147],CTRRow[148],CTRRow[149],CTRRow[150],CTRRow[151],CTRRow[152],CTRRow[153],CTRRow[154],CTRRow[155],CTRRow[156],CTRRow[157],CTRRow[158],CTRRow[159],CTRRow[160],CTRRow[161],CTRRow[162],CTRRow[163],CTRRow[164],CTRRow[165],CTRRow[166],CTRRow[167],CTRRow[168],CTRRow[169],CTRRow[170],CTRRow[171],CTRRow[172],CTRRow[173],CTRRow[174],CTRRow[175],CTRRow[176],CTRRow[177],CTRRow[178],CTRRow[179],CTRRow[180],CTRRow[181],CTRRow[182],CTRRow[183]))

        templateStr = templateStr.replace("MC_NOTES",add_Notes(notesRow[1],notesRow[2]))  
        templateStr = templateStr.replace("MC_FOOTER",add_Footer(checkInRow[0],rowNum))  
        print(templateStr)                  # The page

        #with open("output_card.html", "w") as text_file:
        #    text_file.write(templateStr)

    except Exception as e:
        print("Exception: ",e)
        raise

