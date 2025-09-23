import { CommonModule } from '@angular/common';
import { Component, inject, Input, OnInit } from '@angular/core';
import { FormsModule, ReactiveFormsModule, FormGroup, FormBuilder, FormArray, Validators } from '@angular/forms';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIcon, MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatTooltipModule } from '@angular/material/tooltip';

import { Resource, ToolType, Topic } from '../../../../model/resource.model';

interface SelectOption {
  value: string;
  text: string;
}

@Component({
  selector: 'app-tool-edit-labels',
  imports: [
    CommonModule,
    FormsModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    MatTooltipModule,
    MatChipsModule,
    MatAutocompleteModule
  ],
  templateUrl: './tool-edit-labels.html',
  styleUrl: './tool-edit-labels.scss'
})
export class ToolEditLabels implements OnInit {
  @Input() tool: Resource | null = null;
  @Input() form!: FormGroup;
  @Input() errors: any = null;

  private fb = inject(FormBuilder);

  // Form arrays
  get toolTypeArray(): FormArray {
    return this.form.get('toolType') as FormArray;
  }

  get topicArray(): FormArray {
    return this.form.get('topic') as FormArray;
  }

  get operatingSystemArray(): FormArray {
    return this.form.get('operatingSystem') as FormArray;
  }

  get languageArray(): FormArray {
    return this.form.get('language') as FormArray;
  }

  get collectionArray(): FormArray {
    return this.form.get('collectionID') as FormArray;
  }

  get elixirPlatformArray(): FormArray {
    return this.form.get('elixirPlatform') as FormArray;
  }

  get elixirNodeArray(): FormArray {
    return this.form.get('elixirNode') as FormArray;
  }

  get elixirCommunityArray(): FormArray {
    return this.form.get('elixirCommunity') as FormArray;
  }

  get otherIdArray(): FormArray {
    return this.form.get('otherID') as FormArray;
  }

  // Options for select fields
  // We can acyually fetch these options from Resource model


  maturityOptions: SelectOption[] = [
    { value: 'Mature', text: 'Mature' },
    { value: 'Emerging', text: 'Emerging' },
    { value: 'Legacy', text: 'Legacy' }
  ];

  licenseOptions: SelectOption[] = [
    { value: 'MIT', text: 'MIT License' },
    { value: 'Apache-2.0', text: 'Apache License 2.0' },
    { value: 'GPL-3.0', text: 'GNU General Public License v3.0' },
    { value: 'BSD-3-Clause', text: 'BSD 3-Clause License' },
    { value: 'Proprietary', text: 'Proprietary' },
    { value: 'Other', text: 'Other' }
  ];

  costOptions: SelectOption[] = [
    { value: 'Free of charge', text: 'Free of charge' },
    { value: 'Free of charge (with restrictions)', text: 'Free of charge (with restrictions)' },
    { value: 'Commercial', text: 'Commercial' }
  ];

  accessibilityOptions: SelectOption[] = [
    { value: 'Open access', text: 'Open access' },
    { value: 'Restricted access', text: 'Restricted access' },
    { value: 'Proprietary', text: 'Proprietary' }
  ];

  confidenceOptions: SelectOption[] = [
    { value: 'Very high', text: 'Very high' },
    { value: 'High', text: 'High' },
    { value: 'Medium', text: 'Medium' },
    { value: 'Low', text: 'Low' }
  ];

  // Operating system options
  operatingSystemOptions: SelectOption[] = [
    { value: 'Linux', text: 'Linux' },
    { value: 'Windows', text: 'Windows' },
    { value: 'Mac', text: 'Mac' },
    { value: 'BSD', text: 'BSD' },
    { value: 'Solaris', text: 'Solaris' }
  ];

  // Programming language options
  languageOptions: SelectOption[] = [
    { value: 'Python', text: 'Python' },
    { value: 'Java', text: 'Java' },
    { value: 'JavaScript', text: 'JavaScript' },
    { value: 'R', text: 'R' },
    { value: 'C++', text: 'C++' },
    { value: 'C', text: 'C' },
    { value: 'Perl', text: 'Perl' },
    { value: 'PHP', text: 'PHP' },
    { value: 'Ruby', text: 'Ruby' },
    { value: 'Go', text: 'Go' },
    { value: 'Rust', text: 'Rust' },
    { value: 'Swift', text: 'Swift' },
    { value: 'Other', text: 'Other' }
  ];

  ngOnInit() {
    this.initializeForm();
    this.populateForm();
  }

