from typing import Optional
import ee

def initialize_ee(project_name: Optional[str] = None) -> None:
    """
    Initialize the Earth Engine API.
    :param project_name: The name of the project to use. If None, the default project is used.
    """
    ee.Authenticate()
    if project_name:
        ee.Initialize(project_name)
    else:
        ee.Initialize()