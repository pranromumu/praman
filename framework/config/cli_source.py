import argparse
from framework.contracts.config_source import ConfigSource

class CLISource(ConfigSource):
    """
    Configuration source that reads command-line arguments.
    
    Responsible for:
    - Parsing --base-url, --browser, --headless, --timeout, --version-policy arguments
    - Converting raw strings into appropriate Python types
    
    Not responsible for:
    - Configuration precedence
    - Business validation
    """
    
    def __init__(self, args=None):
        self._args = args

    def get_config(self) -> dict:
        parser = argparse.ArgumentParser(description="Praman QA Engine", add_help=False)
        
        parser.add_argument("--base-url", dest="base_url")
        parser.add_argument("--browser", dest="browser")
        parser.add_argument("--headless", dest="headless")
        parser.add_argument("--timeout", dest="timeout")
        parser.add_argument("--version-policy", dest="version_policy")  # NEW
        
        # parse_known_args allows pytest to run without crashing on its own args
        parsed_args, _ = parser.parse_known_args(self._args)
        
        overrides = {}
        
        if parsed_args.base_url is not None:
            overrides["base_url"] = parsed_args.base_url
            
        if parsed_args.browser is not None:
            overrides["browser"] = parsed_args.browser
            
        if parsed_args.headless is not None:
            val = parsed_args.headless.lower()
            if val == "true":
                overrides["headless"] = True
            elif val == "false":
                overrides["headless"] = False
            else:
                raise ValueError(
                    f"Invalid value for --headless: '{parsed_args.headless}'. "
                    f"Expected 'true' or 'false' (case-insensitive)."
                )
                
        if parsed_args.timeout is not None:
            try:
                overrides["timeout"] = int(parsed_args.timeout)
            except ValueError:
                raise ValueError(
                    f"Invalid value for --timeout: '{parsed_args.timeout}'. "
                    f"Expected an integer."
                )
                
        if parsed_args.version_policy is not None:
            overrides["version_policy"] = parsed_args.version_policy
                
        return overrides