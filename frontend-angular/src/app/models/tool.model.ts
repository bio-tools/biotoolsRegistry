export interface Tool {
  biotoolsID: string;
  name: string;
  description: string;
  homepage: string;
  biotoolsCURIE: string;
  version?: string;
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
  credit?: Credit[];
  owner?: string;
  additionDate?: string;
  lastUpdate?: string;
  publication?: Publication[];
  download?: Download[];
  documentation?: Documentation[];
  relation?: Relation[];
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
  uri: string;
  term: string;
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
  version?: string;
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

export type OperatingSystem = 'Linux' | 'Windows' | 'Mac';
export type ProgrammingLanguage = 'Python' | 'R' | 'Java' | 'C++' | 'C' | 'JavaScript' | 'Perl' | 'PHP' | 'Ruby' | 'Other';
export type Maturity = 'Emerging' | 'Mature' | 'Legacy';
export type Cost = 'Free of charge' | 'Free of charge (with restrictions)' | 'Commercial';
export type Accessibility = 'Open access' | 'Restricted access' | 'Proprietary';
export type EntityType = 'Person' | 'Project' | 'Division' | 'Institute' | 'Consortium' | 'Funding agency';
export type Role = 'Developer' | 'Maintainer' | 'Provider' | 'Documentor' | 'Contributor' | 'Support';
export type PublicationType = 'Primary' | 'Method' | 'Usage' | 'Benchmarking study' | 'Review' | 'Other';
export type DownloadType = 'Source code' | 'Binaries' | 'Container file' | 'CWL file' | 'Tool wrapper (galaxy)' | 'Tool wrapper (taverna)' | 'Tool wrapper (other)' | 'VM image' | 'Downloads page' | 'API specification' | 'Other';
export type DocumentationType = 'General' | 'Manual' | 'Installation instructions' | 'User manual' | 'Quick start guide' | 'Tutorial' | 'FAQ' | 'Training material' | 'Other';
export type RelationType = 'isNewVersionOf' | 'hasNewVersion' | 'usedBy' | 'uses' | 'includes' | 'includedIn';
