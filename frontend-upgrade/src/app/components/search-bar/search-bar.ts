import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { TagInput, TagItem } from '../tag-input/tag-input';
import { filter } from 'rxjs';

@Component({
  standalone: true,
  selector: 'app-search-bar',
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    TagInput
  ],
  templateUrl: './search-bar.html',
  styleUrl: './search-bar.scss'
})
export class SearchBar implements OnInit {

  // tags used by the tag-input component
  tags: TagItem[] = [];

  private router = inject(Router);
  private route = inject(ActivatedRoute);

  ngOnInit() {
    // Initialize tags from URL parameters
    this.updateTagsFromUrl();

    // Listen to route changes to update tags
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        this.updateTagsFromUrl();
      });
  }

  updateTagsFromUrl() {
    const params = this.route.snapshot.queryParams;
    const newTags: TagItem[] = [];

    // List of all possible filter parameters
    const filterParams = ['topic', 'operation', 'input', 'output', 'toolType', 'language', 
                          'accessibility', 'cost', 'license', 'credit', 'collectionID', 'name'];

    // Handle 'q' parameter (everything filter)
    if (params['q']) {
      const qValues = params['q'].split('+');
      for (const value of qValues) {
        if (value.trim()) {
          newTags.push({ text: value.trim(), filter: 'everything' });
        }
      }
    }

    // Handle specific filter parameters
    for (const filterParam of filterParams) {
      if (params[filterParam]) {
        newTags.push({ text: params[filterParam], filter: filterParam });
      }
    }

    this.tags = newTags;
  }

  // Called when tags change from the TagInput component
  onTagsChange(newTags: TagItem[]) {
    // Only update local state here. Navigation will happen when the user explicitly
    // submits (presses Enter)
    this.tags = newTags || [];
  }

  submitSearch() {
    const params: any = {};
    params['page'] = 1;
    params['sort'] = 'score';

    // Build q from 'everything' tags and other filters
    for (const t of this.tags) {
      if (t.filter === 'everything') {
        if (params['q'] && params['q'].length > 0) params['q'] += '+' + t.text;
        else params['q'] = t.text;
      } else {
        params[t.filter] = t.text;
      }
    }

    this.router.navigate(['/t'], { queryParams: params });
  }
}