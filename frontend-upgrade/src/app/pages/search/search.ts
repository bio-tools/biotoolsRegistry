import { Component, inject, OnInit, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Resources } from '../../services/resources';
import { Resource } from '../../model/resource.model';
import { catchError } from 'rxjs';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { Sidebar } from '../../components/sidebar/sidebar';

@Component({
  selector: 'app-search',
  imports: [
    Sidebar,
    // Angular Material
    MatCardModule,
    MatFormFieldModule,
    MatSelectModule,
    MatCheckboxModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
    MatChipsModule
  ],
  templateUrl: './search.html',
  styleUrl: './search.scss'
})
export class Search implements OnInit {

  //vibe coded
  searchQuery = '';
  totalResults = 0;
  pageSize = 50;
  loading = false;

  resourcesService = inject(Resources);
  router = inject(Router);
  tools = signal<Array<Resource>>([]); // signal to hold array of Resource objects

  ngOnInit(): void { // lifecycle hook, called after component's constructor, when component is initialized
    this.resourcesService.getResources()
    .pipe(
      catchError(error => {
        console.log('Error fetching resources:', error);
        throw error;
      })
    )
    .subscribe((resources) => {
      console.log('Fetched resources:', resources);
      this.tools.set(resources);
    });
  }

  //vibe coded
  onPageChange(event: any) {
    this.pageSize = event.pageSize;
    this.loading = true;
    setTimeout(() => {
      this.loading = false;
    }, 1000);
  }

  getToolTopics(tool: Resource): string[] {
  // Return array of topic terms
    return tool.topic?.map(t => t.term) ?? [];
  }

  getToolOperations(tool: Resource): string[] {
    // Return array of operation terms
    return tool.function?.flatMap(f => f.operation.map(op => op.term)) ?? [];
  }

  viewToolDetails(biotoolsID: string) {
    this.router.navigate(['/tool', biotoolsID]);
  }

}
