import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Resource } from '../../../../model/resource.model';
import { JsonPipe } from '@angular/common';

@Component({
  selector: 'app-tool-edit-json',
  imports: [
    JsonPipe,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatTooltipModule
  ],
  templateUrl: './tool-edit-json.html',
  styleUrl: './tool-edit-json.scss'
})
export class ToolEditJson implements OnChanges {
  @Input() tool: Resource | null = null;
  @Input() errors: any = null;

  jsonModel: string = '';
  jsonError: string = '';
  errorCollapsed = true;

  ngOnChanges(changes: SimpleChanges) {
    if (changes['tool']) {
      this.updateModelFromTool();
    }
    if (changes['errors']) {
      // Keep error collapsed when new errors come in
      this.errorCollapsed = true;
    }
  }

  private updateModelFromTool() {
    try {
      if (this.tool) {
        this.jsonModel = JSON.stringify(this.tool, null, 2);
        this.jsonError = '';
      } else {
        this.jsonModel = '';
      }
    } catch (e: any) {
      this.jsonError = 'Unable to serialize tool object to JSON';
    }
  }

  onJsonChange(value: string) {
    this.jsonModel = value;
    try {
      JSON.parse(value);
      this.jsonError = '';
    } catch (e: any) {
      this.jsonError = e.message || 'Invalid JSON';
    }
  }

  downloadTool(pretty: boolean) {
    let content = this.jsonModel;
    if (!content && this.tool) {
      content = pretty ? JSON.stringify(this.tool, null, 2) : JSON.stringify(this.tool);
    }

    // If user edited the text, try to validate and use parsed object
    try {
      const parsed = content ? JSON.parse(content) : null;
      content = pretty ? JSON.stringify(parsed, null, 2) : JSON.stringify(parsed);
    } catch (e) {
      // If invalid, fall back to raw content
    }

    const blob = new Blob([content || ''], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'tool.json';
    a.click();
    window.URL.revokeObjectURL(url);
  }

}
