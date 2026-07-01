import json
import re
from typing import Optional
from app.schemas.judge import JudgeVerdict

class JSONParserError(Exception):
    pass

class JudgeParser:
    @staticmethod
    def extract_json_block(text: str) -> str:
        # Try to find a markdown json block
        match = re.search(r'```(?:json)?(.*?)```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # Fallback to finding the first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
            
        return text.strip()

    @staticmethod
    def parse_verdict(raw_response: str) -> JudgeVerdict:
        extracted = JudgeParser.extract_json_block(raw_response)
        try:
            data = json.loads(extracted)
            return JudgeVerdict(**data)
        except json.JSONDecodeError as e:
            raise JSONParserError(f"Failed to decode JSON: {str(e)}\nRaw extracted: {extracted}")
        except Exception as e:
            raise JSONParserError(f"Failed to validate Pydantic schema: {str(e)}")

judge_parser = JudgeParser()
