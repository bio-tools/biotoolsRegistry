
export interface Tool {
  biotoolsID: string;
  biotoolsCURIE: string;
  name: string;
  description: string;
  homepage: string;
  version?: string[];
  otherID?: OtherID[];
  function?: ToolFunction[];
  toolType?: ToolType[];
  topic?: Topic[];
  operatingSystem?: OperatingSystem[];
  language?: ProgrammingLanguage[];
  license?: string;
  collectionID?: string[];
  maturity?: Maturity;
  cost?: Cost;
  accessibility?: Accessibility[];
  elixirPlatform?: string[];
  elixirNode?: string[];
  elixirCommunity?: string[];
  credit?: Credit[];
  owner: string;
  additionDate: string;
  lastUpdate: string;
  publication?: Publication[];
  link?: Link[];
  download?: Download[];
  documentation?: Documentation[];
  relation?: Relation[];
  editPermission: {
    type: string;
    authors: string[];
  }[];
  validated?: boolean;
  homepageStatus?: number;
  elixir_badge?: number;
  confidence_flag?: string;
}

export interface ToolFunction {
  operation: Operation[];
  input?: DataFormat[];
  output?: DataFormat[];
  note?: string;
  cmd?: string;
}

export interface Operation {
  uri: string;
  term: string;
}

export interface DataFormat {
  data: {  uri: string;
  term: string; };
  format?: Format[];
}

export interface Format {
  uri: string;
  term: string;
}

export interface Topic {
  uri: string;
  term: string;
}

export interface ToolType {
  uri: string;
  term: string;
}

export interface OtherID {
  value: string;
  type: string;
  version?: string;
}

export interface Credit {
  name?: string;
  email?: string;
  url?: string;
  orcidid?: string;
  gridid?: string;
  rorid?: string;
  fundrefid?: string;
  typeEntity?: EntityType;
  typeRole?: Role[];
  note?: string;
}

export interface Publication {
  doi?: string;
  pmid?: string;
  pmcid?: string;
  type?: PublicationType[];
  note?: string;
  // TODO metadata
}

export interface Link {
  url: string;
  type: LinkType;
  note?: string;
}

export interface Download {
  url: string;
  type: DownloadType;
  note?: string;
  version?: string;
}

export interface Documentation {
  url: string;
  type: DocumentationType;
  note?: string;
}

export interface Relation {
  biotoolsID: string;
  type: RelationType;
}


export const TOOL_TYPES = [
  'Bioinformatics portal','Command-line tool', 'Database portal', 'Desktop application', 'Library', 'Ontology', 'Plug-in', 'Script', 'SPARQL endpoint', 'Suite', 'Web application', 'Web API', 'Web service', 'Workbench', 'Workflow'
] as const;

export const PROGRAMMING_LANGUAGES = [
  'Python', 'R', 'Java', 'C++', 'C', 'JavaScript', 'Perl', 'PHP', 'Ruby', 'Other'
] as const;

export const LICENSES = [
  'Apache-2.0', 'Artistic-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'CC-BY-4.0', 'CC-BY-SA-4.0', 'CC0-1.0', 'EPL-1.0', 'EPL-2.0', 'GPL-2.0', 'GPL-3.0', 'LGPL-2.1', 'LGPL-3.0', 'MIT', 'MPL-2.0', 'ODC-BY-1.0', 'Other'
] as const;

export const COST = [
  'Free of charge', 'Free of charge (with restrictions)', 'Commercial'
] as const;

export const OPERATING_SYSTEMS = [
  'Linux', 'Windows', 'Mac'
] as const;

export const ACCESSIBILITY = [
  'Open access', 'Open access (with restrictions)', 'Restricted access'
] as const;

export const MATURITY = [
  'Emerging', 'Mature', 'Legacy'
] as const;

export const CONTACT_ROLES = [
  'General', 'Developer', 'Technical', 'Scientific', 'Helpdesk', 'Maintainer'
] as const;

export const LINK_TYPES = [
  'Discussion forum', 'Galaxy service', 'Helpdesk', 'Issue tracker', 'Mailing list', 'Mirror', 'Repository', 'Service', 'Social media', 'Software catalogue', 'Technical monitoring', 'Other'
] as const;

