
export interface SearchParams {
  q?: string;
  topic?: string[];
  operation?: string[];
  input?: string[];
  output?: string[];
  toolType?: string[];
  language?: string[];
  accessibility?: string[];
  license?: string;
  cost?: string;
  page?: number;
  pageSize?: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

export interface SearchResult<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface Facet {
  name: string;
  count: number;
}

export interface SearchFacets {
  topic: Facet[];
  toolType: Facet[];
  operatingSystem: Facet[];
  language: Facet[];
  license: Facet[];
  maturity: Facet[];
  cost: Facet[];
}