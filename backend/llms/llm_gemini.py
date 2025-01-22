from vertexai.generative_models import GenerativeModel
import vertexai
from backend.llms.llm_protocol import LLMProtocol


import json
import os
import sys

sys.path.insert(0, '.')


class LLMGemini(LLMProtocol):
    def __init__(self, config=None):
        self.name = 'LLMGemini'
        # if config == None:
        #     config = json.load(open('config.json', 'rt'))[self.name]
        # self.config = config
        # vertexai.init(project='clasificationfromdescription',
        #           location='europe-west2')

        # vertexai.init(
        #     project=self.config["gcp_project_id"], location=config["location"])
        self.backend = GenerativeModel("gemini-1.5-pro")

    def process_request(self, message):

        response = self.backend.generate_content(message)

        return response

    def log(self):
        raise NotImplementedError


if __name__ == "__main__":
    """Authenticate first gcloud auth application-default login --impersonate-service-account ia-vertex-ai-pipeline@db-dev-o3zl-afbc-bdc.iam.gserviceaccount.com

    """
    llm_gemini = LLMGemini()
    print(llm_gemini.process_request('why is six afraid of seven ?').text)
