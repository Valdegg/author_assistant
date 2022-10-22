
import streamlit as st
import json

with open('vatnið_brennur_samheiti_nyjast.json', encoding='utf-8') as f2:
    vatnsam = json.load(f2)
with open('vatnið_brennur_orðtíðni_2.json', encoding='utf-8') as f2:
    vatnord = json.load(f2)

#displaying JSON content

st.json(vatnsam)

st.json(vatnord)
