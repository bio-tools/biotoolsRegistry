import { Component, inject, OnInit, signal } from '@angular/core';
import { MatIcon } from '@angular/material/icon';
import { MatTab, MatTabGroup } from '@angular/material/tabs';
import { MatButton } from '@angular/material/button';
import { ToolEditSummary } from './components/tool-edit-summary/tool-edit-summary';
import { FormBuilder, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Resource } from '../../model/resource.model';
import { Router } from '@angular/router';

@Component({
  selector: 'app-tool-edit',
  imports: [
    ToolEditSummary,
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

  registrationErrorPayload = signal<any>(null);

  // Form groups for each tab
  summaryForm!: FormGroup;

  ngOnInit() {
    this.initializeForms();
  }

  private initializeForms() {
    this.summaryForm = this.fb.group({
      name: ['', []]
    });
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
