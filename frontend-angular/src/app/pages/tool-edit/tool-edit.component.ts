import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, ActivatedRoute, RouterLink } from '@angular/router';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatTabsModule } from '@angular/material/tabs';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatDialogModule } from '@angular/material/dialog';

import { Tool } from '../../models/tool.model';
import { ToolService } from '../../services/tool.service';
import { AuthService } from '../../services/auth.service';

// Import tab components (to be created)
import { ToolEditSummaryComponent } from './components/tool-edit-summary/tool-edit-summary.component';
import { ToolEditFunctionComponent } from './components/tool-edit-function/tool-edit-function.component';
import { ToolEditLabelsComponent } from './components/tool-edit-labels/tool-edit-labels.component';
import { ToolEditLinksComponent } from './components/tool-edit-links/tool-edit-links.component';
import { ToolEditDownloadComponent } from './components/tool-edit-download/tool-edit-download.component';
import { ToolEditDocumentationComponent } from './components/tool-edit-documentation/tool-edit-documentation.component';
import { ToolEditPublicationsComponent } from './components/tool-edit-publications/tool-edit-publications.component';
import { ToolEditCreditsComponent } from './components/tool-edit-credits/tool-edit-credits.component';
import { ToolEditRelationsComponent } from './components/tool-edit-relations/tool-edit-relations.component';
import { ToolEditJsonComponent } from './components/tool-edit-json/tool-edit-json.component';
import { ToolEditPermissionsComponent } from './components/tool-edit-permissions/tool-edit-permissions.component';

interface ValidationProgress {
  inProgress: boolean;
  success: boolean;
  error: boolean;
}

interface SavingProgress {
  inProgress: boolean;
  success: boolean;
  error: boolean;
}

interface DeletingProgress {
  inProgress: boolean;
  success: boolean;
  error: boolean;
}

@Component({
  selector: 'app-tool-edit',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    RouterLink,
    MatTabsModule,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    MatDialogModule,
    ToolEditSummaryComponent,
    ToolEditFunctionComponent,
    ToolEditLabelsComponent,
    ToolEditLinksComponent,
    ToolEditDownloadComponent,
    ToolEditDocumentationComponent,
    ToolEditPublicationsComponent,
    ToolEditCreditsComponent,
    ToolEditRelationsComponent,
    ToolEditJsonComponent,
    ToolEditPermissionsComponent
  ],
  templateUrl: './tool-edit.component.html',
  styleUrls: ['./tool-edit.component.scss']
})
export class ToolEditComponent implements OnInit {
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private toolService = inject(ToolService);
  private authService = inject(AuthService);
  private snackBar = inject(MatSnackBar);
  private fb = inject(FormBuilder);

  // Signals for component state
  software = signal<Tool | null>(null);
  loading = signal(true);
  notFound = signal(false);
  isCreateMode = signal(false);
  canEditTool = signal(false);
  currentUser = signal<any>(null);

  // Progress tracking
  validationProgress = signal<ValidationProgress>({
    inProgress: false,
    success: false,
    error: false
  });

  savingProgress = signal<SavingProgress>({
    inProgress: false,
    success: false,
    error: false
  });

  deletingProgress = signal<DeletingProgress>({
    inProgress: false,
    success: false,
    error: false
  });

  registrationSuccess = signal(false);
  registrationErrorPayload = signal<any>(null);

  // Form groups for each tab
  summaryForm!: FormGroup;
  functionForm!: FormGroup;
  labelsForm!: FormGroup;
  linksForm!: FormGroup;
  downloadForm!: FormGroup;
  documentationForm!: FormGroup;
  publicationsForm!: FormGroup;
  creditsForm!: FormGroup;
  relationsForm!: FormGroup;
  jsonForm!: FormGroup;

  // Computed properties
  pageTitle = computed(() => {
    return this.isCreateMode() ? 'Add new tool' : 'Update tool';
  });

  showPermissionsTab = computed(() => {
    const user = this.currentUser();
    const tool = this.software();
    return user && tool && (user.username === tool.owner || user.is_superuser);
  });

  ngOnInit() {
    this.initializeForms();
    this.loadCurrentUser();
    this.loadToolData();
  }

  private initializeForms() {
    this.summaryForm = this.fb.group({
      name: ['', [Validators.required]],
      description: ['', [Validators.required]],
      homepage: [''],
      version: ['']
    });

    this.functionForm = this.fb.group({});
    this.labelsForm = this.fb.group({});
    this.linksForm = this.fb.group({});
    this.downloadForm = this.fb.group({});
    this.documentationForm = this.fb.group({});
    this.publicationsForm = this.fb.group({});
    this.creditsForm = this.fb.group({});
    this.relationsForm = this.fb.group({});
    this.jsonForm = this.fb.group({});
  }

  private loadCurrentUser() {
    this.authService.getCurrentUser().subscribe({
      next: (user) => {
        this.currentUser.set(user);
      },
      error: (error) => {
        console.error('Error loading current user:', error);
      }
    });
  }

