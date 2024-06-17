import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Define the category mapping
category_per_class = {
    "Plastic-Bag": "Daur Ulang", "Paper": "Daur Ulang", "Paper-Container": "Daur Ulang",
    "Paper-Cup": "Daur Ulang", "Tetra-Pak": "Daur Ulang", "Plastic-Bottle": "Guna Ulang",
    "Plastic-Container": "Daur Ulang", "Plastic-Cap": "Daur Ulang", "Plastic-Cup": "Guna Ulang",
    "Plastic-Cutlery": "Daur Ulang", "Plastic-Straw": "Daur Ulang", "Tissue": "Residu",
    "Styrofoam": "Residu"
}

def get_firebase_app():
    if not firebase_admin._apps:
        cred = credentials.Certificate('serviceAccountKey.json')
        return firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://trashdetection-647cc-default-rtdb.firebaseio.com'
        })
    else:
        return firebase_admin.get_app()

app = get_firebase_app()

detections_ref = db.reference('detections')
detection_counts_ref = db.reference('detection_counts')

st.title("Trash Detection Dashboard")

if st.button('Reset Database'):
    detections_ref.set({})
    detection_counts_ref.set({})
    st.success("Database has been reset.")
    
# Fetch detection counts from Firebase
detection_counts = detection_counts_ref.get()
if detection_counts is None:
    detection_counts = {}

# Fetch data from Firebase Realtime Database
data = detections_ref.get()

if data:
    df = pd.DataFrame.from_dict(data, orient='index')

    # Map labels to categories
    df['Category'] = df['label'].map(lambda x: category_per_class.get(x))

    # Group by category and count occurrences
    category_counts = df['Category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Detection Count']

    # Update and save counts to Firebase
    for index, row in category_counts.iterrows():
        category = row['Category']
        count = row['Detection Count']
        if category in detection_counts:
            detection_counts[category] += count
        else:
            detection_counts[category] = count
    detection_counts_ref.set(detection_counts)

    # Group by label and count occurrences
    # Group by label and count occurrences
    label_counts = df.groupby('label').size().reset_index(name='Detection Count')
    label_counts['Category'] = label_counts['label'].map(lambda x: category_per_class.get(x))
    label_counts = label_counts[['label', 'Category', 'Detection Count']]
    label_counts.columns = ['Label', 'Category', 'Detection Count']


    # Display the table of categories and counts
    st.subheader("Detection Counts per Category")
    st.table(category_counts)

    # Create a pie chart
    fig, ax = plt.subplots()
    ax.pie(category_counts['Detection Count'], labels=category_counts['Category'], autopct='%1.1f%%')
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    
    # Display the pie chart
    st.subheader("Detection Counts Distribution by Category")
    st.pyplot(fig)

    # Display the table of labels and counts
    st.subheader("Detection Counts per Label")
    st.table(label_counts)

    # Create a horizontal bar chart
    fig, ax = plt.subplots()
    ax.barh(label_counts['Label'], label_counts['Detection Count'])
    ax.set_xlabel('Detection Count')
    ax.set_title('Detection Counts per Label')
    
    # Display the horizontal bar chart
    st.subheader("Detection Counts per Label")
    st.pyplot(fig)

else:
    st.write("No detection data available.")

