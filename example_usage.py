"""Example usage of the CUSIP pipeline programmatically"""
import os
from src.services.gemini_client import GeminiClient
from src.services.pipeline import CUSIPPipeline


def main():
    """Demonstrate pipeline usage"""

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Please set GOOGLE_API_KEY environment variable")
        print("Or replace with your actual API key below")
        api_key = "your-api-key-here"

    print("Initializing CUSIP Pipeline...")
    gemini_client = GeminiClient(api_key=api_key)
    pipeline = CUSIPPipeline(gemini_client=gemini_client)

    cusip = "912828Z29"
    print(f"\nProcessing CUSIP: {cusip}")

    result = pipeline.process_cusip(cusip=cusip)

    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)

    print(f"\nCUSIP: {result.cusip}")

    if result.error:
        print(f"Error: {result.error}")
        return

    print("\nFinancial Attributes:")
    for attr_name, attr_data in result.attributes.items():
        if isinstance(attr_data, dict):
            value = attr_data.get('value', 'N/A')
            print(f"  - {attr_name}: {value}")
        else:
            print(f"  - {attr_name}: {attr_data}")

    if result.wam_years:
        print(f"\nWeighted Average Maturity:")
        print(f"  - Years: {result.wam_years:.2f}")
        print(f"  - Months: {result.wam_months:.2f}")
        if result.total_principal:
            print(f"  - Total Principal: ${result.total_principal:,.2f}")

    if result.maturities:
        print(f"\nIndividual Maturities ({len(result.maturities)}):")
        for i, mat in enumerate(result.maturities, 1):
            print(f"  Maturity {i}:")
            if mat.maturity_date:
                print(f"    - Date: {mat.maturity_date}")
            if mat.years_to_maturity:
                print(f"    - Years: {mat.years_to_maturity:.2f}")
            if mat.principal_amount:
                print(f"    - Principal: ${mat.principal_amount:,.2f}")

    if result.sources:
        print(f"\nSources ({len(result.sources)}):")
        for i, source in enumerate(result.sources, 1):
            print(f"  {i}. {source}")

    print("\n" + "="*60)


def example_custom_attributes():
    """Example with custom attributes"""
    api_key = os.getenv("GOOGLE_API_KEY", "your-api-key-here")

    print("\nCustom Attributes Example")
    print("-" * 60)

    gemini_client = GeminiClient(api_key=api_key)
    pipeline = CUSIPPipeline(gemini_client=gemini_client)

    cusip = "037833100"
    custom_attrs = [
        "issuer",
        "coupon rate",
        "maturity date",
        "credit rating"
    ]

    print(f"Querying CUSIP: {cusip}")
    print(f"Requested attributes: {', '.join(custom_attrs)}")

    result = pipeline.process_cusip(cusip=cusip, attributes=custom_attrs)

    print(f"\nExtracted {len(result.attributes)} attributes")
    for attr_name, attr_data in result.attributes.items():
        if isinstance(attr_data, dict):
            print(f"  {attr_name}: {attr_data.get('value', 'N/A')}")


def example_wam_only():
    """Example of WAM-only calculation"""
    api_key = os.getenv("GOOGLE_API_KEY", "your-api-key-here")

    print("\nWAM-Only Example")
    print("-" * 60)

    gemini_client = GeminiClient(api_key=api_key)
    pipeline = CUSIPPipeline(gemini_client=gemini_client)

    cusip = "594918104"
    result = pipeline.get_wam_only(cusip=cusip)

    if result.wam_years:
        print(f"WAM for {cusip}:")
        print(f"  {result.wam_years:.2f} years ({result.wam_months:.2f} months)")
    else:
        print("WAM calculation not available")


if __name__ == "__main__":
    print("CUSIP Financial Analyzer - Example Usage")
    print("=" * 60)

    try:
        main()
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nMake sure you have set your GOOGLE_API_KEY environment variable")
        print("or updated the api_key in the code")
