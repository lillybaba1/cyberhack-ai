#!/bin/bash
echo "Installing deps..."
cd ../frontend && npm install
cd ../backend && pip install -r requirements.txt
cd ../services/ai_scanner && pip install -r requirements.txt
