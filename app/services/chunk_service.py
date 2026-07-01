from typing import List, Optional
from app.schemas.document import ParsedDocument, DocumentChunk
from app.core.config import settings

class ChunkService:
    @staticmethod
    def chunk_document(document: ParsedDocument, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None) -> List[DocumentChunk]:
        """
        Chunks a ParsedDocument into smaller DocumentChunk objects.
        Uses a simple overlapping character-based chunking strategy.
        """
        if chunk_size is None:
            chunk_size = settings.chunk_size
        if chunk_overlap is None:
            chunk_overlap = settings.chunk_overlap
            
        chunks: List[DocumentChunk] = []
        chunk_index = 0
        
        for page in document.pages:
            text = page.text
            
            # Simple chunking loop
            start = 0
            while start < len(text):
                # Calculate end index
                end = start + chunk_size
                
                # If we are not at the end of the text, try to find a nice break point (e.g. newline or space)
                # to avoid breaking words in half if possible.
                if end < len(text):
                    # Look backwards for a space or newline within the overlap region
                    break_point = text.rfind("\n", max(0, start + chunk_size - chunk_overlap), end)
                    if break_point == -1:
                        break_point = text.rfind(" ", max(0, start + chunk_size - chunk_overlap), end)
                    
                    if break_point != -1:
                        end = break_point + 1 # Include the space/newline
                
                chunk_text = text[start:end].strip()
                
                if chunk_text:
                    # Use a predictable ID for rigorous IR metric evaluation
                    chunk_id = f"{document.document_path}_page{page.page_number}_chunk{chunk_index}"
                    
                    chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        document_path=document.document_path,
                        page_number=page.page_number,
                        text=chunk_text,
                        metadata=page.metadata.copy()
                    ))
                    chunk_index += 1
                
                if end >= len(text):
                    break
                    
                # Move start forward, accounting for overlap
                new_start = end - chunk_overlap
                
                # If we are in the middle of a word, advance to the next whitespace boundary
                # so the next chunk doesn't start with a partial word.
                if new_start > 0 and text[new_start-1] not in (" ", "\n"):
                    # Find nearest space or newline after new_start
                    next_space = text.find(" ", new_start)
                    next_newline = text.find("\n", new_start)
                    
                    valid_boundaries = [b for b in (next_space, next_newline) if b != -1]
                    if valid_boundaries:
                        new_start = min(valid_boundaries) + 1
                
                start = new_start
                
        return chunks
