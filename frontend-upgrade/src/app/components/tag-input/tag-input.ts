import { Component, EventEmitter, Input, Output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { BiotoolsApiService } from '../../services/biotools-api';
import { debounceTime, Subject, switchMap } from 'rxjs';

export interface TagItem {
  text: string;
  filter: string;
}

@Component({
  selector: 'app-tag-input',
  standalone: true,
  imports: [CommonModule, FormsModule, MatChipsModule, MatIconModule, MatFormFieldModule, MatInputModule, MatAutocompleteModule],
  templateUrl: './tag-input.html',
  styleUrl: './tag-input.scss'
})
export class TagInput {
  @Input() tags: TagItem[] = [];
  @Output() tagsChange = new EventEmitter<TagItem[]>();
  // Emits when the user presses Enter to add a tag (submit intent)
  @Output() submit = new EventEmitter<void>();

  filterOptions = [
    { value: 'everything', label: 'Everything' },
    { value: 'topic', label: 'Topic' },
    { value: 'operation', label: 'Operation' },
    { value: 'input', label: 'Input' },
    { value: 'output', label: 'Output' },
    { value: 'toolType', label: 'Tool type' },
    { value: 'language', label: 'Language' },
    { value: 'accessibility', label: 'Accessibility' },
    { value: 'cost', label: 'Cost' },
    { value: 'license', label: 'License' },
    { value: 'credit', label: 'Credit' },
    { value: 'collectionID', label: 'Collection' },
    { value: 'name', label: 'Name' }
  ];

  selectedFilter = 'everything';
  inputText = '';
  suggestions: Array<any> = [];
  showFilterMenu = false;
  showSuggestions = false;
  selectedSuggestionIndex = -1;

  private input$ = new Subject<string>();
  private api = inject(BiotoolsApiService);

  constructor() {
    // debounce input and query API
    this.input$.pipe(
      debounceTime(200),
      switchMap(q => {
        // Extract filter and search text from input
        const { filter, searchText } = this.parseInput(q);
        const usedTermName = filter === 'everything' ? 'all' : filter;
        // Don't send search text to API - we'll filter client-side
        const params: any = {};
        return this.api.getUsedTerms(usedTermName, params);
      })
    ).subscribe(list => {
      //TODO backend may return objects; normalise to strings or key property
      const allSuggestions = Array.isArray(list) ? list.map(item => (typeof item === 'string' ? item : (item.term || item.text || item.name || JSON.stringify(item)))) : [];
      
      // Filter suggestions client-side based on the search text
      const { filter, searchText } = this.parseInput(this.inputText);
      let filteredSuggestions = allSuggestions;
      
      if (searchText && searchText.trim().length > 0) {
        filteredSuggestions = allSuggestions.filter(suggestion => 
          suggestion.toLowerCase().includes(searchText.toLowerCase())
        );
      }
      
      // Remove already-selected tags from suggestions
      this.suggestions = filteredSuggestions.filter(suggestion => 
        !this.tags.some(tag => 
          tag.filter === filter && tag.text.toLowerCase() === suggestion.toLowerCase()
        )
      );
      
      this.showSuggestions = this.suggestions.length > 0;
      this.showFilterMenu = false;
    }, _err => {
      this.suggestions = [];
      this.showSuggestions = false;
    });
  }

  onInputFocus() {
    if (!this.inputText || this.inputText.trim().length === 0) {
      this.showFilterMenu = true;
      this.showSuggestions = false;
    }
  }

  onInputBlur() {
    // Delay to allow clicking on suggestions
    setTimeout(() => {
      this.showFilterMenu = false;
      this.showSuggestions = false;
    }, 200);
  }

  selectFilter(filter: string) {
    this.selectedFilter = filter;
    this.showFilterMenu = false;
    // Trigger suggestions for the selected filter
    if (this.inputText && this.inputText.trim().length > 0) {
      this.input$.next(this.inputText);
    }
  }

  /**
   * Parse input to extract filter and search text
   * Examples: "topic:genomics" -> {filter: "topic", searchText: "genomics"}
   *           "filtration" -> {filter: "everything", searchText: "filtration"}
   */
  private parseInput(text: string): { filter: string; searchText: string } {
    const trimmed = (text || '').trim();
    const colonIndex = trimmed.indexOf(':');
    
    if (colonIndex > 0 && colonIndex < trimmed.length - 1) {
      const potentialFilter = trimmed.substring(0, colonIndex).trim();
      const searchText = trimmed.substring(colonIndex + 1).trim();
      
      const filterOption = this.filterOptions.find(f => f.value === potentialFilter);
      if (filterOption) {
        return { filter: potentialFilter, searchText };
      }
    }
    
    return { filter: this.selectedFilter, searchText: trimmed };
  }

  onInputChange(v: string) {
    this.inputText = v;
    this.selectedSuggestionIndex = -1; // Reset selection when typing
    if (v && v.trim().length > 0) {
      this.showFilterMenu = false;
      this.input$.next(v);
    } else {
      this.showFilterMenu = true;
      this.showSuggestions = false;
      this.suggestions = [];
    }
  }

  onKeyDown(event: KeyboardEvent) {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      if (this.showFilterMenu) {
        // Navigate filter menu
        const currentIndex = this.filterOptions.findIndex(f => f.value === this.selectedFilter);
        if (currentIndex < this.filterOptions.length - 1) {
          this.selectedFilter = this.filterOptions[currentIndex + 1].value;
        }
      } else if (this.showSuggestions && this.suggestions.length > 0) {
        // Navigate suggestions
        this.selectedSuggestionIndex = Math.min(this.selectedSuggestionIndex + 1, this.suggestions.length - 1);
      }
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      if (this.showFilterMenu) {
        // Navigate filter menu
        const currentIndex = this.filterOptions.findIndex(f => f.value === this.selectedFilter);
        if (currentIndex > 0) {
          this.selectedFilter = this.filterOptions[currentIndex - 1].value;
        }
      } else if (this.showSuggestions && this.suggestions.length > 0) {
        // Navigate suggestions
        this.selectedSuggestionIndex = Math.max(this.selectedSuggestionIndex - 1, -1);
      }
    } else if (event.key === 'Backspace') {
      // Remove last tag if input is empty
      if ((!this.inputText || this.inputText.length === 0) && this.tags.length > 0) {
        event.preventDefault();
        this.removeTag(this.tags.length - 1);
      }
    } else if (event.key === 'Enter') {
      event.preventDefault();
      if (this.showFilterMenu && this.selectedFilter) {
        // Select the filter and close menu
        this.selectFilter(this.selectedFilter);
      } else if (this.showSuggestions && this.selectedSuggestionIndex >= 0) {
        // Select the highlighted suggestion - add as tag but DON'T submit search
        this.selectSuggestion(this.suggestions[this.selectedSuggestionIndex]);
      } else if (this.inputText && this.inputText.trim().length > 0) {
        // Add the typed text as a tag but DON'T submit search
        this.addFromInput(false);
      } else {
        // Empty input - trigger search with existing tags
        this.submit.emit();
      }
    } else if (event.key === 'Escape') {
      this.showFilterMenu = false;
      this.showSuggestions = false;
      this.selectedSuggestionIndex = -1;
    }
  }

  addFromInput(emitSubmit: boolean = false) {
    const text = (this.inputText || '').trim();
    if (text.length === 0) return;
    
    // Parse shorthand format like "topic:genomics" or "operation:filtration"
    const colonIndex = text.indexOf(':');
    if (colonIndex > 0 && colonIndex < text.length - 1) {
      const potentialFilter = text.substring(0, colonIndex).trim();
      const tagText = text.substring(colonIndex + 1).trim();
      
      // Check if the part before colon is a valid filter
      const filterOption = this.filterOptions.find(f => f.value === potentialFilter);
      if (filterOption && tagText.length > 0) {
        this.addTag(tagText, potentialFilter);
        if (emitSubmit) {
          this.submit.emit();
        }
        return;
      }
    }
    
    // If no valid filter prefix found, use current selected filter
    this.addTag(text);
    if (emitSubmit) {
      // signal parent that user added via Enter and intends to search/submit
      this.submit.emit();
    }
  }

  addTag(text: string, filter?: string) {
    const tagFilter = filter || this.selectedFilter;
    
    // Check if tag already exists (same filter and text)
    const isDuplicate = this.tags.some(tag => 
      tag.filter === tagFilter && tag.text.toLowerCase() === text.toLowerCase()
    );
    
    if (isDuplicate) {
      // Don't add duplicate, just clear input
      this.inputText = '';
      this.suggestions = [];
      this.showSuggestions = false;
      this.showFilterMenu = false;
      return;
    }
    
    this.tags = [...this.tags, { text, filter: tagFilter }];
    this.tagsChange.emit(this.tags);
    this.inputText = '';
    this.suggestions = [];
    this.showSuggestions = false;
    this.showFilterMenu = false;
    // Reset to 'everything' after adding a tag
    this.selectedFilter = 'everything';
  }

  removeTag(i: number) {
    const copy = [...this.tags];
    copy.splice(i, 1);
    this.tags = copy;
    this.tagsChange.emit(this.tags);
  }

  selectSuggestion(s: string) {
    // Add tag but don't submit search - allow user to add more tags
    this.addTag(s);
  }

  getFilterLabel(filterValue: string): string {
    const filter = this.filterOptions.find(f => f.value === filterValue);
    return filter ? filter.label : filterValue;
  }
}
