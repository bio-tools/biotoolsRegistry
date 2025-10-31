import { Component, EventEmitter, Input, Output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { BiotoolsApiService } from '../../services/biotools-api';
import { debounceTime, Subject, switchMap } from 'rxjs';

export interface TagItem {
  text: string;
  filter: string;
}

@Component({
  selector: 'app-tag-input',
  standalone: true,
  imports: [CommonModule, FormsModule, MatChipsModule, MatIconModule, MatFormFieldModule, MatInputModule, MatSelectModule],
  templateUrl: './tag-input.html',
  styleUrl: './tag-input.scss'
})
export class TagInput {
  @Input() tags: TagItem[] = [];
  @Output() tagsChange = new EventEmitter<TagItem[]>();

  filterOptions = [
    'everything','topic','operation','input','output','toolType','language','accessibility','cost','license','credit','collectionID','name'
  ];

  selectedFilter = 'everything';
  inputText = '';
  suggestions: Array<any> = [];

  private input$ = new Subject<string>();
  private api = inject(BiotoolsApiService);

  constructor() {
    // debounce input and query API
    this.input$.pipe(
      debounceTime(200),
      switchMap(q => {
        const usedTermName = this.selectedFilter === 'everything' ? 'all' : this.selectedFilter;
        const params: any = {};
        if (q && q.length > 0) params['q'] = q;
        return this.api.getUsedTerms(usedTermName, params);
      })
    ).subscribe(list => {
      // backend may return objects; normalise to strings or key property
      this.suggestions = Array.isArray(list) ? list.map(item => (typeof item === 'string' ? item : (item.term || item.text || item.name || JSON.stringify(item)))) : [];
    }, _err => {
      this.suggestions = [];
    });
  }

  onInputChange(v: string) {
    this.inputText = v;
    this.input$.next(v);
  }

  addFromInput() {
    const text = (this.inputText || '').trim();
    if (text.length === 0) return;
    this.addTag(text);
  }

  addTag(text: string) {
    this.tags = [...this.tags, { text, filter: this.selectedFilter }];
    this.tagsChange.emit(this.tags);
    this.inputText = '';
    this.suggestions = [];
  }

  removeTag(i: number) {
    const copy = [...this.tags];
    copy.splice(i, 1);
    this.tags = copy;
    this.tagsChange.emit(this.tags);
  }

  selectSuggestion(s: string) {
    this.addTag(s);
  }
}
