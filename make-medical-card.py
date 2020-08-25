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
URL="https://docs.google.com/spreadsheets/d/e/2PACX-1vSNoRNS2u26sPvQKgcMtYJy86iKO0yBmRvEMKq4E9hkLqDba0zJSAZb37bgYYZUc37-NrUbz9xoT13-/pub?gid=0&single=true&output=csv&range="

cur = time.time()
os.environ["TZ"] = "GMT"
time.tzset()

def add_Footer(row):
    return "Data from row (<b>" + row + "</b>) in the Google Spreadsheet as of : <b>" + time.strftime("%T %Z", time.localtime(cur)) + "</b><br><hr>\n"

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
    return str(out)

def add_Testing(Eyes,Hearing,Mouth,Hepatitis,HIV,Malaria,STDS):
    out = "Eyes = " + Eyes + "<br>\n"
    out = out + "Hearing = " + Hearing + "<br>\n"
    out = out + "Mouth = " + Mouth + "<br>\n"
    out = out + "Hepatitis = " + Hepatitis + "<br>\n"
    out = out + "HIV = " + HIV + "<br>\n"
    out = out + "Malaria = " + Malaria + "<br>\n"        
    out = out + "STDs = " + STDS + "<br>\n"            
    return str(out)

def add_Treatment(Mstart,Mlast,Mcnt,Hstart,Hlast,Hcnt,Wlast,Wnotes):
    out = "Malaria Started = " + Mstart + "<br>\n" 
    out = out + "Malaria Last = " + Mlast + "<br>\n"
    out = out + "Malaria Treatment Count = " + Mcnt + "<br><hr>\n"
    out = out + "HIV Started = " + Hstart + "<br>\n" 
    out = out + "HIV Last = " + Hlast + "<br>\n"
    out = out + "HIV Treatment Count = " + Hcnt + "<br><hr>\n"
    out = out + "Wound Last = " + Wlast + "<br>\n"
    out = out + "Wound Notes = " + Wnotes + "<br>\n"                        
    return str(out)    

def add_Notes(notes):
    out = "General Notes = " + notes + "<br><hr>\n"
    return str(out)        

if __name__ == "__main__":
    try:
        print("Content-Type: text/html")    # HTML is following
        print()                             # blank line, end of headers
        form = cgi.FieldStorage()
        if "row" not in form:
           print("<H1>GiveDirect Error</H1>")
           print("<h3>You must send a 'row' as a GET argument.</h3><br><hr>")

        rowNum = form["row"].value
        response = urllib.request.urlopen(URL + "A" + rowNum + ":AQ" + rowNum)
        text = response.read().decode('utf-8')
        row = text.split(",")

        templateStr=codecs.open(TEMPLATE_FILE, 'r').read()
        
        # csvFile = open("data.csv")
        # csvFile = open("sample.csv")        
        # readCSV = csv.reader(csvFile)
        
        # readCSV = csv.reader(text)
        # for row in readCSV:
        templateStr = templateStr.replace("MC_PATIENT_NUM",row[0])

        if (len(row) == 43):
            templateStr = templateStr.replace("MC_PATIENT_PHONE",row[2])
            templateStr = templateStr.replace("MC_IMMUNIZATION",add_Imm(row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13],row[14],row[15],row[16],row[17],row[18],row[19],row[20],row[21],row[22],row[23],row[24],row[25],row[26]))
            templateStr = templateStr.replace("MC_TESTING",add_Testing(row[27],row[28],row[29],row[30],row[31],row[32],row[33]))
            templateStr = templateStr.replace("MC_TREATMENT",add_Treatment(row[34],row[35],row[36],row[37],row[38],row[39],row[40],row[41]))  
            templateStr = templateStr.replace("MC_NOTES",add_Notes(row[42]))  
            templateStr = templateStr.replace("MC_FOOTER",add_Footer(rowNum))  
            print(templateStr)                  # The page
        else:
            print("<H1>GiveDirect Error</H1>")
            print("Record not found in Google Sheet, try sharing a different row...")
        
        #with open("output_card.html", "w") as text_file:
        #    text_file.write(templateStr)

    except Exception as e:
        print("Exception: ",e)
        raise

