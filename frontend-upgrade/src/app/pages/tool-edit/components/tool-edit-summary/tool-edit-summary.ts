import { Component, Input } from '@angular/core';
import { Resource } from '../../../../model/resource.model';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatError } from '@angular/material/form-field';

@Component({
  selector: 'app-tool-edit-summary',
  imports: [
    ReactiveFormsModule,
    MatInputModule,
    MatFormFieldModule,
    MatError
  ],
  templateUrl: './tool-edit-summary.html',
  styleUrl: './tool-edit-summary.scss'
})
export class ToolEditSummary {

  @Input() tool: Resource | null = null;
  @Input() form!: FormGroup; // Replace 'any' with the actual type of your form if available
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
