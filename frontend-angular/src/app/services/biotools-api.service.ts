import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, of } from 'rxjs';
import { catchError, retry, map } from 'rxjs/operators';
import { Tool } from '../models/tool.model';
import { SearchParams, SearchResult, SearchFacets } from '../models/search.model';
import { Domain, Community } from '../models/domain.model';
import { environment } from '../../environments/environment';

export interface ApiResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface StatsResponse {
  tools: number;
  domains: number;
  communities: number;
  lastUpdate: string;
}

@Injectable({
  providedIn: 'root'
})
export class BiotoolsApiService {
  private readonly baseUrl = environment.apiUrl;
  private readonly enableMockData = environment.enableMockData;

  constructor(private http: HttpClient) {}

  /**
   * Search for tools using the bio.tools API
   */
  searchTools(params: SearchParams): Observable<SearchResult<Tool>> {
    if (this.enableMockData) {
      return this.getMockTools();
    }

    let httpParams = new HttpParams();
    
    if (params.q) httpParams = httpParams.set('q', params.q);
    if (params.topic?.length) httpParams = httpParams.set('topic', params.topic.join(','));
    if (params.toolType?.length) httpParams = httpParams.set('toolType', params.toolType.join(','));
    if (params.operatingSystem?.length) httpParams = httpParams.set('operatingSystem', params.operatingSystem.join(','));
    if (params.license) httpParams = httpParams.set('license', params.license);
    if (params.maturity) httpParams = httpParams.set('maturity', params.maturity);
    if (params.cost) httpParams = httpParams.set('cost', params.cost);
    if (params.page) httpParams = httpParams.set('page', params.page.toString());
    if (params.pageSize) httpParams = httpParams.set('format', 'json');

    return this.http.get<ApiResponse<Tool>>(`${this.baseUrl}/t`, { params: httpParams })
      .pipe(
        map(response => ({
          count: response.count,
          next: response.next,
          previous: response.previous,
          results: response.results
        })),
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Get a specific tool by its biotoolsID
   */
  getTool(biotoolsID: string): Observable<Tool> {
    if (this.enableMockData) {
      return this.getMockTool(biotoolsID);
    }

    return this.http.get<Tool>(`${this.baseUrl}/t/${biotoolsID}`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Get domains from the API
   */
  getDomains(): Observable<Domain[]> {
    if (this.enableMockData) {
      return this.getMockDomains();
    }

    return this.http.get<ApiResponse<any>>(`${this.baseUrl}/d`)
      .pipe(
        map(response => response.results.map(this.mapApiDomainToDomain)),
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Get tools for a specific domain
   */
  getDomainTools(domainSlug: string, params?: SearchParams): Observable<SearchResult<Tool>> {
    if (this.enableMockData) {
      return this.getMockTools();
    }

    let httpParams = new HttpParams().set('domain', domainSlug);
    if (params?.page) httpParams = httpParams.set('page', params.page.toString());
    if (params?.pageSize) httpParams = httpParams.set('page_size', params.pageSize.toString());

    return this.http.get<ApiResponse<Tool>>(`${this.baseUrl}/d/${domainSlug}`, { params: httpParams })
      .pipe(
        map(response => ({
          count: response.count,
          next: response.next,
          previous: response.previous,
          results: response.results
        })),
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Get tool statistics
   */
  getStats(): Observable<StatsResponse> {
    if (this.enableMockData) {
      return this.getMockStats();
    }

    return this.http.get<any>(`${this.baseUrl}/stats`)
      .pipe(
        map(response => ({
          tools: response.tools || 25000,
          domains: response.domains || 150,
          communities: response.communities || 50,
          lastUpdate: response.lastUpdate || new Date().toISOString()
        })),
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Create a new tool (requires authentication)
   */
  createTool(tool: Partial<Tool>): Observable<Tool> {
    return this.http.post<Tool>(`${this.baseUrl}/t`, tool)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Update an existing tool (requires authentication)
   */
  updateTool(biotoolsID: string, tool: Partial<Tool>): Observable<Tool> {
    return this.http.put<Tool>(`${this.baseUrl}/t/${biotoolsID}`, tool)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Delete a tool (requires authentication)
   */
  deleteTool(biotoolsID: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/t/${biotoolsID}`)
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Get user's tools (requires authentication)
   */
  getUserTools(): Observable<SearchResult<Tool>> {
    return this.http.get<ApiResponse<Tool>>(`${this.baseUrl}/tool-list`)
      .pipe(
        map(response => ({
          count: response.count,
          next: response.next,
          previous: response.previous,
          results: response.results
        })),
        catchError(this.handleError)
      );
  }

  /**
   * Validate tool data
   */
  validateTool(tool: Partial<Tool>): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/t/validate`, tool)
      .pipe(
        catchError(this.handleError)
      );
  }

  // Private helper methods
  private mapApiDomainToDomain(apiDomain: any): Domain {
    return {
      name: apiDomain.name || '',
      description: apiDomain.description || '',
      slug: apiDomain.slug || '',
      toolCount: apiDomain.tool_count || 0,
      subcategories: apiDomain.subcategories || [],
      color: this.getDomainColor(apiDomain.name),
      icon: this.getDomainIcon(apiDomain.name)
    };
  }

  private getDomainColor(domainName: string): string {
    const colors = ['#1976d2', '#388e3c', '#f57c00', '#7b1fa2', '#d32f2f', '#303f9f', '#00796b', '#5d4037'];
    const hash = domainName.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
    return colors[hash % colors.length];
  }

  private getDomainIcon(domainName: string): string {
    const iconMap: { [key: string]: string } = {
      'sequence': 'biotech',
      'structural': 'scatter_plot',
      'genomics': 'dna',
      'proteomics': 'bubble_chart',
      'phylogenetics': 'account_tree',
      'metabolomics': 'device_hub',
      'transcriptomics': 'timeline',
      'epigenomics': 'layers'
    };
    
    const lowerName = domainName.toLowerCase();
    for (const [key, icon] of Object.entries(iconMap)) {
      if (lowerName.includes(key)) {
        return icon;
      }
    }
    return 'category';
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An unknown error occurred';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Client Error: ${error.error.message}`;
    } else {
      // Server-side error
      errorMessage = `Server Error Code: ${error.status}\nMessage: ${error.message}`;
    }
    
    if (environment.enableLogging) {
      console.error(errorMessage);
    }
    
    return throwError(() => new Error(errorMessage));
  }

  // Mock data methods (for development)
  private getMockTools(): Observable<SearchResult<Tool>> {
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

    return of(mockResult);
  }

  private getMockTool(biotoolsID: string): Observable<Tool> {
    const mockTool: Tool = {
      biotoolsID: biotoolsID,
      name: 'BLAST+ Sequence Analysis Suite',
      description: 'BLAST+ is a new suite of BLAST tools that utilizes the NCBI C++ Toolkit. The BLAST+ applications have a number of performance and feature improvements over the legacy BLAST applications.',
      homepage: 'https://blast.ncbi.nlm.nih.gov/Blast.cgi',
      biotoolsCURIE: `biotools:${biotoolsID}`,
      version: '2.13.0',
      toolType: [
        { uri: 'http://edamontology.org/operation_0346', term: 'Sequence similarity search' },
        { uri: 'http://edamontology.org/operation_0292', term: 'Sequence alignment' }
      ],
      topic: [
        { uri: 'http://edamontology.org/topic_0080', term: 'Sequence analysis' },
        { uri: 'http://edamontology.org/topic_0102', term: 'Mapping' },
        { uri: 'http://edamontology.org/topic_3168', term: 'Sequencing' }
      ],
      operatingSystem: ['Linux', 'Windows', 'Mac'],
      language: ['C++'],
      license: 'Public domain',
      maturity: 'Mature',
      cost: 'Free of charge',
      accessibility: ['Open access'],
      additionDate: '2015-01-21',
      lastUpdate: '2023-06-15',
      function: [
        {
          operation: [
            { uri: 'http://edamontology.org/operation_0346', term: 'Sequence similarity search' },
            { uri: 'http://edamontology.org/operation_0292', term: 'Sequence alignment' }
          ],
          input: [
            {
              uri: 'http://edamontology.org/data_2044',
              term: 'Sequence',
              format: [
                { uri: 'http://edamontology.org/format_1929', term: 'FASTA' },
                { uri: 'http://edamontology.org/format_1936', term: 'GenBank format' }
              ]
            },
            {
              uri: 'http://edamontology.org/data_1233',
              term: 'Sequence set (nucleic acid)',
              format: [
                { uri: 'http://edamontology.org/format_1929', term: 'FASTA' }
              ]
            }
          ],
          output: [
            {
              uri: 'http://edamontology.org/data_0857',
              term: 'Sequence search results',
              format: [
                { uri: 'http://edamontology.org/format_3475', term: 'TSV' },
                { uri: 'http://edamontology.org/format_2331', term: 'HTML' },
                { uri: 'http://edamontology.org/format_2332', term: 'XML' }
              ]
            },
            {
              uri: 'http://edamontology.org/data_1384',
              term: 'Sequence alignment (pair)',
              format: [
                { uri: 'http://edamontology.org/format_1982', term: 'BLAST results' }
              ]
            }
          ],
          note: 'Performs local alignment search using BLAST algorithm against sequence databases',
          cmd: 'blastn -query input.fasta -db nt -outfmt 6 -out results.txt'
        },
        {
          operation: [
            { uri: 'http://edamontology.org/operation_0495', term: 'Local alignment' }
          ],
          input: [
            {
              uri: 'http://edamontology.org/data_2976',
              term: 'Protein sequence',
              format: [
                { uri: 'http://edamontology.org/format_1929', term: 'FASTA' }
              ]
            }
          ],
          output: [
            {
              uri: 'http://edamontology.org/data_1384',
              term: 'Sequence alignment (pair)',
              format: [
                { uri: 'http://edamontology.org/format_1982', term: 'BLAST results' },
                { uri: 'http://edamontology.org/format_3475', term: 'TSV' }
              ]
            }
          ],
          note: 'Protein sequence similarity search using BLASTP algorithm',
          cmd: 'blastp -query protein.fasta -db nr -evalue 1e-5 -outfmt 6'
        }
      ],
      credit: [
        {
          name: 'NCBI',
          typeEntity: 'Institute',
          typeRole: ['Provider', 'Developer'],
          url: 'https://www.ncbi.nlm.nih.gov/',
          note: 'National Center for Biotechnology Information'
        },
        {
          name: 'Stephen Altschul',
          typeEntity: 'Person',
          typeRole: ['Developer'],
          note: 'Lead developer of BLAST algorithm'
        }
      ],
      publication: [
        {
          type: ['Primary'],
          doi: '10.1186/1471-2105-10-421',
          pmid: '20003500',
          note: 'BLAST+: architecture and applications'
        }
      ],
      documentation: [
        {
          url: 'https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs',
          type: 'User manual',
          note: 'Official BLAST+ documentation and user guide'
        },
        {
          url: 'https://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE_TYPE=BlastSearch&BLAST_SPEC=blast2seq',
          type: 'Tutorial',
          note: 'Step-by-step tutorial for sequence comparison'
        }
      ],
      download: [
        {
          url: 'https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/',
          type: 'Binaries',
          note: 'Pre-compiled executables for various platforms'
        },
        {
          url: 'https://github.com/ncbi/blast_plus_docs',
          type: 'Source code',
          note: 'Documentation and examples repository'
        }
      ]
    };

    return of(mockTool);
  }

  private getMockDomains(): Observable<Domain[]> {
    const mockDomains: Domain[] = [
      {
        name: 'Sequence Analysis',
        description: 'Tools for analyzing biological sequences',
        slug: 'sequence-analysis',
        toolCount: 8542,
        subcategories: ['Alignment', 'Annotation', 'Assembly'],
        color: '#1976d2',
        icon: 'biotech'
      }
    ];

    return of(mockDomains);
  }

  private getMockStats(): Observable<StatsResponse> {
    return of({
      tools: 25000,
      domains: 150,
      communities: 50,
      lastUpdate: new Date().toISOString()
    });
  }
}
