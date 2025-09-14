# Mock paperqa.agents.search module for notebook compatibility
def get_directory_index(*args, **kwargs):
    """Mock get_directory_index function"""
    return {"mock": "index"}
