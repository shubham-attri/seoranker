def test_imports():
    """Test that all required packages can be imported"""
    try:
        import dotenv
        import langchain
        import exa
        import requests
        import bs4
        print("All imports successful!")
        return True
    except ImportError as e:
        print(f"Import error: {str(e)}")
        return False

if __name__ == "__main__":
    test_imports() 