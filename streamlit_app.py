
import streamlit as st
import pandas as pd
import yaml
import pandas as pd
import numpy as np
import os
from pprint import pprint
from bs4 import BeautifulSoup as soup

def prettify_raw_html(html_string, engine='bs4'):
    if engine == 'bs4':
        return soup(html_string, features='html.parser').prettify()

def generate_html_for_field(field):
    field_type = field.pop('field_type')
    col_size_modifier = 'col-md-6' if field.get('group_id') else ''
    if field_type == 'input':    
        input_field_template = \
        """<div class="{col_size_modifier} mb-3">
            <label for="{backend_field_name}" class="form-label">{field_label}</label>
            <input type="text" class="form-control" id="{backend_field_name}" name="{backend_field_name}" >
        </div>"""
        return input_field_template.format(**{'col_size_modifier': col_size_modifier, **field})
    elif field_type == 'select':
        option_list = '\n'.join([f"<option value=\"{option.strip()}\">{option.strip()}</option>" for option in field['select_options'].split(',')])
        select_field_template = \
        """<div class="{col_size_modifier} mb-3">
            <label for="{backend_field_name}" class="form-label">{field_label}</label>
            <select class="form-select" id="{backend_field_name}" name="{backend_field_name}" >
                {option_list}
            </select>
        </div>"""
        return select_field_template.format(**{
            'col_size_modifier': col_size_modifier,
            'option_list': option_list,
            **field}
        )
    elif field_type == 'text':
        text_field_template = \
        """<div class="{col_size_modifier} mb-3">
            <label for="{backend_field_name}" class="form-label">{field_label}</label>
            <input type="text" class="form-control" id="{backend_field_name}" name="{backend_field_name}" >
        </div>"""
        return text_field_template.format(**{'col_size_modifier': col_size_modifier, **field})
    else:
        print(f"Unknown field type '{field_type}' for field '{field['backend_field_name']}'")
        return ''

def generate_html_for_page(page_number, page_config, field_html):
    page_template = \
    """<div class="form-page" id="page{page_number}">
            <h4 class="mt-4" aria-level="2">{page_title}</h4>
            <p class="text-muted">{page_description}</p>
            {field_html}
       </div>"""
    return page_template.format(**{
        'page_number': page_number,
        'field_html': field_html,
        **page_config
        }
    )

def generate_html_for_input_group_start():
    return "<div class=\"row\">"

def generate_html_for_input_group_end():
    return "</div>"

def generate_form_html_from_config_file(config_file_path):
    config_workbook = pd.ExcelFile(config_file_path)
    form_pages = pd.read_excel(config_workbook, 'Pages').set_index('page_number').to_dict(orient='index')
    form_fields = pd.read_excel(config_workbook, 'Fields')
    generated_form_html = """"""
    for page_number, page_config in form_pages.items():
        # Step 1: Generate HTML for fields inside the page
        generated_field_html = """"""
        # Select subset of data that is associated with the current page, clean up missing group_id values and build a dictionary
        page_fields = form_fields.loc[form_fields['page_number'] == page_number].replace({np.nan:None}).to_dict(orient='records')
        current_group_id = None
        for i, field in enumerate(page_fields):
            if not field['group_id']:
                generated_field_html += generate_html_for_field(field)
            else:
                if current_group_id is None:
                    # First group on the page, so don't end any previous group
                    generated_field_html += generate_html_for_input_group_start()
                elif field['group_id'] != current_group_id:
                    # Non-first group on the page, so end the previous group and start a new one
                    generated_field_html += generate_html_for_input_group_end()
                    generated_field_html += generate_html_for_input_group_start()
                generated_field_html += generate_html_for_field(field)
                current_group_id = field['group_id']
        if current_group_id:
            # If at least 1 group has been created, the last group will need to be closed.
            generated_field_html += generate_html_for_input_group_end()
        # Step 2: Generate HTML for the page using the generated field HTML and page_config information
        generated_page_html = generate_html_for_page(page_number, page_config, generated_field_html)
        # Step 3: Append the generated page HTML to the final form HTML
        generated_form_html += generated_page_html
    # Step 4: Prettify and return the final form content HTML (pages and fields only)
    return prettify_raw_html(generated_form_html)

def generate_config_file_from_raw_data(raw_data):
    config_file_path = "config.xlsx" # This needs to be dynamic
    # OpenAI-based config file generator: raw data -> config file
    prompt = """
    You are a helpful data analyst creating configuration files for large excel-based datasets. A configuration file is another excel file that
    has a header row with the following columns: 'backend_field_name', 'field_label', 'required?', 'field_type', 'select_options'. Then, a new row 
    is generated for for each column in the dataset. The columns in the configuration file are populated as follows:
    1. 'backend_field_name' should be derived from the column name in the dataset, but values should be lowercase and underscore-separated 
    2. 'field_label' should be derived from the column name in the dataset, but values should be HTML-safe and easy to read. They should not be underscore-separated.
    3. 'required' should be marked True only if the dataset contains values for all rows of that column. 
    4. 'field_type' should be an HTML element type such as input, text. select etc. If a column in the dataset only contains a few unique values and looks like it would be a dropdown
    element on a web form, ensure the field_type is 'select'.
    5. 'select_options' should be filled in only when the 'field_type' is 'select'. All unique values for the column in the dataset should be populated here in this case.
    """
    return config_file_path

def generate_html(config_file_path):
    # Process the uploaded file and generate HTML
    html_content = generate_form_html_from_config_file()
    with open(html_file_path, "w") as f:
        f.write(html_content)
    return html_file_path


########### Streamlit App ###########

st.title("UB RA Dynamic Form Generator")

# File upload
uploaded_file = st.file_uploader("To begin, upload an Excel dataset.", type=["xlsx"])

if uploaded_file:
    st.success("File uploaded successfully!")
    
    # Button to generate configuration file
    if st.button("Generate Configuration File"):
        config_file_path = generate_config_file_from_raw_data(uploaded_file)
        st.success(f"Configuration file generated: {config_file_path}")
        st.download_button("Download Configuration File", 
                           data=open(config_file_path, "rb").read(), 
                           file_name="form_configuration.xlsx")

    # Button to generate HTML
    if st.button("Generate HTML"):
        config_file_path = generate_config_file_from_raw_data(uploaded_file)
        html_file_path = generate_html(config_file_path)
        st.success(f"HTML file generated: {html_file_path}")
        st.download_button("Download HTML File", 
                           data=open(html_file_path, "rb").read(), 
                           file_name="form_content.html")
else:
    st.info("Please upload an Excel file to get started.")
