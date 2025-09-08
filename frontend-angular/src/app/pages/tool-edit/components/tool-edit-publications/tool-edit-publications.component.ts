import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormGroup } from '@angular/forms';
import { Tool } from '../../../../models/tool.model';

@Component({
  selector: 'app-tool-edit-publications',
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  template: `<div class="tool-edit-form"><p>Publications editing component - Coming soon</p></div>`,
  styles: [`.tool-edit-form { padding: 2rem; }`]
})
export class ToolEditPublicationsComponent {
  @Input() tool: Tool | null = null;
  @Input() form!: FormGroup;
  @Input() errors: any = null;
}
