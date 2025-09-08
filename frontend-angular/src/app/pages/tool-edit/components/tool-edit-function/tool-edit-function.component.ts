import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { FormGroup } from '@angular/forms';
import { Tool } from '../../../../models/tool.model';
import { MatDialog } from '@angular/material/dialog';
import { MaterialModalComponent } from '../../../../material-modal/material-modal';
import { ToolEditDemoComponent } from '../../../../tool-edit-edam-modal/tool-edit-demo.component';

@Component({
  selector: 'app-tool-edit-function',
  imports: [CommonModule, MatIconModule, ToolEditDemoComponent],
  templateUrl: './tool-edit-function.component.html',
  styleUrls: ['../tool-edit-labels/tool-edit-labels.component.scss']
})
export class ToolEditFunctionComponent {
  @Input() tool: Tool | null = null;
  @Input() form!: FormGroup;
  @Input() errors: any = null;

  constructor(public dialog: MatDialog) {}

  openModal(): void {
    this.dialog.open(MaterialModalComponent);
  }
}
