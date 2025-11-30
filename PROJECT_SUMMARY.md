# CUSIP Financial Information Finder - Project Summary

## Overview

A production-ready, modular application for extracting comprehensive financial information from CUSIP securities using Google Gemini 2.0 with dual search capabilities (Gemini Search Grounding and Custom Search API).

## Key Features

### 1. Dual Search Modes
- **Gemini Search Grounding**: AI autonomously searches the web and extracts data
- **Custom Search API**: Pre-fetch results using Google Custom Search for controlled searches
- Seamless switching between modes via UI
- Source merging from both search methods

### 2. Flexible Attribute Extraction
- Dynamic schema generation based on user requests
- Ask for any financial attribute (not limited to pre-defined fields)
- Common attributes:
  - Maturity dates
  - Coupon rates and yields
  - Credit ratings
  - Issuer information
  - Security types
  - Par values
  - And more...

### 3. Comprehensive Tracing
- Step-by-step processing visibility
- Clear distinction between Custom Search and Gemini operations
- Numbered steps (STEP 1, 2, 3, etc.)
- Source URLs for verification

### 4. User-Friendly Interface
- Clean Streamlit UI
- Dual API key support (Gemini + Custom Search)
- Flexible attribute input
- Detailed results with source citations
- Raw LLM response viewer

## Architecture

### Core Modules

#### 1. Data Models (`src/models/`)
- **schemas.py**: Defines data structures
  - `CUSIPAnalysisResult`: Main result object
  - `FinancialAttributeData`: Individual attribute data
  - `MaturityData`: Maturity schedule data (for WAM calculation)

#### 2. Services (`src/services/`)
- **gemini_client.py**: Gemini API client with dual search support
  - Manages both search modes
  - Custom Search API integration
  - Dynamic prompt building
  - Source extraction and merging
  - Simplified code structure

- **pipeline.py**: Processing pipeline
  - Orchestrates query flow
  - Parses LLM responses (JSON and text fallback)
  - Error handling with graceful degradation

#### 3. Utilities (`src/utils/`)
- **validators.py**: CUSIP validation
  - Format checking
  - Length validation
  - Character validation

#### 4. Frontend (`app.py`)
- Streamlit UI
- Session state management
- Search mode configuration
- Results display with structured traces
- Simplified display functions

## Pipeline Flow

```
User Input (CUSIP + Attributes + Search Mode)
    ↓
CUSIP Validation
    ↓
    ┌─────────────────┐
    │  Search Phase   │
    ├─────────────────┤
    │ Custom Search   │──→ Pre-fetch results
    │      OR         │
    │ Gemini Search   │──→ AI-driven search
    └─────────────────┘
    ↓
Dynamic Prompt Construction
    ↓
Gemini API (2.0 Flash)
    ↓
Pipeline Processing
    ↓
    ├─→ JSON Parsing (preferred)
    └─→ Text Extraction (fallback)
    ↓
Source Extraction & Merging
    ↓
Result Assembly
    ↓
Display with Structured Trace
```

## Search Strategy

### Gemini Search Grounding (Default)
**Workflow:**
1. User specifies CUSIP and attributes
2. Gemini performs autonomous web search
3. AI extracts data from search results
4. Sources from grounding metadata

**Advantages:**
- No additional API keys required
- AI-driven result selection
- Fast and simple
- Single API call

### Custom Search API
**Workflow:**
1. Pre-fetch results from Google Custom Search
2. Embed results in Gemini prompt as context
3. Gemini extracts from provided results
4. Sources from both Custom Search and grounding

**Advantages:**
- Fine-grained control over search
- Configurable via Custom Search Engine
- Can restrict to specific domains
- Compliance-friendly

## Data Flow

### Input
- CUSIP number (9 alphanumeric characters)
- Custom attribute list (user-specified)
- Search mode selection
- API keys

### Processing
1. Validate CUSIP format
2. Execute search (Custom or Gemini)
3. Build dynamic prompt with search context
4. Query Gemini with structured schema
5. Parse response (JSON preferred, text fallback)
6. Extract and merge sources
7. Assemble result

### Output
- Financial attributes dictionary (dynamic)
- Source URLs (deduplicated)
- Comprehensive processing trace
- Raw LLM response
- Error messages (if any)

## File Structure

