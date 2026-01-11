# Creating Figures Using Graphviz DOT Format

This guide explains how to create and convert DOT files to PDF for your LaTeX paper.

## What is Graphviz DOT?

Graphviz is a graph visualization tool that uses DOT language to describe diagrams. It's perfect for flowcharts, architecture diagrams, and process flows.

## Installation

### Windows:
1. Download Graphviz from: https://graphviz.org/download/
2. Install the .msi file
3. Add to PATH (usually done automatically)

### macOS:
```bash
brew install graphviz
```

### Linux:
```bash
sudo apt-get install graphviz  # Ubuntu/Debian
sudo yum install graphviz       # CentOS/RHEL
```

## Converting DOT to PDF

### Method 1: Command Line (Recommended)

Navigate to the `figures/` directory and run:

```bash
# For Windows
dot -Tpdf fig1_methodology.dot -o fig1_methodology.pdf
dot -Tpdf fig2_architecture.dot -o fig2_architecture.pdf
dot -Tpdf fig3_prefect_flow.dot -o fig3_prefect_flow.pdf
dot -Tpdf fig4_containerization.dot -o fig4_containerization.pdf
dot -Tpdf fig5_cicd_pipeline.dot -o fig5_cicd_pipeline.pdf
```

### Method 2: Batch Script (Windows)

Create `convert_figures.bat`:

```batch
@echo off
cd figures
dot -Tpdf fig1_methodology.dot -o fig1_methodology.pdf
dot -Tpdf fig2_architecture.dot -o fig2_architecture.pdf
dot -Tpdf fig3_prefect_flow.dot -o fig3_prefect_flow.pdf
dot -Tpdf fig4_containerization.dot -o fig4_containerization.pdf
dot -Tpdf fig5_cicd_pipeline.dot -o fig5_cicd_pipeline.pdf
echo All figures converted!
pause
```

### Method 3: Shell Script (macOS/Linux)

Create `convert_figures.sh`:

```bash
#!/bin/bash
cd figures
dot -Tpdf fig1_methodology.dot -o fig1_methodology.pdf
dot -Tpdf fig2_architecture.dot -o fig2_architecture.pdf
dot -Tpdf fig3_prefect_flow.dot -o fig3_prefect_flow.pdf
dot -Tpdf fig4_containerization.dot -o fig4_containerization.pdf
dot -Tpdf fig5_cicd_pipeline.dot -o fig5_cicd_pipeline.pdf
echo "All figures converted!"
```

Make executable: `chmod +x convert_figures.sh`

## Customizing DOT Files

### Common Attributes:

**Node Styles:**
- `shape=box` - Rectangular box
- `shape=ellipse` - Ellipse
- `shape=cylinder` - Cylinder (for databases)
- `style=rounded` - Rounded corners
- `fillcolor="#color"` - Fill color
- `style="rounded,filled"` - Rounded and filled

**Graph Layout:**
- `rankdir=LR` - Left to right (horizontal)
- `rankdir=TB` - Top to bottom (vertical)
- `rankdir=RL` - Right to left
- `rankdir=BT` - Bottom to top

**Subgraphs (Clusters):**
- `subgraph cluster_name` - Creates a box around nodes
- `label="Title"` - Adds title to cluster
- `style=dashed` - Dashed border
- `style=bold` - Bold border

### Color Codes (IEEE-friendly grayscale):
- Light gray: `#e3f2fd`, `#f5f5f5`
- Medium gray: `#bbdefb`, `#e0e0e0`
- Dark gray: `#90caf9`, `#bdbdbd`
- For colored versions, use: `#22c55e` (green), `#6366f1` (blue), `#ef4444` (red)

## Editing DOT Files

### Option 1: Text Editor
- Open `.dot` files in any text editor
- Edit the labels, connections, and styles
- Save and regenerate PDF

### Option 2: Visual Editors
- **Graphviz Online:** https://dreampuf.github.io/GraphvizOnline/
- **Viz.js:** https://viz-js.com/
- **VS Code Extension:** "Graphviz Preview"

## Troubleshooting

### "dot: command not found"
- Ensure Graphviz is installed
- Add to PATH: `C:\Program Files\Graphviz\bin\` (Windows)
- Restart terminal/command prompt

### Output looks wrong
- Check DOT syntax (common errors: missing semicolons, unmatched quotes)
- Try different layout engines:
  - `dot` - Hierarchical layouts (default)
  - `neato` - Spring model layouts
  - `fdp` - Force-directed layouts
  - `circo` - Circular layouts

### Text too small/large
- Adjust `fontsize` attribute in nodes
- Default is 14pt, try 10-12pt for paper

### Boxes overlapping
- Add spacing: `nodesep=0.5` or `ranksep=1.0`
- Use subgraphs to group related nodes

## Advanced: Customizing for IEEE Format

For black and white figures:

```dot
digraph Example {
    node [shape=box, style="rounded,filled", fillcolor=white, color=black, fontcolor=black];
    edge [color=black];
    // ... rest of graph
}
```

For grayscale:

```dot
digraph Example {
    node [shape=box, style="rounded,filled", fillcolor="#f5f5f5", color="#424242"];
    edge [color="#757575"];
    // ... rest of graph
}
```

## Quick Reference

**Convert single file:**
```bash
dot -Tpdf input.dot -o output.pdf
```

**Convert all DOT files:**
```bash
# Windows PowerShell
Get-ChildItem *.dot | ForEach-Object { dot -Tpdf $_.Name -o ($_.BaseName + ".pdf") }

# Linux/macOS
for file in *.dot; do dot -Tpdf "$file" -o "${file%.dot}.pdf"; done
```

**Check if Graphviz is installed:**
```bash
dot -V
```

## Next Steps

1. Install Graphviz
2. Navigate to `figures/` folder
3. Run conversion commands
4. Verify PDFs are created
5. Compile LaTeX paper

The PDFs will automatically be included when you compile your LaTeX document!




