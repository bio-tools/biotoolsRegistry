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
}

@Injectable({
  providedIn: 'root'
})
export class BiotoolsApiService {

  // API server base URL (no trailing slash)
  private readonly baseUrl = 'http://localhost:8000'; //TODO make configurable

  //http = inject(HttpClient);
 
  constructor(private http: HttpClient) {}


  /** Search for resources (tools) */
  searchResources(params: SearchParams) { //TODO: define SearchParams interface
    let httpParams = new HttpParams();

    if (params.query) {
      httpParams = httpParams.set('q', params.query);
    }
    if (params.page) {
        httpParams = httpParams.set('page', params.page.toString());   
    }

    return this.http.get<{ list: Array<Tool> }>(`${this.baseUrl}/t`, { params: httpParams })
    .pipe(
      map(response => response.list),

      catchError(this.handleError) //TODO
    );
  }

  /** GET TOOL BY ID */
  getToolByID(biotoolsID: string): Observable<Tool> {
    return this.http.get<Tool>(`${this.baseUrl}/t/${biotoolsID}`).pipe(
      catchError(this.handleError)
    );
  }

  /** DOMAINS */
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

  /** Used terms / autocomplete suggestions
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

  private handleError(error: HttpErrorResponse) {
    // In a real world app, you might use a remote logging infrastructure
    console.error('An error occurred:', error);
    return throwError('Something bad happened; please try again later.');
  }
}
