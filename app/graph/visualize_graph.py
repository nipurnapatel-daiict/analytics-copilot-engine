"""
Purpose: Generate LangGraph workflow visualization and extract Mermaid structures.
"""
import os 
from app.graph.graph_builder import GraphBuilder

def generate_workflow_diagrams():
    print("Compiling State Machine Topology for Verification...")
    
    compiled_graph = GraphBuilder.build_graph()
    mermaid_syntax_code = compiled_graph.get_graph().draw_mermaid()
    
    assets_dir = "assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    mermaid_file_path = os.path.join(assets_dir, "langgraph_workflow.mmd")
    with open(mermaid_file_path, "w", encoding="utf-8") as mmd_file:
        mmd_file.write(mermaid_syntax_code)
    print(f"Success! Mermaid code syntax saved locally to: {mermaid_file_path}")

    print("\nRAW MERMAID SYNTAX FLOWCHART TEXT BLOCK ")
    print(mermaid_syntax_code)
    print("-------------------\n")
    print(" Copy the string block above and paste it directly into your submission documentation.")

    try:
        png_binary_bytes = compiled_graph.get_graph().draw_mermaid_png()
        
        output_image_file = os.path.join(assets_dir, "langgraph_workflow.png")
        
        with open(output_image_file, "wb") as output_image:
            output_image.write(png_binary_bytes)
        print(f"Success! Visual image artifact saved locally to: {output_image_file}")
    except Exception as img_err:
        print(f" Graphic PNG compilation skipped: {img_err}")
        print(" Note: Missing graphviz or pygraphviz packages. The raw text syntax code above satisfies the milestone criteria.")

if __name__ == "__main__":
    generate_workflow_diagrams()
