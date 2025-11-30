# Quick Start Guide

Get up and running with the CUSIP Financial Analyzer in 5 minutes.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Get Your API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

## Step 3: Run the App

```bash
streamlit run app.py
```

This opens your browser at `http://localhost:8501`

## Step 4: Use the App

1. **Enter API Key**: Paste your Google AI Studio API key in the sidebar
2. **Enter CUSIP**: Type a 9-character CUSIP (e.g., `912828Z29`)
3. **Click Analyze**: Wait 10-30 seconds for results
4. **View Results**: See financial attributes, WAM calculation, and sources

## Example CUSIPs to Try

- `912828Z29` - U.S. Treasury Security
- `037833100` - Apple Inc. Bond
- `594918104` - Microsoft Corp Bond

## Programmatic Usage

```python
from src.services.gemini_client import GeminiClient
from src.services.pipeline import CUSIPPipeline

# Initialize
gemini_client = GeminiClient(api_key="your-api-key")
pipeline = CUSIPPipeline(gemini_client=gemini_client)

# Query CUSIP
result = pipeline.process_cusip(cusip="912828Z29")

# Access results
print(result.attributes)
print(f"WAM: {result.wam_years} years")
print(result.sources)
```

## Troubleshooting

**"Invalid API Key"**
- Make sure you copied the full API key
- Check that it's from Google AI Studio (not Google Cloud)

**"CUSIP not found"**
- Verify the CUSIP is correct (9 characters)
- Some CUSIPs may have limited public data

**"Pipeline initialization failed"**
- Check your internet connection
- Verify the API key is valid
- Check if you've exceeded rate limits

## Next Steps

- Read the [full README](README.md) for detailed documentation
- Check [example_usage.py](example_usage.py) for programmatic examples
- Customize attributes in the "Advanced Options" section
- Explore the modular codebase in the `src/` directory

## Support

For issues, check:
1. The error message in the UI
2. The raw LLM response (expand to view)
3. Your API key validity
4. CUSIP format (must be exactly 9 alphanumeric characters)
