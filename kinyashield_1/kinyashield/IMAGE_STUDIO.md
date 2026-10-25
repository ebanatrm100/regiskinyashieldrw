# Image Studio, photo and file uploads

**Create pictures:** Image Studio tab (describe, style, shape, 1-3 pictures, optional reference photo, download) and chat requests such as
`draw a cat on a roof`, `génère une image de ...`, `kora ishusho y'inka`, `tengeneza picha ya simba`. Requests to *show existing photos*
(`photos of lions`) still return real Wikimedia Commons photos.

**Needs one provider in Secrets** (see `deploy/secrets.example.toml`): a Gemini key (image model), `HF_TOKEN`, an OpenAI-compatible
`IMAGE_BASE_URL` + `IMAGE_MODEL`, or the free keyless public service (Pollinations), which is ON by default as the last resort (`IMAGE_ALLOW_PUBLIC=false` turns it off; only the prompt text is sent). Several Gemini image models are tried in turn, and when everything fails the app now shows the real reason (quota, model not available, service busy) instead of a generic message. If every service fails it is usually a Gemini free-tier quota of 0 for images: add HF_TOKEN or enable billing for the key.

**Upload in chat:** photos (PNG/JPG/WEBP, up to 6 MB) and documents (PDF, Word, TXT, MD, CSV, LOG, up to 10 MB), max 4 files. Photos are understood
by the Gemini engine only; documents work with any configured AI. Files are kept in the session only, never written to disk.

**Safety:** a pre-check refuses requests for fake documents/receipts, sexual content involving minors, weapon making, deepfakes of real people
and look-alike phishing pages. Every generated image carries an AI-generated notice. Quality depends on the provider; images can contain errors.
