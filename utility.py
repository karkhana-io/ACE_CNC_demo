import requests
import streamlit as st
import json

class CostSummaryDisplay:
    def __init__(self, data):
        self.data = data
    
    def format_key(self, key):
        
        return key.replace("_", " ").title()
    
    def generate_bullet_points(self):
        hide_cost = ['scrap_savings']
        return "\n".join(f"* {self.format_key(key)}:\t\t{value}" for key, value in self.data.items() if key not in hide_cost)
    
    def display(self):

        st.info('Here is the costing for the Uploaded CAD file:')
        st.markdown(self.generate_bullet_points())



def get_possible_operations(operations):

    possible_operations = {key: value for key, value in operations.items() if value == 1}

    possible_opp = {key.replace("_", " ").title(): value for key, value in possible_operations.items()}
    
    st.info("Outlined below are the essential machining operations required to process the CAD.", icon="ℹ️")
    # Create a Markdown string with bullet points
    bullet_points = "\n".join(f"* {operation}" for operation in possible_opp)
    
    # Display the operations as bullet points
    st.markdown(bullet_points)


def get_cad_feature_extracted(url, file_path, operation='milling'):
    
    payload = {'operation': operation}
    files = [
        ('cad_file', (file_path.split("\\")[-1], open(file_path, 'rb'), 'application/octet-stream'))
    ]
    headers = {}

    response = requests.post(url, headers=headers, data=payload, files=files)

    return response

def get_global_service_data(url):
  
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()

    surface_finish = {}
    for item in data['data']:
        surface_finish[item['name']] = item['id']

    return surface_finish

def get_cnc_costing(costing_url, data):
    
    payload = json.dumps(data)
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(costing_url, headers=headers, data=payload)
    return response
