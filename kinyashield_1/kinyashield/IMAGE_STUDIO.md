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

## Many people at once, and honest limits
- **Shared cache:** the same request (same words, style and shape) is answered from memory and uses no provider quota.
- **Lanes with circuit breakers:** every Gemini key, Hugging Face token/model and image server is its own lane. A lane that is out of quota or failing is skipped for a growing cool-down while the others keep working; load is rotated evenly over all lanes.
- **Queue:** at most `IMAGE_MAX_CONCURRENT` pictures are made at the same moment; others wait in a bounded line and see "try again" instead of crashing the app.
- **Fair use:** per-visitor limits (`IMAGE_PER_MINUTE`, `IMAGE_PER_HOUR`) and an optional app-wide cap (`IMAGE_GLOBAL_PER_MINUTE`).
- **Memory:** each visitor keeps only their newest pictures.
- **Limits you cannot code away:** pictures per minute are decided by your provider quotas (number of keys and plans) and the server size. Streamlit Community Cloud is a small shared server; for a thousand people at once, add many keys/services (above) and move to a bigger host.

## Real photos from the internet
"Find real photos online" searches **Wikimedia Commons, Openverse** (no key) and, with free keys, **Pixabay, Pexels, Unsplash** in parallel, with short time-outs, a one-hour shared cache and cool-downs for a failing source. Each photo shows creator, licence and a link to its page. Pictures are linked, not copied through the server.
It is a licensed-image search, **not** a scraper of every website: copying pictures from arbitrary pages would break licences, so it does not do that.

