# Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface (Streamlit)               │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  API Keys    │  │  CUSIP       │  │  Search Mode │        │
│  │  Input       │  │  + Attributes│  │  Selection   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Results Display & Processing Trace          │ │
│  │  • Financial Attributes  • Sources                       │ │
│  │  • Step-by-step trace   • Raw LLM Response               │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CUSIP Pipeline (Business Logic)            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  CUSIPPipeline                                           │ │
│  │  • Orchestrates processing                               │ │
│  │  • Parses responses (JSON/text)                          │ │
│  │  • Aggregates results                                    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  GeminiClient                                            │ │
│  │  • Manages dual search modes                             │ │
│  │  • Custom Search API integration                         │ │
│  │  • Builds dynamic prompts                                │ │
│  │  • Extracts and merges sources                           │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│  Custom Search API       │  │  Gemini Search Grounding │
│  (Pre-fetch results)     │  │  (AI-driven search)      │
└──────────────────────────┘  └──────────────────────────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               Google Gemini 2.0 Flash API                       │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Context     │→ │  LLM         │→ │  Structured  │        │
│  │  Analysis    │  │  Extraction  │  │  Response    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Data Sources                        │
│                                                                 │
│  • FINRA          • Bloomberg      • SEC EDGAR                  │
│  • Reuters        • Bond Markets   • Financial Databases        │
└─────────────────────────────────────────────────────────────────┘
```

## Component Interaction Flow

```
┌──────────┐
│  User    │
└────┬─────┘
     │ 1. Enter CUSIP + API Keys + Attributes
     ▼
┌──────────────────┐
│  Streamlit UI    │
└────┬─────────────┘
     │ 2. Validate inputs
     ▼
┌──────────────────┐
│  Validators      │
└────┬─────────────┘
     │ 3. Pass validated CUSIP
     ▼
┌──────────────────┐
│  CUSIPPipeline   │──────┐
└────┬─────────────┘      │
     │ 4. Request data    │
     ▼                    │ 8. Parse response
┌──────────────────┐      │    Extract attributes
│  GeminiClient    │      │
└────┬─────────────┘      │
     │ 5a. Custom Search  │
     │     OR             │
     │ 5b. Gemini Search  │
     ▼                    │
┌──────────────────┐      │
│  Search Phase    │      │
│  (Custom/Gemini) │      │
└────┬─────────────┘      │
     │ 6. Build prompt    │
     │    with context    │
     ▼                    │
┌──────────────────┐      │
│  Gemini API      │      │
│  2.0 Flash       │      │
└────┬─────────────┘      │
     │ 7. Structured      │
     │    JSON response   │
     ▼                    │
┌──────────────────┐      │
│  GeminiClient    │◄─────┘
└────┬─────────────┘
     │ 9. Return result + sources
     ▼
┌──────────────────┐
│  CUSIPPipeline   │
└────┬─────────────┘
     │ 10. Format for display
     ▼
┌──────────────────┐
│  Streamlit UI    │
└────┬─────────────┘
     │ 11. Render results + trace
     ▼
┌──────────┐
│  User    │
└──────────┘
```

## Module Dependencies

```
app.py (Streamlit UI)
  │
  ├── src.services.pipeline (CUSIPPipeline)
  │     │
  │     ├── src.services.gemini_client (GeminiClient)
  │     │     ├── google.genai (Gemini API SDK)
  │     │     └── requests (Custom Search API)
  │     │
  │     └── src.models.schemas (Data Models)
  │           ├── CUSIPAnalysisResult
  │           ├── MaturityData
  │           └── FinancialAttributeData
  │
  └── src.utils.validators
        ├── validate_cusip()
        └── format_cusip()
```

## Data Flow

```
Input Stage:
┌─────────────┐
│ CUSIP: str  │
│ API Keys    │
│ Attrs: list │
│ Search Mode │
└──────┬──────┘
       │
       ▼

Search Stage:
┌──────────────────────────┐
│ Dual Search Mode         │
│ • Custom Search API OR   │
│ • Gemini Search Ground   │
└──────┬───────────────────┘
       │
       ▼

Processing Stage:
┌──────────────────────────┐
│ Gemini Query             │
│ • Dynamic prompt build   │
│ • Context incorporation  │
│ • LLM extraction         │
└──────┬───────────────────┘
       │
       ▼

Parsing Stage:
┌──────────────────────────┐
│ Response Parsing         │
│ • JSON extraction        │
│ • Fallback text parse    │
│ • Data validation        │
└──────┬───────────────────┘
       │
       ▼

Output Stage:
┌──────────────────────────┐
│ CUSIPAnalysisResult      │
│ • attributes: dict       │
│ • sources: list          │
│ • error: str|None        │
│ • raw_response: str      │
└──────────────────────────┘
```

## Class Hierarchy

```
Data Models:

@dataclass
FinancialAttributeData
  • attribute_name: str
  • value: Any
  • confidence: str
  • source: str

@dataclass
MaturityData
  • cusip: str
  • maturity_date: str
  • years_to_maturity: float
  • principal_amount: float
  • source: str

@dataclass
CUSIPAnalysisResult
  • cusip: str
  • attributes: Dict[str, Any]
  • sources: List[str]
  • raw_llm_response: str
  • error: str
  • metadata: Dict[str, Any]
