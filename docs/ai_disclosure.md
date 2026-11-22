# AI tool disclosure

OpenAI Codex was used as a coding assistant in this project to plan the architecture, draft application modules, tests, synthetic sample-generation code, evaluation scripts, and documentation. Codex also ran the listed commands and helped debug failures. The developer should review and understand the implementation before submission; this work should not be represented as unaided authorship.

The ten invoice PDFs and two policy text fixtures were generated locally from synthetic data. No employer assessment PDF, personal records, resumes, or third-party documents were sent to an LLM. The assessment PDF was read locally to map requirements. The optional OpenAI-compatible LLM client has no endpoint configured in this environment, so no LLM generation or extraction call has been made. The MiniLM embedding model was downloaded from Hugging Face and runs locally; document content used for embedding is not sent to that provider.
