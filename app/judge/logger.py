import os
import json
from datetime import datetime
from typing import Dict, Any, Optional


class JudgeLogger:
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = logs_dir
        os.makedirs(self.logs_dir, exist_ok=True)
        self.log_file = os.path.join(self.logs_dir, "judge_audit.jsonl")

    def log_evaluation(
        self,
        case_id: str,
        prompt: str,
        raw_response: str,
        parsed_json: Optional[Dict[str, Any]],
        metadata: Dict[str, Any],
    ) -> str:
        timestamp = datetime.now().isoformat()

        log_entry = {
            "timestamp": timestamp,
            "case_id": case_id,
            "metadata": metadata,
            "prompt": prompt,
            "raw_response": raw_response,
            "parsed": parsed_json,
        }

        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        return self.log_file


judge_logger = JudgeLogger()
