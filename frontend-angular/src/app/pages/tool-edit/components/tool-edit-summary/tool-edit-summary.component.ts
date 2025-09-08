import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormGroup } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

import { Tool } from '../../../../models/tool.model';

@Component({
  selector: 'app-tool-edit-summary',
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule
  ],
  templateUrl: './tool-edit-summary.component.html',
  styleUrls: ['./tool-edit-summary.component.scss']
})
export class ToolEditSummaryComponent {
  @Input() tool: Tool | null = null;
  @Input() form!: FormGroup;
  @Input() errors: any = null;

  hasError(fieldName: string): boolean {
    const control = this.form.get(fieldName);
    return control ? control.invalid && (control.dirty || control.touched) : false;
  }

  getErrorMessage(fieldName: string): string {
    const control = this.form.get(fieldName);
    if (control && control.errors) {
      if (control.errors['required']) {
        return `${fieldName} is required`;
      }
      if (control.errors['email']) {
        return 'Please enter a valid email';
      }
      if (control.errors['url']) {
        return 'Please enter a valid URL';
      }
    }
    return '';
  }
}
