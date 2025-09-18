import { inject, Injectable } from '@angular/core';
import { Resource } from '../model/resource.type';
import { HttpClient } from '@angular/common/http';
import { map } from 'rxjs';

@Injectable({
  providedIn: 'root'
})

export class Resources {
  
  private url = 'http://localhost:8000/t/';
  
  http = inject(HttpClient);
 
  // constructor() { }

  getResources() {
    // return this.http.get<Array<Resource>>(this.url);

    return this.http.get<{ list: Array<Resource> }>(this.url).pipe(
      map(response => response.list)
    );
  }
}
