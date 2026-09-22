#!/bin/bash

# Start the background crawler
python core/crawler.py &

# Start the Streamlit web server
streamlit run app/Dashboard.py --server.port=8501 --server.address=0.0.0.0
