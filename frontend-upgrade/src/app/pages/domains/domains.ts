import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Resources } from '../../services/resources';
import { Domain } from '../../model/domain.model';

@Component({
  selector: 'app-domains',
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatGridListModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './domains.html',
  styleUrl: './domains.scss'
})
export class Domains implements OnInit {

  loading = false;

  domainService = inject(Resources);
  domains = signal<Array<Domain>>([]);

  ngOnInit() {
    this.domainService.getDomains().subscribe(data => {
      this.domains.set(data);
    });
  }

}
