

Folder Structure
bash
Copy code
/app
│
├── /backend
│   ├── database.py       # Handles database schema and interactions
│   ├── evaluation.py     # Logic for evaluation and grading
│   ├── chatbot.py        # Chatbot interaction logic
│   ├── utils.py          # Common utilities
│   └── __init__.py       # Marks the folder as a package
│
├── /frontend
│   ├── main.py           # Entry point for Streamlit app
│   ├── sidebar.py        # Components for the left sidebar
│   ├── dialogs.py        # Main dialog zone logic
│   ├── sandbox.py        # Sandbox logic for coding evaluation
│   ├── evaluation_ui.py  # UI components for evaluation
│   └── __init__.py       # Marks the folder as a package
│
├── /static
│   ├── styles.css        # Custom styles for the app
│
├── /data
│   └── example_data.json # Example or test data for development
│
├── requirements.txt      # Python dependencies
├── README.md             # Overview and instructions
└── deploy.sh             # Script for deployment to Google Cloud VM
Content of Key Files
/backend/database.py
Defines the database structure for students, professors, courses, and chapters. Manages CRUD operations.

/backend/evaluation.py
Contains logic to evaluate answers (text, code snippets, or true/false), calculate scores, and provide feedback.

/backend/chatbot.py
Handles chatbot interactions, including structured dialog flow for assisted learning and evaluation.

/backend/utils.py
Utility functions for formatting, logging, and handling errors.

/frontend/main.py
Sets up the Streamlit app layout with sidebar and main content areas.

/frontend/sidebar.py
Implements the sidebar UI:

Selection of chapters/units.
Evaluation of selected chapters.
User feedback surveys.
/frontend/dialogs.py
Handles the main dialog flow for user interaction:

Assisted learning: Displays content and prompts questions.
Evaluation: Allows submission of answers and displays scores.
/frontend/sandbox.py
Implements a coding sandbox for user input and automated evaluation.

/frontend/evaluation_ui.py
Displays results of evaluations and feedback on answers.

/static/styles.css
Customizes the appearance of the Streamlit app.

/data/example_data.json




Deployment Instructions for Google Cloud VM
Create a VM:

Use the Google Cloud Console to create a new VM instance.
Select a machine type and region based on your needs.
Ensure HTTP and HTTPS traffic is allowed.
SSH into the VM:

Connect to the VM using SSH from the Google Cloud Console or terminal.
Install Python:

bash
Copy code
sudo apt-get update
sudo apt-get install -y python3 python3-pip
Upload Application:

Use SCP or upload files directly via the Google Cloud Console.
Run the Deployment Script:

bash
Copy code
chmod +x deploy.sh
./deploy.sh
Access the App:

Open the external IP of your VM in a browser with port 8501.

---------------
Create Google Cloud Service account

Install google-cloud-sdk https://cloud.google.com/sdk/docs/install

gcloud auth login
gcloud config set project __project_id__

gcloud iam service-accounts create sa-teaching-helper \
    --description "Service account dedicated to the external application teaching-helper to consume Vertex AI endpoint" \
    --display-name "Vertex AI consumption for app teaching-helper"
    --role roles/aiplatform.user

gcloud iam service-accounts keys create sa_private_key.json \
    --iam-account sa-teaching-helper@__project_id__.iam.gserviceaccount.com


---------------
Install packages

VIRTUAL_ENV=__working_dir__
python3.10 -m venv $VIRTUAL_ENV
source $VIRTUAL_ENV/bin/activate
pip install --upgrade pip

python3.10 -m pip install --pre torch --extra-index-url https://download.pytorch.org/whl/cu124
python3.10 -m pip install -r requirements.txt

