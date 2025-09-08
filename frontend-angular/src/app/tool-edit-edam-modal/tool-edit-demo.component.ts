
import { Component } from '@angular/core';
import { CommonModule, JsonPipe } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { ToolEditEdamModalComponent, EdamModalData } from '../tool-edit-edam-modal/tool-edit-edam-modal.component';

@Component({
  selector: 'app-tool-edit-demo',
  imports: [CommonModule, MatButtonModule, MatDialogModule, JsonPipe],
  template: `
    <button mat-raised-button color="accent" (click)="openEdamModal()">Open EDAM Modal</button>
    <div *ngIf="modalResult">
      <h3>Modal Result:</h3>
      <pre>{{ modalResult | json }}</pre>
    </div>
  `
})
export class ToolEditDemoComponent {
  modalResult: any;

  constructor(private dialog: MatDialog) {}

  openEdamModal() {
    const dialogRef = this.dialog.open(ToolEditEdamModalComponent, {
      width: '600px',
      data: {
        type: 'data',
        suggestions: [
          { term: 'EDAM:0001' },
          { term: 'EDAM:0002' }
        ],
        onto: [
          { text: 'Root', data: { uri: 'EDAM:root' }, children: [
            { text: 'Child 1', data: { uri: 'EDAM:child1' }, children: [] },
            { text: 'Child 2', data: { uri: 'EDAM:child2' }, children: [] }
          ]}
        ],
        data: { data: {} }
      } as EdamModalData
    });

    dialogRef.afterClosed().subscribe(result => {
      this.modalResult = result;
    });
  }
}
