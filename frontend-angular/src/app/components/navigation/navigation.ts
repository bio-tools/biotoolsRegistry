import { Component } from '@angular/core';
import { RouterModule, Router, NavigationEnd } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { MatIconModule } from '@angular/material/icon';
import { MatDividerModule } from '@angular/material/divider';
import { SearchBar } from '../search-bar/search-bar';
import { AuthService, User } from '../../services/auth.service';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-navigation',
  imports: [
    CommonModule,
    RouterModule,
    MatToolbarModule,
    MatButtonModule,
    MatMenuModule,
    MatIconModule,
    MatDividerModule,
    SearchBar
  ],
  templateUrl: './navigation.html',
  styleUrl: './navigation.scss'
})
export class Navigation {
  showSearch = true;

  constructor(
    private router: Router,
    public authService: AuthService
  ) {
    // Listen to route changes to determine if we should show search
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: NavigationEnd) => {
      this.showSearch = event.url !== '/';
    });
  }

  navigateToHome() {
    this.router.navigate(['/']);
  }

  navigateToSearch() {
    this.router.navigate(['/search']);
  }

  navigateToDomains() {
    this.router.navigate(['/domains']);
  }

  navigateToCommunities() {
    this.router.navigate(['/communities']);
  }

  navigateToAbout() {
    // TODO: Implement about page
    console.log('Navigate to about');
  }

  navigateToLogin() {
    this.router.navigate(['/login']);
  }

  navigateToRegister() {
    this.router.navigate(['/register']);
  }

  navigateToProfile() {
    // TODO: Implement profile page
    console.log('Navigate to profile');
  }

  logout() {
    this.authService.logout().subscribe({
      next: () => {
        this.router.navigate(['/']);
      },
      error: (error) => {
        console.error('Logout error:', error);
        // Even if logout fails, redirect to home
        this.router.navigate(['/']);
      }
    });
  }
}
