def verify_imports():
    """Verify that all required packages can be imported"""
    try:
        from python_dotenv import load_dotenv
        print("✓ python-dotenv import successful")
        
        from exa_py import Client
        print("✓ exa-py import successful")
        
        import langchain
        print("✓ langchain import successful")
        
        import requests
        print("✓ requests import successful")
        
        from bs4 import BeautifulSoup
        print("✓ beautifulsoup4 import successful")
        
        print("\nAll imports verified successfully!")
        return True
    except ImportError as e:
        print(f"\n❌ Import error: {str(e)}")
        return False

if __name__ == "__main__":
    verify_imports() 