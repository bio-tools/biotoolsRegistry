import { Component, Input, Output, EventEmitter, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatCardModule } from '@angular/material/card';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { ToolFunction, DataFormat, Operation, Format } from '../../../../model/resource.model';
import { EdamModal, EdamModalData } from '../../../../components/edam-modal/edam-modal';

@Component({
  selector: 'app-tool-edit-function',
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatCardModule,
    MatTooltipModule,
    MatDialogModule
  ],
  templateUrl: './tool-edit-function.html',
  styleUrl: './tool-edit-function.scss'
})
export class ToolEditFunction {
  @Input() functions = signal<ToolFunction[]>([]);
  @Input() errors = signal<any>({});
  
  @Output() functionsChange = new EventEmitter<ToolFunction[]>();

  constructor(private dialog: MatDialog) {}

  // Add a new function
  addFunction() {
    const newFunction: ToolFunction = {
      operation: [],
      input: [],
      output: [],
      note: '',
      cmd: ''
    };
    
    const currentFunctions = this.functions();
    this.functions.set([...currentFunctions, newFunction]);
    this.functionsChange.emit(this.functions());
  }

  // Remove a function
  removeFunction(index: number) {
    const currentFunctions = this.functions();
    currentFunctions.splice(index, 1);
    this.functions.set([...currentFunctions]);
    this.functionsChange.emit(this.functions());
  }

  // Open EDAM modal for operations
  addOperation(functionItem: ToolFunction) {
    const dialogRef = this.dialog.open(EdamModal, {
      width: '600px',
      data: {
        type: 'operation',
        data: functionItem.operation,
        parentObject: functionItem
      } as EdamModalData
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.functionsChange.emit(this.functions());
      }
    });
  }

  // Remove operation from a function
  removeOperation(functionItem: ToolFunction, operationIndex: number) {
    functionItem.operation.splice(operationIndex, 1);
    this.functionsChange.emit(this.functions());
  }

  // Open EDAM modal for input data
  addInput(functionItem: ToolFunction) {
    if (!functionItem.input) {
      functionItem.input = [];
    }

    const dialogRef = this.dialog.open(EdamModal, {
      width: '600px',
      data: {
        type: 'data',
        data: functionItem.input,
        parentObject: functionItem
      } as EdamModalData
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.functionsChange.emit(this.functions());
      }
    });
  }

  // Remove input from a function
  removeInput(functionItem: ToolFunction, inputIndex: number) {
    functionItem.input?.splice(inputIndex, 1);
    this.functionsChange.emit(this.functions());
  }

  // Open EDAM modal for output data
  addOutput(functionItem: ToolFunction) {
    if (!functionItem.output) {
      functionItem.output = [];
    }

    const dialogRef = this.dialog.open(EdamModal, {
      width: '600px',
      data: {
        type: 'data',
        data: functionItem.output,
        parentObject: functionItem
      } as EdamModalData
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.functionsChange.emit(this.functions());
      }
    });
  }

  // Remove output from a function
  removeOutput(functionItem: ToolFunction, outputIndex: number) {
    functionItem.output?.splice(outputIndex, 1);
    this.functionsChange.emit(this.functions());
  }

  // Open EDAM modal for format
  addFormat(dataFormat: DataFormat) {
    if (!dataFormat.format) {
      dataFormat.format = [];
    }

    const dialogRef = this.dialog.open(EdamModal, {
      width: '600px',
      data: {
        type: 'format',
        data: dataFormat.format,
        parentObject: dataFormat
      } as EdamModalData
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.functionsChange.emit(this.functions());
      }
    });
  }

  // Remove format from input or output
  removeFormat(dataFormat: DataFormat, formatIndex: number) {
    dataFormat.format?.splice(formatIndex, 1);
    this.functionsChange.emit(this.functions());
  }

  // Edit data (input/output)
  editData(dataFormat: DataFormat) {
    const dialogRef = this.dialog.open(EdamModal, {
      width: '600px',
      data: {
        type: 'data',
        data: dataFormat.data,
        parentObject: dataFormat
      } as EdamModalData
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.functionsChange.emit(this.functions());
      }
    });
  }

  // Update function command
  updateCommand(functionItem: ToolFunction, cmd: string) {
    functionItem.cmd = cmd;
    this.functionsChange.emit(this.functions());
  }

  // Update function note
  updateNote(functionItem: ToolFunction, note: string) {
    functionItem.note = note;
    this.functionsChange.emit(this.functions());
  }

  // Get error for specific path
  getError(path: string): string[] {
    const errorObj = this.errors();
    const pathParts = path.split('.');
    let current = errorObj;
    
    for (const part of pathParts) {
      if (current && current[part]) {
        current = current[part];
      } else {
        return [];
      }
    }
    
    return Array.isArray(current) ? current : [];
  }

  // Track by function for ngFor
  trackByFunction(index: number, item: ToolFunction): any {
    return index;
  }

  // Track by operation for ngFor
  trackByOperation(index: number, item: Operation): any {
    return item.uri || index;
  }

  // Track by data format for ngFor
  trackByDataFormat(index: number, item: DataFormat): any {
    return item.data.uri || index;
  }

  // Track by format for ngFor
  trackByFormat(index: number, item: Format): any {
    return item.uri || index;
  }
}
