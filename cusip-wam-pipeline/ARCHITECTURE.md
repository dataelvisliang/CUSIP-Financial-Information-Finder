# Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface (Streamlit)               │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  API Key     │  │  CUSIP       │  │  Advanced    │        │
│  │  Input       │  │  Input       │  │  Options     │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              Results Display                             │ │
│  │  • Financial Attributes  • WAM Calculation               │ │
│  │  • Maturity Data        • Sources                        │ │
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
│  │  • Parses responses                                      │ │
│  │  • Calculates WAM                                        │ │
│  │  • Aggregates results                                    │ │
│  └──────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  GeminiClient                                            │ │
│  │  • Manages API connection                                │ │
│  │  • Builds prompts                                        │ │
│  │  • Extracts sources                                      │ │
│  │  • Handles errors                                        │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               Google Gemini API (with Search Grounding)         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  Web Search  │→ │  LLM         │→ │  Structured  │        │
│  │  for CUSIP   │  │  Extraction  │  │  Response    │        │
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
     │ 1. Enter CUSIP + API Key
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
     ▼                    │ 9. Calculate WAM
┌──────────────────┐      │    Parse response
│  GeminiClient    │      │    Aggregate data
└────┬─────────────┘      │
     │ 5. Build prompt    │
     │    + config        │
     ▼                    │
┌──────────────────┐      │
│  Gemini API      │      │
│  (with Search)   │      │
└────┬─────────────┘      │
     │ 6. Search web      │
     │    for CUSIP       │
     ▼                    │
┌──────────────────┐      │
│  Data Sources    │      │
│  (Web)           │      │
└────┬─────────────┘      │
     │ 7. Return data     │
     ▼                    │
┌──────────────────┐      │
│  Gemini API      │      │
│  (Extract)       │      │
└────┬─────────────┘      │
     │ 8. Structured      │
     │    response        │
     ▼                    │
┌──────────────────┐      │
│  GeminiClient    │◄─────┘
└────┬─────────────┘
     │ 10. Return result
     ▼
┌──────────────────┐
│  CUSIPPipeline   │
└────┬─────────────┘
     │ 11. Format for display
     ▼
┌──────────────────┐
│  Streamlit UI    │
└────┬─────────────┘
     │ 12. Render results
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
  │     │     └── google.generativeai (Gemini API)
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
│ API Key:str │
│ Attrs: list │
└──────┬──────┘
       │
       ▼

Processing Stage:
┌──────────────────────────┐
│ Gemini Query             │
│ • Prompt building        │
│ • Web search grounding   │
│ • LLM extraction         │
└──────┬───────────────────┘
       │
       ▼

Parsing Stage:
┌──────────────────────────┐
│ Response Parsing         │
│ • JSON extraction        │
│ • Text extraction        │
│ • Data validation        │
└──────┬───────────────────┘
       │
       ▼

Computation Stage:
┌──────────────────────────┐
│ WAM Calculation          │
│ • Σ(Mat_i × Prin_i)      │
│ • / Σ(Prin_i)            │
└──────┬───────────────────┘
       │
       ▼

Output Stage:
┌──────────────────────────┐
│ CUSIPAnalysisResult      │
│ • attributes: dict       │
│ • wam_years: float       │
│ • maturities: list       │
│ • sources: list          │
│ • error: str|None        │
└──────────────────────────┘
```

## Class Hierarchy

```
Data Models:

FinancialAttribute (Enum)
  • WAM
  • MATURITY
  • COUPON_RATE
  • YIELD
  • CREDIT_RATING
  • ISSUER
  • ISSUE_DATE
  • PAR_VALUE
  • SECURITY_TYPE

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
CUSIPData
  • cusip: str
  • attributes: Dict[str, FinancialAttributeData]
  • maturities: List[MaturityData]
  • sources: List[str]

@dataclass
CUSIPAnalysisResult
  • cusip: str
  • attributes: Dict[str, Any]
  • wam_years: float
  • wam_months: float
  • maturities: List[MaturityData]
  • sources: List[str]
  • error: str
```

## Service Layer

```
GeminiClient
  │
  ├── __init__(api_key, model_name)
  │     • Configure API
  │     • Set up search grounding
  │     • Initialize safety settings
  │
  ├── query_cusip_attributes(cusip, attributes)
  │     • Build prompt
  │     • Query Gemini
  │     • Extract sources
  │     • Return structured response
  │
  ├── _build_cusip_query_prompt(cusip, attributes)
  │     • Format attribute list
  │     • Add instructions
  │     • Specify output format
  │
  ├── _extract_sources(response)
  │     • Parse grounding metadata
  │     • Extract web URLs
  │     • Deduplicate
  │
  └── query_with_custom_prompt(prompt)
        • Generic query method


CUSIPPipeline
  │
  ├── __init__(gemini_client)
  │     • Store client reference
  │
  ├── process_cusip(cusip, attributes)
  │     • Query Gemini
  │     • Parse response
  │     • Return result
  │
  ├── _parse_gemini_response(cusip, response_data)
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
  │     • Parse maturities
  │     • Calculate WAM
  │
  ├── _build_result_from_text(cusip, text, sources)
  │     • Pattern matching
  │     • Attribute extraction
  │
  ├── _calculate_wam(maturities)
  │     • Weighted average
  │     • Error handling
  │
  └── get_wam_only(cusip)
        • Focused WAM query
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
   API Call
    • Network errors
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
 Computation
    • WAM calculation
    • Data aggregation
         │
    ┌────┴────┐
    │         │
   OK      PARTIAL──→ Return partial results
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

This architecture provides:
- Clear separation of concerns
- Easy testing and maintenance
- Flexible deployment options
- Scalable design
- Robust error handling
