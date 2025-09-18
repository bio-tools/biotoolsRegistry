export interface Resource {

    id?: number;
    biotoolsID: string;
    biotoolsCURIE: string;
    name: string;
    description: string;
    homepage: string; //long
    version?: string[];
    otherID?: string[];
    relation?: string[];
    function?: {
        operation: { uri: string; term: string }[];
        input: { uri: string; term: string }[];
        output: { uri: string; term: string }[];
        note: string;
        cmd: string;
    }[];
    toolType?: string[];
    topic?: { uri: string; term: string }[];
    operatingSystem?: string[];
    language?: string[];
    license?: string;
    collectionID?: string[];
    maturity?: string;
    cost?: string;
    accessibility?: string;
    elixirPlatform?: string[];
    elixirNode?: string[];
    elixirCommunity?: string[];
    link?: { url: string; type: string }[];
    documentation?: { url: string; type: string }[];
    download?: { url: string; type: string }[];
    publication?: {
        doi: string;
        pmid: string;
        pmcid: string;
        type: string[];
        version: string;
        note: string;
        //TODO metadata
    }[];
    credit?: { 
        name: string;
        email: string;
        url: string;
        orcidid: string;
        gridid: string;
        rorid: string;
        fundrefid: string;
        typeEntity: string;
        typeRole: string[];
        note: string;
    }[];
    owner: string;
    additionDate: string;
    lastUpdate: string;
    editPermission: {
        type: string;
        authors: string[];
    }[];
    validated?: boolean;
    homepageStatus?: number;
    elixir_badge?: number; //TODO
    confidence_flag?: string; //TODO
}