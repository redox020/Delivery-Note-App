import streamlit as st
from fpdf import FPDF
import datetime

st.title("PDH & NAS Enterprise - Delivery Note Generator")

# Top section for general info
col1, col2 = st.columns(2)
with col1:
    date_input = st.date_input("Date", datetime.date.today())
    running_no = st.number_input("Running Number (e.g., 1 for 01)", min_value=1, value=1)
with col2:
    premise = st.text_input("Delivery Premise", "CASH (M) HORSE SDN BHD")

st.markdown("---")
st.subheader("Driver Details")

# Let the user choose how many drivers they need
num_drivers = st.number_input("Number of Drivers", min_value=1, max_value=10, value=1, step=1)

drivers = []
lorries = []

# Loop to create dynamic input fields for the chosen number of drivers
for i in range(num_drivers):
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        # Default first row to something, leave others blank
        default_driver = "ALI BIN ABU" if i == 0 else ""
        d_name = st.text_input(f"Driver Name {i+1}", default_driver, key=f"d_name_{i}")
        drivers.append(d_name)
    with d_col2:
        default_lorry = "ABC123" if i == 0 else ""
        l_no = st.text_input(f"Lorry Number {i+1}", default_lorry, key=f"l_no_{i}")
        lorries.append(l_no)

st.markdown("---")

if st.button("Generate PDF"):
    dn_number = f"DN/PDH&NAS/{running_no:02d}/2026"
    formatted_date = date_input.strftime("%d %b %Y")

    pdf = FPDF()
    pdf.add_page()

    # Reduced top margin to 15.0 to push content higher
    pdf.set_margins(left=25.4, top=15.0, right=25.4)

    # Centered and Bold Header
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, txt="PDH & NAS ENTERPRISE", ln=True, align='C')
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 6, txt="LOT 5, BLOK R, TINGKAT BAWAH BANDAR RAMAI-RAMAI", ln=True, align='C')
    pdf.cell(0, 6, txt="JALAN LEILA 90000 SANDAKAN SABAH", ln=True, align='C')
    
    # Add a small gap, draw the horizontal line, and add another gap
    pdf.ln(2)
    current_y = pdf.get_y()
    pdf.line(25.4, current_y, 210 - 25.4, current_y)
    pdf.ln(2)

    # Right-aligned Reference and Date
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 6, txt=f"Ref.No. {dn_number}", ln=True, align='R')
    pdf.cell(0, 6, txt=f"Date : {formatted_date}", ln=True, align='R')
    pdf.ln(5)

    # MANAGER and SECURITY UNIT in bold
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 5, txt="MANAGER", ln=True, align='L')
    pdf.cell(0, 5, txt="SECURITY UNIT", ln=True, align='L')
    
    # Standard text for address
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 5, txt="PEMBANGUNAN LADANG HASSAN SDN. BHD", ln=True, align='L')
    pdf.cell(0, 5, txt="(PLH PALM OIL MILL)", ln=True, align='L')
    pdf.cell(0, 5, txt="KM 57 JALAN SANDAKAN-BELURAN,", ln=True, align='L')
    pdf.cell(0, 5, txt="OFF JALAN SPSI, 91000 SANDAKAN, SABAH.", ln=True, align='L')
    pdf.ln(5)

    pdf.cell(0, 6, txt="Dear Sir,", ln=True, align='L')
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 6, txt=f"TRANSPORTATION OF EMPTY FRUIT BUNCH TO {premise.upper()}", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    pdf.ln(3)
    
    body_text = (f"Referring to the above, we will send lorry truck as below to load EFB from PLH Palm "
                 f"Oil Mill on {formatted_date} and delivery to {premise}. Transportation Company "
                 f"Name : PDH & NAS Enterprise.\n\n"
                 f"Below is the list of lorries truck and transport and driver details for your reference:")
    pdf.multi_cell(0, 6, txt=body_text)
    pdf.ln(5)

    # Table Header
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(79, 8, "DRIVER NAME", border=1)
    pdf.cell(79, 8, "TRUCK / TRAILER NO", border=1, ln=True)

    # Table Content - Loop through all drivers
    pdf.set_font("Arial", size=12)
    for i in range(num_drivers):
        d_name_upper = drivers[i].upper() if drivers[i] else ""
        l_no_upper = lorries[i].upper() if lorries[i] else ""
        pdf.cell(79, 8, d_name_upper, border=1)
        pdf.cell(79, 8, l_no_upper, border=1, ln=True)
        
    pdf.ln(15)

    pdf.cell(0, 6, txt="Thank you", ln=True, align='L')
    pdf.ln(20)
    pdf.cell(0, 6, txt="__________________", ln=True, align='L')
    pdf.cell(0, 6, txt="Admin", ln=True, align='L')
    pdf.cell(0, 6, txt="PDH & NAS Enterprise", ln=True, align='L')

    pdf_file = "Delivery_Note.pdf"
    pdf.output(pdf_file)

    with open(pdf_file, "rb") as file:
        st.download_button(
            label="Download Delivery Note (PDF)",
            data=file,
            file_name=f"{dn_number.replace('/', '_')}.pdf",
            mime="application/pdf"
        )
