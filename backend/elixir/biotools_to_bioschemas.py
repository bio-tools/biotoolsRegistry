# Credit for this script to Alban Gaignard
# https://github.com/albangaignard


def as_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def rdfize(entry):
    """
    Transforms a biotools json entry into RDF, and returns a JSON-LD serialization. The following fields
    are covered: contact, publication, EDAM topic, EDAM operation, EDAM inputs & outputs.
    """

    ctx = {
        "@context": [
            "https://schema.org",
            {
                "@base": "https://bio.tools/",
                "sc": "https://schema.org/",
                "biotools": "https://bio.tools/ontology/",
                "edam": "http://edamontology.org/",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "bsc": "http://bioschemas.org/",
                "bsct": "http://bioschemas.org/types/",
                "primaryContact": "biotools:primaryContact",
                "hasPublication": "citation",
                "hasTopic": "applicationSubCategory",
                "hasOperation": "featureList",
                "hasInputData": "bsc:input",
                "hasOutputData": "bsc:output",
                "hasApiDoc": "softwareHelp",
                "hasGenDoc": "softwareHelp",
                "hasTermsOfUse": "termsOfService",
                "conformsTo": "http://purl.org/dc/terms/conformsTo",
                "version": "softwareVersion",
            },
        ]
    }

    biotools_id = str(entry["biotoolsID"])
    name = str(entry["name"])
    tool = {"@id": str(biotools_id) if biotools_id else None, "@type": "SoftwareApplication", "name": str(name),
            "applicationCategory": "Computational science tool",
            "conformsTo": "https://bioschemas.org/profiles/ComputationalTool/1.0-RELEASE", "author": [], "provider": [],
            "contributor": [], "funder": [], "primaryContact": [], "description": entry.get("description"),
            "url": entry.get("homepage"), "version": entry.get("version"), "license": entry.get("license"),
            "operatingSystem": [os for os in as_list(entry.get("operatingSystem")) if os],
            "toolType": as_list(entry.get("toolType")), "datePublished": entry.get("additionDate"),
            "dateModified": entry.get("lastUpdate")}

    if entry.get("homepage"):
        tool["mainEntityOfPage"] = {"@type": "WebPage", "@id": entry["homepage"]}

    if entry.get("version"):
        tool["version"] = "".join(as_list(entry.get("version")))

    # SameAs from otherID/link
    same_as = []
    for oid in as_list(entry.get("otherID")):
        v = oid.get("value")
        if v:
            same_as.append(v)
    for lnk in as_list(entry.get("link")):
        if lnk.get("url"):
            same_as.append(lnk["url"])
    if same_as:
        tool["sameAs"] = list(dict.fromkeys(same_as))  # de‑dupe

    for credit in as_list(entry.get("credit")):
        roles = set(as_list(credit.get("typeRole")))
        ent = credit.get("typeEntity") or ""
        is_person = "Person" in ent
        sType = "sc:Person" if is_person else "sc:Organization"
        node = {}
        if credit.get("name"):
            node |= {"name": credit["name"]}
        if credit.get("orcidid"):
            node |= {"@id": credit["orcidid"]}
        if credit.get("url"):
            node |= {"url": credit["url"]}

        if not node:
            continue

        node |= {"@type": sType}

        if "Funding agency" in (credit.get("typeEntity") or ""):
            tool["funder"].append(node)
        if "Developer" in roles:
            tool["author"].append(node)
        if "Provider" in roles:
            tool["provider"].append(node)
        if "Contributor" in roles:
            tool["contributor"].append(node)
        if "Primary contact" in roles:
            tool["primaryContact"].append(node)

    if entry.get("publication"):
        pubs = []
        for p in entry["publication"]:
            doi_url = "https://doi.org/" + p["doi"] if p.get("doi") else None
            pmid_url = "https://pubmed.ncbi.nlm.nih.gov/" + p["pmid"] if p.get("pmid") else None
            pmcid_url = "https://pubmed.ncbi.nlm.nih.gov/" + p["pmcid"] if p.get("pmcid") else None

            if not (doi_url or pmid_url or pmcid_url):
                continue

            publication = {
                "@id": doi_url or pmid_url or pmcid_url,
                "@type": "ScholarlyArticle",
                "sameAs": [id for id in [doi_url, pmid_url, pmcid_url] if id],
            }
            pubs.append(publication)
        if pubs:
            tool["hasPublication"] = pubs

    if entry.get("function"):
        op_idx = 0
        for fn in entry["function"]:
            op_idx += 1
            for op in as_list(fn.get("operation")):
                if op and op.get("uri"):
                    tool.setdefault("hasOperation", []).append({"@id": op["uri"]})
            # inputs
            in_idx = 0
            for inp in as_list(fn.get("input")):
                in_idx += 1
                data = inp.get("data") or {}
                term = data.get("term") or data.get("uri") or "Input"
                uri = data.get("uri") or ""
                input_object = {
                    "@id": f"{tool['@id']}/op_{op_idx}/in_{in_idx}",
                    "@type": "bsct:FormalParameter",
                    "name": term,
                    "identifier": uri,
                    "sameAs": uri,
                }
                tool.setdefault("hasInputData", []).append(input_object)
            # outputs
            out_idx = 0
            for outp in as_list(fn.get("output")):
                out_idx += 1
                data = outp.get("data") or {}
                term = data.get("term") or data.get("uri") or "Output"
                uri = data.get("uri") or ""
                output_object = {
                    "@id": f"{tool['@id']}/op_{op_idx}/out_{out_idx}",
                    "@type": "bsct:FormalParameter",
                    "name": term,
                    "identifier": uri,
                    "sameAs": uri,
                }
                tool.setdefault("hasOutputData", []).append(output_object)

    if entry.get("topic"):
        tool["hasTopic"] = [{"@id": t["uri"]} for t in entry["topic"] if t.get("uri")]

    cost = entry.get("cost")
    if cost == "Free of charge":
        tool["isAccessibleForFree"] = True
        # Google prefers 'offers', otherwise it might mark a tool's metadata as invalid
        tool["offers"] = {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD",
        }

    for doc in as_list(entry.get("documentation")):
        url = (doc.get("url") or "").replace("|", "%7C")
        if not url:
            continue
        types = as_list(doc.get("type"))
        if any("API" in t for t in types):
            tool.setdefault("hasApiDoc", []).append({"@id": url})
        elif any("Terms" in t for t in types):
            tool.setdefault("hasTermsOfUse", []).append({"@id": url})
        else:
            tool.setdefault("hasGenDoc", []).append({"@id": url})

    jsonld = {}
    jsonld.update(ctx)
    jsonld["@graph"] = [tool]
    return jsonld
