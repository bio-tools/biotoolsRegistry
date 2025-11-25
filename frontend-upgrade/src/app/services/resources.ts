import { inject, Injectable } from '@angular/core';
import { Tool } from '../model/resource.model';
import { HttpClient, HttpParams } from '@angular/common/http';
import { map } from 'rxjs';
import { Domain } from '../model/domain.model';

export interface ResourceSearchParams {
  sort?: string;
  ord?: 'asc' | 'desc';
  page?: number;
  per_page?: number;
  q?: string;
}

@Injectable({
  providedIn: 'root'
})
export class Resources {
  
  private url = 'http://localhost:8000/t/';
  
  http = inject(HttpClient);
 
  // constructor() { }

  getResources(params?: ResourceSearchParams) {
    let httpParams = new HttpParams();
    
    if (params) {
      if (params.sort) {
        httpParams = httpParams.set('sort', params.sort);
      }
      if (params.ord) {
        httpParams = httpParams.set('ord', params.ord);
      }
      if (params.page) {
        httpParams = httpParams.set('page', params.page.toString());
      }
      if (params.per_page) {
        httpParams = httpParams.set('per_page', params.per_page.toString());
      }
      if (params.q) {
        httpParams = httpParams.set('q', params.q);
      }
    }

    return this.http.get<{ list: Array<Tool> }>(this.url, { params: httpParams }).pipe(
      map(response => response.list)
    );
  }

  getDomains() {
    return this.http.get<{ data: Array<Domain> }>('http://localhost:8000/d/all').pipe(
      map(response => response.data)
    );
  }
}
