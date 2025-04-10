import sys

query_param_dict = {
    "page": {"valid": [1], "invalid": ["invalid", sys.maxsize, ""]},
    "format": {"valid": ["json", "xml", "yaml", ""], "invalid": ["invalid"]},
    # TODO api returns 406, empty shouldn't work i guess
    "sort": {"valid": ["lastUpdate", "additionDate", "name", "affiliation", "score"], "invalid": ["invalid", ""]},
    # TODO empty shouldn't work i guess
    "biotoolsID": {"valid": [], "invalid": ["invalid", ""]}
}