  private loadToolData() {
    const toolId = this.route.snapshot.paramMap.get('id');
    
    if (toolId === 'new') {
      this.isCreateMode.set(true);
      this.canEditTool.set(true);
      this.software.set(this.createEmptyTool());
      this.loading.set(false);
    } else if (toolId) {
      this.toolService.getTool(toolId).subscribe({
        next: (tool) => {
          this.software.set(tool);
          this.checkEditPermissions(tool);
          this.loading.set(false);
          this.populateForms(tool);
        },
        error: (error) => {
          console.error('Error loading tool:', error);
          this.notFound.set(true);
          this.loading.set(false);
        }
      });
    }
  }

  private createEmptyTool(): Tool {
    return {
      biotoolsID: '',
      name: '',
      description: '',
      homepage: '',
      biotoolsCURIE: '',
      function: [],
      toolType: [],
      topic: [],
      operatingSystem: [],
      language: [],
      credit: [],
      publication: [],
      download: [],
      documentation: [],
      relation: []
    };
  }

  private checkEditPermissions(tool: Tool) {
    const user = this.currentUser();
    if (user) {
      this.canEditTool.set(
        user.username === tool.owner || user.is_superuser || this.isCreateMode()
      );
    }
  }

  private populateForms(tool: Tool) {
    this.summaryForm.patchValue({
      name: tool.name,
      description: tool.description,
      homepage: tool.homepage,
      version: tool.version
    });
  }

  // Event handlers
  onValidateClick() {
    this.validationProgress.set({
      inProgress: true,
      success: false,
      error: false
    });

    const toolData = this.getCurrentToolData();
    
    this.toolService.validateTool(toolData).subscribe({
      next: (response) => {
        this.validationProgress.set({
          inProgress: false,
          success: true,
          error: false
        });
        this.registrationErrorPayload.set(null);
        this.snackBar.open('Validation successful', 'Close', { duration: 3000 });
      },
      error: (error) => {
        this.validationProgress.set({
          inProgress: false,
          success: false,
          error: true
        });
        this.registrationErrorPayload.set(error.error);
        this.snackBar.open('Validation failed', 'Close', { duration: 3000 });
      }
    });
  }

  onSaveClick() {
    this.savingProgress.set({
      inProgress: true,
      success: false,
      error: false
    });

    const toolData = this.getCurrentToolData();
    const operation = this.isCreateMode() 
      ? this.toolService.createTool(toolData)
      : this.toolService.updateTool(toolData.biotoolsID, toolData);

    operation.subscribe({
      next: (response) => {
        this.savingProgress.set({
          inProgress: false,
          success: true,
          error: false
        });
        this.registrationSuccess.set(true);
        this.registrationErrorPayload.set(null);
        this.snackBar.open('Tool saved successfully', 'Close', { duration: 3000 });
        
        if (this.isCreateMode()) {
          this.router.navigate(['/tool-edit', response.biotoolsID]);
        }
      },
      error: (error) => {
        this.savingProgress.set({
          inProgress: false,
          success: false,
          error: true
        });
        this.registrationErrorPayload.set(error.error);
        this.snackBar.open('Save failed', 'Close', { duration: 3000 });
      }
    });
  }

  onDeleteClick() {
    if (confirm('Are you sure you want to delete this tool?')) {
      this.deletingProgress.set({
        inProgress: true,
        success: false,
        error: false
      });

      const tool = this.software();
      if (tool) {
        this.toolService.deleteTool(tool.biotoolsID).subscribe({
          next: () => {
            this.deletingProgress.set({
              inProgress: false,
              success: true,
              error: false
            });
            this.snackBar.open('Tool deleted successfully', 'Close', { duration: 3000 });
            this.router.navigate(['/search']);
          },
          error: (error) => {
            this.deletingProgress.set({
              inProgress: false,
              success: false,
              error: true
            });
            this.snackBar.open('Delete failed', 'Close', { duration: 3000 });
          }
        });
      }
    }
  }

  onGoToEntry() {
    const tool = this.software();
    if (tool && tool.biotoolsID) {
      this.router.navigate(['/tool', tool.biotoolsID]);
    }
  }

  private getCurrentToolData(): Tool {
    const currentTool = this.software();
    if (!currentTool) {
      throw new Error('No tool data available');
    }

    // Merge form data with current tool data
    const summaryData = this.summaryForm.value;
    
    return {
      ...currentTool,
      name: summaryData.name,
      description: summaryData.description,
      homepage: summaryData.homepage,
      version: summaryData.version
    };
  }

  // Tab error checking
  hasTabErrors(tabName: string): boolean {
    switch (tabName) {
      case 'summary':
        return this.summaryForm.invalid;
      case 'function':
        return this.registrationErrorPayload()?.function;
      case 'labels':
        return this.labelsForm.invalid;
      case 'links':
        return this.linksForm.invalid || this.registrationErrorPayload()?.link;
      case 'download':
        return this.downloadForm.invalid;
      case 'documentation':
        return this.documentationForm.invalid || this.registrationErrorPayload()?.documentation;
      case 'publications':
        return this.publicationsForm.invalid || this.registrationErrorPayload()?.publication;
      case 'credits':
        return this.creditsForm.invalid || this.registrationErrorPayload()?.credit;
      case 'relations':
        return this.relationsForm.invalid;
      case 'json':
        return this.jsonForm.invalid || this.registrationErrorPayload();
      default:
        return false;
    }
  }
}
