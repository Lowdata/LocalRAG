def test_bug():
    text = "Ollama: Connects to a local Ollama instance (defaulting to qwen2.5:1.5b) for LLM response generation.\nPrerequisites\nBefore running the backend, you must initialize your local environment variables."
    # Let's say new_start lands right in the middle of "Connects"
    # "Ollama: Connects" -> "C" is index 8. Let's say new_start is 8 (on the 'C').
    new_start = 8
    
    if new_start > 0 and text[new_start-1] not in (" ", "\n"):
        print(f"Before snapping: new_start={new_start}, text starts with '{text[new_start:new_start+10]}'")
        next_space = text.find(" ", new_start)
        next_newline = text.find("\n", new_start)
        
        valid_boundaries = [b for b in (next_space, next_newline) if b != -1]
        if valid_boundaries:
            new_start = min(valid_boundaries) + 1
            
        print(f"After snapping: new_start={new_start}, text starts with '{text[new_start:new_start+10]}'")

if __name__ == "__main__":
    test_bug()
