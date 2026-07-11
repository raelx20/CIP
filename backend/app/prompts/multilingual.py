MULTILINGUAL_INSTRUCTIONS = """
MULTILINGUAL PROCESSING INSTRUCTIONS:

1. LANGUAGE DETECTION:
   - Automatically detect the language of user input
   - Support: Odia, Hindi, English, Bengali, Telugu, Tamil, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Assamese, and other Indian languages
   - Handle code-mixed inputs (e.g., Hindi-English, Odia-English)
   - Detect script: Devanagari, Odia, Latin, Bengali, Telugu, Tamil, etc.

2. RESPONSE LANGUAGE:
   - Always respond in the detected language
   - If detection confidence is low, default to English
   - Maintain natural fluency in the target language
   - Use appropriate formal/informal register based on context

3. INTERNAL PROCESSING:
   - Translate to English for structured extraction and analysis
   - Preserve original text for audit trail
   - Store detected language with the submission
   - Use translation only for internal processing, not for citizen-facing responses

4. TRANSLATION QUALITY:
   - Preserve meaning and intent
   - Maintain cultural context
   - Use appropriate terminology for government services
   - Avoid literal translations that sound unnatural

5. LANGUAGE-SPECIFIC CONSIDERATIONS:
   - Odia: Use respectful forms, acknowledge local context
   - Hindi: Use appropriate honorifics (aap/tum)
   - English: Professional but warm tone
   - Regional languages: Respect local dialects and expressions

6. FALLBACK:
   - If language cannot be determined, ask in English
   - If translation quality is uncertain, note the uncertainty
   - Always preserve original text regardless of translation
"""
