#!/usr/bin/python3

import csv
import cgi
import codecs
import time
import os
import urllib.request

# CSV Mappings
###############

TEMPLATE_FILE="card.template.html"

CHECK_IN_CSV_URL="https://docs.google.com/spreadsheets/d/e/2PACX-1vTdGrYYysLlD4lLaIUhhroiw4kDtNWjbpiF5NximTtBK6OAq8OJYJ5ulcPks0_BWDo9PZw7aFc9-37s/pub?gid=535824425&single=true&output=csv&range="
CHECK_IN_END_COL='D'
CHECK_IN_COL_CNT=4

IMM_CSV_URL="https://docs.google.com/spreadsheets/d/e/2PACX-1vTdGrYYysLlD4lLaIUhhroiw4kDtNWjbpiF5NximTtBK6OAq8OJYJ5ulcPks0_BWDo9PZw7aFc9-37s/pub?gid=1308664369&single=true&output=csv&range="
IMM_END_COL='Y'
IMM_COL_CNT=25

TESTING_CSV_URL="https://docs.google.com/spreadsheets/d/e/2PACX-1vTdGrYYysLlD4lLaIUhhroiw4kDtNWjbpiF5NximTtBK6OAq8OJYJ5ulcPks0_BWDo9PZw7aFc9-37s/pub?gid=761782776&single=true&output=csv&range="
TESTING_END_COL='I'
TESTING_COL_CNT=9

TREATMENT_CSV_URL="https://docs.google.com/spreadsheets/d/e/2PACX-1vTdGrYYysLlD4lLaIUhhroiw4kDtNWjbpiF5NximTtBK6OAq8OJYJ5ulcPks0_BWDo9PZw7aFc9-37s/pub?gid=180959187&single=true&output=csv&range="
TREATMENT_END_COL='I'
TREATMENT_COL_CNT=9

NOTES_CSV_URL="https://docs.google.com/spreadsheets/d/e/2PACX-1vTdGrYYysLlD4lLaIUhhroiw4kDtNWjbpiF5NximTtBK6OAq8OJYJ5ulcPks0_BWDo9PZw7aFc9-37s/pub?gid=99678788&single=true&output=csv&range="
NOTES_END_COL='B'
NOTES_COL_CNT=2

PAS_URL="https://ee.humanitarianresponse.info/x/I3AzTNsn"
IMM_REF_URL="http://www.vacfa.uct.ac.za/sites/default/files/image_tool/images/210/Immunization_Schedules/Ghana.pdf"

cur = time.time()
os.environ["TZ"] = "GMT"
time.tzset()

def add_Footer(patientNum, row):
    return "Data from row (<b>" + row + "</b>) in the Google Spreadsheet as of : <b>" + time.strftime("%T %Z", time.localtime(cur)) + "</b><br><hr><p>Please remember to take the Patient Action Survey (PAS) for this patient, linked <a href='" + PAS_URL + '/?&d[Patient_Number]=' + patientNum + "' target='_blank'>here</a>.\n"

def add_Imm(BGC1,OPV1,OPV2,OPV3,OPV4,R1,R2,Hep1,Hep2,Hep3,Pn1,Pn2,Pn3,IPV1,YF1,MR1,MR2,M1,MenA1,Td1,Td2,Td3,Td4,COVID1):
    out = "BGC = " + BGC1 + "<br>\n"
    out = out + "OPV = " + OPV1 + ", " + OPV2 + ", " + OPV3 + ", " + OPV4 + "<br>\n"
    out = out + "Rotavirus = " + R1 + ", " + R2 + "<br>\n"
    out = out + "DTwPHibHepB = " + Hep1 + ", " + Hep2 + ", " + Hep3 + "<br>\n"
    out = out + "Pneumo_conj = " + Pn1 + ", " + Pn2 + ", " + Pn3 + "<br>\n"
    out = out + "IPV (from Sept-2017) = " + IPV1 + "<br>\n"
    out = out + "YF = " + YF1 + "<br>\n"
    out = out + "MR = " + MR1 + ", " + MR2 + "<br>\n"
    out = out + "Measles = " + M1 + "<br>\n"
    out = out + "MenA = " + MenA1 + "<br>\n"
    out = out + "Td = " + Td1 + ", " + Td2 + ", " + Td3 + ", " + Td4 + "<br>\n"
    out = out + "COVID19 = " + COVID1 + "<br>\n"    
    out = out + "<p><i><a href='" + IMM_REF_URL + "' target='_blank'>National  Immunization Schedule - Ghana</a></i><br>\n"    
    return str(out)

