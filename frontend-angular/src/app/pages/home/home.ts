import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { SearchBar } from '../../components/search-bar/search-bar';

@Component({
  selector: 'app-home',
  imports: [MatIconModule, SearchBar],
  templateUrl: './home.html',
  styleUrl: './home.scss'
})
export class Home {
  constructor(private router: Router) {}

  navigateToSearch() {
    this.router.navigate(['/search']);
  }

  navigateToDomains() {
    this.router.navigate(['/domains']);
  }

  navigateToCommunities() {
    this.router.navigate(['/communities']);
  }
}
