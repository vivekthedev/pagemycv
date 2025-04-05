import os
from io import StringIO
from uuid import uuid4

import boto3
import fitz
import pulumi_esc_sdk as esc
from flask import Flask, redirect, render_template, request, url_for
from google import genai
from google.genai import types

app = Flask(__name__)

escOrg = os.getenv("ESC_ORG")
escProjectName = os.getenv("ESC_PROJECT")
escEnvironment = os.getenv("ESC_ENVIRONMENT")
esc_client = esc.esc_client.default_client()
_, values, _ = esc_client.open_and_read_environment(
    escOrg, escProjectName, escEnvironment
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "pdf_file" not in request.files:
        return redirect(url_for("error", msg="No file uploaded."))

    pdf_file = request.files["pdf_file"]

    if pdf_file.filename == "":
        return redirect(url_for("error", msg="No file selected."))

    if not pdf_file.filename.endswith(".pdf"):
        return redirect(
            url_for("error", msg="Invalid file format. Please upload a PDF.")
        )

    try:
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        extracted_text = "\n".join([page.get_text() for page in pdf_document])
        d = getResumeDetails(extracted_text)
        username = d["name"]
        html_content = render_template("site_template.html", **d)
        retUsername = username
        username = (
            username.strip()
            .replace(" ", "_")
            .replace(".", "_")
            .replace(",", "_")
            .replace(":", "_")
            .replace(";", "_")
        )
        obj_name = f"{username}-{uuid4().hex}.html"
        domain = values["CLOUDFRONT_URL"] + obj_name
        s3 = boto3.client("s3")
        s3.put_object(
            Bucket=values["BUCKET_NAME"],
            Key=obj_name,
            Body=html_content.encode("utf-8"),
            ContentType="text/html",
        )
        return redirect(url_for("success", page_url=domain, username=retUsername))
    except Exception as e:
        return redirect(
            url_for(
                "error",
                msg=f"Error while processing PDF Please try again later: {str(e)}",
            )
        )


@app.route("/success")
def success():
    page_url = request.args.get("page_url", None)
    username = request.args.get("username", None)
    if page_url:
        return render_template("success.html", page_url=page_url, username=username)
    else:
        return redirect(url_for("index"))


@app.route("/error")
def error():
    error_message = request.args.get("msg", "An unknown error occurred.")
    return render_template("error.html", message=error_message)


def getResumeDetails(extracted_text):
    resume_details_function = {
        "name": "getResumeDetails",
        "description": "gets the details from the provided resume text",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "nullable": True},
                "email": {"type": "string", "nullable": True},
                "education": {
                    "type": "array",
                    "nullable": True,
                    "items": {
                        "type": "object",
                        "properties": {
                            "institution_name": {"type": "string", "nullable": True},
                            "institution_course": {"type": "string", "nullable": True},
                            "institution_date": {"type": "string", "nullable": True},
                        },
                    },
                },
                "experience": {
                    "type": "array",
                    "nullable": True,
                    "items": {
                        "type": "object",
                        "properties": {
                            "workplace_name": {"type": "string", "nullable": True},
                            "workplace_position": {"type": "string", "nullable": True},
                            "workplace_date": {"type": "string", "nullable": True},
                            "workplace_details": {
                                "type": "array",
                                "nullable": True,
                                "items": {"type": "string"},
                            },
                        },
                    },
                },
                "projects": {
                    "type": "array",
                    "nullable": True,
                    "items": {
                        "type": "object",
                        "properties": {
                            "project_name": {"type": "string", "nullable": True},
                            "project_date": {"type": "string", "nullable": True},
                            "project_tech_stack": {
                                "type": "array",
                                "nullable": True,
                                "items": {"type": "string"},
                            },
                            "project_details": {
                                "type": "array",
                                "nullable": True,
                                "items": {"type": "string"},
                            },
                        },
                    },
                },
                "skills": {
                    "type": "array",
                    "nullable": True,
                    "items": {"type": "string"},
                },
                "links": {
                    "type": "array",
                    "nullable": True,
                    "items": {"type": "string"},
                },
                "notable_things_and_acheivements": {
                    "type": "array",
                    "nullable": True,
                    "items": {"type": "string"},
                },
            },
        },
    }

    client = genai.Client(api_key=values["MODEL_API_KEY"])
    tools = types.Tool(function_declarations=[resume_details_function])
    config = types.GenerateContentConfig(tools=[tools])
    response = client.models.generate_content(
        model=values["MODEL"],
        contents=f"Extract the details from the resume text provided below:\n\n{extracted_text}",
        config=config,
    )
    json_to_dict = response.candidates[0].content.parts[0].to_json_dict()

    return json_to_dict["function_call"]["args"]


if __name__ == "__main__":
    app.run(debug=True)
