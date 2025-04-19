# Welcome to Teaching Helper!

## Folder Structure
```
├── /backend
│ ├── database.py # Handles database schema and interactions
│ ├── evaluation.py # Logic for evaluation and grading
│ ├── chatbot.py # Chatbot interaction logic
│ ├── utils.py # Common utilities
│ └── __init__.py # Marks the folder as a package
│
├── /frontend
│ ├── main.py # Entry point for Streamlit app
│ ├── sidebar.py # Components for the left sidebar
│ ├── dialogs.py # Main dialog zone logic
│ ├── sandbox.py # Sandbox logic for coding evaluation
│ ├── evaluation_ui.py # UI components for evaluation
│ └── __init__.py # Marks the folder as a package
│
├── /static
│ ├── styles.css # Custom styles for the app
│
├── /data
│ └── example_data.json # Example or test data for development
│
├── requirements.txt # Python dependencies
├── README.md # Overview and instructions
└── deploy.sh # Script for deployment to Google Cloud VM
```
### Content of Key Files

`/backend/database.py`
Defines the database structure for students, professors, courses, and chapters. Manages CRUD operations.

`/backend/evaluation.py`
Contains logic to evaluate answers (text, code snippets, or true/false), calculate scores, and provide feedback.

`/backend/chatbot.py`
Handles chatbot interactions, including structured dialog flow for assisted learning and evaluation.

`/backend/utils.py`
Utility functions for formatting, logging, and handling errors.

`/frontend/main.py`
Sets up the Streamlit app layout with sidebar and main content areas.

`/frontend/sidebar.py`
Implements the sidebar UI:
Selection of chapters/units.
Evaluation of selected chapters.
User feedback surveys.

`/frontend/dialogs.py`
Handles the main dialog flow for user interaction:
Assisted learning: Displays content and prompts questions.
Evaluation: Allows submission of answers and displays scores.

`/frontend/sandbox.py`
Implements a coding sandbox for user input and automated evaluation.

`/frontend/evaluation_ui.py`
Displays results of evaluations and feedback on answers.

`/static/styles.css`
Customizes the appearance of the Streamlit app.

`/data/example_data.json`

## Run the code locally

```
VIRTUAL_ENV=__working_dir__
python3.10 -m venv $VIRTUAL_ENV
source $VIRTUAL_ENV/bin/activate
```
You only need to do this once:
`pip install --upgrade pip`
`python3.10 -m pip install --pre torch --extra-index-url https://download.pytorch.org/whl/cu124`
You only need to do this when you change the requirements.txt file:
`python3.10 -m pip install -r requirements.txt`

Run it:
`sh deploy.sh`

## Docker
### Local environment

Build it (every time you change code):
`docker build -t teaching-helper .`

Run it:
```
docker rm -f teaching-helper; docker run --name teaching-helper \
-p 58080:8080 \
-e redirect_uri="http://localhost:58080" \
teaching-helper
```
If you want to debug the container while it's running:
`docker exec -it teaching-helper bash`

### Google Cloud Run
You need to login once with your Google account and activate the project:
`gcloud auth login`
`gcloud config set project clasificationfromdescription`

Creating the depository, you only need to do this once for the project:
`gcloud artifacts repositories create teaching-helper --location="europe-west3" --repository-format=Docker`

Build it (every time you change code):
`gcloud builds submit --tag "europe-west3-docker.pkg.dev/clasificationfromdescription/teaching-helper/teaching-helper"`

Run it:
```
gcloud run deploy "teaching-helper" \
--memory=3Gi \
--cpu=2 \
--port=8080 \
--image="europe-west3-docker.pkg.dev/clasificationfromdescription/teaching-helper/teaching-helper" \
--allow-unauthenticated \
--region="europe-west3" \
--platform=managed \
--project=clasificationfromdescription \
--set-env-vars=GCP_PROJECT=clasificationfromdescription,GCP_REGION=europe-west3,redirect_uri='https://teaching-helper-612652291913.europe-west3.run.app' \
--update-secrets=/app/secrets_sa/sa_private_key.json=sa_private_key:latest \
--update-secrets=/app/secrets_ak/client_secret_auth_key.json=client_secret_auth_key:latest
```

## Create a Google Cloud Service account
**You only need to do this once for the project**:

Install google-cloud-sdk https://cloud.google.com/sdk/docs/install

```
gcloud auth login
gcloud config set project clasificationfromdescription

gcloud iam service-accounts create sa-teaching-helper \
--description "Service account dedicated to the external application teaching-helper to consume Vertex AI endpoint" \
--display-name "Vertex AI consumption for app teaching-helper"

gcloud projects add-iam-policy-binding clasificationfromdescription \
--member 'serviceAccount:sa-teaching-helper@clasificationfromdescription.iam.gserviceaccount.com' \
--role 'roles/aiplatform.user'

gcloud iam service-accounts keys create secrets_sa/sa_private_key.json \
--iam-account sa-teaching-helper@clasificationfromdescription.iam.gserviceaccount.com

gcloud secrets create sa_private_key --data-file=secrets_sa/sa_private_key.json

# for the google_auth 
gcloud secrets create client_secret_auth_key --data-file=secrets_ak/client_secret_auth_key.json

#to add a version
gcloud secrets versions add sa_private_key --data-file=secrets_sa/sa_private_key.json

#run this once for each cloud run container, allows it to read secrets
gcloud projects add-iam-policy-binding clasificationfromdescription \
--member 'serviceAccount:612652291913-compute@developer.gserviceaccount.com' \
--role 'roles/secretmanager.secretAccessor'
```
## Add an email to Gauth (New user)
- you need an user GMAIL account (just gmail)
- got in connsole.cloud.google.com , project clasificationfromdescription, search Oauth Consent
Select Audience, Add users, add gmail user
