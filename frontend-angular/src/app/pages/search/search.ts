import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Tool } from '../../models/tool.model';
import { SearchParams } from '../../models/search.model';
import { BiotoolsApiService } from '../../services/biotools-api.service';

@Component({
  selector: 'app-search',
  imports: [
    CommonModule,
    MatCardModule,
    MatCheckboxModule,
    MatChipsModule,
    MatButtonModule,
    MatSelectModule,
    MatFormFieldModule,
    MatPaginatorModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './search.html',
  styleUrl: './search.scss'
})
export class Search implements OnInit {
  searchQuery = '';
  totalResults = 0;
  pageSize = 25;
  tools: Tool[] = [];
  loading = false;
  
  searchParams: SearchParams = {
    pageSize: 25,
    sort: 'relevance',
    order: 'desc'
  };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private biotoolsApi: BiotoolsApiService
  ) {}

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.searchQuery = params['q'] || '';
      this.searchParams.q = this.searchQuery;
      this.loadTools();
    });
  }

  private loadTools() {
    this.loading = true;
    
    // Use mock data for now - switch to real API when ready
    this.biotoolsApi.searchTools({}).subscribe({
      next: (result) => {
        this.tools = result.results;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error loading tools:', error);
        this.loading = false;
      }
    });
  }

  onSortChange(sortValue: string) {
    this.searchParams.sort = sortValue;
    this.loadTools();
  }

  onPageChange(event: any) {
    this.searchParams.page = event.pageIndex + 1;
    this.searchParams.pageSize = event.pageSize;
    this.loadTools();
  }

  getToolTopics(tool: Tool): string[] {
    return tool.topic?.map(t => t.term) || [];
  }

  getToolType(tool: Tool): string {
    return tool.toolType?.[0]?.term || 'Unknown';
  }

  getOperatingSystems(tool: Tool): string {
    return tool.operatingSystem?.join(', ') || '';
  }

  viewToolDetails(biotoolsID: string) {
    this.router.navigate(['/tool', biotoolsID]);
  }
}
