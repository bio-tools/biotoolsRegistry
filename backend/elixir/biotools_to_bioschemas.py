# Credit for this script to Alban Gaignard
# https://github.com/albangaignard
import json


def rdfize(entry):
    """
    Transforms a biotools json entry into RDF, and returns a JSON-LD serialization. The following fields
    are covered: contact, publication, EDAM topic, EDAM operation, EDAM inputs & outputs.
    """
    jsonld = {}

    try:
        ctx = {
            "@context": {
                "@base": "https://bio.tools/",
                "biotools": "https://bio.tools/ontology/",
                "edam": "http://edamontology.org/",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "sc": "http://schema.org/",
                "dct": "http://purl.org/dc/terms/",
                "bsc": "http://bioschemas.org/",
                "bsct": "http://bioschemas.org/types/",
                "description": "sc:description",
                "name": "sc:name",
                "identifier": "sc:identifier",
                "sameAs": "sc:sameAs",
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
                "hasInputData": "bsc:input",
                "hasOutputData": "bsc:output",
                "license": "sc:license",
                "version": "sc:softwareVersion",
                "isAccessibleForFree": "sc:isAccessibleForFree",
                "operatingSystem": "sc:operatingSystem",
                "hasApiDoc": "sc:softwareHelp",
                "hasGenDoc": "sc:softwareHelp",
                "hasTermsOfUse": "sc:termsOfService",
                "conformsTo": "dct:conformsTo",
            }
        }
        objects = []
        graph = {"@graph": objects}
        jsonld.update(ctx)
        jsonld.update(graph)

        tool = {}
        tool["@id"] = str(entry["biotoolsID"])
        tool["@type"] = ["sc:SoftwareApplication"]
        tool["applicationCategory"] = "Computational science tool"
        tool["primaryContact"] = []
        tool["author"] = []
        tool["contributor"] = []
        tool["provider"] = []
        tool["funder"] = []
        tool[
            "conformsTo"
        ] = "https://bioschemas.org/profiles/ComputationalTool/1.0-RELEASE"

        if entry.get("credit"):
            for credit in entry["credit"]:
                # print(credit)
                ## Retrieving FUNDERS
                if "typeEntity" in credit.keys() and credit["typeEntity"]:
                    if "Funding agency" in credit["typeEntity"]:
                        sType = "schema:Organization"
                        if "orcidid" in credit.keys() and credit["orcidid"] is not None:
                            if not "funder" in tool.keys():
                                tool["funder"] = {
                                    "@id": credit["orcidid"],
                                    "@type": sType,
                                }
                            else:
                                tool["funder"].append(
                                    {"@id": credit["orcidid"], "@type": sType}
                                )
                        elif "name" in credit.keys() and credit["name"] is not None:
                            if not "funder" in tool.keys():
                                tool["funder"] = [credit["name"]]
                            else:
                                tool["funder"].append(credit["name"])

                # Retrieving CONTRIBUTORS, PROVIDERS, DEVELOPERS
                if credit.get("typeRole"):
                    if "Developer" in credit["typeRole"]:
                        # print("**** DEVELOPER ****")
                        # print(credit['name'])
                        if "typeEntity" in credit.keys() and credit["typeEntity"]:
                            if "Person" in credit["typeEntity"]:
                                sType = "schema:Person"
                            else:
                                sType = "schema:Organization"
                            if "orcidid" in credit.keys() and credit["orcidid"] is not None:
                                if not "author" in tool.keys():
                                    tool["author"] = {
                                        "@id": credit["orcidid"],
                                        "@type": sType,
                                    }
                                else:
                                    tool["author"].append(
                                        {"@id": credit["orcidid"], "@type": sType}
                                    )
                            elif "name" in credit.keys() and credit["name"] is not None:
                                if not "author" in tool.keys():
                                    tool["author"] = [credit["name"]]
                                else:
                                    tool["author"].append(credit["name"])
                        else:
                            if "name" in credit.keys() and credit["name"] is not None:
                                if not "author" in tool.keys():
                                    tool["author"] = [credit["name"]]
                                else:
                                    tool["author"].append(credit["name"])

                    if "Provider" in credit["typeRole"]:
                        # print("**** PROVIDER ****")
                        # print(credit['name'])
                        if "typeEntity" in credit.keys() and credit["typeEntity"]:
                            if "Person" in credit["typeEntity"]:
                                sType = "schema:Person"
                            else:
                                sType = "schema:Organization"

                            if "orcidid" in credit.keys() and credit["orcidid"] is not None:
                                if not "provider" in tool.keys():
                                    tool["provider"] = {
                                        "@id": credit["orcidid"],
                                        "@type": sType,
                                    }
                                else:
                                    tool["provider"].append(
                                        {"@id": credit["orcidid"], "@type": sType}
                                    )
                            elif "name" in credit.keys() and credit["name"] is not None:
                                if not "provider" in tool.keys():
                                    tool["provider"] = [credit["name"]]
                                else:
                                    tool["provider"].append(credit["name"])
                        else:
                            if "name" in credit.keys() and credit["name"] is not None:
                                if not "provider" in tool.keys():
                                    tool["provider"] = [credit["name"]]
                                else:
                                    tool["provider"].append(credit["name"])

                    if "Contributor" in credit["typeRole"]:

                        if "typeEntity" in credit.keys() and credit["typeEntity"]:
                            if "Person" in credit["typeEntity"]:
                                sType = "schema:Person"
                            else:
                                sType = "schema:Organization"

                            if "orcidid" in credit.keys() and credit["orcidid"] is not None:
                                if not "contributor" in tool.keys():
                                    tool["contributor"] = {
                                        "@id": credit["orcidid"],
                                        "@type": sType,
                                    }
                                else:
                                    tool["contributor"].append(
                                        {"@id": credit["orcidid"], "@type": sType}
                                    )
                            elif "name" in credit.keys() and credit["name"] is not None:
                                if not "contributor" in tool.keys():
                                    tool["contributor"] = [credit["name"]]
                                else:
                                    tool["contributor"].append(credit["name"])
                        else:
                            if "name" in credit.keys() and credit["name"] is not None:
                                if not "contributor" in tool.keys():
                                    tool["contributor"] = [credit["name"]]
                                else:
                                    tool["contributor"].append(credit["name"])

                    if "Primary contact" in credit["typeRole"]:
                        if "typeEntity" in credit.keys() and credit["typeEntity"]:
                            if "Person" in credit["typeEntity"]:
                                sType = "schema:Person"
                            else:
                                sType = "schema:Organization"

                            if "orcidid" in credit.keys() and credit["orcidid"] is not None:
                                if not "primaryContact" in tool.keys():
                                    tool["primaryContact"] = {
                                        "@id": credit["orcidid"],
                                        "@type": sType,
                                    }
                                else:
                                    tool["primaryContact"].append(
                                        {"@id": credit["orcidid"], "@type": sType}
                                    )
                            elif "name" in credit.keys() and credit["name"] is not None:
                                if not "primaryContact" in tool.keys():
                                    tool["primaryContact"] = [credit["name"]]
                                else:
                                    tool["primaryContact"].append(credit["name"])
                        else:
                            if "name" in credit.keys() and credit["name"] is not None:
                                if not "primaryContact" in tool.keys():
                                    tool["primaryContact"] = [credit["name"]]
                                else:
                                    tool["primaryContact"].append(credit["name"])

        if entry.get("publication"):
            for publication in entry["publication"]:
                if publication.get("pmid"):
                    if not "hasPublication" in tool.keys():
                        tool["hasPublication"] = ["pubmed:" + publication["pmid"]]
                    else:
                        tool["hasPublication"].append("pubmed:" + publication["pmid"])
                if publication.get("pmcid"):
                    if not "hasPublication" in tool.keys():
                        tool["hasPublication"] = ["pmcid:" + publication["pmcid"]]
                    else:
                        tool["hasPublication"].append("pmcid:" + publication["pmcid"])
                if publication.get("doi"):
                    if not ("<" in publication["doi"] or ">" in publication["doi"]):
                        if not "hasPublication" in tool.keys():
                            tool["hasPublication"] = [
                                {
                                    "@id": "https://doi.org/" + publication["doi"],
                                    "@type": "sc:CreativeWork",
                                }
                            ]
                        else:
                            tool["hasPublication"].append(
                                {
                                    "@id": "https://doi.org/" + publication["doi"],
                                    "@type": "sc:CreativeWork",
                                }
                            )

        if entry.get("function"):
            counter_op = 0
            for item in entry["function"]:
                counter_op += 1
                if item.get("operation"):
                    for op in item["operation"]:
                        if not "hasOperation" in tool.keys():
                            tool["hasOperation"] = [{"@id": op["uri"]}]
                        else:
                            tool["hasOperation"].append({"@id": op["uri"]})

                if item.get("input"):
                    counter_in = 0
                    for input in item["input"]:
                        counter_in += 1
                        input_object = {
                            "@id": tool["@id"]
                            + "/op_"
                            + str(counter_op)
                            + "/in_"
                            + str(counter_in),
                            "@type": "bsct:FormalParameter",
                            "name": input["data"]["term"],
                            "identifier": input["data"]["uri"],
                            "sameAs": input["data"]["uri"],
                        }
                        if not "hasInputData" in tool.keys():
                            tool["hasInputData"] = [input_object]
                        else:
                            tool["hasInputData"].append(input_object)

                if item.get("output"):
                    counter_out = 0
                    for output in item["output"]:
                        counter_out += 1
                        output_object = {
                            "@id": tool["@id"]
                            + "/op_"
                            + str(counter_op)
                            + "/in_"
                            + str(counter_out),
                            "@type": "bsct:FormalParameter",
                            "name": output["data"]["term"],
                            "identifier": output["data"]["uri"],
                            "sameAs": output["data"]["uri"],
                        }
                        if not "hasOutputData" in tool.keys():
                            tool["hasOutputData"] = [output_object]
                        else:
                            tool["hasOutputData"].append(output_object)

        if entry.get("topic"):
            for item in entry["topic"]:
                if not "hasTopic" in tool.keys():
                    tool["hasTopic"] = [{"@id": item["uri"]}]
                else:
                    tool["hasTopic"].append({"@id": item["uri"]})

        if entry.get("cost"):
            for item in entry["cost"]:
                if not "isAccessibleForFree" in tool.keys():
                    if "Free" in entry["cost"]:
                        tool["isAccessibleForFree"] = True
                    else:
                        tool["isAccessibleForFree"] = False

        if entry.get("documentation"):
            for item in entry["documentation"]:
                if "type" in item.keys() and item["type"]:
                    item["url"] = item["url"].replace("|", "%7C")
                    if "API" in item["type"]:
                        if not "hasApiDoc" in tool.keys():
                            tool["hasApiDoc"] = [{"@id": item["url"]}]
                        else:
                            tool["hasApiDoc"].append({"@id": item["url"]})
                    elif "Terms" in item["type"]:
                        if not "hasTermsOfUse" in tool.keys():
                            tool["hasTermsOfUse"] = [{"@id": item["url"]}]
                        else:
                            tool["hasTermsOfUse"].append({"@id": item["url"]})
                    else:
                        if not "hasGenDoc" in tool.keys():
                            tool["hasGenDoc"] = [{"@id": item["url"]}]
                        else:
                            tool["hasGenDoc"].append({"@id": item["url"]})

    except KeyError as e:
        print(e)
        pass

    graph["@graph"] = tool
    jsonld.update(graph)
    # print(json.dumps(jsonld, indent=4, sort_keys=True))
    # raw_jld = json.dumps(entry, indent=4, sort_keys=True)
    return jsonld
