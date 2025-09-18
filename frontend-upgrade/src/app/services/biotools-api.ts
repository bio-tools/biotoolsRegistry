import { inject, Injectable } from '@angular/core';
import { Resource } from '../model/resource.model';
import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { catchError, map, Observable, throwError } from 'rxjs';
import { Domain } from '../model/domain.model';


export interface APIResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}


@Injectable({
  providedIn: 'root'
})
export class BiotoolsApiService {

  private readonly baseUrl = 'http://localhost:8000/'; //TODO

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

    return this.http.get<{ list: Array<Resource> }>(`${this.baseUrl}/t`, { params: httpParams })
    .pipe(
      map(response => response.list),

      catchError(this.handleError) //TODOs
    );
  }

  /** GET TOOL BY ID */
  getToolByID(biotoolsID: string): Observable<Resource> {
    return this.http.get<{ detail: Resource }>(`${this.baseUrl}/t/${biotoolsID}`).pipe(
      map(response => response.detail)
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

  private handleError(error: HttpErrorResponse) {
    // In a real world app, you might use a remote logging infrastructure
    console.error('An error occurred:', error);
    return throwError('Something bad happened; please try again later.');
  }
}
