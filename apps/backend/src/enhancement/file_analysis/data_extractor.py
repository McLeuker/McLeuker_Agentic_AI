"""
Data Extractor - Structured Data Extraction
============================================

Extracts structured data from files:
- Tables
- Lists
- Key-value pairs
- Entities
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class DataExtractor:
    """
    Extracts structured data from files.
    
    Capabilities:
    - Table extraction
    - Entity extraction
    - Key-value pair extraction
    - Structured data parsing
    """
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def extract_structured_data(
        self,
        file_path: str,
        schema: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from file.
        
        Args:
            file_path: Path to file
            schema: Optional expected data schema
            
        Returns:
            Extracted data
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Build extraction prompt
            if schema:
                schema_desc = json.dumps(schema, indent=2)
                prompt = f"""Extract structured data from this content according to the schema:

Schema:
{schema_desc}

Extract the data and return it as JSON matching the schema."""
            else:
                prompt = """Extract structured data from this content.
Identify entities, key-value pairs, tables, and lists.
Return the data as JSON."""
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a data extraction expert. Extract structured data accurately."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nContent:\n{content[:8000]}"
                }
            ]
            
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            extracted_data = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "data": extracted_data,
                "source_file": Path(file_path).name
            }
            
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def extract_entities(
        self,
        file_path: str,
        entity_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Extract entities from file.
        
        Args:
            file_path: Path to file
            entity_types: Types of entities to extract
            
        Returns:
            Extracted entities
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            entity_types = entity_types or ["person", "organization", "location", "product", "brand"]
            
            prompt = f"""Extract entities from this content.

Entity types to extract: {', '.join(entity_types)}

For each entity, provide:
- name
- type
- context (how it appears in the text)

Return as JSON."""
            
            messages = [
                {
                    "role": "system",
                    "content": "You are an entity extraction expert."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nContent:\n{content[:8000]}"
                }
            ]
            
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            entities = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "entities": entities,
                "entity_types": entity_types
            }
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def extract_tables(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Extract tables from file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted tables
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            prompt = """Extract all tables from this content.

For each table, provide:
- table_name (if identifiable)
- headers (column names)
- rows (data rows)

Return as JSON."""
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a table extraction expert."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nContent:\n{content[:8000]}"
                }
            ]
            
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            tables = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "tables": tables
            }
            
        except Exception as e:
            logger.error(f"Table extraction failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def extract_key_value_pairs(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Extract key-value pairs from file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted key-value pairs
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            prompt = """Extract all key-value pairs from this content.

Look for patterns like:
- Key: Value
- Key = Value
- "Key": "Value"
- Key - Value

Return as JSON object."""
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a key-value extraction expert."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nContent:\n{content[:8000]}"
                }
            ]
            
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            pairs = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "key_value_pairs": pairs
            }
            
        except Exception as e:
            logger.error(f"Key-value extraction failed: {e}")
            return {"success": False, "error": str(e)}