export const DOWNLOAD_TYPES = [
  'Downloads page', 'API specification', 'Biological data', 'Binaries', 'Command-line specification', 'Container file', 'Icon', 'Screenshot', 'Software package', 'Source code', 'Test data', 'Test script', 'Tool wrapper (CWL)', 'Tool wrapper (Galaxy)', 'Tool wrapper (Taverna)', 'Tool wrapper (Other)', 'VM Image', 'Other'
] as const;

export const DOCUMENTATION_TYPES = [
  'API documentation', 'Citation instructions', 'Code of conduct', 'Command-line options', 'Contributions policy', 'FAQ', 'General', 'Governance', 'Installation instructions', 'Quick start guide', 'Release notes', 'Terms of use', 'Training material', 'User manual', 'Other'
] as const;

export const PUBLICATION_TYPES = [
  'Primary', 'Benchmarking study', 'Method', 'Preprint', 'Usage', 'Review', 'Other'
] as const;

export const ENTITY_TYPES = [
  'Person', 'Project', 'Division', 'Institute', 'Consortium', 'Funding agency'
] as const;

export const ROLE_TYPES = [
  'Primary contact', 'Contributor', 'Developer', 'Documentor', 'Maintainer', 'Provider', 'Support'
] as const;

export const ELIXIR_PLATFORMS = [
  'Compute', 'Data', 'Interoperability', 'Tools', 'Training'
] as const;

export const ELIXIR_COMMUNITIES = [
  '3D-BioInfo', 'Federated Human Data', 'Galaxy', 'Human Copy Number Variation', 'Intrinsically Disordered Proteins', 'Marine Metagenomics', 'Metabolomics', 'Microbial Biotechnology', 'Plant Sciences', 'Proteomics', 'Rare Diseaseas', 'Systems Biology'
] as const;

export const ELIXIR_NODES = [
  'Belgium', 'Czech Republic', 'Denmark', 'EMBL', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Israel', 'Italy', 'Luxembourg', 'Netherlands', 'Norway', 'Portugal', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'UK'
] as const;

export const OTHERID_TYPES = [
  'doi', 'rrid', 'cpe'
] as const;

export const RELATION_TYPES = [
  'hasNewVersion', 'isNewVersionOf', 'includes', 'includedIn', 'uses', 'usedBy'
] as const;

export const CONFIDENCE_FLAGS = [
  'tool', 'high', 'medium', 'low', 'very low'
] as const;

  	


export type OperatingSystem = 'Linux' | 'Windows' | 'Mac';
export type ProgrammingLanguage = 'Python' | 'R' | 'Java' | 'C++' | 'C' | 'JavaScript' | 'Perl' | 'PHP' | 'Ruby' | 'Other'; //TODO
export type Maturity = 'Emerging' | 'Mature' | 'Legacy';
export type Cost = 'Free of charge' | 'Free of charge (with restrictions)' | 'Commercial';
export type Accessibility = 'Open access' | 'Restricted access' | 'Proprietary';
export type EntityType = 'Person' | 'Project' | 'Division' | 'Institute' | 'Consortium' | 'Funding agency';
export type Role = 'Developer' | 'Maintainer' | 'Provider' | 'Documentor' | 'Contributor' | 'Support';
export type PublicationType = 'Primary' | 'Method' | 'Usage' | 'Benchmarking study' | 'Review' | 'Other';
export type LinkType = 'Repository' | 'Issue tracker' | 'Helpdesk' | 'Discussion forum' | 'Mailing list' | 'Service' | 'Galaxy service' | 'Software catalogue' | 'Social media' | 'Technical monitoring' | 'Mirror' | 'Other';
export type DownloadType = 'Source code' | 'Binaries' | 'Container file' | 'CWL file' | 'Tool wrapper (galaxy)' | 'Tool wrapper (taverna)' | 'Tool wrapper (other)' | 'VM image' | 'Downloads page' | 'API specification' | 'Other';
export type DocumentationType = 'General' | 'Manual' | 'Installation instructions' | 'User manual' | 'Quick start guide' | 'Tutorial' | 'FAQ' | 'Training material' | 'Other';
export type RelationType = 'isNewVersionOf' | 'hasNewVersion' | 'usedBy' | 'uses' | 'includes' | 'includedIn';
