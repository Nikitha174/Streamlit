import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------- Page Config ---------------------
st.set_page_config(page_title="📊 Survey Results Visualizer", layout="wide")

# --------------------- Custom CSS ----------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500&family=Open+Sans&display=swap');
    html, body, [class*="css"] {
        font-family: 'Open Sans', sans-serif;
        background: linear-gradient(to right, #e3f2fd, #fce4ec);
    }
    h1 {
        color: #4a148c;
        font-family: 'Orbitron', sans-serif;
    }
    .stButton>button {
        background-color: #6a1b9a;
        color: white;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------- Header ---------------------
st.title("📊 Survey Results Visualizer")
st.markdown("Upload your survey data and visualize the results with **auto-generated charts**.")

# --------------------- File Upload ---------------------
uploaded_file = st.file_uploader("Upload your survey CSV file", type=['csv'])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ File uploaded successfully!")
    
    st.subheader("📄 Preview of Uploaded Data")
    st.dataframe(df.head(), use_container_width=True)

    st.markdown("---")
    st.subheader("📈 Auto-Generated Charts")
    
    # ------------------ Column-wise Visualization ------------------
    for col in df.columns:
        st.markdown(f"#### 📍 Column: `{col}`")
        col_data = df[col].dropna()

        # Try to categorize the column
        if pd.api.types.is_numeric_dtype(col_data):
            chart_type = st.selectbox(f"Choose chart for `{col}`", ["Histogram", "Boxplot"], key=col)

            if chart_type == "Histogram":
                fig = px.histogram(df, x=col, nbins=20, title=f"Histogram of {col}")
            else:
                fig = px.box(df, y=col, title=f"Boxplot of {col}")
            st.plotly_chart(fig, use_container_width=True)

        else:
            if df[col].nunique() <= 10:
                chart_type = st.selectbox(f"Choose chart for `{col}`", ["Bar", "Pie"], key=col)
                value_counts = df[col].value_counts().reset_index()
                value_counts.columns = [col, 'Count']

                if chart_type == "Bar":
                    fig = px.bar(value_counts, x=col, y='Count', title=f"Bar chart of {col}", text='Count', color=col)
                else:
                    fig = px.pie(value_counts, names=col, values='Count', title=f"Pie chart of {col}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"🔍 Too many unique values in `{col}` to generate chart.")

    # --------------------- Raw Data Toggle ---------------------
    with st.expander("🔍 View Full Dataset"):
        st.dataframe(df, use_container_width=True)

else:
    st.info("👆 Please upload a CSV file to begin visualizing.")

# --------------------- Footer ---------------------
st.markdown("---")
st.markdown("<center>Made with ❤️| © 2025</center>", unsafe_allow_html=True)
