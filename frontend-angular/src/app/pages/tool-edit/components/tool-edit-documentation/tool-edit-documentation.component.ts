import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormGroup } from '@angular/forms';
import { Tool } from '../../../../models/tool.model';

@Component({
  selector: 'app-tool-edit-documentation',
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  template: `<div class="tool-edit-form"><p>Documentation editing component - Coming soon</p></div>`,
  styles: [`.tool-edit-form { padding: 2rem; }`]
})
export class ToolEditDocumentationComponent {
  @Input() tool: Tool | null = null;
  @Input() form!: FormGroup;
  @Input() errors: any = null;
}
