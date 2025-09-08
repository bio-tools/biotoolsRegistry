import { Component, Input, Output, EventEmitter } from '@angular/core';

import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-edam-tree',
  imports: [CommonModule],
  template: `
    <ul>
      <ng-container *ngFor="let node of filteredTree(treeData)">
        <li>
          <span (click)="selectNode(node)">{{ node.text }}</span>
          <app-edam-tree *ngIf="node.children" [treeData]="node.children" [filter]="filter" (select)="onSelect($event)"></app-edam-tree>
        </li>
      </ng-container>
    </ul>
  `
})
export class EdamTreeComponent {
  @Input() treeData: any[] = [];
  @Input() filter: string = '';
  @Output() select = new EventEmitter<any>();

  filteredTree(tree: any[]): any[] {
    if (!this.filter) return tree;
    return tree.filter(node =>
      node.text.toLowerCase().includes(this.filter.toLowerCase()) ||
      (node.children && this.filteredTree(node.children).length > 0)
    );
  }

  selectNode(node: any) {
    this.select.emit(node);
  }

  onSelect(event: any) {
    this.select.emit(event);
  }
}