```

## Service Layer

```
GeminiClient
  │
  ├── __init__(api_key, model_name, use_custom_search, ...)
  │     • Configure Gemini API
  │     • Set up search mode
  │     • Initialize Custom Search if enabled
  │
  ├── query_cusip_attributes(cusip, attributes, trace_callback)
  │     • Execute search (Custom or Gemini)
  │     • Build dynamic prompt
  │     • Query Gemini with context
  │     • Extract and merge sources
  │     • Return structured response
  │
  ├── _perform_custom_search(query, num_results, trace_callback)
  │     • Call Google Custom Search API
  │     • Parse search results
  │     • Return formatted results
  │
  ├── _build_cusip_query_prompt(cusip, attributes, custom_search_results)
  │     • Build dynamic JSON schema
  │     • Incorporate search results if available
  │     • Add extraction instructions
  │
  └── _extract_sources(response)
        • Parse grounding metadata
        • Extract web URLs
        • Deduplicate and return


CUSIPPipeline
  │
  ├── __init__(gemini_client)
  │     • Store client reference
  │
  ├── process_cusip(cusip, attributes, trace_callback)
  │     • Query Gemini
  │     • Parse response
  │     • Return result with trace
  │
  ├── _parse_gemini_response(cusip, response_data, sources)
  │     • Try JSON parsing
  │     • Fallback to text parsing
  │     • Build result object
  │
  ├── _extract_json_from_response(text)
  │     • Regex JSON extraction
  │     • Clean and parse
  │
  ├── _build_result_from_json(cusip, data, sources)
  │     • Extract attributes
  │     • Handle nested data
  │
  └── _extract_attributes_from_text(text)
        • Pattern matching
        • Attribute extraction
```

## Search Mode Comparison

```
Gemini Search Grounding:
┌─────────────────────────┐
│ User Query              │
└───────┬─────────────────┘
        │
        ▼
┌─────────────────────────┐
│ Gemini performs search  │
│ autonomously            │
└───────┬─────────────────┘
        │
        ▼
┌─────────────────────────┐
│ AI extracts data        │
│ from search results     │
└───────┬─────────────────┘
        │
        ▼
┌─────────────────────────┐
│ Structured response     │
└─────────────────────────┘

Custom Search API:
┌─────────────────────────┐
│ User Query              │
└───────┬─────────────────┘
        │
        ▼
┌─────────────────────────┐
│ Call Custom Search API  │
│ Pre-fetch results       │
└───────┬─────────────────┘
        │
        ▼
┌─────────────────────────┐
│ Embed results in prompt │
└───────┬─────────────────┘
        │
        ▼
┌─────────────────────────┐
│ Gemini extracts from    │
│ provided context        │
└───────┬─────────────────┘
        │
        ▼
┌─────────────────────────┐
│ Structured response     │
└─────────────────────────┘
```

## Error Handling Flow

```
┌─────────────────┐
│  User Input     │
└────────┬────────┘
         │
         ▼
    Validation Layer
    • CUSIP format
    • API key presence
         │
    ┌────┴────┐
    │         │
   OK      ERROR──→ Display to user
    │
    ▼
   Search Phase
    • Custom Search API errors
    • Network timeouts
         │
    ┌────┴────┐
    │         │
   OK      FALLBACK──→ Continue with empty results
    │
    ▼
   API Call
    • Gemini API errors
    • Rate limits
    • Invalid response
         │
    ┌────┴────┐
    │         │
   OK      ERROR──→ Log + return error result
    │
    ▼
  Parsing Layer
    • JSON parse
    • Text extraction
    • Data validation
         │
    ┌────┴────┐
    │         │
   OK      FALLBACK──→ Try alternative parsing
    │
    ▼
┌─────────────────┐
│  Success Result │
└─────────────────┘
```

## Deployment Architecture

```
Development:
  localhost:8501
    ↓
  Streamlit Dev Server
    ↓
  Local Python Environment

Production Options:

Option 1: Streamlit Cloud
  ┌────────────────┐
  │ Streamlit Cloud│
  │ • Auto deploy  │
  │ • Free tier    │
  │ • GitHub sync  │
  └────────────────┘

Option 2: Container
  ┌────────────────┐
  │ Docker         │
  │ • Streamlit    │
  │ • Python 3.8+  │
  │ • Dependencies │
  └────────────────┘
         ↓
  Cloud Run / ECS / Heroku

Option 3: Custom Server
  ┌────────────────┐
  │ NGINX          │
  └───────┬────────┘
          ↓
  ┌────────────────┐
  │ Streamlit      │
  │ (Port 8501)    │
  └────────────────┘
```

## Key Features

- **Dual Search Modes**: Support for both AI-driven and controlled search
- **Dynamic Schema**: JSON structure built based on user-requested attributes
- **Comprehensive Tracing**: Step-by-step visibility into processing
- **Source Merging**: Combines sources from Custom Search and Gemini grounding
- **Flexible Extraction**: Dynamic attribute retrieval - ask for any financial data
- **Robust Error Handling**: Graceful degradation with fallback mechanisms
- **Clean Architecture**: Separation of concerns with clear module boundaries

This architecture provides:
- Clear separation of concerns
- Dual search mode flexibility
- Easy testing and maintenance
- Scalable design
- Comprehensive observability through tracing
- Robust error handling with fallbacks
