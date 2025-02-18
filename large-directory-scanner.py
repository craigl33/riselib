from pathlib import Path
import os
import json
from collections import defaultdict
import webbrowser
import tempfile
from datetime import datetime
import humanize

class EnhancedDirectoryScanner:
    def __init__(self):
        self.stats = {
            'total_files': 0,
            'total_dirs': 0,
            'total_size': 0,
            'file_types': defaultdict(int)
        }
        self.structure = {}

    def scan_directory(self, root_path, max_depth=None, exclude_patterns=None, 
                      min_size=0, group_by='type'):
        """
        Scan directory with enhanced organization and filtering.
        
        Args:
            root_path: Path to scan
            max_depth: Maximum directory depth
            exclude_patterns: Patterns to exclude
            min_size: Minimum file size to include (bytes)
            group_by: How to group files ('type', 'size', 'date', 'none')
        """
        root_path = Path(root_path)
        exclude_patterns = exclude_patterns or []
        self.structure = self._scan_recursive(root_path, 0, max_depth, 
                                           exclude_patterns, min_size)
        
        if group_by == 'type':
            self.structure = self._group_by_type(self.structure)
        elif group_by == 'size':
            self.structure = self._group_by_size(self.structure)
        elif group_by == 'date':
            self.structure = self._group_by_date(self.structure)

    def _scan_recursive(self, path, current_depth, max_depth, exclude_patterns, min_size):
        """Recursively scan directory with detailed information."""
        if max_depth is not None and current_depth > max_depth:
            return None

        if any(pattern in str(path) for pattern in exclude_patterns):
            return None

        try:
            if path.is_file():
                size = path.stat().st_size
                if size < min_size:
                    return None
                    
                self.stats['total_files'] += 1
                self.stats['total_size'] += size
                self.stats['file_types'][path.suffix.lower()] += 1
                
                return {
                    'type': 'file',
                    'name': path.name,
                    'size': size,
                    'modified': datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
                    'extension': path.suffix.lower()
                }
            elif path.is_dir():
                self.stats['total_dirs'] += 1
                contents = {}
                
                try:
                    for item in sorted(path.iterdir()):
                        result = self._scan_recursive(item, current_depth + 1, 
                                                   max_depth, exclude_patterns, min_size)
                        if result:
                            contents[item.name] = result
                except PermissionError:
                    return {
                        'type': 'error',
                        'message': f'Permission denied: {path}'
                    }
                
                return {
                    'type': 'directory',
                    'name': path.name,
                    'contents': contents
                }
                
        except Exception as e:
            return {
                'type': 'error',
                'message': f'Error processing {path}: {str(e)}'
            }

    def _group_by_type(self, structure):
        """Group files by their extension."""
        if isinstance(structure, dict) and structure.get('type') == 'directory':
            grouped = defaultdict(list)
            for name, item in structure.get('contents', {}).items():
                if isinstance(item, dict) and item.get('type') == 'file':
                    ext = item.get('extension', '').lower() or 'no_extension'
                    grouped[ext].append(item)
                elif isinstance(item, dict) and item.get('type') == 'directory':
                    grouped['directories'].append(self._group_by_type(item))
            
            return {
                'type': 'directory',
                'name': structure.get('name'),
                'contents': dict(grouped)
            }
        return structure

    def _group_by_size(self, structure):
        """Group files by size ranges."""
        size_ranges = {
            'tiny': (0, 1024),  # 0-1KB
            'small': (1024, 1024*1024),  # 1KB-1MB
            'medium': (1024*1024, 1024*1024*10),  # 1MB-10MB
            'large': (1024*1024*10, 1024*1024*100),  # 10MB-100MB
            'huge': (1024*1024*100, float('inf'))  # >100MB
        }
        
        if isinstance(structure, dict) and structure.get('type') == 'directory':
            grouped = defaultdict(list)
            for name, item in structure.get('contents', {}).items():
                if isinstance(item, dict) and item.get('type') == 'file':
                    size = item.get('size', 0)
                    for range_name, (min_size, max_size) in size_ranges.items():
                        if min_size <= size < max_size:
                            grouped[range_name].append(item)
                            break
                elif isinstance(item, dict) and item.get('type') == 'directory':
                    grouped['directories'].append(self._group_by_size(item))
            
            return {
                'type': 'directory',
                'name': structure.get('name'),
                'contents': dict(grouped)
            }
        return structure

    def generate_html(self):
        """Generate an interactive HTML visualization."""
        html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Directory Structure Visualization</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0;
            display: flex;
            height: 100vh;
        }
        #sidebar {
            width: 300px;
            padding: 20px;
            background: #f5f5f5;
            overflow-y: auto;
            border-right: 1px solid #ddd;
        }
        #main {
            flex-grow: 1;
            padding: 20px;
            overflow: auto;
        }
        .node {
            cursor: pointer;
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
        .file circle {
            fill: #fff;
            stroke: #4CAF50;
        }
        .directory circle {
            fill: #fff;
            stroke: #2196F3;
        }
        .node--internal text {
            text-shadow: 0 1px 0 #fff, 0 -1px 0 #fff, 1px 0 0 #fff, -1px 0 0 #fff;
        }
        .tooltip {
            position: absolute;
            padding: 8px;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
            pointer-events: none;
            font-size: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .search-box {
            width: 100%;
            padding: 8px;
            margin-bottom: 16px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div id="sidebar">
        <h2>Directory Analysis</h2>
        <input type="text" class="search-box" placeholder="Search files and folders..." id="search">
        <div id="stats"></div>
    </div>
    <div id="main">
        <div id="chart"></div>
    </div>

    <script>
        const data = {data_json};
        const stats = {stats_json};
        
        // Render stats
        const statsDiv = document.getElementById('stats');
        statsDiv.innerHTML = `
            <h3>Statistics</h3>
            <p>Total Files: ${stats.total_files}</p>
            <p>Total Directories: ${stats.total_dirs}</p>
            <p>Total Size: ${humanizeBytes(stats.total_size)}</p>
            <h3>File Types:</h3>
            <ul>${Object.entries(stats.file_types)
                .map(([ext, count]) => `<li>${ext || 'no extension'}: ${count}</li>`)
                .join('')}</ul>
        `;

        // Set up the D3.js visualization
        const margin = {top: 20, right: 90, bottom: 30, left: 90};
        const width = window.innerWidth - 300 - margin.left - margin.right;
        const height = window.innerHeight - margin.top - margin.bottom;

        // Create a tooltip div
        const tooltip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);

        const svg = d3.select("#chart")
            .append("svg")
            .attr("width", width + margin.right + margin.left)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        // Declares a tree layout and assigns the size
        const treemap = d3.tree().size([height, width]);

        // Assigns parent, children, height, depth
        const root = d3.hierarchy(data, d => {
            if (d.type === 'directory') {
                return Object.values(d.contents || {});
            }
            return null;
        });

        root.x0 = height / 2;
        root.y0 = 0;

        // Collapse after the second level
        root.children.forEach(collapse);

        update(root);

        // Collapse the node and all it's children
        function collapse(d) {
            if(d.children) {
                d._children = d.children;
                d._children.forEach(collapse);
                d.children = null;
            }
        }

        function update(source) {
            // Assigns the x and y position for the nodes
            const treeData = treemap(root);

            // Compute the new tree layout.
            const nodes = treeData.descendants();
            const links = treeData.descendants().slice(1);

            // Normalize for fixed-depth.
            nodes.forEach(d => { d.y = d.depth * 180; });

            // Update the nodes...
            const node = svg.selectAll('g.node')
                .data(nodes, d => d.id || (d.id = ++i));

            // Enter any new nodes at the parent's previous position.
            const nodeEnter = node.enter().append('g')
                .attr('class', 'node')
                .attr("transform", d => `translate(${source.y0},${source.x0})`)
                .on('click', click)
                .on('mouseover', function(event, d) {
                    tooltip.transition()
                        .duration(200)
                        .style("opacity", .9);
                    
                    let tooltipContent = `<strong>${d.data.name}</strong><br/>`;
                    if (d.data.type === 'file') {
                        tooltipContent += `Size: ${humanizeBytes(d.data.size)}<br/>`;
                        tooltipContent += `Modified: ${new Date(d.data.modified).toLocaleString()}`;
                    }
                    
                    tooltip.html(tooltipContent)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 28) + "px");
                })
                .on('mouseout', function(d) {
                    tooltip.transition()
                        .duration(500)
                        .style("opacity", 0);
                });

            nodeEnter.append('circle')
                .attr('class', d => d.data.type)
                .attr('r', 1e-6)
                .style("fill", d => d._children ? "lightsteelblue" : "#fff");

            nodeEnter.append('text')
                .attr("dy", ".35em")
                .attr("x", d => d.children || d._children ? -13 : 13)
                .attr("text-anchor", d => d.children || d._children ? "end" : "start")
                .text(d => d.data.name)
                .style("fill-opacity", 1e-6);

            // Update
            const nodeUpdate = nodeEnter.merge(node);

            nodeUpdate.transition()
                .duration(750)
                .attr("transform", d => `translate(${d.y},${d.x})`);

            nodeUpdate.select('circle')
                .attr('r', 6)
                .style("fill", d => d._children ? "lightsteelblue" : "#fff");

            nodeUpdate.select('text')
                .style("fill-opacity", 1);

            // Remove any exiting nodes
            const nodeExit = node.exit().transition()
                .duration(750)
                .attr("transform", d => `translate(${source.y},${source.x})`)
                .remove();

            nodeExit.select('circle')
                .attr('r', 1e-6);

            nodeExit.select('text')
                .style('fill-opacity', 1e-6);

            // Update the links...
            const link = svg.selectAll('path.link')
                .data(links, d => d.id);

            // Enter any new links at the parent's previous position.
            const linkEnter = link.enter().insert('path', "g")
                .attr("class", "link")
                .attr('d', d => {
                    const o = {x: source.x0, y: source.y0};
                    return diagonal(o, o);
                });

            // UPDATE
            const linkUpdate = linkEnter.merge(link);

            // Transition back to the parent element position
            linkUpdate.transition()
                .duration(750)
                .attr('d', d => diagonal(d, d.parent));

            // Remove any exiting links
            const linkExit = link.exit().transition()
                .duration(750)
                .attr('d', d => {
                    const o = {x: source.x, y: source.y};
                    return diagonal(o, o);
                })
                .remove();

            // Store the old positions for transition.
            nodes.forEach(d => {
                d.x0 = d.x;
                d.y0 = d.y;
            });
        }

        // Creates a curved (diagonal) path from parent to the child nodes
        function diagonal(s, d) {
            return `M ${s.y} ${s.x}
                    C ${(s.y + d.y) / 2} ${s.x},
                      ${(s.y + d.y) / 2} ${d.x},
                      ${d.y} ${d.x}`;
        }

        // Toggle children on click.
        function click(event, d) {
            if (d.children) {
                d._children = d.children;
                d.children = null;
            } else {
                d.children = d._children;
                d._children = null;
            }
            update(d);
        }

        // Search functionality
        document.getElementById('search').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            
            function searchNode(node) {
                if (node.data.name.toLowerCase().includes(searchTerm)) {
                    // Expand all parent nodes
                    let parent = node.parent;
                    while (parent) {
                        if (parent._children) {
                            parent.children = parent._children;
                            parent._children = null;
                        }
                        parent = parent.parent;
                    }
                    update(root);
                    return true;
                }
                
                if (node.children) {
                    return node.children.some(searchNode);
                } else if (node._children) {
                    return node._children.some(child => 
                        child.data.name.toLowerCase().includes(searchTerm)
                    );
                }
                return false;
            }
            
            searchNode(root);
        });

        function humanizeBytes(bytes) {
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
            if (bytes === 0) return '0 Byte';
            const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
            return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
        }

        // Handle window resize
        window.addEventListener('resize', function() {
            const newWidth = window.innerWidth - 300 - margin.left - margin.right;
            const newHeight = window.innerHeight - margin.top - margin.bottom;
            
            svg.attr("width", newWidth + margin.right + margin.left)
               .attr("height", newHeight + margin.top + margin.bottom);
            
            treemap.size([newHeight, newWidth]);
            update(root);
        });
            
        function humanizeBytes(bytes) {
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
            if (bytes === 0) return '0 Byte';
            const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
            return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
        }
    </script>
