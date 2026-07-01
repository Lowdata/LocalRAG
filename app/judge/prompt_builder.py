import os

class PromptBuilder:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = prompts_dir

    def load_prompt(self, version: str) -> str:
        filepath = os.path.join(self.prompts_dir, f"judge_{version}.txt")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Prompt template {filepath} not found.")
        with open(filepath, "r") as f:
            return f.read()

    def build_judge_prompt(self, version: str, question: str, expected: str, generated: str) -> str:
        template = self.load_prompt(version)
        return template.format(
            question=question,
            expected=expected,
            generated=generated
        )

prompt_builder = PromptBuilder()
