import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from openai import OpenAI

# -------------------------------------
# CONFIG
# -------------------------------------

st.set_page_config(
    page_title="What's Missing AI",
    layout="wide"
)

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# -------------------------------------
# PRODUCT CATALOGUE
# -------------------------------------

CATALOGUE = {
    "Chicken": [
        "Buttermilk Chicken Fillet",
        "Southern Fried Chicken Burger"
    ],
    "Pizza": [
        "Pizza Bases",
        "Pizza Toppings"
    ],
    "Dessert": [
        "Chocolate Brownie",
        "Cheesecake",
        "Ice Cream"
    ],
    "Milkshake": [
        "Milkshake Mix"
    ],
    "Loaded Fries": [
        "Loaded Fries"
    ]
}

# -------------------------------------
# WEBSITE SEARCH
# -------------------------------------

def find_website(business, postcode):

    query = f"{business} {postcode}"

    with DDGS() as ddgs:

        results = list(
            ddgs.text(
                query,
                max_results=5
            )
        )

    if not results:
        return None

    return results[0]["href"]

# -------------------------------------
# SCRAPER
# -------------------------------------

def scrape_website(url):

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        response = requests.get(
            url,
            timeout=20,
            headers=headers
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        content = " ".join(
            soup.stripped_strings
        )

        return content[:50000]

    except Exception as e:

        return f"ERROR: {e}"

# -------------------------------------
# OPENAI ANALYSIS
# -------------------------------------

def analyse_business(content):

    prompt = f"""
You are a foodservice sales expert.

Analyse the business website content.

Provide:

1. Business Type
2. Products Sold
3. Food Categories
4. Promotions
5. Missing Categories
6. Revenue Opportunities
7. Products They Should Buy
8. Suggested Sales Pitch

Website Content:

{content}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    return response.choices[0].message.content

# -------------------------------------
# GAP ANALYSIS
# -------------------------------------

def identify_gaps(text):

    text = text.lower()

    gaps = []

    if "pizza" not in text:
        gaps.extend(CATALOGUE["Pizza"])

    if "chicken" not in text:
        gaps.extend(CATALOGUE["Chicken"])

    if (
        "dessert" not in text
        and "brownie" not in text
        and "cheesecake" not in text
    ):
        gaps.extend(CATALOGUE["Dessert"])

    if "milkshake" not in text:
        gaps.extend(CATALOGUE["Milkshake"])

    if "loaded fries" not in text:
        gaps.extend(CATALOGUE["Loaded Fries"])

    return gaps

# -------------------------------------
# UI
# -------------------------------------

st.title("🍔 What's Missing AI")

st.markdown(
"""
Enter a customer name and postcode.

The system will:

✅ Search the business

✅ Find website

✅ Analyse menu

✅ Detect opportunities

✅ Suggest products to sell
"""
)

business = st.text_input(
    "Business Name"
)

postcode = st.text_input(
    "Postcode"
)

if st.button("Analyse Customer"):

    if not business:

        st.error(
            "Please enter a business name."
        )

        st.stop()

    with st.spinner(
        "Searching for customer..."
    ):

        website = find_website(
            business,
            postcode
        )

    if not website:

        st.error(
            "No website found."
        )

        st.stop()

    st.success(
        f"Website Found: {website}"
    )

    with st.spinner(
        "Scraping website..."
    ):

        website_text = scrape_website(
            website
        )

    if website_text.startswith(
        "ERROR"
    ):

        st.error(
            website_text
        )

        st.stop()

    with st.spinner(
        "Running AI analysis..."
    ):

        report = analyse_business(
            website_text
        )

    gaps = identify_gaps(
        website_text
    )

    st.subheader(
        "Customer Opportunity Report"
    )

    st.markdown(report)

    st.subheader(
        "Suggested Products"
    )

    if gaps:

        for item in gaps:

            st.success(item)

    else:

        st.success(
            "No obvious missing categories found."
        )

    st.subheader(
        "Raw Website Data"
    )

    with st.expander(
        "View Website Content"
    ):
        st.write(
            website_text[:10000]
        )
