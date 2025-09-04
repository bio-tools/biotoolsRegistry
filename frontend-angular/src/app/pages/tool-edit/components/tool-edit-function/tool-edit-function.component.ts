import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormGroup } from '@angular/forms';
import { Tool } from '../../../../models/tool.model';

@Component({
  selector: 'app-tool-edit-function',
  standalone: true,
  imports: [CommonModule],
  template: '<div class="tool-edit-form"><p>Function editing component - Coming soon</p></div>',
  styleUrls: ['../tool-edit-labels/tool-edit-labels.component.scss']
})
export class ToolEditFunctionComponent {
  @Input() tool: Tool | null = null;
  @Input() form!: FormGroup;
  @Input() errors: any = null;
}
