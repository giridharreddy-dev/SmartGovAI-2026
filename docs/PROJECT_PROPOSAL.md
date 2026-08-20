# SmartGovAI: An Offline-First, AI-Assisted Welfare Discovery Platform for Rural India

## Abstract
Access to government health and welfare schemes in rural India is impeded by language barriers, complex bureaucratic terminology, and unreliable internet connectivity. This project proposes and implements **SmartGovAI**, an offline-first Progressive Web Application (PWA) designed to mitigate these challenges. By combining an offline-capable Telugu-first interface, pre-cached auditory accessibility, and optional generative AI (Google Gemini) for document simplification, the system provides a localized, privacy-aware framework for welfare discovery.

## Background
India's digital public infrastructure is vast, but last-mile access remains challenging for populations with low digital literacy. Centralized welfare portals often assume high-bandwidth connectivity and English proficiency, alienating rural demographics.

## Problem Statement
How can modern web architectures and generative AI be combined to create a resilient, privacy-preserving, and linguistically accessible tool for rural citizens to navigate government welfare policies?

## Motivation
Bridging the digital divide requires more than simple translation; it requires architectural paradigms (offline-first) and user experience designs (audio-first, simplified logic) tailored specifically to the target demographic's operational realities.

## Objectives
1. Build a robust offline-first catalog of welfare schemes.
2. Prioritize Telugu language localization and auditory support.
3. Ensure client-side privacy for personal eligibility checks.
4. Experiment with generative AI to simplify complex PDF policy documents.

## Research Questions
1. Does an offline-first architecture significantly improve access for rural users with intermittent connectivity compared to standard web portals?
2. How does a Telugu-first interface with pre-cached audio affect comprehension of complex welfare eligibility logic?
3. To what extent can RAG (Retrieval-Augmented Generation) grounded in local datasets accurately answer citizen queries without hallucination?

## Target Users
- Rural citizens in Andhra Pradesh.
- Individuals with limited literacy.
- Community health workers (ASHAs/ANMs).

## Existing Solution Gap
Current solutions are heavily centralized, require persistent internet, store PII on remote servers, and lack integrated, localized audio support for complex policy documents.

## Proposed Solution
A decoupled client-server architecture utilizing Service Workers for offline resilience, `localStorage` for privacy, and optional cloud-based AI for advanced document comprehension.

## Current Implementation
The repository contains a fully implemented functional prototype featuring:
- **Offline PWA Cache**: Fully operational scheme browsing without a network.
- **Eligibility Evaluator**: Localized, boolean-based checklists.
- **RAG AI Chat**: A Gemini-powered assistant grounded in local data.
- **Audio Pre-caching**: `gTTS` generated MP3s for all schemes.

## System Architecture
- **Client**: HTML5, CSS3, Vanilla JS, Service Worker.
- **Server**: Python 3.10, Flask, SQLite.
- **AI Integration**: Google Gemini API via `google-genai` SDK.
- **Geospatial**: Leaflet.js with Haversine distance calculations.

## Technology Stack
- Python, Flask, Pytest
- JavaScript, HTML, CSS
- Google Gemini API, gTTS, PDFPlumber, Tesseract OCR

## AI Components
- **PDF Simplification**: Extracts text using PDFPlumber/OCR, sends to Gemini for summarization into plain Telugu.
- **RAG Chat**: Matches user queries to local scheme schemas using term-overlap, passing the context to Gemini to answer questions securely.

## Accessibility
Implemented via pre-generated MP3 audio caching, allowing text-to-speech functionality without runtime latency or internet dependencies.

## Offline-First Strategy
The Service Worker intercepts network requests and serves the application shell, localized JSON data, and MP3 files from the browser cache.

## Security/Privacy
- **Zero-Trust Client**: Eligibility answers are never transmitted to the server.
- **CSRF/CSP**: Robust security headers mitigate cross-site scripting and request forgery.

## Community Benefits
*(Proposed)*
- Reduces reliance on intermediaries for basic information.
- Empowers health workers with immediate field references.

## Academic Contribution
Demonstrates a practical implementation of graceful degradation in AI applications, ensuring that failure or absence of the AI API defaults to a functional, deterministic local search rather than application failure.

## Scope
Currently limited to a predefined subset of Andhra Pradesh health and welfare schemes.

## Limitations
- Static data requires manual JSON updates.
- AI features are entirely dependent on internet access.
- Not yet validated with real rural users.

## Evaluation Methodology
*(Proposed)*
A mixed-methods approach combining server telemetry (offline cache hits vs. online requests) with qualitative field surveys of community health workers.

## Future Work
- Migration to a dynamic CMS backend.
- Expansion to multiple regional languages.
- Asynchronous queuing for heavy PDF processing tasks.

## Conclusion
SmartGovAI provides a technically sound foundational architecture for localized, offline-resilient civic technology. Future field pilots are required to validate its real-world efficacy.
