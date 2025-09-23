import { inject, Injectable } from '@angular/core';
import { Tool } from '../model/resource.model';
import { HttpClient } from '@angular/common/http';
import { map } from 'rxjs';
import { Domain } from '../model/domain.model';

@Injectable({
  providedIn: 'root'
})
export class Resources {
  
  private url = 'http://localhost:8000/t/';
  
  http = inject(HttpClient);
 
  // constructor() { }

  getResources() {
    return this.http.get<{ list: Array<Tool> }>(this.url).pipe(
      map(response => response.list)
    );
  }

  getDomains() {
    return this.http.get<{ data: Array<Domain> }>('http://localhost:8000/d/all').pipe(
      map(response => response.data)
    );
  }
}
