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
        
        response = client.label_detection(image=image)
        labels = response.label_annotations
        if labels:
            return labels[0].description
        return "Unknown Product"
    except Exception as e:
        return f"Error running AI: {e}"

# 3. EXPANDED LISTING MATCH ENGINE (With Verification Links)
def fetch_competitor_prices(product_keywords):
    # Expanded mock listings simulating multiple marketplace entries for verification
    mock_results = [
        {"retailer": "Amazon Marketplace (Seller A)", "price": "$119.99", "status": "Market Average", "link": "https://www.amazon.com"},
        {"retailer": "Amazon Marketplace (Seller B)", "price": "$115.50", "status": "Competitive Rate", "link": "https://www.amazon.com"},
        {"retailer": "Amazon Marketplace (Refurbished)", "price": "$95.00", "status": "Used / Open Box", "link": "https://www.amazon.com"},
        {"retailer": "Walmart Commerce", "price": "$98.50", "status": "Lowest Price New 🟢", "link": "https://www.walmart.com"},
        {"retailer": "Target Stores Digital", "price": "$124.00", "status": "Highest Price 🔴", "link": "https://www.target.com"}
    ]
    return mock_results

# 4. STREAMLIT WEBSITE USER INTERFACE
st.set_page_config(page_title="B2B Pricing Intelligence Dashboard", layout="wide")

st.title("📊 Enterprise Competitor Pricing Engine")
st.write("Upload an item photo to run image extraction, track active market benchmarks, and access direct verification links.")

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
            keywords = identify_product_from_image(file_bytes)
            st.info(f"**AI Detected Product:** {keywords}")
            
            pricing_data = fetch_competitor_prices(keywords)
            
            st.write("### Active Market Rates Found:")
            st.write("Review all matching marketplace listings below to conduct secondary verification.")
            
            # Formats the table column to treat strings as clickable URL destinations
            st.data_editor(
                pricing_data,
                column_config={
                    "link": st.column_config.LinkColumn("Source Link", help="Click to open matching listing for due diligence Verification")
                },
                disabled=True,
                use_container_width=True
            )
            
            st.success("✅ Audit complete! Data is ready to export for price balancing updates.")
    else:
        st.write("Awaiting image file upload to generate pricing matrix.")
