import os

def parse_environment_variables() -> dict:
    """
    Parses known PRAMAN_* environment variables and returns them as a dictionary
    with correct Python types.
    """
    overrides = {}
    
    # 1. Base URL (String)
    base_url = os.getenv("PRAMAN_BASE_URL")
    if base_url is not None:
        overrides["base_url"] = base_url
        
    # 2. Browser (String)
    browser = os.getenv("PRAMAN_BROWSER")
    if browser is not None:
        overrides["browser"] = browser
        
    # 3. Headless (Boolean)
    headless = os.getenv("PRAMAN_HEADLESS")
    if headless is not None:
        lower_headless = headless.strip().lower()
        if lower_headless == "true":
            overrides["headless"] = True
        elif lower_headless == "false":
            overrides["headless"] = False
        else:
            raise ValueError(
                f"Invalid value for PRAMAN_HEADLESS: '{headless}'. "
                f"Expected 'true' or 'false' (case-insensitive)."
            )
        
    # 4. Timeout (Integer)
    timeout = os.getenv("PRAMAN_TIMEOUT")
    if timeout is not None:
        try:
            overrides["timeout"] = int(timeout)
        except ValueError:
            raise ValueError(
                f"Invalid value for PRAMAN_TIMEOUT: '{timeout}'. "
                f"Expected an integer."
            )
            
    return overrides