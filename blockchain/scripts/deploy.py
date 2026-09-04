import os
import json
import solcx

def deploy_and_save():
    print("Installing solc...")
    solcx.install_solc('0.8.19')
    solcx.set_solc_version('0.8.19')
    
    contract_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "contracts", "ContentRegistry.sol")
    print(f"Compiling {contract_path}...")
    
    with open(contract_path, "r") as file:
        contract_source = file.read()

    compiled_sol = solcx.compile_standard(
        {
            "language": "Solidity",
            "sources": {"ContentRegistry.sol": {"content": contract_source}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                    }
                }
            },
        }
    )

    contract_interface = compiled_sol["contracts"]["ContentRegistry.sol"]["ContentRegistry"]
    abi = contract_interface["abi"]
    bytecode = contract_interface["evm"]["bytecode"]["object"]
    
    output_data = {
        "abi": abi,
        "bytecode": bytecode
    }
    
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "contracts", "ContentRegistry.json")
    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=4)
        
    print(f"Compilation successful! ABI and bytecode saved to {output_path}")

if __name__ == "__main__":
    deploy_and_save()
