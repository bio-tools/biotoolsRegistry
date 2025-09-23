import { Component, inject, OnInit, signal } from '@angular/core';
import { MatIcon } from '@angular/material/icon';
import { MatTab, MatTabGroup } from '@angular/material/tabs';
import { MatButton } from '@angular/material/button';
import { ToolEditSummary } from './components/tool-edit-summary/tool-edit-summary';
import { ToolEditFunction } from './components/tool-edit-function/tool-edit-function';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Resource, ToolFunction } from '../../model/resource.model';
import { Router } from '@angular/router';

@Component({
  selector: 'app-tool-edit',
  imports: [
    ToolEditSummary,
    ToolEditFunction,
    ReactiveFormsModule,
    // Angular Material
    MatIcon,
    MatTabGroup,
    MatTab,
    MatButton
  ],
  templateUrl: './tool-edit.html',
  styleUrl: './tool-edit.scss'
})
export class ToolEdit implements OnInit {
  private fb = inject(FormBuilder);

  software = signal<Resource | null>(null);
  toolFunctions = signal<ToolFunction[]>([]);

  registrationErrorPayload = signal<any>(null);

  // Form groups for each tab
  summaryForm!: FormGroup;

  ngOnInit() {
    this.initializeForms();
    this.initializeMockData();
  }

  private initializeForms() {
    this.summaryForm = this.fb.group({
      name: ['', []]
    });
  }

  private initializeMockData() {
    // Initialize with some mock data for demonstration
    this.toolFunctions.set([
      {
        operation: [],
        input: [],
        output: [],
        note: '',
        cmd: ''
      }
    ]);
  }

  updateFunctions(functions: ToolFunction[]) {
    this.toolFunctions.set(functions);
    
    // Update the software object if it exists
    const currentSoftware = this.software();
    if (currentSoftware) {
      currentSoftware.function = functions;
      this.software.set({ ...currentSoftware });
    }
  }

  notFound() {
    return false;
  }

  canEditTool() {
    return true;
  }

  isCreateMode() {
    return false;
  }

  registrationSuccess() {
    return false;
  }

  viewToolDetails(id: any) {
    return true;
  }
}
