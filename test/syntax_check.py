import ast
import sys
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent
    python_files = list(root.glob("**/*.py"))
    
    print(f"Checking syntax for {len(python_files)} Python files...")
    has_error = False
    
    for path in python_files:
        # Bỏ qua các file trong .venv hoặc build/dist nếu có
        if ".venv" in path.parts or "node_modules" in path.parts:
            continue
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            ast.parse(content, filename=str(path))
        except Exception as e:
            print(f"Syntax error in {path.relative_to(root)}: {e}")
            has_error = True
            
    if has_error:
        print("Syntax check failed.")
        sys.exit(1)
    else:
        print("All Python files have valid syntax!")
        sys.exit(0)

if __name__ == "__main__":
    main()
