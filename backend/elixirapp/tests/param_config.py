import sys

query_param_dict = {
    "page": {"valid": [1], "invalid": ["invalid", sys.maxsize, ""]},
    "format": {"valid": ["json", "xml", "yaml"], "invalid": ["invalid", ""]},
    "sort": {"valid": ["lastUpdate", "additionDate", "name"], "invalid": ["invalid", ""]},
    "biotoolsID": {"valid": [], "invalid": ["invalid", ""]},
    "ord": {"valid": ["desc", "asc"], "invalid": ["invalid", ""]}
}