def add_Testing(Eyes,Hearing,Mouth,Skin,Hepatitis,HIV,Malaria,STDS):
    out = "Eyes = " + Eyes + "<br>\n"
    out = out + "Hearing = " + Hearing + "<br>\n"
    out = out + "Mouth = " + Mouth + "<br>\n"
    out = out + "Skin = " + Skin + "<br>\n"
    out = out + "Hepatitis = " + Hepatitis + "<br>\n"
    out = out + "HIV = " + HIV + "<br>\n"
    out = out + "Malaria = " + Malaria + "<br>\n"        
    out = out + "STDs = " + STDS + "<br>\n"            
    return str(out)

def add_Treatment(Mstart,Mlast,Mcnt,Hstart,Hlast,Hcnt,Wlast,Tnotes):
    out = "Malaria Started = " + Mstart + "<br>\n" 
    out = out + "Malaria Last = " + Mlast + "<br>\n"
    out = out + "Malaria Treatment Count = " + Mcnt + "<br><hr>\n"
    out = out + "HIV Started = " + Hstart + "<br>\n" 
    out = out + "HIV Last = " + Hlast + "<br>\n"
    out = out + "HIV Treatment Count = " + Hcnt + "<br><hr>\n"
    out = out + "Wound Last = " + Wlast + "<br>\n"
    out = out + "Treatment Notes = " + Tnotes + "<br>\n"                        
    return str(out)    

def add_Notes(notes):
    out = "General Notes = " + notes + "<br><hr>\n"
    return str(out)        

def get_Row(url,rowNum,endCol,colCnt):
    fullUrl = url + "A" + rowNum + ":" + endCol + rowNum
    response = urllib.request.urlopen(fullUrl)
    text = response.read().decode('utf-8')
    row = text.split(",")
    # print(str(row))    
    if (len(row) != colCnt):
        print("<H1>GiveDirect Error</H1>")
        print("Valid record not found in Google Sheet at row (" + row + "), try a different row...")
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

        templateStr=codecs.open(TEMPLATE_FILE, 'r').read()
        
        # csvFile = open("data.csv")
        # csvFile = open("sample.csv")        
        # readCSV = csv.reader(csvFile)
        
        # readCSV = csv.reader(text)
        # for row in readCSV:
        
        checkInRow = get_Row(CHECK_IN_CSV_URL,rowNum,CHECK_IN_END_COL, CHECK_IN_COL_CNT)
        immRow = get_Row(IMM_CSV_URL,rowNum,IMM_END_COL,IMM_COL_CNT)
        testingRow = get_Row(TESTING_CSV_URL,rowNum,TESTING_END_COL,TESTING_COL_CNT)
        treatmentRow = get_Row(TREATMENT_CSV_URL,rowNum,TREATMENT_END_COL,TREATMENT_COL_CNT)
        notesRow = get_Row(NOTES_CSV_URL,rowNum,NOTES_END_COL,NOTES_COL_CNT)
        
        templateStr = templateStr.replace("MC_PATIENT_NUM",checkInRow[0])

        templateStr = templateStr.replace("MC_PATIENT_PHONE",checkInRow[3])
        templateStr = templateStr.replace("MC_IMMUNIZATION",add_Imm(immRow[1],immRow[2],immRow[3],immRow[4],immRow[5],immRow[6],immRow[7],immRow[8],immRow[9],immRow[10],immRow[11],immRow[12],immRow[13],immRow[14],immRow[15],immRow[16],immRow[17],immRow[18],immRow[19],immRow[20],immRow[21],immRow[22],immRow[23],immRow[24]))
        templateStr = templateStr.replace("MC_TESTING",add_Testing(testingRow[1],testingRow[2],testingRow[3],testingRow[4],testingRow[5],testingRow[6],testingRow[7],testingRow[8]))
        templateStr = templateStr.replace("MC_TREATMENT",add_Treatment(treatmentRow[1],treatmentRow[2],treatmentRow[3],treatmentRow[4],treatmentRow[5],treatmentRow[6],treatmentRow[7],treatmentRow[8]))  
        templateStr = templateStr.replace("MC_NOTES",add_Notes(notesRow[1]))  
        templateStr = templateStr.replace("MC_FOOTER",add_Footer(checkInRow[0],rowNum))  
        print(templateStr)                  # The page

        #with open("output_card.html", "w") as text_file:
        #    text_file.write(templateStr)

    except Exception as e:
        print("Exception: ",e)
        raise

