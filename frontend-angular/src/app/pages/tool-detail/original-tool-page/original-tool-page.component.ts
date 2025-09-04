import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { BiotoolsApiService } from '../../../services/biotools-api.service';
import { Tool } from '../../../models/tool.model';

@Component({
  selector: 'app-original-tool-page',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTooltipModule
  ],
  templateUrl: './original-tool-page.component.html',
  styleUrl: './original-tool-page.component.scss'
})
export class OriginalToolPageComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private biotoolsApi = inject(BiotoolsApiService);
  
  software = signal<Tool | null>(null);
  loading = signal<boolean>(true);
  notFound = signal<boolean>(false);

  ngOnInit() {
    this.route.params.subscribe(params => {
      const toolId = params['id'];
      if (toolId) {
        this.loadTool(toolId);
      }
    });
  }

  private loadTool(id: string) {
    this.loading.set(true);
    this.notFound.set(false);
    
    this.biotoolsApi.getTool(id).subscribe({
      next: (tool) => {
        this.software.set(tool);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading tool:', error);
        this.notFound.set(true);
        this.loading.set(false);
      }
    });
  }

  // Helper methods for template
  hasCredits(): boolean {
    return !!(this.software()?.credit?.length);
  }

  hasDocumentation(): boolean {
    return !!(this.software()?.documentation?.length);
  }

  hasDownloads(): boolean {
    return !!(this.software()?.download?.length);
  }

  hasLinks(): boolean {
    // Check if there are links in homepage or other link sources
    const tool = this.software();
    return !!(tool?.homepage);
  }

  hasContacts(): boolean {
    // In bio.tools, contact info might be in credit entries with specific roles
    return !!this.software()?.credit?.some(credit => 
      credit.typeRole?.some(role => 
        role.toLowerCase().includes('contact') || 
        role.toLowerCase().includes('support')
      )
    );
  }

  hasPublications(): boolean {
    return !!(this.software()?.publication?.length);
  }

  goBack(): void {
    this.router.navigate(['/search']);
  }

  openHomepage(): void {
    const homepage = this.software()?.homepage;
    if (homepage) {
      window.open(homepage, '_blank');
    }
  }

  openBiotoolsEntry(): void {
    const biotoolsId = this.software()?.biotoolsID;
    if (biotoolsId) {
      window.open(`https://bio.tools/${biotoolsId}`, '_blank');
    }
  }
}