```
cusip-financial-information-finder/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py              # Data models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_client.py        # Gemini + Custom Search client
│   │   └── pipeline.py             # Processing pipeline
│   └── utils/
│       ├── __init__.py
│       └── validators.py           # Validation utilities
├── tests/
│   ├── __init__.py
│   └── test_validators.py          # Unit tests
├── assets/
│   ├── Main Interface.png          # Screenshots
│   └── Results.png
├── app.py                          # Streamlit frontend
├── example_usage.py                # Programmatic examples
├── requirements.txt                # Dependencies
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
├── README.md                       # Full documentation
├── QUICKSTART.md                   # Quick start guide
├── ARCHITECTURE.md                 # Architecture diagrams
└── PROJECT_SUMMARY.md              # This file
```

## Technology Stack

- **Python 3.8+**
- **Streamlit**: Web UI framework
- **google-genai**: New Gemini API SDK
- **Google Gemini 2.0 Flash**: LLM with search grounding
- **requests**: HTTP library for Custom Search API
- **Google Custom Search API**: Optional controlled search

## Design Principles

### 1. Simplicity
- Simplified code structure using modern Python features
- Condensed helper functions
- Clean error handling
- Minimal redundancy

### 2. Flexibility
- Dynamic attribute extraction (ask for anything)
- Dual search modes for different use cases
- User-configurable search preferences
- No hardcoded credentials

### 3. Transparency
- Comprehensive step-by-step tracing
- Clear source citations
- Raw response visibility
- Distinction between search modes

### 4. Reliability
- Input validation
- Robust error handling
- Fallback parsing strategies
- Graceful degradation

## Usage Modes

### 1. Web UI (Streamlit)
- User-friendly interface
- No coding required
- Interactive results
- Search mode switching
- Perfect for analysts

### 2. Programmatic API
- Python library usage
- Batch processing
- Integration into workflows
- Custom applications

### 3. Custom Attributes
- Specify any financial field
- Dynamic schema generation
- Optimize for specific needs
- Flexible extraction

## Code Simplifications

Recent improvements include:
- Condensed `_perform_custom_search()` from 81 to 49 lines
- Simplified `_extract_sources()` using list comprehension
- Streamlined `display_result()` with walrus operator
- Cleaner pattern matching in attribute extraction
- Reduced code duplication across modules

## Testing

Currently includes:
- Unit tests for validators
- Example usage scripts

To run tests:
```bash
python -m pytest tests/
```

## Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Cloud Deployment
- **Streamlit Cloud**: One-click deployment from GitHub
- **Heroku**: Container-based deployment
- **Google Cloud Run**: Serverless containers
- **AWS ECS**: Full container orchestration

## Performance

- **Query Time**: 5-15 seconds per CUSIP (varies by search mode)
- **Rate Limits**: Based on Google AI Studio and Custom Search API tiers
- **Accuracy**: Depends on publicly available sources

## Security Considerations

- API keys stored in session only (not persisted)
- No sensitive data logged
- HTTPS recommended for production
- Input validation prevents injection
- Separate API keys for different services

## Best Practices

1. **Validate CUSIP** before querying
2. **Review sources** for data accuracy
3. **Check raw response** if results seem unexpected
4. **Use appropriate search mode** for your use case
5. **Monitor API usage** to avoid rate limits
6. **Configure Custom Search Engine** for domain restrictions if needed

## Future Enhancements

### Potential Improvements
1. **Caching**: Store results to reduce API calls
2. **Batch Processing**: Query multiple CUSIPs at once
3. **Export**: Download results as CSV/Excel
4. **Historical Tracking**: Monitor changes over time
5. **Multi-Model**: Fallback to other LLMs
6. **Enhanced PDF Parsing**: Better document extraction
7. **Rate Limiting**: Handle API quotas gracefully
8. **Data Validation**: Cross-check multiple sources

### Scaling Considerations
- Add database for result persistence
- Implement job queue for batch processing
- Deploy as containerized web service
- Add authentication for multi-user access
- Implement result caching layer

## Conclusion

This project demonstrates a **clean, flexible approach** to building LLM-powered financial data extraction tools. It prioritizes:
- Code simplicity and maintainability
- User control and transparency
- Dual search mode flexibility
- Comprehensive tracing
- Reliable extraction

The architecture makes it easy to:
- Extract any financial attribute
- Switch between search modes
- Understand exactly what happened
- Integrate into larger systems
- Deploy to production

Perfect for financial analysts, developers, and researchers who need flexible, transparent access to CUSIP data with the power of modern LLMs and search capabilities.
