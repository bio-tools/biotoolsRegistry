import { inject, Injectable } from '@angular/core';
import { Tool } from '../model/resource.model';
import { HttpClient, HttpParams } from '@angular/common/http';
import { map } from 'rxjs';
import { Domain } from '../model/domain.model';
import { Observable } from 'rxjs/internal/Observable';



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

      getToolByID(biotoolsID: string): Observable<Tool> {
          return this.http.get<Tool>(`${this.url}${biotoolsID}`);
      }
      
      validate(id: string, payload: any): Observable<any> {
          return this.http.put(`${this.url}/${id}/validate`, payload);
      }
  
      createTool(payload: Partial<Tool>): Observable<Tool> {
          return this.http.post<Tool>(this.url, payload);
      }
  
      updateTool(id: string, payload: Partial<Tool>): Observable<Tool> {
          return this.http.put<Tool>(`${this.url}${id}/`, payload);
      }
  
      deleteTool(id: string): Observable<any> {
          return this.http.delete(`${this.url}${id}/`);
      }

    // /tool-list == slim list of tools --> maybe we can use this in the initial call when the user is logged_in?
    // example for one tool http://localhost:8000/tool-list?name=EXTRACT
  

  getDomains() {
    return this.http.get<{ data: Array<Domain> }>('http://localhost:8000/d/all').pipe(
      map(response => response.data)
    );
  }

}
