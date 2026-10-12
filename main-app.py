import streamlit as st
from fpdf import FPDF
import datetime

st.title("PDH & NAS Enterprise - Document Generator")

# ---------------------------------------------------------
# 1. DELIVERY NOTE INFORMATION
# ---------------------------------------------------------
st.subheader("1. Delivery Note Information")
col1, col2 = st.columns(2)
with col1:
    date_input = st.date_input("Date", datetime.date.today())
    running_no = st.number_input("Running Number (e.g., 1 for 01)", min_value=1, value=1)
    pickup_loc = st.text_input("Pickup Location (for paragraph)", "LOKASI PENGAMBILAN")
with col2:
    premise = st.text_input("Delivery Destination", "LOKASI PENGHANTARAN")

st.caption("Recipient Address (Top Left of Delivery Note)")
recipient_address = st.text_area(
    "Edit Recipient Details:",
    "NAMA PENERIMA / PENGURUS\nNAMA SYARIKAT\nALAMAT BARIS 1\nALAMAT BARIS 2\nPOSKOD, DAERAH, NEGERI.",
    height=120
)

st.markdown("---")

# ---------------------------------------------------------
# 2. COLLECTION ORDER INFORMATION
# ---------------------------------------------------------
st.subheader("2. Collection Order Information")
co_col1, co_col2 = st.columns(2)
with co_col1:
    co_no = st.text_input("Collection Order NO:", "CO-001")
    buyer = st.text_input("Buyer:", "CASH (M) HORSE SDN BHD")
with co_col2:
    collection_name = st.text_input("Name for Collection:", "EFB")

st.markdown("---")

# ---------------------------------------------------------
# 3. DRIVER DETAILS
# ---------------------------------------------------------
st.subheader("3. Driver Details")
num_drivers = st.number_input("Number of Drivers", min_value=1, max_value=10, value=1, step=1)

drivers = []
ics = []
lorries = []

for i in range(num_drivers):
    st.markdown(f"**Driver {i+1}**")
    d_col1, d_col2, d_col3 = st.columns(3)
    with d_col1:
        default_driver = "ALI BIN ABU" if i == 0 else ""
        d_name = st.text_input("Name", default_driver, key=f"d_name_{i}")
        drivers.append(d_name)
    with d_col2:
        default_ic = "900101-12-3456" if i == 0 else ""
        d_ic = st.text_input("IC Number", default_ic, key=f"d_ic_{i}")
        ics.append(d_ic)
    with d_col3:
        default_lorry = "ABC1234" if i == 0 else ""
        l_no = st.text_input("Lorry Number", default_lorry, key=f"l_no_{i}")
        lorries.append(l_no)

st.markdown("---")

