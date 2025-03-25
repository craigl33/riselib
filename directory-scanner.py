from pathlib import Path
import os

class DirectoryScanner:
    def __init__(self):
        self.nodes = []
        self.connections = []
        self.node_count = 0
        self.node_map = {}  # Maps paths to node IDs

    def _create_node_id(self, path):
        """Create a unique node ID for a path."""
        if path in self.node_map:
            return self.node_map[path]
        
        node_id = f"node{self.node_count}"
        self.node_count += 1
        self.node_map[path] = node_id
        return node_id

    def _add_node(self, path, is_file=False):
        """Add a node to the diagram."""
        node_id = self._create_node_id(path)
        name = path.name or str(path)  # Use name or full path for root
        
        # Escape special characters in name for Mermaid
        name = name.replace("[", "\\[").replace("]", "\\]")
        
        if is_file:
            self.nodes.append(f'{node_id}[{name}]')
        else:
            self.nodes.append(f'{node_id}[/{name}/]')
            
        return node_id

    def _add_connection(self, parent_id, child_id):
        """Add a connection between nodes."""
        self.connections.append(f'{parent_id} --> {child_id}')

    def scan_directory(self, root_path, max_depth=None, exclude_patterns=None):
        """
        Scan a directory and create a Mermaid diagram.
        
        Args:
            root_path (str or Path): Path to the root directory
            max_depth (int, optional): Maximum depth to scan
            exclude_patterns (list, optional): List of patterns to exclude
        """
        root_path = Path(root_path)
        exclude_patterns = exclude_patterns or []
        
        def should_exclude(path):
            """Check if path should be excluded."""
            name = str(path)
            return any(pattern in name for pattern in exclude_patterns)

        def scan_recursive(current_path, current_depth=0):
            """Recursively scan directory and create nodes."""
            if max_depth is not None and current_depth > max_depth:
                return None
                
            if should_exclude(current_path):
                return None
                
            try:
                # Add current node
                current_id = self._add_node(current_path, is_file=current_path.is_file())
                
                # If it's a directory, process its contents
                if current_path.is_dir():
                    try:
                        # Sort contents for consistent output
                        contents = sorted(current_path.iterdir())
                        for item in contents:
                            child_id = scan_recursive(item, current_depth + 1)
                            if child_id is not None:
                                self._add_connection(current_id, child_id)
                    except PermissionError:
                        # Handle permission errors gracefully
                        self.nodes.append(f'error{self.node_count}[❌ No access to {current_path.name}]')
                        self._add_connection(current_id, f'error{self.node_count}')
                        self.node_count += 1
                
                return current_id
                
            except Exception as e:
                print(f"Error processing {current_path}: {e}")
                return None

        # Start the recursive scan
        scan_recursive(root_path)

    def generate_mermaid(self):
        """Generate the Mermaid diagram text."""
        mermaid = ["graph TD"]
        
        # Add all nodes
        for node in self.nodes:
            mermaid.append("    " + node)
        
        # Add a blank line between nodes and connections
        if self.connections:
            mermaid.append("")
            
        # Add all connections
        for connection in self.connections:
            mermaid.append("    " + connection)
            
        return "\n".join(mermaid)

def create_directory_diagram(path, max_depth=None, exclude_patterns=None):
    """
    Create a Mermaid diagram for the specified directory.
    
    Args:
        path (str): Path to the directory
        max_depth (int, optional): Maximum depth to scan
        exclude_patterns (list, optional): List of patterns to exclude
    
    Returns:
        str: Mermaid diagram text
    """
    scanner = DirectoryScanner()
    scanner.scan_directory(path, max_depth, exclude_patterns)
    return scanner.generate_mermaid()

# Example usage
if __name__ == "__main__":
    # Example with some common exclusions
    exclude_patterns = [
        "__pycache__",
        ".git",
        "node_modules",
        ".venv",
        ".env"
    ]
    
    # Get the directory path from command line or use current directory
    import sys
    dir_path = "Y:/GIS/"
    
    # Generate and print the diagram
    diagram = create_directory_diagram(
        dir_path,
        max_depth=3,  # Limit depth to avoid too large diagrams
        exclude_patterns=exclude_patterns
    )
    print(diagram)
