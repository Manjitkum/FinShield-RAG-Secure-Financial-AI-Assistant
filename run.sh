#!/bin/bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
cd finshield/src
streamlit run app.py --server.port 8501 --server.address 0.0.0.0