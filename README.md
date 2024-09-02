# codefest.epo

# Project Description: Hybrid Retrieval-Augmented Generation AI System for Medical Device Patent Analysis

(c) Pierre Jourlin
Avignon University
Laboratoire d’informatique d’Avignon (LIA)
August 5, 2024

## Overview

The proposed project aims to develop a hybrid Retrieval-Augmented Generation (RAG) AI system designed to enhance the patent drafting process in the medical device industry. The system leverages the Unified Medical Language System (UMLS) as a knowledge graph for semantic mapping of medical terms, the Biomistral large language model (LLM) for natural language understanding and generation, and a document set composed of patents related to medical devices. The primary function of the system is to identify and present the most relevant passages from the patent database that closely match a provided patent draft.

## System Components

1. Unified Medical Language System (UMLS): 
       
       UMLS is utilized as the foundational knowledge graph to map medical terms into standardized semantic entities. This allows for a consistent and comprehensive understanding of medical terminologies, enabling the system to accurately interpret the content of patent drafts and existing patents. UMLS's rich semantic network facilitates the identification of synonyms, hierarchical relationships, and other relevant associations between medical concepts.

2. Biomistral Large Language Model: 
       
       Biomistral, a state-of-the-art large language model, serves as the core component for natural language processing tasks. It is responsible for « understanding » the context and intent behind the text in patent drafts and existing patents. The model's advanced capabilities in language understanding and generation allow it to handle complex medical and technical language, ensuring high-quality analysis and matching.
       
3. Patent Database:
       
   The system's database consists of a curated collection of patents specifically focused on medical devices. This dataset is continually updated to include the latest developments and innovations in the field. The comprehensive nature of the database ensures that the system can provide relevant and up-to-date information to users.

## Functionality

The system is designed to perform the following key functions:

1. Patent Draft Analysis: 
       
       Upon receiving a patent draft, the system first preprocesses the text to identify and extract relevant medical and technical terms. Using UMLS, these terms are mapped to their corresponding semantic entities, ensuring a consistent understanding of the content.
       
2. Semantic Retrieval : 
       
       The system utilizes the semantic mappings to query the patent database. By leveraging both the semantic knowledge from UMLS and the language understanding capabilities of Biomistral, the system retrieves passages from existing patents that are semantically closest to the content of the provided draft. This hybrid retrieval process ensures that the returned results are not only relevant in terms of keywords but also in context and meaning.
       
3. Result Presentation:
       
       The system presents a ranked list of the most relevant patent passages to the user. Each passage is accompanied by metadata, including the patent number, title, and a brief summary. This information helps the user quickly assess the relevance of each result and facilitates further exploration.

## Applications

The proposed system has several potential applications in the medical device industry:

- Patent Drafting:
      By providing relevant prior art, the system assists inventors and patent attorneys in crafting more robust and comprehensive patent drafts, potentially increasing the chances of approval.
      
- Prior Art Search:
      The system aids in identifying existing patents that may be relevant to a new invention, helping to avoid potential infringement issues.
      
- Innovation Tracking:
      Researchers and companies can use the system to monitor recent developments in specific areas of medical devices, keeping them informed of the latest innovations and trends.

## Conclusion

The proposed hybrid RAG AI system represents a significant advancement in the field of intellectual property management, particularly for the medical device industry. By integrating cutting-edge technologies in natural language processing and semantic mapping, the system offers an efficient and accurate solution for patent analysis. It promises to streamline the patent drafting process, enhance the quality of patent applications, and support innovation in the medical device sector.
