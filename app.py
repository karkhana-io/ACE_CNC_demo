import streamlit as st
from utility import *



def main():
    cad_extractor_url = st.secrets["cad_extractor"]["cad_extractor_url"]
    costing_url = st.secrets["costing"]["costing_url"]
    surface_finish_url = st.secrets["surface_finish"]["surface_finish_url"]
    material_grade_url = st.secrets["material_grade"]["material_grade_url"]
    tolerance_url = st.secrets["tolerance"]["tolerance_url"]
    st.title("Karkhana.io ACE CNC Demo!!")
    surface_finish = get_global_service_data(surface_finish_url)
    material_grade = get_global_service_data(material_grade_url)
    tolerance = get_global_service_data(tolerance_url)

    # File upload
    uploaded_file = st.file_uploader("Upload a .step or .stp file", type=['step', 'stp'], accept_multiple_files=False)
    # Check file size (max 8 MB)
    if uploaded_file is not None:
        if uploaded_file.size > 100 * 1024 * 1024:
            st.error("File size exceeds 8 MB. Please upload a smaller file.")
            return
    # Process the inputs (add your own logic here)
    if uploaded_file is not None:
        
        file_content = uploaded_file.getvalue()

        # Prepare the file in the correct format for uploading
        file_path = {'file': (uploaded_file.name, file_content)}

        response = get_cad_feature_extracted(cad_extractor_url, file_path)
        
        indicator = False
        if response.status_code == 200:
            response = response.json()
            if response['status'] == 'green':
                st.info("Outlined below are the extracted feature of the CAD.", icon="ℹ️")
                for item_feat in response['data']:
                    st.dataframe(item_feat['features'])
                    indicator = True
            elif response['status'] == 'red':
                st.write(response)
        elif response.status_code != 200:
            st.info(f"CAD Extrcator API Response: {response.status_code}", icon="ℹ️")

        if indicator and len(response['data'])==1:
            # Create two columns for the inputs
            col1, col2 = st.columns(2)

            with col1:
                material_grade_input = st.selectbox("Material Grade", options=material_grade.keys())
                surface_finish_input = st.selectbox("Surface Finish", options=surface_finish.keys())
                
            with col2:
                quantity = st.number_input("Quantity", value=1, min_value=1)
                tolerance = st.selectbox("Tolerance", options=tolerance.keys(), index=0)

            tolerance_options = {"ISO 2768 - Medium": 1, "ISO 2768 - Fine": 0}
            user_input = {
                        'tolarance' : tolerance_options[tolerance] ,
                        'quantity' : quantity,
                        'surface_finish' : surface_finish[surface_finish_input],
                        'material_grade': material_grade[material_grade_input]
                    }

            if st.button("Get the Instant Quote"):
                
                ml_input ={
                            "user_input" : user_input,
                            "cad_data": response['data'] 
                        }

                costing_response = get_cnc_costing(costing_url, ml_input)
                out_put = costing_response.json()['data']
                # st.write(out_put["costing_results"])
                CostSummaryDisplay(out_put["costing_results"]).display()
                get_possible_operations(out_put["ml_output"]["operations"])

        elif indicator and len(response['data'])>1:
            st.info("The CAD file you provided is Assembly file", icon="ℹ️")
        

if __name__ == "__main__":
    main()
