import sys

query_param_dict = {
    "page": {"valid": [1], "invalid": ["invalid", sys.maxsize, ""]},
    "format": {"valid": ["json", "xml", "yaml"], "invalid": ["invalid", ""]}, # TODO look fallbacks
    "sort": {"valid": ["lastUpdate", "additionDate", "name"], "invalid": ["invalid", ""]},
    # TODO affiliation and score
    "biotoolsID": {"valid": [], "invalid": ["invalid", ""]},
    "ord": {"valid": ["desc", "asc"], "invalid": ["invalid", ""]}  # TODO why does "" work, check invalid string
}
