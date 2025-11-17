import { Injectable, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

export interface SortOption {
  value: string;
  label: string;
}

@Injectable({
  providedIn: 'root'
})
export class SortService {
  
  // Available sort options
  readonly sortOptions: SortOption[] = [
    { value: 'lastUpdate', label: 'Updated' },
    { value: 'additionDate', label: 'Added' },
    { value: 'name', label: 'Name' },
    { value: 'citationCount', label: 'Citation Count' },
    { value: 'citationDate', label: 'Publication Date' }
  ];

  // Score option (added conditionally when there's a search query)
  readonly scoreOption: SortOption = { value: 'score', label: 'Score' };

  // Current sort settings
  currentSort = signal<SortOption>(this.sortOptions[0]); // Default: lastUpdate
  sortOrder = signal<'asc' | 'desc'>('desc'); // Default: descending

  // Dynamic list that may include score option
  availableOptions = signal<SortOption[]>(this.sortOptions);

  constructor(private router: Router) {}

  /**
   * Initialize sorting from URL parameters
   */
  initFromParams(params: { sort?: string; ord?: string }): void {
    // Set sort option
    if (params.sort) {
      const option = this.findSortOption(params.sort);
      if (option) {
        this.currentSort.set(option);
      }
    }

    // Set sort order
    if (params.ord) {
      this.sortOrder.set(params.ord as 'asc' | 'desc');
    }
  }

  /**
   * Add the Score option when there's a search query
   */
  addScoreOption(): void {
    const options = this.availableOptions();
    if (!options.some(opt => opt.value === 'score')) {
      this.availableOptions.set([this.scoreOption, ...this.sortOptions]);
      this.currentSort.set(this.scoreOption);
    }
  }

  /**
   * Remove the Score option when there's no search query
   */
  removeScoreOption(): void {
    const options = this.availableOptions();
    if (options[0]?.value === 'score') {
      this.availableOptions.set(this.sortOptions);
      // Reset to default if score was selected
      if (this.currentSort().value === 'score') {
        this.currentSort.set(this.sortOptions[0]);
      }
    }
  }

  /**
   * Update the sort option
   */
  setSortOption(option: SortOption): void {
    this.currentSort.set(option);
    this.updateUrl();
  }

  /**
   * Toggle sort order between ascending and descending
   */
  toggleSortOrder(): void {
    this.sortOrder.update(order => order === 'asc' ? 'desc' : 'asc');
    this.updateUrl();
  }

  /**
   * Get current sort parameters for API calls
   */
  getSortParams(): { sort: string; ord: string } {
    return {
      sort: this.currentSort().value,
      ord: this.sortOrder()
    };
  }

  /**
   * Check if sorting is at default (lastUpdate, desc)
   */
  isDefault(): boolean {
    return this.currentSort().value === 'lastUpdate' && this.sortOrder() === 'desc';
  }

  /**
   * Update URL with current sort parameters
   * Note: This should be called after the component has loaded
   */
  updateUrl(): void {
    const queryParams: any = {};
    
    // Only add sort params to URL if not default
    if (!this.isDefault()) {
      queryParams.sort = this.currentSort().value;
      queryParams.ord = this.sortOrder();
    }

    this.router.navigate([], {
      queryParams,
      queryParamsHandling: 'merge',
      replaceUrl: true
    });
  }

  /**
   * Find a sort option by value
   */
  private findSortOption(value: string): SortOption | undefined {
    // Check if it's the score option
    if (value === 'score') {
      return this.scoreOption;
    }
    // Check regular options
    return this.sortOptions.find(opt => opt.value === value);
  }

  /**
   * Reset to default sorting
   */
  reset(): void {
    this.currentSort.set(this.sortOptions[0]);
    this.sortOrder.set('desc');
    this.availableOptions.set(this.sortOptions);
  }
}
