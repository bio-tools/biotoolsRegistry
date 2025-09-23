import { Component, Inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatTreeModule } from '@angular/material/tree';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

export interface EdamModalData {
  type: 'data' | 'operation' | 'format';
  data: any;
  parentObject?: any;
  suggestions?: EdamTerm[];
}

export interface EdamTerm {
  term: string;
  uri: string;
  definition?: string;
  exact_synonyms?: string[];
}

export interface EdamTreeNode {
  text: string;
  data: {
    uri: string;
  };
  definition?: string;
  exact_synonyms?: string[];
  children?: EdamTreeNode[];
}

@Component({
  selector: 'app-edam-modal',
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatTreeModule,
    MatIconModule,
    MatTooltipModule
  ],
  templateUrl: './edam-modal.html',
  styleUrl: './edam-modal.scss'
})
export class EdamModal {
  predicate = signal('');
  selectedTerm = signal<EdamTerm | null>(null);
  
  // Mock ontology data - in real implementation, this would come from a service
  ontologyData = signal<EdamTreeNode[]>([
    {
      text: 'Data',
      data: { uri: 'http://edamontology.org/data_0006' },
      definition: 'Information, represented in an information artefact (data record) that is "understandable" by dedicated computational tools that can use the data as input or produce it as output.',
      children: [
        {
          text: 'Sequence',
          data: { uri: 'http://edamontology.org/data_2044' },
          definition: 'One or more molecular sequences, possibly with associated annotation.',
          children: [
            {
              text: 'Protein sequence',
              data: { uri: 'http://edamontology.org/data_2976' },
              definition: 'A molecular sequence corresponding to the primary structure of a protein.'
            },
            {
              text: 'DNA sequence',
              data: { uri: 'http://edamontology.org/data_3494' },
              definition: 'A molecular sequence corresponding to a deoxyribonucleic acid (DNA) molecule.'
            }
          ]
        },
        {
          text: 'Structure',
          data: { uri: 'http://edamontology.org/data_0883' },
          definition: 'Protein or nucleic acid structure.',
          children: [
            {
              text: 'Protein structure',
              data: { uri: 'http://edamontology.org/data_1460' },
              definition: 'An ordered spatial arrangement of amino acids in a protein.'
            }
          ]
        }
      ]
    },
    {
      text: 'Operation',
      data: { uri: 'http://edamontology.org/operation_0004' },
      definition: 'A function that processes a set of inputs and results in a set of outputs, or associates arguments (inputs) with values (outputs).',
      children: [
        {
          text: 'Analysis',
          data: { uri: 'http://edamontology.org/operation_2945' },
          definition: 'Apply analytical methods to existing data of a specific type.',
          children: [
            {
              text: 'Sequence analysis',
              data: { uri: 'http://edamontology.org/operation_2403' },
              definition: 'Analyse nucleotide or protein sequences.'
            }
          ]
        },
        {
          text: 'Comparison',
          data: { uri: 'http://edamontology.org/operation_2424' },
          definition: 'Compare two or more data sets.',
          children: [
            {
              text: 'Sequence alignment',
              data: { uri: 'http://edamontology.org/operation_0292' },
              definition: 'Align two or more molecular sequences.'
            }
          ]
        }
      ]
    },
    {
      text: 'Format',
      data: { uri: 'http://edamontology.org/format_1915' },
      definition: 'A defined way or layout of representing and structuring data in a computer file, blob, string, message, or elsewhere.',
      children: [
        {
          text: 'FASTA',
          data: { uri: 'http://edamontology.org/format_1929' },
          definition: 'A simple text-based format for representing nucleotide or protein sequences.'
        },
        {
          text: 'PDB',
          data: { uri: 'http://edamontology.org/format_1476' },
          definition: 'Protein Data Bank format for atomic coordinate data.'
        }
      ]
    }
  ]);

  constructor(
    public dialogRef: MatDialogRef<EdamModal>,
    @Inject(MAT_DIALOG_DATA) public data: EdamModalData
  ) {}

  // Apply a suggestion
  applySuggestion(suggestion: EdamTerm) {
    this.selectedTerm.set(suggestion);
  }

  // Select a term from the tree
  selectTerm(node: EdamTreeNode) {
    this.selectedTerm.set({
      term: node.text,
      uri: node.data.uri,
      definition: node.definition,
      exact_synonyms: node.exact_synonyms
    });
  }

  // Check if a term is suggested
  isSuggested(node: EdamTreeNode): boolean {
    if (!this.data.suggestions) return false;
    return this.data.suggestions.some(suggestion => 
      suggestion.uri === node.data.uri
    );
  }

  // Save the selected term
  saveData() {
    const selected = this.selectedTerm();
    if (selected) {
      if (this.data.type === 'data') {
        // For data type, update the data object
        if (this.data.data && this.data.data.term !== undefined) {
          this.data.data.term = selected.term;
          this.data.data.uri = selected.uri;
        } else if (Array.isArray(this.data.data)) {
          // Add new data format to array
          this.data.data.push({
            data: {
              term: selected.term,
              uri: selected.uri
            },
            format: []
          });
        }
      } else if (this.data.type === 'operation') {
        // For operation type, add to operations array
        if (Array.isArray(this.data.data)) {
          this.data.data.push({
            term: selected.term,
            uri: selected.uri
          });
        }
      } else if (this.data.type === 'format') {
        // For format type, add to formats array
        if (Array.isArray(this.data.data)) {
          this.data.data.push({
            term: selected.term,
            uri: selected.uri
          });
        }
      }
      
      this.dialogRef.close(selected);
    }
  }

  // Cancel and close dialog
  cancel() {
    this.dialogRef.close();
  }

  // Filter the tree based on predicate
  filterTree(nodes: EdamTreeNode[], predicate: string): EdamTreeNode[] {
    if (!predicate.trim()) return nodes;
    
    const filtered: EdamTreeNode[] = [];
    
    for (const node of nodes) {
      const matchesNode = node.text.toLowerCase().includes(predicate.toLowerCase()) ||
                         (node.definition && node.definition.toLowerCase().includes(predicate.toLowerCase()));
      
      const filteredChildren = node.children ? this.filterTree(node.children, predicate) : [];
      
      if (matchesNode || filteredChildren.length > 0) {
        filtered.push({
          ...node,
          children: filteredChildren.length > 0 ? filteredChildren : undefined
        });
      }
    }
    
    return filtered;
  }

  // Get filtered ontology data
  getFilteredData(): EdamTreeNode[] {
    const predicate = this.predicate();
    if (!predicate.trim()) {
      return this.ontologyData();
    }
    return this.filterTree(this.ontologyData(), predicate);
  }

  // Get the link for more information
  getInfoLink(uri: string): string {
    return uri.replace('http://edamontology.org/', 'https://edamontology.github.io/edam-browser/#');
  }
}