# PageMyCV

**PageMyCV** is a Flask-based web application that transforms a PDF resume into a professional-looking online portfolio page. Users can upload their resume, and the app automatically extracts key details using Google GenAI and hosts the final webpage via AWS S3 and CloudFront.

## Features

- Upload a PDF resume via the web interface
- Extract structured information using Google GenAI
- Generate a clean HTML portfolio using Jinja templates
- Automatically host the portfolio using AWS S3 and CloudFront
- Uses Pulumi ESC for managing secure environment variables

---

## Tech Stack

- **Python + Flask** – Web server and routing
- **Fitz (PyMuPDF)** – PDF text extraction
- **Google GenAI** – Resume data extraction
- **Pulumi ESC SDK** – Environment configuration
- **AWS S3 + CloudFront** – Static site hosting
- **Boto3** – AWS SDK for Python

---

## Prerequisites

- Python 3.8 or higher
- Google GenAI API Key
- AWS Account with:
  - S3 Bucket
  - CloudFront distribution
- Pulumi ESC configured with the required environment values

---

## Setting up Environment Variables

- Follow this Tutorial to [install Pulumi CLI](https://www.pulumi.com/docs/esc/download-install/) in your machine
- Follow this Tutorial to [get Pulumi Access Tokens](https://www.pulumi.com/docs/pulumi-cloud/access-management/access-tokens/#creating-personal-access-tokens) for your account and set it as ENV variable in your machine.
- Follow this Tutorial to [set up AWS Credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration) in your machine.

## Getting Started 🚀

1. **Clone the repository**

```bash
git clone https://github.com/vivekthedev/pagemycv.git
cd pagemycv
```

2. Create and activate a virtual environment

```
python -m venv env
source env/bin/activate # for Mac and Linue
env\Scripts\activate    # for Windows
```

3. Install Dependencies

```bash
pip install -r requirements.txt
```

4. Create Pulumi ESC Envrionment

```
pulumi login
esc env init default/flaskapp
```

5. Create Environment Settings

```
esc env set default/flaskapp MODEL [YOUR_MODEL_NAME]
esc env set default/flaskapp MODEL_API_KEY [YOUR_MODEL_API_KEY] --secret
esc env set default/flaskapp BUCKET_NAME [YOUR_BUCKET_NAME]
esc env set default/flaskapp CLOUDFRONT_URL [YOUR_CLOUDFRONT_URL]
```

6. Creating Dynamic Configuration

```
esc env edit default/flaskapp
```
The configuration file would open up add the following changes 

```
values:
  MODEL: [YOUR_MODEL_NAME]
  MODEL_API_KEY:
    fn::secret:
      ciphertext: ZXNjeAAAAAEAAAEAiKFzqkZ6ljM6KYYU++O/Q3tt5kjjcpSWGo5hTyAynZOB2W6a/16EjwVubemQxfay1rqSQYIY2hWVv1qhuqIK7wL0VYTGHZo=
  BUCKET_NAME: [YOUR_BUCKET_NAME]
  CLOUDFRONT_URL: [YOUR_CLOUDFRONT_URL]
  esc_org: ${context.pulumi.organization.login}         
  esc_project: "default"                                
  esc_environment: ${context.currentEnvironment.name}   
  environmentVariables:                                 
    MODEL: ${MODEL}                                     
    MODEL_API_KEY: ${MODEL_API_KEY}
    BUCKET_NAME: ${BUCKET_NAME}
    CLOUDFRONT_URL: ${CLOUDFRONT_URL}
    ESC_ORG: ${esc_org}
    ESC_PROJECT: ${esc_project}
    ESC_ENVIRONMENT: ${esc_environment}
```
Save the file and close to update the environment.

7. Run the application

```
esc env run default/flaskapp -- python app.py
```

Visite 127.0.0.0.1:5000 to view your application.
