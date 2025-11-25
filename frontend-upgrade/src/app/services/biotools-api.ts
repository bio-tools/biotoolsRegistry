import { inject, Injectable } from '@angular/core';
import { Tool } from '../model/resource.model';
import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { catchError, map, Observable, throwError } from 'rxjs';
import { Domain } from '../model/domain.model';


export interface APIResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface SearchParams {
  query?: string;
  page?: number;
  sort?: string;
  ord?: string;
  per_page?: number;
}

// export interface 


@Injectable({
  providedIn: 'root'
})
export class BiotoolsApiService {

  // API server base URL (no trailing slash)
  private readonly baseUrl = 'http://localhost:8000'; //TODO make configurable

  private http = inject(HttpClient);
 
  //constructor(private http: HttpClient) {}

  /** TOOLS */
  /** Search for resources (tools) */
  searchResources(params: SearchParams) {
    let httpParams = new HttpParams();

    if (params.query) {
      httpParams = httpParams.set('q', params.query);
    }
    if (params.page) {
        httpParams = httpParams.set('page', params.page.toString());   
    }
    if (params.sort) {
      httpParams = httpParams.set('sort', params.sort);
    }
    if (params.ord) {
      httpParams = httpParams.set('ord', params.ord);
    }
    if (params.per_page) {
      httpParams = httpParams.set('per_page', params.per_page.toString());
    }

    return this.http.get<{ list: Array<Tool> }>(`${this.baseUrl}/t`, { params: httpParams })
    .pipe(
      map(response => response.list),
      catchError(this.handleError)
    );
  }

  getToolByID(biotoolsID: string): Observable<Tool> {
    return this.http.get<Tool>(`${this.baseUrl}/t/${biotoolsID}`).pipe(
      catchError(this.handleError)
    );
  }
  // Validate
  // Upload

  // /tool-list == slim list of tools --> maybe we can use this in the initial call when the user is logged_in?
  // example for one tool http://localhost:8000/tool-list?name=EXTRACT

  // Request editing rights / ownership

  /** DOMAINS */
  // d/ == DomainView (?)
  // d/domain-name == tools in domain : count, data - name, resources, ...
  // d/all == full domain list ?si result: count, data[]

  // Full complete list
  getDomains(): Observable<Domain[]> {
    return this.http.get<{ list: Domain[] }>(`${this.baseUrl}/domains/all`).pipe(
      map(response => response.list)
    );
  }
  // Slim list only name and resource count
  getSlimDomains(): Observable<Domain[]> {
    return this.http.get<{ list: Domain[] }>(`${this.baseUrl}/domains`).pipe(
      map(response => response.list)
    );
  }
  // Update, delete domains

  /** USED TERMS / autocomplete suggestions
   *  usedTermName: one of 'all','topic','operation',... as in legacy API
   *  params: optional query params (e.g. q, domain, page)
   */
  getUsedTerms(usedTermName: string, params?: {[k:string]: any}) {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(k => {
        if (params[k] !== undefined && params[k] !== null) {
          httpParams = httpParams.set(k, String(params[k]));
        }
      });
    }

    // Call the backend service using the configured baseUrl so requests go to the API server
    return this.http.get<any>(`${this.baseUrl}/used-terms/${usedTermName}`, { params: httpParams }).pipe(
      // the backend returns { data: [...] }
      map(res => res && res.data ? res.data : res),
      catchError(this.handleError)
    );
  }


  //** ONTOLOGY */

  //** STATS */
  //TODO

  private handleError(error: HttpErrorResponse) {
    //TODO: setup remote logging infrastructure
    console.error('An error occurred:', error);
    return throwError('Something bad happened; please try again later.');
  }
}
