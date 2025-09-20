export interface SearchParams {
  q?: string;
  topic?: string[];
  toolType?: string[];
  operatingSystem?: string[];
  license?: string;
  maturity?: string;
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