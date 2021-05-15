##Streamlit app for FSDL course project
#import required libraries
import streamlit as st
from load_css import local_css
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import numpy as np
import requests
import json
import ast
import os

#start page title
st.title('DeepOpinion IPA Demo App')

#login and confirm success
url = "https://api.deepopinion.ai/auth/login"

payload = "{\n\t\"email\": \" \",\n\t\"password\": \" \"\n}"

headers = {
          'Content-Type': 'application/json'
          }

response = requests.request("POST", url, headers=headers, data = payload)

jsn = json.loads(response.text)


st.text(jsn['message'])

st.header('Opinion Mining for Banking!')

x = st.text_area('Enter customer review!')

z = st.button('Hit me for insights')

st.header('Magic Starts Here!')

#side bar
add_selectbox = st.sidebar.header(
    "Upload batch here in csv format [Coming soon!]"
)


f = st.sidebar.file_uploader('File uploader [reviews column title as "text"]')

k = st.sidebar.button('upload file')

if k == True:

	fr = pd.read_csv(f, encoding = 'utf-8-sig')

	st.table(fr)

#analyze text
def analyze(review):
	url = "https://api.deepopinion.ai/organizations/11/analyze"

	payload = json.dumps({
	  "model_id": 255,
	  "documents": [
	    {
	      "text": review
	    }
	  ]
	})
	headers = {
	  'Content-Type': 'application/json',
	  'Authorization': jsn['auth_token']
	}

	response = requests.request("POST", url, headers=headers, data = payload)

	byte_str = response.text.encode("latin_1")
	dict_str = byte_str.decode("latin_1")
	mydata = ast.literal_eval(dict_str)
	de = dict(mydata)

	return de

def highlight(df):

	lst = []

	lst.append("<div>")

	for i in range(len(df['text'])):
		

		if df['label'].iloc[i] == 'POS':

			lst.append("<span class='highlight green'>"+df['text'].iloc[i]+ "</span>")

		else:

			lst.append("<span class='highlight red'>"+df['text'].iloc[i]+ "</span>")

	lst.append("</dev>")

	x = ' '.join(lst)

	return st.markdown(x, unsafe_allow_html=True) 

#Analysis process
if z == True:

	st.text('There are ' + str(len(x.split())) + ' words in this input!')

	de = analyze(x)

	local_css("style.css")

	table = []
	for ix, sent_de in enumerate(de['documents']):
	    for i, seg in enumerate(sent_de['segments']):
	        table.append(seg)

	df = pd.DataFrame(table)
	df['class'] = None
	df['label'] = None
	for i, tag in enumerate(df['tags']):
	    if len(tag) > 0:
	        df['class'].iloc[i] = tag[0]['class']
	        df['label'].iloc[i] = tag[0]['label']

	highlight(df)
	#t = "<div><span class='highlight red'>"+df['text'].iloc[0]+ "</span>"

	#st.markdown(t, unsafe_allow_html=True)

	#z = "<span class='highlight red'>"+df['text'].iloc[1]+ "</span></div>"

	#st.markdown(t + z, unsafe_allow_html=True)

	st.text(' ')

	st.text(df['class'].value_counts())

	st.bar_chart(df['class'].value_counts())

	chart = pd.DataFrame(df['label'].value_counts()).reset_index()

	fig = px.pie(chart, values = 'label', names = 'index', color_discrete_sequence=px.colors.sequential.RdBu,
                 title="Sentiment Distribution")

	st.plotly_chart(fig)

	st.header('Negative Ticket Routing')

	d = {'Customer Service' : ['Expertise', 'Customer Service', 'E-mail service', 'Phone service', 'Branch Service', 'Routing', 'Processing Time'],
	     'Product' : ['Mobile App', 'Credit Card', 'Ease of use', 'Response behaviour', 'Website UX'],
	     'General' : ['Satisfaction', 'Friendliness', 'Brand perception', 'Recommendation', 'Value for money', 'Helpfulness', 'Fees']}

	Customer = df[df['class'].isin(d['Customer Service'])]
	General = Customer[['text', 'class', 'label']]
	Customer = Customer[Customer['label'] == 'NEG']

	st.subheader('Customer Service Tickets')
	st.table(Customer[['text', 'class', 'label']])

	General = df[df['class'].isin(d['General'])]
	General = General[['text', 'class', 'label']]
	General = General[General['label'] == 'NEG']

	st.subheader('General Tickets')
	st.table(General[['text', 'class', 'label']])


