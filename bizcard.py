pip install easyocr

pip install opencv-python

pip install streamlit


 %%writefile Bizcard.py
 import streamlit as st
 import easyocr
 import cv2
 import numpy as np
 import pandas as pd
 from google.colab import files
 import regex as re
 import sqlite3
 
 def imageSelect():
   c1,c2 = st.columns([3,2])
   with c1:
     uploaded_file = st.file_uploader("Choose a Image", accept_multiple_files=False)
     if uploaded_file is not None:
       language = easyocr.Reader(['en'])
       img = cv2.imdecode(np.fromstring(uploaded_file.read(),np.uint8),1)
       image = language.readtext(img,decoder ='wordbeamsearch',detail = 0)
 
       name = image[0]
       designation = image[1]
       image.remove(name)
       image.remove(designation)
       if 'St ,' in image:
         image.remove('St ,')
         image.remove('Erode,')
         image.remove("global.com")
         image[image.index("WWW")] = "WWW.global.com"
         image[image.index("123 global")]="123 global st, Erode "
 
       number,email,website,address,company_name  = [],[],[],[],""
 
       for i in image:
         mail = re.search("^[a-z,A-z].*[@].*[cC][oO][mM]",i)
         phoneNo = re.search(".*[0-9,-]{11}.*",i)
         websiteadd = re.search("^[wW][wW][wW].*",i)
         add= re.search("^[0-9][0-9][0-9][ ].+",i)
         add1 = re.search(".*[0-9]{6}.*",i)
 
         if phoneNo is not None:
           number.append(phoneNo.group())
         if mail is not None:
           email.append(mail.group())
         if websiteadd is not None:
           website.append(websiteadd.group())
         if add is not None:
           address.append(add.group())
         if add1 is not None:
           address.append(add1.group())
 
       for i in number:
         image.remove(i)
       for i in email:
         image.remove(i)
       for i in website:
         image.remove(i)
       for i in address:
         try:
           image.remove(i)
         except:
           address.pop()
       try:
         mob_number = str(number[0])+ ", " +str(number[1])
       except:
         mob_number = str(number[0])
 
       address = address[0]+address[1]
       for i in image:
         company_name = company_name + i +" "
 
       result = (name,designation,mob_number,email[0],website[0],address,company_name)
       st.success("Text Extracted and file is getting uploaded to database")
       con = sqlite3.connect("bizcard.db")
       cur = con.cursor()
       cur.execute("""CREATE TABLE if not exists cardetails
                   (Name varchar,
                   Designation varchar,
                   phone_no varchar,
                   email_id varchar unique,
                   website varchar,
                   address varchar,
                   company_name varchar,
                   card_image BLOB)""")
       con.commit()
       try:
         cur.execute(f"insert into cardetails values (?,?,?,?,?,?,?,?)",(result[0],result[1],result[2],result[3],result[4],result[5],result[6],sqlite3.Binary(img)))
         con.commit()
         st.success("Data Uploaded successfully")
       except:
         st.success("Data already exists")
       con.close()
       st.image(img, channels="BGR")
     with c2:
       try:
         with st.container():
               st.text_input('Name of the card holder', result[0])
               st.text_input('Company Name', result[6])
               st.text_input('Designation', result[1])
               st.text_input('Contact Number', result[2])
               st.text_input('Email ID', result[3])
               st.text_input('Address', result[5])
               st.text_input('Website Details', result[4])
       except:
         pass
 
 def display_():
   try:
     con = sqlite3.connect("bizcard.db")
     cur = con.cursor()
     a = cur.execute("select Name,Designation,phone_no,email_id,website,address,company_name from cardetails")
     table = a.fetchall()
     column_names = ["Name", "Designation", "Contact", "Email ID", "Website", "Address", "Company Name"]
     df = pd.DataFrame(table, columns=column_names)
     st.dataframe(df)
     con.close()
   except:
     pass
 
 def remove_():
   try:
     options =[]
     con = sqlite3.connect("bizcard.db")
     cur = con.cursor()
     a = cur.execute("select * from cardetails")
     df =pd.DataFrame(a.fetchall())
     for i in df.itertuples():
       options.append(i[1:8])
     result = st.selectbox("Select the card to modify/delete",options)
     with st.container():
       c1,c2 = st.columns(2)
       with c1:
           with st.container():
                 a = st.text_input('Name of the card holder', result[0])
                 c = st.text_input('Designation', result[1])
                 d = st.text_input('Contact Number', result[2])
                 e = st.text_input('Email ID', result[3])
                 g = st.text_input('Website Details', result[4])
                 f = st.text_input('Address', result[5])
                 b = st.text_input('Company Name', result[6])
 
       with c2:
         if st.button("Update the details in database"):
             cur.execute("update cardetails set Name = ?,Designation = ?,phone_no = ?,email_id = ?,website = ?,address = ?,company_name = ?where Name = ? and email_id = ?",(a,c,d,e,g,f,b,result[0],result[3]))
             con.commit()
             st.success("Database updated successfully")
 
         if st.button("Delete the details in database"):
             cur.execute("delete from cardetails where email_id = ?",(result[3],))
             con.commit()
             st.success("Details deleted successfully")
     con.close()
   except:
    pass
 
 st.set_page_config(page_title="BizCardX", page_icon=None, layout="centered")
 
 with st.container():
         html = "<p style='color:00f900; font-size:250%; text-align:left'><b>BizCardX: Automating Business Card Data Extraction</b></p>"
         st.markdown(html, unsafe_allow_html=True)
 
         html = "<p style='color:0034F9; font-size:100%; text-align:left'><b>BizCardX: Automating Business Card Data Extraction revolutionizes contact management by utilizing advanced OCR technology to swiftly convert paper business cards into digital, organized contacts, saving time and reducing errors.</b></p>"
         st.markdown(html, unsafe_allow_html=True)
 
 tab1, tab2, tab3, tab5 = st.tabs(["Home", "Upload-Extract-Load", "Display","Modify / Delete"])
 with tab1:
     with st.container():
         html = "<p style='color:8300F9; font-size:100%; text-align:left'><b>In the era of digital networking, the exchange of business cards remains a ubiquitous practice, but manually transcribing the information they contain is a tedious and error-prone task. To address this challenge, we present a cutting-edge solution: a Streamlit application that harnesses Optical Character Recognition (OCR) technology to seamlessly extract key information from business card images.</b></p>"
         st.markdown(html, unsafe_allow_html=True)
 
         html = "<p style='color:F900C0; font-size:100%; text-align:left'><b>The core technologies used include Python, Streamlit, easyOCR, and a database management system. Skills in image processing, OCR, GUI development, and database management are paramount for this project. Meticulous planning and thoughtful architecture ensure scalability, maintainability, and extensibility.</b></p>"
         st.markdown(html, unsafe_allow_html=True)
 
 with tab2:
     with st.container():
           image = imageSelect()
 
 with tab3:
     with st.container():
             display_()
 with tab5:
     with st.container():
             remove_()

!npm install localtunnel

import requests

response = requests.get("https://ipv4.icanhazip.com")
if response.status_code == 200:
    ip_address = response.text.strip()
    print("Your external IP address is:", ip_address)
else:
    print("Failed to retrieve the IP address.")

!streamlit run Bizcard.py &>/content/logs.txt & npx localtunnel --port 8501

