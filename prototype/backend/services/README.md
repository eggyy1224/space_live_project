# Backend Services Restructuring

This directory contains the modular services for the backend application. As part of Task 1 in our refactoring effort, the following new module structure has been created:

## New Module Structure

- **murmur_service/**: Self-talk (murmur) functionality with configurable context memory
- **memory_system/**: Memory retrieval system with optimizations for sub-500ms response times
- **tool_executor/**: Tool detection and execution decoupled from dialogue flow
- **dialogue_manager/**: Dialogue flow graph and conversation state management
- **ai_service/**: AI model integration and generation services

## Migration Plan

The following files need to be migrated to their new locations:

### From services/ai/:
- `dialogue_graph.py` → `services/dialogue_manager/dialogue_graph.py` (placeholder already created)
- `graph_nodes/` → `services/dialogue_manager/graph_nodes/`
- `tools/` → `services/tool_executor/tools/`
- `memory_system.py` → `services/memory_system/`
- `memory_components/` → `services/memory_system/memory_components/`
- AI-specific portions of `__init__.py` → `services/ai_service/`

### Existing Files:
- `text_to_speech.py` and `speech_to_text.py` can remain in the services root directory for now

## Import Path Updates

During the migration, all import statements will need to be updated to reflect the new module structure. For example:

```python
# Old import path
from services.ai.dialogue_graph import DialogueGraph

# New import path
from services.dialogue_manager.dialogue_graph import DialogueGraph
```

## Phased Migration

To minimize disruption, the migration will be done in phases:

1. Create new directory structure ✓
2. Create placeholder files in new locations ✓
3. Move functionality from existing files to new locations
4. Update import paths
5. Test application functionality
6. Remove deprecated files once all functionality is migrated

## Note

This refactoring focuses on restructuring the codebase without changing functionality. The goal is to prepare for modular refactoring in subsequent tasks. 