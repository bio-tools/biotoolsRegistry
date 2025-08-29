import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Tool } from '../models/tool.model';
import { SearchParams, SearchResult, SearchFacets } from '../models/search.model';

@Injectable({
  providedIn: 'root'
})
export class BiotoolsApiService {
  private readonly baseUrl = 'https://bio.tools/api';

  constructor(private http: HttpClient) {}

  /**
   * Search for tools using the bio.tools API
   */
  searchTools(params: SearchParams): Observable<SearchResult<Tool>> {
    let httpParams = new HttpParams();
    
    if (params.q) httpParams = httpParams.set('q', params.q);
    if (params.topic?.length) httpParams = httpParams.set('topic', params.topic.join(','));
    if (params.toolType?.length) httpParams = httpParams.set('toolType', params.toolType.join(','));
    if (params.operatingSystem?.length) httpParams = httpParams.set('operatingSystem', params.operatingSystem.join(','));
    if (params.license) httpParams = httpParams.set('license', params.license);
    if (params.maturity) httpParams = httpParams.set('maturity', params.maturity);
    if (params.cost) httpParams = httpParams.set('cost', params.cost);
    if (params.page) httpParams = httpParams.set('page', params.page.toString());
    if (params.pageSize) httpParams = httpParams.set('pageSize', params.pageSize.toString());
    if (params.sort) httpParams = httpParams.set('sort', params.sort);
    if (params.order) httpParams = httpParams.set('order', params.order);

    return this.http.get<SearchResult<Tool>>(`${this.baseUrl}/tool`, { params: httpParams });
  }

  /**
   * Get a specific tool by its biotoolsID
   */
  getTool(biotoolsID: string): Observable<Tool> {
    return this.http.get<Tool>(`${this.baseUrl}/tool/${biotoolsID}`);
  }

  /**
   * Get search facets for filtering
   */
  getSearchFacets(): Observable<SearchFacets> {
    return this.http.get<SearchFacets>(`${this.baseUrl}/tool/facets`);
  }

  /**
   * Get tool statistics
   */
  getStats(): Observable<any> {
    return this.http.get(`${this.baseUrl}/stats`);
  }

  /**
   * Mock data for development - remove when connecting to real API
   */
  getMockTools(): Observable<SearchResult<Tool>> {
    const mockTools: Tool[] = [
      {
        biotoolsID: 'blast',
        name: 'BLAST',
        description: 'Basic Local Alignment Search Tool for comparing sequences against databases',
        homepage: 'https://blast.ncbi.nlm.nih.gov/',
        biotoolsCURIE: 'biotools:blast',
        version: '2.13.0',
        toolType: [{ uri: 'http://edamontology.org/operation_0346', term: 'Sequence similarity search' }],
        topic: [
          { uri: 'http://edamontology.org/topic_0080', term: 'Sequence analysis' },
          { uri: 'http://edamontology.org/topic_0102', term: 'Mapping' }
        ],
        operatingSystem: ['Linux', 'Windows', 'Mac'],
        language: ['C++'],
        license: 'Public domain',
        maturity: 'Mature',
        cost: 'Free of charge',
        accessibility: ['Open access'],
        additionDate: '2015-01-21',
        lastUpdate: '2023-01-01'
      },
      {
        biotoolsID: 'clustal_omega',
        name: 'Clustal Omega',
        description: 'Multiple sequence alignment program for proteins and DNA/RNA',
        homepage: 'http://www.clustal.org/omega/',
        biotoolsCURIE: 'biotools:clustal_omega',
        version: '1.2.4',
        toolType: [{ uri: 'http://edamontology.org/operation_0492', term: 'Multiple sequence alignment' }],
        topic: [
          { uri: 'http://edamontology.org/topic_0080', term: 'Sequence analysis' },
          { uri: 'http://edamontology.org/topic_0182', term: 'Phylogeny' }
        ],
        operatingSystem: ['Linux', 'Windows', 'Mac'],
        language: ['C++'],
        license: 'GPL-2.0',
        maturity: 'Mature',
        cost: 'Free of charge',
        accessibility: ['Open access'],
        additionDate: '2015-01-21',
        lastUpdate: '2022-06-15'
      },
      {
        biotoolsID: 'emboss',
        name: 'EMBOSS',
        description: 'European Molecular Biology Open Software Suite',
        homepage: 'http://emboss.sourceforge.net/',
        biotoolsCURIE: 'biotools:emboss',
        version: '6.6.0',
        toolType: [{ uri: 'http://edamontology.org/operation_2403', term: 'Sequence analysis' }],
        topic: [
          { uri: 'http://edamontology.org/topic_0091', term: 'Bioinformatics' },
          { uri: 'http://edamontology.org/topic_0080', term: 'Sequence analysis' }
        ],
        operatingSystem: ['Linux', 'Windows', 'Mac'],
        language: ['C'],
        license: 'GPL-2.0',
        maturity: 'Mature',
        cost: 'Free of charge',
        accessibility: ['Open access'],
        additionDate: '2015-01-21',
        lastUpdate: '2022-03-10'
      }
    ];

    const mockResult: SearchResult<Tool> = {
      count: mockTools.length,
      results: mockTools
    };

    return new Observable(observer => {
      setTimeout(() => {
        observer.next(mockResult);
        observer.complete();
      }, 500); // Simulate network delay
    });
  }
}
