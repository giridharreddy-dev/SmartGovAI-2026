# SmartGovAI — Demo Script

**Estimated Time:** 5-10 minutes
**Audience:** Academic Professors / Project Evaluators
**Requirement:** Smartphone or laptop with a local instance of the application running. Internet required for Steps 9 & 10 only.

## 1. Problem (30 sec)
*Speaker:* "Accessing government welfare in rural India is hard. Citizens face language barriers, complex bureaucratic texts, and unreliable internet. Today, we're demonstrating SmartGovAI, an academic prototype built to solve these exact problems using an offline-first architecture and targeted AI."

## 2. Target Users (30 sec)
*Speaker:* "Our target users are rural Telugu-speaking citizens, elderly populations, and the community health workers (ASHAs) who assist them. They need fast, reliable, and private access to information."

## 3. Open Application
*Action:* Open `localhost:5000` (or local network IP on mobile).
*Speaker:* "Here is the application shell. It is a Progressive Web Application (PWA). Once loaded, the core app is cached entirely."

## 4. Telugu Interface
*Action:* Show the language toggle.
*Speaker:* "The interface defaults to Telugu. It is not an afterthought or an auto-translation widget; it is the primary language of the application."

## 5. Scheme Discovery
*Action:* Scroll through the main page.
*Speaker:* "Users can filter schemes by category—health, maternity, or pediatrics. Notice the speed; this data is loaded from a local JSON structure, not a remote database."

## 6. Scheme Details
*Action:* Click on "Dr. YSR Aarogyasri" (or similar scheme).
*Speaker:* "Inside, we see the benefits and requirements. Notice the provenance details showing the last verified date and the official website."

## 7. Eligibility
*Action:* Scroll to the Eligibility Check section.
*Speaker:* "Instead of reading a long PDF, citizens answer simple 'Yes/No' questions in Telugu. Let's select a few."
*Action:* Toggle the checkboxes.
*Speaker:* "The system instantly evaluates basic eligibility locally. No data is sent to a server, preserving user privacy."

## 8. Document Checklist
*Action:* Show the generated checklist below the eligibility evaluator.
*Speaker:* "Based on the scheme, it generates an interactive document checklist, so citizens know exactly what to bring to the office."

## 9. AI Assistant (Internet Required)
*Action:* Open the Chat interface (bottom right).
*Speaker:* "If they have a specific question, they can use our AI Chat. This requires internet. It uses Retrieval-Augmented Generation (RAG). Watch what happens if I ask about maternity benefits."
*Action:* Type a question in Telugu or English.
*Speaker:* "The system retrieves the relevant scheme context and constrains the Gemini API to answer *only* based on our verified local data."

## 10. PDF Simplification (Internet Required)
*Action:* Go to the "Simplify Document" section and upload a mock complex PDF.
*Speaker:* "Bureaucratic PDFs are hard to read. Here, we upload a PDF. Our Python backend extracts the text (with OCR fallback) and Gemini translates and simplifies it into plain Telugu."

## 11. Audio
*Action:* Click the "Read Aloud" button on a scheme page.
*Speaker:* "For users with limited literacy, we provide audio. This isn't live TTS that fails on bad networks. These MP3s were pre-generated and cached on the device."

## 12. Offline Functionality
*Action:* Turn off Wi-Fi/Ethernet on the presentation device. Refresh the page.
*Speaker:* "Let's turn off the internet. I refresh the page. The application still loads. I can browse schemes, check eligibility, and listen to the audio. Only the AI chat and PDF upload are disabled."

## 13. Healthcare Facilities
*Action:* Re-enable internet. Navigate to the local facilities map.
*Speaker:* "We also integrated a Leaflet map. It loads over 1,480 local AP healthcare facilities and calculates the nearest one to the user's GPS."

## 14. Sharing/QR
*Action:* Click the WhatsApp share button and show the QR code.
*Speaker:* "Health workers can easily share this localized information via pre-formatted WhatsApp messages or by showing a dynamically generated QR code."

## 15. Privacy/Security
*Speaker:* "To reiterate, all eligibility checks happen in the browser's `localStorage`. We've implemented CSRF, CSP, and strict rate-limiting on the backend."

## 16. Community Impact
*Speaker:* "While this is a prototype, it demonstrates a feasible architecture for empowering citizens, reducing confusion at government offices, and assisting field workers."

## 17. Limitations
*Speaker:* "We must be honest about limitations: we have not yet tested this with actual rural users, the AI still carries a minor hallucination risk, and our data must be manually updated."

## 18. Conclusion & Future Work
*Speaker:* "SmartGovAI proves that civic tech can be accessible, offline-resilient, and AI-enhanced. Our next steps involve real-world validation and expanding the dataset. Thank you."