# ---------------------------------------------------------
# GENERATE PDFS BUTTON & MEMORY
# ---------------------------------------------------------
if st.button("Generate Both PDFs", type="primary"):
    dn_number = f"DN/PDH&NAS/{running_no:02d}/2026"
    formatted_date = date_input.strftime("%d %b %Y")

    # ==========================================
    # PDF 1: DELIVERY NOTE
    # ==========================================
    pdf_dn = FPDF()
    pdf_dn.add_page()
    pdf_dn.set_margins(left=25.4, top=15.0, right=25.4)

    pdf_dn.set_font("Arial", 'B', 14)
    pdf_dn.cell(0, 8, txt="PDH & NAS ENTERPRISE", ln=True, align='C')
    pdf_dn.set_font("Arial", 'B', 12)
    pdf_dn.cell(0, 6, txt="LOT 5, BLOK R, TINGKAT BAWAH BANDAR RAMAI-RAMAI", ln=True, align='C')
    pdf_dn.cell(0, 6, txt="JALAN LEILA 90000 SANDAKAN SABAH", ln=True, align='C')
    
    pdf_dn.ln(2)
    current_y = pdf_dn.get_y()
    pdf_dn.line(25.4, current_y, 210 - 25.4, current_y)
    pdf_dn.ln(2)

    pdf_dn.set_font("Arial", size=12)
    pdf_dn.cell(0, 6, txt=f"Ref.No. {dn_number}", ln=True, align='R')
    pdf_dn.cell(0, 6, txt=f"Date : {formatted_date}", ln=True, align='R')
    pdf_dn.ln(5)

    address_lines = recipient_address.split('\n')
    for line in address_lines:
        if line.strip().upper() in ["MANAGER", "SECURITY UNIT"]:
            pdf_dn.set_font("Arial", 'B', 12)
        else:
            pdf_dn.set_font("Arial", size=12)
        pdf_dn.cell(0, 5, txt=line, ln=True, align='L')
        
    pdf_dn.ln(5)
    pdf_dn.cell(0, 6, txt="Dear Sir,", ln=True, align='L')
    pdf_dn.set_font("Arial", 'B', 12)
    pdf_dn.cell(0, 6, txt=f"TRANSPORTATION OF EMPTY FRUIT BUNCH TO {premise.upper()}", ln=True, align='L')
    pdf_dn.set_font("Arial", size=12)
    pdf_dn.ln(3)
    
    body_text = (f"Referring to the above, we will send lorry truck as below to load EFB from {pickup_loc} "
                 f"on {formatted_date} and delivery to {premise}. Transportation Company "
                 f"Name : PDH & NAS Enterprise.\n\n"
                 f"Below is the list of lorries truck and transport and driver details for your reference:")
    pdf_dn.multi_cell(0, 6, txt=body_text)
    pdf_dn.ln(5)

    pdf_dn.set_font("Arial", 'B', 12)
    pdf_dn.cell(79, 8, "DRIVER NAME", border=1)
    pdf_dn.cell(79, 8, "TRUCK / TRAILER NO", border=1, ln=True)

    pdf_dn.set_font("Arial", size=12)
    for i in range(num_drivers):
        pdf_dn.cell(79, 8, drivers[i].upper() if drivers[i] else "", border=1)
        pdf_dn.cell(79, 8, lorries[i].upper() if lorries[i] else "", border=1, ln=True)
        
    pdf_dn.ln(15)
    pdf_dn.cell(0, 6, txt="Thank you", ln=True, align='L')
    pdf_dn.ln(30)
    pdf_dn.cell(0, 6, txt="__________________", ln=True, align='L')
    pdf_dn.cell(0, 6, txt="Admin", ln=True, align='L')
    pdf_dn.cell(0, 6, txt="PDH & NAS Enterprise", ln=True, align='L')

    file_dn = "Delivery_Note.pdf"
    pdf_dn.output(file_dn)

    # ==========================================
    # PDF 2: COLLECTION ORDER
    # ==========================================
    pdf_co = FPDF()
    for i in range(num_drivers):
        pdf_co.add_page()
        pdf_co.set_margins(left=25.4, top=20.0, right=25.4)

        pdf_co.set_font("Arial", size=12)
        pdf_co.cell(0, 6, txt="PDH & NAS ENTERPRISE", ln=True, align='C')
        pdf_co.cell(0, 6, txt="LOT 5, BLOK R, TINGKAT BAWAH BANDAR RAMAI-RAMAI", ln=True, align='C')
        pdf_co.cell(0, 6, txt="JALAN LEILA 90000 SANDAKAN SABAH", ln=True, align='C')
        pdf_co.ln(15)
        
        pdf_co.set_font("Arial", 'U', 12)
        pdf_co.cell(100, 6, txt="COLLECTION ORDER", align='L')
        pdf_co.set_font("Arial", size=12)
        pdf_co.cell(0, 6, txt=f"NO: {co_no}", ln=True, align='L')
        pdf_co.ln(5)

        pdf_co.cell(100, 6, txt=f"DN NO: {dn_number}", align='L')
        pdf_co.cell(0, 6, txt=f"DATE: {formatted_date}", ln=True, align='L')
        pdf_co.ln(8)

        pdf_co.set_font("Arial", 'U', 12)
        pdf_co.cell(0, 6, txt="PLEASE ALLOW THE COLLECTION AS STATTED BELOW FOR TRANSPORTATION", ln=True, align='C')
        pdf_co.set_font("Arial", size=12)
        pdf_co.ln(12)

        label_w = 60
        colon_w = 5
        line_height = 8

        def add_co_row(label, value):
            pdf_co.cell(label_w, line_height, txt=label, align='L')
            pdf_co.cell(colon_w, line_height, txt=":", align='C')
            pdf_co.cell(0, line_height, txt=value, ln=True, align='L')

        add_co_row("Buyer", buyer)
        add_co_row("Name for Collection", collection_name)
        add_co_row("Name of Transportation", "PDH & NAS Enterprise")
        add_co_row("Driver Name", drivers[i].upper() if drivers[i] else "")
        add_co_row("ID Card Number", ics[i].upper() if ics[i] else "")
        add_co_row("Lorry No", lorries[i].upper() if lorries[i] else "")
        
        pdf_co.cell(label_w, 35, txt="Company Cop", align='L')
        pdf_co.cell(colon_w, 35, txt=":", align='C')
        pdf_co.cell(0, 35, txt="", ln=True, align='C') 
        
        pdf_co.cell(label_w, 10, txt="Driver Signature", align='L')
        pdf_co.cell(colon_w, 10, txt=":", align='C')
        pdf_co.ln(15)
        pdf_co.cell(0, 6, txt=".........................................................................................................", ln=True, align='L')

    file_co = "Collection_Order.pdf"
    pdf_co.output(file_co)

    # Save to memory (session_state) so they survive the page refresh
    with open(file_dn, "rb") as f:
        st.session_state.dn_pdf_bytes = f.read()
    with open(file_co, "rb") as f:
        st.session_state.co_pdf_bytes = f.read()
        
    st.session_state.dn_filename = f"Delivery_Note_{dn_number.replace('/', '_')}.pdf"
    st.session_state.co_filename = f"Collection_Order_{co_no}.pdf"
    st.session_state.pdfs_generated = True

# ---------------------------------------------------------
# DISPLAY DOWNLOAD BUTTONS (Always visible if generated)
# ---------------------------------------------------------
if st.session_state.get('pdfs_generated', False):
    st.success("Both documents generated successfully!")
    dl_col1, dl_col2 = st.columns(2)
    
    with dl_col1:
        st.download_button(
            label="📥 Download Delivery Note",
            data=st.session_state.dn_pdf_bytes,
            file_name=st.session_state.dn_filename,
            mime="application/pdf",
            use_container_width=True
        )
            
    with dl_col2:
        st.download_button(
            label="📥 Download Collection Order",
            data=st.session_state.co_pdf_bytes,
            file_name=st.session_state.co_filename,
            mime="application/pdf",
            use_container_width=True
        )