</body>
</html>
'''
        return html_template.replace(
            '{data_json}', json.dumps(self.structure)
        ).replace(
            '{stats_json}', json.dumps(self.stats)
        )

def visualize_large_directory(path, output_format='html', **kwargs):
    """
    Visualize a large directory structure with various output formats.
    
    Args:
        path: Directory path to scan
        output_format: 'html', 'json', or 'text'
        **kwargs: Additional arguments for scanning
    """
    scanner = EnhancedDirectoryScanner()
    scanner.scan_directory(path, **kwargs)
    
    if output_format == 'html':
        # Create and open HTML visualization
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
            f.write(scanner.generate_html())
            webbrowser.open('file://' + os.path.abspath(f.name))
    elif output_format == 'json':
        # Return JSON structure
        return json.dumps(scanner.structure, indent=2)
    elif output_format == 'text':
        # Return text representation
        def print_tree(structure, indent=0):
            result = []
            if isinstance(structure, dict):
                if structure.get('type') == 'file':
                    size = humanize.naturalsize(structure.get('size', 0))
                    result.append(f"{'  ' * indent}├── {structure['name']} ({size})")
                elif structure.get('type') == 'directory':
                    result.append(f"{'  ' * indent}├── {structure['name']}/")
                    for item in structure.get('contents', {}).values():
                        result.extend(print_tree(item, indent + 1))
            return result
        
        return '\n'.join(print_tree(scanner.structure))

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualize large directory structures')
    parser.add_argument('path', help='Directory path to scan')
    parser.add_argument('--max-depth', type=int, help='Maximum depth to scan')
    parser.add_argument('--min-size', type=int, default=0, help='Minimum file size to include (bytes)')
    parser.add_argument('--group-by', choices=['type', 'size', 'date', 'none'], 
                       default='type', help='How to group files')
    parser.add_argument('--format', choices=['html', 'json', 'text'], 
                       default='html', help='Output format')
    parser.add_argument('--exclude', nargs='+', default=['.git', '__pycache__', 'node_modules'],
                       help='Patterns to exclude')
    
    args = parser.parse_args()
    
    result = visualize_large_directory(
        args.path,
        output_format=args.format,
        max_depth=args.max_depth,
        min_size=args.min_size,
        group_by=args.group_by,
        exclude_patterns=args.exclude
    )
    
    if args.format in ['json', 'text']:
        print(result)
