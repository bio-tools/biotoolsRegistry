import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

export interface EdamModalData {
  type: 'data' | 'operation' | 'format';
  suggestions: { term: string; }[];
  onto: any[];
  data: any;
}

import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatExpansionModule } from '@angular/material/expansion';
import { EdamTreeComponent } from './edam-tree.component';

@Component({
  selector: 'app-tool-edit-edam-modal',
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatExpansionModule,
    EdamTreeComponent
  ],
  templateUrl: './tool-edit-edam-modal.component.html',
  styleUrls: ['./tool-edit-edam-modal.component.css']
})
export class ToolEditEdamModalComponent {
  predicate = '';

  constructor(
    public dialogRef: MatDialogRef<ToolEditEdamModalComponent>,
    @Inject(MAT_DIALOG_DATA) public vm: EdamModalData
  ) {}

  applySuggestion(suggestion: { term: string }) {
    // You may want to update vm.data here as needed
    this.dialogRef.close({ selected: suggestion });
  }

  saveData() {
    this.dialogRef.close({ saved: true, data: this.vm.data });
  }

  cancel() {
    this.dialogRef.close();
  }
}
