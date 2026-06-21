from app.tools.sql_tool import sql_tool

def run_analytical_test():
    print("Testing Analytical SQL Engine...")
    
    test_queries = [
        "What is the total revenue?",
        "Which city has the highest number of customers?",
        "How many completed orders exist?"
    ]
    
    for query in test_queries:
        print(f"\nEvaluating Prompt: '{query}'")
        try:
            response = sql_tool.invoke({"question": query})
            print("Execution Successful!")
            print(f"Generated SQL -> {response['query']}")
            print(f"Dataset Output -> {response['result']}")
        except Exception as err:
            print(f"Validation Block Triggered: {err}")

if __name__ == "__main__":
    run_analytical_test()
