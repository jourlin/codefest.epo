# PATCHAT : a simple Retrieval-Augmented Generation AI System for Medical Device Patent Analysis
# to be submitted to EPO's codefest competition on october 23, 2024

**(c) Pierre Jourlin**
__Avignon University__
__Laboratoire d’informatique d’Avignon (LIA)__
__September 22, 2024__

## Overview
The proposed project aims to develop a Retrieval-Augmented Generation (RAG) AI system designed to enhance the patent exploring and drafting process in the medical device industry. The system leverages the Unified Medical Language System (UMLS) concepts and their textual forms for semantic mapping of medical terms, the Llama 3 Large Language model (LLM) for natural language "understanding" and generation, and a document set composed of patents related to medical devices. The primary function of the system is to identify and present the most relevant patents in EPO database that closely match the user's query. The secondary function of the system is to provide a chatbot to question the information contained in the selected patent documentation.

## Testing without installing

Open a browser at http://jourlin.ddns.net:5000
It should be active from october 23th 2024 to december 31th 2024 during working hours, let say from 10am to 18am.

## Installation
See [INSTALL.md](./docs/INSTALL.md)

## Test
See [USER_GUIDE.md](./docs/USER_GUIDE.md)

## Files short descriptions
See [FILES_DESC.md](./docs/FILES_DESC.md)



