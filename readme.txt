# Create new virtual environment
python -m venv venv

# Activate virtual environment
# For Windows:
venv\Scripts\activate
# For Linux/Mac:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

python src/main.py