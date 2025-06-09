class DummyAgent:
    def run(self, prompt):
        return "Mock response: Control is partially implemented."

# Replace Agent with DummyAgent for testing without API calls
agent = DummyAgent()

# Your existing code continues...
