import datetime
from decimal import Decimal

import streamlit as st

from invoice_pdf import amount_in_words, build_invoice_pdf, compute_items, money

st.title("PDH & NAS Enterprise - Invoice Generator")

# ---------------------------------------------------------
# 1. INVOICE INFORMATION
# ---------------------------------------------------------
st.subheader("1. Invoice Information")
c1, c2 = st.columns(2)
with c1:
    inv_date = st.date_input("Invoice Date", datetime.date.today())
with c2:
    running_no = st.number_input("Running Number (resets each month, e.g. 1 for 01)",
                                 min_value=1, value=1)

invoice_no = f"INV/PDHNAS/{inv_date.month:02d}/{inv_date.year}/{running_no:02d}"
st.caption(f"Invoice number: **{invoice_no}**")

# ---------------------------------------------------------
# 2. CUSTOMER
# ---------------------------------------------------------
st.subheader("2. Customer (Pelanggan)")
customer = st.text_area(
    "Customer name & address (one line per row):",
    "CASH HORSE (M) SDN.BHD (785805-W)\nLot 70, Block 6, Prima Square,\n"
    "Mile 4, North Road,\n90000 SANDAKAN, SABAH.",
    height=130,
)

st.markdown("---")

# ---------------------------------------------------------
# 3. WORK ITEMS
# ---------------------------------------------------------
st.subheader("3. Work Items (Keterangan Kerja)")
num_items = st.number_input("Number of items", min_value=1, max_value=10, value=1, step=1)

items = []
for i in range(num_items):
    st.markdown(f"**Item {i + 1}**")
    desc = st.text_area(
        "Description (press Enter for new lines, e.g. one line per trip/DN)",
        "TRANSPORTATION - EFB PURCHASE\nPEMBANGUNAN LADANG HASAN - CASH HORSE BIOMAS SEGALIUD"
        if i == 0 else "",
        height=150, key=f"desc_{i}",
    )
    q1, q2, q3 = st.columns(3)
    with q1:
        qty = st.number_input("Quantity", min_value=0.0, value=0.0, step=0.01,
                              format="%.2f", key=f"qty_{i}")
    with q2:
        unit = st.text_input("Unit", "MT", key=f"unit_{i}")
    with q3:
        price = st.number_input("Unit Price (RM)", min_value=0.0, value=0.0, step=0.01,
                                format="%.2f", key=f"price_{i}")
    items.append({"description": desc, "qty": Decimal(str(qty)),
                  "unit": unit, "price": Decimal(str(price))})

total = compute_items(items)
st.info(f"**Total: RM {money(total)}**  \n{amount_in_words(total)}")

st.markdown("---")

# ---------------------------------------------------------
# GENERATE
# ---------------------------------------------------------
if st.button("Generate Invoice PDF", type="primary"):
    if total <= 0:
        st.error("Please enter a quantity and unit price first.")
    else:
        st.session_state.inv_pdf = build_invoice_pdf(
            inv_date, invoice_no, customer.split("\n"), items)
        st.session_state.inv_filename = f"Invoice_{invoice_no.replace('/', '_')}.pdf"

if st.session_state.get("inv_pdf"):
    st.success("Invoice generated successfully!")
    st.download_button("📥 Download Invoice", data=st.session_state.inv_pdf,
                       file_name=st.session_state.inv_filename,
                       mime="application/pdf", use_container_width=True)