  private initializeForm() {
    this.form.addControl('toolType', this.fb.array([]));
    this.form.addControl('topic', this.fb.array([]));
    this.form.addControl('operatingSystem', this.fb.array([]));
    this.form.addControl('language', this.fb.array([]));
    this.form.addControl('maturity', this.fb.control(''));
    this.form.addControl('license', this.fb.control(''));
    this.form.addControl('cost', this.fb.control(''));
    this.form.addControl('collectionID', this.fb.array([]));
    this.form.addControl('accessibility', this.fb.control(''));
    this.form.addControl('elixirPlatform', this.fb.array([]));
    this.form.addControl('elixirNode', this.fb.array([]));
    this.form.addControl('elixirCommunity', this.fb.array([]));
    this.form.addControl('confidence_flag', this.fb.control(''));
    this.form.addControl('otherID', this.fb.array([]));
  }

  private populateForm() {
    if (!this.tool) return;

    // Populate tool types
    if (this.tool.toolType) {
      this.tool.toolType.forEach(toolType => {
        this.toolTypeArray.push(this.createToolTypeFormGroup(toolType));
      });
    }

    // Populate topics
    if (this.tool.topic) {
      this.tool.topic.forEach(topic => {
        this.topicArray.push(this.createTopicFormGroup(topic));
      });
    }

    // Populate operating systems
    if (this.tool.operatingSystem) {
      this.tool.operatingSystem.forEach(os => {
        this.operatingSystemArray.push(this.fb.control(os));
      });
    }

    // Populate languages
    if (this.tool.language) {
      this.tool.language.forEach(lang => {
        this.languageArray.push(this.fb.control(lang));
      });
    }

    // Populate simple fields
    this.form.patchValue({
      maturity: this.tool.maturity || '',
      license: this.tool.license || '',
      cost: this.tool.cost || '',
      accessibility: this.tool.accessibility || '',
      confidence_flag: (this.tool as any).confidence_flag || ''
    });

    // Populate collections
    if (this.tool.collectionID) {
      this.tool.collectionID.forEach(collection => {
        this.collectionArray.push(this.fb.control(collection));
      });
    }

    // Populate other IDs
    if (this.tool.otherID) {
      this.tool.otherID.forEach(otherId => {
        this.otherIdArray.push(this.createOtherIdFormGroup(otherId));
      });
    }
  }

  private createToolTypeFormGroup(toolType?: ToolType) {
    return this.fb.group({
      uri: [toolType?.uri || ''],
      term: [toolType?.term || '', Validators.required]
    });
  }

  private createTopicFormGroup(topic?: Topic) {
    return this.fb.group({
      uri: [topic?.uri || ''],
      term: [topic?.term || '', Validators.required]
    });
  }

  private createOtherIdFormGroup(otherId?: any) {
    return this.fb.group({
      value: [otherId?.value || '', Validators.required],
      type: [otherId?.type || '', Validators.required],
      version: [otherId?.version || '']
    });
  }

  // Add/Remove methods
  addToolType() {
    this.toolTypeArray.push(this.createToolTypeFormGroup());
  }

  removeToolType(index: number) {
    this.toolTypeArray.removeAt(index);
  }

  addTopic() {
    this.topicArray.push(this.createTopicFormGroup());
  }

  removeTopic(index: number) {
    this.topicArray.removeAt(index);
  }

  addOperatingSystem() {
    this.operatingSystemArray.push(this.fb.control(''));
  }

  removeOperatingSystem(index: number) {
    this.operatingSystemArray.removeAt(index);
  }

  addLanguage() {
    this.languageArray.push(this.fb.control(''));
  }

  removeLanguage(index: number) {
    this.languageArray.removeAt(index);
  }

  addCollection() {
    this.collectionArray.push(this.fb.control(''));
  }

  removeCollection(index: number) {
    this.collectionArray.removeAt(index);
  }

  addElixirPlatform() {
    this.elixirPlatformArray.push(this.fb.control(''));
  }

  removeElixirPlatform(index: number) {
    this.elixirPlatformArray.removeAt(index);
  }

  addElixirNode() {
    this.elixirNodeArray.push(this.fb.control(''));
  }

  removeElixirNode(index: number) {
    this.elixirNodeArray.removeAt(index);
  }

  addElixirCommunity() {
    this.elixirCommunityArray.push(this.fb.control(''));
  }

  removeElixirCommunity(index: number) {
    this.elixirCommunityArray.removeAt(index);
  }

  addOtherId() {
    this.otherIdArray.push(this.createOtherIdFormGroup());
  }

  removeOtherId(index: number) {
    this.otherIdArray.removeAt(index);
  }

  // Error checking
  hasError(fieldName: string, index?: number): boolean {
    if (this.errors && this.errors[fieldName]) {
      if (index !== undefined) {
        return this.errors[fieldName][index] && this.errors[fieldName][index][0];
      }
      return true;
    }
    return false;
  }

  getErrorMessage(fieldName: string, index?: number): string {
    if (this.errors && this.errors[fieldName]) {
      if (index !== undefined && this.errors[fieldName][index]) {
        return this.errors[fieldName][index][0];
      }
      if (typeof this.errors[fieldName] === 'string') {
        return this.errors[fieldName];
      }
    }
    return '';
  }
}
