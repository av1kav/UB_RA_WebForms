
import streamlit as st
import pandas as pd

def generate_configuration(uploaded_file):
    # Process the uploaded file and generate a configuration file
    df = pd.read_excel(uploaded_file)
    config_file_path = "form_configuration.xlsx"
    config = df.copy()  # Replace this with actual configuration logic
    config.to_excel(config_file_path, index=False)
    return config_file_path

def generate_html(uploaded_file):
    # Process the uploaded file and generate HTML
    df = pd.read_excel(uploaded_file)
    html_file_path = "form.html"
    html_content = "<!DOCTYPE html>\n<html>\n<head>\n<title>Form</title>\n</head>\n<body>\n"
    
    for _, row in df.iterrows():
        html_content += f"<label>{row['field_label']}</label>\n"
        html_content += f"<input type='{row['field_type']}' name='{row['backend_field_name']}' required='{row['required?']}' />\n<br>\n"
    
    html_content += "</body>\n</html>"
    with open(html_file_path, "w") as f:
        f.write(html_content)
    return html_file_path

# Streamlit app starts here
st.title("Dynamic Form Generator")

# File upload
uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx"])

if uploaded_file:
    st.success("File uploaded successfully!")
    
    # Button to generate configuration file
    if st.button("Generate Configuration File"):
        config_file_path = generate_configuration(uploaded_file)
        st.success(f"Configuration file generated: {config_file_path}")
        st.download_button("Download Configuration File", 
                           data=open(config_file_path, "rb").read(), 
                           file_name="form_configuration.xlsx")

    # Button to generate HTML
    if st.button("Generate HTML"):
        html_file_path = generate_html(uploaded_file)
        st.success(f"HTML file generated: {html_file_path}")
        st.download_button("Download HTML File", 
                           data=open(html_file_path, "rb").read(), 
                           file_name="form.html")
else:
    st.info("Please upload an Excel file to get started.")
