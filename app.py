import os
import json
import streamlit as st
from google.cloud import vision

# 1. SECURE CREDENTIAL CHECK (Reads from your GitHub Vault)
if "GOOGLE_CREDENTIALS" in os.environ:
    try:
        creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
        with open("temp_credentials.json", "w") as f:
            json.dump(creds_dict, f)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "temp_credentials.json"
    except Exception as e:
        st.error(f"Vault key error: {e}")
else:
    st.warning("Running without Google Credentials. AI scanning will be unavailable.")

# 2. VISUAL AI SCANNER FUNCTION
def identify_product_from_image(image_bytes):
    try:
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_bytes)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if texts:
            detected_text = texts[0].description.replace('\n', ' ')
            return detected_text
        
        # Fallback to general object labels if no text found
        response = client.label_detection(image=image)
        labels = response.label_annotations
        if labels:
            return labels[0].description
        return "Unknown Product"
    except Exception as e:
        return f"Error running AI: {e}"

# 3. COMPETITOR PRICE SCRAPER (Simulated for MVP)
def fetch_competitor_prices(product_keywords):
    # Simulated database matching your business concept
    mock_results = [
        {"retailer": "Amazon Marketplace", "price": "$119.99", "status": "Market Average"},
        {"retailer": "Walmart Commerce", "price": "$98.50", "status": "Lowest Price 🟢"},
        {"retailer": "Target Stores Digital", "price": "$124.00", "status": "Highest Price 🔴"}
    ]
    return mock_results

# 4. STREAMLIT WEBSITE USER INTERFACE
st.set_page_config(page_title="B2B Pricing Intelligence Dashboard", layout="wide")

st.title("📊 Enterprise Competitor Pricing Engine")
st.write("Upload an item photo to run image extraction and track active market benchmarking benchmarks.")

# Create two side-by-side columns on your webpage
col1, col2 = st.columns(2)

with col1:
    st.subheader("📸 Step 1: Upload Product Snapshot")
    uploaded_file = st.file_uploader("Drop a product image here...", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        st.image(file_bytes, caption='Target Audit Item', width=400)

with col2:
    st.subheader("📊 Step 2: Competitor Live Benchmarking")
    if uploaded_file is not None:
        with st.spinner("🤖 Extracting identity and pulling competitor retail data..."):
            # Execute our code logic
            keywords = identify_product_from_image(file_bytes)
            st.info(f"**AI Detected Product:** {keywords}")
            
            pricing_data = fetch_competitor_prices(keywords)
            
            # Display results in a clean dashboard table
            st.write("### Active Market Rates Found:")
            st.table(pricing_data)
            
            st.success("✅ Audit complete! Data is ready to export for price balancing updates.")
    else:
        st.write("Awaiting image file upload to generate pricing matrix.")
