import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule, FormGroup } from '@angular/forms';
import { Tool } from '../../../../models/tool.model';

@Component({
  selector: 'app-tool-edit-credits',
  imports: [CommonModule, FormsModule, ReactiveFormsModule],
  template: `<div class="tool-edit-form"><p>Credits editing component - Coming soon</p></div>`,
  styles: [`.tool-edit-form { padding: 2rem; }`]
})
export class ToolEditCreditsComponent {
  @Input() tool: Tool | null = null;
  @Input() form!: FormGroup;
  @Input() errors: any = null;
}
