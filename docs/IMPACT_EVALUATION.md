# Impact Evaluation Plan

*Note: This document proposes a methodology for future field validation. The targets and metrics discussed below are PROPOSED TARGETS — NOT YET EVALUATED.*

## Research Questions
1. Does the offline-first architecture of SmartGovAI significantly improve information access speed in low-bandwidth rural environments compared to standard centralized portals?
2. Does Telugu localization and auditory synthesis improve objective comprehension of eligibility rules for citizens with limited digital literacy?
3. How accurately does the Gemini-powered RAG chat answer citizen questions without generating hallucinated eligibility claims?

## Hypotheses
- **H1:** Users utilizing the offline PWA will experience zero network-related failures during core catalog navigation.
- **H2:** Pre-cached audio instructions will reduce the time taken for a user to identify required documents by at least 30%. *(Proposed target — not yet evaluated)*

## Participants
- **Target Size:** 30 rural households and 5 community health workers (ASHAs).
- **Recruitment:** Selected via coordination with local NGOs in Andhra Pradesh.
- **Criteria:** Basic smartphone ownership, Telugu as a primary language, varied digital literacy levels.

## Experimental Conditions
- **Control Group (Baseline):** Navigating official English/Telugu government web portals via standard mobile browser.
- **Test Group:** Utilizing the locally installed SmartGovAI PWA.

## Tasks
1. Identify the nearest Primary Health Centre.
2. Determine eligibility for the "Dr. YSR Aarogyasri" scheme.
3. List the documents required for application.
4. Upload a mock policy PDF for simplification (Internet required condition).

## Metrics
### Quantitative
- **Task Completion Time:** Time from prompt to correct answer identification.
- **Error Rate:** Instances of incorrect eligibility self-assessment.
- **Offline Cache Hits:** Ratio of requests served by the Service Worker vs. network fetches.

### Qualitative
- System Usability Scale (SUS) scores adapted for Telugu.
- Semi-structured interviews regarding trust in the AI-simplified text.

## Specific Evaluations
- **AI Accuracy Evaluation:** 50 predetermined edge-case questions fed to the RAG chat. Responses evaluated by domain experts for hallucination and accuracy.
- **Usability Evaluation:** Field observation of first-time navigation without guidance.
- **Accessibility Evaluation:** Measuring the utilization rate of the "Read Aloud" auditory feature.
- **Offline Evaluation:** Conducting tasks with the device actively placed in Airplane Mode.

## Ethical Considerations & Consent
- Explicit, recorded verbal consent from all participants.
- **Privacy:** Strict adherence to zero-data collection. No real PII or actual identification documents will be used during the evaluation (mock data only).

## Proposed Success Criteria
- *Proposed target — not yet evaluated:* 85% task completion rate in the Test Group vs. anticipated 50% in the Control Group.
- *Proposed target — not yet evaluated:* Zero PII leakage incidents.

## Limitations
- The evaluation requires significant logistical coordination.
- Results in one village may not generalize to other districts with different infrastructural realities.
