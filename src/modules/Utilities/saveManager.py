from modules.Main.abstractScheme import SchemeScreen
import json

def get_scheme_filepath(scheme_type: type):
    return f"resource/{scheme_type.__name__}.json"

def save_scheme_data(to_be_saved: SchemeScreen) -> None:
    
    file_path = get_scheme_filepath(type(to_be_saved))
    
    with open(file_path, "r") as outfile:
        data = json.load(outfile)
    
    data[to_be_saved.identifier_key] = to_be_saved.dict_data

    with open(file_path, "w") as outfile:
        json.dump(data, outfile)
    
def load_scheme_data_from_file(scheme_type: type, identifier_key: str) -> dict:

    if not issubclass(scheme_type, SchemeScreen):
            raise ValueError(f"Invalid scheme type: {scheme_type.__name__}")

    file_path = get_scheme_filepath(scheme_type)

    with open(file_path, "r") as outfile:
        data = json.load(outfile)
    
    if identifier_key not in data:
        default_data = scheme_type.default_data()
        data[identifier_key] = default_data
        with open(file_path, "w") as outfile:
            json.dump(data, outfile)
        
        return default_data
        
    return data[identifier_key]

    


