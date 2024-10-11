import streamlit as st

st.title("Donate via PayPal QR Code")

st.write("Scan the QR code below to donate via PayPal:")

# Replace this with your actual Cloudinary image URL
qr_code_url = "https://res.cloudinary.com/dqqghauxt/image/upload/v1728690000/qrcode_warg7k.png"

# Display the QR code
st.image(qr_code_url, caption="PayPal QR Code", width=300)
