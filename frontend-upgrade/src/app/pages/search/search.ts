import { Component, inject, OnInit, signal, AfterViewInit } from '@angular/core';
import { Router, NavigationEnd, ActivatedRoute } from '@angular/router';
import { Resources } from '../../services/resources';
import { Tool } from '../../model/resource.model';
import { catchError, filter } from 'rxjs';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Sidebar } from '../../components/sidebar/sidebar';
import { SortService } from '../../services/sort.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-search',
  imports: [
    CommonModule,
    Sidebar,
    // Angular Material
    MatCardModule,
    MatFormFieldModule,
    MatSelectModule,
    MatCheckboxModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
    MatChipsModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule
  ],
  templateUrl: './search.html',
  styleUrl: './search.scss'
})
export class Search implements OnInit, AfterViewInit {

  searchQuery = '';
  totalResults = 0;
  pageSize = 50;
  loading = false;

  resourcesService = inject(Resources);
  sortService = inject(SortService);
  router = inject(Router);
  route = inject(ActivatedRoute);
  tools = signal<Array<Tool>>([]); // signal to hold array of Resource objects

  ngOnInit(): void {
    // Initialize sort service from URL parameters
    this.route.queryParams.subscribe(params => {
      this.sortService.initFromParams({
        sort: params['sort'],
        ord: params['ord']
      });
      
      // Check if there's a search query to add/remove score option
      if (params['q']) {
        this.searchQuery = params['q'];
        this.sortService.addScoreOption();
      } else {
        this.sortService.removeScoreOption();
      }
      
      // Pass all query params to loadResources
      this.loadResources(params);
    });

    // Listen for navigation events to restore scroll position when coming back from tool page
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe((event: NavigationEnd) => {
        // If we're navigating to the search page from a tool page, don't scroll to top
        if (event.url === '/t' && event.urlAfterRedirects === '/t') {
          // Let the browser handle scroll restoration naturally
          return;
        }
      });
  }

  loadResources(queryParams?: any): void {
    this.loading = true;
    const sortParams = this.sortService.getSortParams();
    
    // Build API parameters from URL query params
    const apiParams: any = {
      sort: sortParams.sort,
      ord: sortParams.ord as 'asc' | 'desc',
      per_page: this.pageSize
    };

    // Add all filter parameters from URL
    if (queryParams) {
      const filterParams = ['q', 'page', 'topic', 'operation', 'input', 'output', 'toolType', 
                           'language', 'accessibility', 'cost', 'license', 'credit', 'collectionID', 'name'];
      
      for (const param of filterParams) {
        if (queryParams[param]) {
          apiParams[param] = queryParams[param];
        }
      }
    }
    
    this.resourcesService.getResources(apiParams)
    .pipe(
      catchError(error => {
        console.log('Error fetching resources:', error);
        this.loading = false;
        throw error;
      })
    )
    .subscribe((resources) => {
      console.log('Fetched resources:', resources);
      this.tools.set(resources);
      this.loading = false;
    });
  }

  ngAfterViewInit(): void {
    // Restore scroll position if coming back from a tool page
    const savedScrollPosition = sessionStorage.getItem('searchScrollPosition');
    if (savedScrollPosition) {
      setTimeout(() => {
        window.scrollTo(0, parseInt(savedScrollPosition, 10));
        sessionStorage.removeItem('searchScrollPosition');
      }, 100);
    }
  }

  onPageChange(event: any) {
    this.pageSize = event.pageSize;
    this.loadResources(this.route.snapshot.queryParams);
  }

  onSortChange(sortValue: string): void {
    const option = this.sortService.availableOptions().find(opt => opt.value === sortValue);
    if (option) {
      this.sortService.setSortOption(option);
      this.loadResources(this.route.snapshot.queryParams);
    }
  }

  onToggleSortOrder(): void {
    this.sortService.toggleSortOrder();
    this.loadResources(this.route.snapshot.queryParams);
  }

  getToolTopics(tool: Tool): string[] {
    // Return array of topic terms
    return tool.topic?.map(t => t.term) ?? [];
  }

  getToolOperations(tool: Tool): string[] {
    // Return array of operation terms
    return tool.function?.flatMap(f => f.operation.map(op => op.term)) ?? [];
  }

  viewToolDetails(biotoolsID: string) {
    // Store current scroll position before navigating
    sessionStorage.setItem('searchScrollPosition', window.pageYOffset.toString());
    this.router.navigate(['/tool', biotoolsID]);
  }

}
