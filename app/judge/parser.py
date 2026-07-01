import json
import re
from app.schemas.judge import JudgeVerdict


class JSONParserError(Exception):
    pass


class JudgeParser:
    @staticmethod
    def extract_json_block(text: str) -> str:
        # Try to find a markdown json block
        match = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Fallback to finding the first { and last }
        start = text.find("{")
        end = text.rfind("}")

        # If it found a start but no end, it might have been cut off. Try appending '}'
        if start != -1 and end == -1:
            text = text + "}"
            end = text.rfind("}")

        if start != -1 and end != -1 and end > start:
            # Check if it needs quotes closed
            extracted = text[start : end + 1]
            if extracted.count('"') % 2 != 0:
                extracted = extracted[:-1] + '"}'
            return extracted

        return text.strip()

    @staticmethod
    def parse_verdict(raw_response: str) -> JudgeVerdict:
        extracted = JudgeParser.extract_json_block(raw_response)
        try:
            data = json.loads(extracted)
            return JudgeVerdict(**data)
        except json.JSONDecodeError as e:
            raise JSONParserError(
                f"Failed to decode JSON: {str(e)}\nRaw extracted: {extracted}"
            )
        except Exception as e:
            raise JSONParserError(f"Failed to validate Pydantic schema: {str(e)}")


judge_parser = JudgeParser()
