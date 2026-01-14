class BaseTool:
    """
    Minimal local replacement for CrewAI BaseTool / CrewAITool.
    Provides a consistent interface for your custom tools.
    """

    name: str = "UnnamedTool"
    description: str = "Generic tool interface"

    def __init__(self):
        pass

    def run(self, *args, **kwargs):
        """Public interface — calls _run implementation."""
        return self._run(*args, **kwargs)

    def _run(self, *args, **kwargs):
        """To be overridden by subclasses."""
        raise NotImplementedError("Tool must implement _run() method.")
