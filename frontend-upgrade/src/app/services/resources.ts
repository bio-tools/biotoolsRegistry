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
 

  getResources(params: any) {
    let httpParams = new HttpParams();
    
    Object.keys(params).forEach(key => {
      const val = params[key];
      if (val !== undefined && val !== null) {
        httpParams = httpParams.set(key, String(val));
      }
    });

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
