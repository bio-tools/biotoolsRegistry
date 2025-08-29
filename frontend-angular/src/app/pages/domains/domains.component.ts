import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Domain } from '../../models/domain.model';

@Component({
  selector: 'app-domains',
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatGridListModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './domains.component.html',
  styleUrl: './domains.component.scss'
})
export class Domains implements OnInit {
  domains: Domain[] = [];
  loading = false;

  constructor(private router: Router) {}

  ngOnInit() {
    this.loadDomains();
  }

  private loadDomains() {
    this.loading = true;
    
    // Mock data - replace with actual API call
    setTimeout(() => {
      this.domains = [
        {
          name: 'Sequence Analysis',
          description: 'Tools for analyzing biological sequences including DNA, RNA, and protein sequences.',
          slug: 'sequence-analysis',
          toolCount: 8542,
          subcategories: ['Alignment', 'Annotation', 'Assembly', 'Motif discovery'],
          color: '#1976d2',
          icon: 'biotech'
        },
        {
          name: 'Structural Biology',
          description: 'Tools for protein structure analysis, prediction, and visualization.',
          slug: 'structural-biology',
          toolCount: 2134,
          subcategories: ['Structure prediction', 'Molecular dynamics', 'Visualization'],
          color: '#388e3c',
          icon: 'scatter_plot'
        },
        {
          name: 'Genomics',
          description: 'Tools for genome-wide analysis and comparative genomics.',
          slug: 'genomics',
          toolCount: 4521,
          subcategories: ['Variant analysis', 'Genome assembly', 'Comparative genomics'],
          color: '#f57c00',
          icon: 'dna'
        },
        {
          name: 'Proteomics',
          description: 'Tools for protein identification, quantification, and analysis.',
          slug: 'proteomics',
          toolCount: 1876,
          subcategories: ['Mass spectrometry', 'Protein identification', 'PTM analysis'],
          color: '#7b1fa2',
          icon: 'bubble_chart'
        },
        {
          name: 'Phylogenetics',
          description: 'Tools for evolutionary analysis and phylogenetic tree construction.',
          slug: 'phylogenetics',
          toolCount: 987,
          subcategories: ['Tree construction', 'Evolutionary analysis', 'Dating'],
          color: '#d32f2f',
          icon: 'account_tree'
        },
        {
          name: 'Metabolomics',
          description: 'Tools for metabolite analysis and metabolic pathway reconstruction.',
          slug: 'metabolomics',
          toolCount: 654,
          subcategories: ['Pathway analysis', 'Metabolite identification', 'Flux analysis'],
          color: '#303f9f',
          icon: 'device_hub'
        },
        {
          name: 'Transcriptomics',
          description: 'Tools for RNA-seq analysis and gene expression studies.',
          slug: 'transcriptomics',
          toolCount: 3421,
          subcategories: ['RNA-seq', 'Expression analysis', 'Alternative splicing'],
          color: '#00796b',
          icon: 'timeline'
        },
        {
          name: 'Epigenomics',
          description: 'Tools for epigenetic analysis including DNA methylation and histone modifications.',
          slug: 'epigenomics',
          toolCount: 892,
          subcategories: ['DNA methylation', 'Histone modifications', 'Chromatin analysis'],
          color: '#5d4037',
          icon: 'layers'
        }
      ];
      this.loading = false;
    }, 500);
  }

  onDomainClick(domain: Domain) {
    this.router.navigate(['/search'], { 
      queryParams: { domain: domain.slug } 
    });
  }

  onExploreTools(domain: Domain) {
    this.router.navigate(['/search'], { 
      queryParams: { domain: domain.slug } 
    });
  }

  getTotalTools(): number {
    return this.domains.reduce((total, domain) => total + domain.toolCount, 0);
  }

  getTotalSubcategories(): number {
    return this.domains.reduce((total, domain) => total + (domain.subcategories?.length || 0), 0);
  }
}
