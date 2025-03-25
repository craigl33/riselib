import os
import json
from pathlib import Path
import webbrowser
import tempfile
from datetime import datetime

class DirectoryScanner:
    def __init__(self):
        self.tree = {}
        
    def scan(self, path, max_depth=None):
        """Scan directory and create tree structure."""
        path = Path(path)
        self.tree = self._scan_recursive(path, current_depth=0, max_depth=max_depth)
        return self.tree
    
    def _scan_recursive(self, path, current_depth, max_depth):
        """Recursively scan directory."""
        if max_depth is not None and current_depth > max_depth:
            return None
            
        if path.is_file():
            stats = path.stat()
            return {
                'type': 'file',
                'name': path.name,
                'size': stats.st_size,
                'modified': datetime.fromtimestamp(stats.st_mtime).isoformat()
            }
        elif path.is_dir():
            try:
                children = {}
                for child in sorted(path.iterdir()):
                    # Skip hidden files and directories
                    if not child.name.startswith('.'):
                        result = self._scan_recursive(child, current_depth + 1, max_depth)
                        if result:
                            children[child.name] = result
                            
                return {
                    'type': 'directory',
                    'name': path.name,
                    'children': children
                }
            except PermissionError:
                return {
                    'type': 'directory',
                    'name': path.name,
                    'error': 'Permission denied'
                }
    
    def save_json(self, output_path):
        """Save the tree structure to a JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.tree, f, indent=2, ensure_ascii=False)
            
    def visualize(self):
        """Create and open an interactive visualization."""
        html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Directory Visualization</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <style>
        body { 
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
        .node circle {
            fill: #fff;
            stroke: steelblue;
            stroke-width: 1.5px;
        }
        .node text {
            font: 12px sans-serif;
        }
        .link {
            fill: none;
            stroke: #ccc;
            stroke-width: 1.5px;
        }
        .tooltip {
            position: absolute;
            background: white;
            border: 1px solid #ddd;
            padding: 8px;
            border-radius: 4px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div id="tree"></div>
    <script>
        // Convert the tree data to D3 hierarchy format
        const treeData = ''' + json.dumps(self.tree) + ''';
        
        // Set dimensions
        const width = window.innerWidth - 40;
        const height = window.innerHeight - 40;
        
        // Create the SVG container
        const svg = d3.select("#tree")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", "translate(40,0)");
            
        // Create the tree layout
        const tree = d3.tree()
            .size([height, width - 160]);
            
        // Create the root node
        const root = d3.hierarchy(treeData, d => 
            d.type === 'directory' ? Object.values(d.children || {}) : null
        );
        
        // Assign positions to nodes
        tree(root);
        
        // Create links
        svg.selectAll(".link")
            .data(root.links())
            .join("path")
            .attr("class", "link")
            .attr("d", d3.linkHorizontal()
                .x(d => d.y)
                .y(d => d.x));
                
        // Create nodes
        const node = svg.selectAll(".node")
            .data(root.descendants())
            .join("g")
            .attr("class", "node")
            .attr("transform", d => `translate(${d.y},${d.x})`);
            
        // Add circles to nodes
        node.append("circle")
            .attr("r", 4)
            .style("fill", d => d.data.type === 'directory' ? "steelblue" : "#fff");
            
        // Add text labels
        node.append("text")
            .attr("dy", ".31em")
            .attr("x", d => d.children ? -6 : 6)
            .style("text-anchor", d => d.children ? "end" : "start")
            .text(d => d.data.name);
            
        // Add tooltips
        const tooltip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);
            
        node.on("mouseover", function(event, d) {
            let content = `<strong>${d.data.name}</strong><br>`;
            content += `Type: ${d.data.type}<br>`;
            if (d.data.size) {
                content += `Size: ${formatBytes(d.data.size)}<br>`;
            }
            if (d.data.modified) {
                content += `Modified: ${new Date(d.data.modified).toLocaleString()}`;
            }
            
            tooltip.html(content)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 10) + "px")
                .style("opacity", 1);
        })
        .on("mouseout", function(d) {
            tooltip.style("opacity", 0);
        });
        
        function formatBytes(bytes) {
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
            if (bytes === 0) return '0 Byte';
            const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
            return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
        }
    </script>
</body>
</html>
'''
        # Create temporary HTML file and open in browser
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
            f.write(html)
            webbrowser.open('file://' + os.path.abspath(f.name))

def scan_and_visualize(directory_path, max_depth=None, save_json_path=None):
    """
    Scan a directory, visualize it, and optionally save to JSON.
    
    Args:
        directory_path (str): Path to directory to scan
        max_depth (int, optional): Maximum depth to scan
        save_json_path (str, optional): Path to save JSON output
    """
    scanner = DirectoryScanner()
    scanner.scan(directory_path, max_depth=max_depth)
    
    # Save JSON if path provided
    if save_json_path:
        scanner.save_json(save_json_path)
    
    # Create visualization
    scanner.visualize()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Directory Visualization Tool')
    parser.add_argument('path', help='Directory path to scan')
    parser.add_argument('--max-depth', type=int, help='Maximum depth to scan')
    parser.add_argument('--save-json', help='Path to save JSON output')
    
    args = parser.parse_args()
    
    scan_and_visualize(args.path, args.max_depth, args.save_json)
