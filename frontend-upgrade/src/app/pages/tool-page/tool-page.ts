import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ActivatedRoute, Router } from '@angular/router';
import { Tool } from '../../model/resource.model';
import { Resources } from '../../services/resources';

@Component({
  selector: 'app-tool-page',
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatTooltipModule
  ],
  templateUrl: './tool-page.html',
  styleUrl: './tool-page.scss'
})
export class ToolPage implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private resourcesAPI = inject(Resources);
  
  software = signal<Tool | null>(null);
  loading = signal<boolean>(true);
  notFound = signal<boolean>(false);

  ngOnInit() {
    this.route.params.subscribe(params => {
      const toolId = params['id'];
      console.log('Route param id:', toolId);
      if (toolId) {
        this.loadTool(toolId);
      }
    });
  }

  private loadTool(id: string) {
    this.loading.set(true);
    this.notFound.set(false);
    
    this.resourcesAPI.getToolByID(id).subscribe({
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

  goBackToSearch() {
    this.router.navigate(['/t']);
  }


}
