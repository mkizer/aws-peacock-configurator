import json5 as json_lib
import os

def test_json_rw():
    filepath = os.path.join("examples", "CoSD_SSO_Configuration.json")
    print(f"Testing read on {filepath}")
    
    try:
        with open(filepath, 'r') as f:
            data = json_lib.load(f)
        
        print("Read success. Item count:", len(data))
        
        # Test write
        output_path = "examples/test_output.json"
        with open(output_path, 'w') as f:
            json_lib.dump(data, f, indent=2)
            
        print(f"Write success to {output_path}")
        
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_json_rw()
