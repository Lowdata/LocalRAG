import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

class JudgeLogger:
    def __init__(self, logs_dir: str = "logs/judge"):
        self.logs_dir = logs_dir
        os.makedirs(self.logs_dir, exist_ok=True)

    def log_evaluation(
        self, 
        case_id: str, 
        prompt: str, 
        raw_response: str, 
        parsed_json: Optional[Dict[str, Any]], 
        metadata: Dict[str, Any]
    ) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        run_dir = os.path.join(self.logs_dir, f"{case_id}_{timestamp}")
        os.makedirs(run_dir, exist_ok=True)

        with open(os.path.join(run_dir, "prompt.txt"), "w") as f:
            f.write(prompt)
            
        with open(os.path.join(run_dir, "response.txt"), "w") as f:
            f.write(raw_response)
            
        if parsed_json:
            with open(os.path.join(run_dir, "parsed.json"), "w") as f:
                json.dump(parsed_json, f, indent=2)
                
        with open(os.path.join(run_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        return run_dir

judge_logger = JudgeLogger()
