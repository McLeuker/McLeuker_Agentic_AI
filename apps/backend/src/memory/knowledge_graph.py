"""
Knowledge Graph — Entity and Relationship Tracking
====================================================

Tracks entities and relationships discovered during execution:
- Entity extraction and storage
- Relationship mapping
- Graph traversal and search
- Knowledge accumulation across sessions
"""

import json
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """A knowledge graph entity."""
    id: str
    name: str
    entity_type: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    mentions: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "entity_type": self.entity_type,
            "attributes": self.attributes,
            "mentions": self.mentions,
        }


@dataclass
class Relationship:
    """A relationship between entities."""
    source_id: str
    target_id: str
    relation_type: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "confidence": self.confidence,
        }


class KnowledgeGraph:
    """
    Knowledge graph for entity and relationship tracking.

    Features:
    - Entity CRUD
    - Relationship management
    - Graph traversal
    - Search
    - Persistence
    """

    def __init__(self):
        self._entities: Dict[str, Entity] = {}
        self._relationships: Dict[str, List[Relationship]] = {}
        self._name_index: Dict[str, str] = {}

    def add_entity(
        self,
        name: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Entity:
        """Add or update an entity."""
        existing_id = self._name_index.get(name.lower())
        if existing_id:
            entity = self._entities[existing_id]
            entity.mentions += 1
            if attributes:
                entity.attributes.update(attributes)
            return entity

        entity_id = entity_id or f"{entity_type}_{len(self._entities)}"
        entity = Entity(
            id=entity_id,
            name=name,
            entity_type=entity_type,
            attributes=attributes or {},
        )

        self._entities[entity_id] = entity
        self._name_index[name.lower()] = entity_id
        return entity

    def add_relationship(
        self,
        source_name: str,
        target_name: str,
        relation_type: str,
        confidence: float = 1.0,
    ) -> Optional[Relationship]:
        """Add a relationship between entities."""
        source_id = self._name_index.get(source_name.lower())
        target_id = self._name_index.get(target_name.lower())

        if not source_id or not target_id:
            return None

        rel = Relationship(
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            confidence=confidence,
        )

        if source_id not in self._relationships:
            self._relationships[source_id] = []
        self._relationships[source_id].append(rel)
        return rel

    def get_entity(self, name_or_id: str) -> Optional[Entity]:
        """Get entity by name or ID."""
        if name_or_id in self._entities:
            return self._entities[name_or_id]
        entity_id = self._name_index.get(name_or_id.lower())
        return self._entities.get(entity_id) if entity_id else None

    def search_entities(self, query: str, entity_type: Optional[str] = None) -> List[Entity]:
        """Search entities by name."""
        query_lower = query.lower()
        results = []
        for entity in self._entities.values():
            if entity_type and entity.entity_type != entity_type:
                continue
            if query_lower in entity.name.lower():
                results.append(entity)
        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            "entity_count": len(self._entities),
            "relationship_count": sum(len(r) for r in self._relationships.values()),
            "entity_types": list(set(e.entity_type for e in self._entities.values())),
        }

    def export_to_dict(self) -> Dict[str, Any]:
        """Export graph to dictionary."""
        return {
            "entities": [e.to_dict() for e in self._entities.values()],
            "relationships": [
                r.to_dict()
                for rels in self._relationships.values()
                for r in rels
            ],
        }

    def save_to_file(self, path: str) -> bool:
        """Save graph to file."""
        try:
            with open(path, "w") as f:
                json.dump(self.export_to_dict(), f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save knowledge graph: {e}")
            return False
