# Credit for this script to Alban Gaignard
# https://github.com/albangaignard
import json

def rdfize(json_entry):
    """
    Transforms a biotools json entry into RDF, and returns a JSON-LD serialization. The following fields
    are covered: contact, publication, EDAM topic, EDAM operation, EDAM inputs & outputs.
    """

    entry = json_entry

    try:

        ctx = {
            "@context": {
                "@base": "https://bio.tools/",
                "biotools": "https://bio.tools/ontology/",
                "edam": "http://edamontology.org/",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "sc": "http://schema.org/",
                "bsc": "http://bioschemas.org/",
                "description": "sc:description",
                "name": "sc:name",
                "homepage": "sc:url",
                "toolType": "sc:additionalType",
                "primaryContact": "biotools:primaryContact",
                "author": "sc:author",
                "provider": "sc:provider",
                "contributor": "sc:contributor",
                "funder": "sc:funder",
                "hasPublication": "sc:citation",
                "hasTopic": "sc:applicationSubCategory",
                "hasOperation": "sc:featureList",
                "hasInputData": "edam:has_input",
                "hasOutputData": "edam:has_output",
                "license": "sc:license",
                "version": "sc:version",
                "isAccessibleForFree": "sc:isAccessibleForFree",
                "operatingSystem": "sc:operatingSystem",
                "hasApiDoc": "sc:softwareHelp",
                "hasGenDoc": "sc:softwareHelp",
                "hasTermsOfUse": "sc:termsOfService",
            }
        }
        entry.update(ctx)

        entry["@id"] = str(entry["biotoolsID"])
        # entry['@type'] = ['bsc:Tool','sc:SoftwareApplication']
        entry["@type"] = ["sc:SoftwareApplication"]
        entry["applicationCategory"] = "Computational science tool"
        entry["primaryContact"] = []
        entry["author"] = []
        entry["contributor"] = []
        entry["provider"] = []
        entry["funder"] = []

        for credit in entry["credit"]:
            # print(credit)

            ## Retrieving FUNDERS
            if "typeEntity" in credit.keys() and credit["typeEntity"]:
                if "Funding agency" in credit["typeEntity"]:
                    sType = "schema:Organization"
                    if "orcidid" in credit.keys() and credit["orcidid"] != None:
                        if not "funder" in entry.keys():
                            entry["funder"] = {"@id": credit["orcidid"], "@type": sType}
                        else:
                            entry["funder"].append(
                                {"@id": credit["orcidid"], "@type": sType}
                            )
                    elif "name" in credit.keys() and credit["name"] != None:
                        if not "funder" in entry.keys():
                            entry["funder"] = [credit["name"]]
                        else:
                            entry["funder"].append(credit["name"])

            # Retrieving CONTRIBUTORS, PROVIDERS, DEVELOPERS
            if credit["typeRole"]:
                if "Developer" in credit["typeRole"]:
                    # print("**** DEVELOPER ****")
                    # print(credit['name'])
                    if "typeEntity" in credit.keys() and credit["typeEntity"]:
                        if "Person" in credit["typeEntity"]:
                            sType = "schema:Person"
                        else:
                            sType = "schema:Organization"
                        if "orcidid" in credit.keys() and credit["orcidid"] != None:
                            if not "author" in entry.keys():
                                entry["author"] = {
                                    "@id": credit["orcidid"],
                                    "@type": sType,
                                }
                            else:
                                entry["author"].append(
                                    {"@id": credit["orcidid"], "@type": sType}
                                )
                        elif "name" in credit.keys() and credit["name"] != None:
                            if not "author" in entry.keys():
                                entry["author"] = [credit["name"]]
                            else:
                                entry["author"].append(credit["name"])
                    else:
                        if "name" in credit.keys() and credit["name"] != None:
                            if not "author" in entry.keys():
                                entry["author"] = [credit["name"]]
                            else:
                                entry["author"].append(credit["name"])

                if "Provider" in credit["typeRole"]:
                    # print("**** PROVIDER ****")
                    # print(credit['name'])
                    if "typeEntity" in credit.keys() and credit["typeEntity"]:
                        if "Person" in credit["typeEntity"]:
                            sType = "schema:Person"
                        else:
                            sType = "schema:Organization"

                        if "orcidid" in credit.keys() and credit["orcidid"] != None:
                            if not "provider" in entry.keys():
                                entry["provider"] = {
                                    "@id": credit["orcidid"],
                                    "@type": sType,
                                }
                                # if 'name' in credit.keys() and credit['name'] != None:
                                #    entry['author_person']['name'] = credit['name']
                            else:
                                entry["provider"].append(
                                    {"@id": credit["orcidid"], "@type": sType}
                                )
                        elif "name" in credit.keys() and credit["name"] != None:
                            if not "provider" in entry.keys():
                                entry["provider"] = [credit["name"]]
                            else:
                                entry["provider"].append(credit["name"])
                    else:
                        if "name" in credit.keys() and credit["name"] != None:
                            if not "provider" in entry.keys():
                                entry["provider"] = [credit["name"]]
                            else:
                                entry["provider"].append(credit["name"])

                if "Contributor" in credit["typeRole"]:
                    # print("**** CONTRIBUTOR ****")
                    # print(credit['name'])

                    if "typeEntity" in credit.keys() and credit["typeEntity"]:
                        if "Person" in credit["typeEntity"]:
                            sType = "schema:Person"
                        else:
                            sType = "schema:Organization"

                        if "orcidid" in credit.keys() and credit["orcidid"] != None:
                            if not "contributor" in entry.keys():
                                entry["contributor"] = {
                                    "@id": credit["orcidid"],
                                    "@type": sType,
                                }
                            else:
                                entry["contributor"].append(
                                    {"@id": credit["orcidid"], "@type": sType}
                                )
                        elif "name" in credit.keys() and credit["name"] != None:
                            if not "contributor" in entry.keys():
                                entry["contributor"] = [credit["name"]]
                            else:
                                entry["contributor"].append(credit["name"])
                    else:
                        if "name" in credit.keys() and credit["name"] != None:
                            if not "contributor" in entry.keys():
                                entry["contributor"] = [credit["name"]]
                            else:
                                entry["contributor"].append(credit["name"])

                if "Primary contact" in credit["typeRole"]:
                    # print("**** CONTRIBUTOR ****")
                    # print(credit['name'])

                    if "typeEntity" in credit.keys() and credit["typeEntity"]:
                        if "Person" in credit["typeEntity"]:
                            sType = "schema:Person"
                        else:
                            sType = "schema:Organization"

                        if "orcidid" in credit.keys() and credit["orcidid"] != None:
                            if not "primaryContact" in entry.keys():
                                entry["primaryContact"] = {
                                    "@id": credit["orcidid"],
                                    "@type": sType,
                                }
                            else:
                                entry["primaryContact"].append(
                                    {"@id": credit["orcidid"], "@type": sType}
                                )
                        elif "name" in credit.keys() and credit["name"] != None:
                            if not "primaryContact" in entry.keys():
                                entry["primaryContact"] = [credit["name"]]
                            else:
                                entry["primaryContact"].append(credit["name"])
                    else:
                        if "name" in credit.keys() and credit["name"] != None:
                            if not "primaryContact" in entry.keys():
                                entry["primaryContact"] = [credit["name"]]
                            else:
                                entry["primaryContact"].append(credit["name"])

        for publication in entry["publication"]:
            if publication["pmid"]:
                if not "hasPublication" in entry.keys():
                    # entry['hasPublication'] = [{"@id": 'pubmed:' + publication['pmid']}]
                    entry["hasPublication"] = ["pubmed:" + publication["pmid"]]
                else:
                    # entry['hasPublication'].append({"@id": 'pubmed:' + publication['pmid']})
                    entry["hasPublication"].append("pubmed:" + publication["pmid"])
            if publication["pmcid"]:
                if not "hasPublication" in entry.keys():
                    entry["hasPublication"] = ["pmcid:" + publication["pmcid"]]
                else:
                    entry["hasPublication"].append("pmcid:" + publication["pmcid"])
            if publication["doi"]:
                if not ("<" in publication["doi"] or ">" in publication["doi"]):
                    if not "hasPublication" in entry.keys():
                        entry["hasPublication"] = [
                            {
                                "@id": "https://doi.org/" + publication["doi"],
                                "@type": "sc:CreativeWork",
                            }
                        ]
                    else:
                        entry["hasPublication"].append(
                            {
                                "@id": "https://doi.org/" + publication["doi"],
                                "@type": "sc:CreativeWork",
                            }
                        )

        for item in entry["function"]:
            for op in item["operation"]:
                if not "hasOperation" in entry.keys():
                    entry["hasOperation"] = [{"@id": op["uri"]}]
                else:
                    entry["hasOperation"].append({"@id": op["uri"]})

            for input in item["input"]:
                if not "hasInputData" in entry.keys():
                    entry["hasInputData"] = [{"@id": input["data"]["uri"]}]
                else:
                    entry["hasInputData"].append({"@id": input["data"]["uri"]})

            for output in item["output"]:
                if not "hasOutputData" in entry.keys():
                    entry["hasOutputData"] = [{"@id": output["data"]["uri"]}]
                else:
                    entry["hasOutputData"].append({"@id": output["data"]["uri"]})

        for item in entry["topic"]:
            if not "hasTopic" in entry.keys():
                entry["hasTopic"] = [{"@id": item["uri"]}]
            else:
                entry["hasTopic"].append({"@id": item["uri"]})

        if entry["cost"]:
            for item in entry["cost"]:
                if not "isAccessibleForFree" in entry.keys():
                    if "Free" in entry["cost"]:
                        entry["isAccessibleForFree"] = True
                    else:
                        entry["isAccessibleForFree"] = False

        for item in entry["documentation"]:
            if "type" in item.keys() and item["type"]:
                item["url"] = item["url"].replace("|", "%7C")
                if "API" in item["type"]:
                    if not "hasApiDoc" in entry.keys():
                        entry["hasApiDoc"] = [{"@id": item["url"]}]
                    else:
                        entry["hasApiDoc"].append({"@id": item["url"]})
                elif "Terms" in item["type"]:
                    if not "hasTermsOfUse" in entry.keys():
                        entry["hasTermsOfUse"] = [{"@id": item["url"]}]
                    else:
                        entry["hasTermsOfUse"].append({"@id": item["url"]})
                else:
                    if not "hasGenDoc" in entry.keys():
                        entry["hasGenDoc"] = [{"@id": item["url"]}]
                    else:
                        entry["hasGenDoc"].append({"@id": item["url"]})

    except KeyError as error:
        #print(error)
        return {}
    raw_jld = json.dumps(entry, indent=4, sort_keys=True)
    return raw_jld
