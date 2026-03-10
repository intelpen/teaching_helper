import json
import os
import sys

import vertexai
from google.api_core.exceptions import NotFound, PermissionDenied
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel

from backend.llms.llm_protocol import LLMProtocol

sys.path.insert(0, '.')


class LLMGemini(LLMProtocol):
    def __init__(self, config=None):
        self.name = 'LLMGemini'
        if config is None:
            with open('backend/config.json', 'rt', encoding='utf-8') as config_file:
                config = json.load(config_file)[self.name]
        self.config = config

        self.project_id = os.getenv('GCP_PROJECT', self.config.get('gcp_project_id'))
        if not self.project_id:
            raise ValueError('Missing GCP project id. Set GCP_PROJECT or LLMGemini.gcp_project_id.')

        self.credentials = self._load_credentials(self.config.get('credentials'))
        self.model_candidates = self._build_candidates(
            os.getenv('GEMINI_MODEL', self.config.get('model_name', 'gemini-2.0-flash')),
            self.config.get('fallback_models'),
            ['gemini-2.0-flash', 'gemini-2.0-flash-001', 'gemini-1.5-flash-001'],
        )
        self.location_candidates = self._build_candidates(
            os.getenv('GCP_REGION', self.config.get('location', 'us-central1')),
            self.config.get('fallback_locations'),
            ['us-central1', 'europe-west4', 'global'],
        )

        self.backend = None
        self._active_pair = None

    @staticmethod
    def _build_candidates(preferred, fallback_values, default_values):
        values = []
        seen = set()

        candidates = [preferred]
        if fallback_values:
            candidates.extend(fallback_values)
        candidates.extend(default_values)

        for candidate in candidates:
            if not candidate:
                continue
            value = str(candidate).strip()
            if value and value not in seen:
                seen.add(value)
                values.append(value)
        return values

    @staticmethod
    def _load_credentials(credentials_path):
        if not credentials_path:
            return None
        return service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )

    def _init_backend(self, location, model_name):
        vertexai.init(
            project=self.project_id,
            location=location,
            credentials=self.credentials,
        )
        self.backend = GenerativeModel(model_name)
        self._active_pair = (location, model_name)

    def _candidate_pairs(self):
        pairs = []
        for location in self.location_candidates:
            for model_name in self.model_candidates:
                pairs.append((location, model_name))
        return pairs

    def process_request(self, message):
        response = {}
        attempted = []
        last_model_error = None

        for location, model_name in self._candidate_pairs():
            try:
                if self._active_pair != (location, model_name):
                    self._init_backend(location, model_name)
                response['text'] = self.backend.generate_content(message).text
                return response
            except (NotFound, PermissionDenied) as exc:
                attempted.append(f'{model_name}@{location}')
                last_model_error = exc
                continue

        attempts = ', '.join(attempted) if attempted else 'none'
        reason = f' Last model error: {last_model_error}' if last_model_error else ''
        raise RuntimeError(
            f'No accessible Gemini model found. Tried: {attempts}.'
            ' Set LLMGemini.model_name/location (or GEMINI_MODEL/GCP_REGION) to a model'
            ' version available in your Vertex AI project/region.'
            f'{reason}'
        )

    def log(self):
        raise NotImplementedError


if __name__ == "__main__":
    llm_gemini = LLMGemini()
    print(llm_gemini.process_request('why is six afraid of seven ?')['text'])
