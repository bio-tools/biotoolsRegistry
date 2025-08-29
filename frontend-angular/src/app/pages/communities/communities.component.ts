import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Community } from '../../models/domain.model';

@Component({
  selector: 'app-communities',
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './communities.component.html',
  styleUrl: './communities.component.scss'
})
export class Communities implements OnInit {
  communities: Community[] = [];
  loading = false;

  constructor(private router: Router) {}

  ngOnInit() {
    this.loadCommunities();
  }

  private loadCommunities() {
    this.loading = true;
    
    // Mock data - replace with actual API call
    setTimeout(() => {
      this.communities = [
        {
          name: 'ELIXIR',
          description: 'The European bioinformatics infrastructure providing life science data resources and tools.',
          slug: 'elixir',
          memberCount: 21,
          toolCount: 1847,
          website: 'https://elixir-europe.org',
          contact: 'info@elixir-europe.org',
          tags: ['Infrastructure', 'Data sharing', 'Interoperability'],
          established: '2014'
        },
        {
          name: 'Galaxy Project',
          description: 'An open platform for accessible, reproducible, and transparent computational research.',
          slug: 'galaxy',
          memberCount: 150,
          toolCount: 2341,
          website: 'https://galaxyproject.org',
          contact: 'galaxy-contact@galaxyproject.org',
          tags: ['Workflows', 'Reproducibility', 'Education'],
          established: '2005'
        },
        {
          name: 'Bioconductor',
          description: 'Open source software for bioinformatics based on the R statistical computing language.',
          slug: 'bioconductor',
          memberCount: 89,
          toolCount: 1956,
          website: 'https://bioconductor.org',
          contact: 'bioc-devel@r-project.org',
          tags: ['R', 'Statistics', 'Genomics'],
          established: '2001'
        },
        {
          name: 'NCBI',
          description: 'National Center for Biotechnology Information providing biomedical databases and tools.',
          slug: 'ncbi',
          memberCount: 45,
          toolCount: 234,
          website: 'https://ncbi.nlm.nih.gov',
          contact: 'info@ncbi.nlm.nih.gov',
          tags: ['Databases', 'Literature', 'Government'],
          established: '1988'
        },
        {
          name: 'EBI',
          description: 'European Bioinformatics Institute providing freely available data and bioinformatics services.',
          slug: 'ebi',
          memberCount: 67,
          toolCount: 456,
          website: 'https://ebi.ac.uk',
          contact: 'datasubs@ebi.ac.uk',
          tags: ['Data', 'Services', 'Research'],
          established: '1994'
        },
        {
          name: 'Broad Institute',
          description: 'Biomedical research institute focused on genomic medicine and computational biology.',
          slug: 'broad',
          memberCount: 34,
          toolCount: 187,
          website: 'https://broadinstitute.org',
          contact: 'info@broadinstitute.org',
          tags: ['Genomics', 'Medicine', 'Research'],
          established: '2004'
        }
      ];
      this.loading = false;
    }, 500);
  }

  onCommunityClick(community: Community) {
    this.router.navigate(['/search'], { 
      queryParams: { community: community.slug } 
    });
  }

  onVisitWebsite(community: Community) {
    if (community.website) {
      window.open(community.website, '_blank');
    }
  }

  onContactCommunity(community: Community) {
    if (community.contact) {
      window.open(`mailto:${community.contact}`, '_blank');
    }
  }

  getTotalMembers(): number {
    return this.communities.reduce((total, community) => total + community.memberCount, 0);
  }

  getTotalTools(): number {
    return this.communities.reduce((total, community) => total + community.toolCount, 0);
  }
}
