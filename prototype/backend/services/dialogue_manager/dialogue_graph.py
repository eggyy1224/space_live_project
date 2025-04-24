"""
DialogueGraph for managing conversation flow.

This module:
- Defines the graph structure for conversation flow
- Separates node definitions from graph construction
- Provides a clean interface for graph traversal
"""


class Node:
    """Base class for dialogue graph nodes."""
    
    def __init__(self, node_id, config=None):
        """
        Initialize a new node.
        
        Args:
            node_id: Unique identifier for this node
            config: Configuration options for the node
        """
        self.node_id = node_id
        self.config = config or {}
        self.next_nodes = {}
        
    async def process(self, context):
        """
        Process the node with the given context.
        
        Args:
            context: Current conversation context
            
        Returns:
            str: Next node ID to transition to
        """
        # This should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement process()")
    
    def add_edge(self, condition, next_node_id):
        """
        Add an edge from this node to another.
        
        Args:
            condition: Condition for taking this edge
            next_node_id: ID of the node to transition to
        """
        self.next_nodes[condition] = next_node_id


class DialogueGraph:
    """Manages the dialogue flow graph structure and execution."""
    
    def __init__(self):
        """Initialize a new dialogue graph."""
        self.nodes = {}
        self.current_node_id = None
        
    def add_node(self, node):
        """
        Add a node to the graph.
        
        Args:
            node: The node to add
        """
        self.nodes[node.node_id] = node
        
    def set_start_node(self, node_id):
        """
        Set the starting node for the graph.
        
        Args:
            node_id: ID of the starting node
        """
        self.current_node_id = node_id
        
    async def process_step(self, context):
        """
        Process one step through the graph.
        
        Args:
            context: Current conversation context
            
        Returns:
            dict: Result of processing the current node
        """
        if not self.current_node_id or self.current_node_id not in self.nodes:
            return {"error": "Invalid current node"}
            
        current_node = self.nodes[self.current_node_id]
        next_node_id = await current_node.process(context)
        self.current_node_id = next_node_id
        
        return {"current_node": self.current_node_id} 