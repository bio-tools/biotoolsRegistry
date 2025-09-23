import { Component, inject, OnInit, signal } from '@angular/core';
import { MatIcon } from '@angular/material/icon';
import { MatTab, MatTabGroup, MatTabLabel } from '@angular/material/tabs';
import { MatButton } from '@angular/material/button';
import { ToolEditSummary } from './components/tool-edit-summary/tool-edit-summary';
import { ToolEditFunction } from './components/tool-edit-function/tool-edit-function';
import { ToolEditJson } from './components/tool-edit-json/tool-edit-json';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Tool, ToolFunction } from '../../model/resource.model';
import { Router } from '@angular/router';
import { ToolEditLabels } from './components/tool-edit-labels/tool-edit-labels';

@Component({
  selector: 'app-tool-edit',
  imports: [
    ToolEditSummary,
    ToolEditFunction,
    ToolEditJson,
    ToolEditLabels,
    ReactiveFormsModule,
    // Angular Material
    MatIcon,
    MatTabGroup,
    MatTab,
    MatButton,
    MatTabLabel
  ],
  templateUrl: './tool-edit.html',
  styleUrl: './tool-edit.scss'
})
export class ToolEdit implements OnInit {
  private fb = inject(FormBuilder);

  software = signal<Tool | null>(null);
  toolFunctions = signal<ToolFunction[]>([]);

  registrationErrorPayload = signal<any>(null);

  //TODO: differentiate between create and edit 
  //TODO: get credit names for suggestions

  //TODO: for storing validation and saving progress
  validationProgress = {};
  savingProgress = {};
  deletingProgress = {};

  // Form groups for each tab
  summaryForm!: FormGroup;
  labelsForm!: FormGroup;

  ngOnInit() {
    this.initializeForms();
    this.initializeMockData();
  }

  initializePermissions() {
    //TODO fetch user permissions for the tool
  }

  private initializeForms() {
    this.summaryForm = this.fb.group({
      name: ['', []]
    });

    // Start with an empty FormGroup for labels; the child `ToolEditLabels`
    // component will add the required FormArray/FormControl entries.
    this.labelsForm = this.fb.group({});
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

  //TODO send resource to validation or saving endpoins
  sendResource(tool: Tool) {
    this.software.set(tool);
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
