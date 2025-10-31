import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { TagInput } from '../../components/tag-input/tag-input';
import type { TagItem } from '../../components/tag-input/tag-input';


@Component({
  selector: 'app-home',
  imports: [CommonModule, FormsModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatCardModule, TagInput],
  templateUrl: './home.html',
  styleUrl: './home.scss'
})
export class Home {
  router = inject(Router);

  // tags in legacy format: { text, filter }
  queryTags: TagItem[] = [];

  // logos shown on the home page with personalized alt/title text
  logos: { file: string; alt: string }[] = [
    { file: 'dtu.png', alt: 'Technical University of Denmark' },
    { file: 'ku.png', alt: 'University of Copenhagen' },
    { file: 'aarhus-uni.jpg', alt: 'Aarhus University' },
    { file: 'aalborg-uni.png', alt: 'Aalborg University' },
    { file: 'sdu2.png', alt: 'University of Southern Denmark' },
    { file: 'institut-pasteur.png', alt: 'Institut Pasteur' },
    { file: 'bergen.jpg', alt: 'University of Bergen' },
    { file: 'bsc.jpg', alt: 'Barcelona Supercomputing Center' },
    { file: 'ceitec.jpg', alt: 'Central European Institute of Technology' },
    { file: 'tartu.png', alt: 'University of Tartu' },
    { file: 'embl.png', alt: 'EMBL-EBI' },
    { file: 'sib.png', alt: 'Swiss Institute of Bioinformatics' },
    { file: 'irb.jpeg', alt: 'Institute For Research In Biomedicine Barcelona' },
    { file: 'inesc.png', alt: 'Instituto de Engenharia de Sistemas e Computadores - Investigação e Desenvolvimento' },
    { file: 'cnrs.png', alt: 'Centre national de la recherche scientifique' },
    { file: 'OIP.jpeg', alt: 'Leiden University Medical Center' }
  ];

  doSearch() {
    const params: any = {};
    params['page'] = 1;
    params['sort'] = 'score';

    // Build q from 'everything' tags and other filters
    for (const t of this.queryTags) {
      if (t.filter === 'everything') {
        if (params['q'] && params['q'].length > 0) params['q'] += '+' + t.text;
        else params['q'] = t.text;
      } else {
        // if multiple tags for same filter, take last one (simple behaviour)
        params[t.filter] = t.text;
      }
    }

    // If no params at all, navigate to /t (full list)
    const hasParams = Object.keys(params).some(k => params[k] !== undefined && params[k] !== null && params[k] !== '');
    if (!hasParams) {
      this.router.navigate(['/t']);
    } else {
      this.router.navigate(['/t'], { queryParams: params });
    }
  }

  // helper to navigate to search with quoted topic/operation (match legacy quoting)
  quote(v: string) {
    if (!v) return '';
    return `"${v}"`;
  }

  goToTopic(topic: string) {
    this.router.navigate(['/t'], { queryParams: { topic: this.quote(topic), page: 1, sort: 'score' } });
  }

  goToOperation(op: string) {
    this.router.navigate(['/t'], { queryParams: { operation: this.quote(op), page: 1, sort: 'score' } });
  }

}
